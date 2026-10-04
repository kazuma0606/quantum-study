"""テーマ A-5：トロッター誤差と雑音の綱引き ― 計算の本体。

N スピンの横磁場イジング模型（開いた鎖）
    H = A + B,   A = J Σ_i Z_i Z_{i+1}（交換する項の和）,   B = g Σ_i X_i（交換する項の和）
の時間発展 e^{-iHt} を、トロッター分解（1次）とストラング分解（2次）で近似し、
各ステップの CNOT（ZZ の項1つにつき2個）の後に2量子ビットの脱分極雑音（強さ p）を入れて、
誤差がどう変わるかを密度行列で正確に計算する。

  1次（Lie）    : U_1(δ) = e^{-iBδ} e^{-iAδ}                 （A を先に作用）
  2次（Strang） : U_2(δ) = e^{-iBδ/2} e^{-iAδ} e^{-iBδ/2}     （外側が B、真ん中が A）
  δ = t/n。どちらも1ステップに ZZ の項を1回ずつ使うので、CNOT の数は同じ 2(N-1) 個/ステップ。

誤差の上限（反エルミート版 A,B に対して知られているもの。tests/ で反例を探す）
  1次：‖U_1(δ) - e^{-iHδ}‖ ≤ δ²/2 ‖[A,B]‖
  2次：‖U_2(δ) - e^{-iHδ}‖ ≤ δ³ ( ‖[M,[M,O]]‖/12 + ‖[O,[O,M]]‖/24 )   （O = 外側の B、M = 真ん中の A）
  n ステップでは、望遠鏡和 ‖U^n - V^n‖ ≤ n‖U - V‖（‖U‖,‖V‖ ≤ 1）から n 倍。
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm

Matrix = NDArray[np.complex128]

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


# ------------------------------------------------------------------------------ 演算子
def op_on(single: Matrix, site: int, n_qubits: int) -> Matrix:
    """site 番目（0 始まり、左端が 0）の量子ビットに single を、他に I を置いたテンソル積。"""
    return reduce(np.kron, [single if k == site else I2 for k in range(n_qubits)])


def tfim_parts(n_qubits: int, J: float = 1.0, g: float = 1.0) -> tuple[Matrix, Matrix]:
    """横磁場イジング模型の A = J Σ Z_i Z_{i+1}、B = g Σ X_i。"""
    dim = 2**n_qubits
    A = np.zeros((dim, dim), dtype=complex)
    for i in range(n_qubits - 1):
        A += J * op_on(Z, i, n_qubits) @ op_on(Z, i + 1, n_qubits)
    B = sum(g * op_on(X, i, n_qubits) for i in range(n_qubits))
    return A, np.asarray(B, dtype=complex)


def comm(P: Matrix, Q: Matrix) -> Matrix:
    return P @ Q - Q @ P


def opnorm(M: Matrix) -> float:
    """作用素ノルム（最大特異値）。"""
    return float(np.linalg.norm(M, 2))


# ------------------------------------------------------------------------------ トロッター
def step_unitary(A: Matrix, B: Matrix, dt: float, order: int) -> Matrix:
    if order == 1:
        return expm(-1j * B * dt) @ expm(-1j * A * dt)
    if order == 2:
        half = expm(-1j * B * dt / 2)
        return half @ expm(-1j * A * dt) @ half
    raise ValueError("order は 1 か 2")


def trotter_bound(A: Matrix, B: Matrix, t: float, n: int, order: int) -> float:
    """n ステップの誤差の上限（モジュールの docstring の式）。"""
    dt = t / n
    if order == 1:
        return n * dt**2 / 2 * opnorm(comm(A, B))
    O, M = B, A
    return n * dt**3 * (opnorm(comm(M, comm(M, O))) / 12 + opnorm(comm(O, comm(O, M))) / 24)


# ------------------------------------------------------------------------------ 雑音
def depolarize_pair(rho: Matrix, i: int, j: int, p: float, n_qubits: int) -> Matrix:
    """量子ビット i, j に2量子ビットの脱分極雑音：ρ → (1-p) ρ + p (I/4)_{ij} ⊗ Tr_{ij} ρ。"""
    if p == 0:
        return rho
    n = n_qubits
    rest = [k for k in range(n) if k not in (i, j)]
    perm = rest + [i, j] + [n + k for k in rest] + [n + i, n + j]     # i, j をケット側・ブラ側とも末尾へ
    d_rest = 2 ** (n - 2)
    t = np.transpose(rho.reshape([2] * (2 * n)), perm).reshape(d_rest, 4, d_rest, 4)
    reduced = np.einsum("aibi->ab", t)                                 # Tr_{ij}
    mixed = np.einsum("ab,ij->aibj", reduced, np.eye(4) / 4)           # (Tr_{ij} ρ) ⊗ I/4
    inv = np.argsort(perm)
    mixed = np.transpose(mixed.reshape([2] * (2 * n)), inv).reshape(rho.shape)
    return (1 - p) * rho + p * mixed


def noisy_step(rho: Matrix, U: Matrix, p: float, n_qubits: int) -> Matrix:
    """1ステップ：ユニタリ U を作用させ、ZZ の項ごとに CNOT 2個分の雑音を入れる。"""
    rho = U @ rho @ U.conj().T
    for i in range(n_qubits - 1):
        for _ in range(2):                                             # ZZ の項1つに CNOT 2個
            rho = depolarize_pair(rho, i, i + 1, p, n_qubits)
    return rho


# ------------------------------------------------------------------------------ 実験の1点
@dataclass
class Result:
    n_qubits: int
    t: float
    J: float
    g: float
    order: int
    n_steps: int
    p: float
    cnots: int
    infidelity: float          # 1 - <ψ_exact|ρ|ψ_exact>（状態全体）
    local_err: float           # |<Z_0>_ρ - <Z_0>_exact|（局所的な量）
    trotter_err: float         # 雑音なしの ‖U^n - e^{-iHt}‖
    bound: float               # trotter_bound
    z_exact: float = 0.0       # <Z_0>（正確な時間発展）
    z_trotter_part: float = 0.0  # <Z_0>（雑音なしのトロッター積）- z_exact（符号つき）
    z_noise_part: float = 0.0    # <Z_0>（雑音あり）- <Z_0>（雑音なし）（符号つき）
    # local_err = |z_trotter_part + z_noise_part|。2つの符号が逆だと打ち消し合う


def run_point(n_qubits: int, t: float, order: int, n_steps: int, p: float,
              J: float = 1.0, g: float = 1.0) -> Result:
    A, B = tfim_parts(n_qubits, J, g)
    dim = 2**n_qubits
    psi0 = np.zeros(dim, dtype=complex)
    psi0[0] = 1.0                                                      # |00…0>
    U_exact = expm(-1j * (A + B) * t)
    psi_exact = U_exact @ psi0
    Z0 = op_on(Z, 0, n_qubits)
    z_exact = float(np.real(psi_exact.conj() @ Z0 @ psi_exact))

    U = step_unitary(A, B, t / n_steps, order)
    rho = np.outer(psi0, psi0.conj())
    for _ in range(n_steps):
        rho = noisy_step(rho, U, p, n_qubits)
    fid = float(np.real(psi_exact.conj() @ rho @ psi_exact))
    z = float(np.real(np.trace(Z0 @ rho)))
    U_n = np.linalg.matrix_power(U, n_steps)
    psi_clean = U_n @ psi0
    z_clean = float(np.real(psi_clean.conj() @ Z0 @ psi_clean))
    trotter_err = opnorm(U_n - U_exact)
    return Result(n_qubits, t, J, g, order, n_steps, p, 2 * (n_qubits - 1) * n_steps,
                  1 - fid, abs(z - z_exact), trotter_err, trotter_bound(A, B, t, n_steps, order),
                  z_exact, z_clean - z_exact, z - z_clean)


# ------------------------------------------------------------------------------ 1次の誤差の係数
def first_order_coefficient(A: Matrix, B: Matrix, psi0: Matrix, O: Matrix, t: float) -> float:
    """1次の分解 U_1(δ)^n（δ = t/n）で測った <O> の誤差の、δ について1次の係数 c_1：
        <O>_{U_1^n} - <O>_exact = c_1 δ + O(δ²)
        c_1 = -(i/2) ( <ψ(t)|[A, O]|ψ(t)> - <ψ_0|[A, O(t)]|ψ_0> ),   O(t) = e^{iHt} O e^{-iHt}
    導出：U_1^n = e^{-iBδ/2} U_2^n e^{iBδ/2}（U_2 はストラング分解で、誤差は O(δ²)）。両端の e^{±iBδ/2} を
    δ の1次まで展開し、B(t) - B = -(A(t) - A)（H = A + B は保存）を使う。
    O が A と交換すれば第1項が、ψ_0 が A の固有状態なら第2項が消える（両方満たせば c_1 = 0。Layden の条件）。"""
    U = expm(-1j * (A + B) * t)
    psit = U @ psi0
    Ot = U.conj().T @ O @ U
    term_end = psit.conj() @ (A @ O - O @ A) @ psit
    term_start = psi0.conj() @ (A @ Ot - Ot @ A) @ psi0
    return float(np.real(-0.5j * (term_end - term_start)))
