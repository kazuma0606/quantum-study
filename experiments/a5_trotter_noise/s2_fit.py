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
    "F5": "branch",                  # 制御の状態ごとの、標的の回転（制御 |0> で3成分、|1> で3成分）＋ ZI
}
I_ZI = nm.LABELS15.index("ZI")
KMAX = 12
KMAX_T1 = 24                                # T1 専用の回路の、CX の組の回数の上限（既定。データの k がこれより大きければ、そちらに合わせる）


def kmax_t1(prep) -> int:
    """T1 専用の回路の予測を作る k の上限：データの最大の k（KMAX_T1 より小さければ KMAX_T1）。10/17 の監査：k = 32, 48 の
    データを渡すと、上限 24 までしか予測を作らず添字が範囲外になっていた。"""
    ks = [int(np.max(g["k"])) for g in prep.get("zgroups", {}).values() if len(g["k"])]
    return max([KMAX_T1] + ks)
GAMMA_T1 = 6e-4                            # CX ごとの振幅減衰の目安（0.1 μs / 160 μs）
CALIB_R = np.array([0.00182, 0.00213])     # 較正の CZ 誤差の中央値（113 日分、22-23 と 142-143。calibration_history_ibm_fez.csv）


def _nonneg_int(v: str) -> int:
    """引数用：0 以上の整数だけを受け付ける（負の k は配列の末尾を指し、生成と尤度で別の回路になるため。10/17 の監査）。"""
    k = int(v)
    if k < 0:
        raise argparse.ArgumentTypeError(f"0 以上の整数にする：{v}")
    return k


def add_common_args(ap) -> None:
    """s2_fit.py と s2_map.py で共通の引数（同じモデル・同じデータ・同じ名前にするため）。"""
    ap.add_argument("--data", choices=["real", "synthetic"], default="synthetic")
    ap.add_argument("--form", choices=list(FORMS), default="F2")
    ap.add_argument("--drift", choices=["D0", "D1"], default="D1")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--d-sign", type=float, choices=[1.0, -1.0], default=1.0, help="F3s で、22–23 の IZ−ZZ の符号")
    ap.add_argument("--prior-width", type=float, default=0.05, help="コヒーレントな回転の事前分布の幅（rad）")
    ap.add_argument("--calib", action="store_true",
                    help="較正の値を事前分布に入れる：0.8Σθ² + 0.75p が較正の CZ 誤差のまわり（対数正規、幅 0.5）")
    ap.add_argument("--label", default="", help="結果のファイル名の末尾に付ける名前（同じ設定を、サンプル数や種を変えて回すとき）")
    ap.add_argument("--t1", action="store_true", help="CX ごとの振幅減衰（T1 緩和）を入れる")
    ap.add_argument("--obs-scale", action="store_true", help="誤差棒を広げる係数（トロッター回路・直接の測定で別々）を入れる")
    ap.add_argument("--drop-trotter", nargs="*", help="トロッター回路の点を抜く（ジョブ ID:次数:n。外れ値の影響を見るとき。--label で名前を変える）")
    ap.add_argument("--with-c1-hw", action="store_true", help="10/12 の実機の、制御 |1> の Z 回転の直接の測定を加える")
    ap.add_argument("--mixed-job", action="store_true",
                    help="合成データに、来月の測り方（1本のジョブにトロッター回路・監視用の回路・制御 |1> の Z の測定を混ぜる）を組ごとに加える")
    ap.add_argument("--t1-probe", action="store_true", help="--mixed-job に、T1 専用の回路（制御 |0>・|1>、k=2〜24）を加える")
    ap.add_argument("--t1-shots", type=int, help="T1 専用の回路のショット数（既定は直接の測定と同じ 3000）")
    ap.add_argument("--t1-ks", type=_nonneg_int, nargs="+", help="T1 専用の回路の CX の組の回数の並び（既定 2 4 8 16 24、0 以上の整数）")
    ap.add_argument("--syn-ro", type=float, nargs=2,
                    help="合成データの T1 専用の回路に、読み出しの誤り（e01 = P(1|0)、e10 = P(0|1)）を入れる")
    ap.add_argument("--zcorr", action="store_true",
                    help="T1 専用の回路の制御と標的の <Z>（同じショットの同時測定）を、相関つきの2変量正規分布で数える（10/17 の監査）")
    ap.add_argument("--ro-model", action="store_true",
                    help="T1 専用の回路の <Z> に、読み出しの倍率とずれ（組・量子ビットごと）を推定するパラメータを入れる")
    ap.add_argument("--truth-no-t1", action="store_true", help="--truth-from の当てはめに T1 があっても、正解の T1 を 0 にする")
    ap.add_argument("--truth-new-c1z", type=float,
                    help="--mixed-job のジョブだけ、22–23 の制御 |1> の Z 回転をこの値にする（「時期で回転が変わった」世界）")
    ap.add_argument("--split-shrink", type=float,
                    help="--split-hw で、来月の回転を「昔の回転＋変化 Δ」と置き、Δ ～ N(0, この値) で縮める")
    ap.add_argument("--split-hw", action="store_true",
                    help="--with-c1-hw のジョブだけ、22–23 の制御 |1> の Z 回転を別のパラメータにする（時期で分けるモデル）")
    ap.add_argument("--robust", action="store_true", help="観測の誤差を t 分布（自由度 4）にする（外れ値に強い尤度）")
    ap.add_argument("--obs-scale-pair", action="store_true",
                    help="誤差棒の倍率を、組ごと・種類ごと（トロッター回路／直接の測定）に別々に置く（--obs-scale の代わり）")
    ap.add_argument("--drop-probe", nargs="*", help="直接の測定の点を抜く（ジョブ ID:軸:対象:k）")
    ap.add_argument("--truth-from",help="合成データの正解を、このタグの NUTS の事後平均（回転・p・ジョブごとのずれ）から作る")
    ap.add_argument("--truth-c1z", type=float, help="合成データの正解の、22–23 の制御 |1> の Z 回転（rot_c1 の z）を置き換える")
    ap.add_argument("--c1-design", choices=["all", "rec"], default="all",
                    help="--extra-c1 の測定：all＝両方の組で X と Z（k=2,4,8,12）、rec＝S6 の推奨（Z だけ、22–23 は k=1〜4、142–143 は k=2〜12）")
    ap.add_argument("--syn-noise", type=float, nargs=2, default=[1.0, 1.0],
                    help="合成データのばらつきの倍率（トロッター回路、直接の測定）。実データの事後予測チェックでは約 1.4、1.35")
    ap.add_argument("--extra-c1", action="store_true",
                    help="合成データに、制御を |1> にした直接の測定を加える（来月の測定の設計の下調べ）")


