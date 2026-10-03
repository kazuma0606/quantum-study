/-
  det(e^A) = e^{tr A} の形式証明（対角化できる行列、とくにエルミート行列の場合）
  対応ノート: 研究ノート/04_群論・代数/det_exp_trace_proof.md

  Mathlib v4.28.0 には、一般の行列についてのこの定理はまだない
  （Mathlib/Analysis/Normed/Algebra/MatrixExponential.lean の TODO に挙がっている）。
  ここでは、ノートの証明1（対角化を使う）と同じ道筋で、次を証明する。
    1. 対角行列 D：det(e^D) = e^{tr D}（ノートの式12〜14）
    2. A = U D U⁻¹ と書ける行列（ノートの式1〜8、式17）
    3. エルミート行列 H と複素数 c について det(e^{cH}) = e^{c tr H}
       （c = it とすると、SU(2) の議論で使う det(e^{itH}) = e^{it tr H}）
  一般の行列（ノートの証明2：Jacobi の公式）は今後の課題。
-/
import Mathlib.Analysis.Normed.Algebra.MatrixExponential
import Mathlib.Analysis.Matrix.Spectrum
import Mathlib.Analysis.SpecialFunctions.Exponential

open Matrix NormedSpace

namespace QuantumStudy

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- 1. 対角行列：det(e^D) = ∏ e^{d_i} = e^{Σ d_i} = e^{tr D} -/
theorem det_exp_diagonal (d : n → ℂ) :
    (exp (diagonal d)).det = Complex.exp (diagonal d).trace := by
  rw [Matrix.exp_diagonal, det_diagonal, trace_diagonal, Complex.exp_sum, Pi.exp_def,
    ← Complex.exp_eq_exp_ℂ]

/-- 2. 対角化できる行列：A = U D U⁻¹ なら det(e^A) = e^{tr A}（ノートの証明1） -/
theorem det_exp_conj_diagonal (U : Matrix n n ℂ) (hU : IsUnit U) (d : n → ℂ) :
    (exp (U * diagonal d * U⁻¹)).det = Complex.exp (U * diagonal d * U⁻¹).trace := by
  rw [Matrix.exp_conj U _ hU, det_conj hU, trace_conj hU, det_exp_diagonal]

/-- 3. エルミート行列 H と複素数 c について det(e^{cH}) = e^{c tr H}。
  スペクトル定理 H = U D U*（U はユニタリ、D は実対角）を使って 2. に帰着させる。 -/
theorem det_exp_smul_of_isHermitian {H : Matrix n n ℂ} (hH : H.IsHermitian) (c : ℂ) :
    (exp (c • H)).det = Complex.exp (c * H.trace) := by
  set U : Matrix n n ℂ := (hH.eigenvectorUnitary : Matrix n n ℂ) with hUdef
  set d : n → ℂ := RCLike.ofReal ∘ hH.eigenvalues
  have hspec : H = U * diagonal d * star U := by
    simpa [hUdef, d] using hH.spectral_theorem
  have hinv : U⁻¹ = star U := Matrix.inv_eq_right_inv (Unitary.coe_mul_star_self _)
  have hunit : IsUnit U := Unitary.isUnit_coe
  have hcH : c • H = U * diagonal (c • d) * U⁻¹ := by
    rw [hinv, diagonal_smul, Matrix.mul_smul, Matrix.smul_mul, ← hspec]
  rw [hcH, det_exp_conj_diagonal U hunit, ← hcH, trace_smul, smul_eq_mul]

/-- 系：トレースゼロのエルミート行列 H なら、すべての実数 t で det(e^{itH}) = 1。
  （e^{itH} がユニタリであることと合わせて、e^{itH} ∈ SU(n)） -/
theorem det_exp_I_smul_eq_one {H : Matrix n n ℂ} (hH : H.IsHermitian) (h0 : H.trace = 0)
    (t : ℝ) : (exp (((t : ℂ) * Complex.I) • H)).det = 1 := by
  rw [det_exp_smul_of_isHermitian hH, h0, mul_zero, Complex.exp_zero]

/-- 反例：1つの U だけからは tr = 0 は出ない（ノートの「この公式の意味」）。
  A = diag(2π, 0) はエルミートで e^{iA} = I（したがって det = 1）だが、tr A = 2π ≠ 0。 -/
theorem exp_I_smul_diag_two_pi :
    exp (Complex.I • diagonal ![(2 * Real.pi : ℂ), 0]) = (1 : Matrix (Fin 2) (Fin 2) ℂ) ∧
      (diagonal ![(2 * Real.pi : ℂ), 0]).trace ≠ 0 := by
  constructor
  · rw [← diagonal_smul, Matrix.exp_diagonal, Pi.exp_def, ← diagonal_one]
    congr 1
    funext i
    fin_cases i
    · simp [← Complex.exp_eq_exp_ℂ, mul_comm Complex.I, Complex.exp_two_pi_mul_I]
    · simp
  · simp [trace_diagonal, Fin.sum_univ_two, Real.pi_ne_zero]

end QuantumStudy
