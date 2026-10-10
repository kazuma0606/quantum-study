"""雑音のモデリング S4（docs/a5_modeling_plan.md）：シミュレーションに基づく推論（SBI、ニューラル事後推定 NPE）。

F5 のモデル（制御の状態ごとの、標的の回転＋ZI＋脱分極＋ジョブごとの揺らぎ）で、実データと同じ構造の合成データを大量に作り、
「データ → 事後分布」を正規化フロー（sbi の NPE、ニューラルスプラインフロー）に学習させる。

推定するパラメータ（17 個、すべて制約のない形）：
  組ごと（22-23, 142-143）に：zi、制御 |0> の回転 (x0, y0, z0)、制御 |1> の回転 (x1, y1, z1)、log p
  共通：log σ_drift（ジョブごとの揺らぎの大きさ）
ジョブごとのずれ δ（ZI へ足す、組ごとに平均 0）は、シミュレーションの中で引いて積分する（推定しない＝局外パラメータ）。
事前分布は s2_fit.py の F5 に合わせる（回転は N(0, 0.05) と N(0, 0.05√2)、p は対数正規）。σ_drift だけは扱いやすさのため
log σ_drift ～ N(log 0.003, 1) に置く（s2_fit.py は半正規分布）。観測の雑音は、s2_fit.py と同じ正規分布（統計誤差の大きさ）。

3つの使い方（--mode）：
  trial      ：試運転。速さを測り、合成データ1組の事後分布を正解と比べる
  amortized  ：事前分布全体からのシミュレーションで学習し（どのデータにも使える推定器）、
               SBC（シミュレーションに基づく較正）で区間の正直さを確かめ、実データの事後分布を NUTS と比べる
  sequential ：逐次版（SNPE）。実データの事後分布の範囲に絞ってシミュレーションし直し、学習し直すことを何回かくり返す。
               NUTS と比べる（実データ専用の推定器になるので、SBC はしない）

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s4_sbi.py --mode trial --sims 2000
    uv run python experiments/a5_trotter_noise/s4_sbi.py --mode amortized --sims 1000000 --sbc 300
    uv run python experiments/a5_trotter_noise/s4_sbi.py --mode sequential --rounds 6 --sims 50000
出力: results/s4/<tag>_summary.json と、事後分布のサンプル（_samples.npz）
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a5_data  # noqa: E402
import noise_model_jax as nm  # noqa: E402
import s2_fit  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "s4"
W = 0.05
NAMES = [f"{pair}_{n}" for pair in s2_fit.PAIRS for n in ("zi", "x0", "y0", "z0", "x1", "y1", "z1", "logp")] + ["log_sigma_drift"]
PRIOR_MEAN = np.array(([0.0] * 7 + [np.log(0.002)]) * 2 + [np.log(0.003)])
PRIOR_SD = np.array(([W] + [W * np.sqrt(2)] * 6 + [0.8]) * 2 + [1.0])
AXES = (("IX", "ZX"), ("IY", "ZY"), ("IZ", "ZZ"))


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def theta_from_params(par):
    """17 個のパラメータ（1組分）から、組ごとの 15 成分の回転 θ と p、σ_drift を作る（F5 と同じ変換）。"""
    thetas, ps = [], []
    for g in range(2):
        b = par[8 * g: 8 * g + 8]
        zi, r0, r1, logp = b[0], b[1:4], b[4:7], b[7]
        th = jnp.zeros(15).at[s2_fit.I_ZI].set(zi)
        for ax, (li, lz) in enumerate(AXES):
            th = th.at[nm.LABELS15.index(li)].set((r0[ax] + r1[ax]) / 2).at[nm.LABELS15.index(lz)].set((r0[ax] - r1[ax]) / 2)
        thetas.append(th)
        ps.append(jnp.exp(logp))
    return jnp.stack(thetas), jnp.stack(ps), jnp.exp(par[16])


def params_from_theta15(th15: np.ndarray, p: float) -> list[float]:
    """15 成分の回転と p（1組分）から、8 個のパラメータ（zi, 制御 |0> の3成分, 制御 |1> の3成分, log p）へ。"""
    g = lambda l: th15[..., nm.LABELS15.index(l)]
    out = [g("ZI")]
    out += [g(li) + g(lz) for li, lz in AXES]
    out += [g(li) - g(lz) for li, lz in AXES]
    out += [np.log(p)]
    return out


def make_simulator(prep):
    """パラメータの束 (B, 17) と乱数の鍵 → 合成データの束 (B, 観測の数)。JAX で jit・vmap する。"""
    jp = jnp.asarray(prep["job_pair"])
    n_jobs = len(prep["jobs"])
    _, ys, sds = s2_fit.predictions(jnp.zeros((n_jobs, 15)), jnp.full(n_jobs, 0.002), prep)
    sds = jnp.asarray(sds)

    def one(par, key):
        theta, p, sd = theta_from_params(par)
        k1, k2 = jax.random.split(key)
        raw = sd * jax.random.t(k1, 3.0, (n_jobs,))
        pair_mean = jax.ops.segment_sum(raw, jp, num_segments=2) / jnp.bincount(jp, length=2)
        delta = raw - pair_mean[jp]
        theta_job = theta[jp].at[:, s2_fit.I_ZI].add(delta)
        mu, _, _ = s2_fit.predictions(theta_job, p[jp], prep)
        return mu + sds * jax.random.normal(k2, mu.shape)

    return jax.jit(jax.vmap(one)), np.asarray(ys)


def simulate(sim, thetas: np.ndarray, batch: int, seed: int, label: str) -> tuple[np.ndarray, np.ndarray]:
    xs, t0 = [], time.time()
    n = len(thetas)
    for i in range(0, n, batch):
        par = jnp.asarray(thetas[i:i + batch])
        xs.append(np.asarray(sim(par, jax.random.split(jax.random.PRNGKey(seed * 1_000_003 + i), len(par)))))
        if (i // batch) % 40 == 0:
            done = i + len(par)
            rate = done / max(time.time() - t0, 1e-9)
            log(f"{label}：シミュレーション {done}/{n}（{rate:.0f} 回/秒、残り約 {(n - done) / rate / 60:.1f} 分）")
    xs = np.concatenate(xs)
    ok = np.all(np.isfinite(xs), axis=1)
    log(f"{label}：シミュレーション完了（{n / (time.time() - t0):.0f} 回/秒、有限でない結果 {np.sum(~ok)} 件を除く）")
    return thetas[ok], xs[ok]


def torch_prior(dev):
    import torch
    from torch.distributions import Independent, Normal
    return Independent(Normal(torch.tensor(PRIOR_MEAN, dtype=torch.float32, device=dev),
                              torch.tensor(PRIOR_SD, dtype=torch.float32, device=dev)), 1)


def nuts_reference() -> np.ndarray | None:
    """S2 で収束した NUTS（real_F5_D1_long）の事後分布を、17 個のパラメータの形で返す（無ければ None）。"""
    path = HERE / "results" / "s2" / "real_F5_D1_long_draws.npz"
    if not path.exists():
        return None
    d = np.load(path)
    th = d["theta"].reshape(-1, 2, 15)
    p = d["p"].reshape(-1, 2)
    cols = []
    for g in range(2):
        cols += params_from_theta15(th[:, g, :], p[:, g])
    cols.append(np.log(d["sigma_drift"].reshape(-1)))
    return np.stack(cols, axis=1)


def compare_to_nuts(samp: np.ndarray, label: str) -> list[dict]:
    ref = nuts_reference()
    rows = []
    for k, name in enumerate(NAMES):
        r = {"name": name, "sbi_median": float(np.median(samp[:, k])), "sbi_sd": float(np.std(samp[:, k]))}
        if ref is not None:
            r["nuts_median"] = float(np.median(ref[:, k]))
            r["nuts_sd"] = float(np.std(ref[:, k]))
            r["shift_in_nuts_sd"] = (r["sbi_median"] - r["nuts_median"]) / max(r["nuts_sd"], 1e-12)
            r["width_ratio"] = r["sbi_sd"] / max(r["nuts_sd"], 1e-12)
        rows.append(r)
        if ref is not None:
            log(f"{label} {name:22s} SBI {r['sbi_median']:+.4f}±{r['sbi_sd']:.4f}  NUTS {r['nuts_median']:+.4f}±{r['nuts_sd']:.4f}"
                f"（ずれ {r['shift_in_nuts_sd']:+.1f}σ、幅の比 {r['width_ratio']:.1f}）")
    return rows


def train(inference, thetas, xs, max_epochs, proposal=None):
    import torch
    t1 = time.time()
    inference.append_simulations(torch.tensor(thetas, dtype=torch.float32), torch.tensor(xs, dtype=torch.float32),
                                 proposal=proposal)
    est = inference.train(training_batch_size=512, max_num_epochs=max_epochs, show_train_summary=False)
    log(f"学習完了：{time.time() - t1:.0f} 秒、検証の損失 {inference._summary['best_validation_loss'][-1]:.2f}")
    return est


def synthetic_check(prep, trotter, probes, posterior, dev) -> tuple[list[dict], str]:
    """正解の分かる合成データ1組（s2_fit.py の合成データと同じ正解）での確かめ。"""
    import torch
    truths = s2_fit.synthetic_truth(prep)
    syn_t, syn_p = a5_data.synthetic_like(trotter, probes, truths, np.random.default_rng(123))
    _, x_syn, _ = s2_fit.predictions(jnp.zeros((len(prep["jobs"]), 15)), jnp.full(len(prep["jobs"]), 0.002),
                                     s2_fit.prepare(syn_t, syn_p))
    samp = posterior.sample((2000,), x=torch.tensor(np.asarray(x_syn), dtype=torch.float32, device=dev),
                            show_progress_bars=False).cpu().numpy()
    truth_vec = []
    for pair in s2_fit.PAIRS:
        truth_vec += params_from_theta15(truths[pair].theta15, truths[pair].p)
    truth_vec.append(np.nan)
    rows = []
    for k, name in enumerate(NAMES):
        lo, md, hi = np.percentile(samp[:, k], [5, 50, 95])
        tv = float(truth_vec[k])
        rows.append({"name": name, "truth": tv, "median": md, "lo90": lo, "hi90": hi,
                     "in90": bool(lo <= tv <= hi) if np.isfinite(tv) else None})
    hits = sum(r["in90"] for r in rows if r["in90"] is not None)
    log(f"合成データ1組：正解が 90% 区間に入った数 {hits}/{len(NAMES) - 1}")
    return rows, f"{hits}/{len(NAMES) - 1}"


def sbc(sim, posterior, n_sets: int, n_draws: int, batch: int, seed: int, dev) -> dict:
    """シミュレーションに基づく較正（Talts ら 2018）：事前分布から正解を引いて合成データを作り、事後分布の中での正解の順位を数える。
    推定が正直なら、順位は一様に分布し、68%・90% 区間に正解が入る割合はそれぞれ 0.68・0.90 になる。"""
    import torch
    rng = np.random.default_rng(seed + 777)
    th_true = PRIOR_MEAN + PRIOR_SD * rng.standard_normal((n_sets, len(NAMES)))
    th_true, xs = simulate(sim, th_true, batch, seed + 777, "SBC")
    ranks, in68, in90 = [], [], []
    t0 = time.time()
    for i in range(len(th_true)):
        s = posterior.sample((n_draws,), x=torch.tensor(xs[i], dtype=torch.float32, device=dev),
                             show_progress_bars=False).cpu().numpy()
        ranks.append(np.sum(s < th_true[i], axis=0))
        lo68, hi68 = np.percentile(s, [16, 84], axis=0)
        lo90, hi90 = np.percentile(s, [5, 95], axis=0)
        in68.append((lo68 <= th_true[i]) & (th_true[i] <= hi68))
        in90.append((lo90 <= th_true[i]) & (th_true[i] <= hi90))
        if (i + 1) % 50 == 0:
            log(f"SBC：{i + 1}/{len(th_true)}（{time.time() - t0:.0f} 秒）")
    ranks, in68, in90 = np.array(ranks), np.array(in68), np.array(in90)
    out = {"n_sets": int(len(th_true)), "n_draws": n_draws,
           "coverage68": dict(zip(NAMES, in68.mean(axis=0).round(3).tolist())),
           "coverage90": dict(zip(NAMES, in90.mean(axis=0).round(3).tolist())),
           "coverage68_mean": float(in68.mean()), "coverage90_mean": float(in90.mean())}
    hist = np.stack([np.histogram(ranks[:, k], bins=10, range=(0, n_draws))[0] for k in range(len(NAMES))])
    out["rank_hist10"] = dict(zip(NAMES, hist.tolist()))
    log(f"SBC：68% 区間の当たり率 平均 {out['coverage68_mean']:.3f}（理想 0.68）、90% 区間 {out['coverage90_mean']:.3f}（理想 0.90）")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["trial", "amortized", "sequential"], default="trial")
    ap.add_argument("--sims", type=int, default=5000, help="シミュレーションの回数（sequential では1回あたり）")
    ap.add_argument("--rounds", type=int, default=5, help="sequential のくり返しの回数")
    ap.add_argument("--batch", type=int, default=1000)
    ap.add_argument("--max-epochs", type=int, default=1000)
    ap.add_argument("--sbc", type=int, default=0, help="amortized の SBC に使う合成データの組の数（0 なら SBC しない）")
    ap.add_argument("--sbc-draws", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tag = args.tag or (args.mode if args.mode == "trial" else f"{args.mode}_{args.sims}")

    import torch
    from sbi.inference import NPE
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    trotter, probes = a5_data.load_all()
    prep = s2_fit.prepare(trotter, probes)
    sim, x_real = make_simulator(prep)
    log(f"{tag}：開始（観測 {len(x_real)} 点、パラメータ {len(NAMES)} 個、学習は {dev}）")
    prior = torch_prior(dev)
    x_o = torch.tensor(x_real, dtype=torch.float32, device=dev)
    summary = {"args": vars(args), "device": dev, "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    rng = np.random.default_rng(args.seed)

    if args.mode in ("trial", "amortized"):
        thetas = PRIOR_MEAN + PRIOR_SD * rng.standard_normal((args.sims, len(NAMES)))
        thetas, xs = simulate(sim, thetas, args.batch, args.seed, tag)
        inference = NPE(prior=prior, density_estimator="nsf", device=dev)
        est = train(inference, thetas, xs, 200 if args.mode == "trial" else args.max_epochs)
        posterior = inference.build_posterior(est)
        summary["synthetic_rows"], summary["synthetic_hits"] = synthetic_check(prep, trotter, probes, posterior, dev)
        if args.sbc > 0:
            summary["sbc"] = sbc(sim, posterior, args.sbc, args.sbc_draws, args.batch, args.seed, dev)
    else:
        inference = NPE(prior=prior, density_estimator="nsf", device=dev)
        proposal = prior
        for r in range(args.rounds):
            if r == 0:
                thetas = PRIOR_MEAN + PRIOR_SD * rng.standard_normal((args.sims, len(NAMES)))
            else:
                thetas = proposal.sample((args.sims,), show_progress_bars=False).cpu().numpy().astype(np.float64)
            thetas, xs = simulate(sim, thetas, args.batch, args.seed + r, f"{tag} 第{r + 1}回")
            est = train(inference, thetas, xs, args.max_epochs, proposal=None if r == 0 else proposal)
            posterior = inference.build_posterior(est).set_default_x(x_o)
            proposal = posterior
            samp = posterior.sample((4000,), show_progress_bars=False).cpu().numpy()
            sd = samp.std(axis=0)
            log(f"{tag} 第{r + 1}回：22-23 の制御 |0> の X 回転 {np.median(samp[:, 1]):+.4f}±{sd[1]:.4f}、"
                f"制御 |1> の Z 回転 {np.median(samp[:, 6]):+.4f}±{sd[6]:.4f}")

    samp = posterior.sample((4000,), x=x_o, show_progress_bars=False).cpu().numpy()
    np.savez_compressed(OUT / f"{tag}_samples.npz", samples=samp, names=np.array(NAMES))
    summary["real_vs_nuts"] = compare_to_nuts(samp, tag)
    summary["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (OUT / f"{tag}_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    log(f"{tag}：書き出し {OUT / tag}_summary.json")


if __name__ == "__main__":
    main()
