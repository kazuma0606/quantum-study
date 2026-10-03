# pytest テスト
# 対応ノート: 研究ノート/04_群論・代数/det_exp_trace_proof.md

import numpy as np
import pytest
from sympy import Matrix, exp, trace, det, simplify
from det_exp_trace import verify_numerically, proof1_step_by_step


# ============================================================
# 数値テスト（NumPy + SciPy）
# ============================================================

class TestNumerical:

    def test_2x2_diagonalizable(self):
        A = np.array([[2, 1], [0, 3]], dtype=float)
        r = verify_numerically(A)
        assert r["match"], f"det(exp(A))={r['det(exp(A))']}, exp(tr(A))={r['exp(tr(A))']}"

    def test_2x2_symmetric(self):
        A = np.array([[1, 2], [2, 3]], dtype=float)
        r = verify_numerically(A)
        assert r["match"]

    def test_3x3_upper_triangular(self):
        A = np.array([[1, 2, 0], [0, 3, 1], [0, 0, 2]], dtype=float)
        r = verify_numerically(A)
        assert r["match"]

    def test_diagonal_matrix(self):
        A = np.diag([1.0, 2.0, 3.0])
        r = verify_numerically(A)
        assert r["match"]

    def test_zero_matrix(self):
        # e^0 = I, det(I) = 1, e^(tr 0) = e^0 = 1
        A = np.zeros((3, 3))
        r = verify_numerically(A)
        assert r["match"]

    def test_traceless_matrix(self):
        # tr A = 0 → det(e^A) = e^0 = 1
        # Pauli行列はトレースゼロ → これが SU(2) の条件
        sx = np.array([[0, 1], [1, 0]], dtype=float)
        r = verify_numerically(sx)
        assert r["match"]
        assert np.isclose(r["exp(tr(A))"], 1.0), "トレースゼロなら det(e^A) = 1"


# ============================================================
# 記号テスト（SymPy）：証明1の各ステップ
# ============================================================

class TestSymbolicProof1:

    @pytest.fixture
    def A_2x2(self):
        return Matrix([[2, 1], [0, 3]])

    @pytest.fixture
    def A_3x3(self):
        return Matrix([[1, 2, 0], [0, 3, 1], [0, 0, 2]])

    def test_all_steps_2x2(self, A_2x2):
        results = proof1_step_by_step(A_2x2)
        for label, ok in results.items():
            assert ok, f"失敗: {label}"

    def test_all_steps_3x3(self, A_3x3):
        results = proof1_step_by_step(A_3x3)
        for label, ok in results.items():
            assert ok, f"失敗: {label}"

    def test_pauli_sz_traceless(self):
        # sz はトレースゼロ → det(e^sz) = 1
        sz = Matrix([[1, 0], [0, -1]])
        lhs = det(sz.exp())
        assert simplify(lhs - 1) == 0, "Pauli σz: det(e^σz) should be 1"

    def test_pauli_sx_traceless(self):
        sx = Matrix([[0, 1], [1, 0]])
        lhs = det(sx.exp())
        assert simplify(lhs - 1) == 0, "Pauli σx: det(e^σx) should be 1"


# ============================================================
# 証明2（Jacobi の公式）：複素行列・対角化できない行列
# ============================================================

