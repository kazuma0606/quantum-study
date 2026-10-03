"""pauli_matrices_derivation_and_group.md（パウリ行列）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/04_群論・代数/figures/make_pauli_figures.py            # すべて
    uv run python 研究ノート/04_群論・代数/figures/make_pauli_figures.py pauli01    # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    pauli01_tangent_space.png   Part I U(1) で見る接空間と、SU(2) の元の固有値 e^{±iα}
    pauli02_basis.png           Part II 基底 {I, σx, σy, σz} の成分、M と n の対応、直交性 ½tr(σiσj)=δij
    pauli03_product_table.png   Part IV 積の表 σiσj と、x→y→z の循環（ε_ijk）
    pauli04_dot_cross.png       Part V (a·σ)(b·σ) = (a·b)I + i(a×b)·σ の係数
    pauli05_bloch_sphere.png    Part VI ブロッホ球（6つの点と、一般の状態の θ, φ）
    pauli06_half_angle_mixed.png  Part VI 半角 |⟨+m|+n⟩|² = cos²(Θ/2)、密度行列の純度と固有値

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY = "#1f77b4", "#e67e00", "#d62728", "#888888"

SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]])
SZ = np.diag([1.0 + 0j, -1.0])


def random_su2(rng):
    """ランダムな SU(2) の元（複素ガウス行列の QR 分解でユニタリ行列を作り、det で割る）"""
    Z = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    Q, R = np.linalg.qr(Z)
    Q = Q @ np.diag(np.diag(R) / np.abs(np.diag(R)))
    return Q / np.sqrt(np.linalg.det(Q)), Q


# ------------------------------------------------------------------------------------- pauli01
def pauli01():
    """Part I：(a) U(1) で見る接空間、(b) SU(2) の元の固有値 e^{±iα} と、U = e^{iA} の構成。"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8))

    # (a) U(1) = 単位円。I = 1 での接ベクトルは純虚数
    ax = axes[0]
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(th), np.sin(th), color="#bbbbbb", lw=1.5)
    ax.plot([1, 1], [-1.5, 1.5], color=C_A, lw=1.5, ls="--")
    ax.text(1.05, 1.32, "$1$ での接空間 $=i\\mathbb{R}$\n（$i\\times$ 実数）", color=C_A, fontsize=11)
    a = 0.8
    t = np.linspace(0, 1.4, 100)
    z = np.exp(1j * a * t)
    ax.plot(z.real, z.imag, color=C_B, lw=3, label="曲線 $U(t)=e^{iat}$（$a=0.8$）")
    ax.annotate("", xy=(1, a * 0.9), xytext=(1, 0), arrowprops=dict(arrowstyle="-|>", color=C_BAD, lw=2.5))
    ax.text(1.05, 0.3, "速度 $U'(0)=ia$", color=C_BAD, fontsize=11)
    h = 1e-6
    assert np.isclose((np.exp(1j * a * h) - np.exp(-1j * a * h)) / (2 * h), 1j * a)   # U'(0) = ia
    t2 = 2 * np.pi / a
    assert np.isclose(np.exp(1j * a * t2), 1)                                          # t = 2π/a で 1 に戻る
    ax.plot(1, 0, "o", color="#222", ms=8)
    ax.text(0.62, -0.18, "$1=U(0)$", fontsize=11)
    ax.text(-1.45, -1.38, f"$t=2\\pi/a\\approx{t2:.2f}$ で $e^{{iat}}=1$ に戻る：\n1つの値 $e^{{ia t}}=1$ からは $a=0$ と言えない", fontsize=10)
    ax.set_aspect("equal"), ax.set_xlim(-1.5, 2.2), ax.set_ylim(-1.5, 1.6)
    ax.set_xlabel("実部"), ax.set_ylabel("虚部"), ax.legend(fontsize=10, loc="upper left")
    ax.set_title("(a) いちばん簡単な例 $U(1)=\\{e^{i\\theta}\\}$（単位円）：\n$1$ での接ベクトルは純虚数 $ia$（$a$ は $1\\times1$ のエルミート行列＝実数）", fontsize=11)

    # (b) SU(2) の元の固有値
    ax = axes[1]
    rng = np.random.default_rng(3)
    ax.plot(np.cos(th), np.sin(th), color="#bbbbbb", lw=1.5)
    for k in range(40):
        U, Q = random_su2(rng)
        assert np.allclose(U.conj().T @ U, np.eye(2)) and np.isclose(np.linalg.det(U), 1)
        assert np.isclose(abs(U[0, 0]) ** 2 + abs(U[1, 0]) ** 2, 1)
        assert np.isclose(U[1, 1], np.conj(U[0, 0])) and np.isclose(U[0, 1], -np.conj(U[1, 0]))   # [[a,-b*],[b,a*]]
        lam, V = np.linalg.eig(U)
        assert np.allclose(np.abs(lam), 1) and np.isclose(lam[0] * lam[1], 1)        # |λ|=1、λ1λ2=1
        # U は正規行列なので、固有ベクトルを正規直交化すれば V はユニタリ
        V, _ = np.linalg.qr(V)
        alpha = np.angle(lam[0])
        A = V @ np.diag([alpha, -alpha]) @ V.conj().T
        assert np.allclose(A, A.conj().T) and np.isclose(np.trace(A), 0)
        assert np.allclose(expm(1j * A), U, atol=1e-10)                               # U = e^{iA}
        lq = np.linalg.eigvals(Q)                                                     # 比較：一般の U(2) の元
        if k < 25:
            ax.plot([lam[0].real, lam[1].real], [lam[0].imag, lam[1].imag], color=C_A, lw=0.8, alpha=0.6)
            ax.plot(lam.real, lam.imag, "o", color=C_A, ms=5)
            ax.plot(lq.real * 1.0, lq.imag * 1.0, "x", color=C_GRAY, ms=5, alpha=0.6)
    ax.plot([], [], "o-", color=C_A, label="$SU(2)$ の元の固有値の組 $e^{\\pm i\\alpha}$（線で結ぶ）")
    ax.plot([], [], "x", color=C_GRAY, label="比較：$U(2)$ の元の固有値（組になっていない）")
    ax.axhline(0, color="#dddddd", lw=1, zorder=0)
    ax.set_aspect("equal"), ax.set_xlim(-1.5, 1.5), ax.set_ylim(-1.5, 1.9)
    ax.set_xlabel("実部"), ax.set_ylabel("虚部"), ax.legend(fontsize=9.5, loc="upper center")
    ax.set_title("(b) $SU(2)$ の元の固有値：$|\\lambda|=1$、$\\lambda_1\\lambda_2=\\det U=1$ なので\n実軸について対称な組 $e^{\\pm i\\alpha}$ → $U=e^{iA}$、$A=V\\,\\mathrm{diag}(\\alpha,-\\alpha)\\,V^\\dagger$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "pauli01_tangent_space.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- pauli02
def pauli02():
    """Part II：基底 {I, σx, σy, σz} の成分、M ↔ n の対応、直交性 ½tr(σiσj) = δij。"""
    basis = [("I", np.eye(2, dtype=complex)), ("\\sigma_x", SX), ("\\sigma_y", SY), ("\\sigma_z", SZ)]
    fig = plt.figure(figsize=(18, 6.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1, 0.9])

    # (a) 4つの基底行列の成分
    ax = fig.add_subplot(gs[0, 0])
    colors = {1: C_A, -1: C_BAD, 1j: "#2ca02c", -1j: "#9467bd"}
    labels = {1: "$1$", -1: "$-1$", 1j: "$i$", -1j: "$-i$", 0: "$0$"}
    for k, (name, Mtx) in enumerate(basis):
        x0 = k * 2.7
        for r in range(2):
            for c in range(2):
                v = complex(np.round(Mtx[r, c], 12))
                key = 0 if v == 0 else (1 if v == 1 else -1 if v == -1 else 1j if v == 1j else -1j)
                fc = "white" if key == 0 else colors[key]
                ax.add_patch(plt.Rectangle((x0 + c, 1 - r), 1, 1, fc=fc, ec="#444", lw=1.2, alpha=0.85))
                ax.text(x0 + c + 0.5, 1 - r + 0.5, labels[key], ha="center", va="center", fontsize=14,
                        color="#999999" if key == 0 else "white")
        ax.text(x0 + 1, -0.45, f"${name}$", ha="center", fontsize=15)
    ax.text(5.4, -1.25, "$\\sigma_z$：対角成分だけ　$\\sigma_x$：非対角の実数　$\\sigma_y$：非対角の純虚数", ha="center", fontsize=10.5, color="#444")
    ax.set_xlim(-0.2, 10.9), ax.set_ylim(-1.6, 2.3), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(a) エルミート $2\\times2$ 行列の基底 $\\{I,\\sigma_x,\\sigma_y,\\sigma_z\\}$ の成分\n（成分の位置と位相がすべて違う → 互いに直交）", fontsize=11)

    # (b) トレースゼロのエルミート行列 M ↔ 3次元ベクトル n
    ax = fig.add_subplot(gs[0, 1], projection="3d")
    M = np.array([[1, 2 - 1j], [2 + 1j, -1]])
    n = np.array([0.5 * np.trace(S @ M) for S in (SX, SY, SZ)])
    assert np.allclose(n.imag, 0) and np.allclose(n.real, [2, 1, 1])                     # n_i = ½tr(σi M)
    assert np.allclose(n[0] * SX + n[1] * SY + n[2] * SZ, M)
    n = n.real
    for e, lab in zip(np.eye(3), ("\\sigma_x", "\\sigma_y", "\\sigma_z")):
        ax.quiver(0, 0, 0, *(2.6 * e), color="#888", lw=1.2, arrow_length_ratio=0.06)
        ax.text(*(2.8 * e), f"${lab}$", fontsize=13, color="#444")
    ax.quiver(0, 0, 0, *n, color=C_BAD, lw=3, arrow_length_ratio=0.12)
    ax.plot([n[0], n[0], 0], [0, n[1], n[1]], [0, 0, 0], color=C_BAD, lw=0.8, ls=":")
    ax.plot([n[0], n[0]], [n[1], n[1]], [0, n[2]], color=C_BAD, lw=0.8, ls=":")
    ax.text(*(n + [0.1, 0.1, 0.25]), "$\\vec n=(2,1,1)$", color=C_BAD, fontsize=12)
    ax.set_xlim(0, 2.6), ax.set_ylim(0, 2.6), ax.set_zlim(0, 2.6)
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=22, azim=-65)
    ax.set_title("(b) $M$ と $\\vec n$ の対応（§4 の例）\n"
                 "$M$ = (1, 2−i ; 2+i, −1) $=2\\sigma_x+\\sigma_y+\\sigma_z$", fontsize=11)

    # (c) 直交性：½ tr(A_i A_j) = δ_ij
    ax = fig.add_subplot(gs[0, 2])
    G = np.array([[0.5 * np.trace(A.conj().T @ B) for _, B in basis] for _, A in basis])
    assert np.allclose(G, np.eye(4))                                                   # ½⟨A_i, A_j⟩ = δ_ij
    for _, A in basis[1:]:
        for _, B in basis[1:]:
            assert np.isclose(np.trace(A.conj().T @ B), np.trace(A @ B))                # エルミートなら tr(A†B) = tr(AB)
    rng = np.random.default_rng(5)
    Z = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    coef = [0.5 * np.trace(A @ Z) for _, A in basis]
    assert np.allclose(sum(c * A for c, (_, A) in zip(coef, basis)), Z)                # 任意の複素行列も展開できる
    H = Z + Z.conj().T
    assert np.allclose([0.5 * np.trace(A @ H) for _, A in basis], np.real([0.5 * np.trace(A @ H) for _, A in basis]))
    ax.imshow(G.real, cmap="Blues", vmin=-0.2, vmax=1.3)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{G[i, j].real:.0f}", ha="center", va="center", fontsize=14, color="white" if i == j else "#555")
    names = ["$I$", "$\\sigma_x$", "$\\sigma_y$", "$\\sigma_z$"]
    ax.set_xticks(range(4), names, fontsize=12), ax.set_yticks(range(4), names, fontsize=12)
    ax.set_title("(c) 内積 $\\frac{1}{2}\\mathrm{tr}(A^\\dagger B)$ の表：単位行列になる\n（$\\mathrm{tr}(\\sigma_i\\sigma_j)=2\\delta_{ij}$、$I$ とも直交）", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "pauli02_basis.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- pauli03
def pauli03():
    """Part IV：積の表 σiσj と、x→y→z の循環（ε_ijk）。"""
    S = {"x": SX, "y": SY, "z": SZ}
    names = ["x", "y", "z"]
    eps = {("x", "y", "z"): 1, ("y", "z", "x"): 1, ("z", "x", "y"): 1,
           ("x", "z", "y"): -1, ("z", "y", "x"): -1, ("y", "x", "z"): -1}
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw=dict(width_ratios=[1.15, 1]))

    ax = axes[0]
    for r, i in enumerate(names):
        for c, j in enumerate(names):
            P = S[i] @ S[j]
            if i == j:
                assert np.allclose(P, np.eye(2))
                txt, fc = "$I$", "#dddddd"
            else:
                k = [m for m in names if m not in (i, j)][0]
                e = eps[(i, j, k)]
                assert np.allclose(P, e * 1j * S[k])                                     # σiσj = i ε_ijk σk
                assert np.allclose(S[i] @ S[j] - S[j] @ S[i], 2j * e * S[k])               # 交換関係
                assert np.allclose(S[i] @ S[j] + S[j] @ S[i], 0)                          # 反交換関係
                txt = f"$+i\\sigma_{k}$" if e > 0 else f"$-i\\sigma_{k}$"
                fc = "#cfe2f3" if e > 0 else "#fde3c8"
            ax.add_patch(plt.Rectangle((c, 2 - r), 1, 1, fc=fc, ec="#555", lw=1.2))
            ax.text(c + 0.5, 2 - r + 0.5, txt, ha="center", va="center", fontsize=18)
    for k, m in enumerate(names):
        ax.text(k + 0.5, 3.12, f"$\\sigma_{m}$", ha="center", fontsize=15)
        ax.text(-0.15, 2 - k + 0.5, f"$\\sigma_{m}$", ha="right", va="center", fontsize=15)
    ax.text(1.5, 3.55, "右から掛ける $\\sigma_j$", ha="center", fontsize=11, color="#555")
    ax.text(-0.75, 1.5, "左の $\\sigma_i$", ha="center", va="center", rotation=90, fontsize=11, color="#555")
    ax.set_xlim(-1.0, 3.2), ax.set_ylim(-0.2, 3.8), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(a) 積の表 $\\sigma_i\\sigma_j=\\delta_{ij}I+i\\varepsilon_{ijk}\\sigma_k$\n（青：$+i$、橙：$-i$。表は対角線について反対称）", fontsize=11)

    # (b) 循環図
    ax = axes[1]
    ang = {"x": 90, "y": -30, "z": 210}
    pos = {m: np.array([np.cos(np.radians(a)), np.sin(np.radians(a))]) for m, a in ang.items()}
    for m in names:
        ax.add_patch(plt.Circle(pos[m], 0.22, fc="white", ec=C_A, lw=2.5, zorder=3))
        ax.text(*pos[m], f"$\\sigma_{m}$", ha="center", va="center", fontsize=18, zorder=4)
    for a_, b_ in [("x", "y"), ("y", "z"), ("z", "x")]:
        p, q = pos[a_], pos[b_]
        d = (q - p) / np.linalg.norm(q - p)
        ax.annotate("", xy=q - 0.26 * d, xytext=p + 0.26 * d,
                    arrowprops=dict(arrowstyle="-|>", color=C_A, lw=2.5, connectionstyle="arc3,rad=-0.25", mutation_scale=22))
    ax.text(0, 0.02, "矢印の向きに\n2つ掛けると\n残りの $+i$ 倍", ha="center", va="center", fontsize=11, color=C_A)
    ax.text(0, -1.45, "例：$\\sigma_x\\sigma_y=+i\\sigma_z$、$\\sigma_y\\sigma_z=+i\\sigma_x$、$\\sigma_z\\sigma_x=+i\\sigma_y$\n"
            "逆向き：$\\sigma_y\\sigma_x=-i\\sigma_z$ など（$\\varepsilon_{ijk}$ の符号）",
            ha="center", va="center", fontsize=11)
    ax.set_xlim(-1.7, 1.7), ax.set_ylim(-1.9, 1.5), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(b) $x\\to y\\to z\\to x$ の循環：$\\varepsilon_{xyz}=\\varepsilon_{yzx}=\\varepsilon_{zxy}=+1$\n逆回りは $-1$、同じ添字を含むと $0$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "pauli03_product_table.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- pauli04