def make_tag(args) -> str:
    tag = f"{args.data}_{args.form}_{args.drift}"
    if args.form == "F3s":
        tag += "_pos" if args.d_sign > 0 else "_neg"
    if args.prior_width != 0.05:
        tag += f"_w{args.prior_width:g}"
    if args.calib:
        tag += "_calib"
    if getattr(args, "t1", False):
        tag += "_t1"
    if getattr(args, "obs_scale", False):
        tag += "_os"
    if getattr(args, "obs_scale_pair", False):
        tag += "_osp"
    if getattr(args, "robust", False):
        tag += "_rob"
    if getattr(args, "with_c1_hw", False):
        tag += "_hw1"
    if getattr(args, "split_hw", False):
        tag += "_split"
        if getattr(args, "split_shrink", None):
            tag += f"shr{args.split_shrink:g}"
    if getattr(args, "mixed_job", False):
        tag += "_mix"
    if getattr(args, "t1_probe", False):
        tag += "_t1p"
    if getattr(args, "ro_model", False):
        tag += "_ro"
    if getattr(args, "zcorr", False):
        tag += "_zc"
    # 合成データの条件も名前に入れる（同じ --label で条件だけ変えると結果が上書きされるため。10/14 の監査）。
    # 10/14 の結果のファイル名は、これを入れる前の名前のまま
    if getattr(args, "syn_ro", None):
        tag += f"_sro{args.syn_ro[0]:g}-{args.syn_ro[1]:g}"
    if getattr(args, "t1_shots", None):
        tag += f"_t1s{args.t1_shots}"
    if getattr(args, "t1_ks", None):
        tag += "_t1k" + "-".join(map(str, args.t1_ks))
    if args.extra_c1:
        tag += "_c1" if getattr(args, "c1_design", "all") == "all" else "_c1rec"
    if args.label:
        tag += f"_{args.label}"
    return tag


def model_opts(args) -> dict:
    return {"width": args.prior_width, "calib": args.calib, "t1": getattr(args, "t1", False),
            "obs_scale": getattr(args, "obs_scale", False), "obs_scale_pair": getattr(args, "obs_scale_pair", False),
            "robust": getattr(args, "robust", False), "split_hw": getattr(args, "split_hw", False),
            "ro_model": getattr(args, "ro_model", False), "zcorr": getattr(args, "zcorr", False),
            "split_shrink": getattr(args, "split_shrink", None),
            "hw_jobs": split_jobs(args)}


def split_jobs(args) -> list[str]:
    """時期で分けるモデル（--split-hw）で、22–23 の制御 |1> の Z 回転を別にするジョブ：
    合成データの来月のジョブ（--mixed-job）、または 10/12 の実機のジョブ（--with-c1-hw）。"""
    if not getattr(args, "split_hw", False):
        return []
    if getattr(args, "mixed_job", False):
        return [a5_data.MIXED_JOB.format(pair="22-23")]
    return sorted({o["job"] for o in a5_data.load_c1_probes()})


