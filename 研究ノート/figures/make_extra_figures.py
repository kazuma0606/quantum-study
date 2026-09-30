"""christoffel_riemann_intro.md 用の追加の図（図4〜図8）を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/figures/make_extra_figures.py

出力（このスクリプトと同じ figures/ ディレクトリ）:
    fig4_flat_but_gamma_nonzero.png  一様な場の極座標成分と、共変微分がゼロになること（Part VI §9）
    fig5_sphere_basis_triangle.png   球面の基底ベクトルと、直角3つの球面三角形（Part VIII §13〜）
    fig6_geodesics_sphere.png        球面の測地線と、測地線でない緯線（Part V §6〜8）
    fig7_cylinder_unrolled.png       円柱を切り開くと平面になる（Part VIII §16-e）
    fig8_adm_slicing.png             ADM 分解のラプス・シフトと、ガウス正規座標（付録C）

図1〜3は make_christoffel_figures.py にある。共通の色・矢印の関数はそちらから読み込む。
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

from make_christoffel_figures import C_GRID, C_R, C_TH, OUT, arrow, e_r  # noqa: F401 (rcParams も設定される)

C_GREEN = "#2ca02c"
C_ORANGE = "#ff7f0e"


def sph(th, ph):
    th, ph = np.broadcast_arrays(th, ph)
    return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])


def south(th, ph):
    """余緯度 θ が増える向き（南向き）の単位接ベクトル e_θ/a。"""
    th, ph = np.broadcast_arrays(th, ph)
    return np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])


def east(th, ph):
    """φ が増える向き（東向き）の単位接ベクトル e_φ/(a sinθ)。"""
    ph = np.asarray(ph, dtype=float)
    return np.array([-np.sin(ph), np.cos(ph), 0 * ph])


def faint_sphere(ax, alpha=0.12):
    u, w = np.meshgrid(np.linspace(0, np.pi, 60), np.linspace(0, 2 * np.pi, 120))
    ax.plot_surface(np.sin(u) * np.cos(w), np.sin(u) * np.sin(w), np.cos(u),
                    color="#dfe8f5", alpha=alpha, linewidth=0, shade=False)


def clean3d(ax, elev, azim):
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


def title3d(ax, main, sub=None):
    ax.text2D(0.5, 1.02, main, transform=ax.transAxes, ha="center", fontsize=13.5,
              fontweight="bold")
    if sub:
        ax.text2D(0.5, 0.94, sub, transform=ax.transAxes, ha="center", fontsize=11.5)


# ---------------------------------------------------------------- 図4
def fig4():
    """一様な場 V=(1,0) は平面では一定だが、極座標成分は場所で変わる。共変微分は 0。"""
    fig = plt.figure(figsize=(13.5, 6.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1])

    ax = fig.add_subplot(gs[:, 0])
    t = np.linspace(0, 2 * np.pi, 400)
    for r in (1, 2, 3):
        ax.plot(r * np.cos(t), r * np.sin(t), color=C_GRID, lw=0.8)
    for th in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        ax.plot([0, 3.3 * np.cos(th)], [0, 3.3 * np.sin(th)], color=C_GRID, lw=0.8)
    for r, deg in [(1.5, 35), (1.5, 145), (1.5, 255), (2.6, 80), (2.6, 200), (2.6, 320)]:
        th = np.deg2rad(deg)
        p = r * e_r(th)
        e_t = np.array([-np.sin(th), np.cos(th)])  # 単位 e_θ
        s = 0.85
        arrow(ax, p, s * np.array([1.0, 0.0]), "k", lw=2.8)
        arrow(ax, p, s * np.cos(th) * e_r(th), C_R, lw=1.8)
        arrow(ax, p, s * (-np.sin(th)) * e_t, C_TH, lw=1.8)
        ax.plot(*p, "o", color="k", ms=4)
    ax.set_aspect("equal")
    ax.set_xlim(-3.6, 3.6)
    ax.set_ylim(-3.6, 3.6)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title("平らな平面の一様な場 $V=(1,0)$\n（極座標では成分が場所で変わる）", fontsize=13)
    ax.legend(handles=[
        Line2D([0], [0], color="k", lw=2.8, label=r"$V$（どこでも同じ）"),
        Line2D([0], [0], color=C_R, lw=2, label=r"$e_r$ 方向の成分 $\cos\theta$"),
        Line2D([0], [0], color=C_TH, lw=2, label=r"$e_\theta$ 方向の成分（単位長）$-\sin\theta$"),
    ], loc="lower left", fontsize=9.5)

    th = np.linspace(0, 2 * np.pi, 400)
    d = np.rad2deg(th)
    # r=1 での ∇_θ V^r = ∂_θ V^r + Γ^r_θθ V^θ,  V^r=cosθ, V^θ=-sinθ/r, Γ^r_θθ=-r
    ax1 = fig.add_subplot(gs[0, 1])
    ax1.plot(d, -np.sin(th), "--", color=C_R, lw=2, label=r"$\partial_\theta V^r=-\sin\theta$")
    ax1.plot(d, np.sin(th), "--", color=C_TH, lw=2,
             label=r"$\Gamma^r{}_{\theta\theta}V^\theta=+\sin\theta$")
    ax1.plot(d, 0 * th, "k-", lw=2.6, label=r"和 $\nabla_\theta V^r=0$")
    ax1.set_title(r"$\nabla_\theta V^r=\partial_\theta V^r+\Gamma^r{}_{\theta\theta}V^\theta$"
                  r"   （$r=1$）", fontsize=12)
    ax1.legend(fontsize=9.5, loc="lower left", ncol=1)
    ax1.set_xlim(0, 360)
    ax1.set_xticks(range(0, 361, 90))
    ax1.grid(alpha=0.3)

    # ∇_θ V^θ = ∂_θ V^θ + Γ^θ_{rθ} V^r + Γ^θ_{θθ} V^θ   （Γ^θ_θθ=0）
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.plot(d, -np.cos(th), "--", color=C_R, lw=2, label=r"$\partial_\theta V^\theta=-\cos\theta$")
    ax2.plot(d, np.cos(th), "--", color=C_TH, lw=2,
             label=r"$\Gamma^\theta{}_{r\theta}V^r=+\cos\theta$")
    ax2.plot(d, 0 * th, "k-", lw=2.6, label=r"和 $\nabla_\theta V^\theta=0$")
    ax2.set_title(r"$\nabla_\theta V^\theta=\partial_\theta V^\theta+\Gamma^\theta{}_{r\theta}V^r$"
                  r"   （$r=1$）", fontsize=12)
    ax2.set_xlabel(r"$\theta$ [度]")
    ax2.legend(fontsize=9.5, loc="lower left")
    ax2.set_xlim(0, 360)
    ax2.set_xticks(range(0, 361, 90))
    ax2.grid(alpha=0.3)

    fig.text(0.5, 0.01,
             r"成分の偏微分 $\partial_\theta V^k$ は $0$ でないが、$\Gamma$ の補正項がちょうど打ち消す。"
             r"$\Gamma\neq0$ でも空間は平坦（$V$ は本当に一定）",
             ha="center", fontsize=12)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / "fig4_flat_but_gamma_nonzero.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- 図5
def arc_on_sphere(ax, P, u, v, rad=0.22, color="k", lift=1.03):
    """点 P で 2 つの接ベクトル u, v がなす角の弧を球面上に描く。"""
    s = np.linspace(0, np.pi / 2, 30)
    pts = np.array([P + rad * (np.cos(a) * u + np.sin(a) * v) for a in s])
    pts = lift * pts / np.linalg.norm(pts, axis=1)[:, None]
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=color, lw=2)


def fig5():
    fig = plt.figure(figsize=(13, 6.2))

    # 左: (θ, φ) の格子と基底ベクトル。|e_φ| = a sinθ が極に近づくほど短い
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    faint_sphere(ax, 0.18)
    s = np.linspace(0, 2 * np.pi, 200)
    for deg in (30, 60, 90, 120, 150):
        ax.plot(*sph(np.deg2rad(deg), s), color=C_GRID, lw=0.8)
    s2 = np.linspace(0, np.pi, 100)
    for deg in range(0, 360, 30):
        ax.plot(*sph(s2, np.deg2rad(deg)), color=C_GRID, lw=0.8)
    L, LIFT, ph0 = 0.42, 1.03, np.deg2rad(40)
    for deg in (30, 60, 90):
        th = np.deg2rad(deg)
        p = LIFT * sph(th, ph0)
        ax.quiver(*p, *(L * south(th, ph0)), color=C_R, lw=3, arrow_length_ratio=0.3)
        ax.quiver(*p, *(L * np.sin(th) * east(th, ph0)), color=C_TH, lw=3, arrow_length_ratio=0.3)
        ax.plot(*p, "ko", ms=4)
        # 3D 投影では見かけの長さが変わるので、実際の長さを数値で添える
        tip = p + L * np.sin(th) * east(th, ph0)
        ax.text(*(tip + [0.04, 0.0, 0.03]), rf"$|\mathbf{{e}}_\phi|={np.sin(th):.2f}a$",
                color=C_TH, fontsize=10.5)
    ax.legend(handles=[
        Line2D([0], [0], color=C_R, lw=3, label=r"$\mathbf{e}_\theta$（実際の長さは常に $a$）"),
        Line2D([0], [0], color=C_TH, lw=3, label=r"$\mathbf{e}_\phi$（実際の長さ $a\sin\theta$、極で $0$）"),
    ], loc="lower center", fontsize=10.5, bbox_to_anchor=(0.5, -0.02))
    clean3d(ax, 22, 40)
    title3d(ax, "球面の基底ベクトル", r"$g_{\theta\theta}=a^2,\ \ g_{\phi\phi}=a^2\sin^2\theta$")

    # 右: 直角が3つの球面三角形（1/8 球面）
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    faint_sphere(ax, 0.10)
    uo, wo = np.meshgrid(np.linspace(0, np.pi / 2, 30), np.linspace(0, np.pi / 2, 30))
    ax.plot_surface(np.sin(uo) * np.cos(wo), np.sin(uo) * np.sin(wo), np.cos(uo),
                    color="#f5e6b8", alpha=0.5, linewidth=0, shade=False)
    e = np.linspace(0, np.pi / 2, 60)
    ax.plot(*sph(e, 0.0), "k-", lw=2.2)
    ax.plot(*sph(np.pi / 2, e), "k-", lw=2.2)
    ax.plot(*sph(e, np.pi / 2), "k-", lw=2.2)
    N_, A_, B_ = np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    arc_on_sphere(ax, N_, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), color=C_TH)
    arc_on_sphere(ax, A_, np.array([0, 0, 1.0]), np.array([0, 1.0, 0]), color=C_TH)
    arc_on_sphere(ax, B_, np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), color=C_TH)
    ax.text(0.18, 0.18, 1.12, r"$90^\circ$", color=C_TH, fontsize=12)
    ax.text(1.12, 0.22, 0.12, r"$90^\circ$", color=C_TH, fontsize=12)
    ax.text(0.22, 1.12, 0.12, r"$90^\circ$", color=C_TH, fontsize=12)
    ax.text(0, 0, 1.2, "北極", ha="center", fontsize=11)
    clean3d(ax, 26, 42)
    title3d(ax, "球面三角形：内角の和が $180^\\circ$ を超える",
            r"$90^\circ+90^\circ+90^\circ=270^\circ$")

    fig.text(0.5, 0.02,
             r"超過 $270^\circ-180^\circ=\frac{\pi}{2}=K\times$面積 $=\frac{1}{a^2}\cdot\frac{4\pi a^2}{8}$"
             r"    （平面なら内角の和はちょうど $180^\circ$、曲率 $0$）",
             ha="center", fontsize=12)
    fig.subplots_adjust(left=0.0, right=1.0, top=0.9, bottom=0.08, wspace=0.0)
    fig.savefig(OUT / "fig5_sphere_basis_triangle.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- 図6
def fig6():
    fig = plt.figure(figsize=(13.5, 6.0))

    ax = fig.add_subplot(1, 2, 1, projection="3d")
    faint_sphere(ax, 0.15)
    alpha = np.deg2rad(40)
    s = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(s), np.sin(s), 0 * s, color=C_R, lw=2.6)  # 赤道
    ax.plot(np.cos(s), np.sin(s) * np.cos(alpha), np.sin(s) * np.sin(alpha), color=C_R, lw=2.6)
    th0 = np.pi / 4
    ax.plot(*sph(th0, s), color=C_TH, lw=2.6, ls="--")  # 緯度 45°
    for deg in (240, 285, 330, 15):  # 視点（経度 300°）から見て手前側だけに描く
        ph = np.deg2rad(deg)
        p = 1.03 * sph(th0, ph)
        ax.quiver(*p, *(-0.28 * south(th0, ph)), color=C_TH, lw=2.4, arrow_length_ratio=0.35)
    ax.legend(handles=[
        Line2D([0], [0], color=C_R, lw=2.6, label="測地線（大円）：赤道、傾いた大円"),
        Line2D([0], [0], color=C_TH, lw=2.6, ls="--", label="緯線（北緯 45°）：測地線ではない"),
        Line2D([0], [0], color=C_TH, lw=2.4, label="緯線を保つのに必要な加速度（北向き）"),
    ], loc="lower center", fontsize=9.5, bbox_to_anchor=(0.5, -0.04))
    clean3d(ax, 24, -60)  # 傾いた大円を真横から見ないような視点
    title3d(ax, "球面上の「まっすぐ」な道")

    ax = fig.add_subplot(1, 2, 2)
    ph = np.linspace(0, 2 * np.pi, 400)
    d = np.rad2deg(ph)
    ax.plot(d, 0 * d, color=C_R, lw=2.6, label="赤道（測地線）")
    ax.plot(d, np.rad2deg(np.arctan(np.tan(alpha) * np.sin(ph))), color=C_R, lw=2.6,
            label="傾いた大円（測地線）")
    ax.plot(d, 0 * d + 45, color=C_TH, lw=2.6, ls="--", label="北緯 45° の緯線（測地線ではない）")
    ax.set_xlim(0, 360)
    ax.set_ylim(-60, 75)
    ax.set_xticks(range(0, 361, 60))
    ax.set_xlabel(r"経度 $\phi$ [度]")
    ax.set_ylabel(r"緯度 $90^\circ-\theta$ [度]")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10, loc="lower left")
    ax.set_title(r"座標 $(\phi,\theta)$ の地図：直線に見えても測地線とは限らない", fontsize=12.5)
    ax.text(0.02, 0.98,
            r"測地線方程式 $\ddot\theta=\sin\theta\cos\theta\,\dot\phi^{\,2}$"
            "\n"
            r"緯線は $\ddot\theta=0$ だが $\sin\theta\cos\theta\neq0$ なので満たさない"
            "\n"
            r"（$\theta=\pi/2$ の赤道だけが例外）",
            transform=ax.transAxes, fontsize=10.5, va="top",
            bbox=dict(boxstyle="round", fc="white", ec="#888"))

    fig.text(0.5, 0.015,
             r"保存量（キリングベクトル $\partial_\phi$）：測地線に沿って $a^2\sin^2\theta\,\dot\phi$ は一定",
             ha="center", fontsize=12)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.11, wspace=0.08)
    fig.savefig(OUT / "fig6_geodesics_sphere.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- 図7
def fig7():
    fig = plt.figure(figsize=(13.5, 6.0), constrained_layout=True)
    V = np.array([[0.6, 0.15], [2.6, 0.55], [1.3, 1.25]])  # (s = aφ (a=1), z)
    close = np.vstack([V, V[0]])

    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, z = np.meshgrid(np.linspace(0, 2 * np.pi, 160), np.linspace(-0.1, 1.5, 30))
    ax.plot_surface(np.cos(u), np.sin(u), z, color="#dfe8f5", alpha=0.35, linewidth=0, shade=False)
    ax.plot([1, 1], [0, 0], [-0.1, 1.5], color="k", lw=1.2, ls=":")  # 切り開く線 s=0
    for a, b in zip(close[:-1], close[1:]):
        k = np.linspace(0, 1, 80)
        ss = a[0] + k * (b[0] - a[0])
        zz = a[1] + k * (b[1] - a[1])
        ax.plot(np.cos(ss), np.sin(ss), zz, color=C_R, lw=3)
    for p in V:
        ax.plot([np.cos(p[0])], [np.sin(p[0])], [p[1]], "ko", ms=5)
    ax.set_box_aspect((1, 1, 0.8))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-0.1, 1.5)
    ax.view_init(elev=15, azim=92)  # 三角形の中心（φ≒92°）を正面から見る
    ax.set_axis_off()
    title3d(ax, "円柱の上の三角形", "辺はらせん（測地線）、点線は切り開く線")

    ax = fig.add_subplot(1, 2, 2)
    ax.add_patch(Polygon(V, closed=True, fc="#fbe3e3", ec=C_R, lw=3))
    ax.plot(*V.T, "ko", ms=6)
    ax.plot([0, 0], [-0.1, 1.5], color="k", ls=":", lw=1.4)
    ax.plot([2 * np.pi, 2 * np.pi], [-0.1, 1.5], color="k", ls=":", lw=1.4)
    ax.text(0, 1.55, "切り開く線", ha="center", fontsize=10)
    ax.text(2 * np.pi, 1.55, "同じ線", ha="center", fontsize=10)
    angs = []
    for i in range(3):
        a, b, c = V[i], V[(i + 1) % 3], V[(i - 1) % 3]
        v1, v2 = b - a, c - a
        angs.append(np.degrees(np.arccos(v1 @ v2 / np.linalg.norm(v1) / np.linalg.norm(v2))))
    off = [(-0.28, -0.05), (0.30, -0.02), (0.0, 0.12)]
    for p, ang, o in zip(V, angs, off):
        ax.text(p[0] + o[0], p[1] + o[1], f"{ang:.0f}°", ha="center", va="center",
                fontsize=12, color=C_R)
    ax.set_aspect("equal")
    ax.set_xlim(-0.4, 2 * np.pi + 0.4)
    ax.set_ylim(-0.35, 1.8)
    ax.set_xlabel(r"$s=a\phi$（円周方向に測った長さ）")
    ax.set_ylabel(r"$z$")
    assert abs(sum(angs) - 180) < 1e-9  # 平面の三角形なので必ず 180°
    ax.set_title("切り開いた平面：内角の和 $=180^\\circ$", fontsize=13)
    ax.text(0.98, 0.42,
            r"$g=a^2d\phi^2+dz^2=ds^2+dz^2$" "\n" r"（定数）$\ \Rightarrow\ \Gamma=0,\ R=0$",
            transform=ax.transAxes, ha="right", va="center", fontsize=12,
            bbox=dict(boxstyle="round", fc="white", ec="#888"))

    fig.text(0.5, -0.03,
             "円柱は曲がって見えても、切り開けば距離も角度も変わらない平面：内在的には平坦。"
             "外から見た曲がり方 ($\\kappa_1=1/a$) と内在的な曲率 ($K=0$) は別のもの。"
             "球面は同じ操作で切り開けない ($K\\neq0$)",
             ha="center", fontsize=11.5)
    fig.savefig(OUT / "fig7_cylinder_unrolled.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- 図8
def fig8():
    """(y, t) の平坦な時空図。計量は dy^2 - dt^2、光円錐は 45 度線。"""
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.5, 6.4))

    def h0(y):
        return 0.30 * np.sin(0.9 * y)

    def dh0(y):
        return 0.27 * np.cos(0.9 * y)

    def eta(u, v):
        return u[0] * v[0] - u[1] * v[1]

    # --- 左: ラプスとシフト
    X = np.array([0.9, 1.1])  # 時間の流れ ∂_t（座標時間 dt=1 ぶん）。シフトが見えるよう横にずらす
    yy = np.linspace(-2.6, 2.6, 300)
    ax.plot(yy, h0(yy), color="k", lw=2.4)
    ax.plot(yy, h0(yy - X[0]) + X[1], color="k", lw=2.4)
    ax.text(2.45, h0(2.45) - 0.30, r"$\Sigma_t$", fontsize=14)
    ax.text(2.45, h0(2.45 - X[0]) + X[1] + 0.12, r"$\Sigma_{t+dt}$", fontsize=14)

    y0 = 0.2
    P = np.array([y0, h0(y0)])
    sp = dh0(y0)
    g = np.sqrt(1 - sp**2)
    T = np.array([1.0, sp]) / g   # Σ に接する単位ベクトル（空間的）
    n = np.array([sp, 1.0]) / g   # Σ に垂直な単位ベクトル（時間的）
    N = -eta(X, n)
    beta = eta(X, T)
    assert abs(eta(n, n) + 1) < 1e-12 and abs(eta(T, T) - 1) < 1e-12 and abs(eta(n, T)) < 1e-12
    assert np.allclose(N * n + beta * T, X)

    # 光円錐
    c = 1.35
    ax.fill([P[0], P[0] - c, P[0] + c], [P[1], P[1] + c, P[1] + c], color="#fff2b3", alpha=0.7, zorder=0)
    ax.plot([P[0] - c, P[0], P[0] + c], [P[1] + c, P[1], P[1] + c], color="#c9a800", lw=1.2, zorder=1)
    ax.text(P[0] - 1.05, P[1] + 1.2, "光円錐", color="#8a7400", fontsize=11)

    C_E = "#9467bd"
    arrow(ax, P, T * 0.9, C_E, lw=2, zorder=5)
    ax.text(*(P + T * 0.9 + [0.03, -0.20]), r"$e_i$", color=C_E, fontsize=13)
    arrow(ax, P, N * n, C_GREEN, lw=3, zorder=5)
    ax.text(*(P + N * n / 2 + [-0.55, 0.0]), r"$N\,n$", color=C_GREEN, fontsize=14)
    arrow(ax, P + N * n, beta * T, C_ORANGE, lw=3, zorder=5)
    ax.text(*(P + N * n + beta * T / 2 + [0.55, -0.35]), r"$N^i e_i$", color=C_ORANGE, fontsize=13)
    arrow(ax, P, X, "k", lw=2.4, zorder=6)
    ax.text(*(P + X + [-0.38, 0.16]), r"$\partial_t$", fontsize=15)
    ax.plot(*P, "ko", ms=5, zorder=7)

    ax.set_aspect("equal")
    ax.set_xlim(-2.6, 3.4)
    ax.set_ylim(-0.6, 3.3)
    ax.set_xlabel(r"空間 $y$")
    ax.set_ylabel(r"時間 $t$")
    ax.set_title("ADM 分解：時間の流れ $\\partial_t = N\\,n + N^i e_i$", fontsize=13)
    ax.text(0.02, 0.98,
            r"$N$：ラプス（隣の断面までの固有時間）" "\n"
            r"$N^i$：シフト（断面ごとの座標のずれ）" "\n"
            r"$n$ は $\Sigma_t$ に「垂直」（ローレンツ計量 $dy^2-dt^2$ の意味で。" "\n"
            r"見た目の直角ではなく、45° 線に関して $e_i$ と鏡映）",
            transform=ax.transAxes, fontsize=9.5, va="top",
            bbox=dict(boxstyle="round", fc="white", ec="#888"))

    # --- 右: ガウス正規座標（N=1, N^i=0）：断面から法線方向に測地線
    def s0(y):
        return 0.4 * y**2

    tau = 0.8
    yy = np.linspace(-1.2, 1.2, 200)
    bx.plot(yy, s0(yy), color="k", lw=2.4)
    y0s = np.linspace(-1.1, 1.1, 9)
    ends = []
    for y_ in y0s:
        sl = 0.8 * y_
        nn = np.array([sl, 1.0]) / np.sqrt(1 - sl**2)
        p0 = np.array([y_, s0(y_)])
        p1 = p0 + tau * nn
        bx.plot([p0[0], p1[0]], [p0[1], p1[1]], color=C_GREEN, lw=1.8)
        ends.append(p1)
    ends = np.array(ends)
    bx.plot(ends[:, 0], ends[:, 1], color="k", lw=2.4, ls="--")
    for p in np.vstack([np.array([[y_, s0(y_)] for y_ in y0s]), ends]):
        bx.plot(*p, "ko", ms=3.5)
    bx.text(1.3, s0(1.2) - 0.30, r"$\Sigma$  ($t=0$)", fontsize=13)
    bx.text(ends[-1, 0] + 0.12, ends[-1, 1] - 0.05, r"$t=\tau$", fontsize=13)
    # 隣り合う 2 本の間隔の比較（中央付近）
    i = 4
    bx.annotate("", xy=(y0s[i + 1], s0(y0s[i + 1]) - 0.12), xytext=(y0s[i], s0(y0s[i]) - 0.12),
                arrowprops=dict(arrowstyle="<->", color=C_TH, lw=2))
    bx.annotate("", xy=(ends[i + 1, 0], ends[i + 1, 1] + 0.12), xytext=(ends[i, 0], ends[i, 1] + 0.12),
                arrowprops=dict(arrowstyle="<->", color=C_TH, lw=2))
    bx.text((y0s[i] + y0s[i + 1]) / 2, s0(y0s[i]) - 0.32, r"$g_{ij}(0)$", color=C_TH,
            fontsize=12, ha="center")
    bx.text((ends[i, 0] + ends[i + 1, 0]) / 2, ends[i, 1] + 0.26, r"$g_{ij}(\tau)$（広い）",
            color=C_TH, fontsize=12, ha="center", bbox=dict(fc="white", ec="none", pad=1.5))
    bx.set_aspect("equal")
    bx.set_xlim(-3.0, 3.6)
    bx.set_ylim(-0.7, 2.8)
    bx.set_xlabel(r"空間 $y$")
    bx.set_ylabel(r"時間 $t$")
    bx.set_title("ガウス正規座標（$N=1,\\ N^i=0$）：法線方向の測地線", fontsize=13)
    bx.text(0.02, 0.98,
            r"隣り合う測地線の間隔が広がる" "\n"
            r"$\Rightarrow\ \partial_t g_{ij}>0\ \Rightarrow\ K_{ij}=-\frac{1}{2}\partial_t g_{ij}<0$",
            transform=bx.transAxes, fontsize=11.5, va="top",
            bbox=dict(boxstyle="round", fc="white", ec="#888"))

    fig.tight_layout()
    fig.savefig(OUT / "fig8_adm_slicing.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    fig4()
    fig5()
    fig6()
    fig7()
    fig8()
    print("saved to", OUT)
