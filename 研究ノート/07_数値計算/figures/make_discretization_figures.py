"""vandermonde_finite_difference_spectral.md（ヴァンデルモンド行列と、差分法・スペクトル法）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/07_数値計算/figures/make_discretization_figures.py          # すべて
    uv run python 研究ノート/07_数値計算/figures/make_discretization_figures.py dz02     # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    dz01_vandermonde_runge.png        Part I   ヴァンデルモンド行列の条件数と、ルンゲ現象（等間隔の点 vs チェビシェフ点）
    dz02_fd_vs_spectral.png           Part II  調和振動子の固有値：差分法（誤差 ∝ h²）と、フーリエ・スペクトル法（指数関数的）
    dz03_crank_nicolson.png           Part III 時間発展：前進オイラー法はノルムが増え、クランク・ニコルソン法は保存する
    dz04_slater_vandermonde.png       Part IV  2つのフェルミ粒子の波動関数（ヴァンデルモンド行列式）と、ボース粒子との比較

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from math import factorial
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import hermite as Hm
from scipy.interpolate import BarycentricInterpolator

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"


def cheb_points(n: int) -> np.ndarray:
    """チェビシェフ点 x_k = cos((2k+1)π/(2n))（k = 0, …, n−1）。"""
    k = np.arange(n)
    return np.cos((2 * k + 1) * np.pi / (2 * n))


# ------------------------------------------------------------------------------------- dz01
def dz01():
    # ヴァンデルモンド行列式 = Π_{i<j}(x_j − x_i)（式 (I-3)）
    xs = np.array([0.3, -1.2, 2.0, 0.7])
    V = np.vander(xs, increasing=True)
    prod = np.prod([xs[j] - xs[i] for i in range(4) for j in range(i + 1, 4)])
    assert np.isclose(np.linalg.det(V), prod)

    ns = np.arange(2, 31)
    cond_eq = [np.linalg.cond(np.vander(np.linspace(-1, 1, n), increasing=True)) for n in ns]
    cond_ch = [np.linalg.cond(np.vander(cheb_points(n), increasing=True)) for n in ns]
    cond_tt = [np.linalg.cond(np.polynomial.chebyshev.chebvander(cheb_points(n), n - 1)) for n in ns]
    assert cond_eq[-1] > 1e11 and cond_tt[-1] < 2                   # 等間隔・単項式は悪条件、チェビシェフは √2 程度

    f = lambda x: 1 / (1 + 25 * x**2)
    n = 21
    xx = np.linspace(-1, 1, 2001)
    p_eq = BarycentricInterpolator(np.linspace(-1, 1, n), f(np.linspace(-1, 1, n)))(xx)
    p_ch = BarycentricInterpolator(cheb_points(n), f(cheb_points(n)))(xx)
    err_eq, err_ch = np.max(np.abs(p_eq - f(xx))), np.max(np.abs(p_ch - f(xx)))
    assert err_eq > 10 and err_ch < 0.05

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
    ax = axes[0]
    ax.semilogy(ns, cond_eq, "o-", color=C_BAD, ms=3, label="単項式 $x^k$、等間隔の点")
    ax.semilogy(ns, cond_ch, "s-", color=C_B, ms=3, label="単項式 $x^k$、チェビシェフ点")
    ax.semilogy(ns, cond_tt, "^-", color=C_A, ms=3, label="チェビシェフ多項式 $T_k(x)$、チェビシェフ点")
    ax.set_xlabel("点の数 $n$（多項式の次数 $n-1$）")
    ax.set_ylabel("条件数")
    ax.set_title("(a) 「基底を点で評価した行列」の条件数", fontsize=11)
    ax.legend(fontsize=9)
    ax = axes[1]
    ax.plot(xx, f(xx), color="#aaa", lw=4, label="$f(x)=1/(1+25x^2)$")
    ax.plot(xx, p_eq, color=C_BAD, lw=1.5, label=f"等間隔の {n} 点で補間（最大誤差 {err_eq:.0f}）")
    ax.plot(xx, p_ch, color=C_A, lw=1.5, label=f"チェビシェフ点の {n} 点で補間（最大誤差 {err_ch:.3f}）")
    ax.plot(np.linspace(-1, 1, n), f(np.linspace(-1, 1, n)), "o", color=C_BAD, ms=3)
    ax.set_ylim(-1.5, 2.0)
    ax.set_title("(b) ルンゲ現象：等間隔の点で高い次数の補間をすると、端で暴れる", fontsize=11)
    ax.legend(fontsize=8.5, loc="upper center")
    fig.tight_layout()
    fig.savefig(OUT / "dz01_vandermonde_runge.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- dz02
def fd_hamiltonian(N: int, L: float) -> tuple[np.ndarray, np.ndarray, float]:
    """−½ d²/dx² + ½x² を、[−L/2, L/2] の内部 N 点の差分で（両端で ψ = 0）。"""
    h = L / (N + 1)
    x = -L / 2 + h * np.arange(1, N + 1)
    main = 1 / h**2 + 0.5 * x**2
    off = -0.5 / h**2 * np.ones(N - 1)
    return np.diag(main) + np.diag(off, 1) + np.diag(off, -1), x, h


def fourier_hamiltonian(N: int, L: float) -> tuple[np.ndarray, np.ndarray]:
    """−½ d²/dx² + ½x² を、周期 L の N 点フーリエ・スペクトル法で（微分は FFT で ik を掛ける）。"""
    x = -L / 2 + L * np.arange(N) / N
    k = 2 * np.pi * np.fft.fftfreq(N, d=L / N)
    T = np.real(np.fft.ifft(np.diag(0.5 * k**2) @ np.fft.fft(np.eye(N), axis=0), axis=0))
    return T + np.diag(0.5 * x**2), x


def dz02():
    L = 20.0
    exact = np.arange(6) + 0.5
    Ns_fd = np.array([20, 40, 80, 160, 320, 640])
    Ns_sp = np.array([10, 16, 24, 32, 40, 48, 56, 64])
    err_fd = np.array([np.abs(np.linalg.eigvalsh(fd_hamiltonian(N, L)[0])[[0, 5]] - exact[[0, 5]]) for N in Ns_fd])
    err_sp = np.array([np.abs(np.linalg.eigvalsh(fourier_hamiltonian(N, L)[0])[[0, 5]] - exact[[0, 5]]) for N in Ns_sp])
    slope = np.polyfit(np.log(Ns_fd[2:]), np.log(err_fd[2:, 0]), 1)[0]
    assert abs(slope + 2) < 0.1                                        # 差分法：誤差 ∝ h² ∝ N^{−2}
    assert err_sp[-1, 0] < 1e-12 and err_sp[-1, 1] < 1e-10            # スペクトル法：64点で丸め誤差の水準
    # 差分法の行列は三重対角、スペクトル法の行列は密
    H_fd, _, _ = fd_hamiltonian(40, L)
    H_sp, _ = fourier_hamiltonian(40, L)
    assert np.count_nonzero(np.abs(H_fd) > 1e-14) == 40 + 2 * 39
    assert np.count_nonzero(np.abs(H_sp) > 1e-14) > 0.9 * 40 * 40

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    ax = axes[0]
    ax.spy(np.abs(H_fd) > 1e-14, markersize=2, color=C_B)
    ax.set_title("(a) 差分法の行列（40点）：三重対角", fontsize=11)
    ax = axes[1]
    ax.spy(np.abs(H_sp) > 1e-14, markersize=2, color=C_A)
    ax.set_title("(b) スペクトル法の行列（40点）：密", fontsize=11)
    ax = axes[2]
    ax.loglog(Ns_fd, err_fd[:, 0], "o-", color=C_B, label=f"差分法、基底状態（傾き {slope:.2f}）")
    ax.loglog(Ns_fd, err_fd[:, 1], "o--", color=C_B, alpha=0.6, label="差分法、第5励起状態")
    ax.loglog(Ns_sp, np.maximum(err_sp[:, 0], 1e-16), "s-", color=C_A, label="スペクトル法、基底状態")
    ax.loglog(Ns_sp, np.maximum(err_sp[:, 1], 1e-16), "s--", color=C_A, alpha=0.6, label="スペクトル法、第5励起状態")
    ax.set_xlabel("点の数 $N$")
    ax.set_ylabel("固有値の誤差 $|E-E_{\\mathrm{exact}}|$")
    ax.set_title("(c) 調和振動子の固有値 $n+\\frac{1}{2}$ の誤差", fontsize=11)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "dz02_fd_vs_spectral.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- dz03
def thomas(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    """三重対角の連立方程式（下 a、対角 b、上 c）をトーマス法で解く（式 (III-4)・(III-5)）。"""
    n = len(b)
    cp = np.zeros(n - 1, dtype=complex)
    dp = np.zeros(n, dtype=complex)
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        denom = b[i] - a[i - 1] * cp[i - 1]
        if i < n - 1:
            cp[i] = c[i] / denom
        dp[i] = (d[i] - a[i - 1] * dp[i - 1]) / denom
    x = np.zeros(n, dtype=complex)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def dz03():
    L, N = 20.0, 400
    H, x, h = fd_hamiltonian(N, L)
    dt, T = 0.01, 2 * np.pi
    steps = int(round(T / dt))
    x0 = 2.0
    psi0 = np.pi ** (-0.25) * np.exp(-(x - x0) ** 2 / 2) * np.sqrt(h)   # 格子上で Σ|ψ|² = 1
    psi0 /= np.linalg.norm(psi0)
    # トーマス法の確認
    A = np.eye(N) + 0.5j * dt * H
    rhs = (np.eye(N) - 0.5j * dt * H) @ psi0
    sol = thomas(np.diag(A, -1), np.diag(A), np.diag(A, 1), rhs)
    assert np.allclose(sol, np.linalg.solve(A, rhs))
    # クランク・ニコルソン法のステップ行列はユニタリ
    U = np.linalg.solve(A, np.eye(N) - 0.5j * dt * H)
    assert np.allclose(U.conj().T @ U, np.eye(N), atol=1e-10)

    a_, b_, c_ = np.diag(A, -1), np.diag(A), np.diag(A, 1)
    psi_cn, psi_eu = psi0.astype(complex), psi0.astype(complex)
    ts, norm_cn, norm_eu, mean_x = [0.0], [1.0], [1.0], [x0]
    for s in range(1, steps + 1):
        psi_cn = thomas(a_, b_, c_, psi_cn - 0.5j * dt * (H @ psi_cn))
        if norm_eu[-1] < 1e50:                                       # あふれる前に止める
            psi_eu = psi_eu - 1j * dt * (H @ psi_eu)
        ts.append(s * dt)
        norm_cn.append(np.linalg.norm(psi_cn))
        norm_eu.append(np.linalg.norm(psi_eu) if norm_eu[-1] < 1e50 else np.nan)
        mean_x.append(np.real(np.sum(x * np.abs(psi_cn) ** 2)))
    ts, norm_cn, norm_eu, mean_x = map(np.array, (ts, norm_cn, norm_eu, mean_x))
    assert np.max(np.abs(norm_cn - 1)) < 1e-10                       # ノルムは保存
    assert np.nanmax(norm_eu) > 1e10                                 # 前進オイラー法は発散
    assert np.max(np.abs(mean_x - x0 * np.cos(ts))) < 0.02          # ⟨x⟩ = x0 cos t（ずれは Δt² の位相誤差で約 0.012）

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.5))
    ax = axes[0]
    ax.semilogy(ts, norm_eu, color=C_BAD, lw=2, label="前進オイラー法 $\\psi^{n+1}=(I-iH\\Delta t)\\psi^n$")
    ax.semilogy(ts, norm_cn, color=C_A, lw=2, label="クランク・ニコルソン法")
    ax.set_xlabel("$t$")
    ax.set_ylabel("ノルム $\\|\\psi\\|$")
    ax.set_title("(a) ノルム（確率の合計）：オイラー法は爆発、CN 法は 1 のまま", fontsize=11)
    ax.legend(fontsize=9)
    ax = axes[1]
    ax.plot(ts, mean_x, color=C_A, lw=2.5, label="クランク・ニコルソン法の $\\langle x\\rangle$")
    ax.plot(ts, x0 * np.cos(ts), "k--", lw=1.2, label="$x_0\\cos t$（古典的な振動）")
    ax.set_xlabel("$t$")
    ax.set_title("(b) 調和振動子の中の波束の位置の期待値", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "dz03_crank_nicolson.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- dz04
def hermite_function(n: int, x: np.ndarray) -> np.ndarray:
    c = np.zeros(n + 1)
    c[n] = 1
    return Hm.hermval(x, c) * np.exp(-x**2 / 2) / np.sqrt(2.0**n * factorial(n) * np.sqrt(np.pi))


def dz04():
    # det[H_j(x_i)] = (Π_j 2^j) Π_{i<j}(x_j − x_i)（式 (IV-3)）
    rng = np.random.default_rng(1)
    xs = rng.normal(size=4)
    M = np.array([[Hm.hermval(xi, np.eye(4)[j]) for j in range(4)] for xi in xs])
    vander = np.prod([xs[j] - xs[i] for i in range(4) for j in range(i + 1, 4)])
    assert np.isclose(np.linalg.det(M), 2 ** (0 + 1 + 2 + 3) * vander)

    g = np.linspace(-3, 3, 241)
    X1, X2 = np.meshgrid(g, g, indexing="ij")
    p0, p1 = hermite_function(0, g), hermite_function(1, g)
    psi_f = (np.outer(p0, p1) - np.outer(p1, p0)) / np.sqrt(2)
    psi_b = (np.outer(p0, p1) + np.outer(p1, p0)) / np.sqrt(2)
    # フェルミ粒子：Ψ ∝ (x2 − x1) e^{−(x1²+x2²)/2}
    ref = (X2 - X1) * np.exp(-(X1**2 + X2**2) / 2) / np.sqrt(np.pi)
    assert np.allclose(psi_f, ref, atol=1e-12)
    assert np.allclose(np.diag(psi_f), 0)                            # x1 = x2 で 0（パウリの排他原理）
    dA = (g[1] - g[0]) ** 2
    assert abs(np.sum(psi_f**2) * dA - 1) < 1e-3 and abs(np.sum(psi_b**2) * dA - 1) < 1e-3

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, psi, title in ((axes[0], psi_f, "(a) フェルミ粒子：$\\Psi\\propto(x_2-x_1)e^{-(x_1^2+x_2^2)/2}$"),
                           (axes[1], psi_b, "(b) ボース粒子：$\\phi_0\\phi_1$ を対称化")):
        im = ax.imshow(psi.T**2, origin="lower", extent=[-3, 3, -3, 3], cmap="viridis")
        ax.plot([-3, 3], [-3, 3], color="w", ls="--", lw=1)
        ax.set_xlabel("$x_1$")
        ax.set_ylabel("$x_2$")
        ax.set_title(title, fontsize=10.5)
        fig.colorbar(im, ax=ax, shrink=0.85, label="$|\\Psi(x_1,x_2)|^2$")
    fig.tight_layout()
    fig.savefig(OUT / "dz04_slater_vandermonde.png", dpi=150)
    plt.close(fig)


FIGS = {"dz01": dz01, "dz02": dz02, "dz03": dz03, "dz04": dz04}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGS:
        FIGS[name]()
        print("保存:", name)