def pauli04():
    """Part V：(a·σ)(b·σ) = (a·b)I + i(a×b)·σ。係数を ½tr で取り出して確かめる。"""
    a = np.array([1.2, 0.3, 0.2])
    b = np.array([0.2, 1.0, 0.6])
    dot = lambda v: v[0] * SX + v[1] * SY + v[2] * SZ
    P = dot(a) @ dot(b)
    c0 = 0.5 * np.trace(P)
    ck = np.array([0.5 * np.trace(S @ P) for S in (SX, SY, SZ)])
    assert np.isclose(c0, a @ b) and np.allclose(ck, 1j * np.cross(a, b))                  # 係数 = a·b と i(a×b)
    assert np.allclose(P, (a @ b) * np.eye(2) + 1j * dot(np.cross(a, b)))
    assert np.allclose(dot(a) @ dot(a), (a @ a) * np.eye(2))                                # (a·σ)² = |a|² I
    assert np.allclose(dot(a) @ dot(b) - dot(b) @ dot(a), 2j * dot(np.cross(a, b)))         # [a·σ, b·σ] = 2i(a×b)·σ
    assert np.allclose(dot(a) @ dot(b) + dot(b) @ dot(a), 2 * (a @ b) * np.eye(2))          # {a·σ, b·σ} = 2(a·b)I
    # 四元数：𝐢 = -iσx など。(−i a·σ)(−i b·σ) は純四元数の積 (−a·b, a×b)
    Q = (-1j * dot(a)) @ (-1j * dot(b))
    assert np.allclose(Q, -(a @ b) * np.eye(2) + (-1j) * dot(np.cross(a, b)))

    fig = plt.figure(figsize=(15, 6.2))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    cr = np.cross(a, b)
    for v, col, lab in [(a, C_A, "$\\vec a$"), (b, C_B, "$\\vec b$"), (cr, C_BAD, "$\\vec a\\times\\vec b$")]:
        ax.quiver(0, 0, 0, *v, color=col, lw=3, arrow_length_ratio=0.1)
        ax.text(*(v * 1.12), lab, color=col, fontsize=13)
    for e in np.eye(3):
        ax.quiver(0, 0, 0, *(1.3 * e), color="#bbbbbb", lw=1, arrow_length_ratio=0.05)
    ax.set_xlim(-0.2, 1.3), ax.set_ylim(-0.2, 1.3), ax.set_zlim(-0.2, 1.3)
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=22, azim=-50)
    ax.set_title(f"(a) $\\vec a=(1.2,0.3,0.2)$、$\\vec b=(0.2,1.0,0.6)$\n"
                 f"$\\vec a\\cdot\\vec b={a @ b:.2f}$、$\\vec a\\times\\vec b=({cr[0]:.2f},{cr[1]:.2f},{cr[2]:.2f})$", fontsize=11)

    ax = fig.add_subplot(1, 2, 2)
    labels = ["$I$ の係数\n（実部）", "$\\sigma_x$ の係数\n（虚部）", "$\\sigma_y$ の係数\n（虚部）", "$\\sigma_z$ の係数\n（虚部）"]
    vals = [c0.real, *ck.imag]
    target = [a @ b, *cr]
    cols = [C_A, C_BAD, C_BAD, C_BAD]
    ax.bar(range(4), vals, color=cols, alpha=0.75, width=0.6)
    ax.scatter(range(4), target, marker="_", s=900, color="#222", linewidths=2.5, zorder=3,
               label="直接計算した $\\vec a\\cdot\\vec b$ と $\\vec a\\times\\vec b$ の成分")
    for k, v in enumerate(vals):
        ax.text(k, v + (0.04 if v >= 0 else -0.08), f"{v:.2f}", ha="center", fontsize=11)
    ax.axhline(0, color="#888", lw=1)
    ax.set_xticks(range(4), labels, fontsize=10.5)
    ax.legend(fontsize=10, loc="lower left")
    ax.set_ylim(-0.85, 1.3)
    ax.set_title("(b) 積 $(\\vec a\\cdot\\vec\\sigma)(\\vec b\\cdot\\vec\\sigma)$ を $\\{I,\\sigma_x,\\sigma_y,\\sigma_z\\}$ で展開した係数\n"
                 "（$\\frac{1}{2}\\mathrm{tr}$ で取り出す）：$I$ の係数 $=\\vec a\\cdot\\vec b$、$\\vec\\sigma$ の係数 $=i\\,\\vec a\\times\\vec b$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "pauli04_dot_cross.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- pauli05
def ket_n(th, ph):
    """n·σ の固有値 +1 の固有ベクトル |+n⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩"""
    return np.array([np.cos(th / 2), np.exp(1j * ph) * np.sin(th / 2)])


def nvec(th, ph):
    return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])


