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
    s2_fit.add_common_args(ap)
    ap.add_argument("--starts", type=int, default=40)
    ap.add_argument("--start-from", metavar="TAG",
                    help="出発点を、このタグの NUTS の事後平均（zi、rot_c0、rot_c1、p、gamma）から始める（11 月の回転も 10 月の値から）")
    ap.add_argument("--p-jitter", type=float, default=0.0, metavar="SIGMA",
                    help="2 本目からの出発点で、p・gamma・dephase に exp(N(0, SIGMA)) をかけて広げる（既定 0：広げない）。"
                         "11/08 の MAP の探索は、--start-from の p（約 3×10⁻⁴）のまわりだけを探し、NUTS が見つけた p≈10⁻⁴ の領域を見落とした")
    args = ap.parse_args()
    tag = s2_fit.make_tag(args)
    prep, _ = s2_fit.build_data(args)
    model_args = (prep, args.form, args.drift, args.d_sign, s2_fit.model_opts(args))

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

    start_vals = {}
    if args.start_from:
        d = np.load(s2_fit.OUT / f"{args.start_from}_draws.npz")
        for name in ("zi", "rot_c0", "rot_c1", "p", "gamma"):
            if name in d.files:
                m = d[name].reshape((-1,) + d[name].shape[2:]).mean(0)
                start_vals[name] = m
                if name in ("zi", "rot_c0", "rot_c1"):
                    start_vals[f"{name}_p2"] = m
        print(f"出発点：{args.start_from} の事後平均（{sorted(start_vals)}）", flush=True)

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
            elif name in ("zi", "zi_p2"):
                values[name] = jnp.asarray(rng.normal(0, 0.005, shape))
            elif name in ("rot_c0", "rot_c0_p2"):
                values[name] = jnp.asarray(rng.normal(0, 0.01, shape))
            elif name in ("rot_c1", "rot_c1_p2"):
                values[name] = jnp.asarray(rng.normal(0, 0.02, shape))
            elif name in ("zi_change", "rot_c0_change", "rot_c1_change"):
                # --split-period-shrink の変化 Δ。指定しないと、既定の −2〜2 の一様乱数から始まってしまう（2026-11-07）
                values[name] = jnp.asarray(rng.normal(0, 0.01, shape))
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
            elif name == "gamma":
                values[name] = jnp.asarray(s2_fit.GAMMA_T1 * np.exp(rng.normal(0, 0.3, shape)))
            elif name in ("ro_e01", "ro_e10"):
                values[name] = jnp.asarray(np.clip(0.02 + rng.normal(0, 0.005, shape), 0.005, 0.1))
            elif name in ("obs_scale", "obs_scale_zpop", "obs_scale_p2"):
                values[name] = jnp.asarray(np.exp(rng.normal(0.2, 0.1, shape)))
            elif name == "dephase":
                values[name] = jnp.asarray(2e-4 * np.exp(rng.normal(0, 0.3, shape)))
            elif name == "flip_ratio":
                # 1（対称な脱分極）から 0.2 くらいまでを広く探す
                values[name] = jnp.asarray(np.exp(rng.uniform(np.log(0.2), 0.0, shape)))
        if start_vals:
            # --start-from：別の当てはめの事後平均から始める（1 本目はそのまま、2 本目からは回転に 0.002 rad の揺らぎを足す）。
            # 11 月の回転（*_p2）も、10 月の値から始める
            for name, v in start_vals.items():
                if name not in values:
                    continue
                jit = rng.normal(0, 0.002, np.shape(v)) if (i > 0 and name.startswith(("zi", "rot_"))) else 0.0
                values[name] = jnp.asarray(v + jit)
        if args.p_jitter > 0 and i > 0:
            for name in ("p", "gamma", "dephase"):
                if name in values:
                    v = np.asarray(values[name])
                    values[name] = jnp.asarray(v * np.exp(rng.normal(0, args.p_jitter, np.shape(v))))
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
                        "theta": np.asarray(cons["theta"]), "p": np.asarray(cons["p"]),
                        # --split-period の 11 月の回転（2026-11-10、Codex の監査 #98：10 月の回転だけで山を分けると、11 月の回転だけが違う山をまとめてしまう）
                        "theta_p2": np.asarray(cons["theta_p2"]) if "theta_p2" in cons else None,
                        "extra": {k: np.asarray(cons[k]).tolist() for k in ("gamma", "obs_scale", "sigma_drift", "dephase", "flip_ratio", "obs_scale_zpop", "obs_scale_p2") if k in cons}})
        print(f"[{time.strftime('%H:%M:%S')}] 出発点 {i + 1}/{args.starts}：負の対数事後確率 {val:.2f}（経過 {time.time() - t0:.0f} 秒）", flush=True)

    # 着いた点を、回転の角度（2組 × 15成分。--split-period では 10 月と 11 月の両方）が 0.002 rad 以内なら同じ山とみなしてまとめる
    def angles(r):
        return r["theta"] if r["theta_p2"] is None else np.concatenate([r["theta"], r["theta_p2"]])
    results.sort(key=lambda r: r["neg_log_post"])
    modes = []
    for r in results:
        for m in modes:
            if np.max(np.abs(angles(r) - angles(m))) < 0.002:
                m["count"] += 1
                break
        else:
            modes.append({**r, "count": 1})
    best = modes[0]
    out = []
    for m in modes:
        entry = {"neg_log_post": m["neg_log_post"], "delta_from_best": m["neg_log_post"] - best["neg_log_post"],
                 "count": m["count"], "p": m["p"].tolist(), **m["extra"]}
        for g, pair in enumerate(s2_fit.PAIRS):
            entry[pair] = {lab: float(m["theta"][g, k]) for k, lab in enumerate(nm.LABELS15) if abs(m["theta"][g, k]) > 1e-4}
            if m["theta_p2"] is not None:
                entry[pair + "_p2"] = {lab: float(m["theta_p2"][g, k]) for k, lab in enumerate(nm.LABELS15)
                                       if abs(m["theta_p2"][g, k]) > 1e-4}
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