def build_data(args):
    """実データ、または正解の分かる合成データ（必要なら制御 |1> の直接の測定を加える）を作り、prepare する。"""
    trotter, probes = a5_data.load_all(with_c1=getattr(args, "with_c1_hw", False))
    for spec in getattr(args, "drop_trotter", None) or []:
        # 外れ値の影響を見るため、トロッター回路の1点を抜く（ジョブ ID:次数:n）
        job, order, n = spec.split(":")
        hits = [j for j in trotter if j["job"] == job and j["order"] == int(order) and int(n) in j["n"]]
        assert len(hits) == 1, f"抜く点が見つからない：{spec}"
        j = hits[0]
        keep = j["n"] != int(n)
        for key in ("n", "z", "sem", "z_trot"):
            j[key] = j[key][keep]
    for spec in getattr(args, "drop_probe", None) or []:
        # 直接の測定・監視用の回路の1点を抜く（ジョブ ID:軸:対象:k）
        job, axis, target, k = spec.split(":")
        hits = [i for i, o in enumerate(probes) if o["job"] == job and o["axis"] == axis
                and o["target"] == int(target) and o["k"] == int(k)]
        assert len(hits) == 1, f"抜く点が見つからない：{spec}（{len(hits)} 件）"
        probes = [o for i, o in enumerate(probes) if i != hits[0]]
    prep = prepare(trotter, probes)
    truth_meta = None
    if args.data == "synthetic":
        if getattr(args, "truth_c1z", None) is not None and not getattr(args, "truth_from", None):
            raise ValueError("--truth-c1z は --truth-from と一緒に使う（既定の正解には適用しない）")
        truths = truth_from_fit(prep, args.truth_from, args.truth_c1z) if getattr(args, "truth_from", None) \
            else synthetic_truth(prep)
        rng = np.random.default_rng(args.seed + 100)
        noise = tuple(getattr(args, "syn_noise", [1.0, 1.0]))
        if getattr(args, "truth_new_c1z", None) is not None:
            if not getattr(args, "mixed_job", False):
                raise ValueError("--truth-new-c1z は --mixed-job と一緒に使う")
            tr = truths["22-23"]
            vals = dict(zip(nm.LABELS15, tr.theta15))
            c0z = vals["IZ"] + vals["ZZ"]
            th = tr.theta15.copy()
            th[nm.LABELS15.index("IZ")], th[nm.LABELS15.index("ZZ")] = (c0z + args.truth_new_c1z) / 2, (c0z - args.truth_new_c1z) / 2
            tr.job_theta[a5_data.MIXED_JOB.format(pair="22-23")] = th
        if getattr(args, "truth_no_t1", False):
            # T1 なしの世界：昔のデータも来月のジョブも、T1 を入れずに作る（10/13 の監査で、昔のデータを作ったあとに
            # 外していた不具合を直した）
            for tr in truths.values():
                tr.gamma = None
        trotter, probes = a5_data.synthetic_like(trotter, probes, truths, rng, noise_scale=noise)
        if getattr(args, "mixed_job", False):
            rng_mix = np.random.default_rng(args.seed + 300)
            for pair, tr in truths.items():
                tr.job_offsets[a5_data.MIXED_JOB.format(pair=pair)] = float(rng_mix.normal(0, 0.0015))
            t_mix, p_mix = a5_data.synthetic_mixed_job(truths, rng_mix, noise_scale=noise,
                                                       t1_probe=getattr(args, "t1_probe", False),
                                                       t1_shots=getattr(args, "t1_shots", None),
                                                       t1_ks=tuple(args.t1_ks) if getattr(args, "t1_ks", None) else None,
                                                       readout=tuple(args.syn_ro) if getattr(args, "syn_ro", None) else None)
            trotter, probes = trotter + t_mix, probes + p_mix
        if args.extra_c1:
            design = REC_C1_DESIGN if getattr(args, "c1_design", "all") == "rec" else None
            probes = probes + a5_data.synthetic_c1_probes(truths, np.random.default_rng(args.seed + 200),
                                                          design=design, noise_scale=noise[1])
        prep = prepare(trotter, probes)
        truth_meta = {pair: {"theta": dict(zip(nm.LABELS15, tr.theta15.tolist())), "p": tr.p,
                             "job_offsets": tr.job_offsets, "gamma": tr.gamma} for pair, tr in truths.items()}
    return prep, truth_meta


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
    pgroups, zgroups = {}, {}
    for o in probes:
        if o.get("kind") == "zpop":
            # T1 専用の回路（制御を |0>／|1> に準備し CX の組を k 回、量子ビット q の <Z>）
            g = zgroups.setdefault((o["control_one"], o["qubit"]), {"job": [], "k": [], "z": [], "sigma": [], "shots": []})
            g["job"].append(job_index[(o["pair"], o["job"])])
            g["k"].append(o["k"])
            g["z"].append(o["z"])
            g["sigma"].append(o["sigma"])
            g["shots"].append(o.get("shots", 0))
            continue
        key = (o["axis"], o["target"], o.get("control_one", False), o.get("unflip", False))
        g = pgroups.setdefault(key, {"job": [], "k": [], "phase": [], "sigma": []})
        g["job"].append(job_index[(o["pair"], o["job"])])
        g["k"].append(o["k"])
        g["phase"].append(o["phase"])
        g["sigma"].append(o["sigma"])
    pgroups = {k: {kk: np.array(vv) for kk, vv in g.items()} for k, g in pgroups.items()}
    zgroups = {k: {kk: np.array(vv) for kk, vv in g.items()} for k, g in zgroups.items()}
    return {"jobs": jobs, "job_pair": job_pair, "tgroups": tgroups, "pgroups": pgroups, "zgroups": zgroups}


