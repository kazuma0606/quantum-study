"""christoffel_riemann_intro.md 用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/figures/make_christoffel_figures.py

出力（このスクリプトと同じ figures/ ディレクトリ）:
    fig1_polar_basis.png       極座標の基底ベクトルの場所依存と Γ^r_θθ = -r
    fig2_parallel_transport.png 平面と球面での並行移動（ホロノミー）
    fig3_principal_curvature.png 球・円柱・鞍面の主曲率とガウス曲率の符号

極座標の約定は標準の x = r cosθ, y = r sinθ（本文の Part I §1 と Part VI に合わせている）。
本文の Part IV §5-b ③ だけは x = r sinθ, y = r cosθ を使っているが、Γ の値は同じ。
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_R = "#1f77b4"  # e_r
C_TH = "#d62728"  # e_theta
C_GRID = "#b0b0b0"


def e_r(theta):
    return np.array([np.cos(theta), np.sin(theta)])


def e_th(r, theta):
    return np.array([-r * np.sin(theta), r * np.cos(theta)])


def arrow(ax, p, v, color, lw=2.2, **kw):
    ax.add_patch(
        FancyArrowPatch(
            p, p + v, arrowstyle="-|>", mutation_scale=14, color=color, lw=lw, **kw
        )
    )


# ---------------------------------------------------------------- 図1
def fig1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))

    # 左: 座標グリッドと、場所ごとの基底ベクトル
    for r in (1, 2, 3):
        t = np.linspace(0, 2 * np.pi, 400)
        ax1.plot(r * np.cos(t), r * np.sin(t), color=C_GRID, lw=0.8)
    for th in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        ax1.plot([0, 3.3 * np.cos(th)], [0, 3.3 * np.sin(th)], color=C_GRID, lw=0.8)

    pts = [(1, np.deg2rad(30)), (2, np.deg2rad(120)), (2, np.deg2rad(240)),
           (3, np.deg2rad(330)), (1, np.deg2rad(200))]
    for r, th in pts:
        p = r * e_r(th)
        arrow(ax1, p, 0.7 * e_r(th), C_R)
        # e_θ は長さ r なので、見やすさのため 0.7/… ではなく単位化して描く
        eth_unit = e_th(r, th) / r
        arrow(ax1, p, 0.7 * eth_unit, C_TH)
        ax1.plot(*p, "o", color="k", ms=4)

    ax1.set_aspect("equal")
    ax1.set_xlim(-3.6, 3.6)
    ax1.set_ylim(-3.6, 3.6)
    ax1.set_title("基底ベクトルは場所ごとに向きが変わる", fontsize=13)
    ax1.set_xlabel("$x$")
    ax1.set_ylabel("$y$")
    ax1.plot([], [], color=C_R, lw=2.2, label=r"$\mathbf{e}_r$（向きのみ表示）")
    ax1.plot([], [], color=C_TH, lw=2.2, label=r"$\mathbf{e}_\theta/r$（向きのみ表示）")
    ax1.legend(loc="lower left", fontsize=10)

    # 右: θ を dθ 動かしたときの e_θ の変化 -> Γ^r_θθ = -r
    r0, th0, dth = 2.0, np.deg2rad(20), np.deg2rad(40)
    th1 = th0 + dth
    t = np.linspace(th0 - 0.3, th1 + 0.3, 100)
    ax2.plot(r0 * np.cos(t), r0 * np.sin(t), color=C_GRID, lw=1.2)

    p0, p1 = r0 * e_r(th0), r0 * e_r(th1)
    s = 0.55  # 描画上の倍率（e_θ = r * 単位ベクトル）
    v0, v1 = s * e_th(r0, th0), s * e_th(r0, th1)
    arrow(ax2, p0, v0, C_TH)
    arrow(ax2, p1, v1, C_TH)
    ax2.plot(*p0, "ko", ms=4)
    ax2.plot(*p1, "ko", ms=4)
    ax2.text(*(p0 + v0 + [0.04, 0.06]), r"$\mathbf{e}_\theta(\theta)$", color=C_TH, fontsize=12)
    ax2.text(*(p1 + v1 + [-0.05, 0.10]), r"$\mathbf{e}_\theta(\theta+d\theta)$",
             color=C_TH, fontsize=12, ha="center")

    # e_θ(θ+dθ) を p0 に平行移動して、差 Δe_θ を示す
    arrow(ax2, p0, v1, C_TH, lw=1.3, linestyle="--", alpha=0.6)
    diff = v1 - v0
    arrow(ax2, p0 + v0, diff, "#2ca02c", lw=2.6)
    ax2.text(*(p0 + v0 + diff / 2 + [0.10, -0.02]),
             r"$\Delta\mathbf{e}_\theta$", color="#2ca02c", fontsize=13,
             bbox=dict(fc="white", ec="none", pad=1.5))

    # 原点方向（-e_r）の補助
    ax2.plot([0, p0[0]], [0, p0[1]], color=C_R, lw=1, ls=":")
    ax2.plot([0, p1[0]], [0, p1[1]], color=C_R, lw=1, ls=":")
    ax2.plot(0, 0, "ko", ms=4)
    ax2.text(-0.05, -0.28, "原点", fontsize=10, ha="right")
    ax2.add_patch(Arc((0, 0), 1.0, 1.0, theta1=np.rad2deg(th0),
                      theta2=np.rad2deg(th1), color="k", lw=1))
    ax2.text(0.62 * np.cos((th0 + th1) / 2), 0.62 * np.sin((th0 + th1) / 2) - 0.04,
             r"$d\theta$", fontsize=12)

    ax2.set_aspect("equal")
    ax2.set_xlim(-1.4, 3.0)
    ax2.set_ylim(-0.9, 2.9)
    ax2.set_title(r"$\theta$ 方向に動くと $\mathbf{e}_\theta$ は原点側へ傾く", fontsize=13)
    ax2.set_xlabel("$x$")
    ax2.set_ylabel("$y$")
    ax2.text(0.98, 0.02,
             r"$\dfrac{\partial\mathbf{e}_\theta}{\partial\theta}"
             r"=\Gamma^r{}_{\theta\theta}\mathbf{e}_r+\Gamma^\theta{}_{\theta\theta}\mathbf{e}_\theta"
             r"=-r\,\mathbf{e}_r$",
             transform=ax2.transAxes, fontsize=12, va="bottom", ha="right",
             bbox=dict(boxstyle="round", fc="white", ec="#888"))

    fig.tight_layout()
    fig.savefig(OUT / "fig1_polar_basis.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- 図2
def fig2():
    fig = plt.figure(figsize=(12, 5.6))

    # 左: 平面（一周しても元に戻る）
    ax = fig.add_subplot(1, 2, 1)
    tri = np.array([[0, 0], [2, 0], [0, 2], [0, 0]], dtype=float)
    ax.plot(tri[:, 0], tri[:, 1], "k-", lw=1.5)
    v = np.array([0.3, 0.6])
    for p in ([0, 0], [1, 0], [2, 0], [1, 1], [0, 2], [0, 1]):
        arrow(ax, np.array(p, float), v, C_TH)
    ax.set_aspect("equal")
    ax.set_xlim(-0.6, 2.8)
    ax.set_ylim(-0.6, 3.0)
    ax.set_title("平面：一周して戻ると元のベクトルと一致\n（曲率 $=0$）", fontsize=13)
    ax.set_xticks([])
    ax.set_yticks([])

    # 右: 球面の「1/8 球面三角形」
    ax3 = fig.add_subplot(1, 2, 2, projection="3d")
    u, w = np.meshgrid(np.linspace(0, np.pi, 60), np.linspace(0, 2 * np.pi, 120))
    ax3.plot_surface(np.sin(u) * np.cos(w), np.sin(u) * np.sin(w), np.cos(u),
                     color="#dfe8f5", alpha=0.10, linewidth=0, shade=False)
    uo, wo = np.meshgrid(np.linspace(0, np.pi / 2, 30), np.linspace(0, np.pi / 2, 30))
    ax3.plot_surface(np.sin(uo) * np.cos(wo), np.sin(uo) * np.sin(wo), np.cos(uo),
                     color="#f5e6b8", alpha=0.45, linewidth=0, shade=False)

    def sph(th, ph):
        th, ph = np.broadcast_arrays(th, ph)
        return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])

    def south(th, ph):  # 子午線に沿って南向きの単位接ベクトル
        return np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])

    # 経路: 北極 -> (赤道, φ=0) -> (赤道, φ=90°) -> 北極
    s1 = np.linspace(0, np.pi / 2, 60)
    ax3.plot(*sph(s1, 0.0), "k-", lw=2)
    ax3.plot(*sph(np.pi / 2, s1), "k-", lw=2)
    ax3.plot(*sph(s1[::-1], np.pi / 2), "k-", lw=2)

    L, LIFT = 0.34, 1.03  # 矢印は球面のわずか外側に浮かせて、面に埋もれないようにする
    # 子午線 φ=0 を下る（ベクトルは進行方向＝南向き）
    for th in (0.0, np.pi / 4, np.pi / 2):
        p, d = LIFT * sph(th, 0.0), L * south(th, 0.0)
        ax3.quiver(*p, *d, color=C_TH, lw=2.6, arrow_length_ratio=0.35)
    # 赤道を東へ（ベクトルは常に南向き、経路に直交）
    for ph in (np.pi / 4, np.pi / 2):
        p, d = LIFT * sph(np.pi / 2, ph), L * np.array([0, 0, -1.0])
        ax3.quiver(*p, *d, color=C_TH, lw=2.6, arrow_length_ratio=0.35)
    # 子午線 φ=90° を上る（ベクトルは南向き＝進行方向と逆）
    for th in (np.pi / 4, np.pi / 8):
        p, d = LIFT * sph(th, np.pi / 2), L * south(th, np.pi / 2)
        ax3.quiver(*p, *d, color=C_TH, lw=2.6, arrow_length_ratio=0.35)
    # 北極: 出発時のベクトル（青）と帰着時のベクトル（赤）を区別して描く
    pole = LIFT * sph(0.0, 0.0)
    ax3.quiver(*pole, *(1.6 * L * south(0.0, 0.0)), color=C_R, lw=3.4, arrow_length_ratio=0.25)
    ax3.quiver(*pole, *(1.6 * L * south(0.0, np.pi / 2)), color=C_TH, lw=3.4, arrow_length_ratio=0.25)
    ax3.text(0.95, -0.55, 1.12, "出発時", color=C_R, fontsize=11)
    ax3.text(-0.15, 0.55, 1.10, "帰着時", color=C_TH, fontsize=11)

    ax3.text(0, 0, 1.22, "北極", ha="center", fontsize=11)
    ax3.text(1.12, 0, -0.10, "A", fontsize=13)
    ax3.text(0, 1.12, -0.10, "B", fontsize=13)
    ax3.set_box_aspect((1, 1, 1))
    ax3.set_xlim(-1, 1)
    ax3.set_ylim(-1, 1)
    ax3.set_zlim(-1, 1)
    ax3.view_init(elev=28, azim=42)
    ax3.set_axis_off()
    ax3.set_title("球面：北極→A→B→北極と一周すると\nベクトルが $90^\\circ$ 回転して戻る", fontsize=13)

    fig.text(0.5, 0.02,
             "回転角 $=\\int K\\,dA = K\\times$面積 $=\\frac{1}{a^2}\\cdot\\frac{4\\pi a^2}{8}"
             " = \\frac{\\pi}{2}$   （並行移動の回転は曲率 $R^i{}_{jkl}$ が測る）",
             ha="center", fontsize=12)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "fig2_parallel_transport.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- 図3
def fig3():
    fig = plt.figure(figsize=(14, 5.2))
    C1, C2 = "#d62728", "#1f77b4"

    def base(ax, title, sub):
        ax.set_box_aspect((1, 1, 1))
        ax.set_axis_off()
        ax.view_init(elev=24, azim=-58)
        # 3D 軸では set_title が tight_layout で切れやすいので、軸座標に直接置く
        ax.text2D(0.5, 1.02, title, transform=ax.transAxes, ha="center",
                  fontsize=15, fontweight="bold")
        ax.text2D(0.5, 0.94, sub, transform=ax.transAxes, ha="center", fontsize=12.5)

    # 球
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    u, w = np.meshgrid(np.linspace(0, np.pi, 60), np.linspace(0, 2 * np.pi, 120))
    ax.plot_surface(np.sin(u) * np.cos(w), np.sin(u) * np.sin(w), np.cos(u),
                    color="#dfe8f5", alpha=0.6, linewidth=0, shade=True)
    t = np.linspace(-1.0, 1.0, 100)
    ax.plot(np.sin(t), 0 * t, np.cos(t), color=C1, lw=2.4)
    ax.plot(0 * t, np.sin(t), np.cos(t), color=C2, lw=2.4)
    ax.plot([0], [0], [1], "ko")
    base(ax, "球", r"$\kappa_1=\kappa_2=1/a\ \Rightarrow\ K=1/a^2>0$")

    # 円柱
    ax = fig.add_subplot(1, 3, 2, projection="3d")
    u, z = np.meshgrid(np.linspace(0, 2 * np.pi, 120), np.linspace(-1, 1, 30))
    ax.plot_surface(np.cos(u), np.sin(u), z, color="#dfe8f5", alpha=0.6, linewidth=0)
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(t), np.sin(t), 0 * t, color=C1, lw=2.4)  # 円: κ=1/R
    ax.plot([1, 1], [0, 0], [-1, 1], color=C2, lw=2.4)  # 母線: κ=0
    ax.plot([1], [0], [0], "ko")
    base(ax, "円柱", r"$\kappa_1=1/a,\ \kappa_2=0\ \Rightarrow\ K=0$")

    # 鞍面
    ax = fig.add_subplot(1, 3, 3, projection="3d")
    x, y = np.meshgrid(np.linspace(-1, 1, 50), np.linspace(-1, 1, 50))
    ax.plot_surface(x, y, (x**2 - y**2) / 2, color="#dfe8f5", alpha=0.6, linewidth=0)
    t = np.linspace(-1, 1, 100)
    ax.plot(t, 0 * t, t**2 / 2, color=C1, lw=2.4)  # 上に凸でない側（κ>0）
    ax.plot(0 * t, t, -(t**2) / 2, color=C2, lw=2.4)  # κ<0
    ax.plot([0], [0], [0], "ko")
    base(ax, "鞍面", r"$\kappa_1>0,\ \kappa_2<0\ \Rightarrow\ K<0$")

    fig.text(0.5, 0.03,
             r"赤・青の曲線：黒点で曲面に垂直な平面で切った断面（主方向）。"
             r"ガウス曲率 $K=\kappa_1\kappa_2$ は断面の曲がる向きが同じか逆かで符号が決まる",
             ha="center", fontsize=12)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.10, wspace=0.02)
    fig.savefig(OUT / "fig3_principal_curvature.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    print("saved to", OUT)