def check_bloch_formulas():
    """Part VI の式を、ランダムな方向で確かめる"""
    rng = np.random.default_rng(7)
    for _ in range(50):
        th, ph = rng.uniform(0.05, np.pi - 0.05), rng.uniform(-np.pi, np.pi)
        n = nvec(th, ph)
        N = n[0] * SX + n[1] * SY + n[2] * SZ
        assert np.allclose(N, [[np.cos(th), np.sin(th) * np.exp(-1j * ph)], [np.sin(th) * np.exp(1j * ph), -np.cos(th)]])
        vp = ket_n(th, ph)
        vm = np.array([np.sin(th / 2), -np.exp(1j * ph) * np.cos(th / 2)])
        assert np.allclose(N @ vp, vp) and np.allclose(N @ vm, -vm)                        # 固有値 ±1 の固有ベクトル
        assert np.allclose(vm, ket_n(np.pi - th, ph + np.pi))                               # −1 は対蹠点の状態
        assert np.allclose([np.vdot(vp, S @ vp) for S in (SX, SY, SZ)], n)                  # ⟨σ⟩ = n
        assert np.allclose(np.outer(vp, vp.conj()), 0.5 * (np.eye(2) + N))                  # |+n⟩⟨+n| = ½(I + n·σ)
        assert np.isclose(vp[1] / vp[0], (n[0] + 1j * n[1]) / (1 + n[2]))                   # β/α = 南極からの立体射影
        th2, ph2 = rng.uniform(0, np.pi), rng.uniform(-np.pi, np.pi)
        m = nvec(th2, ph2)
        assert np.isclose(abs(np.vdot(ket_n(th2, ph2), vp)) ** 2, (1 + n @ m) / 2)          # |⟨+m|+n⟩|² = (1+n·m)/2
        # 任意の状態は、大域位相を除いて |+n⟩
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        psi /= np.linalg.norm(psi)
        psi0 = psi * np.exp(-1j * np.angle(psi[0]))
        t0, p0 = 2 * np.arccos(psi0[0].real), np.angle(psi0[1])
        assert np.allclose(psi0, ket_n(t0, p0))