def point_kind_pair(prep):
    """predictions() と同じ順に、観測ごとの (種類：0 トロッター回路／1 直接の測定, 組の番号) を返す。"""
    kind, pair = [], []
    for _, g in sorted(prep["tgroups"].items()):
        for jb, mask in zip(g["job"], g["mask"]):
            kind += [0] * int(mask.sum())
            pair += [int(prep["job_pair"][jb])] * int(mask.sum())
    for _, g in sorted(prep["pgroups"].items()):
        kind += [1] * len(g["job"])
        pair += [int(prep["job_pair"][jb]) for jb in g["job"]]
    for _, g in sorted(prep.get("zgroups", {}).items()):
        kind += [1] * len(g["job"])
        pair += [int(prep["job_pair"][jb]) for jb in g["job"]]
    return np.array(kind), np.array(pair)


def _wrap(x):
    return jnp.arctan2(jnp.sin(x), jnp.cos(x))


def predictions(theta_job, p_job, prep, gamma_job=None):
    """ジョブごとのパラメータから、すべての観測の予測を、観測の順に並べて返す（y と sd も同じ順）。
    gamma_job があれば、CX ごとの振幅減衰（T1）も入れる。"""
    mus, ys, sds = [], [], []
    for (order, twirled), g in sorted(prep["tgroups"].items()):
        if gamma_job is None:
            err = jax.vmap(lambda th, p: nm.error_sup(th, p, twirled))(theta_job[g["job"]], p_job[g["job"]])
        else:
            err = jax.vmap(lambda th, p, ga: nm.error_sup(th, p, twirled, ga))(theta_job[g["job"]], p_job[g["job"]],
                                                                               gamma_job[g["job"]])
        z = jax.vmap(lambda e, n: nm.trotter_z0(order, n, e))(err, jnp.asarray(g["n"]))
        mus.append(z[g["mask"]])
        ys.append(g["z"][g["mask"]])
        sds.append(g["sem"][g["mask"]])
    for (axis, target, c1, unflip), g in sorted(prep["pgroups"].items()):
        if gamma_job is None:
            err = jax.vmap(lambda th, p: nm.error_sup(th, p, False))(theta_job[g["job"]], p_job[g["job"]])
        else:
            err = jax.vmap(lambda th, p, ga: nm.error_sup(th, p, False, ga))(theta_job[g["job"]], p_job[g["job"]],
                                                                             gamma_job[g["job"]])
        e_ref, e_y = jax.vmap(lambda e: nm.probe_expectations(e, axis, target, tuple(range(KMAX + 1)),
                                                              control_one=c1, unflip=unflip))(err)
        ph = jnp.arctan2(e_y, e_ref)[jnp.arange(len(g["k"])), jnp.asarray(g["k"])]
        mus.append(g["phase"] - _wrap(g["phase"] - ph))          # 観測との差を ±π で折り返した予測
        ys.append(g["phase"])
        sds.append(g["sigma"])
    for (c1, q), g in sorted(prep.get("zgroups", {}).items()):
        if gamma_job is None:
            err = jax.vmap(lambda th, p: nm.error_sup(th, p, False))(theta_job[g["job"]], p_job[g["job"]])
        else:
            err = jax.vmap(lambda th, p, ga: nm.error_sup(th, p, False, ga))(theta_job[g["job"]], p_job[g["job"]],
                                                                             gamma_job[g["job"]])
        z = jax.vmap(lambda e: nm.t1_probe_z(e, c1, tuple(range(kmax_t1(prep) + 1)))[q])(err)
        mus.append(z[jnp.arange(len(g["k"])), jnp.asarray(g["k"])])
        ys.append(g["z"])
        sds.append(g["sigma"])
    return jnp.concatenate(mus), np.concatenate(ys), np.concatenate(sds)


