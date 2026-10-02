"""lie_derivative.md（リー微分のノート）用のアニメーション（GIF）を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/02_微分幾何/figures/make_lie_animations.py            # すべて
    uv run python 研究ノート/02_微分幾何/figures/make_lie_animations.py lieanim01  # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    lieanim01_drag_back.gif     §8・§13 流れで運んだ Y を、元の点に持ち帰って比べる
    lieanim02_flow_square.gif   §14-1 四角形を小さくしていくと、ずれ/ε² が [X,Y] に近づく

どちらも、描く値が本文の式と一致することを assert で確認してから書き出す。
"""

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from make_christoffel_figures import OUT  # 日本語フォント等の rcParams も設定される
from make_lie_figures import Xs, Ys, bracket_s, square_path

C_X, C_Y, C_BR, C_GRAY = "#1f77b4", "#e67e00", "#d62728", "#888888"


def R(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def quiver_arrow(ax, color, lw=2.5):
    return ax.annotate("", xy=(0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=16))


def set_arrow(art, p, v):
    art.set_position(p)            # 矢印の始点（xytext）
    art.xy = tuple(np.asarray(p) + np.asarray(v))


# ------------------------------------------------------------------------------- lieanim01
def lieanim01():
    """回転 X の流れで Y=∂x を運び、元の点 p に持ち帰る（引き戻し）。t を動かして変化率を見る。"""
    p = np.array([1.2, 0.0])
    ts = np.concatenate([np.linspace(0, 1.0, 50), np.full(12, 1.0)])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw=dict(width_ratios=[1.1, 1]))

    g = np.linspace(-1.8, 1.8, 7)
    GX, GY = np.meshgrid(g, g)
    ax.quiver(GX, GY, 0.35 + 0 * GX, 0 * GY, color="#e8c9a0", angles="xy", scale_units="xy", scale=1, width=0.004)
    ang = np.linspace(0, 2 * np.pi, 200)
    ax.plot(1.2 * np.cos(ang), 1.2 * np.sin(ang), color="#ddd", lw=1)
    ax.plot(*p, "o", color="#222", ms=7)
    ax.text(*(p + [-0.22, -0.05]), "$p$", fontsize=14)
    ax.set_xlim(-0.6, 2.4), ax.set_ylim(-1.2, 1.9), ax.set_aspect("equal"), ax.set_xticks([]), ax.set_yticks([])
    ax.set_title("回転 $X$ の流れで $p$ を運び、その先の $Y=\\partial_x$ を $p$ に持ち帰る", fontsize=11)
    path_line, = ax.plot([], [], color=C_GRAY, lw=2, ls=":")
    q_dot, = ax.plot([], [], "o", color="#222", ms=6)
    q_txt = ax.text(0, 0, "$\\phi_t(p)$", fontsize=13)
    a_Y = quiver_arrow(ax, C_Y)
    a_pull = quiver_arrow(ax, C_BR, lw=3)
    tip_line, = ax.plot([], [], color=C_BR, lw=1.2, alpha=0.6)
    ax.text(0.0, -1.05, "橙：$\\phi_t(p)$ での $Y=\\partial_x$　赤：$p$ に持ち帰った $\\phi_t^*Y$", fontsize=10)

    bx.set_xlim(0, 1.0), bx.set_ylim(-1.1, 1.15)
    bx.axhline(0, color="#ccc", lw=1)
    bx.plot([0, 1], [1, 1], color=C_X, ls=":", lw=1.2)
    bx.plot([0, 1], [0, -1], color=C_Y, ls=":", lw=1.2)
    bx.text(0.55, 1.03, "$t=0$ での接線（傾き 0）", fontsize=9, color=C_X)
    bx.text(0.6, -0.5, "$t=0$ での接線（傾き $-1$）", fontsize=9, color=C_Y)
    lx, = bx.plot([], [], color=C_X, lw=2.5, label="$\\phi_t^*Y$ の $x$ 成分 $=\\cos t$")
    ly, = bx.plot([], [], color=C_Y, lw=2.5, label="$\\phi_t^*Y$ の $y$ 成分 $=-\\sin t$")
    bx.legend(loc="lower left", fontsize=9)
    bx.set_xlabel("$t$")
    bx.set_title("$t=0$ での傾き $(0,-1)$ が $\\mathcal{L}_XY=[X,\\partial_x]=-\\partial_y$（§13）", fontsize=11)
    title = fig.suptitle("", fontsize=12)

    tips = []

    def draw(k):
        t = ts[k]
        q = R(t) @ p
        Y = np.array([0.6, 0.0])
        pulled = R(-t) @ Y                                   # §7：φ_t^*∂x = cos t ∂x − sin t ∂y
        assert np.allclose(pulled / 0.6, [np.cos(t), -np.sin(t)])
        arc = np.array([R(s) @ p for s in np.linspace(0, t, 40)])
        path_line.set_data(arc[:, 0], arc[:, 1])
        q_dot.set_data([q[0]], [q[1]])
        q_txt.set_position(q + [0.05, 0.08])
        set_arrow(a_Y, q, Y)
        set_arrow(a_pull, p, pulled)
        if k < 50:
            tips.append(p + pulled)
        tip = np.array(tips)
        tip_line.set_data(tip[:, 0], tip[:, 1])
        tt = ts[: min(k, 49) + 1]
        lx.set_data(tt, np.cos(tt)), ly.set_data(tt, -np.sin(tt))
        title.set_text(f"$t={t:.2f}$　$\\phi_t^*Y=({np.cos(t):+.2f},\\ {-np.sin(t):+.2f})$")
        return []

    anim = animation.FuncAnimation(fig, draw, frames=len(ts), interval=80)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    anim.save(OUT / "lieanim01_drag_back.gif", writer=animation.PillowWriter(fps=12), dpi=90)
    plt.close(fig)


