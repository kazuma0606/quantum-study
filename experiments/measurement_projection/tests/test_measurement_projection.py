"""射影演算子による測定確率のノートの検算（本編、付録A〜C）。"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import measurement_projection as mp  # noqa: E402

rng = np.random.default_rng(0)


def rand_c(*shape):
    return rng.normal(size=shape) + 1j * rng.normal(size=shape)


def rand_state(d):
    v = rand_c(d)
    return v / np.linalg.norm(v)


F_EXAMPLE = lambda x: 1 if x == 3 else 0  # ⑧：f(x)=1 ⇔ x=11


# ------------------------------------------------------------- 本編
def test_mixed_product_rule_3_1():
    """(III-1) (A⊗B)(u⊗v) = Au⊗Bv"""
    for m, n in [(2, 2), (2, 4), (4, 2), (3, 5)]:
        A, B = rand_c(m, m), rand_c(n, n)
        u, v = rand_c(m), rand_c(n)
        assert np.allclose(np.kron(A, B) @ np.kron(u, v), np.kron(A @ u, B @ v))


def test_kron_components_and_labels():
    k0, k1 = mp.ket(0, 2), mp.ket(1, 2)
    assert np.allclose(np.kron(k0, k0), [1, 0, 0, 0]) and np.allclose(np.kron(k1, k0), [0, 0, 1, 0])
    a, b, c, d = 0.3, 0.4j, 0.5, 0.6
    assert np.allclose(np.kron([a, b], [c, d]), [a * c, a * d, b * c, b * d])


def test_projector_properties():
    P = mp.proj(3, 4)
    assert np.allclose(P @ P, P) and np.allclose(P.conj().T, P)
    for i in range(4):
        assert np.allclose(P @ mp.ket(i, 4), (1 if i == 3 else 0) * mp.ket(3, 4))


def test_identity_commutes_with_other_register_operator():
    """③-2-6-7：(A⊗I_n)(I_m⊗B) = A⊗B = (I_m⊗B)(A⊗I_n)、一方 X⊗I ≠ I⊗X"""
    for m, n in [(2, 2), (2, 4), (4, 2), (3, 5)]:
        A, B = rand_c(m, m), rand_c(n, n)
        L = np.kron(A, np.eye(n)) @ np.kron(np.eye(m), B)
        R = np.kron(np.eye(m), B) @ np.kron(A, np.eye(n))
        assert np.allclose(L, np.kron(A, B)) and np.allclose(R, np.kron(A, B))
    assert not np.allclose(np.kron(mp.X, mp.I2), np.kron(mp.I2, mp.X))
    assert np.allclose(np.kron(mp.X, mp.I2) @ mp.ket(0, 4), mp.ket(2, 4))  # |00⟩ → |10⟩
    assert np.allclose(np.kron(mp.I2, mp.X) @ mp.ket(0, 4), mp.ket(1, 4))  # |00⟩ → |01⟩
    # A⊗I_m は m² 次元（ここで考える複合系 mn 次元と合わない）
    A = rand_c(2, 2)
    assert np.kron(A, np.eye(2)).shape == (4, 4) and np.kron(A, np.eye(4)).shape == (8, 8)


def test_entangled_state_is_not_product():
    """③-2-6-5：|Φ+⟩ は積状態でない。積状態の判定 w00 w11 = w01 w10"""
    bell = np.array([1, 0, 0, 1]) / np.sqrt(2)
    assert not np.isclose(bell[0] * bell[3], bell[1] * bell[2])
    for _ in range(20):
        w = np.kron(rand_c(2), rand_c(2))
        assert np.isclose(w[0] * w[3], w[1] * w[2])


def test_cnot_is_not_a_tensor_product():
    """③-2-7-2：CNOT = B1⊗B2 と書けない（階数1の分解がない）"""
    # 再配置（Van Loan）：B1⊗B2 の再配置行列は階数 1。CNOT のそれは階数 2。
    def rearranged_rank(B):
        R = B.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3).reshape(4, 4)
        return np.linalg.matrix_rank(R)

    assert rearranged_rank(np.kron(rand_c(2, 2), rand_c(2, 2))) == 1
    assert rearranged_rank(mp.CNOT) == 2
    # 判定の議論そのもの：左上ブロックから B2 ∝ I、右下ブロックから X ∝ I となって矛盾
    assert not np.allclose(mp.X, mp.X[0, 0] * np.eye(2))


def test_mixed_product_of_tensor_products_and_cnot_squared():
    U1, U2, V1, V2 = (rand_c(2, 2) for _ in range(4))
    assert np.allclose(np.kron(U1, U2) @ np.kron(V1, V2), np.kron(U1 @ V1, U2 @ V2))
    assert np.allclose(mp.CNOT @ mp.CNOT, np.eye(4)) and np.allclose(np.kron(mp.I2, mp.I2), np.eye(4))
    assert np.allclose(np.kron(mp.X, mp.I2) @ np.kron(mp.I2, mp.Z), np.kron(mp.X, mp.Z))  # (X⊗I)(I⊗Z)=X⊗Z


def test_born_rule_and_projector_agree_for_random_states():
    """④-7：P(x) = Σ_y |c_xy|² = ‖(P_x⊗I)Φ‖² = ⟨Φ|P_x⊗I|Φ⟩"""
    for N, M in [(4, 2), (2, 4), (4, 4), (3, 5)]:
        phi = rand_state(N * M)
        for x in range(N):
            p1 = mp.prob_input(phi, x, N, M)
            assert np.isclose(p1, mp.prob_input_born(phi, x, N, M))
            assert np.isclose(p1, np.vdot(phi, mp.M_op(x, N, M) @ phi).real)
            Mx = mp.M_op(x, N, M)
            assert np.allclose(Mx.conj().T @ Mx, Mx)  # (P⊗I)†(P⊗I) = P⊗I


def test_inner_product_of_tensor_products_4_2():
    a, b, c, d = (rand_c(3) for _ in range(4))
    assert np.isclose(np.vdot(np.kron(a, b), np.kron(c, d)), np.vdot(a, c) * np.vdot(b, d))


@pytest.mark.parametrize("n_in,n_out", [(2, 1), (3, 2), (1, 1)])
def test_uniform_superposition_gives_one_over_N(n_in, n_out):
    N, M = 2**n_in, 2**n_out
    f = lambda x: (x * 5 + 1) % M  # 任意の関数
    psi = mp.psi_state(f, n_in, n_out)
    for x in range(N):
        assert np.isclose(mp.prob_input(psi, x, N, M), 1 / N)
        v = mp.M_op(x, N, M) @ psi
        assert np.allclose(v, 1 / np.sqrt(N) * np.kron(mp.ket(x, N), mp.ket(f(x), M)))  # ⑤


def test_general_amplitudes_give_alpha_squared():
    """⑦：P(x*) = |α_x*|²（U_f は振幅を変えない）"""
    alpha = rand_c(4)
    alpha /= np.linalg.norm(alpha)
    psi = mp.psi_state(F_EXAMPLE, 2, 1, alpha)
    for x in range(4):
        assert np.isclose(mp.prob_input(psi, x, 4, 2), abs(alpha[x]) ** 2)


def test_example_8():
    """⑧：|Ψ⟩ の成分、M_11 の対角、M_11|Ψ⟩ = ½|111⟩、確率"""
    psi = mp.psi_state(F_EXAMPLE, 2, 1)
    assert np.allclose(psi, 0.5 * np.array([1, 0, 1, 0, 1, 0, 0, 1]))
    M11 = mp.M_op(3, 4, 2)
    assert np.allclose(np.diag(M11), [0, 0, 0, 0, 0, 0, 1, 1]) and np.allclose(M11, np.diag(np.diag(M11)))
    assert np.allclose(M11 @ psi, 0.5 * mp.ket(7, 8))
    assert np.allclose(mp.proj(3, 4), np.diag([0, 0, 0, 1]))
    assert np.allclose([mp.prob_input(psi, x, 4, 2) for x in range(4)], 0.25)


# ------------------------------------------------------------- 付録A
@pytest.mark.parametrize("N,M", [(4, 2), (3, 5)])
def test_projective_measurement_is_complete(N, M):
    ops = [mp.M_op(x, N, M) for x in range(N)]
    assert np.allclose(sum(ops), np.eye(N * M))  # ΣM_x = I
    for x in range(N):
        for xp in range(N):
            assert np.allclose(ops[x] @ ops[xp], (ops[x] if x == xp else 0 * ops[x]))
    phi = rand_state(N * M)
    assert np.isclose(sum(mp.prob_input(phi, x, N, M) for x in range(N)), 1.0)


def test_post_measurement_state_and_repeatability():
    N, M = 4, 2
    phi = rand_state(N * M)
    for x in range(N):
        post, p = mp.post_measurement_state(phi, x, N, M)
        assert np.isclose(np.linalg.norm(post), 1.0)
        post2, p2 = mp.post_measurement_state(post, x, N, M)  # 同じ測定をもう一度：確率 1
        assert np.isclose(p2, 1.0) and np.allclose(post2, post)
        assert all(np.isclose(mp.prob_input(post, xp, N, M), 0) for xp in range(N) if xp != x)


def test_post_measurement_of_example_is_a_product_state():
    psi = mp.psi_state(F_EXAMPLE, 2, 1)
    post, p = mp.post_measurement_state(psi, 3, 4, 2)
    assert np.isclose(p, 0.25) and np.allclose(post, mp.ket(7, 8))  # |11⟩|1⟩
    post0, p0 = mp.post_measurement_state(psi, 0, 4, 2)
    assert np.allclose(post0, mp.ket(0, 8))  # |00⟩|0⟩


def test_general_measurement_kraus_completeness():
    for eps in (0.0, 0.1, 0.3, 0.5):
        K0, K1 = mp.unsharp_measurement_kraus(eps)
        assert np.allclose(K0.conj().T @ K0 + K1.conj().T @ K1, np.eye(2))
        E0 = K0.conj().T @ K0
        assert np.allclose(E0, np.diag([1 - eps, eps]))
        psi = rand_state(2)
        p0 = np.linalg.norm(K0 @ psi) ** 2
        assert np.isclose(p0, (1 - eps) * abs(psi[0]) ** 2 + eps * abs(psi[1]) ** 2)
        assert np.isclose(p0 + np.linalg.norm(K1 @ psi) ** 2, 1.0)
    # ε=0 なら射影測定
    K0, K1 = mp.unsharp_measurement_kraus(0.0)
    assert np.allclose(K0, mp.proj(0, 2)) and np.allclose(K1, mp.proj(1, 2))
    # 射影測定 ≠ 一般の測定：K_0 は ε>0 で射影演算子でない
    K0, _ = mp.unsharp_measurement_kraus(0.1)
    assert not np.allclose(K0 @ K0, K0)


def test_sum_of_kraus_then_product_is_not_identity():
    """ΣK†K = I だが、(ΣK†)(ΣK) = I + 2√(p(1-p)) X"""
    for p in (0.1, 0.3):
        K0, K1 = mp.bit_flip_kraus(p)
        assert np.allclose(K0.conj().T @ K0 + K1.conj().T @ K1, np.eye(2))
        S = K0 + K1
        assert np.allclose(S.conj().T @ S, np.eye(2) + 2 * np.sqrt(p * (1 - p)) * mp.X)
    for gamma in (0.2, 0.7):
        K0, K1 = mp.amplitude_damping_kraus(gamma)
        assert np.allclose(K0.conj().T @ K0 + K1.conj().T @ K1, np.eye(2))
        assert np.allclose(K1.conj().T @ K1, gamma * mp.proj(1, 2))  # γ|1⟩⟨1|


def test_stinespring_form_of_kraus():
    """K_m = ⟨m_E|U|0_E⟩ から ΣK†K = I（U がユニタリなら）"""
    from scipy.stats import unitary_group

    U = unitary_group.rvs(4, random_state=1)  # 系(2) ⊗ 環境(2)
    K = [U.reshape(2, 2, 2, 2)[:, m, :, 0] for m in range(2)]  # 行(系,環境m), 列(系, 環境0)
    assert np.allclose(sum(k.conj().T @ k for k in K), np.eye(2))


# ------------------------------------------------------------- 付録B
def test_result_register_collapse_for_example():
    psi = mp.psi_state(F_EXAMPLE, 2, 1)
    s0, p0 = mp.result_register_collapse(psi, 0, 4, 2)
    s1, p1 = mp.result_register_collapse(psi, 1, 4, 2)
    assert np.isclose(p0, 0.75) and np.isclose(p1, 0.25)
    assert np.allclose(s0, np.array([1, 0, 1, 0, 1, 0, 0, 0]) / np.sqrt(3))  # (|00⟩+|01⟩+|10⟩)|0⟩/√3
    assert np.allclose(s1, mp.ket(7, 8))  # |11⟩|1⟩


def test_result_register_collapse_is_uniform_on_preimage():
    n_in, n_out = 3, 2
    N, M = 2**n_in, 2**n_out
    f = lambda x: (x * x + 1) % M
    alpha = rand_c(N)
    alpha /= np.linalg.norm(alpha)
    psi = mp.psi_state(f, n_in, n_out, alpha)
    for y in range(M):
        pre = [x for x in range(N) if f(x) == y]
        p_expected = sum(abs(alpha[x]) ** 2 for x in pre)
        if p_expected < 1e-12:
            continue
        s, p = mp.result_register_collapse(psi, y, N, M)
        assert np.isclose(p, p_expected)
        expected = np.zeros(N, dtype=complex)
        for x in pre:
            expected[x] = alpha[x]
        assert np.allclose(s, np.kron(expected / np.sqrt(p_expected), mp.ket(y, M)))


def test_rank_of_coefficient_matrix_decides_product_form():
    N = 4
    for name, f, n_out, rank in [("constant", lambda x: 0, 1, 1), ("example", F_EXAMPLE, 1, 2), ("injective", lambda x: x, 2, 4)]:
        M = 2**n_out
        psi = mp.psi_state(f, 2, n_out)
        C = mp.coefficient_matrix(psi, N, M)
        assert np.linalg.matrix_rank(C) == rank, name
    # 階数 1 ⇔ 積状態
    C = np.outer(rand_c(4), rand_c(2))
    psi = C.reshape(-1)
    u = C[:, 0] / C[0, 0] * C[0, 0]
    assert np.allclose(psi, np.kron(C[:, 0] / C[0, 0], C[0, :]))  # C = u v^T と書ける


def test_schmidt_numbers_of_example_and_entropy():
    psi = mp.psi_state(F_EXAMPLE, 2, 1)
    p = mp.schmidt_probabilities(psi, 4, 2)
    assert np.allclose(sorted(p), [0.25, 0.75])
    assert np.isclose(mp.entropy_bits(p), -(0.75 * np.log2(0.75) + 0.25 * np.log2(0.25)))
    assert np.isclose(mp.entropy_bits(p), 0.8113, atol=1e-4)
    # 定数関数：エントロピー 0、1対1：log2 N = 2 bit（均等な重ね合わせ）
    assert np.isclose(mp.entropy_bits(mp.schmidt_probabilities(mp.psi_state(lambda x: 0, 2, 1), 4, 2)), 0.0)
    assert np.isclose(mp.entropy_bits(mp.schmidt_probabilities(mp.psi_state(lambda x: x, 2, 2), 4, 4)), 2.0)


def test_reduced_state_diagonal_is_input_probability():
    for N, M in [(4, 2), (2, 4)]:
        phi = rand_state(N * M)
        rho = mp.reduced_input_state(phi, N, M)
        assert np.isclose(np.trace(rho), 1.0)
        assert np.allclose(np.diag(rho).real, [mp.prob_input(phi, x, N, M) for x in range(N)])


# ------------------------------------------------------------- 付録C
def test_tensor_product_invariants():
    A, B = rand_c(2, 2), rand_c(3, 3)
    K = np.kron(A, B)
    assert np.isclose(np.trace(K), np.trace(A) * np.trace(B))
    assert np.allclose(K.conj().T, np.kron(A.conj().T, B.conj().T))
    assert np.allclose(K.T, np.kron(A.T, B.T))
    assert np.isclose(np.linalg.det(K), np.linalg.det(A) ** 3 * np.linalg.det(B) ** 2)  # det(A⊗B)=det(A)^n det(B)^m
    ev = sorted(np.linalg.eigvals(K), key=lambda z: (z.real, z.imag))
    ev2 = sorted([a * b for a in np.linalg.eigvals(A) for b in np.linalg.eigvals(B)], key=lambda z: (z.real, z.imag))
    assert np.allclose(ev, ev2)
    from scipy.stats import unitary_group

    U1, U2 = unitary_group.rvs(2, random_state=2), unitary_group.rvs(3, random_state=3)
    W = np.kron(U1, U2)
    assert np.allclose(W.conj().T @ W, np.eye(6))


def test_qiskit_ordering_matches_the_note():
    qc, sv = mp.qiskit_example()
    psi = mp.psi_state(F_EXAMPLE, 2, 1)
    assert np.allclose(sv.data, psi)  # 教科書の「第1」を番号の大きい量子ビットに対応させると、同じベクトル
    # 入力レジスタ（q2, q1）の確率
    probs = sv.probabilities([2, 1])  # 戻り値は q2q1 のラベル順（添字 = 2*q2 + q1）
    assert np.allclose(probs, 0.25)
    # 量子ビット 0 に X → ラベル '01'、ベクトル (0,1,0,0)
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator, Statevector

    q = QuantumCircuit(2)
    q.x(0)
    assert np.allclose(Statevector(q).data, [0, 1, 0, 0])
    cx01, cx10 = QuantumCircuit(2), QuantumCircuit(2)
    cx01.cx(0, 1)
    cx10.cx(1, 0)
    assert np.allclose(Operator(cx10).data, mp.CNOT)  # 教科書の CNOT（制御が左）は cx(1, 0)
    assert not np.allclose(Operator(cx01).data, mp.CNOT)
    # M_11 = P_11⊗I_2 を Qiskit の状態に作用させても同じ
    assert np.allclose(mp.M_op(3, 4, 2) @ sv.data, 0.5 * mp.ket(7, 8))


def test_qiskit_single_qubit_gate_positions():
    """付録C-3：q0 に X は I⊗X、q1 に X は X⊗I（教科書の第1 = q1）"""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator, Statevector

    a, b = QuantumCircuit(2), QuantumCircuit(2)
    a.x(0)
    b.x(1)
    assert np.allclose(Operator(a).data, np.kron(mp.I2, mp.X))
    assert np.allclose(Operator(b).data, np.kron(mp.X, mp.I2))
    assert np.allclose(Statevector(b).data, [0, 0, 1, 0])  # |10⟩


# ------------------------------------------------------------- 部分トレース（別ノート）
def test_partial_trace_definition_on_product_operators():
    """Tr_B(X⊗Y) = X tr(Y)、Tr_A(X⊗Y) = tr(X) Y"""
    X_, Y_ = rand_c(3, 3), rand_c(2, 2)
    rho = np.kron(X_, Y_)
    assert np.allclose(mp.partial_trace(rho, 3, 2, "A"), X_ * np.trace(Y_))
    assert np.allclose(mp.partial_trace(rho, 3, 2, "B"), np.trace(X_) * Y_)


def test_expectation_value_needs_only_the_reduced_state():
    """tr[(A⊗I)ρ] = tr[A Tr_B ρ]"""
    for N, M in [(4, 2), (2, 4), (3, 3)]:
        phi = rand_state(N * M)
        rho = mp.density(phi)
        A = rand_c(N, N)
        assert np.isclose(np.trace(np.kron(A, np.eye(M)) @ rho), np.trace(A @ mp.partial_trace(rho, N, M, "A")))


def test_reduced_state_is_C_Cdagger_and_CTCbar():
    for N, M in [(4, 2), (2, 4), (3, 5)]:
        phi = rand_state(N * M)
        C = mp.coefficient_matrix(phi, N, M)
        rho = mp.density(phi)
        assert np.allclose(mp.partial_trace(rho, N, M, "A"), C @ C.conj().T)
        assert np.allclose(mp.partial_trace(rho, N, M, "B"), C.T @ C.conj())
        # 固有値は、Σ s_k²（シュミット係数の2乗）
        ev = np.sort(np.linalg.eigvalsh(C @ C.conj().T))[::-1][: min(N, M)]
        assert np.allclose(ev, np.sort(np.linalg.svd(C, compute_uv=False) ** 2)[::-1])
        assert np.isclose(np.trace(C @ C.conj().T), 1.0)


def test_reduced_state_of_the_example():
    psi = mp.psi_state(F_EXAMPLE, 2, 1)
    rho_a = mp.partial_trace(mp.density(psi), 4, 2, "A")
    expect = 0.25 * np.array([[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0], [0, 0, 0, 1]])
    assert np.allclose(rho_a, expect)
    assert np.allclose(np.sort(np.linalg.eigvalsh(rho_a)), [0, 0, 0.25, 0.75])
    rho_b = mp.partial_trace(mp.density(psi), 4, 2, "B")
    assert np.allclose(rho_b, np.diag([0.75, 0.25]))
    # 固有ベクトル：(|00⟩+|01⟩+|10⟩)/√3（固有値 3/4）と |11⟩（固有値 1/4）。付録B-2 の測定後の入力の状態
    s = np.array([1, 1, 1, 0]) / np.sqrt(3)
    assert np.allclose(rho_a @ s, 0.75 * s) and np.allclose(rho_a @ mp.ket(3, 4), 0.25 * mp.ket(3, 4))
    # ρ_A = Σ_y P(y) |φ_y⟩⟨φ_y|
    mix = sum(p * np.outer(v, v.conj()) for v, p in [(s, 0.75), (mp.ket(3, 4), 0.25)])
    assert np.allclose(rho_a, mix)


def test_constant_and_injective_functions():
    rho_const = mp.partial_trace(mp.density(mp.psi_state(lambda x: 0, 2, 1)), 4, 2, "A")
    assert np.allclose(rho_const, np.full((4, 4), 0.25))  # 純粋状態（一様）
    assert np.isclose(np.trace(rho_const @ rho_const), 1.0)
    rho_inj = mp.partial_trace(mp.density(mp.psi_state(lambda x: x, 2, 2)), 4, 4, "A")
    assert np.allclose(rho_inj, np.eye(4) / 4)  # 最大混合状態
    assert np.isclose(np.trace(rho_inj @ rho_inj), 0.25)


def test_interference_after_hadamard_depends_on_the_result_register():
    """入力に H^{⊗2} をかけて 00 が出る確率：定数 1、例 5/8、1対1 1/4"""
    for f, n_out, expect in [(lambda x: 0, 1, 1.0), (F_EXAMPLE, 1, 5 / 8), (lambda x: x, 2, 0.25)]:
        psi = mp.psi_state(f, 2, n_out)
        rho_a = mp.partial_trace(mp.density(psi), 4, 2**n_out, "A")
        p = mp.prob_all_zero_after_hadamard(rho_a, 2)
        assert np.isclose(p, expect)
        assert np.isclose(p, rho_a.sum().real / 4)  # (1/N) Σ ρ_{xx'}
        # 全体の状態に H⊗H⊗I をかけて、入力が 00 になる確率と一致
        H2 = np.kron(mp.hadamard_all(2), np.eye(2**n_out))
        out = H2 @ psi
        assert np.isclose(p, mp.prob_input(out, 0, 4, 2**n_out))


def test_visibility_and_environment_overlap():
    for theta in (0.0, 0.4, 1.0, np.pi / 2, 2.5, np.pi):
        phi = mp.two_qubit_state(theta)
        rho_a = mp.partial_trace(mp.density(phi), 2, 2, "A")
        assert np.isclose(abs(rho_a[0, 1]), abs(np.cos(theta)) / 2)  # コヒーレンス = |⟨e0|e1⟩|/2
        H = mp.hadamard_all(1)
        p0 = (H @ rho_a @ H.conj().T)[0, 0].real
        assert np.isclose(p0, (1 + np.cos(theta)) / 2)
    # θ=π/2：環境が直交 → ρ_A = I/2（ベル状態）
    bell = mp.two_qubit_state(np.pi / 2)
    assert np.allclose(mp.partial_trace(mp.density(bell), 2, 2, "A"), np.eye(2) / 2)


def test_environment_picture_gives_kraus_sum():
    """Tr_E[U(ρ⊗|0⟩⟨0|)U†] = Σ_m K_m ρ K_m†、K_m = ⟨m_E|U|0_E⟩"""
    from scipy.stats import unitary_group

    U = unitary_group.rvs(4, random_state=11)
    K = [U.reshape(2, 2, 2, 2)[:, m, :, 0] for m in range(2)]  # (系, 環境m; 系, 環境0)
    rho = mp.density(rand_state(2))
    big = U @ np.kron(rho, mp.proj(0, 2)) @ U.conj().T
    assert np.allclose(mp.partial_trace(big, 2, 2, "A"), sum(k @ rho @ k.conj().T for k in K))


def test_unsharp_measurement_differs_from_readout_error_after_the_measurement():
    """付録A-4：弱い測定 K_0 と、射影測定＋ラベルの取り違え（確率 ε）は、結果の確率は同じだが、測定後の状態が違う"""
    eps = 0.1
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    K0, _ = mp.unsharp_measurement_kraus(eps)
    v = K0 @ plus
    p0 = float(np.vdot(v, v).real)
    post_weak = np.outer(v, v.conj()) / p0
    # ラベル取り違えの模型：結果ラベル 0 の条件付き状態は (1-ε)|0⟩⟨0| + ε|1⟩⟨1|（|+⟩ では確率 1/2 ずつ）
    P0, P1 = mp.proj(0, 2), mp.proj(1, 2)
    p0_mis = (1 - eps) * np.vdot(plus, P0 @ plus).real + eps * np.vdot(plus, P1 @ plus).real
    post_mis = ((1 - eps) * P0 @ np.outer(plus, plus.conj()) @ P0 + eps * P1 @ np.outer(plus, plus.conj()) @ P1) / p0_mis
    assert np.isclose(p0, p0_mis)
    assert np.allclose(post_mis, np.diag([1 - eps, eps]))
    assert abs(post_weak[0, 1]) > 0.1 and abs(post_mis[0, 1]) < 1e-12  # 弱い測定にはコヒーレンスが残る
    assert np.isclose(abs(post_weak[0, 1]), np.sqrt(eps * (1 - eps)))


def test_rank_is_not_a_measure_of_entanglement():
    """付録B-3：階数は積状態の判定。振幅が偏ると 1対1 でも階数・エントロピーは下がり、階数が大きくてもエントロピーは小さくなりうる"""
    alpha = np.array([np.sqrt(0.9), np.sqrt(0.1), 0, 0], dtype=complex)
    psi = mp.psi_state(lambda x: x, 2, 2, alpha)
    C = mp.coefficient_matrix(psi, 4, 4)
    assert np.linalg.matrix_rank(C) == 2
    assert np.isclose(mp.entropy_bits(mp.schmidt_probabilities(psi, 4, 4)), 0.469, atol=1e-3)
    assert mp.entropy_bits([0.999, 0.0005, 0.0005]) < mp.entropy_bits([0.5, 0.5])


def test_injective_function_rank_counts_nonzero_amplitudes():
    """付録B-3：1対1では階数 = 振幅がゼロでない入力の個数。偏りだけならエントロピーが下がる"""
    alpha = np.sqrt(np.array([0.4, 0.3, 0.2, 0.1]), dtype=complex)
    psi = mp.psi_state(lambda x: x, 2, 2, alpha)
    assert np.linalg.matrix_rank(mp.coefficient_matrix(psi, 4, 4)) == 4
    assert mp.entropy_bits(mp.schmidt_probabilities(psi, 4, 4)) < 2.0
    # 入力が |0⟩ だけなら、非定数の f でも積状態（階数 1）
    psi0 = mp.psi_state(F_EXAMPLE, 2, 1, np.array([1, 0, 0, 0], dtype=complex))
    assert np.linalg.matrix_rank(mp.coefficient_matrix(psi0, 4, 2)) == 1