def model(prep, form: str, drift: str, d_sign: float = 1.0, opts: dict | None = None):
    opts = {"width": 0.05, "calib": False, "t1": False, "obs_scale": False, "obs_scale_pair": False, "robust": False,
            "ro_model": False, "zcorr": False, **(opts or {})}
    w = opts["width"]
    active = FORMS[form]
    if active == "branch":
        # 制御の状態ごとの、標的の回転：制御が |0> のとき (x0, y0, z0)、|1> のとき (x1, y1, z1)。
        # exp(-i(a IX + b ZX)) = |0><0|⊗exp(-i(a+b)X) + |1><1|⊗exp(-i(a−b)X) なので、IX = (x0+x1)/2、ZX = (x0−x1)/2（Y・Z も同じ）。
        # データがよく決める側（制御 |0>）と、ほとんど決まらない側（制御 |1>）が、最初から別のパラメータになる
        zi = numpyro.sample("zi", dist.Normal(jnp.zeros(2), w))
        r0 = numpyro.sample("rot_c0", dist.Normal(jnp.zeros((2, 3)), w * np.sqrt(2)))
        r1 = numpyro.sample("rot_c1", dist.Normal(jnp.zeros((2, 3)), w * np.sqrt(2)))
        theta = jnp.zeros((2, 15)).at[:, I_ZI].set(zi)
        for ax, (li, lz) in enumerate((("IX", "ZX"), ("IY", "ZY"), ("IZ", "ZZ"))):
            theta = theta.at[:, nm.LABELS15.index(li)].set((r0[:, ax] + r1[:, ax]) / 2)
            theta = theta.at[:, nm.LABELS15.index(lz)].set((r0[:, ax] - r1[:, ax]) / 2)
        theta = numpyro.deterministic("theta", theta)
    elif active == "sumdiff":
        # F3 の IZ と ZZ を、和 u = IZ + ZZ（データがよく決める）と差 v = IZ − ZZ（ほとんど決まらない）に置き直す。
        # 22–23 では差の大きさは決まるが符号がほぼ決まらず、山が2つに分かれる（10/8 の MAP 探索）。
        # そこで 22–23 の差の符号は d_sign で固定し、正と負の2回の当てはめを予測の良さで重みづけして合わせる。
        main = ["ZI", "IX", "ZX"]
        idx = jnp.array([nm.LABELS15.index(l) for l in main])
        th_main = numpyro.sample("theta_active", dist.Normal(jnp.zeros((2, 3)), w))
        u = numpyro.sample("iz_zz_sum", dist.Normal(jnp.zeros(2), w * np.sqrt(2)))
        v_mag = numpyro.sample("iz_zz_diff_22", dist.HalfNormal(w * np.sqrt(2)))
        v_142 = numpyro.sample("iz_zz_diff_142", dist.Normal(0.0, w * np.sqrt(2)))
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
        th_act = numpyro.sample("theta_active", dist.Normal(jnp.zeros((2, len(active))), w))
        theta = numpyro.deterministic("theta", jnp.zeros((2, 15)).at[:, idx].set(th_act))
    p = numpyro.sample("p", dist.LogNormal(jnp.full(2, np.log(0.002)), 0.8))
    if opts["calib"]:
        # 較正の値を事前分布に入れる：平均ゲート不忠実度 r ≈ 0.8Σθ² + 0.75p（ノートの式 (III-4)）が、
        # 較正の CZ 誤差のまわり（対数で幅 0.5、およそ 0.6〜1.6 倍）にある、という知識
        r = 0.8 * jnp.sum(theta**2, axis=1) + 0.75 * p
        numpyro.factor("calib", jnp.sum(dist.LogNormal(jnp.log(jnp.asarray(CALIB_R)), 0.5).log_prob(r)))
    jp = jnp.asarray(prep["job_pair"])
    theta_job = theta[jp]
    if opts.get("split_hw") and active == "branch":
        # 時期で分けるモデル：10/12 の実機のジョブ（制御 |1> の Z の測定）だけ、22–23 の制御 |1> の Z 回転を別のパラメータにする
        # （「1週間で回転が変わった」という仮説。そのジョブが測るのはこの方向だけなので、ほかの成分は共通のまま）
        hw = [i for i, (pair, job) in enumerate(prep["jobs"]) if job in opts["hw_jobs"]]
        if opts.get("split_shrink"):
            # 縮める事前分布：来月の回転 = 昔の回転 ＋ 変化 Δ、Δ ～ N(0, split_shrink)。「変わっていない」寄りに縮め、
            # 自由すぎる昔の回転が偶然のばらつきを拾って予測の良さで得をする（偽の陽性）のを防ぐ（10/19 の結果を受けて）
            dz = numpyro.sample("rot_c1z_change", dist.Normal(0.0, opts["split_shrink"]))
            r1z_hw = numpyro.deterministic("rot_c1z_hw", r1[0, 2] + dz)
        else:
            r1z_hw = numpyro.sample("rot_c1z_hw", dist.Normal(0.0, w * np.sqrt(2)))
        iz, zz = nm.LABELS15.index("IZ"), nm.LABELS15.index("ZZ")
        for i in hw:
            theta_job = theta_job.at[i, iz].set((r0[0, 2] + r1z_hw) / 2).at[i, zz].set((r0[0, 2] - r1z_hw) / 2)
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
    gamma_job = None
    if opts["t1"]:
        # CX ごとの振幅減衰 γ = 1 − exp(−t/T1)。較正の T1（中央値 約 160 μs、calibration_history_ibm_fez.csv）と、
        # CX 1回と前後の1量子ビットゲートの時間 約 0.1 μs から、γ ≈ 6×10⁻⁴ を中心に置く（対数で幅 0.7、およそ 0.5〜2 倍）
        gamma = numpyro.sample("gamma", dist.LogNormal(jnp.full(2, np.log(GAMMA_T1)), 0.7))
        gamma_job = gamma[jp]
    mu, y, sd_obs = predictions(theta_job, p[jp], prep, gamma_job)
    if opts["ro_model"] and prep.get("zgroups"):
        # 読み出しの偏り：測った <Z> = 倍率 × 本当の <Z> ＋ ずれ。倍率 = 1 − e01 − e10、ずれ = e10 − e01（組・量子ビットごと）。
        # 偏りは k によらず一定、T1 は k とともに育つので、k への依存で分けられる
        # 誤読の確率そのもの（0〜1）を置き、そこから倍率とずれを作る（10/14 の監査：倍率とずれを独立な正規分布に置くと、
        # 誤読の確率が負になる領域を許してしまう）。Beta(1.5, 40) は平均約 3.6%、95% 点で約 10%
        e01 = numpyro.sample("ro_e01", dist.Beta(jnp.full((2, 2), 1.5), 40.0))
        e10 = numpyro.sample("ro_e10", dist.Beta(jnp.full((2, 2), 1.5), 40.0))
        ro_s = numpyro.deterministic("ro_scale", 1 - e01 - e10)
        ro_b = numpyro.deterministic("ro_bias", e10 - e01)
        n_z = sum(len(g["k"]) for g in prep["zgroups"].values())
        zq = np.concatenate([np.full(len(g["k"]), q) for (c1, q), g in sorted(prep["zgroups"].items())])
        zp = np.concatenate([prep["job_pair"][g["job"]] for _, g in sorted(prep["zgroups"].items())])
        mu = mu.at[-n_z:].set(ro_s[zp, zq] * mu[-n_z:] + ro_b[zp, zq])
    else:
        e01 = e10 = None
    if opts["obs_scale"]:
        # 誤差棒の広げ方：統計誤差に入っていないばらつき（読み出し補正の不確かさなど。10/11 の事後予測チェックで約 1.3 倍）。
        # トロッター回路と、直接の測定（位相）で別々に置く
        scale = numpyro.sample("obs_scale", dist.LogNormal(jnp.zeros(2), 0.5))
        n_trot = sum(int(g["mask"].sum()) for g in prep["tgroups"].values())
        sd_obs = sd_obs * jnp.where(jnp.arange(len(y)) < n_trot, scale[0], scale[1])
    if opts["obs_scale_pair"]:
        # 誤差棒の倍率を、(種類, 組) の 2×2 で別々に置く。10/11 に、142–143 の1点を抜くと 22–23 の値まで入れ替わった
        # （倍率を2つの組で共有していたことが原因の候補）ため
        scale = numpyro.sample("obs_scale", dist.LogNormal(jnp.zeros((2, 2)), 0.5))
        kind, pair = point_kind_pair(prep)
        sd_obs = sd_obs * scale[kind, pair]
    keep = np.ones(len(y), bool)
    if opts["zcorr"] and prep.get("zgroups"):
        # T1 専用の回路では、制御と標的の <Z> を同じショットで同時に測るので、2つの値には相関がある。独立に数えると同じ情報を
        # 二重に数える（10/17 の監査）。そこで、同じ (準備, ジョブ, k) の2つの値を組にし、モデルの4通りの同時確率から
        # 1ショットの共分散 (E[ZcZt] − E[Zc]E[Zt]) / ショット数 を計算して、2変量正規分布で数える。余分なばらつき（誤差棒の倍率）は
        # 2つの値に独立にかかると置くので、相関は「ショットの共分散 / (広げた誤差棒の積)」になる
        keys = sorted(prep["zgroups"])
        n_z = sum(len(g["k"]) for g in prep["zgroups"].values())
        off = len(y) - n_z
        starts = {}
        pos = off
        for key in keys:
            starts[key] = pos
            pos += len(prep["zgroups"][key]["k"])
        zc_, zt_ = jnp.array([1.0, 1.0, -1.0, -1.0]), jnp.array([1.0, -1.0, 1.0, -1.0])
        locs, covs, obs = [], [], []
        for c1 in (False, True):
            g0, g1 = prep["zgroups"][(c1, 0)], prep["zgroups"][(c1, 1)]
            assert np.array_equal(g0["job"], g1["job"]) and np.array_equal(g0["k"], g1["k"])
            jobs = g0["job"]
            th, pp = theta_job[jobs], p[jp][jobs]
            if gamma_job is None:
                errs = jax.vmap(lambda a, b: nm.error_sup(a, b, False))(th, pp)
            else:
                errs = jax.vmap(lambda a, b, c: nm.error_sup(a, b, False, c))(th, pp, gamma_job[jobs])
            P = jax.vmap(lambda e: nm.t1_probe_probs(e, c1, tuple(range(kmax_t1(prep) + 1))))(errs)[jnp.arange(len(jobs)), jnp.asarray(g0["k"])]
            if e01 is not None:
                pr = prep["job_pair"][jobs]

                def conf(a, b):
                    return jnp.array([[1 - a, b], [a, 1 - b]])
                M = jax.vmap(lambda a0, b0, a1, b1: jnp.kron(conf(a0, b0), conf(a1, b1)))(
                    e01[pr, 0], e10[pr, 0], e01[pr, 1], e10[pr, 1])
                P = jnp.einsum("nij,nj->ni", M, P)
            ezc, ezt, ezct = P @ zc_, P @ zt_, P @ (zc_ * zt_)
            n_sh = jnp.asarray(np.maximum(g0["shots"], 1), dtype=float)
            cov = (ezct - ezc * ezt) / n_sh
            i0 = starts[(c1, 0)] + np.arange(len(jobs))
            i1 = starts[(c1, 1)] + np.arange(len(jobs))
            s0, s1 = sd_obs[i0], sd_obs[i1]
            rho = jnp.clip(cov / (s0 * s1), -0.95, 0.95)
            locs.append(jnp.stack([mu[i0], mu[i1]], -1))
            covs.append(jnp.stack([jnp.stack([s0**2, rho * s0 * s1], -1), jnp.stack([rho * s0 * s1, s1**2], -1)], -2))
            obs.append(np.stack([y[i0], y[i1]], -1))
            keep[i0] = False
            keep[i1] = False
        loc_z, cov_z = jnp.concatenate(locs), jnp.concatenate(covs)
        if opts["robust"]:
            # --robust と併用するときは、組の観測も外れ値に強い形にする：自由度 4 の2変量 t 分布（尺度行列は上の共分散。
            # 10/17 の確認：組だけ正規分布のままで、--robust が残りの観測にしか効いていなかった）
            numpyro.sample("yz", dist.MultivariateStudentT(4.0, loc_z, scale_tril=jnp.linalg.cholesky(cov_z)),
                           obs=np.concatenate(obs))
        else:
            numpyro.sample("yz", dist.MultivariateNormal(loc_z, covariance_matrix=cov_z), obs=np.concatenate(obs))
    if opts["robust"]:
        # 外れ値に強い尤度：自由度 4 の t 分布（正規分布より裾が重く、外れた点の重みが自動で下がる。深層学習の Huber 損失に近い）
        numpyro.sample("y", dist.StudentT(4.0, mu[keep], sd_obs[keep]), obs=y[keep])
    else:
        numpyro.sample("y", dist.Normal(mu[keep], sd_obs[keep]), obs=y[keep])


