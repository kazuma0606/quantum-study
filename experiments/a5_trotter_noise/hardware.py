"""IBM Quantum の実機で、トロッター分解の <Z_0> を測る（テーマ A-5）。

回路：aer_check.trotter_circuit と同じ（ZZ は CNOT・RZ・CNOT、横磁場は RX）。最後に全量子ビットを測る。
読み出しの補正：同じ量子ビットで「全 0」「全 1」を準備して測る較正の回路を2本加え、量子ビット 0 の
  P(1|0) = e0、P(0|1) = e1 から  <Z>_補正 = (<Z>_測定 - (e1 - e0)) / (1 - e0 - e1)  とする
  （測定の P(1) = e0 (1 - P1) + (1 - e1) P1 を P1 について解いたもの）。
回路の変換：最適化はレベル1まで（レベル2以上は2量子ビットの回路全体を CZ 3個にまとめてしまう）。
  変換後の CZ の数が 2 (N-1) n に一致することを、投げる前に確かめる（一致しなければ投げない）。
実機の利用時間を消費するので、quantum-experiment Skill の手順（事前の見積もりと承認）に従って使う。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware.py --N 2 --order 1 --ns 2 8 16 --shots 4000 --tag pilot
    （--dry-run で、実機に投げずに回路の確認だけを行う）
出力: results/hardware_<tag>_<日時>.csv（n ごとの結果）と .json（実行の記録：実機、量子ビット、較正、ジョブ ID、利用時間）
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
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aer_check  # noqa: E402
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
JST = timezone(timedelta(hours=9))


def measured_trotter_circuit(N: int, t: float, order: int, n: int) -> QuantumCircuit:
    qc = aer_check.trotter_circuit(N, t, order, n)
    qc.data = [ins for ins in qc.data if ins.operation.name != "save_density_matrix"]
    qc.measure_all()
    qc.name = f"trotter_N{N}_o{order}_n{n}"
    return qc


def calibration_circuits(N: int) -> list[QuantumCircuit]:
    zero = QuantumCircuit(N, name="cal_0")
    zero.measure_all()
    one = QuantumCircuit(N, name="cal_1")
    one.x(range(N))
    one.measure_all()
    return [zero, one]


def best_chain(backend, N: int) -> list[int]:
    """CZ の誤差の和が最小になる、つながった N 個の量子ビットの鎖（N ≤ 4 を想定した素朴な探索）。"""
    t = backend.target
    gate = "cz" if "cz" in t.operation_names else "ecr"
    err = {}
    for q, props in t[gate].items():
        if props is not None and props.error is not None:
            err[tuple(q)] = props.error
    nbrs: dict[int, set[int]] = {}
    for a, b in err:
        nbrs.setdefault(a, set()).add(b)
    best, best_cost = None, np.inf
    def extend(path: list[int], cost: float) -> None:
        nonlocal best, best_cost
        if len(path) == N:
            if cost < best_cost:
                best, best_cost = list(path), cost
            return
        for nb in nbrs.get(path[-1], ()):
            if nb not in path:
                e = err.get((path[-1], nb), err.get((nb, path[-1]), np.inf))
                extend(path + [nb], cost + e)
    for q in nbrs:
        extend([q], 0.0)
    return best


def z0_from_counts(counts: dict[str, int]) -> float:
    """量子ビット 0（ビット列の右端）の <Z>。"""
    shots = sum(counts.values())
    ones = sum(c for b, c in counts.items() if b[-1] == "1")
    return 1 - 2 * ones / shots


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2)
    ap.add_argument("--order", type=int, default=1)
    ap.add_argument("--ns", type=int, nargs="+", default=[2, 8, 16])
    ap.add_argument("--t", type=float, default=2.0)
    ap.add_argument("--shots", type=int, default=4000)
    ap.add_argument("--backend", default=None, help="省略すると、待ちの少ない実機を選ぶ")
    ap.add_argument("--tag", default="pilot")
    ap.add_argument("--dd", default=None, help="動的デカップリングの系列（XY4、XpXm など）。省略で使わない")
    ap.add_argument("--twirl", action="store_true", help="2量子ビットゲートのパウリ・ツイリングを使う")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    service = QiskitRuntimeService(instance="open-instance")
    backend = service.backend(args.backend) if args.backend else service.least_busy(operational=True, simulator=False)
    chain = best_chain(backend, args.N)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=chain)

    logical = [measured_trotter_circuit(args.N, args.t, args.order, n) for n in args.ns] + calibration_circuits(args.N)
    isa = pm.run(logical)
    for qc, n in zip(isa, args.ns):
        cz = qc.count_ops().get("cz", 0) + qc.count_ops().get("ecr", 0)
        expected = 2 * (args.N - 1) * n
        assert cz == expected, f"{qc.name}：変換後の2量子ビットゲートが {cz} 個（想定 {expected} 個）。回路がまとめられた可能性"
        print(f"{qc.name}: 2量子ビットゲート {cz} 個、深さ {qc.depth()}")

    t = backend.target
    gate = "cz" if "cz" in t.operation_names else "ecr"
    calib = {
        "pair_errors": {f"{a}-{b}": (t[gate].get((a, b)) or t[gate].get((b, a))).error for a, b in zip(chain, chain[1:])},
        "readout_errors": {q: t["measure"][(q,)].error for q in chain},
        "t1_us": {q: backend.qubit_properties(q).t1 * 1e6 for q in chain},
        "t2_us": {q: backend.qubit_properties(q).t2 * 1e6 for q in chain},
    }
    print(f"実機 {backend.name}、量子ビット {chain}、較正 {json.dumps(calib, ensure_ascii=False)}")
    if args.dry_run:
        print("--dry-run：実機には投げずに終了")
        return

    sampler = SamplerV2(mode=backend)
    if args.dd:
        sampler.options.dynamical_decoupling.enable = True
        sampler.options.dynamical_decoupling.sequence_type = args.dd
    if args.twirl:
        sampler.options.twirling.enable_gates = True
        sampler.options.twirling.num_randomizations = 32
        sampler.options.twirling.shots_per_randomization = -(-args.shots // 32)   # 切り上げ（32 × これ ≥ shots が必要）
    submitted = datetime.now(timezone.utc)
    job = sampler.run(isa, shots=args.shots)
    print(f"投入：ジョブ {job.job_id()}（{submitted.astimezone(JST):%Y-%m-%d %H:%M:%S} JST）", flush=True)
    result = job.result()
    usage = job.usage()
    counts = [r.data.meas.get_counts() for r in result]

    cal0, cal1 = counts[-2], counts[-1]
    e0 = 1 - (z0_from_counts(cal0) + 1) / 2          # 全 0 を準備して 1 と読んだ割合
    e1 = (z0_from_counts(cal1) + 1) / 2              # 全 1 を準備して 0 と読んだ割合
    A, B = tn.tfim_parts(args.N)
    rows = []
    for n, c in zip(args.ns, counts[:-2]):
        z_meas = z0_from_counts(c)
        z_corr = (z_meas - (e1 - e0)) / (1 - e0 - e1)
        sim = tn.run_point(args.N, args.t, args.order, n, 0.0)
        rows.append({"n_steps": n, "shots": args.shots, "z_measured": z_meas, "z_readout_corrected": z_corr,
                     "z_sem": float(np.sqrt(max(1 - z_meas**2, 0)) / np.sqrt(args.shots) / (1 - e0 - e1)),
                     "z_exact": sim.z_exact, "z_trotter_noiseless": sim.z_exact + sim.z_trotter_part,
                     "local_err_hw": abs(z_corr - sim.z_exact),
                     "noise_part_hw": z_corr - (sim.z_exact + sim.z_trotter_part)})
    stamp = submitted.strftime("%Y%m%dT%H%M%SZ")
    out = HERE / "results" / f"hardware_{args.tag}_{stamp}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    record = {
        "args": vars(args), "backend": backend.name, "qubits": chain, "job_id": job.job_id(),
        "submitted_utc": submitted.isoformat(), "finished_utc": datetime.now(timezone.utc).isoformat(),
        "usage_quantum_seconds": usage, "readout_e0": e0, "readout_e1": e1, "calibration": calib,
        "sampler_options": {"dynamical_decoupling": args.dd, "twirling_gates": args.twirl},
        "two_qubit_gates": {qc.name: qc.count_ops().get(gate, 0) for qc in isa},
        "depths": {qc.name: qc.depth() for qc in isa},
        "qiskit": qiskit.__version__, "qiskit_ibm_runtime": qiskit_ibm_runtime.__version__,
    }
    out.with_suffix(".json").write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"利用時間（quantum seconds）：{usage}")
    print(f"読み出しの誤差：e0 = {e0:.4f}、e1 = {e1:.4f}")
    for r in rows:
        print(f"n={r['n_steps']:2d}：<Z0> 測定 {r['z_measured']:+.4f} → 補正 {r['z_readout_corrected']:+.4f} ± {r['z_sem']:.4f}"
              f"  ／ 雑音なしのトロッター {r['z_trotter_noiseless']:+.4f}、正確な値 {r['z_exact']:+.4f}")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
