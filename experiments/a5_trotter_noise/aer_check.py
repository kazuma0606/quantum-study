"""Qiskit Aer の密度行列シミュレータで、実際の回路（雑音つき）から最適な分割数を求める（独立した検証）。

回路：ZZ の項は CNOT・RZ(2Jδ)・CNOT、横磁場は RX(2gδ)。1次は ZZ を先、2次は RX(gδ)・ZZ・RX(gδ)。
雑音：各 CNOT の後に2量子ビットの脱分極（強さ p）を NoiseModel で付ける。
  （trotter_noise.py はステップの最後にまとめて雑音を入れるので、雑音の位置が少し違う。）
量子ビットの番号：Qiskit の量子ビット k ＝ こちらの site k。Qiskit の状態ベクトルは量子ビット 0 が最下位ビット。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/aer_check.py --qubits 4 10 --ps 0.005 --nmax 14
出力: results/aer_check_<日時>.csv と .meta.json
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import qiskit
import qiskit_aer
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from scipy.sparse.linalg import expm_multiply

HERE = Path(__file__).resolve().parent


def hamiltonian(N: int, J: float = 1.0, g: float = 1.0) -> SparsePauliOp:
    terms = []
    for i in range(N - 1):
        lab = ["I"] * N
        lab[i] = lab[i + 1] = "Z"
        terms.append(("".join(lab)[::-1], J))                       # Qiskit のラベルは右端が量子ビット 0
    for i in range(N):
        lab = ["I"] * N
        lab[i] = "X"
        terms.append(("".join(lab)[::-1], g))
    return SparsePauliOp.from_list(terms)


def trotter_circuit(N: int, t: float, order: int, n: int, J: float = 1.0, g: float = 1.0) -> QuantumCircuit:
    d = t / n
    qc = QuantumCircuit(N)

    def zz_layer() -> None:
        for i in range(N - 1):
            qc.cx(i, i + 1)
            qc.rz(2 * J * d, i + 1)
            qc.cx(i, i + 1)

    def x_layer(angle: float) -> None:
        for k in range(N):
            qc.rx(angle, k)

    for _ in range(n):
        if order == 1:
            zz_layer()
            x_layer(2 * g * d)
        else:
            x_layer(g * d)
            zz_layer()
            x_layer(g * d)
    qc.save_density_matrix()
    return qc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qubits", type=int, nargs="+", default=[4])
    ap.add_argument("--ps", type=float, nargs="+", default=[0.005])
    ap.add_argument("--orders", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--nmin", type=int, default=2)
    ap.add_argument("--nmax", type=int, default=14)
    ap.add_argument("--t", type=float, default=2.0)
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = HERE / "results" / f"aer_check_{stamp}.csv"
    rows = []
    t0 = time.time()
    for N in args.qubits:
        H = hamiltonian(N)
        psi0 = np.zeros(2**N, dtype=complex)
        psi0[0] = 1
        exact = expm_multiply(-1j * args.t * H.to_matrix(sparse=True), psi0)
        z0 = SparsePauliOp.from_list([("I" * (N - 1) + "Z", 1.0)]).to_matrix(sparse=True)   # 量子ビット 0 の Z
        z_exact = float(np.real(np.vdot(exact, z0 @ exact)))
        for p in args.ps:
            noise = NoiseModel()
            noise.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
            sim = AerSimulator(method="density_matrix", noise_model=noise)
            for order in args.orders:
                for n in range(args.nmin, args.nmax + 1):
                    rho = np.asarray(sim.run(trotter_circuit(N, args.t, order, n), shots=1).result().data()["density_matrix"])
                    fid = float(np.real(np.vdot(exact, rho @ exact)))
                    z = float(np.real(np.trace(z0 @ rho)))
                    rows.append({"n_qubits": N, "order": order, "p": p, "n_steps": n,
                                 "infidelity": 1 - fid, "local_err": abs(z - z_exact)})
                best = min((r for r in rows if r["n_qubits"] == N and r["order"] == order and r["p"] == p),
                           key=lambda r: r["infidelity"])
                print(f"Aer：N={N} 次数{order} p={p}：不忠実度の最適 n* = {best['n_steps']}（{best['infidelity']:.4f}）"
                      f"  {time.time() - t0:.0f} 秒", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    out.with_suffix(".meta.json").write_text(json.dumps(
        {"args": vars(args), "utc": stamp, "elapsed_sec": round(time.time() - t0, 1),
         "qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__,
         "noise": "各 CNOT の後に2量子ビット脱分極（NoiseModel）", "method": "AerSimulator density_matrix"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
