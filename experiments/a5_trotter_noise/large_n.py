"""大きな N（〜20 量子ビット）のための、状態ベクトルによる計算。

密度行列（4^N）の代わりに、状態ベクトル（2^N）を使う：
  - 雑音なしのトロッター積：ZZ の項 e^{-iAδ} は対角（各基底状態に位相を掛けるだけ）、横磁場 e^{-iBδ} は
    各量子ビットの回転 e^{-igδX} の積なので、行列を作らずに状態ベクトルに直接作用させる。
  - 正確な時間発展：疎行列のハミルトニアンに scipy の expm_multiply を使う。
  - 雑音：2量子ビットの脱分極（強さ p）は「確率 p で、16 個の2量子ビットのパウリ行列（恒等も含む）の
    どれかを等確率に掛ける」ことと同じ（(1-p)ρ + p (1/16) Σ_P P ρ P = (1-p)ρ + p (I/4) ⊗ Tr ρ）。
    これをランダムに入れた状態ベクトル（軌跡）を多数作り、平均を取る（軌跡法）。

量子ビットの並び：状態ベクトルの添字のビットの、最上位が量子ビット 0（trotter_noise.op_on と同じ、左端が 0）。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import expm_multiply

Vector = NDArray[np.complex128]


def zz_diagonal(N: int, J: float = 1.0) -> NDArray[np.float64]:
    """A = J Σ Z_i Z_{i+1} の対角成分（計算基底での値）。"""
    idx = np.arange(2**N)
    bits = (idx[:, None] >> (N - 1 - np.arange(N))[None, :]) & 1        # bits[:, k] = 量子ビット k の値
    z = 1 - 2 * bits                                                    # Z の固有値 ±1
    return J * np.sum(z[:, :-1] * z[:, 1:], axis=1).astype(float)


def apply_single(psi: Vector, N: int, k: int, U: NDArray) -> Vector:
    """量子ビット k に 2x2 の行列 U を作用させる。"""
    t = psi.reshape([2] * N)
    t = np.moveaxis(np.tensordot(U, t, axes=([1], [k])), 0, k)
    return t.reshape(-1)


def apply_rx_all(psi: Vector, N: int, theta: float) -> Vector:
    """e^{-iθ X} をすべての量子ビットに（= e^{-iθ Σ X_i}）。"""
    U = np.array([[np.cos(theta), -1j * np.sin(theta)], [-1j * np.sin(theta), np.cos(theta)]])
    for k in range(N):
        psi = apply_single(psi, N, k, U)
    return psi


PAULIS = [np.eye(2, dtype=complex), np.array([[0, 1], [1, 0]], dtype=complex),
          np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], dtype=complex)]


def trotter_state(N: int, t: float, order: int, n_steps: int, psi0: Vector, J: float = 1.0, g: float = 1.0,
                  p: float = 0.0, rng: np.random.Generator | None = None) -> Vector:
    """トロッター積 U^n を psi0 に作用させる。p > 0 なら、ZZ の項ごとに CNOT 2個分の雑音を1つの軌跡として入れる。
    雑音を入れる位置：trotter_noise.noisy_step と同じく、各ステップのユニタリの後。"""
    d = t / n_steps
    phase_A = np.exp(-1j * d * zz_diagonal(N, J))
    psi = psi0.copy()
    for _ in range(n_steps):
        if order == 1:
            psi = apply_rx_all(phase_A * psi, N, g * d)
        else:
            psi = apply_rx_all(psi, N, g * d / 2)
            psi = apply_rx_all(phase_A * psi, N, g * d / 2)
        if p > 0:
            for i in range(N - 1):
                for _ in range(2):
                    if rng.random() < p:
                        a, b = rng.integers(4), rng.integers(4)
                        if a:
                            psi = apply_single(psi, N, i, PAULIS[a])
                        if b:
                            psi = apply_single(psi, N, i + 1, PAULIS[b])
    return psi


def tfim_sparse(N: int, J: float = 1.0, g: float = 1.0) -> csr_matrix:
    """H = J Σ Z_i Z_{i+1} + g Σ X_i の疎行列。"""
    dim = 2**N
    H = diags(zz_diagonal(N, J)).tocsr()
    idx = np.arange(dim)
    for k in range(N):
        flipped = idx ^ (1 << (N - 1 - k))
        H = H + csr_matrix((g * np.ones(dim), (idx, flipped)), shape=(dim, dim))
    return H


def exact_state(N: int, t: float, psi0: Vector, J: float = 1.0, g: float = 1.0) -> Vector:
    return expm_multiply(-1j * t * tfim_sparse(N, J, g), psi0)


def z0_expectation(psi: Vector, N: int) -> float:
    probs = np.abs(psi) ** 2
    sign = 1 - 2 * ((np.arange(2**N) >> (N - 1)) & 1)                  # 量子ビット 0 の Z
    return float(np.sum(sign * probs))


@dataclass
class LargeResult:
    n_qubits: int
    t: float
    order: int
    n_steps: int
    p: float
    trajectories: int
    infidelity: float          # 軌跡の平均 1 - |<ψ_exact|ψ_k>|²（雑音なしなら厳密）
    infidelity_sem: float      # その標準誤差
    local_err: float           # |平均 <Z_0> - <Z_0>_exact|
    z_trotter_part: float      # 雑音なしのトロッター積の <Z_0> 誤差（厳密）
    z_noise_part: float        # 雑音による変化（軌跡の平均、統計誤差あり）
    z_sem: float               # 平均 <Z_0> の標準誤差


def run_point_large(N: int, t: float, order: int, n_steps: int, p: float, trajectories: int = 200,
                    seed: int = 0) -> LargeResult:
    psi0 = np.zeros(2**N, dtype=complex)
    psi0[0] = 1
    ex = exact_state(N, t, psi0)
    z_ex = z0_expectation(ex, N)
    clean = trotter_state(N, t, order, n_steps, psi0)
    z_clean = z0_expectation(clean, N)
    if p == 0:
        inf = 1 - abs(np.vdot(ex, clean)) ** 2
        return LargeResult(N, t, order, n_steps, p, 1, inf, 0.0, abs(z_clean - z_ex), z_clean - z_ex, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    infs, zs = [], []
    for _ in range(trajectories):
        psi = trotter_state(N, t, order, n_steps, psi0, p=p, rng=rng)
        infs.append(1 - abs(np.vdot(ex, psi)) ** 2)
        zs.append(z0_expectation(psi, N))
    infs, zs = np.array(infs), np.array(zs)
    z_mean = float(zs.mean())
    return LargeResult(N, t, order, n_steps, p, trajectories, float(infs.mean()),
                       float(infs.std(ddof=1) / np.sqrt(trajectories)), abs(z_mean - z_ex),
                       z_clean - z_ex, z_mean - z_clean, float(zs.std(ddof=1) / np.sqrt(trajectories)))
