"""generalized_pauli_and_sun_generators.md（一般化パウリ行列と SU(n) の生成子）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/04_群論・代数/figures/make_generalized_pauli_figures.py

出力（このスクリプトと同じ figures/ ディレクトリ）:
    gp01_qudit_and_gellmann.png   一般化パウリ行列 X, Z（n=3）、X^aZ^b の直交性、Gell-Mann 行列 λ1〜λ8

描く前に、ノートの主張（ZX = ωXZ、X^aZ^b の直交性と積の公式、Gell-Mann 行列の性質と構造定数 f_abc）を assert で確認する。
"""

import itertools
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY = "#1f77b4", "#e67e00", "#d62728", "#888888"


def shift_phase(n):
    """巡回シフト X|j⟩ = |j+1 mod n⟩ と、位相 Z|j⟩ = ω^j |j⟩"""
    w = np.exp(2j * np.pi / n)
    X = np.zeros((n, n), complex)
    for j in range(n):
        X[(j + 1) % n, j] = 1
    Z = np.diag([w**j for j in range(n)])
    return X, Z, w


def gell_mann():
    s3 = 1 / np.sqrt(3)
    L = np.zeros((8, 3, 3), complex)
    L[0][0, 1] = L[0][1, 0] = 1
    L[1][0, 1], L[1][1, 0] = -1j, 1j
    L[2][0, 0], L[2][1, 1] = 1, -1
    L[3][0, 2] = L[3][2, 0] = 1
    L[4][0, 2], L[4][2, 0] = -1j, 1j
    L[5][1, 2] = L[5][2, 1] = 1
    L[6][1, 2], L[6][2, 1] = -1j, 1j
    L[7] = s3 * np.diag([1, 1, -2])
    return L


def check_claims():
    mp = np.linalg.matrix_power
    for n in (2, 3, 4, 5):
        X, Z, w = shift_phase(n)
        assert np.allclose(Z @ X, w * X @ Z)                                               # ZX = ωXZ
        assert np.allclose(X.conj().T @ X, np.eye(n)) and np.allclose(Z.conj().T @ Z, np.eye(n))   # ユニタリ
        if n > 2:
            assert not np.allclose(X, X.conj().T) and not np.allclose(Z, Z.conj().T)       # n > 2 ではエルミートでない
            assert np.allclose(X.conj().T, mp(X, n - 1))                                   # X† = X^{n-1}
        P = {(a, b): mp(X, a) @ mp(Z, b) for a in range(n) for b in range(n)}
        for (a, b), A in P.items():
            for (c, d), B in P.items():
                assert np.isclose(np.trace(A.conj().T @ B), n * (a == c) * (b == d))        # 直交性
                assert np.allclose(A @ B, w ** (b * c) * mp(X, (a + c) % n) @ mp(Z, (b + d) % n))   # 積の公式
        rng = np.random.default_rng(n)
        M = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
        assert np.allclose(sum(np.trace(A.conj().T @ M) / n * A for A in P.values()), M)  # 基底（展開できる）
    X2, Z2, _ = shift_phase(2)
    assert np.allclose(1j * X2 @ Z2, [[0, -1j], [1j, 0]])                                  # n=2：iXZ = σy
    L = gell_mann()
    for a in range(8):
        assert np.allclose(L[a], L[a].conj().T) and np.isclose(np.trace(L[a]), 0)
        for b in range(8):
            assert np.isclose(np.trace(L[a] @ L[b]), 2 * (a == b))                         # tr(λaλb) = 2δab
    f = np.zeros((8, 8, 8))
    for a, b, c in itertools.product(range(8), repeat=3):
        f[a, b, c] = (np.trace((L[a] @ L[b] - L[b] @ L[a]) @ L[c]) / 4j).real
    for a, b in itertools.product(range(8), repeat=2):
        assert np.allclose(L[a] @ L[b] - L[b] @ L[a], 2j * sum(f[a, b, c] * L[c] for c in range(8)))
    expected = {(1, 2, 3): 1, (1, 4, 7): 0.5, (2, 4, 6): 0.5, (2, 5, 7): 0.5, (3, 4, 5): 0.5,
                (1, 5, 6): -0.5, (3, 6, 7): -0.5, (4, 5, 8): np.sqrt(3) / 2, (6, 7, 8): np.sqrt(3) / 2}
    for (a, b, c), v in expected.items():
        for p in itertools.permutations(range(3)):
            idx = [(a, b, c)[k] - 1 for k in p]
            sign = np.linalg.det(np.eye(3)[list(p)])
            assert np.isclose(f[tuple(idx)], sign * v)                                     # 完全反対称
    nonzero = {tuple(sorted(x)) for x in zip(*np.nonzero(np.abs(f) > 1e-12))}
    assert nonzero == {tuple(k - 1 for k in key) for key in expected}                      # 0 でないのはこれだけ
    return f


