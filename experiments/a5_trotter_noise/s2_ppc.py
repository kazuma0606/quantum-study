"""S2 の当てはめの事後予測チェック（モデルの当てはまりの悪さを探す。docs/a5_modeling_plan.md の S5 の先取り）。

NUTS のサンプル（_draws.npz）から、すべての観測の予測を作り、次を比べる。
  1. 観測のまとまり（トロッター回路の 次数・ツイリング・組、直接の測定の 軸・対象・組）ごとの
     標準化残差 r = (y − 予測の平均) / 統計誤差 の平均と、カイ二乗 Σr²／点の数
  2. 事後予測 p 値：T(y) = Σ((y − μ_s)/σ)² と、同じ μ_s から作った複製 y_rep の T(y_rep) を、サンプル s ごとに比べた
     P(T(y_rep) ≥ T(y))。0.5 前後なら当てはまっている。0 に近いと、統計誤差では説明できないずれがある
  3. トロッター回路の残差の、深さ n への傾き（振幅が深さとともに余分に減る ＝ T1 緩和などがモデルに無い、の兆候）
  4. PSIS-LOO の k̂（0.7 を超える点は、その点だけでモデルが大きく動く ＝ 外れ値の候補）

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s2_ppc.py --tag real_F5_D1_long
出力: results/s2/<tag>_ppc.md（表）と _ppc_points.csv（点ごとの残差）
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s2_fit  # noqa: E402
from s2_fit import I_ZI, PAIRS, jax, jnp  # noqa: E402

OUT = s2_fit.OUT


def point_meta(prep) -> list[dict]:
    """predictions() と同じ順に、観測ひとつずつの説明を並べる。"""
    rows = []
    for (order, twirled), g in sorted(prep["tgroups"].items()):
        for jb, n, mask in zip(g["job"], g["n"], g["mask"]):
            for nn in n[mask]:
                rows.append({"kind": "trotter", "group": f"trotter o{order} {'tw' if twirled else 'raw'} {PAIRS[prep['job_pair'][jb]]}",
                             "pair": PAIRS[prep["job_pair"][jb]], "job": prep["jobs"][jb][1], "x": int(nn)})
    for (axis, target, c1, unflip), g in sorted(prep["pgroups"].items()):
        for jb, k in zip(g["job"], g["k"]):
            rows.append({"kind": "probe", "group": f"probe {axis} t{target}{' c1' if c1 else ''} {PAIRS[prep['job_pair'][jb]]}",
                         "pair": PAIRS[prep["job_pair"][jb]], "job": prep["jobs"][jb][1], "x": int(k)})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="real_F5_D1_long")
    ap.add_argument("--draws", type=int, default=400, help="使うサンプルの数（間引く）")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    meta = json.loads((OUT / f"{args.tag}_meta.json").read_text(encoding="utf-8"))
    a = argparse.Namespace(**meta["args"])
    prep, _ = s2_fit.build_data(a)
    d = np.load(OUT / f"{args.tag}_draws.npz")
    theta = d["theta"].reshape(-1, 2, 15)
    p = d["p"].reshape(-1, 2)
    delta = d["delta_job"].reshape(-1, d["delta_job"].shape[-1]) if "delta_job" in d.files else None
    gamma = d["gamma"].reshape(-1, 2) if "gamma" in d.files else None
    rng = np.random.default_rng(args.seed)
    idx = rng.choice(len(theta), size=min(args.draws, len(theta)), replace=False)
    jp = jnp.asarray(prep["job_pair"])

    def mu_of(th, pp, de, ga):
        tj = th[jp]
        if de is not None:
            tj = tj.at[:, I_ZI].add(de)
        return s2_fit.predictions(tj, pp[jp], prep, None if ga is None else ga[jp])[0]

    f = jax.jit(mu_of)
    mus = np.stack([np.asarray(f(jnp.asarray(theta[i]), jnp.asarray(p[i]),
                                 None if delta is None else jnp.asarray(delta[i]),
                                 None if gamma is None else jnp.asarray(gamma[i]))) for i in idx])
    _, y, sd = s2_fit.predictions(jnp.asarray(theta[0])[jp], jnp.asarray(p[0])[jp], prep)
    y, sd = np.asarray(y), np.asarray(sd)
    rows = point_meta(prep)
    if "obs_scale" in d.files:
        # 誤差棒を広げたモデルでは、広げた誤差棒で比べる（事後分布の中央値の倍率）
        sc = np.median(d["obs_scale"].reshape(-1, 2), axis=0)
        sd = sd * np.where(np.array([row["kind"] == "trotter" for row in rows]), sc[0], sc[1])
        print(f"誤差棒の倍率（中央値）：トロッター回路 {sc[0]:.2f}、直接の測定 {sc[1]:.2f}")
    assert len(rows) == len(y) == mus.shape[1]

    yrep = mus + sd * rng.standard_normal(mus.shape)
    r = (y - mus.mean(0)) / sd
    # PSIS-LOO の k̂
    try:
        import arviz as az
        ll = d["log_lik"]
        idata = az.from_dict({"posterior": {"mu0": np.zeros(ll.shape[:1])[None]},
                              "log_likelihood": {"y": ll[None]}})
        khat = np.asarray(az.loo(idata, pointwise=True).pareto_k).ravel()
    except Exception as e:  # noqa: BLE001
        print(f"k̂ を計算できなかった：{e}")
        khat = np.full(len(y), np.nan)

    lines = [f"# 事後予測チェック：{args.tag}", "",
             f"サンプル {len(idx)} 個、観測 {len(y)} 点。r は標準化残差（統計誤差の何倍ずれているか）。"
             "p_ppc は事後予測 p 値（0.5 前後なら当てはまり、0.05 未満は統計誤差で説明できないずれ）。", "",
             "| まとまり | 点 | r の平均 | Σr²/点 | p_ppc | k̂>0.7 |", "|---|---|---|---|---|---|"]
    groups = sorted({row["group"] for row in rows})
    for gname in groups + ["（全体）"]:
        m = np.array([gname == "（全体）" or row["group"] == gname for row in rows])
        t_obs = (((y[m] - mus[:, m]) / sd[m]) ** 2).sum(1)
        t_rep = (((yrep[:, m] - mus[:, m]) / sd[m]) ** 2).sum(1)
        lines.append(f"| {gname} | {m.sum()} | {r[m].mean():+.2f} | {(r[m] ** 2).mean():.2f} | "
                     f"{(t_rep >= t_obs).mean():.3f} | {int((khat[m] > 0.7).sum())} |")

    lines += ["", "## トロッター回路の残差の、深さへの傾き", "",
              "残差 y − 予測（⟨Z₀⟩ の単位）を深さ n に直線で当てはめた傾き（1 ステップあたり）と、その標準誤差。"
              "振幅の余分な減衰があれば、⟨Z₀⟩ の符号の側から 0 へ寄る向きにずれが n とともに育つ。", "",
              "| まとまり | 点 | 傾き ×10³ | 標準誤差 ×10³ | 傾き/標準誤差 |", "|---|---|---|---|---|"]
    for gname in [g for g in groups if g.startswith("trotter")]:
        m = np.array([row["group"] == gname for row in rows])
        x = np.array([row["x"] for row in rows])[m]
        if len(set(x)) < 3:
            continue
        res, w = (y - mus.mean(0))[m], 1 / sd[m] ** 2
        X = np.stack([np.ones_like(x, float), x], 1)
        cov = np.linalg.inv(X.T @ (w[:, None] * X))
        beta = cov @ X.T @ (w * res)
        lines.append(f"| {gname} | {m.sum()} | {beta[1] * 1e3:+.2f} | {np.sqrt(cov[1, 1]) * 1e3:.2f} | "
                     f"{beta[1] / np.sqrt(cov[1, 1]):+.1f} |")

    # T1 緩和の形：|0> へ戻る（⟨Z⟩ が +1 の側へ寄る）ずれは、⟨Z₀⟩ の符号によらず n に比例して正。
    # 脱分極の取り残し：0 へ縮むずれは −n·予測 に比例する。残差 = a·n + c·(−n·予測) を同時に当てはめる
    lines += ["", "## T1 の形のずれと、縮みの取り残し", "",
              "残差 = a·n + c·(−n·予測) の重みつき最小二乗。a > 0 は |0⟩ への緩和（T1）がモデルに無い兆候、"
              "c > 0 は脱分極 p の過小評価（c < 0 は過大評価）。", "",
              "| まとまり | a ×10³ | a/標準誤差 | c ×10³ | c/標準誤差 |", "|---|---|---|---|---|"]
    tmask = np.array([row["kind"] == "trotter" for row in rows])
    for gname in [g for g in groups if g.startswith("trotter")] + ["（トロッター全体）"]:
        m = tmask & np.array([gname == "（トロッター全体）" or row["group"] == gname for row in rows])
        x = np.array([row["x"] for row in rows], float)[m]
        mu = mus.mean(0)[m]
        res, w = (y - mus.mean(0))[m], 1 / sd[m] ** 2
        X = np.stack([x, -x * mu], 1)
        cov = np.linalg.inv(X.T @ (w[:, None] * X))
        beta = cov @ X.T @ (w * res)
        se = np.sqrt(np.diag(cov))
        lines.append(f"| {gname} | {beta[0] * 1e3:+.2f} | {beta[0] / se[0]:+.1f} | {beta[1] * 1e3:+.2f} | {beta[1] / se[1]:+.1f} |")

    worst = np.argsort(-np.abs(r))[:10]
    lines += ["", "## 残差の大きい点（上位 10）", "", "| まとまり | ジョブ | n または k | y | 予測 | r | k̂ |", "|---|---|---|---|---|---|---|"]
    for i in worst:
        lines.append(f"| {rows[i]['group']} | {rows[i]['job']} | {rows[i]['x']} | {y[i]:+.4f} | {mus[:, i].mean():+.4f} | "
                     f"{r[i]:+.2f} | {khat[i]:.2f} |")
    (OUT / f"{args.tag}_ppc.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (OUT / f"{args.tag}_ppc_points.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "job", "x", "y", "mu_mean", "mu_sd", "sigma", "r", "khat"])
        for i, row in enumerate(rows):
            w.writerow([row["group"], row["job"], row["x"], y[i], mus[:, i].mean(), mus[:, i].std(), sd[i], r[i], khat[i]])
    print("\n".join(lines))


if __name__ == "__main__":
    main()
