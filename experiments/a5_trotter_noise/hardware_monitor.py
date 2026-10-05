"""監視用の回路（チェック標準）の試運転：同じ短いジョブを時間をおいて何本か投げ、ジョブごとの揺らぎを見る。

1本のジョブに、次の回路を混ぜて入れる（比べたいものを同じジョブに入れる＝ブロック化）：
  監視用    ：CNOT の組を k 回くり返す回路（hardware_zprobe.py と同じ）
              ・制御（量子ビット 0）の Z 回転：|+> にして X・Y で測る
              ・標的（量子ビット 1）の X 回転：|0> のまま Z・Y で測る
  トロッター：1次と2次の n 段の回路（hardware.py と同じ）
  読み出し  ：全 0・全 1 の較正の回路
ジョブごとに、監視用の位相（atan2）と、トロッター回路の雑音による変化を記録する。
利用時間の合計が --max-seconds を超えそうなら、次のジョブを投げずに止める。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_monitor.py --qubits 22 23 --repeats 5 --interval 120 --shots 1500 --dry-run
出力: results/hardware_monitor_<日時>.csv（ジョブごとの1行）と .json（実行の記録）
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import qiskit
import qiskit_ibm_runtime
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hardware as hw  # noqa: E402
import hardware_zprobe as hz  # noqa: E402
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
JST = timezone(timedelta(hours=9))
N, T = 2, 2.0
# 実績からの見積もり：利用時間 ≈ 1ジョブあたり 1.6 秒 ＋ 1ショットあたり 0.27 ミリ秒
SEC_PER_JOB, SEC_PER_SHOT = 1.6, 0.27e-3


def build(k: int, n: int):
    probes = [("Z", 0, "X"), ("Z", 0, "Y"), ("X", 1, "Z"), ("X", 1, "Y")]       # (回転の軸, 調べる量子ビット, 測る基底)
    circuits = [hz.probe_circuit(t, k, b, a) for a, t, b in probes]
    circuits += [hw.measured_trotter_circuit(N, T, 1, n), hw.measured_trotter_circuit(N, T, 2, n)]
    circuits += hw.calibration_circuits(N)
    return probes, circuits


def expectation(counts: dict[str, int]) -> float:
    """1ビットの測定（hardware_zprobe の回路）の <Z>。"""
    shots = sum(counts.values())
    return (counts.get("0", 0) - counts.get("1", 0)) / shots


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--qubits", type=int, nargs=2, default=[22, 23])
    ap.add_argument("--k", type=int, default=12, help="監視用の回路で CNOT の組をくり返す回数")
    ap.add_argument("--n", type=int, default=14, help="トロッター回路の分割数")
    ap.add_argument("--shots", type=int, default=1500)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--interval", type=float, default=120.0, help="ジョブを投げる間隔（秒、前のジョブの結果が返ってから数える）")
    ap.add_argument("--max-seconds", type=float, default=25.0, help="利用時間の上限（見積もりで超えそうなら止める）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    service = QiskitRuntimeService(instance="open-instance")
    backend = service.backend(args.backend)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=args.qubits)
    probes, logical = build(args.k, args.n)
    isa = pm.run(logical)
    expected_cz = [2 * args.k] * len(probes) + [2 * args.n, 2 * args.n, 0, 0]
    for qc, e in zip(isa, expected_cz):
        cz = qc.count_ops().get("cz", 0)
        assert cz == e, f"{qc.name}：CZ が {cz} 個（想定 {e}）"
    per_job = SEC_PER_JOB + SEC_PER_SHOT * args.shots * len(isa)
    print(f"1ジョブ：回路 {len(isa)} 本 × {args.shots} ショット、見積もり {per_job:.1f} 秒。"
          f"{args.repeats} 本で約 {per_job * args.repeats:.0f} 秒（上限 {args.max_seconds} 秒）。CZ の数はすべて想定どおり")
    if args.dry_run:
        print("--dry-run：実機には投げずに終了")
        return

    z_exact = tn.run_point(N, T, 1, args.n, 0.0).z_exact
    z_trot = {o: z_exact + tn.run_point(N, T, o, args.n, 0.0).z_trotter_part for o in (1, 2)}
    rows, jobs, used = [], [], 0.0
    for rep in range(args.repeats):
        if used + per_job > args.max_seconds:
            print(f"利用時間の合計 {used:.0f} 秒＋見積もり {per_job:.1f} 秒が上限を超えるので、ここで止めます")
            break
        if rep > 0:
            time.sleep(args.interval)
        submitted = datetime.now(timezone.utc)
        job = SamplerV2(mode=backend).run(isa, shots=args.shots)
        res = job.result()
        usage = job.usage()
        used += usage
        jobs.append({"job_id": job.job_id(), "submitted_utc": submitted.isoformat(), "usage_quantum_seconds": usage})
        ev = {}
        for (a, t, b), r in zip(probes, res[:4]):
            ev[(a, b)] = expectation(r.data.c.get_counts())
        trot_counts = [r.data.meas.get_counts() for r in res[4:]]
        cal0, cal1 = trot_counts[2], trot_counts[3]
        e0 = 1 - (hw.z0_from_counts(cal0) + 1) / 2
        e1 = (hw.z0_from_counts(cal1) + 1) / 2
        row = {"rep": rep, "submitted_jst": submitted.astimezone(JST).strftime("%H:%M:%S"), "usage_s": usage,
               "phase_ctrl_Z": float(np.arctan2(ev[("Z", "Y")], ev[("Z", "X")])),
               "phase_tgt_X": float(np.arctan2(ev[("X", "Y")], ev[("X", "Z")])),
               "readout_e0": e0, "readout_e1": e1}
        for o, c in zip((1, 2), trot_counts[:2]):
            zm = hw.z0_from_counts(c)
            zc = (zm - (e1 - e0)) / (1 - e0 - e1)
            row[f"noise_o{o}"] = zc - z_trot[o]
            row[f"sem_o{o}"] = float(np.sqrt(max(1 - zm**2, 0)) / np.sqrt(args.shots) / (1 - e0 - e1))
        rows.append(row)
        print(f"#{rep} {row['submitted_jst']} JST 利用 {usage} 秒（合計 {used:.0f}）：監視 制御Z {row['phase_ctrl_Z']:+.3f}、"
              f"標的X {row['phase_tgt_X']:+.3f} rad ／ 雑音による変化 1次 {row['noise_o1']:+.3f}、2次 {row['noise_o2']:+.3f}"
              f"（±{row['sem_o1']:.3f}）", flush=True)
    if not rows:
        return
    stamp = datetime.fromisoformat(jobs[0]["submitted_utc"]).strftime("%Y%m%dT%H%M%SZ")
    out = HERE / "results" / f"hardware_monitor_{stamp}.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    out.with_suffix(".json").write_text(json.dumps(
        {"args": vars(args), "backend": backend.name, "jobs": jobs, "usage_total": used,
         "z_exact": z_exact, "z_trotter_noiseless": z_trot,
         "qiskit": qiskit.__version__, "qiskit_ibm_runtime": qiskit_ibm_runtime.__version__},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"利用時間の合計：{used} 秒")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