def grid(ax, M, x0, y0, labels, colors, size=1.0, fs=11):
    n = M.shape[0]
    for r in range(n):
        for c in range(n):
            v = complex(np.round(M[r, c], 10))
            key = min(labels, key=lambda k: abs(k - v))
            if abs(key - v) > 1e-6:
                raise ValueError(v)
            fc = colors.get(key, "white")
            ax.add_patch(plt.Rectangle((x0 + c * size, y0 + (n - 1 - r) * size), size, size, fc=fc, ec="#555", lw=1, alpha=0.85))
            ax.text(x0 + (c + 0.5) * size, y0 + (n - 1 - r + 0.5) * size, labels[key], ha="center", va="center",
                    fontsize=fs, color="#999999" if key == 0 else "white")


def gp01():
    check_claims()
    fig = plt.figure(figsize=(17, 10.5))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], width_ratios=[1.2, 1])

    # (a) n = 3 の X, Z
    ax = fig.add_subplot(gs[0, 0])
    X, Z, w = shift_phase(3)
    labels = {0: "$0$", 1: "$1$", w: "$\\omega$", w**2: "$\\omega^2$"}
    colors = {1: C_A, w: "#2ca02c", w**2: "#9467bd"}
    grid(ax, X, 0, 0, labels, colors, fs=14)
    grid(ax, Z, 4.2, 0, labels, colors, fs=14)
    ax.text(1.5, -0.55, "$X$：$|j\\rangle\\mapsto|j+1\\rangle$（巡回シフト）", ha="center", fontsize=11)
    ax.text(5.7, -0.55, "$Z$：$|j\\rangle\\mapsto\\omega^j|j\\rangle$（位相）", ha="center", fontsize=11)
    ax.text(3.6, -1.35, "$\\omega=e^{2\\pi i/3}$、$ZX=\\omega XZ$。$X^\\dagger=X^{-1}\\neq X$、$Z^\\dagger=Z^{-1}\\neq Z$（ユニタリだがエルミートでない）",
            ha="center", fontsize=10.5, color="#444")
    ax.set_xlim(-0.3, 7.5), ax.set_ylim(-1.7, 3.3), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(a) 一般化パウリ行列（$n=3$）", fontsize=12)

    # (b) X^a Z^b の直交性（n = 3）
    ax = fig.add_subplot(gs[0, 1])
    mp = np.linalg.matrix_power
    keys = [(a, b) for a in range(3) for b in range(3)]
    P = [mp(X, a) @ mp(Z, b) for a, b in keys]
    G = np.array([[np.trace(A.conj().T @ B) / 3 for B in P] for A in P])
    assert np.allclose(G, np.eye(9))
    ax.imshow(np.abs(G), cmap="Blues", vmin=-0.2, vmax=1.3)
    for i in range(9):
        for j in range(9):
            ax.text(j, i, f"{abs(G[i, j]):.0f}", ha="center", va="center", fontsize=9, color="white" if i == j else "#777")
    names = [f"$X^{a}Z^{b}$" for a, b in keys]
    ax.set_xticks(range(9), names, fontsize=9, rotation=45), ax.set_yticks(range(9), names, fontsize=9)
    ax.set_title("(b) $X^aZ^b$（$n=3$、9個）の内積 $\\frac{1}{3}\\mathrm{tr}(A^\\dagger B)$：単位行列\n"
                 "→ 互いに直交するので、位相を調整しなくても $M_3(\\mathbb{C})$ の基底", fontsize=11)

    # (c) Gell-Mann 行列
    ax = fig.add_subplot(gs[1, :])
    L = gell_mann()
    s3 = 1 / np.sqrt(3)
    lab = {0: "$0$", 1: "$1$", -1: "$-1$", 1j: "$i$", -1j: "$-i$", s3: "$\\frac{1}{\\sqrt{3}}$", -2 * s3: "$\\frac{-2}{\\sqrt{3}}$"}
    col = {1: C_A, -1: C_BAD, 1j: "#2ca02c", -1j: "#9467bd", s3: "#5b9bd5", -2 * s3: "#e06666"}
    blocks = ["(1,2) 成分：$\\sigma_x$", "(1,2) 成分：$\\sigma_y$", "対角：$\\sigma_z$", "(1,3) 成分：$\\sigma_x$",
              "(1,3) 成分：$\\sigma_y$", "(2,3) 成分：$\\sigma_x$", "(2,3) 成分：$\\sigma_y$", "対角"]
    for k in range(8):
        x0 = k * 3.6
        grid(ax, L[k], x0, 0, lab, col, fs=10)
        ax.text(x0 + 1.5, 3.25, f"$\\lambda_{k + 1}$", ha="center", fontsize=14)
        ax.text(x0 + 1.5, -0.45, blocks[k], ha="center", fontsize=9.5, color="#444")
    ax.set_xlim(-0.3, 28.6), ax.set_ylim(-0.9, 3.8), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(c) Gell-Mann 行列 $\\lambda_1,\\dots,\\lambda_8$（$SU(3)$ の生成子）：パウリ行列 $\\sigma_x,\\sigma_y$ を3つの成分の組に埋め込んだ6個と、"
                 "トレースゼロの対角行列2個。$\\mathrm{tr}(\\lambda_a\\lambda_b)=2\\delta_{ab}$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "gp01_qudit_and_gellmann.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(gp01=gp01)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