# S6 で選んだ制御 |1> の測定（反転を戻す Z だけ。22–23 は位相の折り返しを避けて k を小さく）
REC_C1_DESIGN = {"22-23": [("Z", True, (1, 2, 3, 4))], "142-143": [("Z", True, (2, 4, 8, 12))]}


def truth_from_fit(prep, tag: str, c1z: float | None) -> dict:
    """合成データの正解を、実データの当てはめ（NUTS）の事後平均から作る。c1z を与えれば、22–23 の制御 |1> の Z 回転だけ置き換える
    （本番の予行演習：正解が −0.11 の世界と +0.105 の世界で、推奨の測定が正しい側を選べるか）。"""
    d = np.load(OUT / f"{tag}_draws.npz")
    gamma = d["gamma"].reshape(-1, 2).mean(0) if "gamma" in d.files else None       # T1 つきの当てはめなら、正解にも T1 を入れる
    meta = json.loads((OUT / f"{tag}_meta.json").read_text(encoding="utf-8"))
    r0, r1 = d["rot_c0"].reshape(-1, 2, 3).mean(0), d["rot_c1"].reshape(-1, 2, 3).mean(0).copy()
    if c1z is not None:
        r1[0, 2] = c1z
    zi, p = d["zi"].reshape(-1, 2).mean(0), d["p"].reshape(-1, 2).mean(0)
    delta = d["delta_job"].reshape(-1, d["delta_job"].shape[-1]).mean(0)
    jobs = [tuple(j) for j in meta["jobs"]]
    truths = {}
    for g, pair in enumerate(PAIRS):
        vals = {"ZI": zi[g]}
        for ax, (li, lz) in enumerate((("IX", "ZX"), ("IY", "ZY"), ("IZ", "ZZ"))):
            vals[li], vals[lz] = (r0[g, ax] + r1[g, ax]) / 2, (r0[g, ax] - r1[g, ax]) / 2
        truths[pair] = nm.PairTruth(theta15=nm.theta_from(vals), p=float(p[g]),
                                    gamma=None if gamma is None else float(gamma[g]))
    for (pair, job), de in zip(jobs, delta):
        truths[pair].job_offsets[job] = float(de)
    # 当てはめに、今回のデータにないジョブ（10/12 の実機など）が含まれていてもよい。今回のジョブはすべて当てはめに含まれていること
    missing = set(map(tuple, prep["jobs"])) - set(jobs)
    assert not missing, f"正解の当てはめに含まれないジョブ：{missing}"
    return truths


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
    add_common_args(ap)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--chains", type=int, default=4)
    ap.add_argument("--max-tree-depth", type=int, default=8, help="1回の更新で使う勾配の数の上限は 2^深さ - 1")
    ap.add_argument("--init", choices=["median", "map"], default="median",
                    help="map：s2_map.py で見つけた一番高い山（_map_init.npz）の近くから、チェーンごとに少しずらして始める")
    ap.add_argument("--sigma-floor", type=float, default=1e-4, help="--init map で、MAP の σ_drift がこれより小さければ置き直す")
    ap.add_argument("--sigma-reset", type=float, default=1e-3, help="置き直すときの σ_drift の値")
    ap.add_argument("--map-from", help="MAP の出発点を、別のタグの _map_init.npz から読む（MAP 探索をやり直さずに NUTS だけ回すとき）")
    args = ap.parse_args()
    prep, truth_meta = build_data(args)
    tag = make_tag(args)
    margs = (prep, args.form, args.drift, args.d_sign, model_opts(args))

    def log(msg: str) -> None:
        print(f"[{time.strftime('%H:%M:%S')}] {tag}：{msg}", flush=True)

    log(f"開始（観測 {sum(int(g['mask'].sum()) for g in prep['tgroups'].values()) + sum(len(g['k']) for g in prep['pgroups'].values())} 点、"
        f"チェーン {args.chains}、ウォームアップ {args.warmup}、サンプル {args.samples}）")

    t0 = time.time()
    init_params, inv_mass = None, None
    if args.init == "map":
        from jax.flatten_util import ravel_pytree
        from numpyro.infer.util import initialize_model
        info = initialize_model(jax.random.PRNGKey(args.seed), model, model_args=margs, init_strategy=init_to_median)
        _, unravel = ravel_pytree(info.param_info.z)
        x_map = np.load(OUT / f"{args.map_from or tag}_map_init.npz")["x"]
        if "sigma_drift" in info.param_info.z:
            # 階層の広がり σ_drift は、MAP 探索で 0 へ落ちることがある（δ も 0 に寄せると事後密度がいくらでも高くなる、
            # ニールの漏斗の首）。そこから始めると NUTS が抜け出せない（10/11、制御 |1> つき合成データの seed1 で確認）。
            # 小さすぎるときは、妥当な値に置き直してから始める（制約のない空間では log σ）
            flag = {k: jnp.full(jnp.shape(v), k == "sigma_drift", float) for k, v in info.param_info.z.items()}
            i_sd = int(np.argmax(np.asarray(ravel_pytree(flag)[0])))
            if np.exp(x_map[i_sd]) < args.sigma_floor:
                log(f"MAP の σ_drift = {np.exp(x_map[i_sd]):.1e} は小さすぎる（漏斗の首）ので、{args.sigma_reset:.0e} に置き直す")
                x_map = x_map.copy()
                x_map[i_sd] = np.log(args.sigma_reset)
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
    mcmc.run(jax.random.PRNGKey(args.seed), *margs, extra_fields=("diverging", "num_steps"),
             init_params=init_params)
    samples = jax.block_until_ready(mcmc.get_samples(group_by_chain=True))   # JAX は非同期に計算するので、終わるのを待ってから時刻を記録する
    elapsed = time.time() - t0
    log(f"サンプリング終了（{elapsed:.0f} 秒）。後処理中")
    ll_all = log_likelihood(model, mcmc.get_samples(), *margs)
    # 点ごとの対数尤度：ふつうの観測は1点ずつ、--zcorr の T1 専用の回路は (制御, 標的) の組を1点として数える
    ll = jnp.concatenate([ll_all["y"]] + ([ll_all["yz"]] if "yz" in ll_all else []), axis=1)
    extra = mcmc.get_extra_fields(group_by_chain=True)
    divergences = int(np.sum(np.asarray(extra["diverging"])))
    steps = np.asarray(extra["num_steps"])
    cap = 2**args.max_tree_depth - 1
    log(f"1回の更新あたりの勾配の数：平均 {steps.mean():.0f}、最大 {steps.max()}（上限 {cap}、上限に達した割合 {np.mean(steps >= cap):.0%}）、発散 {divergences}")

    OUT.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT / f"{tag}_draws.npz", log_lik=np.asarray(ll),
                        **{k: np.asarray(v) for k, v in samples.items()})
    import arviz as az
    idata = az.from_dict({"posterior": {k: np.asarray(v) for k, v in samples.items() if k in ("theta", "p", "sigma_drift", "delta_job", "s", "tau", "gamma", "obs_scale")}})
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
