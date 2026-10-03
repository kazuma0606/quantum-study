"""manifolds_introduction.md（多様体入門）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/03_多様体・微分形式・トポロジー/figures/make_manifold_figures.py            # すべて
    uv run python 研究ノート/03_多様体・微分形式・トポロジー/figures/make_manifold_figures.py mani01     # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    mani01_charts.png          Part I §4・§5 円の2枚の地図、球面の立体射影と座標変換 u ↦ u/|u|²
    mani02_not_manifolds.png   Part I §7 多様体でない例（2本の直線の交点、二重円錐の頂点）

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY = "#1f77b4", "#e67e00", "#d62728", "#888888"


def sigma_N_inv(u):
    """北極からの立体射影の逆写像 R^2 → S^2（u は (..., 2) の配列）"""
    s = np.sum(u**2, axis=-1, keepdims=True)
    return np.concatenate([2 * u / (s + 1), (s - 1) / (s + 1)], axis=-1)


def sigma_N(p):
    return p[..., :2] / (1 - p[..., 2:3])


def sigma_S(p):
    return p[..., :2] / (1 + p[..., 2:3])


# ------------------------------------------------------------------------------------- mani01
def mani01():
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.8))

    # (a) 円の2枚の地図
    ax = axes[0]
    t1 = np.linspace(-np.pi + 0.05, np.pi - 0.05, 300)
    t2 = np.linspace(0.05, 2 * np.pi - 0.05, 300)
    ax.plot(np.cos(t1), np.sin(t1), color=C_A, lw=6, alpha=0.7, label="地図1：$-\\pi<\\theta<\\pi$")
    ax.plot(1.12 * np.cos(t2), 1.12 * np.sin(t2), color=C_B, lw=6, alpha=0.7, label="地図2：$0<\\theta'<2\\pi$")
    ax.plot(-1, 0, "o", color=C_A, mfc="white", mew=2.5, ms=10)
    ax.plot(1.12, 0, "o", color=C_B, mfc="white", mew=2.5, ms=10)
    ax.text(-1.55, 0.08, "地図1に\n入らない点", fontsize=9, color=C_A, ha="center")
    ax.text(1.62, 0.08, "地図2に\n入らない点", fontsize=9, color=C_B, ha="center")
    ax.text(0, 0.35, "上半分：$\\theta'=\\theta$", ha="center", fontsize=10)
    ax.text(0, -0.45, "下半分：$\\theta'=\\theta+2\\pi$", ha="center", fontsize=10)
    ax.set_aspect("equal"), ax.set_xlim(-2, 2), ax.set_ylim(-1.6, 1.6), ax.axis("off")
    ax.legend(fontsize=9, loc="lower center", bbox_to_anchor=(0.5, -0.06), ncol=2)
    ax.set_title("(a) 円 $S^1$：1枚の地図では、どこかで\n角度が跳ぶので、2枚で覆う", fontsize=11)

    # (b) 立体射影（xz 平面での断面）
    ax = axes[1]
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(th), np.sin(th), color="#333", lw=2)
    ax.axhline(0, color=C_GRAY, lw=1.2)
    N, S = np.array([0, 1.0]), np.array([0, -1.0])
    ang = 0.5
    P = np.array([np.cos(ang), np.sin(ang)])            # 断面の円の上の点（x, z）
    uN = P[0] / (1 - P[1])
    uS = P[0] / (1 + P[1])
    p3 = np.array([[P[0], 0.0, P[1]]])
    assert np.isclose(sigma_N(p3)[0, 0], uN) and np.isclose(sigma_S(p3)[0, 0], uS) and np.isclose(uS, 1 / uN)
    ax.plot([N[0], uN], [N[1], 0], color=C_A, lw=1.8)
    ax.plot([S[0], P[0]], [S[1], P[1]], color=C_B, lw=1.8)
    ax.plot(*N, "o", color=C_A, ms=9), ax.text(0.08, 1.08, "$N$（北極）", fontsize=11, color=C_A)
    ax.plot(*S, "o", color=C_B, ms=9), ax.text(0.08, -1.2, "$S$（南極）", fontsize=11, color=C_B)
    ax.plot(*P, "o", color="#222", ms=8), ax.text(P[0] + 0.07, P[1] + 0.07, "$p$", fontsize=13)
    ax.plot(uN, 0, "s", color=C_A, ms=8), ax.text(uN - 0.1, -0.22, f"$u=\\sigma_N(p)$", fontsize=11, color=C_A)
    ax.plot(uS, 0, "s", color=C_B, ms=8), ax.text(uS - 0.15, 0.1, f"$\\sigma_S(p)$", fontsize=11, color=C_B)
    ax.set_aspect("equal"), ax.set_xlim(-1.5, 2.6), ax.set_ylim(-1.5, 1.5), ax.axis("off")
    ax.set_title("(b) 立体射影（断面）：$N$ から $p$ を通る直線と、\n赤道面の交点が $\\sigma_N(p)$。$S$ からも同様", fontsize=11)

    # (c) 座標変換 u ↦ u/|u|^2
    ax = axes[2]
    rs = [0.4, 0.7, 1.0, 1.4, 2.5]
    cols = plt.get_cmap("viridis")(np.linspace(0, 0.9, len(rs)))
    for r, c in zip(rs, cols):
        tt = np.linspace(0, 2 * np.pi, 200)
        ax.plot(r * np.cos(tt), r * np.sin(tt), color=c, lw=2)
        ax.plot(np.cos(tt) / r, np.sin(tt) / r, color=c, lw=2, ls="--")
    rng = np.random.default_rng(0)
    U = rng.uniform(-2, 2, (200, 2))
    U = U[np.linalg.norm(U, axis=1) > 0.1]
    assert np.allclose(sigma_S(sigma_N_inv(U)), U / np.sum(U**2, axis=1, keepdims=True))   # 座標変換は u/|u|^2
    for a in np.linspace(0, np.pi, 5, endpoint=False):
        ax.plot([-3 * np.cos(a), 3 * np.cos(a)], [-3 * np.sin(a), 3 * np.sin(a)], color="#dddddd", lw=0.8, zorder=0)
    ax.plot([], [], color="#333", lw=2, label="地図 $\\sigma_N$ での円 $|u|=r$")
    ax.plot([], [], color="#333", lw=2, ls="--", label="同じ点の、地図 $\\sigma_S$ での座標（$|v|=1/r$）")
    ax.set_aspect("equal"), ax.set_xlim(-2.7, 2.7), ax.set_ylim(-2.7, 2.7)
    ax.legend(fontsize=9, loc="lower center", bbox_to_anchor=(0.5, -0.02))
    ax.set_title("(c) 座標変換 $v=u/|u|^2$（同じ色は同じ緯線）：\n$u\\neq0$ で滑らかで、逆も同じ形", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mani01_charts.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mani02
def mani02():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.4))

    # (a) 直線（多様体）：点を除くと2つに分かれる
    ax = axes[0]
    ax.plot([-1.5, -0.08], [0, 0], color=C_A, lw=4)
    ax.plot([0.08, 1.5], [0, 0], color=C_B, lw=4)
    ax.plot(0, 0, "o", color="white", mec="#333", mew=2, ms=10)
    ax.text(0, 0.25, "1点を除くと 2 つに分かれる", ha="center", fontsize=11)
    ax.set_xlim(-1.7, 1.7), ax.set_ylim(-1.2, 1.2), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(a) 直線 $\\mathbb{R}$（1次元の多様体）の、点の近く", fontsize=11)

    # (b) 2本の直線の交点
    ax = axes[1]
    cols = [C_A, C_B, "#2ca02c", "#9467bd"]
    for k, a in enumerate([0, np.pi / 2, np.pi, 3 * np.pi / 2]):
        d = np.array([np.cos(a + np.pi / 4), np.sin(a + np.pi / 4)])
        ax.plot([0.12 * d[0], 1.5 * d[0]], [0.12 * d[1], 1.5 * d[1]], color=cols[k], lw=4)
    ax.plot(0, 0, "o", color="white", mec=C_BAD, mew=2.5, ms=11)
    ax.text(0, -1.45, "交点を除くと 4 つに分かれる\n→ どんな小さな近くも $\\mathbb{R}$ と同じ形にならない", ha="center", fontsize=10.5, color=C_BAD)
    ax.set_xlim(-1.7, 1.7), ax.set_ylim(-1.8, 1.4), ax.set_aspect("equal"), ax.axis("off")
    ax.set_title("(b) 2本の直線の和 $\\{xy=0\\}$ の交点\n（多様体でない）", fontsize=11)

    # (c) 二重円錐の頂点
    ax = axes[2]
    ax.remove()
    ax = fig.add_subplot(1, 3, 3, projection="3d")
    r, t = np.meshgrid(np.linspace(0.08, 1, 20), np.linspace(0, 2 * np.pi, 50))
    for sgn, col in [(1, C_A), (-1, C_B)]:
        ax.plot_surface(r * np.cos(t), r * np.sin(t), sgn * r, color=col, alpha=0.55, linewidth=0)
    ax.scatter([0], [0], [0], color=C_BAD, s=60, depthshade=False)
    ax.set_box_aspect((1, 1, 1.2)), ax.set_axis_off(), ax.view_init(elev=12, azim=-60)
    ax.set_title("(c) 二重円錐 $x^2+y^2=z^2$ の頂点：\n除くと上下 2 つに分かれる（円板は分かれない）", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mani02_not_manifolds.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(mani01=mani01, mani02=mani02)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
