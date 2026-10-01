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
