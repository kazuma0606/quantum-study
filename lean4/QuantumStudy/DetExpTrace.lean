/-
  det(e^A) = e^{tr A} の形式証明
  対応ノート: 研究ノート/04_群論・代数/det_exp_trace_proof.md

  Mathlib v4.28.0 には、この定理はまだない
  （Mathlib/Analysis/Normed/Algebra/MatrixExponential.lean の TODO に挙がっている）。

  前半：ノートの証明1（対角化を使う）と同じ道筋
    1. 対角行列 D：det(e^D) = e^{tr D}（ノートの式12〜14）
    2. A = U D U⁻¹ と書ける行列（ノートの式1〜8、式17）
    3. エルミート行列 H と複素数 c について det(e^{cH}) = e^{c tr H}
       （c = it とすると、SU(2) の議論で使う det(e^{itH}) = e^{it tr H}）

  後半：ノートの証明2（Jacobi の公式と微分方程式）と同じ道筋で、一般の複素正方行列について
    手順1. 行列式は微分可能（置換の和と、成分の積の微分可能性から）
    手順2. 単位行列での行列式の微分は、方向 M に対して tr M（ノートの式20。Mathlib の
           「det(1 + X•M) の X の1次の係数 = tr M」を、h ↦ det(1 + h•M) の微分に読み替える）
    手順3. g(h) = det(e^{hA}) の h = 0 での微分は tr A（連鎖律）
    手順4. f(t) = det(e^{tA}) は f(t+h) = f(t) g(h) なので f′(t) = f(t)·tr A（ノートの式23）
    手順5. e^{−t tr A} f(t) の微分は 0 なので定数で、t = 1 として det(e^A) = e^{tr A}（ノートの式24）
  手順2 の「微分」は、ノートの Jacobi の公式（式21）の M = 1 の場合にあたる。
-/
import Mathlib.Analysis.Normed.Algebra.MatrixExponential
import Mathlib.Analysis.Matrix.Spectrum
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.Calculus.FDeriv.Pi
import Mathlib.Analysis.Calculus.FDeriv.Mul
import Mathlib.Analysis.Calculus.Deriv.Polynomial
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff

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

/-! ## 一般の複素正方行列（ノートの証明2） -/

section General

open Polynomial
-- 微分を扱うため、行列に作用素ノルムを入れる（どのノルムでも、微分可能性と微分は同じ）
open scoped Matrix.Norms.Operator

/-- 手順1：行列式は微分可能 -/
theorem differentiable_det : Differentiable ℂ (fun M : Matrix n n ℂ => M.det) := by
  simp only [det_apply]
  refine Differentiable.fun_sum fun σ _ => ?_
  refine Differentiable.const_smul ?_ _
  intro M
  have h : ∀ i ∈ (Finset.univ : Finset n),
      HasFDerivAt (fun M : Matrix n n ℂ => M (σ i) i)
        (fderiv ℂ (fun M : Matrix n n ℂ => M (σ i) i) M) M :=
    fun i _ => (by fun_prop : DifferentiableAt ℂ (fun M : Matrix n n ℂ => M (σ i) i) M).hasFDerivAt
  exact (HasFDerivAt.finset_prod h).differentiableAt

/-- 手順2a：h ↦ det(1 + h•M) の 0 での微分は tr M（多項式 det(1 + X•M) の1次の係数） -/
theorem hasDerivAt_det_one_add_smul (M : Matrix n n ℂ) :
    HasDerivAt (fun h : ℂ => (1 + h • M).det) M.trace 0 := by
  set p : ℂ[X] := det (1 + (X : ℂ[X]) • M.map C)
  have heval : ∀ h : ℂ, p.eval h = (1 + h • M).det := by
    intro h
    have := (Polynomial.evalRingHom h).map_det (1 + (X : ℂ[X]) • M.map C)
    rw [Polynomial.coe_evalRingHom] at this
    rw [this]
    congr 1
    ext i j
    by_cases hij : i = j <;> simp [hij] <;> ring
  have hp := p.hasDerivAt 0
  rw [derivative_det_one_add_X_smul] at hp
  have hfun : (fun x : ℂ => p.eval x) = fun h : ℂ => (1 + h • M).det := funext heval
  rw [hfun] at hp
  exact hp

