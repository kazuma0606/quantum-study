"""pauli_matrices_derivation_and_group.md（パウリ行列）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/04_群論・代数/figures/make_pauli_figures.py            # すべて
    uv run python 研究ノート/04_群論・代数/figures/make_pauli_figures.py pauli01    # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    pauli01_tangent_space.png   Part I U(1) で見る接空間と、SU(2) の元の固有値 e^{±iα}
    pauli02_basis.png           Part II 基底 {I, σx, σy, σz} の成分、M と n の対応、直交性 ½tr(σiσj)=δij
    pauli03_product_table.png   Part IV 積の表 σiσj と、x→y→z の循環（ε_ijk）
    pauli04_dot_cross.png       Part V (a·σ)(b·σ) = (a·b)I + i(a×b)·σ の係数

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


FIGS = dict(pauli01=pauli01, pauli02=pauli02, pauli03=pauli03, pauli04=pauli04)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
