"""実機の T1 専用の回路（制御を |0>・|1> に準備し、CX の組を k 回くり返して、2つの量子ビットの <Z> を同時に測る）。

S6 で選んだ設計（k = 4, 8, 16, 32, 48、3000 ショット、両方の組）を、実機の回路に変換して、深さと QPU の時間を見積もる。
noise_model_jax.t1_probe_probs と同じ回路：
  制御（論理 0）：|0> のまま、または X で |1>。標的（論理 1）：|0>
  CX(0→1)・バリア・CX(0→1)・バリア を k 回（バリアは、変換で CX の組が打ち消されて消えないようにするため）
  最後に両方を Z 基底で測る（4通りの同時の結果を記録する）
QPU の時間の見積もり（2通り）：
  (a) これまでのジョブから：2 秒 ＋ 0.3 ms × 回路 × ショット（回路の長さを考えない）
  (b) 回路の長さを足す：2 秒 ＋ Σ ショット × (0.3 ms ＋ その回路の実行時間)。実行時間は qiskit の estimate_duration で見積もる
このスクリプトは、--submit をつけない限り実機にジョブを出さない（既定はドライラン）。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_t1probe.py --ks 4 8 16 32 48 --shots 3000 --qubits 22 23
"""

from __future__ import annotations

import argparse

from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService

SEC_PER_JOB, SEC_PER_SHOT = 2.0, 3e-4


def t1probe_circuit(k: int, control_one: bool) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2, name=f"t1probe_c{int(control_one)}_k{k}")
    if control_one:
        qc.x(0)
    for _ in range(k):
        qc.cx(0, 1)
        qc.barrier()
        qc.cx(0, 1)
        qc.barrier()
    qc.measure([0, 1], [0, 1])
    return qc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ks", type=int, nargs="+", default=[4, 8, 16, 32, 48])
    ap.add_argument("--shots", type=int, default=3000)
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--qubits", type=int, nargs=2, default=[22, 23])
    ap.add_argument("--submit", action="store_true", help="実機にジョブを出す（出す前に、時間の見積もりと承認が要る）")
    args = ap.parse_args()
    if args.submit:
        raise SystemExit("--submit はまだ用意していない（見積もりと承認のあとで足す）")

    service = QiskitRuntimeService(instance="open-instance")
    backend = service.backend(args.backend)
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=args.qubits)
    specs = [(k, c1) for c1 in (False, True) for k in args.ks]
    isa = pm.run([t1probe_circuit(k, c1) for k, c1 in specs])
    total_b = SEC_PER_JOB
    print(f"量子ビット {args.qubits}、{args.backend}、各 {args.shots} ショット")
    print("| 準備 | k | CZ の数 | 深さ | 1回の実行時間（μs） |")
    print("|---|---|---|---|---|")
    for (k, c1), qc in zip(specs, isa):
        cz = qc.count_ops().get("cz", 0)
        assert cz == 2 * k, f"{qc.name}：CZ が {cz} 個（想定 {2 * k}）"
        dur = qc.estimate_duration(backend.target, unit="s")
        total_b += args.shots * (SEC_PER_SHOT + dur)
        print(f"| {'|1>' if c1 else '|0>'} | {k} | {cz} | {qc.depth()} | {dur * 1e6:.1f} |")
    total_a = SEC_PER_JOB + SEC_PER_SHOT * len(isa) * args.shots
    print(f"回路 {len(isa)} 本。QPU の時間の見積もり：(a) 回路の長さを考えない {total_a:.1f} 秒、(b) 回路の長さを足す {total_b:.1f} 秒")
    print("ドライラン：実機にはジョブを出していない")


if __name__ == "__main__":
    main()
