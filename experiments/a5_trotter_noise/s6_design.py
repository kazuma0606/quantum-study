"""雑音のモデリング S6（docs/a5_modeling_plan.md）：来月の実機の測り方を、測る前に比べる（ガウス近似による実験計画）。

考え方（ラプラス近似と同じ、事後分布を正規分布で近似する）
  今の知識：実データの F5＋D1 の事後分布（NUTS のサンプル）の平均 φ₀ と共分散 Σ₀
            φ = (zi 2個, rot_c0 2×3, rot_c1 2×3, log p 2個) の 16 個
  新しい測定：候補の回路とショット数から、予測 μ(φ, δ) と統計誤差 σ を作る。δ は新しいジョブごとのずれ（ZI に足す、
            事前分布 N(0, σ_drift²)、推定はするが目的ではない局外パラメータ）
  測ったあとの共分散 ≈ (Σ₀⁻¹ ⊕ σ_drift⁻² + Jᵀ diag(σ⁻²) J)⁻¹、J = ∂μ/∂(φ, δ) を φ₀ で計算（フィッシャー情報）
  → 候補ごとに、知りたい量の標準偏差がどれだけ縮むかを、QPU の使用時間あたりで比べる
QPU の使用時間は、これまでのジョブの記録から 約 2 秒 ＋ 3×10⁻⁴ 秒 × (回路の数 × ショット数) と見積もる
（トロッター回路 14 本 × 15000 ショットで 65 秒、× 8000 で 36 秒）。

限界：線形化なので、事後分布が複数の山を持つ量（揺らぎを入れないと符号が逆になる制御 |1> の Z 回転など）では、
「どちらの山かを見分けられるか」までは言えない。そこで、制御 |1> の Z 回転の2つの候補（−0.11 と +0.105）での予測の差を、
統計誤差の何倍かでも示す。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s6_design.py
出力: results/s6/design.md（表）と design.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import noise_model_jax as nm  # noqa: E402
from s2_fit import OUT as S2_OUT, PAIRS, jax, jnp  # noqa: E402

OUT = Path(__file__).resolve().parent / "results" / "s6"
TAG = "real_F5_D1_long"
NAMES = ([f"zi[{p}]" for p in PAIRS] + [f"c0_{a}[{p}]" for p in PAIRS for a in "xyz"]
         + [f"c1_{a}[{p}]" for p in PAIRS for a in "xyz"] + [f"log_p[{p}]" for p in PAIRS])
SEC_PER_SHOT, SEC_PER_JOB = 3e-4, 2.0


def theta15(phi, g, delta):
    """F5 のパラメータ φ から、組 g の 15 成分の回転（s2_fit.model の branch と同じ置き方）。"""
    zi, r0, r1 = phi[0:2], phi[2:8].reshape(2, 3), phi[8:14].reshape(2, 3)
    th = jnp.zeros(15).at[nm.LABELS15.index("ZI")].set(zi[g] + delta)
    for ax, (li, lz) in enumerate((("IX", "ZX"), ("IY", "ZY"), ("IZ", "ZZ"))):
        th = th.at[nm.LABELS15.index(li)].set((r0[g, ax] + r1[g, ax]) / 2)
        th = th.at[nm.LABELS15.index(lz)].set((r0[g, ax] - r1[g, ax]) / 2)
    return th


# 回路の種類：("trotter", 次数, ツイリング, n の並び) または ("probe", 軸, 対象, 制御 |1>, 反転を戻す, k の並び)
def circuit_outputs(phi, g, delta, spec):
    """予測（トロッター回路は <Z0>、直接の測定は位相）と、統計誤差の計算に使う期待値を返す。"""
    p = jnp.exp(phi[14 + g])
    if spec[0] == "trotter":
        _, order, tw, ns = spec
        z = nm.trotter_z0(order, jnp.asarray(ns), nm.error_sup(theta15(phi, g, delta), p, tw)).real
        return z, (z,)
    _, axis, target, c1, unflip, ks = spec
    e_ref, e_y = nm.probe_expectations(nm.error_sup(theta15(phi, g, delta), p, False), axis, target, tuple(ks),
                                       control_one=c1, unflip=unflip)
    return jnp.arctan2(e_y.real, e_ref.real), (e_ref.real, e_y.real)


def sigmas(spec, aux, shots):
    if spec[0] == "trotter":
        (z,) = aux
        return np.sqrt(np.maximum(1 - np.asarray(z) ** 2, 1e-6) / shots)
    e_ref, e_y = (np.asarray(a) for a in aux)
    vx, vy = (1 - e_ref**2) / shots, (1 - e_y**2) / shots
    r2 = e_ref**2 + e_y**2
    return np.sqrt((e_ref**2 * vy + e_y**2 * vx) / r2**2)


def n_circuits(spec):
    return len(spec[3]) if spec[0] == "trotter" else 2 * len(spec[5])        # 直接の測定は基準の基底と Y の2本ずつ


KS = (2, 4, 8, 12)
NS = tuple(range(1, 15))
C1_Z = ("probe", "Z", 1, True, True, KS)        # 制御 |1>、標的の Z 回転（反転を戻す）
C1_X = ("probe", "X", 1, True, False, KS)       # 制御 |1>、標的の X 回転
C0_PROBES = [("probe", "Z", 0, False, False, KS), ("probe", "Z", 1, False, False, KS), ("probe", "X", 1, False, False, KS)]
# 候補：名前 → [(組の番号の並び, 回路の種類の並び, ショット数)]。1つの要素が1ジョブ（ジョブごとにずれ δ を置く）
DESIGNS = {
    "c1 Z（反転を戻す）": [((0, 1), [C1_Z], 3000)],
    "c1 X": [((0, 1), [C1_X], 3000)],
    "c1 Z＋X": [((0, 1), [C1_Z, C1_X], 3000)],
    "c1 Z＋X（22-23 だけ）": [((0,), [C1_Z, C1_X], 3000)],
    "c1 Z＋X、k を 2〜24": [((0, 1), [C1_Z[:5] + ((2, 4, 8, 12, 16, 24),), C1_X[:5] + ((2, 4, 8, 12, 16, 24),)], 3000)],
    "c0 の直接の測定（10/5 と同じ）": [((0, 1), C0_PROBES, 3000)],
    "c0＋c1 の直接の測定": [((0, 1), C0_PROBES + [C1_Z, C1_X], 3000)],
    "トロッター 1次 生（n=1〜14）": [((0, 1), [("trotter", 1, False, NS)], 8000)],
    "トロッター 1次 ツイリング": [((0, 1), [("trotter", 1, True, NS)], 8000)],
    "トロッター 2次 生": [((0, 1), [("trotter", 2, False, NS)], 8000)],
    "c1 Z＋X を2回（別の時刻）": [((0, 1), [C1_Z, C1_X], 3000), ((0, 1), [C1_Z, C1_X], 3000)],
}
TARGETS = ["c1_z[22-23]", "c1_x[22-23]", "c1_z[142-143]", "zi[22-23]", "c0_x[22-23]", "log_p[22-23]"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(S2_OUT / f"{TAG}_draws.npz")
    draws = np.concatenate([d["zi"].reshape(-1, 2), d["rot_c0"].reshape(-1, 6), d["rot_c1"].reshape(-1, 6),
                            np.log(d["p"].reshape(-1, 2))], axis=1)
    phi0, cov0 = draws.mean(0), np.cov(draws.T)
    sd_drift = float(np.median(d["sigma_drift"]))
    prec0 = np.linalg.inv(cov0)
    sd0 = np.sqrt(np.diag(cov0))
    print(f"今の事後分布：{TAG}、σ_drift = {sd_drift:.4f}")

    rows = []
    for name, jobs in DESIGNS.items():
        blocks, shots_total, secs = [], 0, 0.0
        n_jobs = sum(len(gs) for gs, _, _ in jobs)                  # 組ごとに別のジョブ（別の δ）
        j_idx = 0
        for gs, specs, shots in jobs:
            for g in gs:
                for spec in specs:
                    def f(x, g=g, spec=spec):
                        return circuit_outputs(x[:16], g, x[16], spec)[0]
                    x0 = jnp.asarray(np.r_[phi0, 0.0])
                    J = np.asarray(jax.jacfwd(f)(x0))               # (出力, 17)
                    _, aux = circuit_outputs(x0[:16], g, 0.0, spec)
                    sig = sigmas(spec, aux, shots)
                    Jfull = np.zeros((J.shape[0], 16 + n_jobs))
                    Jfull[:, :16], Jfull[:, 16 + j_idx] = J[:, :16], J[:, 16]
                    blocks.append(Jfull / sig[:, None])
                    shots_total += n_circuits(spec) * shots
                j_idx += 1
            secs += SEC_PER_JOB + SEC_PER_SHOT * shots_total
            shots_total = 0
        A = np.concatenate(blocks)
        prior = np.zeros((16 + n_jobs, 16 + n_jobs))
        prior[:16, :16] = prec0
        prior[16:, 16:] = np.eye(n_jobs) / sd_drift**2
        cov = np.linalg.inv(prior + A.T @ A)[:16, :16]
        sd = np.sqrt(np.diag(cov))
        rows.append({"design": name, "qpu_s": secs, **{t: sd[NAMES.index(t)] for t in TARGETS},
                     "info_gain_nats": 0.5 * (np.linalg.slogdet(cov0)[1] - np.linalg.slogdet(cov)[1])})

    # 制御 |1> の Z 回転の2つの候補で、c1 Z の予測がどれだけ違うか（山を見分けられるか）
    sep_lines = []
    i_c1z = NAMES.index("c1_z[22-23]")
    phi_a, phi_b = phi0.copy(), phi0.copy()
    phi_a[i_c1z], phi_b[i_c1z] = -0.11, 0.105
    za, aux = circuit_outputs(jnp.asarray(phi_a), 0, 0.0, C1_Z)
    zb, _ = circuit_outputs(jnp.asarray(phi_b), 0, 0.0, C1_Z)
    sig = sigmas(C1_Z, aux, 3000)
    for k, a, b, s in zip(KS, np.asarray(za), np.asarray(zb), sig):
        diff = np.angle(np.exp(1j * (a - b)))
        sep_lines.append(f"| {k} | {a:+.3f} | {b:+.3f} | {diff:+.3f} | {s:.3f} | {abs(diff) / s:.0f} |")

    lines = ["# S6：来月の測り方の比較（ガウス近似）", "",
             f"今の知識は `{TAG}` の事後分布（NUTS）。表は、各候補を測ったあとの標準偏差（今の値との比）。"
             f"QPU 秒は見積もり（約 {SEC_PER_JOB:.0f} 秒/ジョブ ＋ {SEC_PER_SHOT * 1e3:.1f} ms × 回路×ショット）。"
             "情報量は事後分布の体積の縮み（ナット、½ log det の差）。", "",
             "| 候補 | QPU 秒 | " + " | ".join(TARGETS) + " | 情報量 | 情報量/QPU 秒 |",
             "|---|---|" + "---|" * len(TARGETS) + "---|---|",
             "| （今） | 0 | " + " | ".join(f"{sd0[NAMES.index(t)]:.4f}" for t in TARGETS) + " | 0 | |"]
    for r in rows:
        cells = [f"{r[t]:.4f}（{r[t] / sd0[NAMES.index(t)]:.2f}）" for t in TARGETS]
        lines.append(f"| {r['design']} | {r['qpu_s']:.0f} | " + " | ".join(cells)
                     + f" | {r['info_gain_nats']:.1f} | {r['info_gain_nats'] / r['qpu_s']:.2f} |")
    lines += ["", "## 制御 |1⟩ の Z 回転の2つの候補（22–23）を、c1 Z の測定で見分けられるか", "",
              "揺らぎありの F5 の値 −0.11 と、揺らぎなしの値 +0.105 のときの、位相の予測（rad、3000 ショット）。", "",
              "| k | −0.11 のとき | +0.105 のとき | 差 | 統計誤差 | 差/誤差 |", "|---|---|---|---|---|---|"] + sep_lines
    (OUT / "design.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (OUT / "design.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
