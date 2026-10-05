"""実機の <Z_0>（N=2）を、CNOT ごとのコヒーレントな誤差のモデルで当てはめる。ツイリングなし・ありのデータを同時に使う。

回路は aer_check.trotter_circuit と同じ順（RX、CX・RZ・CX）。各 CX の直後に
  コヒーレントな誤差 E = exp(-i Σ_k θ_k P_k)（P_k は下の候補の2量子ビットのパウリ、c = 制御 = 量子ビット 0、t = 標的 = 1）
  と、2量子ビット脱分極 p を入れる。
ツイリングありのデータでは、E をパウリ・ツイリングしたもの（E = Σ_P c_P P と展開したときの、確率 |c_P|² のパウリ通路）に置き換える。
  ツイリングは、コヒーレントな誤差を同じ大きさの確率的な誤差に変えるだけなので、同じ θ と p で両方のデータを説明できるはず。
候補のモデル：
  Z 位相        ：Z_c, Z_t（各量子ビットの余分な Z 回転）
  CZ 型         ：Z_c, X_t, Z_c X_t（ネイティブの CZ の位相の誤差と CZ の角度の誤差を、CX = H_t CZ H_t の枠に移したもの）
  一般（5 項）  ：Z_c, Z_t, X_t, Z_c X_t, Z_c Z_t
  CZ 型＋RX の誤差：CZ 型に加えて、RX の層の直後に exp(-i(a X_c + b X_t + c Z_c + e Z_t))（1量子ビットゲートのコヒーレントな誤差）
独立の確かめ：当てはめに使っていない Z の直接測定（hardware_zprobe.py、量子ビット 22–23）の位相の傾きを、モデルから予測して比べる。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/coherent_fits.py
出力: results/coherent_fits_N2.csv と figures/coherent_fits_N2.png
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

N, T = 2, 2.0
I2 = np.eye(2, dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
PAULI1 = {"I": I2, "X": tn.X, "Y": Y, "Z": tn.Z}
LABELS2 = [a + b for a in "IXYZ" for b in "IXYZ"]          # 1文字目 = 制御（量子ビット 0）、2文字目 = 標的（量子ビット 1）
PAULI2 = {lab: tn.op_on(PAULI1[lab[0]], 0, N) @ tn.op_on(PAULI1[lab[1]], 1, N) for lab in LABELS2}
P0, P1 = np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)
CX = tn.op_on(P0, 0, N) + tn.op_on(P1, 0, N) @ tn.op_on(tn.X, 1, N)
H1 = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
SDG = np.diag([1, -1j])
Z0 = PAULI2["ZI"]
VEC_I = np.eye(4, dtype=complex).reshape(-1)

MODELS = {  # 名前 → (CX の直後の誤差のパウリ, RX の層の直後の誤差のパウリ)
    "Z 位相": (["ZI", "IZ"], []),
    "CZ 型": (["ZI", "IX", "ZX"], []),
    "一般（5 項）": (["ZI", "IZ", "IX", "ZX", "ZZ"], []),
    "CZ 型＋RX の誤差": (["ZI", "IX", "ZX"], ["XI", "IX", "ZI", "IZ"]),
}
SHOWN = "CZ 型"   # 図に描くモデル（両方の組に共通の、いちばん単純で 142–143 を説明できるもの）
PAIRS = {  # 量子ビットの組 → [(ファイル名の接頭辞, 次数, ツイリング)]
    "22–23": [("hardware_main_o1_", 1, False), ("hardware_main_o2_", 2, False), ("hardware_twirl_o1_", 1, True)],
    # 1日目の2次の実行は、1次と続けて測り直した2日目の値と大きく違った（1回だけの揺らぎ）。それを2日目の1次・2次に置き換えたもの
    "22–23（2日目）": [("hardware_day2_o1_", 1, False), ("hardware_day2_o2_", 2, False), ("hardware_twirl_o1_", 1, True)],
    "142–143": [("hardware_q142_o1_", 1, False), ("hardware_q142_o2_", 2, False),
                ("hardware_q142_twirl_o1_", 1, True), ("hardware_q142_twirl_o2_", 2, True)],
}


def sup(U: np.ndarray) -> np.ndarray:
    """ρ → U ρ U† の超演算子（行優先の vec）。"""
    return np.kron(U, U.conj())


def depol_sup(p: float) -> np.ndarray:
    return (1 - p) * np.eye(16) + p * np.outer(VEC_I, VEC_I) / 4


def error_sup(labels: list[str], theta: np.ndarray, p: float, twirled: bool) -> np.ndarray:
    E = expm(-1j * sum(th * PAULI2[lab] for lab, th in zip(labels, theta)))
    if twirled:
        coef = {lab: np.trace(PAULI2[lab] @ E) / 4 for lab in LABELS2}
        S = sum(abs(c) ** 2 * sup(PAULI2[lab]) for lab, c in coef.items())
    else:
        S = sup(E)
    return depol_sup(p) @ S


def rx(theta: float) -> np.ndarray:
    return expm(-0.5j * theta * tn.X)


def z0_curve(order: int, ns: list[int], err: np.ndarray, x_err: np.ndarray | None = None) -> np.ndarray:
    """各 n について、雑音つきの回路の <Z_0>。err は CX の直後、x_err は RX の層の直後に入れる誤差の超演算子。
    2次は、変換後の回路と同じく隣り合う RX(d) を RX(2d) にまとめた形：X(d)、[ZZ・X(2d)]×(n-1)、ZZ、X(d)。
    （1次との違いは、X(d) を回路の最後から最初に移しただけで、間の回路は同じ。）"""
    cx_e = err @ sup(CX)
    xe = np.eye(16) if x_err is None else x_err
    out = []
    for n in ns:
        d = T / n
        zz = cx_e @ sup(tn.op_on(expm(-1j * d * tn.Z), 1, N)) @ cx_e        # RZ(2d) = exp(-i d Z)
        x2 = xe @ sup(np.kron(rx(2 * d), rx(2 * d)))
        x1 = xe @ sup(np.kron(rx(d), rx(d)))
        rho = np.zeros(16, dtype=complex)
        rho[0] = 1.0
        if order == 1:
            for _ in range(n):
                rho = x2 @ (zz @ rho)
        else:
            rho = x1 @ rho
            for i in range(n):
                rho = (x2 if i < n - 1 else x1) @ (zz @ rho)
        out.append(np.real(np.trace(Z0 @ rho.reshape(4, 4))))
    return np.array(out)


def load_pair(pair: str) -> list[dict]:
    data = []
    for prefix, order, twirled in PAIRS[pair]:
        path = sorted((HERE / "results").glob(prefix + "2*.csv"))[-1]
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        data.append({"order": order, "twirled": twirled, "file": path.name,
                     "ns": [int(float(r["n_steps"])) for r in rows],
                     "z": np.array([float(r["z_readout_corrected"]) for r in rows]),
                     "sem": np.array([float(r["z_sem"]) for r in rows]),
                     "z_trotter": np.array([float(r["z_trotter_noiseless"]) for r in rows])})
    return data


def split(x: np.ndarray, model: tuple[list[str], list[str]]) -> tuple[np.ndarray, float, np.ndarray]:
    """パラメータの並び：[CX の誤差の θ…, p, RX の層の誤差の θ…]。"""
    k = len(model[0])
    return x[:k], x[k], x[k + 1:]


def curves_for(x: np.ndarray, model: tuple[list[str], list[str]], d: dict) -> np.ndarray:
    theta, p, theta_x = split(x, model)
    x_err = sup(expm(-1j * sum(a * PAULI2[lab] for lab, a in zip(model[1], theta_x)))) if model[1] else None
    # ゲートのツイリングは2量子ビットゲートだけに効くので、RX の誤差はツイリングありでもコヒーレントのまま
    return z0_curve(d["order"], d["ns"], error_sup(model[0], theta, p, d["twirled"]), x_err)


def residuals(x: np.ndarray, model: tuple[list[str], list[str]], data: list[dict]) -> np.ndarray:
    return np.concatenate([(curves_for(x, model, d) - d["z"]) / d["sem"] for d in data])


def fit(model: tuple[list[str], list[str]], data: list[dict], starts: int = 40, seed: int = 0) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    k, kx = len(model[0]), len(model[1])
    lo = np.r_[-0.4 * np.ones(k), 0.0, -0.4 * np.ones(kx)]
    hi = np.r_[0.4 * np.ones(k), 0.05, 0.4 * np.ones(kx)]
    best = None
    for _ in range(starts):
        x0 = np.r_[rng.uniform(-0.15, 0.15, k), rng.uniform(0.0, 0.01), rng.uniform(-0.1, 0.1, kx)]
        r = least_squares(residuals, x0, bounds=(lo, hi), args=(model, data))
        if best is None or r.cost < best.cost:
            best = r
    return best.x, 2 * best.cost


def zprobe_slopes(labels: list[str], theta: np.ndarray, p: float, ks=(0, 2, 4, 8, 12)) -> dict[int, float]:
    """hardware_zprobe.py の回路（H で |+>、CX・CX を k 回、X と Y で測る）の位相の傾きを、モデルから予測する。"""
    cx_e = error_sup(labels, theta, p, False) @ sup(CX)
    pair_map = cx_e @ cx_e
    slopes = {}
    for t in (0, 1):
        Ht = tn.op_on(H1, t, N)
        rho = np.zeros(16, dtype=complex)
        rho[0] = 1.0
        rho = sup(Ht) @ rho
        phases = []
        for k in ks:
            r = rho.copy()
            for _ in range(k):
                r = pair_map @ r
            R = r.reshape(4, 4)
            ex = np.real(np.trace(tn.op_on(tn.X, t, N) @ R))
            ey = np.real(np.trace(tn.op_on(Y, t, N) @ R))
            phases.append(np.arctan2(ey, ex))
        slopes[t] = float(np.polyfit(ks, np.unwrap(phases), 1)[0])
    return slopes


def xprobe_slope(labels: list[str], theta: np.ndarray, p: float, ks=(0, 2, 4, 8, 12)) -> float:
    """hardware_zprobe.py --x-axis の回路（両方 |0>、CX・CX を k 回、標的を Z と Y で測る）の、atan2(<Y>, <Z>) の傾きの予測。"""
    cx_e = error_sup(labels, theta, p, False) @ sup(CX)
    pair_map = cx_e @ cx_e
    phases = []
    for k in ks:
        r = np.zeros(16, dtype=complex)
        r[0] = 1.0
        for _ in range(k):
            r = pair_map @ r
        R = r.reshape(4, 4)
        phases.append(np.arctan2(np.real(np.trace(tn.op_on(Y, 1, N) @ R)), np.real(np.trace(tn.op_on(tn.Z, 1, N) @ R))))
    return float(np.polyfit(ks, np.unwrap(phases), 1)[0])


def main() -> None:
    table, shown = [], {}
    for pair in PAIRS:
        data = load_pair(pair)
        npts = sum(len(d["ns"]) for d in data)
        for name, model in MODELS.items():
            x, chi2 = fit(model, data)
            theta, p, theta_x = split(x, model)
            row = {"qubits": pair, "model": name, "n_points": npts, "n_params": len(x), "chi2": float(chi2), "p": float(p)}
            row.update({f"theta_cx_{lab}": float(th) for lab, th in zip(model[0], theta)})
            row.update({f"theta_rx_{lab}": float(th) for lab, th in zip(model[1], theta_x)})
            if pair.startswith("22–23"):
                s = zprobe_slopes(model[0], theta, p)
                row["zprobe_slope_q22_pred"], row["zprobe_slope_q23_pred"] = s[0], s[1]
            table.append(row)
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
            if name == SHOWN:
                shown[pair] = (x, chi2, data)
    meas = json.loads(sorted((HERE / "results").glob("hardware_zprobe_2*.json"))[-1].read_text(encoding="utf-8"))
    print(f"Z の直接測定（実測）の傾き：{meas['phase_slope_rad_per_pair']}")

    fig, axes = plt.subplots(1, len(PAIRS), figsize=(6.5 * len(PAIRS), 4.8))
    colors = {(1, False): "#1f77b4", (2, False): "#e67e00", (1, True): "#2ca02c", (2, True): "#d62728"}
    for ax, (pair, (x, chi2, data)) in zip(axes, shown.items()):
        for d in data:
            c = colors[(d["order"], d["twirled"])]
            lab = f"{d['order']}次・{'ツイリング' if d['twirled'] else '設定なし'}"
            ax.errorbar(d["ns"], d["z"] - d["z_trotter"], yerr=d["sem"], fmt="o", color=c, ms=4, capsize=2, label=f"実機：{lab}")
            ax.plot(d["ns"], curves_for(x, MODELS[SHOWN], d) - d["z_trotter"], "-", color=c, lw=1.2)
        name = SHOWN
        ax.axhline(0, color="#999", lw=0.8)
        ax.set_xlabel("分割数 $n$")
        ax.set_ylabel("雑音による変化（実機 − 雑音なしのトロッター積）")
        ax.set_title(f"量子ビット {pair}：{name}（線）、$\\chi^2$={chi2:.0f}／{sum(len(d['ns']) for d in data)} 点", fontsize=11)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "coherent_fits_N2.png", dpi=150)

    out = HERE / "results" / "coherent_fits_N2.csv"
    keys = []
    for r in table:
        keys += [k for k in r if k not in keys]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(table)
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
