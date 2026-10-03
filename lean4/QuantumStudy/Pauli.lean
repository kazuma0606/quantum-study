/-
  パウリ行列と、その基本的な関係式
  対応ノート: 研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md（Part IV・V）

  ノートでは行列の積を手で計算して確かめた関係式を、ここでは Lean が成分ごとに検査する。
-/
import Mathlib.Data.Complex.Basic
import Mathlib.LinearAlgebra.Matrix.Notation

open Matrix

namespace QuantumStudy

/-- パウリ行列 σx -/
def σx : Matrix (Fin 2) (Fin 2) ℂ := !![0, 1; 1, 0]

/-- パウリ行列 σy -/
def σy : Matrix (Fin 2) (Fin 2) ℂ := !![0, -Complex.I; Complex.I, 0]

/-- パウリ行列 σz -/
def σz : Matrix (Fin 2) (Fin 2) ℂ := !![1, 0; 0, -1]

/-- 積：σx σy = i σz -/
theorem σx_mul_σy : σx * σy = Complex.I • σz := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [σx, σy, σz, Matrix.mul_apply, Fin.sum_univ_two]

/-- 積：σy σx = -i σz -/
theorem σy_mul_σx : σy * σx = (-Complex.I) • σz := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [σx, σy, σz, Matrix.mul_apply, Fin.sum_univ_two]

/-- 交換関係：[σx, σy] = σx σy - σy σx = 2i σz -/
theorem comm_σx_σy : σx * σy - σy * σx = (2 * Complex.I) • σz := by
  rw [σx_mul_σy, σy_mul_σx, ← sub_smul]
  congr 1
  ring

/-- σx² = I（σy, σz も同様） -/
theorem σx_sq : σx * σx = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [σx, Matrix.mul_apply, Fin.sum_univ_two]

end QuantumStudy
