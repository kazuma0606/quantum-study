"""射影演算子による測定確率のノート（研究ノート/08_量子コンピュータ/measurement_projection_born_rule.md）の検算。

本編：テンソル積の作用 (A⊗B)(u⊗v)=Au⊗Bv、P(x*)=‖(P_x*⊗I)|Ψ⟩‖²=1/N、④のボルン則の式、⑧の4候補の数値例
付録A：テンソル積の性質（準備）、完全な射影測定、測定後の状態、POVM
付録B：係数行列の階数とエンタングルメント、結果レジスタを測ったときの入力の状態
付録C：Qiskit の並び順

使い方:
    uv run python experiments/measurement_projection/measurement_projection.py   # 値を表示する
    uv run pytest experiments/measurement_projection -q                          # 検算
"""

import numpy as np

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)


def ket(index, dim):
    v = np.zeros(dim, dtype=complex)
    v[index] = 1
    return v


def proj(index, dim):
    """|index⟩⟨index|"""
    k = ket(index, dim)
    return np.outer(k, k.conj())


# ---------------------------------------------------------------- 本編：状態 |Ψ⟩
def psi_state(f, n_in, n_out, alpha=None):
    """Σ_x α_x |x⟩|f(x)⟩（入力 n_in 量子ビット、結果 n_out 量子ビット）。alpha=None なら均等。"""
    N, M = 2**n_in, 2**n_out
    if alpha is None:
        alpha = np.ones(N, dtype=complex) / np.sqrt(N)
    psi = np.zeros(N * M, dtype=complex)
    for x in range(N):
        psi[x * M + f(x)] += alpha[x]
    return psi


def coefficient_matrix(psi, N, M):
    """c_{x,y}（入力 x が行、結果 y が列）"""
    return psi.reshape(N, M)


def M_op(x, N, M):
    """M_x = P_x ⊗ I_M"""
    return np.kron(proj(x, N), np.eye(M))


def prob_input(psi, x, N, M):
    """P(x) = ‖(P_x⊗I)|Ψ⟩‖²"""
    v = M_op(x, N, M) @ psi
    return float(np.vdot(v, v).real)


def prob_input_born(psi, x, N, M):
    """ボルン則 (IV-1)：P(x) = Σ_y |c_{x,y}|²"""
    return float(np.sum(np.abs(coefficient_matrix(psi, N, M)[x]) ** 2))


# ---------------------------------------------------------------- 付録A
def post_measurement_state(psi, x, N, M):
    """射影仮説：M_x|Ψ⟩ / √P(x)"""
    v = M_op(x, N, M) @ psi
    p = float(np.vdot(v, v).real)
    return v / np.sqrt(p), p


def unsharp_measurement_kraus(eps):
    """誤差 ε のある Z 測定：K_0, K_1（ΣK†K=I）"""
    K0 = np.diag([np.sqrt(1 - eps), np.sqrt(eps)]).astype(complex)
    K1 = np.diag([np.sqrt(eps), np.sqrt(1 - eps)]).astype(complex)
    return K0, K1


def bit_flip_kraus(p):
    return np.sqrt(1 - p) * np.eye(2, dtype=complex), np.sqrt(p) * X


def amplitude_damping_kraus(gamma):
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    return K0, K1


# ---------------------------------------------------------------- 付録B
def result_register_collapse(psi, y, N, M):
    """結果レジスタを測って y が出たとき、入力レジスタに残る状態（規格化済み）と確率 P(y)。"""
    My = np.kron(np.eye(N), proj(y, M))
    v = My @ psi
    p = float(np.vdot(v, v).real)
    return v / np.sqrt(p), p


def schmidt_probabilities(psi, N, M):
    """係数行列の特異値の2乗（シュミット係数の2乗）"""
    s = np.linalg.svd(coefficient_matrix(psi, N, M), compute_uv=False)
    return s**2


def entropy_bits(p):
    p = np.asarray([x for x in p if x > 1e-15])
    return float(-(p * np.log2(p)).sum())


def reduced_input_state(psi, N, M):
    """結果レジスタの部分トレース：ρ = C C†"""
    C = coefficient_matrix(psi, N, M)
    return C @ C.conj().T


# ---------------------------------------------------------------- 付録C
def qiskit_example():
    """⑧の回路を Qiskit で作る。教科書の「第1量子ビット」は番号の大きい方に対応させる（入力 q2, q1、結果 q0）。"""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    qc = QuantumCircuit(3)
    qc.h(2)
    qc.h(1)
    qc.ccx(2, 1, 0)  # f(x)=1 ⇔ x=11：両方の入力が 1 のとき結果レジスタを反転
    sv = Statevector(qc)
    return qc, sv


# ---------------------------------------------------------------- 部分トレース（partial_trace_reduced_density_matrix.md）
def density(psi):
    return np.outer(psi, psi.conj())


def partial_trace(rho, dim_a, dim_b, keep="A"):
    """ρ（dim_a*dim_b 次元）の部分トレース。keep="A" なら B をトレースアウト。"""
    r = rho.reshape(dim_a, dim_b, dim_a, dim_b)
    if keep == "A":
        return np.einsum("ijkj->ik", r)
    return np.einsum("ijil->jl", r)


def hadamard_all(n):
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    out = np.eye(1)
    for _ in range(n):
        out = np.kron(out, H)
    return out


def prob_all_zero_after_hadamard(rho_a, n):
    """入力レジスタ（n量子ビット）に H^{⊗n} をかけて全部測ったとき、00…0 が出る確率 = (1/N) Σ_{x,x'} ρ_{xx'}"""
    H = hadamard_all(n)
    return float((H @ rho_a @ H.conj().T)[0, 0].real)


def two_qubit_state(theta):
    """(|0⟩|0⟩ + |1⟩(cosθ|0⟩ + sinθ|1⟩))/√2：結果レジスタ（環境）の状態の重なりが cosθ"""
    e0 = np.array([1, 0], dtype=complex)
    e1 = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
    return (np.kron(ket(0, 2), e0) + np.kron(ket(1, 2), e1)) / np.sqrt(2)


def main():
    f = lambda x: 1 if x == 3 else 0
    psi = psi_state(f, 2, 1)
    print("⑧ の |Ψ⟩ =", np.round(psi.real, 3))
    print("P(11) =", prob_input(psi, 3, 4, 2), " ボルン則:", prob_input_born(psi, 3, 4, 2))
    print("M_11 の対角:", np.diag(M_op(3, 4, 2)).real)
    print("結果レジスタを測ったとき（y=0, y=1）:", [round(result_register_collapse(psi, y, 4, 2)[1], 4) for y in (0, 1)])
    print("シュミット係数の2乗:", np.round(schmidt_probabilities(psi, 4, 2), 4), " エントロピー(bit):", round(entropy_bits(schmidt_probabilities(psi, 4, 2)), 4))
    qc, sv = qiskit_example()
    print("Qiskit の状態ベクトル:", np.round(sv.data.real, 3))


if __name__ == "__main__":
    main()
