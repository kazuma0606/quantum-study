/-
  シューア分解と、三角化の道による det(e^A) = e^{tr A}
  対応ノート: 研究ノート/04_群論・代数/det_exp_trace_proof.md（証明1の「対角化」を「三角化」に置き換えたもの）

  Mathlib v4.28.0 には、複素行列のシューア分解（ユニタリ行列による三角化）はない
  （Mathlib の docs/undergrad.yaml でも、triangularization は未対応の項目として残っている）。

  1. シューア分解 `schur`：どの複素正方行列 A も、ユニタリ行列 U と上三角行列 T で A = U T U* と書ける。
     行列の大きさ n についての帰納法：
       部品1. 長さ 1 の固有ベクトル u がある（ℂ は代数的閉体）
       部品2. u を最初の列にもつユニタリ行列 W がある（u を正規直交基底に延長する）
       部品3. B = W* A W の第1列は (μ, 0, …, 0)
       部品4. B の右下の n×n 部分に帰納法の仮定を使い、diag(1, U') で組み合わせる
  2. 上三角行列 T について、e^T も上三角で、対角成分は e^{T_ii}（指数関数の級数を成分ごとに見る）
  3. `det_exp_via_schur`：e^{UTU*} = U e^T U* と、上三角行列の行列式 = 対角成分の積から、
     det(e^A) = ∏ e^{T_ii} = e^{Σ T_ii} = e^{tr T} = e^{tr A}
  （DetExpTrace.lean の `det_exp` とは別の道筋。あちらはノートの証明2：微分方程式）
-/
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Eigenspace.Triangularizable
import Mathlib.LinearAlgebra.Matrix.Block
import Mathlib.Analysis.Complex.Polynomial.Basic
import Mathlib.Analysis.Normed.Algebra.MatrixExponential
import Mathlib.Analysis.SpecialFunctions.Exponential

open Matrix

namespace QuantumStudy.Schur

variable {n : ℕ}

/-- 部品1：長さ 1 の固有ベクトルがある（ℂ は代数的閉体） -/
theorem exists_unit_eigenvector (A : Matrix (Fin (n + 1)) (Fin (n + 1)) ℂ) :
    ∃ μ : ℂ, ∃ u : EuclideanSpace ℂ (Fin (n + 1)), ‖u‖ = 1 ∧ ∀ k, (A *ᵥ (fun l => u l)) k = μ * u k := by
  obtain ⟨μ, hμ⟩ := Module.End.exists_eigenvalue (Matrix.toLin' A)
  obtain ⟨v, hv⟩ := hμ.exists_hasEigenvector
  have hAv : A *ᵥ v = μ • v := by rw [← Matrix.toLin'_apply]; exact hv.apply_eq_smul
  set w : EuclideanSpace ℂ (Fin (n + 1)) := WithLp.toLp 2 v with hw
  have hw0 : w ≠ 0 := by
    intro h; apply hv.2; ext k; have := congrArg (fun x : EuclideanSpace ℂ _ => x k) h; simpa [w] using this
  refine ⟨μ, ((‖w‖⁻¹ : ℝ) : ℂ) • w, ?_, ?_⟩
  · rw [norm_smul, Complex.norm_real, norm_inv, norm_norm]
    exact inv_mul_cancel₀ (norm_ne_zero_iff.mpr hw0)
  · intro k
    have : (fun l => (((‖w‖⁻¹ : ℝ) : ℂ) • w) l) = ((‖w‖⁻¹ : ℝ) : ℂ) • v := by
      ext l; simp [w]
    rw [this, Matrix.mulVec_smul, hAv]
    simp [w, smul_eq_mul]
    ring

/-- 部品2：長さ 1 のベクトル u を最初の列にもつユニタリ行列がある -/
theorem exists_unitary_first_col (u : EuclideanSpace ℂ (Fin (n + 1))) (hu : ‖u‖ = 1) :
    ∃ b : OrthonormalBasis (Fin (n + 1)) ℂ (EuclideanSpace ℂ (Fin (n + 1))), b 0 = u := by
  have hv : Orthonormal ℂ (({0} : Set (Fin (n + 1))).restrict fun _ => u) := by
    rw [orthonormal_iff_ite]
    rintro ⟨i, hi⟩ ⟨j, hj⟩
    simp only [Set.mem_singleton_iff] at hi hj
    subst hi; subst hj
    simp [inner_self_eq_norm_sq_to_K, hu]
  obtain ⟨b, hb⟩ := Orthonormal.exists_orthonormalBasis_extension_of_card_eq (𝕜 := ℂ)
    (ι := Fin (n + 1)) (by simp) hv
  exact ⟨b, hb 0 rfl⟩

/-- 正規直交基底 b の各ベクトルを列に並べた行列 -/
noncomputable def basisMatrix (b : OrthonormalBasis (Fin (n + 1)) ℂ (EuclideanSpace ℂ (Fin (n + 1)))) :
    Matrix (Fin (n + 1)) (Fin (n + 1)) ℂ :=
  (EuclideanSpace.basisFun (Fin (n + 1)) ℂ).toBasis.toMatrix b

theorem basisMatrix_apply (b : OrthonormalBasis (Fin (n + 1)) ℂ (EuclideanSpace ℂ (Fin (n + 1))))
    (k j : Fin (n + 1)) : basisMatrix b k j = b j k := by
  simp [basisMatrix, Module.Basis.toMatrix_apply]

theorem basisMatrix_mem_unitary (b : OrthonormalBasis (Fin (n + 1)) ℂ (EuclideanSpace ℂ (Fin (n + 1)))) :
    basisMatrix b ∈ unitaryGroup (Fin (n + 1)) ℂ :=
  (EuclideanSpace.basisFun (Fin (n + 1)) ℂ).toMatrix_orthonormalBasis_mem_unitary b

/-- 部品3：b 0 = u が固有ベクトルなら、W*AW の第1列は (μ, 0, …, 0) -/
theorem first_col_eq_zero (A : Matrix (Fin (n + 1)) (Fin (n + 1)) ℂ) (μ : ℂ)
    (u : EuclideanSpace ℂ (Fin (n + 1))) (hAu : ∀ k, (A *ᵥ (fun l => u l)) k = μ * u k)
    (b : OrthonormalBasis (Fin (n + 1)) ℂ (EuclideanSpace ℂ (Fin (n + 1)))) (hb : b 0 = u)
    (i : Fin (n + 1)) (hi : i ≠ 0) :
    (star (basisMatrix b) * A * basisMatrix b) i 0 = 0 := by
  have hcol : ∀ k, (A * basisMatrix b) k 0 = μ * u k := by
    intro k
    rw [← hAu k, Matrix.mul_apply]
    simp [Matrix.mulVec, dotProduct, basisMatrix_apply, hb]
  have horth : inner ℂ (b i) (b 0) = 0 := by
    have := orthonormal_iff_ite.mp b.orthonormal i 0
    simp only [hi, if_false] at this
    exact this
  rw [Matrix.mul_assoc, Matrix.mul_apply]
  simp only [Matrix.star_eq_conjTranspose, conjTranspose_apply, basisMatrix_apply, hcol]
  rw [EuclideanSpace.inner_eq_star_dotProduct, hb] at horth
  simp only [dotProduct, Pi.star_apply] at horth
  calc ∑ k, star (b i k) * (μ * u k) = μ * ∑ k, u k * star (b i k) := by
        rw [Finset.mul_sum]; congr 1; ext k; ring
    _ = 0 := by rw [horth, mul_zero]

/-- ブロック対角の拡張 diag(1, U)（(n+1)×(n+1) 行列） -/
def extend (U : Matrix (Fin n) (Fin n) ℂ) : Matrix (Fin (n + 1)) (Fin (n + 1)) ℂ :=
  Matrix.of (Fin.cons (Fin.cons 1 0) fun i => Fin.cons 0 (U i))

@[simp] theorem extend_zero_zero (U : Matrix (Fin n) (Fin n) ℂ) : extend U 0 0 = 1 := rfl
@[simp] theorem extend_zero_succ (U : Matrix (Fin n) (Fin n) ℂ) (j : Fin n) :
    extend U 0 j.succ = 0 := rfl
@[simp] theorem extend_succ_zero (U : Matrix (Fin n) (Fin n) ℂ) (i : Fin n) :
    extend U i.succ 0 = 0 := rfl
@[simp] theorem extend_succ_succ (U : Matrix (Fin n) (Fin n) ℂ) (i j : Fin n) :
    extend U i.succ j.succ = U i j := rfl

theorem extend_mul (U V : Matrix (Fin n) (Fin n) ℂ) : extend U * extend V = extend (U * V) := by
  ext i j
  refine Fin.cases ?_ (fun i => ?_) i <;> refine Fin.cases ?_ (fun j => ?_) j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_succ]

theorem star_extend (U : Matrix (Fin n) (Fin n) ℂ) : star (extend U) = extend (star U) := by
  ext i j
  refine Fin.cases ?_ (fun i => ?_) i <;> refine Fin.cases ?_ (fun j => ?_) j <;>
    simp [Matrix.star_eq_conjTranspose, conjTranspose_apply]

theorem extend_one : extend (1 : Matrix (Fin n) (Fin n) ℂ) = 1 := by
  ext i j
  refine Fin.cases ?_ (fun i => ?_) i <;> refine Fin.cases ?_ (fun j => ?_) j <;>
    simp [Matrix.one_apply, Fin.succ_ne_zero, (Fin.succ_ne_zero _).symm]

theorem extend_mem_unitary {U : Matrix (Fin n) (Fin n) ℂ} (hU : U ∈ unitaryGroup (Fin n) ℂ) :
    extend U ∈ unitaryGroup (Fin (n + 1)) ℂ := by
  rw [mem_unitaryGroup_iff] at hU ⊢
  rw [star_extend, extend_mul, hU, extend_one]

/-- (diag(1,U))* M diag(1,U) の右下のブロックは U* M' U（M' は M の右下のブロック） -/
theorem conj_extend_succ_succ (U : Matrix (Fin n) (Fin n) ℂ) (M : Matrix (Fin (n + 1)) (Fin (n + 1)) ℂ)
    (i j : Fin n) :
    (star (extend U) * M * extend U) i.succ j.succ =
      (star U * M.submatrix Fin.succ Fin.succ * U) i j := by
  rw [star_extend]
  simp [Matrix.mul_apply, Fin.sum_univ_succ]

/-- M の第1列が (*, 0, …, 0) なら、(diag(1,U))* M diag(1,U) の第1列も (*, 0, …, 0) -/
theorem conj_extend_succ_zero (U : Matrix (Fin n) (Fin n) ℂ) (M : Matrix (Fin (n + 1)) (Fin (n + 1)) ℂ)
    (hM : ∀ k : Fin n, M k.succ 0 = 0) (i : Fin n) :
    (star (extend U) * M * extend U) i.succ 0 = 0 := by
  rw [star_extend]
  simp [Matrix.mul_apply, Fin.sum_univ_succ, hM]

/-- ユニタリ行列 U について、A = U T U* なら U* A U = T -/
theorem conj_of_eq {U A T : Matrix (Fin n) (Fin n) ℂ} (hU : U ∈ unitaryGroup (Fin n) ℂ)
    (h : A = U * T * star U) : star U * A * U = T := by
  have h1 : star U * U = 1 := (mem_unitaryGroup_iff').mp hU
  have h2 : U * star U = 1 := (mem_unitaryGroup_iff).mp hU
  rw [h]
  calc star U * (U * T * star U) * U = (star U * U) * T * (star U * U) := by
        simp only [Matrix.mul_assoc]
    _ = T := by rw [h1, Matrix.one_mul, Matrix.mul_one]

/-- シューア分解：どの複素正方行列も、ユニタリ行列 U と上三角行列 T で A = U T U* と書ける -/
theorem schur : ∀ (n : ℕ) (A : Matrix (Fin n) (Fin n) ℂ),
    ∃ U ∈ unitaryGroup (Fin n) ℂ, ∃ T : Matrix (Fin n) (Fin n) ℂ,
      T.BlockTriangular id ∧ A = U * T * star U
  | 0, A => ⟨1, one_mem _, A, fun i => i.elim0, by simp⟩
  | n + 1, A => by
    obtain ⟨μ, u, hu, hAu⟩ := exists_unit_eigenvector A
    obtain ⟨b, hb⟩ := exists_unitary_first_col u hu
    set W := basisMatrix b
    have hW : W ∈ unitaryGroup (Fin (n + 1)) ℂ := basisMatrix_mem_unitary b
    set B := star W * A * W with hBdef
    have hB0 : ∀ k : Fin n, B k.succ 0 = 0 := fun k =>
      first_col_eq_zero A μ u hAu b hb k.succ (Fin.succ_ne_zero k)
    obtain ⟨U', hU', T', hT', hA'⟩ := schur n (B.submatrix Fin.succ Fin.succ)
    set V := extend U'
    have hV : V ∈ unitaryGroup (Fin (n + 1)) ℂ := extend_mem_unitary hU'
    refine ⟨W * V, Submonoid.mul_mem _ hW hV, star V * B * V, ?_, ?_⟩
    · -- 上三角：j < i なら (V* B V) i j = 0
      intro i j hij
      induction i using Fin.cases with
      | zero => exact absurd hij (Fin.not_lt_zero _)
      | succ i =>
        induction j using Fin.cases with
        | zero => exact conj_extend_succ_zero U' B hB0 i
        | succ j =>
          rw [conj_extend_succ_succ, conj_of_eq hU' hA']
          exact hT' (Fin.succ_lt_succ_iff.mp hij)
    · -- A = (W V)(V* B V)(W V)*
      have hW1 : W * star W = 1 := (mem_unitaryGroup_iff).mp hW
      have hV1 : V * star V = 1 := (mem_unitaryGroup_iff).mp hV
      rw [Matrix.star_mul, hBdef]
      calc A = (W * star W) * A * (W * star W) := by rw [hW1, Matrix.one_mul, Matrix.mul_one]
        _ = W * (V * star V) * (star W * A * W) * (V * star V) * star W := by
            rw [hV1]; simp only [Matrix.mul_one, Matrix.mul_assoc]
        _ = W * V * (star V * (star W * A * W) * V) * (star V * star W) := by
            simp only [Matrix.mul_assoc]

/-! ## 三角化の道：det(e^A) = e^{tr A} -/

section Triangular

variable {m : Type*} [Fintype m] [DecidableEq m] [LinearOrder m]

omit [DecidableEq m] in
/-- 上三角行列の積の対角成分は、対角成分の積 -/
theorem upper_mul_diag {M N : Matrix m m ℂ} (hM : M.BlockTriangular id) (hN : N.BlockTriangular id)
    (i : m) : (M * N) i i = M i i * N i i := by
  rw [Matrix.mul_apply, Finset.sum_eq_single i]
  · intro k _ hki
    rcases lt_or_gt_of_ne hki with h | h
    · rw [hM h, zero_mul]
    · rw [hN h, mul_zero]
  · simp

/-- 上三角行列のべき乗は上三角で、対角成分は T_ii^k -/
theorem upper_pow {T : Matrix m m ℂ} (hT : T.BlockTriangular id) :
    ∀ k : ℕ, (T ^ k).BlockTriangular id ∧ ∀ i, (T ^ k) i i = T i i ^ k
  | 0 => ⟨blockTriangular_one, fun i => by simp⟩
  | k + 1 => by
    obtain ⟨h1, h2⟩ := upper_pow hT k
    refine ⟨by rw [pow_succ]; exact h1.mul hT, fun i => ?_⟩
    rw [pow_succ, upper_mul_diag h1 hT, h2, pow_succ]

open scoped Matrix.Norms.Operator in
/-- 上三角行列の指数関数は上三角で、対角成分は e^{T_ii}（級数を成分ごとに見る） -/
theorem upper_exp {T : Matrix m m ℂ} (hT : T.BlockTriangular id) :
    (NormedSpace.exp T).BlockTriangular id ∧ ∀ i, NormedSpace.exp T i i = Complex.exp (T i i) := by
  have hsum := NormedSpace.exp_series_hasSum_exp' (𝕂 := ℂ) T
  have hentry : ∀ i j, HasSum (fun k : ℕ => ((k.factorial⁻¹ : ℂ) • T ^ k) i j)
      (NormedSpace.exp T i j) := fun i j => Pi.hasSum.mp (Pi.hasSum.mp hsum i) j
  refine ⟨fun i j hij => ?_, fun i => ?_⟩
  · have hzero : (fun k : ℕ => ((k.factorial⁻¹ : ℂ) • T ^ k) i j) = fun _ => 0 := by
      funext k; rw [Matrix.smul_apply, smul_eq_mul]; exact mul_eq_zero_of_right _ ((upper_pow hT k).1 hij)
    have h := hentry i j
    rw [hzero] at h
    exact h.unique hasSum_zero
  · have hdiag : (fun k : ℕ => ((k.factorial⁻¹ : ℂ) • T ^ k) i i) =
        fun k => (k.factorial⁻¹ : ℂ) • T i i ^ k := by
      funext k; rw [Matrix.smul_apply]; exact congrArg _ ((upper_pow hT k).2 i)
    have := hentry i i
    rw [hdiag] at this
    rw [Complex.exp_eq_exp_ℂ]
    exact this.unique (NormedSpace.exp_series_hasSum_exp' (𝕂 := ℂ) (T i i))

end Triangular

/-- 三角化の道による det(e^A) = e^{tr A}：A = U T U*（シューア分解）と、上三角行列の性質から -/
theorem det_exp_via_schur {n : ℕ} (A : Matrix (Fin n) (Fin n) ℂ) :
    (NormedSpace.exp A).det = Complex.exp A.trace := by
  obtain ⟨U, hU, T, hT, rfl⟩ := schur n A
  have hinv : U⁻¹ = star U := Matrix.inv_eq_right_inv ((mem_unitaryGroup_iff).mp hU)
  have hunit : IsUnit U := Unitary.isUnit_coe (U := ⟨U, hU⟩)
  rw [← hinv, Matrix.exp_conj U T hunit, det_conj hunit, trace_conj hunit,
    det_of_upperTriangular (upper_exp hT).1, Matrix.trace, Complex.exp_sum]
  exact Finset.prod_congr rfl fun i _ => (upper_exp hT).2 i

end QuantumStudy.Schur


