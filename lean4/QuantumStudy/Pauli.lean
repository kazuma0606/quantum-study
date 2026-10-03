/-
  パウリ行列と、その基本的な関係式
  対応ノート: 研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md（Part II §6・Part IV・Part V）

  ノートでは行列の積を手で計算して確かめた関係式を、ここでは Lean が成分ごとに検査する。
    ・積の表：σx² = σy² = σz² = I、σxσy = iσz、σyσz = iσx、σzσx = iσy（逆順は −i 倍）
    ・交換関係：[σx, σy] = 2iσz、[σy, σz] = 2iσx、[σz, σx] = 2iσy
    ・反交換関係：{σi, σj} = 0（i ≠ j）
    ・トレース：tr σi = 0、tr(σi σj) = 2δij の対角成分 tr(σi²) = 2
-/
import Mathlib.Data.Complex.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.Trace

open Matrix

namespace QuantumStudy

/-- パウリ行列 σx -/
def σx : Matrix (Fin 2) (Fin 2) ℂ := !![0, 1; 1, 0]

/-- パウリ行列 σy -/
def σy : Matrix (Fin 2) (Fin 2) ℂ := !![0, -Complex.I; Complex.I, 0]

/-- パウリ行列 σz -/
def σz : Matrix (Fin 2) (Fin 2) ℂ := !![1, 0; 0, -1]

/-- 2×2 の行列の等式を、4つの成分ごとに検査する -/
macro "pauli_ext" : tactic =>
  `(tactic| (ext i j; fin_cases i <;> fin_cases j <;>
    simp [σx, σy, σz, Matrix.mul_apply, Fin.sum_univ_two]))

/-! ### 積の表（ノートの Part IV §5） -/

theorem σx_sq : σx * σx = 1 := by pauli_ext
theorem σy_sq : σy * σy = 1 := by pauli_ext
theorem σz_sq : σz * σz = 1 := by pauli_ext

theorem σx_mul_σy : σx * σy = Complex.I • σz := by pauli_ext
theorem σy_mul_σz : σy * σz = Complex.I • σx := by pauli_ext
theorem σz_mul_σx : σz * σx = Complex.I • σy := by pauli_ext

theorem σy_mul_σx : σy * σx = (-Complex.I) • σz := by pauli_ext
theorem σz_mul_σy : σz * σy = (-Complex.I) • σx := by pauli_ext
theorem σx_mul_σz : σx * σz = (-Complex.I) • σy := by pauli_ext

/-! ### 交換関係 [σi, σj] = 2i ε_ijk σk（ノートの Part IV §1〜§3） -/

theorem comm_σx_σy : σx * σy - σy * σx = (2 * Complex.I) • σz := by
  rw [σx_mul_σy, σy_mul_σx, ← sub_smul]; congr 1; ring

theorem comm_σy_σz : σy * σz - σz * σy = (2 * Complex.I) • σx := by
  rw [σy_mul_σz, σz_mul_σy, ← sub_smul]; congr 1; ring

theorem comm_σz_σx : σz * σx - σx * σz = (2 * Complex.I) • σy := by
  rw [σz_mul_σx, σx_mul_σz, ← sub_smul]; congr 1; ring

/-! ### 反交換関係 {σi, σj} = 2δij I（ノートの Part V §1） -/

theorem anticomm_σx_σy : σx * σy + σy * σx = 0 := by
  rw [σx_mul_σy, σy_mul_σx, ← add_smul]; simp

theorem anticomm_σy_σz : σy * σz + σz * σy = 0 := by
  rw [σy_mul_σz, σz_mul_σy, ← add_smul]; simp

theorem anticomm_σz_σx : σz * σx + σx * σz = 0 := by
  rw [σz_mul_σx, σx_mul_σz, ← add_smul]; simp

/-! ### トレース（ノートの Part II §4・§6） -/

theorem trace_σx : σx.trace = 0 := by simp [σx, Matrix.trace, Fin.sum_univ_two]
theorem trace_σy : σy.trace = 0 := by simp [σy, Matrix.trace, Fin.sum_univ_two]
theorem trace_σz : σz.trace = 0 := by simp [σz, Matrix.trace, Fin.sum_univ_two]

/-- tr(σx σy) = 0（直交性 tr(σi σj) = 2δij の一例） -/
theorem trace_σx_mul_σy : (σx * σy).trace = 0 := by rw [σx_mul_σy, trace_smul, trace_σz, smul_zero]

/-- tr(σi²) = 2 -/
theorem trace_σx_sq : (σx * σx).trace = 2 := by
  rw [σx_sq, trace_one]; simp

end QuantumStudy