class TestProof2:

    rng = np.random.default_rng(0)

    def random_complex(self, n):
        return self.rng.normal(size=(n, n)) + 1j * self.rng.normal(size=(n, n))

    def test_complex_matrices(self):
        # 複素行列でも det(e^A) = e^(tr A)（位相まで一致する）
        for n in (2, 3, 4):
            A = self.random_complex(n)
            r = verify_numerically(A)
            assert r["match"]

    def test_jordan_block_not_diagonalizable(self):
        # A = [[λ,1],[0,λ]] は対角化できないが、e^{tA} = e^{λt}(I + tN) で det = e^{2λt}
        from scipy.linalg import expm
        lam, t = 0.3, 1.7
        A = np.array([[lam, 1.0], [0.0, lam]])
        E = expm(t * A)
        assert np.allclose(E, np.exp(lam * t) * np.array([[1.0, t], [0.0, 1.0]]))
        assert np.isclose(np.linalg.det(E), np.exp(t * np.trace(A)))
        from sympy import Rational
        assert not Matrix([[Rational(3, 10), 1], [0, Rational(3, 10)]]).is_diagonalizable()

    def test_det_identity_plus_eps(self):
        # det(I + εX) = 1 + ε tr X + O(ε²)
        X = self.random_complex(4)
        for eps in (1e-3, 1e-4):
            d = np.linalg.det(np.eye(4) + eps * X)
            assert abs(d - (1 + eps * np.trace(X))) < 50 * eps**2

    def test_jacobi_formula_three_forms(self):
        # d/dt det M(t) = det M · tr(M^{-1} M') = tr(adj M · M')、M(t) = M0 + t M1 + t² M2
        M0, M1, M2 = (self.random_complex(3) for _ in range(3))
        M = lambda t: M0 + t * M1 + t**2 * M2
        dM = lambda t: M1 + 2 * t * M2
        t, h = 0.4, 1e-6
        lhs = (np.linalg.det(M(t + h)) - np.linalg.det(M(t - h))) / (2 * h)
        inv = np.linalg.inv(M(t))
        form1 = np.linalg.det(M(t)) * np.trace(inv @ dM(t))
        adj = np.linalg.det(M(t)) * inv
        form2 = np.trace(adj @ dM(t))
        assert np.isclose(lhs, form1, rtol=1e-6) and np.isclose(form1, form2)

    def test_log_abs_det_loses_phase(self):
        # d/dt ln|det M| は Re tr(M^{-1} M') だけで、位相の変化を取りこぼす
        from scipy.linalg import expm
        A = np.diag([1j, 1j])                      # det e^{tA} = e^{2it}
        f = lambda t: np.linalg.det(expm(t * A))
        t, h = 0.8, 1e-6
        dlogabs = (np.log(abs(f(t + h))) - np.log(abs(f(t - h)))) / (2 * h)
        assert np.isclose(dlogabs, np.real(np.trace(A)), atol=1e-8)   # = 0
        assert np.isclose(f(t), np.exp(2j * t))                         # 位相は e^{2it}

    def test_ode_solution_g_constant(self):
        # g(t) = e^{-t trA} det e^{tA} は一定（= 1）
        from scipy.linalg import expm
        A = self.random_complex(3)
        for t in np.linspace(0, 2, 9):
            g = np.exp(-t * np.trace(A)) * np.linalg.det(expm(t * A))
            assert np.isclose(g, 1)


# ============================================================
# 「この公式の意味」：1つの U からは tr A = 0 は出ない
# ============================================================

class TestSU2Logic:

    def test_single_U_counterexample_trace(self):
        # A = diag(2π, 0) はエルミートで e^{iA} = I（det = 1）だが tr A = 2π
        from scipy.linalg import expm
        A = np.diag([2 * np.pi, 0.0])
        U = expm(1j * A)
        assert np.allclose(U, np.eye(2)) and np.isclose(np.linalg.det(U), 1)
        assert np.isclose(np.trace(A), 2 * np.pi)

    def test_single_U_counterexample_hermitian(self):
        # A = P diag(2π, 0) P^{-1}（P はユニタリでない）は非エルミートだが e^{iA} = I
        from scipy.linalg import expm
        P = np.array([[1.0, 2.0], [0.0, 1.0]])
        A = P @ np.diag([2 * np.pi, 0.0]) @ np.linalg.inv(P)
        assert not np.allclose(A, A.conj().T)
        assert np.allclose(expm(1j * A), np.eye(2))

    def test_one_parameter_family(self):
        # トレースゼロのエルミート H なら、すべての t で e^{itH} ∈ SU(2)
        from scipy.linalg import expm
        sx = np.array([[0, 1], [1, 0]], dtype=complex)
        sy = np.array([[0, -1j], [1j, 0]])
        sz = np.diag([1.0 + 0j, -1.0])
        H = 0.3 * sx - 1.1 * sy + 0.7 * sz
        for t in np.linspace(-3, 3, 13):
            U = expm(1j * t * H)
            assert np.allclose(U.conj().T @ U, np.eye(2)) and np.isclose(np.linalg.det(U), 1)
        # tr H = c ≠ 0 なら det e^{itH} = e^{itc} は t = 2πk/c でしか 1 にならない
        c = 0.5
        H2 = H + (c / 2) * np.eye(2)
        dets = [np.linalg.det(expm(1j * t * H2)) for t in (1.0, 2 * np.pi / c)]
        assert not np.isclose(dets[0], 1) and np.isclose(dets[1], 1)
