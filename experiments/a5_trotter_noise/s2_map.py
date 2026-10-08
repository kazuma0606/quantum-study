"""S2 の補助：事後分布の山（最も尤もらしい点、MAP）を、多くの出発点から探す。

NUTS が別々の山に落ちて収束しない（10/7、142–143 で2つの解）ので、先に山がいくつあり、どれが一番高いかを把握する。
s2_fit.py と同じモデルの「負の対数事後確率」（制約のない空間）を、出発点を変えて BFGS で最小化し、着いた点をまとめる。
出発点は、これまでに分かっている大きさの範囲からランダムに選ぶ（回転は N(0, 0.02) rad、脱分極は 0.003 のまわり、
ジョブごとのずれは 0）。事前分布からそのまま選ぶと、極端な値から始まって最適化が発散することがあった（10/8）。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s2_map.py --data synthetic --form F2 --drift D1 --starts 40
出力: results/s2/<data>_<form>_<drift>_modes.json（山ごとの値・高さ・何回たどり着いたか）と _map_init.npz（一番高い山の、制約のない空間での値）
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
from jax.flatten_util import ravel_pytree
from scipy.optimize import minimize
from numpyro.infer import init_to_sample, init_to_value
from numpyro.infer.util import constrain_fn, initialize_model

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a5_data  # noqa: E402
import noise_model_jax as nm  # noqa: E402
import s2_fit  # noqa: E402

OUT = Path(__file__).resolve().parent / "results" / "s2"


def load_prep(data: str, seed: int):
    trotter, probes = a5_data.load_all()
    prep = s2_fit.prepare(trotter, probes)
    if data == "synthetic":
        truths = s2_fit.synthetic_truth(prep)
        trotter, probes = a5_data.synthetic_like(trotter, probes, truths, np.random.default_rng(seed + 100))
        prep = s2_fit.prepare(trotter, probes)
    return prep


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", choices=["real", "synthetic"], default="synthetic")
    ap.add_argument("--form", choices=list(s2_fit.FORMS), default="F2")
    ap.add_argument("--drift", choices=["D0", "D1"], default="D1")
    ap.add_argument("--starts", type=int, default=40)
    ap.add_argument("--d-sign", type=float, choices=[1.0, -1.0], default=1.0, help="F3s で、22–23 の IZ−ZZ の符号")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    tag = f"{args.data}_{args.form}_{args.drift}" + ("" if args.form != "F3s" else ("_pos" if args.d_sign > 0 else "_neg"))
    prep = load_prep(args.data, args.seed)
    model_args = (prep, args.form, args.drift, args.d_sign)

    info = initialize_model(jax.random.PRNGKey(args.seed), s2_fit.model, model_args=model_args, init_strategy=init_to_sample)
    flat0, unravel = ravel_pytree(info.param_info.z)
    pot = jax.jit(lambda x: info.potential_fn(unravel(x)))
    vg = jax.jit(jax.value_and_grad(lambda x: info.potential_fn(unravel(x))))

    def fun(x):
        """SciPy の L-BFGS に渡す値と勾配（JAX で計算）。NaN になる点は大きな値で避けさせる。"""
        v, g = vg(jnp.asarray(x))
        v, g = float(v), np.asarray(g, dtype=float)
        if not (np.isfinite(v) and np.all(np.isfinite(g))):
            return 1e10, np.zeros_like(g)
        return v, g

    pot(flat0).block_until_ready()

    results = []
    t0 = time.time()
    for i in range(args.starts):
        rng = np.random.default_rng(1000 + i)
        values = {"p": jnp.asarray(0.003 * np.exp(rng.normal(0, 0.3, 2)))}
        for name, site in info.model_trace.items():
            if site["type"] != "sample" or site.get("is_observed"):
                continue
            shape = np.shape(site["value"])
            if name == "theta_active":
                values[name] = jnp.asarray(rng.normal(0, 0.02, shape))
            elif name == "zraw":
                values[name] = jnp.asarray(rng.normal(0, 0.3, shape))
            elif name == "iz_zz_sum":
                values[name] = jnp.asarray(rng.normal(0, 0.005, shape))
            elif name in ("iz_zz_diff_22",):
                values[name] = jnp.asarray(abs(rng.normal(0, 0.05)))
            elif name == "iz_zz_diff_142":
                values[name] = jnp.asarray(rng.normal(0, 0.02))
            elif name in ("t_job", "delta_raw"):
                values[name] = jnp.zeros(shape)
            elif name == "sigma_drift":
                values[name] = jnp.asarray(0.002)
        start = initialize_model(jax.random.PRNGKey(1000 + i), s2_fit.model, model_args=model_args,
                                 init_strategy=init_to_value(values=values))
        x0, _ = ravel_pytree(start.param_info.z)
        res = minimize(fun, np.asarray(x0, dtype=float), jac=True, method="L-BFGS-B", options={"maxiter": 3000})
        val = float(res.fun)
        if not (np.isfinite(val) and np.all(np.isfinite(np.asarray(res.x)))):
            print(f"[{time.strftime('%H:%M:%S')}] 出発点 {i + 1}/{args.starts}：最適化が発散したので飛ばす", flush=True)
            continue
        try:
            cons = constrain_fn(s2_fit.model, model_args, {}, unravel(res.x), return_deterministic=True)
        except ValueError:
            print(f"[{time.strftime('%H:%M:%S')}] 出発点 {i + 1}/{args.starts}：着いた点が不正な値なので飛ばす", flush=True)
            continue
        results.append({"start": i, "neg_log_post": val, "x": np.asarray(res.x),
                        "theta": np.asarray(cons["theta"]), "p": np.asarray(cons["p"])})
        print(f"[{time.strftime('%H:%M:%S')}] 出発点 {i + 1}/{args.starts}：負の対数事後確率 {val:.2f}（経過 {time.time() - t0:.0f} 秒）", flush=True)

    # 着いた点を、回転の角度（2組 × 15成分）が 0.002 rad 以内なら同じ山とみなしてまとめる
    results.sort(key=lambda r: r["neg_log_post"])
    modes = []
    for r in results:
        for m in modes:
            if np.max(np.abs(r["theta"] - m["theta"])) < 0.002:
                m["count"] += 1
                break
        else:
            modes.append({**r, "count": 1})
    best = modes[0]
    out = []
    for m in modes:
        entry = {"neg_log_post": m["neg_log_post"], "delta_from_best": m["neg_log_post"] - best["neg_log_post"],
                 "count": m["count"], "p": m["p"].tolist()}
        for g, pair in enumerate(s2_fit.PAIRS):
            entry[pair] = {lab: float(m["theta"][g, k]) for k, lab in enumerate(nm.LABELS15) if abs(m["theta"][g, k]) > 1e-4}
        out.append(entry)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{tag}_modes.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    np.savez(OUT / f"{tag}_map_init.npz", x=best["x"])
    print(f"山の数 {len(modes)}（出発点 {len(results)} 個から）")
    for e in out[:5]:
        print(f"  高さの差 {e['delta_from_best']:7.2f}、たどり着いた回数 {e['count']:3d}："
              + "  ".join(f"{pair} " + ", ".join(f"{k} {v:+.4f}" for k, v in e[pair].items()) for pair in s2_fit.PAIRS))
    print(f"書き出し: {OUT / tag}_modes.json、_map_init.npz")


if __name__ == "__main__":
    main()
