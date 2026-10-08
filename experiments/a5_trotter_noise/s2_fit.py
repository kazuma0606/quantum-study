"""雑音のモデリング S2（docs/a5_modeling_plan.md）：誤差の形 F1〜F4 と揺らぎ D0・D1 を、NUTS（NumPyro）で当てはめる。

モデル（組 g = 22-23, 142-143、ジョブ j）
  θ_g（LABELS15 の順の15成分。形ごとに使う成分だけが 0 でない）
     F1〜F3：使う成分 θ_gk = s · z_gk、z ～ N(0,1)、s ～ HalfNormal(0.05)（2組で共通の大きさ＝階層）
     F4    ：15成分すべてに正則化ホースシュー事前分布（ほとんどは 0 に近い、と置いて、要る成分をデータに選ばせる）
  p_g ～ LogNormal(log 0.002, 0.8)（CNOT ごとの脱分極。較正の CZ 誤差の中央値 0.0018〜0.0021 のまわり）
  揺らぎ D0：なし ／ D1：ジョブごとに制御の Z 位相（ZI）へずれ δ_j = σ_d · t_j、t_j ～ StudentT(3)、σ_d ～ HalfNormal(0.01)
  観測：トロッター回路の <Z_0> ～ N(モデル, 統計誤差)、直接の測定・監視用の回路の位相 ～ N(モデル, 位相の統計誤差)（差は ±π で折り返す）
すべての観測は1つの観測サイト "y" にまとめる（点ごとの対数尤度を、PSIS-LOO に使う）。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s2_fit.py --data synthetic --form F2 --drift D1
    uv run python experiments/a5_trotter_noise/s2_fit.py --data real --form F4 --drift D1
長く走るので、進み具合（NumPyro の進捗バーと、時刻つきの段階のログ）をファイルに残して実行する：
    uv run python experiments/a5_trotter_noise/s2_fit.py ... > experiments/a5_trotter_noise/results/s2/<data>_<form>_<drift>.log 2>&1
出力: results/s2/<data>_<form>_<drift>_summary.csv（事後分布の要約）と _draws.npz（サンプル、点ごとの対数尤度）と _meta.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("XLA_FLAGS", "--xla_force_host_platform_device_count=4")
import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402
import numpyro  # noqa: E402
import numpyro.distributions as dist  # noqa: E402
from numpyro.infer import MCMC, NUTS, init_to_median, log_likelihood  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a5_data  # noqa: E402
import noise_model_jax as nm  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "s2"
PAIRS = ["22-23", "142-143"]
FORMS = {
    "F1": ["ZI", "IZ"],
    "F2": ["ZI", "IX", "ZX"],
    "F3": ["ZI", "IZ", "IX", "ZX", "ZZ"],
    "F4": None,                      # 15成分すべて（ホースシュー）
    "F3s": "sumdiff",                # F3 を、IZ と ZZ の「和」と「差」で置き直したもの（下の model を参照）
}
I_ZI = nm.LABELS15.index("ZI")
KMAX = 12


def prepare(trotter: list[dict], probes: list[dict]) -> dict:
    """観測を、(次数, ツイリング) と (軸, 対象) ごとの配列にまとめる。"""
    jobs = sorted({(j["pair"], j["job"]) for j in trotter} | {(o["pair"], o["job"]) for o in probes})
    job_index = {jb: i for i, jb in enumerate(jobs)}
    job_pair = np.array([PAIRS.index(p) for p, _ in jobs])
    tgroups = {}
    for j in trotter:
        key = (j["order"], j["twirled"])
        g = tgroups.setdefault(key, {"job": [], "n": [], "mask": [], "z": [], "sem": []})
        n = np.ones(nm.NMAX, int)
        mask = np.zeros(nm.NMAX, bool)
        z = np.zeros(nm.NMAX)
        sem = np.ones(nm.NMAX)
        m = len(j["n"])
        n[:m], mask[:m], z[:m], sem[:m] = j["n"], True, j["z"], j["sem"]
        g["job"].append(job_index[(j["pair"], j["job"])])
        for k, v in (("n", n), ("mask", mask), ("z", z), ("sem", sem)):
            g[k].append(v)
    tgroups = {k: {kk: np.array(vv) for kk, vv in g.items()} for k, g in tgroups.items()}
    pgroups = {}
    for o in probes:
        key = (o["axis"], o["target"])
        g = pgroups.setdefault(key, {"job": [], "k": [], "phase": [], "sigma": []})
        g["job"].append(job_index[(o["pair"], o["job"])])
        g["k"].append(o["k"])
        g["phase"].append(o["phase"])
        g["sigma"].append(o["sigma"])
    pgroups = {k: {kk: np.array(vv) for kk, vv in g.items()} for k, g in pgroups.items()}
    return {"jobs": jobs, "job_pair": job_pair, "tgroups": tgroups, "pgroups": pgroups}


def _wrap(x):
    return jnp.arctan2(jnp.sin(x), jnp.cos(x))


def predictions(theta_job, p_job, prep):
    """ジョブごとのパラメータから、すべての観測の予測を、観測の順に並べて返す（y と sd も同じ順）。"""
    mus, ys, sds = [], [], []
    for (order, twirled), g in sorted(prep["tgroups"].items()):
        err = jax.vmap(lambda th, p: nm.error_sup(th, p, twirled))(theta_job[g["job"]], p_job[g["job"]])
        z = jax.vmap(lambda e, n: nm.trotter_z0(order, n, e))(err, jnp.asarray(g["n"]))
        mus.append(z[g["mask"]])
        ys.append(g["z"][g["mask"]])
        sds.append(g["sem"][g["mask"]])
    for (axis, target), g in sorted(prep["pgroups"].items()):
        err = jax.vmap(lambda th, p: nm.error_sup(th, p, False))(theta_job[g["job"]], p_job[g["job"]])
        e_ref, e_y = jax.vmap(lambda e: nm.probe_expectations(e, axis, target, tuple(range(KMAX + 1))))(err)
        ph = jnp.arctan2(e_y, e_ref)[jnp.arange(len(g["k"])), jnp.asarray(g["k"])]
        mus.append(g["phase"] - _wrap(g["phase"] - ph))          # 観測との差を ±π で折り返した予測
        ys.append(g["phase"])
        sds.append(g["sigma"])
    return jnp.concatenate(mus), np.concatenate(ys), np.concatenate(sds)


def model(prep, form: str, drift: str, d_sign: float = 1.0):
    active = FORMS[form]
    if active == "sumdiff":
        # F3 の IZ と ZZ を、和 u = IZ + ZZ（データがよく決める）と差 v = IZ − ZZ（ほとんど決まらない）に置き直す。
        # 22–23 では差の大きさは決まるが符号がほぼ決まらず、山が2つに分かれる（10/8 の MAP 探索）。
        # そこで 22–23 の差の符号は d_sign で固定し、正と負の2回の当てはめを予測の良さで重みづけして合わせる。
        main = ["ZI", "IX", "ZX"]
        idx = jnp.array([nm.LABELS15.index(l) for l in main])
        th_main = numpyro.sample("theta_active", dist.Normal(jnp.zeros((2, 3)), 0.05))
        u = numpyro.sample("iz_zz_sum", dist.Normal(jnp.zeros(2), 0.05 * np.sqrt(2)))
        v_mag = numpyro.sample("iz_zz_diff_22", dist.HalfNormal(0.05 * np.sqrt(2)))
        v_142 = numpyro.sample("iz_zz_diff_142", dist.Normal(0.0, 0.05 * np.sqrt(2)))
        v = jnp.stack([d_sign * v_mag, v_142])                  # PAIRS の順（22-23, 142-143）
        theta = jnp.zeros((2, 15)).at[:, idx].set(th_main)
        theta = theta.at[:, nm.LABELS15.index("IZ")].set((u + v) / 2).at[:, nm.LABELS15.index("ZZ")].set((u - v) / 2)
        theta = numpyro.deterministic("theta", theta)
    elif active is None:
        tau = numpyro.sample("tau", dist.HalfCauchy(0.01))
        lam = numpyro.sample("lam", dist.HalfCauchy(jnp.ones((2, 15))))
        c2 = numpyro.sample("c2", dist.InverseGamma(2.0, 2.0 * 0.05**2))          # 大きな成分の上限の目安 約 0.05 rad
        lam_t = jnp.sqrt(c2 * lam**2 / (c2 + tau**2 * lam**2))
        zraw = numpyro.sample("zraw", dist.Normal(jnp.zeros((2, 15)), 1.0))
        theta = numpyro.deterministic("theta", tau * lam_t * zraw)
    else:
        # θ を s・z と分けず、直接（中心化した形で）置く。データが θ を強く決めるので、分けると
        # 「s × z = 一定」に沿った細長い谷ができて NUTS が遅くなる（10/7 の最初の実行で確認）
        # 組が2つしかないので、組どうしで共有する大きさ s はデータからほとんど決まらない（10/7 の2回目の実行で R-hat 2.5）。
        # 組が増えるまでは、固定の事前分布 N(0, 0.05 rad) を置く
        idx = jnp.array([nm.LABELS15.index(l) for l in active])
        th_act = numpyro.sample("theta_active", dist.Normal(jnp.zeros((2, len(active))), 0.05))
        theta = numpyro.deterministic("theta", jnp.zeros((2, 15)).at[:, idx].set(th_act))
    p = numpyro.sample("p", dist.LogNormal(jnp.full(2, np.log(0.002)), 0.8))
    jp = jnp.asarray(prep["job_pair"])
    theta_job = theta[jp]
    if drift == "D1":
        sd = numpyro.sample("sigma_drift", dist.HalfNormal(0.01))
        # δ を σ・t と分けず、直接置く（中心化）。監視用の回路などでずれがよく決まるジョブでは、分けると
        # 「σ × t = 一定」に沿って曲がった谷ができ、質量行列では追えずに NUTS が遅くなった（10/8 に確認）
        t = numpyro.sample("delta_raw", dist.StudentT(3.0, jnp.zeros(len(prep["jobs"])), sd)) / sd
        # 組ごとに平均 0 にする：組全体のずれは theta の ZI が、ジョブごとの違いは delta が担う
        # （平均 0 にしないと、全ジョブのずれに同じ値を足して ZI から引いても予測が変わらず、尾根ができる）
        raw = sd * t
        pair_mean = jax.ops.segment_sum(raw, jp, num_segments=2) / jnp.bincount(jp, length=2)
        delta = numpyro.deterministic("delta_job", raw - pair_mean[jp])
        theta_job = theta_job.at[:, I_ZI].add(delta)
    mu, y, sd_obs = predictions(theta_job, p[jp], prep)
    numpyro.sample("y", dist.Normal(mu, sd_obs), obs=y)


def synthetic_truth(prep) -> dict:
    """合成データの正解：既定の値（これまでの当てはめに近い）に、ジョブごとの小さなずれと、1本だけ大きな跳びを入れる。"""
    truths = nm.default_truth()
    rng = np.random.default_rng(7)
    for (pair, job) in prep["jobs"]:
        truths[pair].job_offsets[job] = float(rng.normal(0, 0.001))
    jump_job = a5_data.load_trotter()[-10]["job"]                       # 監視用の回路の最初のジョブ（19:49）
    truths["22-23"].job_offsets[jump_job] = 0.006
    return truths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", choices=["real", "synthetic"], default="synthetic")
    ap.add_argument("--form", choices=list(FORMS), default="F2")
    ap.add_argument("--drift", choices=["D0", "D1"], default="D1")
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--chains", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-tree-depth", type=int, default=8, help="1回の更新で使う勾配の数の上限は 2^深さ - 1")
    ap.add_argument("--d-sign", type=float, choices=[1.0, -1.0], default=1.0, help="F3s で、22–23 の IZ−ZZ の符号")
    ap.add_argument("--init", choices=["median", "map"], default="median",
                    help="map：s2_map.py で見つけた一番高い山（_map_init.npz）の近くから、チェーンごとに少しずらして始める")
    args = ap.parse_args()

    trotter, probes = a5_data.load_all()
    prep = prepare(trotter, probes)
    truth_meta = None
    if args.data == "synthetic":
        truths = synthetic_truth(prep)
        trotter, probes = a5_data.synthetic_like(trotter, probes, truths, np.random.default_rng(args.seed + 100))
        prep = prepare(trotter, probes)
        truth_meta = {pair: {"theta": dict(zip(nm.LABELS15, tr.theta15.tolist())), "p": tr.p,
                             "job_offsets": tr.job_offsets} for pair, tr in truths.items()}

    tag = f"{args.data}_{args.form}_{args.drift}" + ("" if args.form != "F3s" else ("_pos" if args.d_sign > 0 else "_neg"))

    def log(msg: str) -> None:
        print(f"[{time.strftime('%H:%M:%S')}] {tag}：{msg}", flush=True)

    log(f"開始（観測 {sum(int(g['mask'].sum()) for g in prep['tgroups'].values()) + sum(len(g['k']) for g in prep['pgroups'].values())} 点、"
        f"チェーン {args.chains}、ウォームアップ {args.warmup}、サンプル {args.samples}）")

    t0 = time.time()
    init_params, inv_mass = None, None
    if args.init == "map":
        from jax.flatten_util import ravel_pytree
        from numpyro.infer.util import initialize_model
        info = initialize_model(jax.random.PRNGKey(args.seed), model, model_args=(prep, args.form, args.drift, args.d_sign))
        _, unravel = ravel_pytree(info.param_info.z)
        x_map = np.load(OUT / f"{tag}_map_init.npz")["x"]
        rng = np.random.default_rng(args.seed)
        starts = [unravel(jnp.asarray(x_map + rng.normal(0, 1e-3, x_map.shape))) for _ in range(args.chains)]
        init_params = starts[0] if args.chains == 1 else jax.tree_util.tree_map(lambda *xs: jnp.stack(xs), *starts)
        # MAP での曲がり具合（ヘッセ行列）の逆行列を、NUTS の歩幅の形（質量行列）の初期値にする。
        # 事後分布の幅は成分によって 1000 倍以上違い、相関もあるので、最初から形を教えると更新が速くなる
        H = np.asarray(jax.hessian(lambda x: info.potential_fn(unravel(x)))(jnp.asarray(x_map)))
        w, V = np.linalg.eigh((H + H.T) / 2)
        inv_mass = (V / np.clip(w, 1e-8 * w.max(), None)) @ V.T
        log(f"一番高い山（MAP）の近くから始める（質量行列はヘッセ行列から。固有値の比 {w.max() / max(w.min(), 1e-300):.1e}）")
    # 進み具合は NumPyro の進捗バー（チェーンごと、標準エラー出力）に出る。ファイルに残すときは、出力をログファイルへ向けて実行する
    kernel = NUTS(model, init_strategy=init_to_median, target_accept_prob=0.9, dense_mass=True,
                  max_tree_depth=args.max_tree_depth,
                  inverse_mass_matrix=None if args.init != "map" else jnp.asarray(inv_mass))
    mcmc = MCMC(kernel, num_warmup=args.warmup, num_samples=args.samples, num_chains=args.chains,
                chain_method="parallel", progress_bar=True)
    mcmc.run(jax.random.PRNGKey(args.seed), prep, args.form, args.drift, args.d_sign, extra_fields=("diverging", "num_steps"),
             init_params=init_params)
    samples = jax.block_until_ready(mcmc.get_samples(group_by_chain=True))   # JAX は非同期に計算するので、終わるのを待ってから時刻を記録する
    elapsed = time.time() - t0
    log(f"サンプリング終了（{elapsed:.0f} 秒）。後処理中")
    ll = log_likelihood(model, mcmc.get_samples(), prep, args.form, args.drift, args.d_sign)["y"]
    extra = mcmc.get_extra_fields(group_by_chain=True)
    divergences = int(np.sum(np.asarray(extra["diverging"])))
    steps = np.asarray(extra["num_steps"])
    cap = 2**args.max_tree_depth - 1
    log(f"1回の更新あたりの勾配の数：平均 {steps.mean():.0f}、最大 {steps.max()}（上限 {cap}、上限に達した割合 {np.mean(steps >= cap):.0%}）、発散 {divergences}")

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"{tag}_draws.npz", log_lik=np.asarray(ll),
                        **{k: np.asarray(v) for k, v in samples.items()})
    import arviz as az
    idata = az.from_dict({"posterior": {k: np.asarray(v) for k, v in samples.items() if k in ("theta", "p", "sigma_drift", "delta_job", "s", "tau")}})
    summ = az.summary(idata)
    summ.to_csv(OUT / f"{tag}_summary.csv")
    meta = {"args": vars(args), "elapsed_s": elapsed, "divergences": divergences, "n_obs": int(ll.shape[1]),
            "num_steps_mean": float(steps.mean()), "num_steps_max": int(steps.max()), "tree_cap_fraction": float(np.mean(steps >= cap)),
            "jobs": [list(jb) for jb in prep["jobs"]], "labels15": nm.LABELS15, "truth": truth_meta,
            "numpyro": numpyro.__version__, "jax": jax.__version__}
    (OUT / f"{tag}_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"{tag}：{elapsed:.0f} 秒、発散 {divergences}、観測 {ll.shape[1]} 点")
    print(f"書き出し: {OUT / tag}_*")


if __name__ == "__main__":
    main()
