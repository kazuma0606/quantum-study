"""分割数 n についての外挿で、正確な値 <Z_0>(t=2) = -0.2959 を推定する（既存の手法を手元の実機データに当てる）。

h = 1/n（刻み幅に比例）として、次の3通りを比べる。
  (1) トロッター誤差だけの外挿（Endo ら 2019 の考え方、リチャードソン型）：
        z(h) = z0 + c2 h^2 + c3 h^3（1次。この模型の局所的な量では h の1次の項が消える）
        z(h) = z0 + c2 h^2 + c4 h^4（2次。対称な分解なので偶数次）
      を雑音なしの値に当てはめ、z0 が正確な値に戻るかを確かめる（手法の確認）。
  (2) 同じ当てはめを、実機の値にそのまま使う（実機の誤差が n とともに増えると、どれだけ狂うか）。
  (3) 2つの誤差をまとめて当てはめる（Hakkaku ら 2025、Zhou ら 2026 の考え方）：
        z(n) = (1 - λ)^n × [ z0 + トロッター誤差の項 ]
      確率的な誤差（脱分極）なら、1ステップごとに <Z_0> が一定の割合で縮むので、この形になる（N=2 の全体の脱分極では厳密）。
いずれも、実機の統計誤差（z_sem）で重みをつけた最小二乗。z0 の誤差は当てはめの共分散から求める。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/extrapolation.py
出力: results/extrapolation_N2.csv と figures/extrapolation_N2.png
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

DATASETS = [  # (ラベル, ファイル名の接頭辞, 次数, ツイリング)
    ("22–23 1次（10/4）", "hardware_main_o1_", 1, False),
    ("22–23 2次（10/4、外れた1本）", "hardware_main_o2_", 2, False),
    ("22–23 1次（10/5）", "hardware_day2_o1_", 1, False),
    ("22–23 2次（10/5）", "hardware_day2_o2_", 2, False),
    ("22–23 1次・ツイリング", "hardware_twirl_o1_", 1, True),
    ("142–143 1次", "hardware_q142_o1_", 1, False),
    ("142–143 2次", "hardware_q142_o2_", 2, False),
    ("142–143 1次・ツイリング", "hardware_q142_twirl_o1_", 1, True),
    ("142–143 2次・ツイリング", "hardware_q142_twirl_o2_", 2, True),
]
POWERS = {1: (2, 3), 2: (2, 4)}      # トロッター誤差の展開に使う h の次数


def trotter_poly(h, z0, ca, cb, order):
    pa, pb = POWERS[order]
    return z0 + ca * h**pa + cb * h**pb


def load(prefix: str) -> dict:
    path = sorted(RES.glob(prefix + "2*.csv"))[-1]
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    return {"file": path.name,
            "n": np.array([int(float(r["n_steps"])) for r in rows]),
            "z": np.array([float(r["z_readout_corrected"]) for r in rows]),
            "sem": np.array([float(r["z_sem"]) for r in rows]),
            "z_trot": np.array([float(r["z_trotter_noiseless"]) for r in rows]),
            "z_exact": float(rows[0]["z_exact"])}


def fit_trotter(n, z, sem, order):
    h = 1.0 / n
    f = lambda h, z0, ca, cb: trotter_poly(h, z0, ca, cb, order)
    p, cov = curve_fit(f, h, z, p0=[z[-1], 0.0, 0.0], sigma=sem, absolute_sigma=sem is not None)
    chi2 = float(np.sum(((f(h, *p) - z) / (sem if sem is not None else 1)) ** 2))
    return p, np.sqrt(np.diag(cov)), chi2, f


def fit_joint(n, z, sem, order):
    h = 1.0 / n
    def f(n_, z0, ca, cb, lam):
        return (1 - lam) ** n_ * trotter_poly(1.0 / n_, z0, ca, cb, order)
    p, cov = curve_fit(f, n.astype(float), z, p0=[z[-1], 0.0, 0.0, 0.005], sigma=sem, absolute_sigma=True,
                       bounds=([-1.5, -50, -50, -0.2], [1.5, 50, 50, 0.2]))
    chi2 = float(np.sum(((f(n.astype(float), *p) - z) / sem) ** 2))
    return p, np.sqrt(np.diag(cov)), chi2, f


def main() -> None:
    table = []
    fig, axes = plt.subplots(3, 3, figsize=(15, 11), sharex=True)
    for ax, (label, prefix, order, twirled) in zip(axes.flat, DATASETS):
        d = load(prefix)
        z_exact = d["z_exact"]
        for nmin in (3, 4, 5):
            sel = d["n"] >= nmin
            n, z, sem, zt = d["n"][sel], d["z"][sel], d["sem"][sel], d["z_trot"][sel]
            # (1) 雑音なしの値（重みなし、手法そのものの誤差）
            p1, _, _, _ = fit_trotter(n, zt, None, order)
            # (2) 実機の値にトロッターだけの外挿
            p2, e2, c2, f2 = fit_trotter(n, z, sem, order)
            # (3) まとめて当てはめ
            p3, e3, c3, f3 = fit_joint(n, z, sem, order)
            table.append({"data": label, "file": d["file"], "order": order, "twirled": twirled, "n_min": nmin, "n_points": int(sel.sum()),
                          "z_exact": z_exact,
                          "noiseless_trotter_only_z0": p1[0], "noiseless_bias": p1[0] - z_exact,
                          "hw_trotter_only_z0": p2[0], "hw_trotter_only_err": e2[0], "hw_trotter_only_bias": p2[0] - z_exact,
                          "hw_trotter_only_chi2": c2,
                          "hw_joint_z0": p3[0], "hw_joint_err": e3[0], "hw_joint_bias": p3[0] - z_exact,
                          "hw_joint_lambda": p3[3], "hw_joint_chi2": c3,
                          "hw_raw_largest_n": z[-1], "hw_raw_largest_n_bias": z[-1] - z_exact})
            if nmin == 4:
                hh = np.linspace(0, 1 / nmin, 100)
                ax.errorbar(1 / d["n"], d["z"], yerr=d["sem"], fmt="o", ms=3.5, color="#1f77b4", capsize=2, label="実機")
                ax.plot(1 / d["n"], d["z_trot"], "x", color="#888", ms=4, label="雑音なしのトロッター")
                ax.plot(hh, f2(hh, *p2), "-", color="#e67e00", lw=1.2, label="トロッターだけの外挿")
                nn = np.linspace(nmin, 400, 400)
                ax.plot(1 / nn, f3(nn, *p3) / (1 - p3[3]) ** nn, "-", color="#2ca02c", lw=1.2,
                        label="まとめた当てはめ（雑音を除いた部分）")
                ax.errorbar([0], [p2[0]], yerr=e2[0], fmt="s", color="#e67e00", ms=6, capsize=3)
                ax.errorbar([0], [p3[0]], yerr=e3[0], fmt="D", color="#2ca02c", ms=6, capsize=3)
                ax.axhline(z_exact, color="k", lw=0.8, ls="--", label="正確な値 −0.2959")
                ax.set_title(label, fontsize=10)
                ax.set_xlim(-0.01, 0.36)
                ax.set_ylim(-0.75, 0.0)
    for ax in axes[-1]:
        ax.set_xlabel("刻み幅に比例する $h=1/n$（左端 $h=0$ が外挿の先）")
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$\langle Z_0\rangle$")
    axes[0, 0].legend(fontsize=7.5, loc="lower right")
    fig.suptitle("n についての外挿（n ≥ 4 を使用）：□ トロッターだけの外挿、◇ 2つの誤差をまとめた当てはめ", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "extrapolation_N2.png", dpi=140)

    out = RES / "extrapolation_N2.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    print("n≥4 の結果（正確な値 −0.2959 との差）")
    print(f"{'データ':28s} {'雑音なし':>8s} {'実機の生値(n=14)':>14s} {'トロッターだけ':>16s} {'まとめて':>18s}  λ")
    for r in table:
        if r["n_min"] != 4:
            continue
        print(f"{r['data']:28s} {r['noiseless_bias']:+8.4f} {r['hw_raw_largest_n_bias']:+14.3f} "
              f"{r['hw_trotter_only_bias']:+9.3f}±{r['hw_trotter_only_err']:.3f} {r['hw_joint_bias']:+9.3f}±{r['hw_joint_err']:.3f}"
              f"  {r['hw_joint_lambda']:.4f}（χ² {r['hw_joint_chi2']:.0f}/{r['n_points']}）")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
