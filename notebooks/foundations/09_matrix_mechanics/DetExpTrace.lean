-- det(e^A) = e^(tr A) の形式証明
-- 対応ノート: 研究ノート/det_exp_trace_proof.md
--
-- Lean4 + Mathlib では Matrix.exp（行列指数関数）が定義されており、
-- この定理は Mathlib に既に収録されている。
-- ここでは「どう書けるか」「何が使われているか」を示す。
--
-- 実行には Mathlib が必要:
--   lake update
--   lake build

import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Analysis.NormedSpace.MatrixExponential
import Mathlib.Topology.Algebra.Module.FiniteDimension

open Matrix Complex

variable {n : Type*} [Fintype n] [DecidableEq n]

-- ============================================================
-- Mathlib に収録されている定理の確認
-- ============================================================

-- Matrix.det_exp_of_mem_skewAdjointMatricesLie や
-- より一般に次が使える：
--
-- theorem Matrix.exp_det {𝕜 : Type*} [RCLike 𝕜]
--     (A : Matrix n n 𝕜) :
--     det (exp 𝕜 A) = exp (trace A) :=
--   ...  ← Mathlib が証明を持っている

-- ============================================================
-- 証明1の骨格（対角化を使う場合）を手で書くと
-- ============================================================

-- 補題1: 対角行列の行列指数は成分ごとの指数
-- Matrix.exp_diagonal が Mathlib にある:
--   exp 𝕜 (diagonal d) = diagonal (fun i => exp (d i))

-- 補題2: 行列式の乗法性
-- Matrix.det_mul が Mathlib にある:
--   det (A * B) = det A * det B

-- 補題3: トレースの相似不変性
-- Matrix.trace_similarMatrix または巡回性 trace_mul_comm:
--   trace (A * B) = trace (B * A)

-- ============================================================
-- 小さな例：2×2 具体行列で数値確認
-- ============================================================

-- Lean4 では #eval で具体的な計算ができる
-- （行列指数の数値計算は浮動小数点ではなく有理数・整数の範囲で）

-- 例：単位行列 I_2 → e^I の行列式
#check @Matrix.exp_identity   -- exp I = e * I ではなく exp(1) * I

-- ============================================================
-- 証明のスケッチ（Mathlib の補題を組み合わせる）
-- ============================================================

/-- det(e^A) = e^(tr A) （対角化できる場合のスケッチ） -/
theorem det_exp_eq_exp_trace_sketch
    (A : Matrix (Fin 2) (Fin 2) ℂ)
    -- 対角化可能性の仮定（Mathlibでは IsAlgClosed を使う）
    : det (exp ℂ A) = Complex.exp (trace A) := by
  -- Mathlib の定理をそのまま呼べる
  exact Matrix.det_exp_of_mem_unitary _ (by sorry) -- 実際はもう少し条件が必要
  -- 完全な証明は Mathlib の exp_det を参照

-- ============================================================
-- 参考：Pauli 行列のトレースゼロ → det(e^σ) = 1
-- ============================================================

/-- Pauli σz のトレースはゼロ -/
lemma trace_pauli_sz : trace !![( 1 : ℂ), 0; 0, -1] = 0 := by
  simp [Matrix.trace, Fin.sum_univ_two]

/-- トレースゼロなら det(e^A) = 1 -/
-- これが「SU(2) の生成子はトレースゼロでなければならない」の根拠
example (A : Matrix (Fin 2) (Fin 2) ℂ) (h : trace A = 0) :
    det (exp ℂ A) = 1 := by
  -- Matrix.det_exp + h を組み合わせる
  rw [Matrix.det_exp_of_mem_unitary] -- Mathlib の定理
  simp [h]
  sorry -- 完全な証明は Mathlib に委ねる

-- ============================================================
-- Python との比較まとめ
-- ============================================================
--
-- Python (SymPy)               │ Lean4 (Mathlib)
-- ─────────────────────────────┼────────────────────────────
-- A.exp()                      │ Matrix.exp ℂ A
-- det(A.exp())                 │ Matrix.det (Matrix.exp ℂ A)
-- simplify(lhs - rhs) == 0     │ rfl / ring / simp
-- 数値的に「確かめる」          │ 形式的に「証明する」
-- 特定の行列で検証              │ ∀ A : Matrix n n ℂ で成立
--
-- Lean4 の強みは「全ての行列に対して成り立つ」を
-- 型として表現し、コンパイラが検証すること。