# ------------------------------------------------------------------------------- lieanim02
def lieanim02():
    """四角形の刻み ε を小さくしていくと、ずれ/ε² が [X,Y] に近づく。"""
    p = np.array([0.3, 0.3])
    br = bracket_s(p)
    es = np.concatenate([np.geomspace(0.8, 0.03, 45), np.full(12, 0.03)])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 5.4))
    ax.set_xlim(-0.6, 2.2), ax.set_ylim(-1.4, 2.2), ax.set_aspect("equal"), ax.set_xticks([]), ax.set_yticks([])
    ax.axhline(0, color="#eee", lw=1), ax.axvline(0, color="#eee", lw=1)
    ax.set_title("経路を $\\varepsilon$ で割って拡大表示（経路の大きさを一定に保つ）", fontsize=11)
    cols = [C_X, C_Y, C_X, C_Y]
    lines = [ax.plot([], [], color=c, lw=2.2, ls=ls)[0] for c, ls in zip(cols, ["-", "-", "--", "--"])]
    ax.plot(0, 0, "o", color="#222", ms=7), ax.text(-0.18, -0.2, "$p$", fontsize=14)
    a_gap = quiver_arrow(ax, C_BR, lw=3)
    a_br = quiver_arrow(ax, "#7b2fbf", lw=2)
    ax.text(-0.5, -1.25, "赤：ずれ$/\\varepsilon^2$（図の上のすきまを、さらに $1/\\varepsilon$ 倍したもの）\n紫：$[X,Y](p)$", fontsize=10)

    bx.set_xscale("log"), bx.invert_xaxis()
    bx.set_xlim(0.9, 0.025), bx.set_ylim(-1.0, 1.0)
    bx.set_xticks([0.8, 0.4, 0.2, 0.1, 0.05]), bx.set_xticklabels(["0.8", "0.4", "0.2", "0.1", "0.05"]), bx.minorticks_off()
    bx.axhline(br[0], color=C_X, ls=":", lw=1.5), bx.axhline(br[1], color=C_Y, ls=":", lw=1.5)
    bx.text(0.85, br[0] + 0.05, f"$[X,Y]^x={br[0]:.1f}$", color=C_X, fontsize=10)
    bx.text(0.85, br[1] - 0.12, f"$[X,Y]^y={br[1]:.1f}$", color=C_Y, fontsize=10)
    gx, = bx.plot([], [], "o-", color=C_X, ms=3, label="ずれ$/\\varepsilon^2$ の $x$ 成分")
    gy, = bx.plot([], [], "o-", color=C_Y, ms=3, label="ずれ$/\\varepsilon^2$ の $y$ 成分")
    bx.legend(loc="center right", fontsize=9)
    bx.set_xlabel("刻み $\\varepsilon=t=s$（右ほど小さい）")
    bx.set_title("ずれ$/\\varepsilon^2$ は $[X,Y]$ に近づく（§14-1）", fontsize=11)
    title = fig.suptitle("", fontsize=12)
    hist = []

    def draw(k):
        e = es[k]
        legs, q = square_path(p, e, n=40)
        for ln, seg in zip(lines, legs):
            ln.set_data((seg[:, 0] - p[0]) / e, (seg[:, 1] - p[1]) / e)
        D = (q - p) / e**2
        set_arrow(a_gap, (0, 0), D)
        set_arrow(a_br, (0, 0), br)
        if k < 45:
            hist.append((e, *D))
        h = np.array(hist)
        gx.set_data(h[:, 0], h[:, 1]), gy.set_data(h[:, 0], h[:, 2])
        title.set_text(f"$\\varepsilon={e:.3f}$　ずれ$/\\varepsilon^2=({D[0]:+.3f},\\ {D[1]:+.3f})$　$[X,Y]=({br[0]:+.1f},\\ {br[1]:+.1f})$")
        return []

    anim = animation.FuncAnimation(fig, draw, frames=len(es), interval=80)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    anim.save(OUT / "lieanim02_flow_square.gif", writer=animation.PillowWriter(fps=12), dpi=90)
    D_end = (square_path(p, 0.03, n=3)[1] - p) / 0.03**2
    assert np.allclose(D_end, br, atol=0.05)
    plt.close(fig)


ANIMS = dict(lieanim01=lieanim01, lieanim02=lieanim02)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in ANIMS] or list(ANIMS)
    for name in names:
        ANIMS[name]()
        print("書き出し:", name)
