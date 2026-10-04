import Mathlib.Analysis.Normed.Ring.Basic
import Mathlib.Analysis.Matrix.Normed
import Mathlib.Analysis.CStarAlgebra.Matrix

/-!
# 望遠鏡和の不等式 ‖Uⁿ − Vⁿ‖ ≤ n‖U − V‖

トロッター分解の誤差解析の要になる不等式。ノルム環の元 `U`, `V` が `‖U‖ ≤ 1`, `‖V‖ ≤ 1` を
満たすとき、

  ‖Uⁿ − Vⁿ‖ ≤ n ‖U − V‖.

`U = e^{A/n} e^{B/n}`、`V = e^{(A+B)/n}` とおくと（`A`, `B` が反エルミートなら両方ともユニタリで
ノルム 1）、

  ‖(e^{A/n} e^{B/n})ⁿ − e^{A+B}‖ ≤ n ‖e^{A/n} e^{B/n} − e^{(A+B)/n}‖

となり、1 ステップの誤差 O(1/n²) が n 倍されて全体の誤差 O(1/n) になる。

対応ノート：研究ノート/04_群論・代数/matrix_exponential_commutator_bch_trotter.md の Part VI §2。
実験：experiments/a5_trotter_noise/。

証明は `U^{n+1} − V^{n+1} = U (Uⁿ − Vⁿ) + (U − V) Vⁿ` による n についての帰納法。
`NormOneClass`（‖1‖ = 1）も完備性も使わない。`‖1‖` が 1 より大きいノルム環でも成り立つように、
`‖Vⁿ‖ ≤ 1` ではなく `‖x Vⁿ‖ ≤ ‖x‖` を補題として使う（n = 0 で `1` のノルムが現れないため）。
-/

namespace QuantumStudy.Telescoping

section NormedRing

variable {R : Type*} [NormedRing R]

/-- `‖V‖ ≤ 1` なら、右から `Vⁿ` を掛けてもノルムは増えない：`‖x Vⁿ‖ ≤ ‖x‖`。
（`‖Vⁿ‖ ≤ 1` とは書かない。`NormOneClass` がないと `‖V⁰‖ = ‖1‖` が 1 を超えうるため。） -/
theorem norm_mul_pow_le_of_norm_le_one {V : R} (hV : ‖V‖ ≤ 1) (x : R) (n : ℕ) :
    ‖x * V ^ n‖ ≤ ‖x‖ := by
  induction n with
  | zero => simp
  | succ n ih =>
    calc ‖x * V ^ (n + 1)‖ = ‖(x * V ^ n) * V‖ := by rw [pow_succ, mul_assoc]
      _ ≤ ‖x * V ^ n‖ * ‖V‖ := norm_mul_le _ _
      _ ≤ ‖x * V ^ n‖ * 1 := by gcongr
      _ = ‖x * V ^ n‖ := mul_one _
      _ ≤ ‖x‖ := ih

/-- `‖U‖ ≤ 1` なら、左から `U` を掛けてもノルムは増えない：`‖U x‖ ≤ ‖x‖`。 -/
theorem norm_mul_le_of_norm_le_one {U : R} (hU : ‖U‖ ≤ 1) (x : R) : ‖U * x‖ ≤ ‖x‖ :=
  calc ‖U * x‖ ≤ ‖U‖ * ‖x‖ := norm_mul_le _ _
    _ ≤ 1 * ‖x‖ := by gcongr
    _ = ‖x‖ := one_mul _

/-- 帰納法の1ステップで使う恒等式：`U^{n+1} − V^{n+1} = U (Uⁿ − Vⁿ) + (U − V) Vⁿ`。
（非可換環で成り立つ。） -/
theorem pow_succ_sub_pow_succ (U V : R) (n : ℕ) :
    U ^ (n + 1) - V ^ (n + 1) = U * (U ^ n - V ^ n) + (U - V) * V ^ n := by
  rw [pow_succ', pow_succ', mul_sub, sub_mul]
  abel

/-- **望遠鏡和の不等式**。ノルム環の元 `U`, `V` が `‖U‖ ≤ 1`, `‖V‖ ≤ 1` を満たすとき、
すべての自然数 `n` について `‖Uⁿ − Vⁿ‖ ≤ n ‖U − V‖`。

トロッター分解の誤差
`‖(e^{A/n} e^{B/n})ⁿ − e^{A+B}‖ ≤ n ‖e^{A/n} e^{B/n} − e^{(A+B)/n}‖`
を導くのに使う補題（`U = e^{A/n} e^{B/n}`、`V = e^{(A+B)/n}`、`Vⁿ = e^{A+B}`）。
`NormOneClass` も完備性も仮定しない。 -/
theorem norm_pow_sub_pow_le_mul {U V : R} (hU : ‖U‖ ≤ 1) (hV : ‖V‖ ≤ 1) (n : ℕ) :
    ‖U ^ n - V ^ n‖ ≤ n * ‖U - V‖ := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ_sub_pow_succ]
    calc ‖U * (U ^ n - V ^ n) + (U - V) * V ^ n‖
        ≤ ‖U * (U ^ n - V ^ n)‖ + ‖(U - V) * V ^ n‖ := norm_add_le _ _
      _ ≤ ‖U ^ n - V ^ n‖ + ‖U - V‖ :=
          add_le_add (norm_mul_le_of_norm_le_one hU _)
            (norm_mul_pow_le_of_norm_le_one hV _ _)
      _ ≤ n * ‖U - V‖ + ‖U - V‖ := by gcongr
      _ = ((n + 1 : ℕ) : ℝ) * ‖U - V‖ := by push_cast; ring

end NormedRing

/-! ## 系：行列の場合

行列 `Matrix ι ι 𝕜` には Mathlib で既定のノルムが入っていない（入れ方が何通りもあるため）。
ノルム環の構造を局所的に入れれば、上の定理がそのまま使える。 -/

section MatrixLinfty

attribute [local instance] Matrix.linftyOpNormedRing

/-- 行列（ℓ∞ 作用素ノルム = 行ごとの絶対値和の最大値）での望遠鏡和の不等式。 -/
theorem matrix_linftyOp_norm_pow_sub_pow_le_mul {ι : Type*} [Fintype ι] [DecidableEq ι]
    {U V : Matrix ι ι ℂ} (hU : ‖U‖ ≤ 1) (hV : ‖V‖ ≤ 1) (n : ℕ) :
    ‖U ^ n - V ^ n‖ ≤ n * ‖U - V‖ :=
  norm_pow_sub_pow_le_mul hU hV n

end MatrixLinfty

section MatrixL2

open scoped Matrix.Norms.L2Operator

/-- 行列（ℓ² 作用素ノルム = スペクトルノルム、ユニタリ行列のノルムは 1）での望遠鏡和の不等式。
量子回路のトロッター誤差で普通に使うのはこのノルム。 -/
theorem matrix_l2Op_norm_pow_sub_pow_le_mul {ι : Type*} [Fintype ι] [DecidableEq ι]
    {U V : Matrix ι ι ℂ} (hU : ‖U‖ ≤ 1) (hV : ‖V‖ ≤ 1) (n : ℕ) :
    ‖U ^ n - V ^ n‖ ≤ n * ‖U - V‖ :=
  norm_pow_sub_pow_le_mul hU hV n

end MatrixL2

end QuantumStudy.Telescoping