def pauli05():
    """Part VI：ブロッホ球。6つの点と、一般の状態 cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩。"""
    check_bloch_formulas()
    six = [((0, 0, 1), "$|0\\rangle$", (0, 0.06, 0.12)), ((0, 0, -1), "$|1\\rangle$", (0, 0.06, -0.2)),
           ((1, 0, 0), "$|{+}\\rangle$", (0.05, 0.12, -0.22)), ((-1, 0, 0), "$|{-}\\rangle$", (-0.15, 0, 0.05)),
           ((0, 1, 0), "$|{+i}\\rangle$", (0.02, 0.1, 0.02)), ((0, -1, 0), "$|{-i}\\rangle$", (0, -0.25, 0.04))]
    for v, _, _ in six:                                                                       # 6点が対応する固有状態
        v = np.array(v, float)
        th, ph = np.arccos(v[2]), np.arctan2(v[1], v[0])
        N = v[0] * SX + v[1] * SY + v[2] * SZ
        assert np.allclose(N @ ket_n(th, ph), ket_n(th, ph))
    fig = plt.figure(figsize=(9, 8.4))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    u, w = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 60))
    ax.plot_surface(np.sin(u) * np.cos(w), np.sin(u) * np.sin(w), np.cos(u), color="#dbe6f2", alpha=0.18, linewidth=0)
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(t), np.sin(t), 0, color="#aaaaaa", lw=0.8)
    ax.plot(np.cos(t), 0 * t, np.sin(t), color="#cccccc", lw=0.6)
    for e, lab in zip(np.eye(3), ("$x$", "$y$", "$z$")):
        ax.plot(*np.array([-1.3 * e, 1.3 * e]).T, color="#999999", lw=0.8)
        ax.text(*(1.55 * e), lab, fontsize=13, color="#666")
    for v, lab, off in six:
        v = np.array(v, float)
        ax.scatter(*v, color=C_A, s=45, depthshade=False)
        ax.text(*(v * 1.12 + np.array(off)), lab, fontsize=14, color=C_A)
    th, ph = np.radians(55), np.radians(40)
    n = nvec(th, ph)
    ax.quiver(0, 0, 0, *n, color=C_BAD, lw=2.5, arrow_length_ratio=0.1)
    ax.plot([0, n[0]], [0, n[1]], [0, 0], color=C_BAD, lw=0.8, ls="--")
    ax.plot([n[0], n[0]], [n[1], n[1]], [0, n[2]], color=C_BAD, lw=0.8, ls=":")
    tt = np.linspace(0, th, 40)
    ax.plot(0.35 * np.sin(tt) * np.cos(ph), 0.35 * np.sin(tt) * np.sin(ph), 0.35 * np.cos(tt), color="#333", lw=1.2)
    ax.text(0.1, 0.12, 0.42, "$\\theta$", fontsize=13)
    pp = np.linspace(0, ph, 40)
    ax.plot(0.45 * np.cos(pp), 0.45 * np.sin(pp), 0 * pp, color="#333", lw=1.2)
    ax.text(0.5, 0.2, -0.05, "$\\phi$", fontsize=13)
    ax.text(*(n * 1.15 + np.array([0, 0.05, 0.05])), "$\\vec n$", fontsize=14, color=C_BAD)
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=18, azim=30)
    ax.set_xlim(-1.1, 1.1), ax.set_ylim(-1.1, 1.1), ax.set_zlim(-1.1, 1.1)
    ax.set_title("ブロッホ球：状態 $\\cos\\frac{\\theta}{2}|0\\rangle+e^{i\\phi}\\sin\\frac{\\theta}{2}|1\\rangle$ は\n"
                 "$\\hat n\\cdot\\vec\\sigma$ の固有値 $+1$ の固有状態で、球面上の点 $\\vec n=(\\sin\\theta\\cos\\phi,\\ \\sin\\theta\\sin\\phi,\\ \\cos\\theta)$ に対応する",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "pauli05_bloch_sphere.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- pauli06
def pauli06():
    """Part VI：(a) 半角 |⟨+m|+n⟩|² = cos²(Θ/2)、(b) 密度行列 ρ = ½(I + r·σ) の純度と固有値。"""
    rng = np.random.default_rng(11)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    ax = axes[0]
    Th = np.linspace(0, np.pi, 300)
    ax.plot(np.degrees(Th), np.cos(Th / 2) ** 2, color=C_A, lw=2.5, label="$\\cos^2(\\Theta/2)=(1+\\hat n\\cdot\\hat m)/2$")
    pts = []
    for _ in range(60):
        a1, b1, a2, b2 = rng.uniform(0, np.pi), rng.uniform(-np.pi, np.pi), rng.uniform(0, np.pi), rng.uniform(-np.pi, np.pi)
        n, m = nvec(a1, b1), nvec(a2, b2)
        ov = abs(np.vdot(ket_n(a2, b2), ket_n(a1, b1))) ** 2
        ang = np.arccos(np.clip(n @ m, -1, 1))
        assert np.isclose(ov, np.cos(ang / 2) ** 2)
        pts.append((np.degrees(ang), ov))
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1], "o", color=C_BAD, ms=5, label="ランダムな2状態（数値計算）")
    ax.annotate("対蹠点（$\\Theta=180^\\circ$）\n→ 直交する状態", xy=(180, 0), xytext=(128, 0.6), fontsize=10,
                arrowprops=dict(arrowstyle="-|>", color="#333"))
    ax.annotate("$\\Theta=90^\\circ$ → $1/2$\n（例：$|0\\rangle$ と $|{+}\\rangle$）", xy=(90, 0.5), xytext=(20, 0.25), fontsize=10,
                arrowprops=dict(arrowstyle="-|>", color="#333"))
    assert np.isclose(abs(np.vdot(ket_n(0, 0), ket_n(np.pi / 2, 0))) ** 2, 0.5)
    assert np.isclose(abs(np.vdot(ket_n(0, 0), ket_n(np.pi, 0))) ** 2, 0)
    ax.set_xlim(0, 182), ax.set_ylim(-0.03, 1.05), ax.set_xticks([0, 45, 90, 135, 180])
    ax.set_xlabel("球面上の2点 $\\hat n,\\hat m$ のなす角 $\\Theta$ [度]"), ax.set_ylabel("$|\\langle +m|+n\\rangle|^2$")
    ax.legend(fontsize=10, loc="upper right")
    ax.set_title("(a) 状態の重なりは、球面上の角度の半分 $\\Theta/2$ で決まる\n（状態ベクトルの角度は、ブロッホ球の角度の半分）", fontsize=11)

    ax = axes[1]
    r = np.linspace(0, 1.25, 300)
    ax.axvspan(1, 1.25, color="#f3d1d1", alpha=0.6)
    ax.text(1.02, 0.12, "$|\\vec r|>1$：\n固有値が負になり\n密度行列でない", fontsize=10, color=C_BAD)
    ax.plot(r, (1 + r**2) / 2, color=C_A, lw=2.5, label="純度 $\\mathrm{tr}\\,\\rho^2=(1+|\\vec r|^2)/2$")
    ax.plot(r, (1 + r) / 2, color=C_B, lw=2, ls="--", label="固有値 $(1+|\\vec r|)/2$")
    ax.plot(r, (1 - r) / 2, color=C_B, lw=2, ls=":", label="固有値 $(1-|\\vec r|)/2$")
    rs, pur = [], []
    for _ in range(80):                                                                      # ランダムな混合状態
        k = rng.integers(1, 4)
        w = rng.dirichlet(np.ones(k))
        rho = np.zeros((2, 2), complex)
        for wi in w:
            a, b = rng.uniform(0, np.pi), rng.uniform(-np.pi, np.pi)
            v = ket_n(a, b)
            rho += wi * np.outer(v, v.conj())
        rv = np.array([np.trace(S @ rho).real for S in (SX, SY, SZ)])
        assert np.allclose(rho, 0.5 * (np.eye(2) + rv[0] * SX + rv[1] * SY + rv[2] * SZ))   # ρ = ½(I + r·σ)
        lam = np.linalg.eigvalsh(rho)
        R = np.linalg.norm(rv)
        assert R <= 1 + 1e-12 and np.allclose(sorted(lam), [(1 - R) / 2, (1 + R) / 2])
        assert np.isclose(np.trace(rho @ rho).real, (1 + R**2) / 2)
        rs.append(R), pur.append(np.trace(rho @ rho).real)
    ax.plot(rs, pur, "o", color=C_BAD, ms=4, label="ランダムな混合状態（数値計算）")
    ax.axvline(1, color="#888", lw=1)
    ax.text(0.97, 1.08, "純粋状態\n（球面上）", fontsize=10, ha="right")
    ax.annotate("完全な混合状態 $\\rho=I/2$\n（球の中心）", xy=(0, 0.5), xytext=(0.06, 0.3), fontsize=10,
                arrowprops=dict(arrowstyle="-|>", color="#333"))
    ax.set_xlim(0, 1.25), ax.set_ylim(-0.15, 1.25)
    ax.set_xlabel("ブロッホベクトルの長さ $|\\vec r|$"), ax.legend(fontsize=9.5, loc="upper left")
    ax.set_title("(b) 密度行列 $\\rho=\\frac{1}{2}(I+\\vec r\\cdot\\vec\\sigma)$：固有値 $\\frac{1}{2}(1\\pm|\\vec r|)\\geq0$ から $|\\vec r|\\leq1$\n"
                 "球面上（$|\\vec r|=1$）が純粋状態、内側が混合状態", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "pauli06_half_angle_mixed.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(pauli01=pauli01, pauli02=pauli02, pauli03=pauli03, pauli04=pauli04, pauli05=pauli05, pauli06=pauli06)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
