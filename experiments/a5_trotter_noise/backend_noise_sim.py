"""実機の較正データから作った雑音モデル（Qiskit Aer の AerSimulator.from_backend）で、実機に送ったのと同じ
変換済みの回路を計算し、実機の結果と比べる（実機の利用時間は使わない）。

雑音モデルに入るもの：ゲートごとの脱分極（較正の誤差から）、ゲートの時間中の T1・T2 の緩和、読み出しの誤差。
入らないもの：コヒーレントな誤差（回転角のずれ、クロストーク）、待ち時間中の緩和（回路をスケジュールしないため）。
<Z_0> は、測定を外して save_expectation_value で密度行列から正確に求める（読み出しの誤差は含まない＝補正後の実機と比べる）。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/backend_noise_sim.py results/hardware_main_o1_….json results/hardware_main_o2_….json
出力: results/backend_noise_sim_N2.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aer_check  # noqa: E402
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    metas = [json.loads(Path(a).read_text(encoding="utf-8")) for a in sys.argv[1:]]
    service = QiskitRuntimeService(instance="open-instance")
    rows = []
    for meta in metas:
        backend = service.backend(meta["backend"])
        sim = AerSimulator.from_backend(backend, method="density_matrix")
        N, order, t, qubits = meta["args"]["N"], meta["args"]["order"], meta["args"]["t"], meta["qubits"]
        pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=qubits)
        hw = {int(float(r["n_steps"])): r for r in csv.DictReader(
            (HERE / "results" / (Path(sys.argv[1 + metas.index(meta)]).stem + ".csv")).open(encoding="utf-8"))}
        for n in meta["args"]["ns"]:
            qc = aer_check.trotter_circuit(N, t, order, n)
            qc.data = [ins for ins in qc.data if ins.operation.name != "save_density_matrix"]
            isa = pm.run(qc)
            phys0 = isa.layout.final_index_layout()[0]                     # 論理量子ビット 0 の物理番号
            obs = SparsePauliOp.from_sparse_list([("Z", [phys0], 1.0)], num_qubits=isa.num_qubits)
            isa.save_expectation_value(obs, list(range(isa.num_qubits)), label="z0")
            z_sim = float(np.real(sim.run(isa).result().data()["z0"]))
            ref = tn.run_point(N, t, order, n, 0.0)
            z_clean = ref.z_exact + ref.z_trotter_part
            rows.append({"order": order, "n_steps": n, "z_backend_model": z_sim,
                         "z_hardware_corrected": float(hw[n]["z_readout_corrected"]), "z_sem": float(hw[n]["z_sem"]),
                         "z_trotter_noiseless": z_clean, "z_exact": ref.z_exact,
                         "noise_part_model": z_sim - z_clean, "noise_part_hw": float(hw[n]["noise_part_hw"])})
            print(f"次数{order} n={n:2d}：雑音モデル {z_sim:+.4f}（変化 {z_sim - z_clean:+.4f}）"
                  f"  実機 {float(hw[n]['z_readout_corrected']):+.4f}（変化 {float(hw[n]['noise_part_hw']):+.4f}）", flush=True)
    out = HERE / "results" / "backend_noise_sim_N2.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