/-- 手順2b：単位行列での行列式の微分は、方向 M に対して tr M -/
theorem fderiv_det_one_apply (M : Matrix n n ℂ) :
    fderiv ℂ (fun M : Matrix n n ℂ => M.det) 1 M = M.trace := by
  have hline : HasDerivAt (fun h : ℂ => (1 : Matrix n n ℂ) + h • M) M 0 := by
    simpa using ((hasDerivAt_id (0 : ℂ)).smul_const M).const_add (1 : Matrix n n ℂ)
  have hcomp := (differentiable_det (n := n) 1).hasFDerivAt.comp_hasDerivAt_of_eq (x := (0 : ℂ))
    hline (by simp)
  exact (hcomp.unique (hasDerivAt_det_one_add_smul M))

/-- 手順3：g(h) = det exp(h•A) の 0 での微分は tr A -/
theorem hasDerivAt_det_exp_smul_zero (A : Matrix n n ℂ) :
    HasDerivAt (fun h : ℂ => (exp (h • A)).det) A.trace 0 := by
  have hexp := hasDerivAt_exp_smul_const (𝕂 := ℂ) A (0 : ℂ)
  rw [zero_smul, exp_zero, one_mul] at hexp
  have hcomp := (differentiable_det (n := n) (exp ((0 : ℂ) • A))).hasFDerivAt.comp_hasDerivAt
    (x := (0 : ℂ)) (by simpa using hexp)
  rw [zero_smul, exp_zero, fderiv_det_one_apply] at hcomp
  exact hcomp

/-- 手順4：f(t) = det exp(t•A) は f′(t) = f(t)·tr A を満たす -/
theorem hasDerivAt_det_exp_smul (A : Matrix n n ℂ) (t : ℂ) :
    HasDerivAt (fun s : ℂ => (exp (s • A)).det) ((exp (t • A)).det * A.trace) t := by
  have hsplit : (fun s : ℂ => (exp (s • A)).det) =
      fun s => (exp (t • A)).det * (exp ((s - t) • A)).det := by
    funext s
    rw [← det_mul, ← Matrix.exp_add_of_commute _ _ ((Commute.refl A).smul_left t |>.smul_right _),
      ← add_smul, add_sub_cancel]
  rw [hsplit]
  have hg := hasDerivAt_det_exp_smul_zero A
  rw [← sub_self t] at hg
  have hg' : HasDerivAt (fun s : ℂ => (exp ((s - t) • A)).det) A.trace t :=
    hg.comp_sub_const t t
  exact hg'.const_mul _

/-- 手順5：det(e^A) = e^{tr A}（一般の複素正方行列） -/
theorem det_exp (A : Matrix n n ℂ) : (exp A).det = Complex.exp A.trace := by
  set f : ℂ → ℂ := fun s => (exp (s • A)).det
  set q : ℂ → ℂ := fun s => Complex.exp (-(s * A.trace)) * f s
  have hq : ∀ s, HasDerivAt q 0 s := by
    intro s
    have h1 : HasDerivAt (fun s : ℂ => Complex.exp (-(s * A.trace)))
        (Complex.exp (-(s * A.trace)) * (-A.trace)) s := by
      have := ((hasDerivAt_id s).mul_const A.trace).neg.cexp
      simpa using this
    have := h1.mul (hasDerivAt_det_exp_smul A s)
    convert this using 1
    ring
  have hconst := is_const_of_deriv_eq_zero (fun s => (hq s).differentiableAt)
    (fun s => (hq s).deriv) 1 0
  simp only [q, f, one_smul, zero_smul, exp_zero, det_one, mul_one, zero_mul, neg_zero,
    Complex.exp_zero, one_mul] at hconst
  have hne : Complex.exp (-A.trace) ≠ 0 := Complex.exp_ne_zero _
  calc (exp A).det = Complex.exp A.trace * (Complex.exp (-A.trace) * (exp A).det) := by
        rw [← mul_assoc, ← Complex.exp_add, add_neg_cancel, Complex.exp_zero, one_mul]
    _ = Complex.exp A.trace := by rw [hconst, mul_one]

end General

end QuantumStudy
