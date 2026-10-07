"""雑音のモデリング（docs/a5_modeling_plan.md の S1）：実機のデータを1つの形にまとめる読み込みと、同じ形の合成データ。

まとめる形：
  trotter：トロッター回路の1本のジョブ = {pair, job, time, order, twirled, dd, n[], z[], sem[], z_trot[], z_exact}
           z は読み出しを補正した <Z_0>、z_trot は雑音なしのトロッター回路の値
  probe  ：CNOT の組だけの回路（直接の測定、監視用の回路）の位相 = {pair, job, time, axis, target, k, phase, sigma}
           axis="Z"：target を |+> にした Z 回転、axis="X"：標的を |0> にした X 回転。phase = atan2(<Y>, <基準>)
time は実際の実行時刻（分かるもの）または投入時刻（UTC、datetime）。
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

import noise_model_jax as nm

RES = Path(__file__).resolve().parent / "results"
JST = timezone(timedelta(hours=9))
NMAX = nm.NMAX

TROTTER_JOBS = [  # (ファイル名の接頭辞, 組, 次数, ツイリング, 動的デカップリング)
    ("hardware_pilot_", "22-23", 1, False, False),
    ("hardware_main_o1_", "22-23", 1, False, False),
    ("hardware_main_o2_", "22-23", 2, False, False),
    ("hardware_dd_xy4_o1_", "22-23", 1, False, True),
    ("hardware_twirl_o1_", "22-23", 1, True, False),
    ("hardware_day2_o1_", "22-23", 1, False, False),
    ("hardware_day2_o2_", "22-23", 2, False, False),
    ("hardware_q142_o1_", "142-143", 1, False, False),
    ("hardware_q142_o2_", "142-143", 2, False, False),
    ("hardware_q142_twirl_o1_", "142-143", 1, True, False),
    ("hardware_q142_twirl_o2_", "142-143", 2, True, False),
]


def _utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _phase_sigma(e_ref: float, e_y: float, shots: int) -> float:
    """位相 atan2(y, x) の標準誤差（x, y の二項分布のばらつきを伝える）。"""
    var_x, var_y = (1 - e_ref**2) / shots, (1 - e_y**2) / shots
    r2 = e_ref**2 + e_y**2
    return float(np.sqrt((e_ref**2 * var_y + e_y**2 * var_x) / r2**2))


def load_trotter() -> list[dict]:
    jobs = []
    for prefix, pair, order, twirled, dd in TROTTER_JOBS:
        path = sorted(RES.glob(prefix + "2*.csv"))[-1]
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        rows = [r for r in csv.DictReader(path.open(encoding="utf-8")) if int(float(r["n_steps"])) <= NMAX]
        jobs.append({"pair": pair, "job": meta["job_id"], "time": _utc(meta["submitted_utc"]), "order": order,
                     "twirled": twirled, "dd": dd, "source": path.name,
                     "n": np.array([int(float(r["n_steps"])) for r in rows]),
                     "z": np.array([float(r["z_readout_corrected"]) for r in rows]),
                     "sem": np.array([float(r["z_sem"]) for r in rows]),
                     "z_trot": np.array([float(r["z_trotter_noiseless"]) for r in rows]),
                     "z_exact": float(rows[0]["z_exact"])})
    # 監視用の回路のジョブに含まれるトロッター回路（n=14、1次と2次）
    mon = sorted(RES.glob("hardware_monitor_2*.csv"))[-1]
    meta = json.loads(mon.with_suffix(".json").read_text(encoding="utf-8"))
    runtimes = {r["job_id"]: datetime.fromisoformat(r["running_jst"])
                for r in csv.DictReader((RES / "hardware_monitor_runtimes.csv").open(encoding="utf-8"))}
    for r, j in zip(csv.DictReader(mon.open(encoding="utf-8")), meta["jobs"]):
        for o in (1, 2):
            z_trot = float(meta["z_trotter_noiseless"][str(o)])
            jobs.append({"pair": "22-23", "job": j["job_id"], "time": runtimes[j["job_id"]], "order": o, "twirled": False,
                         "dd": False, "source": mon.name, "n": np.array([meta["args"]["n"]]),
                         "z": np.array([float(r[f"noise_o{o}"]) + z_trot]), "sem": np.array([float(r[f"sem_o{o}"])]),
                         "z_trot": np.array([z_trot]), "z_exact": float(meta["z_exact"])})
    return jobs


def load_probes() -> list[dict]:
    obs = []
    # 10/4 の Z 回転だけの測定（量子ビット 22–23）
    path = RES / "hardware_zprobe_20261004T121216Z.csv"
    meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    shots = meta["args"]["shots"]
    for r in csv.DictReader(path.open(encoding="utf-8")):
        x, y = float(r["exp_X"]), float(r["exp_Y"])
        if int(r["k_pairs"]) == 0:
            continue
        obs.append({"pair": "22-23", "job": meta["job_id"], "time": _utc(meta["submitted_utc"]), "axis": "Z",
                    "target": int(r["target_logical"]), "k": int(r["k_pairs"]), "phase": float(np.arctan2(y, x)),
                    "sigma": _phase_sigma(x, y, shots)})
    # 10/5 の Z 回転と X 回転の測定（両方の組）
    for path, pair in ((RES / "hardware_zprobe_q22_20261005T095539Z.csv", "22-23"),
                       (RES / "hardware_zprobe_q142_20261005T095633Z.csv", "142-143")):
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        shots = meta["args"]["shots"]
        for r in csv.DictReader(path.open(encoding="utf-8")):
            if int(r["k_pairs"]) == 0:
                continue
            e_ref, e_y = float(r["exp_ref"]), float(r["exp_Y"])
            obs.append({"pair": pair, "job": meta["job_id"], "time": _utc(meta["submitted_utc"]), "axis": r["axis"],
                        "target": int(r["target_logical"]), "k": int(r["k_pairs"]), "phase": float(np.arctan2(e_y, e_ref)),
                        "sigma": _phase_sigma(e_ref, e_y, shots)})
    # 監視用の回路（k=12、位相だけを記録してあるので、コヒーレンスは同じ日の直接の測定の値で近似する）
    mon = sorted(RES.glob("hardware_monitor_2*.csv"))[-1]
    meta = json.loads(mon.with_suffix(".json").read_text(encoding="utf-8"))
    shots, k = meta["args"]["shots"], meta["args"]["k"]
    runtimes = {r["job_id"]: datetime.fromisoformat(r["running_jst"])
                for r in csv.DictReader((RES / "hardware_monitor_runtimes.csv").open(encoding="utf-8"))}
    for r, j in zip(csv.DictReader(mon.open(encoding="utf-8")), meta["jobs"]):
        for axis, target, col, coh in (("Z", 0, "phase_ctrl_Z", 0.92), ("X", 1, "phase_tgt_X", 0.95)):
            obs.append({"pair": "22-23", "job": j["job_id"], "time": runtimes[j["job_id"]], "axis": axis, "target": target,
                        "k": k, "phase": float(r[col]), "sigma": 1 / (np.sqrt(shots) * coh)})
    return obs


def load_all() -> tuple[list[dict], list[dict]]:
    return load_trotter(), load_probes()


def synthetic_like(trotter: list[dict], probes: list[dict], truths: dict, rng: np.random.Generator):
    """実データと同じ構造（同じジョブ・同じ n・同じショット数）の合成データを、正解のパラメータ truths から作る。
    truths：組 → noise_model_jax.PairTruth。ジョブごとの揺らぎは PairTruth.job_offsets（ジョブ ID → ずれ）で与える。"""
    import jax.numpy as jnp
    syn_t, syn_p = [], []
    for j in trotter:
        tr = truths[j["pair"]]
        th = tr.theta15.copy()
        th[nm.LABELS15.index(tr.drift_label)] += tr.job_offsets.get(j["job"], 0.0)
        z_true = np.asarray(nm.trotter_z0(j["order"], j["n"], nm.error_sup(jnp.array(th), tr.p, j["twirled"])))
        shots = np.round((1 - z_true**2) / np.maximum(j["sem"], 1e-6) ** 2).astype(int)     # 実データの統計誤差に合うショット数
        z = 2 * rng.binomial(np.maximum(shots, 100), np.clip((1 + z_true) / 2, 0, 1)) / np.maximum(shots, 100) - 1
        syn_t.append({**j, "z": z, "z_true": z_true})
    for o in probes:
        tr = truths[o["pair"]]
        th = tr.theta15.copy()
        th[nm.LABELS15.index(tr.drift_label)] += tr.job_offsets.get(o["job"], 0.0)
        e_ref, e_y = nm.probe_expectations(nm.error_sup(jnp.array(th), tr.p, False), o["axis"], o["target"], (o["k"],))
        ph_true = float(np.arctan2(float(e_y[0]), float(e_ref[0])))
        syn_p.append({**o, "phase": ph_true + rng.normal(0, o["sigma"]), "phase_true": ph_true})
    return syn_t, syn_p


if __name__ == "__main__":
    t, p = load_all()
    print(f"トロッター回路のジョブ {len(t)} 本、点の合計 {sum(len(j['n']) for j in t)}")
    for j in t:
        print(f"  {j['pair']:8s} {j['time'].astimezone(JST):%m/%d %H:%M} JST {j['order']}次 ツイリング{'あり' if j['twirled'] else 'なし'}"
              f"{' DD' if j['dd'] else ''}  n={j['n'].min()}〜{j['n'].max()}（{len(j['n'])}点）  {j['source']}")
    print(f"直接の測定・監視用の回路の位相 {len(p)} 点（ジョブ {len({o['job'] for o in p})} 本）")
