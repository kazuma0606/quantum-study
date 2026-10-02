"""lie_derivative.md（リー微分のノート）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/02_微分幾何/figures/make_lie_figures.py            # すべて
    uv run python 研究ノート/02_微分幾何/figures/make_lie_figures.py lie03      # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    lie01_flows.png            §2  流れの例（回転・拡大・せん断・有限時間で飛んでいく流れ）
    lie02_pushforward.png      §7  押し出しと引き戻し（回転の例）
    lie03_lie_derivative.png   §13 リー微分の定義：引き戻したベクトルを t で微分する
    lie04_flow_square.png      §14-1 流れで四角形を一周したずれ ≈ ts[X,Y]
    lie05_divergence.png       §27 流れによる面積の変化と発散
    lie06_killing.png          §30・§31 平面と球面のキリングベクトル
    lie07_clairaut.png         §31-1 球面の測地線とクレローの関係
    lie08_picard.png           付録A-4 逐次近似（x^2 ∂x）

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

from make_christoffel_figures import OUT, arrow  # 日本語フォント等の rcParams も設定される

C_X, C_Y, C_BR, C_GRAY = "#1f77b4", "#e67e00", "#d62728", "#888888"


def flow(F, p, t):
    """ベクトル場 F の流れで、点 p から時間 t 進んだ点（数値積分）"""
    if t == 0:
        return np.array(p, float)
    return solve_ivp(lambda _, z: F(z), [0, t], np.array(p, float), rtol=1e-11, atol=1e-13).y[:, -1]


def R(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


# ------------------------------------------------------------------------------------- lie01
def lie01():
    fields = [
        ("回転  $X=-y\\,\\partial_x+x\\,\\partial_y$", lambda p: np.array([-p[1], p[0]]),
         lambda p0, t: R(t) @ p0, ([1.2, 0.0], [0.0, 0.7], [-0.6, -0.5], [0.4, -1.1])),
        ("拡大  $X=x\\,\\partial_x+y\\,\\partial_y$", lambda p: np.array([p[0], p[1]]),
         lambda p0, t: np.exp(t) * p0, ([0.5, 0.0], [0.0, 0.4], [-0.4, -0.3], [0.3, -0.6])),
        ("せん断  $X=y\\,\\partial_x$", lambda p: np.array([p[1], 0.0]),
         lambda p0, t: np.array([p0[0] + t * p0[1], p0[1]]), ([-1.2, 1.0], [0.2, 0.5], [-0.5, -0.6], [1.0, -1.2])),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.6), gridspec_kw=dict(width_ratios=[1, 1, 1, 1.15]))
    g = np.linspace(-2, 2, 17)
    GX, GY = np.meshgrid(g, g)
    for ax, (title, F, exact, starts0) in zip(axes[:3], fields):
        U = np.vectorize(lambda x, y: F((x, y))[0])(GX, GY)
        V = np.vectorize(lambda x, y: F((x, y))[1])(GX, GY)
        ax.streamplot(GX, GY, U, V, color="#cfcfcf", density=0.9, linewidth=0.8, arrowsize=0.8)
        starts = [np.array(s_, float) for s_ in starts0]
        ts = np.linspace(0, 1, 60)
        for p0 in starts:
            path = np.array([exact(p0, t) for t in ts])
            # 数値の流れと、本文の解（閉じた式）が一致することを確認
            assert np.allclose(flow(F, p0, 1.0), exact(p0, 1.0), atol=1e-8)
            ax.plot(path[:, 0], path[:, 1], color=C_X, lw=2)
            ax.plot(*p0, "o", color="#222", ms=5)
            ax.plot(*path[-1], "o", color=C_X, ms=6, mfc="white", mew=2)
        ax.set_title(title, fontsize=12)
        ax.set_xlim(-2, 2), ax.set_ylim(-2, 2), ax.set_aspect("equal")
        ax.set_xticks([]), ax.set_yticks([])
    axes[0].plot([], [], "o", color="#222", label="出発点 $p$（$t=0$）")
    axes[0].plot([], [], "o", color=C_X, mfc="white", mew=2, label="$\\phi_1(p)$（$t=1$）")
    axes[0].legend(loc="lower left", fontsize=9, framealpha=0.9)

    # 有限時間で飛んでいく流れ
    ax = axes[3]
    for x0 in [0.5, 1.0, 2.0, -1.0]:
        tmax = 1 / x0 - 0.02 if x0 > 0 else 3.0
        tt = np.linspace(0, tmax, 400)
        xx = x0 / (1 - tt * x0)
        assert abs(flow(lambda z: z**2, [x0], 0.5 * min(tmax, 1.0))[0] - x0 / (1 - 0.5 * min(tmax, 1.0) * x0)) < 1e-7
        ax.plot(tt, xx, lw=2, label=f"$x_0={x0:g}$")
        if x0 > 0:
            ax.axvline(1 / x0, color=C_GRAY, ls="--", lw=1)
            ax.text(1 / x0 + 0.04, 9.2, f"$t=1/x_0={1 / x0:g}$", fontsize=9, color="#555", rotation=90, va="top")
    ax.set_xlim(0, 2.6), ax.set_ylim(-1.2, 10)
    ax.set_xlabel("$t$"), ax.set_ylabel("$\\phi_t(x_0)$")
    ax.set_title("$X=x^2\\,\\partial_x$：有限の時間で飛んでいく", fontsize=12)
    ax.legend(fontsize=9, loc="center right")
    fig.tight_layout()
    fig.savefig(OUT / "lie01_flows.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie02
def lie02():
    t = np.pi / 4
    J, Jinv = R(t), R(-t)
    p = np.array([1.4, 0.3])
    q = J @ p
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
    for ax in axes:
        ang = np.linspace(0, 2 * np.pi, 200)
        rr = np.linalg.norm(p)
        ax.plot(rr * np.cos(ang), rr * np.sin(ang), color="#ddd", lw=1)
        arc = np.array([R(s) @ p for s in np.linspace(0, t, 40)])
        ax.plot(arc[:, 0], arc[:, 1], color=C_GRAY, lw=2, ls=":")
        ax.plot(*p, "o", color="#222", ms=6), ax.plot(*q, "o", color="#222", ms=6)
        ax.text(*(p + [0.07, -0.18]), "$p$", fontsize=13)
        ax.text(*(q + [0.06, 0.08]), "$\\phi_t(p)$", fontsize=13)
        ax.set_xlim(-0.6, 2.6), ax.set_ylim(-0.7, 2.2), ax.set_aspect("equal")
        ax.axhline(0, color="#eee", lw=1, zorder=0), ax.axvline(0, color="#eee", lw=1, zorder=0)
        ax.set_xticks([]), ax.set_yticks([])

    # 左：押し出し
    V = np.array([0.0, 0.8])
    arrow(axes[0], p, V, C_X)
    arrow(axes[0], q, J @ V, C_X)
    axes[0].text(*(p + V + [0.05, 0.0]), "$V$", fontsize=13, color=C_X)
    axes[0].text(*(q + J @ V + [-0.45, 0.05]), "$\\phi_*V=J\\,V$", fontsize=13, color=C_X)
    axes[0].set_title("押し出し：点 $p$ のベクトルを、$\\phi(p)$ へ運ぶ（§5）", fontsize=12)

    # 右：ベクトル場 Y=∂x の引き戻し
    Y = np.array([0.9, 0.0])
    pulled = Jinv @ Y
    assert np.allclose(pulled / 0.9, [np.cos(t), -np.sin(t)])  # §7：φ_t^*∂x = cos t ∂x − sin t ∂y
    arrow(axes[1], q, Y, C_Y)
    arrow(axes[1], p, Y, C_Y, alpha=0.35, ls="--")
    arrow(axes[1], p, pulled, C_BR)
    axes[1].text(*(q + Y + [0.04, 0.03]), "$Y=\\partial_x$", fontsize=13, color=C_Y)
    axes[1].text(*(p + Y + [0.03, 0.06]), "$p$ での $Y$", fontsize=11, color=C_Y, alpha=0.7)
    axes[1].text(*(p + pulled + [-0.15, -0.28]), "$\\phi_t^*Y=J^{-1}Y$", fontsize=13, color=C_BR)
    axes[1].set_title("引き戻し：$\\phi_t(p)$ の $Y$ を、$p$ へ持ち帰る（§5・§7）", fontsize=12)
    fig.suptitle("回転 $\\phi_t$（$t=45^\\circ$）での例。ヤコビ行列 $J$ は回転行列そのもの", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "lie02_pushforward.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie03
def lie03():
    p = np.array([0.0, 0.0])
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2))
    ax = axes[0]
    cmap = plt.get_cmap("coolwarm")
    ts = np.linspace(-0.9, 0.9, 13)
    for t in ts:
        v = np.array([np.cos(t), -np.sin(t)])
        arrow(ax, p, v, cmap((t + 0.9) / 1.8), lw=1.6, alpha=0.9)
    arrow(ax, p, [1.0, 0.0], "#222", lw=2.6)
    arrow(ax, np.array([1.0, 0.0]), [0.0, -0.75], C_BR, lw=3)
    ax.text(1.06, -0.45, "$\\mathcal{L}_XY=\\left.\\dfrac{d}{dt}\\right|_{0}\\phi_t^*Y=-\\partial_y$", fontsize=13, color=C_BR)
    ax.text(1.08, 0.05, "$t=0$：$Y=\\partial_x$", fontsize=11)
    ax.text(0.30, 0.86, "$t<0$", fontsize=11, color=cmap(0.0))
    ax.text(0.30, -0.95, "$t>0$", fontsize=11, color=cmap(1.0))
    ax.set_xlim(-0.3, 2.6), ax.set_ylim(-1.15, 1.15), ax.set_aspect("equal")
    ax.set_xticks([]), ax.set_yticks([])
    ax.set_title("点 $p$ に持ち帰った $\\phi_t^*Y$（$t$ ごとに色分け）", fontsize=12)

    ax = axes[1]
    tt = np.linspace(-1.2, 1.2, 200)
    ax.plot(tt, np.cos(tt), color=C_X, lw=2, label="$x$ 成分 $\\cos t$")
    ax.plot(tt, -np.sin(tt), color=C_Y, lw=2, label="$y$ 成分 $-\\sin t$")
    ax.plot(tt, 1 + 0 * tt, color=C_X, ls=":", lw=1.4, label="$t=0$ での接線（傾き $0$）")
    ax.plot(tt, -tt, color=C_Y, ls=":", lw=1.4, label="$t=0$ での接線（傾き $-1$）")
    # 数値微分で、傾きが [X, ∂x] = (0, -1) と一致することを確認
    h = 1e-6
    d = (np.array([np.cos(h), -np.sin(h)]) - np.array([np.cos(-h), -np.sin(-h)])) / (2 * h)
    assert np.allclose(d, [0, -1])
    ax.axvline(0, color="#ccc", lw=1), ax.axhline(0, color="#ccc", lw=1)
    ax.set_xlabel("$t$"), ax.set_ylim(-1.3, 1.3)
    ax.set_title("成分のグラフ：$t=0$ での傾きが $\\mathcal{L}_XY$ の成分 $(0,-1)$", fontsize=12)
    ax.legend(fontsize=9, loc="lower left")
    fig.suptitle("$X=-y\\,\\partial_x+x\\,\\partial_y$（回転）、$Y=\\partial_x$：§8 の定義と、§13 の $[X,\\partial_x]=-\\partial_y$", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "lie03_lie_derivative.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie04
def Xs(p):
    x, y = p
    return np.array([1.0, 0.8 * y])


def Ys(p):
    x, y = p
    return np.array([0.8 * x, 1.0])


def bracket_s(p):
    """[X,Y]^i = X^j ∂_j Y^i − Y^j ∂_j X^i（§11 の公式）"""
    dY = np.array([[0.8, 0.0], [0.0, 0.0]])   # 行 i、列 j の成分が ∂_j Y^i
    dX = np.array([[0.0, 0.0], [0.0, 0.8]])   # 行 i、列 j の成分が ∂_j X^i
    return dY @ Xs(p) - dX @ Ys(p)


def square_path(p, e, n=60):
    legs, pts = [(Xs, e), (Ys, e), (Xs, -e), (Ys, -e)], []
    cur = np.array(p, float)
    for F, t in legs:
        seg = solve_ivp(lambda _, z: F(z), [0, t], cur, rtol=1e-11, atol=1e-13, dense_output=True)
        pts.append(seg.sol(np.linspace(0, t, n)).T)
        cur = seg.y[:, -1]
    return pts, cur


def lie04():
    p = np.array([0.3, 0.3])
    br = bracket_s(p)
    assert np.allclose(br, [0.8, -0.8])
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
    ax = axes[0]
    e = 0.6
    legs, q = square_path(p, e)
    cols = [C_X, C_Y, C_X, C_Y]
    names = ["① $X$ で $t$ 進む", "② $Y$ で $s$ 進む", "③ $X$ で $t$ 戻る", "④ $Y$ で $s$ 戻る"]
    for seg, c, nm, ls in zip(legs, cols, names, ["-", "-", "--", "--"]):
        ax.plot(seg[:, 0], seg[:, 1], color=c, lw=2.2, ls=ls, label=nm)
        mid = len(seg) // 2
        ax.annotate("", xy=seg[mid + 1], xytext=seg[mid - 1], arrowprops=dict(arrowstyle="-|>", color=c, lw=2))
    ax.plot(*p, "o", color="#222", ms=7), ax.text(*(p + [-0.12, -0.12]), "$p$", fontsize=14)
    ax.plot(*q, "s", color=C_BR, ms=6), ax.text(*(q + [0.04, -0.1]), "$q$", fontsize=14, color=C_BR)
    arrow(ax, p, q - p, C_BR, lw=2)
    arrow(ax, p, e * e * br, "#7b2fbf", lw=2, ls=":")
    ax.plot([], [], color=C_BR, lw=2, label="ずれ $q-p$")
    ax.plot([], [], color="#7b2fbf", lw=2, ls=":", label="$ts\\,[X,Y](p)$")
    ax.set_aspect("equal"), ax.legend(fontsize=9, loc="upper left", ncol=2)
    ax.set_xlim(0.0, 1.6), ax.set_ylim(-0.15, 1.55)
    ax.set_title(f"$t=s={e}$ で一周（$X=\\partial_x+0.8y\\,\\partial_y$、$Y=0.8x\\,\\partial_x+\\partial_y$）", fontsize=11)

    ax = axes[1]
    es = np.array([0.4, 0.3, 0.2, 0.14, 0.1, 0.07, 0.05, 0.035, 0.025])
    D = np.array([(square_path(p, e_, n=3)[1] - p) / e_**2 for e_ in es])
    assert np.allclose(D[-1], br, atol=0.05)  # ε → 0 で ずれ/ε² → [X,Y]
    ax.plot(es, D[:, 0], "o-", color=C_X, label="ずれ$/\\varepsilon^2$ の $x$ 成分")
    ax.plot(es, D[:, 1], "o-", color=C_Y, label="ずれ$/\\varepsilon^2$ の $y$ 成分")
    ax.axhline(br[0], color=C_X, ls=":", lw=1.5, label=f"$[X,Y]^x={br[0]:.3f}$")
    ax.axhline(br[1], color=C_Y, ls=":", lw=1.5, label=f"$[X,Y]^y={br[1]:.3f}$")
    ax.set_xscale("log"), ax.invert_xaxis()
    ax.set_xticks([0.4, 0.2, 0.1, 0.05, 0.025]), ax.set_xticklabels(["0.4", "0.2", "0.1", "0.05", "0.025"])
    ax.minorticks_off()
    ax.set_xlabel("刻み $\\varepsilon=t=s$（右ほど小さい）")
    ax.set_title("$\\varepsilon\\to0$ で、ずれ$/\\varepsilon^2$ が $[X,Y]$ に近づく（§14-1）", fontsize=12)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "lie04_flow_square.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie05
def shoelace(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def lie05():
    s = np.linspace(0, 1, 50)
    square = np.concatenate([np.c_[s, 0 * s], np.c_[1 + 0 * s, s], np.c_[1 - s, 1 + 0 * s], np.c_[0 * s, 1 - s]]) + [0.3, 0.2]
    cases = [
        ("回転  $\\nabla\\cdot X=0$", lambda P, t: P @ R(t).T, 0.0),
        ("せん断  $\\nabla\\cdot X=0$", lambda P, t: np.c_[P[:, 0] + t * P[:, 1], P[:, 1]], 0.0),
        ("拡大  $\\nabla\\cdot X=2$", lambda P, t: np.exp(t) * P, 2.0),
    ]
    times = [(0, 0.5, 1.0), (0, 0.5, 1.0), (0, 0.4, 0.8)]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (title, phi, div), tset in zip(axes, cases, times):
        A0 = shoelace(square)
        rows = []
        for t, c, a in zip(tset, ["#999", C_X, C_X], [0.25, 0.25, 0.45]):
            P = phi(square, t)
            A = shoelace(P)
            assert abs(A - A0 * np.exp(div * t)) < 1e-6 * max(1, A)  # 面積は e^{(∇·X) t} 倍
            ax.fill(P[:, 0], P[:, 1], color=c, alpha=a)
            ax.plot(P[:, 0], P[:, 1], color=c, lw=1.5)
            corner = phi(np.array([[1.3, 1.2]]), t)[0]
            ax.text(*(corner + [0.05, 0.05]), f"$t={t:g}$", fontsize=10)
            rows.append(f"$t={t:g}$：{A:.2f}")
        ax.text(0.97, 0.04, "面積\n" + "\n".join(rows), transform=ax.transAxes, ha="right", va="bottom", fontsize=10,
                bbox=dict(boxstyle="round", fc="white", ec="#ccc"))
        ax.set_aspect("equal"), ax.set_xticks([]), ax.set_yticks([])
        ax.axhline(0, color="#eee", lw=1, zorder=0), ax.axvline(0, color="#eee", lw=1, zorder=0)
        ax.set_title(title + f"：面積は $e^{{{div:g}t}}$ 倍", fontsize=12)
    axes[0].set_xlim(-1.9, 1.9), axes[0].set_ylim(-0.7, 2.1)
    axes[1].set_xlim(-0.3, 3.5), axes[1].set_ylim(-0.7, 2.1)
    axes[2].set_xlim(-0.3, 3.7), axes[2].set_ylim(0.0, 3.0)
    fig.suptitle("正方形を流れで運ぶ：発散がゼロなら面積は変わらず、発散が正なら膨らむ（§26・§27）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "lie05_divergence.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie06
def lie06():
    fig = plt.figure(figsize=(15, 9.4))
    g = np.linspace(-1.5, 1.5, 9)
    GX, GY = np.meshgrid(g, g)
    plane = [("$\\partial_x$（$x$ 方向の平行移動）", 1 + 0 * GX, 0 * GX),
             ("$\\partial_y$（$y$ 方向の平行移動）", 0 * GX, 1 + 0 * GX),
             ("$-y\\,\\partial_x+x\\,\\partial_y$（回転）", -GY, GX)]
    for k, (title, U, V) in enumerate(plane):
        ax = fig.add_subplot(2, 3, k + 1)
        ax.quiver(GX, GY, U, V, color=C_X, angles="xy", scale_units="xy", scale=4.5, width=0.006)
        ax.set_aspect("equal"), ax.set_xticks([]), ax.set_yticks([])
        ax.set_xlim(-1.8, 1.8), ax.set_ylim(-1.8, 1.8)
        ax.set_title("平面：" + title, fontsize=12)

    # 球面：L_a は e_a × x
    th, ph = np.meshgrid(np.linspace(0.45, np.pi - 0.45, 6), np.linspace(0, 2 * np.pi, 12, endpoint=False))
    P = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1).reshape(-1, 3)
    uu, vv = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 60))
    for k, (name, e) in enumerate([("L_x", np.array([1.0, 0, 0])), ("L_y", np.array([0, 1.0, 0])), ("L_z", np.array([0, 0, 1.0]))]):
        ax = fig.add_subplot(2, 3, 4 + k, projection="3d")
        ax.plot_surface(np.sin(uu) * np.cos(vv), np.sin(uu) * np.sin(vv), np.cos(uu), color="#dbe6f2", alpha=0.35, linewidth=0)
        Vv = np.cross(e, P)
        assert np.allclose(np.sum(Vv * P, axis=1), 0)  # 球面に接している（x·(e×x)=0）
        front = P @ np.array([0.6, -0.6, 0.5]) > -0.2
        ax.quiver(*P[front].T, *(0.25 * Vv[front]).T, color=C_X, linewidth=1.2, arrow_length_ratio=0.35)
        ax.quiver(0, 0, 0, *(1.45 * e), color=C_BR, linewidth=2, arrow_length_ratio=0.12)
        ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=22, azim=-50)
        ax.set_title(f"球面：${name}$（赤い軸の周りの回転）", fontsize=12)
    fig.suptitle("キリングベクトル：平面は平行移動2つと回転1つ（§30）、球面は回転3つ（§31）", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "lie06_killing.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie07
def lie07():
    a = 1.0

    def geo(_, z):
        th, ph, dth, dph = z
        return [dth, dph, np.sin(th) * np.cos(th) * dph**2, -2 * np.cos(th) / np.sin(th) * dth * dph]

    th0, ph0, psi0 = 1.3, 0.0, 0.9          # 出発点と、緯線となす角 ψ（速さ 1）
    z0 = [th0, ph0, -np.sin(psi0) / a, np.cos(psi0) / (a * np.sin(th0))]
    T = 2 * np.pi * a
    sol = solve_ivp(geo, [0, T], z0, rtol=1e-11, atol=1e-12, dense_output=True)
    tau = np.linspace(0, T, 600)
    th, ph, dth, dph = sol.sol(tau)
    X = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
    rho = a * np.sin(th)
    cospsi = a * np.sin(th) * dph            # 速さ 1 なので、緯線方向の速さ = cos ψ
    Q = rho * cospsi
    assert np.ptp(Q) < 1e-8 and np.allclose(Q, a**2 * np.sin(th) ** 2 * dph)
    # 大円であること：角運動量 x × ẋ が一定
    v0 = np.array([np.cos(th0) * np.cos(ph0) * z0[2] - np.sin(th0) * np.sin(ph0) * z0[3],
                   np.cos(th0) * np.sin(ph0) * z0[2] + np.sin(th0) * np.cos(ph0) * z0[3],
                   -np.sin(th0) * z0[2]])                    # 出発時の速度（R^3 の成分）
    n = np.cross(X[:, 0], v0)                                 # 角運動量 x × ẋ
    assert np.allclose(X.T @ n, 0, atol=1e-8)

    fig = plt.figure(figsize=(14, 5.6))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    uu, vv = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 60))
    ax.plot_surface(np.sin(uu) * np.cos(vv), np.sin(uu) * np.sin(vv), np.cos(uu), color="#dbe6f2", alpha=0.35, linewidth=0)
    ax.plot(*X, color=C_X, lw=2.5, label="測地線（大円）")
    th_top = np.arcsin(Q[0] / a)
    for thc, lab in [(th_top, "届く範囲の境界の緯線（$\\rho=Q_{L_z}$）"), (np.pi - th_top, None)]:
        vv1 = np.linspace(0, 2 * np.pi, 100)
        ax.plot(np.sin(thc) * np.cos(vv1), np.sin(thc) * np.sin(vv1), np.cos(thc) + 0 * vv1, color=C_Y, lw=1.5, ls="--", label=lab)
    ax.plot([0, 0], [0, 0], [-1.3, 1.3], color=C_BR, lw=2, label="$z$ 軸")
    ax.set_xlim(-1, 1), ax.set_ylim(-1, 1), ax.set_zlim(-1, 1)
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=18, azim=-60)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("球面の測地線が届く範囲は、$\\rho=Q_{L_z}$ の緯線の間", fontsize=12)

    ax = fig.add_subplot(1, 2, 2)
    ax.plot(tau, rho, color=C_X, lw=2, label="$z$ 軸までの距離 $\\rho=a\\sin\\theta$")
    ax.plot(tau, cospsi, color=C_Y, lw=2, label="緯線となす角の $\\cos\\psi$")
    ax.plot(tau, Q, color=C_BR, lw=3, label="$Q_{L_z}=\\rho\\cos\\psi=a^2\\sin^2\\theta\\,\\dot\\phi$（一定）")
    ax.set_xlabel("測地線に沿った長さ $\\tau$"), ax.set_ylim(0, 1.15)
    ax.legend(fontsize=9, loc="lower left")
    ax.set_title("クレローの関係：$\\rho$ が小さいところでは $\\cos\\psi$ が大きい（§31-1）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "lie07_clairaut.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lie08
def lie08():
    """付録A-4：X = x^2 ∂x の逐次近似。x0 = 1。"""
    import sympy as sp

    t, s = sp.symbols("t s")
    it = [sp.Integer(1)]
    for _ in range(7):
        it.append(sp.expand(1 + sp.integrate(it[-1].subs(t, s) ** 2, (s, 0, t))))
    exact_series = sp.series(1 / (1 - t), t, 0, 8).removeO()
    for k in range(1, 8):  # k 回目の近似は、正しい解のテイラー展開と t^k の項まで一致する
        diff = sp.Poly(sp.expand(it[k] - exact_series), t).all_coeffs()[::-1]
        assert all(c == 0 for c in diff[: k + 1])
    tt = np.linspace(0, 0.95, 300)
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.axvspan(0, 1 / 8, color="#cde6c7", alpha=0.7, label="付録A-3 で存在が保証される範囲 $t\\leq 1/(8x_0)$")
    ax.axvline(1.0, color=C_GRAY, ls="--", lw=1.2)
    ax.text(1.008, 5, "発散する時刻 $t=1/x_0$", ha="left", va="center", rotation=90, fontsize=10, color="#555")
    cmap = plt.get_cmap("viridis")
    for k in range(8):
        f = sp.lambdify(t, it[k], "numpy")
        ax.plot(tt, f(tt) + 0 * tt, color=cmap(k / 8), lw=1.6, label=f"$x^{{({k})}}(t)$" if k in (0, 1, 2, 3, 7) else None)
    ax.plot(tt, 1 / (1 - tt), color=C_BR, lw=3, label="正しい解 $x_0/(1-tx_0)$")
    ax.set_xlim(0, 1.06), ax.set_ylim(0, 10)
    ax.set_xlabel("$t$"), ax.set_ylabel("$x$")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("$\\dot x=x^2,\\ x_0=1$ の逐次近似：$k$ 回目の近似は、解のテイラー展開と $t^k$ の項まで一致する", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "lie08_picard.png", dpi=150)
    plt.close(fig)


FIGS = dict(lie01=lie01, lie02=lie02, lie03=lie03, lie04=lie04, lie05=lie05, lie06=lie06, lie07=lie07, lie08=lie08)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
