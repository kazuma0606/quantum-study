"""実機で、CNOT の組（理想では何もしない操作）のくり返しによって、各量子ビットに余分な Z 回転がたまるかを直接測る。

回路：調べる量子ビット（target）を H で |+> にし、もう一方は |0> のまま、
  CX(22→23)・バリア・CX(22→23)・バリア を k 回くり返す（バリアは、変換で CX の組が打ち消されて消えないようにするため）。
  最後に target を X 基底（H のあと測定）と Y 基底（S†・H のあと測定）で測る。
  位相 φ(k) = atan2(<Y>, <X>) の k に対する傾きが、CX の組1回あたりの余分な Z 回転（rad）。
  トロッター分解の1ステップ（N=2）は CX の組1回なので、noise_model_fits.py の ζ（rad/ステップ）と直接比べられる。
  （ZZ の回転 RZ は仮想ゲートで時間がかからないので、ここでは省いている。）

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_zprobe.py --ks 0 2 4 8 12 --shots 4000 --dry-run
出力: results/hardware_zprobe_<日時>.csv と .json
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import qiskit
import qiskit_ibm_runtime
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

HERE = Path(__file__).resolve().parent
JST = timezone(timedelta(hours=9))


def probe_circuit(target: int, k: int, basis: str) -> QuantumCircuit:
    qc = QuantumCircuit(2, 1, name=f"zprobe_t{target}_k{k}_{basis}")
    qc.h(target)
    for _ in range(k):
        qc.cx(0, 1)
        qc.barrier()
        qc.cx(0, 1)
        qc.barrier()
    if basis == "Y":
        qc.sdg(target)
    qc.h(target)
    qc.measure(target, 0)
    return qc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ks", type=int, nargs="+", default=[0, 2, 4, 8, 12])
    ap.add_argument("--shots", type=int, default=4000)
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--qubits", type=int, nargs=2, default=[22, 23])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    service = QiskitRuntimeService(instance="open-instance")
    backend = service.backend(args.backend)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=args.qubits)
    specs = [(t, k, b) for t in (0, 1) for k in args.ks for b in ("X", "Y")]
    isa = pm.run([probe_circuit(t, k, b) for t, k, b in specs])
    for (t, k, b), qc in zip(specs, isa):
        cz = qc.count_ops().get("cz", 0)
        assert cz == 2 * k, f"{qc.name}：CZ が {cz} 個（想定 {2 * k}）"
    print(f"回路 {len(isa)} 本、各 {args.shots} ショット、合計 {len(isa) * args.shots} ショット。CZ の数はすべて想定どおり")
    if args.dry_run:
        print("--dry-run：実機には投げずに終了")
        return

    submitted = datetime.now(timezone.utc)
    job = SamplerV2(mode=backend).run(isa, shots=args.shots)
    print(f"投入：ジョブ {job.job_id()}（{submitted.astimezone(JST):%Y-%m-%d %H:%M:%S} JST）", flush=True)
    res = job.result()
    usage = job.usage()
    expv = {}
    for (t, k, b), r in zip(specs, res):
        c = r.data.c.get_counts()
        expv[(t, k, b)] = (c.get("0", 0) - c.get("1", 0)) / args.shots
    rows = []
    for t in (0, 1):
        for k in args.ks:
            x, y = expv[(t, k, "X")], expv[(t, k, "Y")]
            rows.append({"target_logical": t, "target_physical": args.qubits[t], "k_pairs": k,
                         "exp_X": x, "exp_Y": y, "phase_rad": float(np.arctan2(y, x)), "coherence": float(np.hypot(x, y))})
    slopes = {}
    for t in (0, 1):
        ks = np.array([r["k_pairs"] for r in rows if r["target_logical"] == t])
        ph = np.unwrap([r["phase_rad"] for r in rows if r["target_logical"] == t])
        slopes[args.qubits[t]] = float(np.polyfit(ks, ph, 1)[0])
    stamp = submitted.strftime("%Y%m%dT%H%M%SZ")
    out = HERE / "results" / f"hardware_zprobe_{stamp}.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    out.with_suffix(".json").write_text(json.dumps(
        {"args": vars(args), "backend": backend.name, "job_id": job.job_id(), "submitted_utc": submitted.isoformat(),
         "usage_quantum_seconds": usage, "phase_slope_rad_per_pair": slopes,
         "qiskit": qiskit.__version__, "qiskit_ibm_runtime": qiskit_ibm_runtime.__version__},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"利用時間：{usage} 秒")
    for r in rows:
        print(f"量子ビット {r['target_physical']}、k={r['k_pairs']:2d}：<X>={r['exp_X']:+.3f}、<Y>={r['exp_Y']:+.3f}、"
              f"位相 {r['phase_rad']:+.3f} rad、コヒーレンス {r['coherence']:.3f}")
    print(f"位相の傾き（rad / CX の組1回）：{slopes}")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
