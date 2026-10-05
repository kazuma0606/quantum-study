"""監視用の回路の試運転（hardware_monitor.py）の結果を、実際の実行時刻に沿って描く。
同じ日（10/5）の、それより前の測定（18:31・18:32 のトロッター回路、18:55 の直接測定）も基準として描き込む。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_monitor_plot.py
出力: figures/hardware_monitor_N2.png と results/hardware_monitor_runtimes.csv（各ジョブの実際の実行時刻）
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
JST = timezone(timedelta(hours=9))
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"


def runtimes(meta: dict) -> list[datetime]:
    """各ジョブの実際の実行時刻。保存済みなら CSV から読み、なければ IBM の記録から取り出して保存する。"""
    path = RES / "hardware_monitor_runtimes.csv"
    if path.exists():
        return [datetime.fromisoformat(r["running_jst"]) for r in csv.DictReader(path.open(encoding="utf-8"))]
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(instance="open-instance")
    out = []
    for j in meta["jobs"]:
        t = service.job(j["job_id"]).metrics()["timestamps"]["running"]
        out.append(datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(JST))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["job_id", "running_jst"])
        for j, t in zip(meta["jobs"], out):
            w.writerow([j["job_id"], t.isoformat()])
    return out


def minutes(t: datetime) -> float:
    """10/5 18:00 JST からの経過分。"""
    return (t - datetime(2026, 10, 5, 18, 0, tzinfo=JST)).total_seconds() / 60


def main() -> None:
    mon_csv = sorted(RES.glob("hardware_monitor_2*.csv"))[-1]
    meta = json.loads(mon_csv.with_suffix(".json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(mon_csv.open(encoding="utf-8")))
    ts = np.array([minutes(t) for t in runtimes(meta)])
    shots = meta["args"]["shots"]
    sp = 1 / np.sqrt(shots) / 0.93          # 位相の統計誤差（コヒーレンス約 0.93）

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    ax.errorbar(ts, [float(r["phase_ctrl_Z"]) for r in rows], yerr=sp, fmt="o-", color="#1f77b4", capsize=2,
                label="量子ビット 22 の Z 回転（監視）")
    ax.errorbar(ts, [float(r["phase_tgt_X"]) for r in rows], yerr=sp, fmt="s-", color="#2ca02c", capsize=2,
                label="量子ビット 23 の X 回転（監視）")
    probe = list(csv.DictReader((RES / "hardware_zprobe_q22_20261005T095539Z.csv").open(encoding="utf-8")))
    t_probe = minutes(datetime(2026, 10, 5, 18, 55, 44, tzinfo=JST))
    for r in probe:
        if r["k_pairs"] == "12" and (r["axis"], r["target_physical"]) in (("Z", "22"), ("X", "23")):
            c = "#1f77b4" if r["axis"] == "Z" else "#2ca02c"
            ax.errorbar([t_probe], [float(r["phase_rad"])], yerr=1 / np.sqrt(3000) / 0.93, fmt="*", ms=11, color=c, capsize=2,
                        label="★ 18:55 の直接測定" if r["axis"] == "Z" else None)
    ax.set_xlabel("10/5 18:00 からの経過時間（分）")
    ax.set_ylabel("CNOT の組 12 回での位相（rad）")
    ax.set_title("(a) 監視用の回路：19:49 の1本だけ、量子ビット 22 の Z 回転が跳んだ", fontsize=11)
    ax.legend(fontsize=8.5, loc="center left")

    ax = axes[1]
    for o, c, m in ((1, "#1f77b4", "o"), (2, "#e67e00", "D")):
        ax.errorbar(ts, [float(r[f"noise_o{o}"]) for r in rows], yerr=[float(r[f"sem_o{o}"]) for r in rows],
                    fmt=m + "-", color=c, capsize=2, label=f"{o}次・n={meta['args']['n']}（監視つきのジョブ）")
        ref = list(csv.DictReader(sorted(RES.glob(f"hardware_day2_o{o}_2*.csv"))[-1].open(encoding="utf-8")))
        r14 = [r for r in ref if int(float(r["n_steps"])) == meta["args"]["n"]][0]
        t_ref = minutes(datetime(2026, 10, 5, 18, 31 + o, tzinfo=JST))
        ax.errorbar([t_ref], [float(r14["noise_part_hw"])], yerr=float(r14["z_sem"]), fmt="*", ms=11, color=c, capsize=2,
                    label="★ 18:31・18:32 の測定（8000 ショット）" if o == 1 else None)
    ax.set_xlabel("10/5 18:00 からの経過時間（分）")
    ax.set_ylabel("雑音による変化（実機 − 雑音なしのトロッター積）")
    ax.set_title("(b) トロッター回路（n=14）：同じジョブで、わずかに小さい（約 2σ）", fontsize=11)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "hardware_monitor_N2.png", dpi=150)
    print("書き出し: figures/hardware_monitor_N2.png")


if __name__ == "__main__":
    main()
