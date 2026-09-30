"""付録A・B・C 用の図（図14〜図22）を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/figures/make_appendix_figures.py

出力（figures/）:
  付録A
    fig14_gauss_weingarten.png     ガウスの公式（r_ij の分解）とヴァインガルテンの公式（n_i は接平面内）
    fig15_gauss_codazzi_flow.png   3階微分を2通りで計算 → ガウス方程式・コダッツィ方程式
  付録B
    fig16_torus_curvature.png      トーラスのガウス曲率（K>0, K=0, K<0 の領域）
    fig17_integrability.png        可積分条件：長方形を2通りの経路で回ると Φ は一致するか
    fig18_bonnet_uniqueness.png    g だけでは曲面が決まらない例と、(g, L) で決まること
  付録C
    fig19_spacelike_hypersurface.png  空間的超曲面（ε=-1）と時間的超曲面（ε=+1）
    fig20_sphere_vs_hyperboloid.png   球面（ε=+1, K>0）と双曲面（ε=-1, K<0）
    fig21_constraint_blocks.png       拘束条件と発展方程式：アインシュタインテンソルの成分の分解
    fig22_cauchy_problem.png          初期値問題：初期データと因果領域

記号・式は christoffel_riemann_intro.md の本文と同じ。図の数値（曲面上のベクトルなど）は
スクリプト内で実際に計算し、本文の公式（ガウスの公式・ヴァインガルテンの公式など）が
成り立つことを assert で確認してから描いている。
色の約束：曲率の符号は発散配色（青＝負、灰＝0、赤＝正）。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Arc, FancyArrowPatch, Polygon, Rectangle
from scipy.linalg import expm

from index_typeset import Canvas, LETTER
from make_christoffel_figures import OUT

# 発散配色（青↔赤、中間は灰色 #f0efec）。K<0 が青、K>0 が赤。
BLUE, RED, NEUTRAL = "#184f95", "#b02a2f", "#f0efec"
DIV = LinearSegmentedColormap.from_list("div", [BLUE, "#86b6ef", NEUTRAL, "#ef9f99", RED])

C_R1, C_R2, C_N = "#1f77b4", "#2ca02c", "#9467bd"   # r_1, r_2, n
C_TAN, C_NOR = "#e67e00", "#9467bd"                 # 接線成分（橙）、法線成分（紫）
C_TIME, C_SPACE, C_NULL = "#2563a8", "#c2410c", "#8a7400"


def arrow3d(ax, p, v, color, lw=2.6, ratio=0.22, **kw):
    ax.quiver(*p, *v, color=color, lw=lw, arrow_length_ratio=ratio, **kw)


# ======================================================================== 図14
def fig14():
    # 曲面 z = f(x, y)。r(x,y) = (x, y, f)、r_1 = (1,0,f_x)、r_2 = (0,1,f_y)、r_ij = (0,0,f_ij)
    def f(x, y):
        return 0.45 * x**2 + 0.25 * y**2 + 0.2 * x * y

    def derivs(x, y):
        fx, fy = 0.9 * x + 0.2 * y, 0.5 * y + 0.2 * x
        return fx, fy, 0.9, 0.2, 0.5  # fx, fy, fxx, fxy, fyy

    def frame(x, y):
        fx, fy, fxx, fxy, fyy = derivs(x, y)
        r1, r2 = np.array([1, 0, fx]), np.array([0, 1, fy])
        n = np.array([-fx, -fy, 1.0])
        n /= np.linalg.norm(n)
        rij = {(1, 1): np.array([0, 0, fxx]), (1, 2): np.array([0, 0, fxy]), (2, 2): np.array([0, 0, fyy])}
        return r1, r2, n, rij

    x0, y0 = 0.90, 0.20
    P = np.array([x0, y0, f(x0, y0)])
    r1, r2, n, rij = frame(x0, y0)
    g = np.array([[r1 @ r1, r1 @ r2], [r2 @ r1, r2 @ r2]])
    ginv = np.linalg.inv(g)
    L = {k: v @ n for k, v in rij.items()}
    L11 = L[(1, 1)]
    # ガウスの公式: r_11 = Γ^k_11 r_k + L_11 n。接線成分を r_1, r_2 で展開して Γ を求める
    tan11 = rij[(1, 1)] - L11 * n
    coef = ginv @ np.array([tan11 @ r1, tan11 @ r2])  # Γ^k_11
    assert np.allclose(coef[0] * r1 + coef[1] * r2, tan11), "ガウスの公式（接線成分）が成り立たない"
    assert abs(tan11 @ n) < 1e-12
    # ヴァインガルテンの公式: n_1 = -L_1^k r_k （n を x 方向に有限差分で微分して確認）
    h = 1e-6
    n_plus = frame(x0 + h, y0)[2]
    n_minus = frame(x0 - h, y0)[2]
    n1 = (n_plus - n_minus) / (2 * h)
    L1k = ginv @ np.array([L[(1, 1)], L[(1, 2)]])  # L_1^k = g^{jk} L_{1j}
    wein = -(L1k[0] * r1 + L1k[1] * r2)
    assert np.allclose(n1, wein, atol=1e-5), "ヴァインガルテンの公式が成り立たない"
    assert abs(n1 @ n) < 1e-6

    fig = plt.figure(figsize=(14, 5.6))

    XR, YR = (0.0, 1.7), (-0.5, 0.95)

    def patch(ax, alpha=0.30):
        xs, ys = np.meshgrid(np.linspace(*XR, 40), np.linspace(*YR, 40))
        ax.plot_surface(xs, ys, f(xs, ys), color="#cfe0f5", alpha=alpha, linewidth=0, shade=False, zorder=0)
        for yy in np.linspace(*YR, 7):
            xx = np.linspace(*XR, 60)
            ax.plot(xx, 0 * xx + yy, f(xx, yy), color="#9ab5d6", lw=0.7)
        for xx in np.linspace(*XR, 9):
            yy = np.linspace(*YR, 60)
            ax.plot(0 * yy + xx, yy, f(xx, yy), color="#9ab5d6", lw=0.7)

    def clean(ax):
        ax.set_axis_off()
        ax.set_box_aspect((1.45, 1.25, 1.0), zoom=1.22)
        ax.set_xlim(*XR)
        ax.set_ylim(*YR)
        ax.set_zlim(0, 1.9)
        ax.view_init(elev=22, azim=-62)

    def tangent_plane(ax, P, r1, r2, half=0.42):
        aa, bb = np.meshgrid(np.linspace(-half, half, 3), np.linspace(-half, half, 3))
        Q = P[:, None, None] + aa * r1[:, None, None] + bb * r2[:, None, None]
        ax.plot_surface(Q[0], Q[1], Q[2], color="#ffe9a8", alpha=0.45, linewidth=0, shade=False)

    def legend2d(ax, lines):
        for k, (txt, col) in enumerate(lines):
            ax.text2D(0.02, 0.10 - 0.055 * k, txt, transform=ax.transAxes, color=col, fontsize=12.5)

    # ---- 左: ガウスの公式
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    patch(ax)
    tangent_plane(ax, P, r1, r2)
    s = 0.55
    arrow3d(ax, P, s * r1, C_R1)
    arrow3d(ax, P, s * r2, C_R2)
    arrow3d(ax, P, 0.55 * n, C_N)
    k11 = 0.62
    vec11 = k11 * rij[(1, 1)]
    arrow3d(ax, P, vec11, "k", lw=3.4)
    arrow3d(ax, P, k11 * tan11, C_TAN, lw=3.2)
    arrow3d(ax, P + k11 * tan11, k11 * L11 * n, C_NOR, lw=3.2)
    ax.plot([P[0] + vec11[0], P[0] + k11 * tan11[0]], [P[1] + vec11[1], P[1] + k11 * tan11[1]],
            [P[2] + vec11[2], P[2] + k11 * tan11[2]], color="#888", lw=1.0, ls=":")
    ax.plot(*P, "ko", ms=5)
    ax.text(*(P + s * r1 + [0.05, 0, 0.0]), r"$\mathbf{r}_1$", color=C_R1, fontsize=17)
    ax.text(*(P + s * r2 + [0, 0.05, 0.0]), r"$\mathbf{r}_2$", color=C_R2, fontsize=17)
    ax.text(*(P + 0.55 * n + [-0.08, 0.0, 0.05]), r"$\mathbf{n}$", color=C_N, fontsize=17)
    ax.text(*(P + vec11 + [-0.12, 0.0, 0.03]), r"$\mathbf{r}_{11}$", color="k", fontsize=17)
    clean(ax)
    legend2d(ax, [(r"■ $\mathbf{r}_{11}$（2階微分）", "k"),
                  (r"■ $\Gamma^k{}_{11}\mathbf{r}_k$（接線成分）", C_TAN),
                  (r"■ $L_{11}\,\mathbf{n}$（法線成分）", C_NOR)])
    ax.set_title("ガウスの公式：2階微分 $\\mathbf{r}_{ij}$ を、接線成分と法線成分に分ける\n"
                 r"$\mathbf{r}_{ij}=\Gamma^k{}_{ij}\mathbf{r}_k+L_{ij}\mathbf{n}$", fontsize=13.5)

    # ---- 右: ヴァインガルテンの公式
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    patch(ax)
    tangent_plane(ax, P, r1, r2)
    for xk in (0.25, 0.6, 1.25, 1.55):
        Pk = np.array([xk, y0, f(xk, y0)])
        nk = frame(xk, y0)[2]
        arrow3d(ax, Pk, 0.5 * nk, C_N, lw=2.2, ratio=0.28)
        ax.plot(*Pk, "o", color="#555", ms=3.5)
    xs = np.linspace(0.1, 1.65, 60)
    ax.plot(xs, 0 * xs + y0, f(xs, y0), color="k", lw=2.0)
    ax.text(1.62, y0, f(1.62, y0) + 0.22, r"$u^1$ 曲線", fontsize=12)
    arrow3d(ax, P, 0.55 * n, C_N, lw=3.2)
    arrow3d(ax, P, 0.55 * wein, C_TAN, lw=3.4)
    ax.plot(*P, "ko", ms=5)
    ax.text(*(P + 0.55 * n + [-0.05, 0.0, 0.06]), r"$\mathbf{n}$", color=C_N, fontsize=17)
    ax.text(*(P + 0.55 * wein + [-0.02, -0.05, -0.12]), r"$\mathbf{n}_1$", color=C_TAN, fontsize=17)
    clean(ax)
    legend2d(ax, [(r"■ $\mathbf{n}$（単位法線）", C_N),
                  (r"■ $\mathbf{n}_1=-L_1{}^k\mathbf{r}_k$（接平面の中）", C_TAN)])
    ax.set_title("ヴァインガルテンの公式：$\\mathbf{n}$ の変化 $\\mathbf{n}_i$ は接平面の中に収まる\n"
                 r"$\mathbf{n}\cdot\mathbf{n}=1\ \Rightarrow\ \mathbf{n}_i\perp\mathbf{n}$、$\mathbf{n}_i=-L_i{}^k\mathbf{r}_k$", fontsize=13.5)

    fig.text(0.5, 0.025,
             rf"図の数値（点 $P$）：$L_{{11}}={L11:.3f}$、$\Gamma^1{{}}_{{11}}={coef[0]:.3f},\ \Gamma^2{{}}_{{11}}={coef[1]:.3f}$。"
             "黄色は接平面。ガウスの公式（$\\mathbf{r}_{11}$ の分解）とヴァインガルテンの公式（$\\mathbf{n}_1$）が成り立つことを数値で確認して描いた。",
             ha="center", fontsize=11.5)
    fig.subplots_adjust(left=0.0, right=1.0, top=0.86, bottom=0.08, wspace=0.0)
    fig.savefig(OUT / "fig14_gauss_weingarten.png", dpi=150)
    plt.close(fig)


# ======================================================================== 図15
def fig15():
    cv = Canvas(1500, 1250)
    EC = "#3b6fb6"
    GRAY = "#444444"

    def m(s, col=GRAY):
        return (s, col, "m")

    cv.card(30, 1210, 1440, 250, "A-2・A-3　出発点：2階微分の分解と、法線の微分", ec=EC)
    cv.rich(70, 1080, [("ガウスの公式（A-2）", GRAY), ("　", GRAY),
                       m(r"\mathbf{r}_{ij}=\Gamma^k{}_{ij}\,\mathbf{r}_k\,+\,L_{ij}\,\mathbf{n}", "k")], size=21)
    cv.rich(70, 1020, [("接する方向（内部の量 ", GRAY), m(r"\Gamma", C_TAN), ("）と、法線方向（外から見た量 ", GRAY),
                       m(r"L", C_NOR), ("）に分かれる", GRAY)], size=15)
    cv.rich(800, 1080, [("ヴァインガルテンの公式（A-3）", GRAY), ("　", GRAY), m(r"\mathbf{n}_i=-L_i{}^k\,\mathbf{r}_k", "k")], size=21)
    cv.rich(800, 1020, [(r"\mathbf{n}_i", GRAY, "m"), (" は接する方向だけ（法線成分なし）", GRAY)], size=15)

    cv.arrow((750, 955), (750, 900), GRAY, lw=2.6, ms=20)
    cv.rich(770, 925, [("もう一段微分して、A-2・A-3 を代入する", GRAY)], size=15)

    cv.card(30, 890, 1440, 330, "A-4　3階微分を、順序を変えた2通りで計算する", ec=EC)
    cv.rich(70, 770, [m(r"\mathbf{r}_{ijl}=\partial_l(\mathbf{r}_{ij})", GRAY), ("　", GRAY)], size=17)
    x = cv.rich(70, 720, [m(r"[\partial_l\Gamma^m{}_{ij}+\Gamma^k{}_{ij}\Gamma^m{}_{kl}-L_{ij}L_l{}^m]\,\mathbf{r}_m", C_TAN)],
                size=17)
    cv.rich(x + 12, 720, [m(r"+\ [\Gamma^k{}_{ij}L_{kl}+\partial_lL_{ij}]\,\mathbf{n}", C_NOR)], size=17)
    cv.rich(70, 660, [m(r"\mathbf{r}_{ilj}=\partial_j(\mathbf{r}_{il})", GRAY)], size=17)
    x = cv.rich(70, 610, [m(r"[\partial_j\Gamma^m{}_{il}+\Gamma^k{}_{il}\Gamma^m{}_{kj}-L_{il}L_j{}^m]\,\mathbf{r}_m", C_TAN)],
                size=17)
    cv.rich(x + 12, 610, [m(r"+\ [\Gamma^k{}_{il}L_{kj}+\partial_jL_{il}]\,\mathbf{n}", C_NOR)], size=17)

    cv.arrow((750, 555), (750, 500), GRAY, lw=2.6, ms=20)
    cv.rich(770, 525, [("混合偏微分の対称性（A-5）：", GRAY), m(r"\mathbf{r}_{ijl}=\mathbf{r}_{ilj}", "k"),
                       ("　→ 基底 ", GRAY), m(r"\{\mathbf{r}_1,\mathbf{r}_2,\mathbf{n}\}", GRAY),
                       (" ごとに係数が一致", GRAY)], size=15)

    cv.card(30, 490, 700, 330, "A-6　接する方向の係数どうしが一致", ec=C_TAN, lw=4)
    cv.rich(60, 350, [("左辺が ", GRAY), m(r"R^m{}_{ilj}", C_TAN), (" になり、", GRAY)], size=15)
    cv.rich(60, 290, [m(r"R^m{}_{ilj}=L_{ij}L_l{}^m-L_{il}L_j{}^m", C_TAN)], size=23)
    cv.rich(60, 230, [("ガウス方程式：内部の曲率 ", GRAY), m(r"R", C_TAN), (" を、外から見た量 ", GRAY), m(r"L", C_NOR),
                      (" で表す", GRAY)], size=15)
    cv.rich(60, 195, [("（ここから ", GRAY), m(r"K=R_{\theta\phi\theta\phi}/\det g", GRAY), ("、ガウスの驚異の定理）", GRAY)], size=14)

    cv.card(770, 490, 700, 330, "A-7　法線方向の係数どうしが一致", ec=C_NOR, lw=4)
    cv.rich(800, 350, [("移項して整理すると、", GRAY)], size=15)
    cv.rich(800, 290, [m(r"\partial_lL_{ij}-\partial_jL_{il}=\Gamma^k{}_{il}L_{kj}-\Gamma^k{}_{ij}L_{kl}", C_NOR)], size=20)
    cv.rich(800, 230, [("コダッツィ・マイナルディ方程式：", GRAY), m(r"L_{ij}", C_NOR), (" は勝手な値を取れない", GRAY)], size=15)
    cv.rich(800, 195, [("（付録B で、曲面が存在する条件として使う）", GRAY)], size=14)

    cv.save("fig15_gauss_codazzi_flow.png")


# ======================================================================== 図16
def fig16():
    a, b = 1.0, 2.4
    kmax = 0.85
    norm = Normalize(-kmax, kmax)

    def Kfun(th):
        return np.cos(th) / (a * (b + a * np.cos(th)))

    fig = plt.figure(figsize=(15.5, 6.6))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.35, 1.0, 1.0], hspace=0.42, wspace=0.28)

    # ---- 3D トーラス（一部を切り取って断面を見せる）
    ax = fig.add_subplot(gs[:, 0], projection="3d")
    th = np.linspace(-np.pi, np.pi, 140)
    ph = np.linspace(0.55, 2 * np.pi, 160)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    rho = b + a * np.cos(TH)
    X, Y, Z = rho * np.cos(PH), rho * np.sin(PH), a * np.sin(TH)
    fc = DIV(norm(Kfun(TH)))
    ax.plot_surface(X, Y, Z, facecolors=fc, rstride=1, cstride=1, linewidth=0, antialiased=False, shade=True)
    for sgn in (+1, -1):  # K=0 の円周（θ=±π/2）
        p = np.linspace(0.55, 2 * np.pi, 200)
        ax.plot(b * np.cos(p), b * np.sin(p), sgn * a + 0 * p, color="k", lw=1.8, ls="--")
    t = np.linspace(-np.pi, np.pi, 100)
    ax.plot((b + a * np.cos(t)) * np.cos(0.55), (b + a * np.cos(t)) * np.sin(0.55), a * np.sin(t), color="k", lw=1.6)
    ax.set_box_aspect((1, 1, 0.42), zoom=1.25)
    ax.set_axis_off()
    ax.view_init(elev=38, azim=-62)
    ax.set_xlim(-b - a, b + a)
    ax.set_ylim(-b - a, b + a)
    ax.set_zlim(-1.6, 1.6)
    ax.set_title("トーラスをガウス曲率 $K$ で色分け", fontsize=13.5)
    sm = ScalarMappable(norm=norm, cmap=DIV)
    cb = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.03, aspect=18, location="bottom")
    cb.set_label(r"$K=\dfrac{\cos\theta}{a\,(b+a\cos\theta)}$　（$a=1,\ b=2.4$）", fontsize=11.5)
    ax.text2D(0.0, 0.93, "赤：$K>0$（外側）", color=RED, fontsize=12.5, transform=ax.transAxes)
    ax.text2D(0.0, 0.88, "青：$K<0$（内側）", color=BLUE, fontsize=12.5, transform=ax.transAxes)
    ax.text2D(0.0, 0.83, "黒の破線：$K=0$（上端・下端）", color="k", fontsize=12.5, transform=ax.transAxes)

    # ---- 断面（φ = const）
    bx = fig.add_subplot(gs[:, 1])
    tt = np.linspace(-np.pi, np.pi, 400)
    cx, cy = b + a * np.cos(tt), a * np.sin(tt)
    for i in range(len(tt) - 1):
        bx.plot(cx[i:i + 2], cy[i:i + 2], color=DIV(norm(Kfun(tt[i]))), lw=7, solid_capstyle="butt")
    bx.axvline(0, color="#777", lw=1.6, ls="-.")
    bx.text(0.1, 1.75, "回転軸", fontsize=11, color="#555")
    th0 = np.deg2rad(50)
    Pp = np.array([b + a * np.cos(th0), a * np.sin(th0)])
    bx.plot(b, 0, "ko", ms=4)
    bx.plot([b, Pp[0]], [0, Pp[1]], color="k", lw=1.4)
    bx.text(b + 0.05, 0.52, r"$a$", fontsize=15)
    bx.plot([0, b], [-0.08, -0.08], color="#333", lw=1.4)
    bx.text(b / 2, -0.38, r"$b$", fontsize=15, ha="center")
    bx.plot([0, Pp[0]], [Pp[1], Pp[1]], color="#333", lw=1.2, ls=":")
    bx.text(Pp[0] * 0.35, Pp[1] + 0.1, r"$\rho$", fontsize=15, ha="center")
    bx.add_patch(Arc((b, 0), 0.9, 0.9, theta1=0, theta2=50, color="k", lw=1.3))
    bx.text(b + 0.55, 0.12, r"$\theta$", fontsize=14)
    n_dir = np.array([np.cos(th0), np.sin(th0)])
    bx.add_patch(FancyArrowPatch(Pp, Pp + 0.75 * n_dir, arrowstyle="-|>", mutation_scale=16, color=C_N, lw=2.6))
    bx.text(*(Pp + 0.83 * n_dir + [0.05, 0.02]), r"$\mathbf{n}$", color=C_N, fontsize=16)
    bx.text(b + a + 0.15, -0.05, "外側\n$\\theta=0$\n$K>0$", color=RED, fontsize=12, va="center")
    bx.text(b - a - 0.15, -0.95, "内側\n$\\theta=\\pi$\n$K<0$", color=BLUE, fontsize=12, va="center", ha="right")
    bx.text(b, a + 0.68, "上端 $\\theta=\\pi/2$：$K=0$", fontsize=12, ha="center", va="bottom")
    bx.text(b, -a - 0.68, "下端 $\\theta=-\\pi/2$：$K=0$", fontsize=12, ha="center", va="top")
    bx.set_aspect("equal")
    bx.set_xlim(-0.3, b + a + 1.4)
    bx.set_ylim(-2.1, 2.1)
    bx.axis("off")
    bx.set_title("断面（$\\phi$ 一定）\n" r"$\rho=b+a\cos\theta,\ \ \kappa_1=-\dfrac{1}{a},\ \ \kappa_2=-\dfrac{\cos\theta}{\rho}$",
                 fontsize=12.5)

    # ---- K(θ) と K√g
    cx1 = fig.add_subplot(gs[0, 2])
    tth = np.linspace(-np.pi, np.pi, 500)
    K = Kfun(tth)
    cx1.axhline(0, color="#777", lw=1)
    cx1.fill_between(tth, 0, K, where=K >= 0, color="#ef9f99", alpha=0.8, lw=0)
    cx1.fill_between(tth, 0, K, where=K < 0, color="#86b6ef", alpha=0.8, lw=0)
    cx1.plot(tth, K, color="k", lw=1.8)
    cx1.set_xlim(-np.pi, np.pi)
    cx1.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    cx1.set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])
    cx1.set_title(r"ガウス曲率 $K(\theta)$：内側ほど大きく負", fontsize=12)
    cx1.set_ylabel(r"$K$")
    cx2 = fig.add_subplot(gs[1, 2])
    Kdens = np.cos(tth)  # K * sqrt(det g) = cosθ
    assert np.allclose(Kfun(tth) * a * (b + a * np.cos(tth)), Kdens)
    cx2.axhline(0, color="#777", lw=1)
    cx2.fill_between(tth, 0, Kdens, where=Kdens >= 0, color="#ef9f99", alpha=0.8, lw=0)
    cx2.fill_between(tth, 0, Kdens, where=Kdens < 0, color="#86b6ef", alpha=0.8, lw=0)
    cx2.plot(tth, Kdens, color="k", lw=1.8)
    cx2.set_xlim(-np.pi, np.pi)
    cx2.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    cx2.set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])
    cx2.set_xlabel(r"$\theta$")
    cx2.set_ylabel(r"$K\sqrt{\det g}$")
    cx2.set_title("面積で重みを付けると $K\\sqrt{\\det g}=\\cos\\theta$\n正負がちょうど打ち消し合う", fontsize=11.5)
    cx2.text(0.0, -0.55, "$\\int\\!\\!\\int K\\,dA=0=2\\pi\\chi\\ (\\chi=0)$", ha="center", fontsize=11.5,
             bbox=dict(boxstyle="round", fc="white", ec="#888"))

    fig.savefig(OUT / "fig16_torus_curvature.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ======================================================================== 図17
def fig17():
    def K_(axis):
        m = np.zeros((3, 3))
        i, j = [(1, 2), (2, 0), (0, 1)][axis]
        m[i, j], m[j, i] = -1.0, 1.0
        return m

    u1 = u2 = 1.1
    cases = [
        ("$A_1,\\,A_2$ が可換でない（例：$x$ 軸まわりと $y$ 軸まわりの回転）", 1.0 * K_(0), 1.0 * K_(1)),
        ("$A_1,\\,A_2$ が可換（例：どちらも $z$ 軸まわりの回転）", 1.0 * K_(2), 0.6 * K_(2)),
    ]
    fig = plt.figure(figsize=(13.5, 8.6))
    for c, (title, A1, A2) in enumerate(cases):
        Om = A1 @ A2 - A2 @ A1  # 定数行列なので Ω_12 = ∂_2A_1 - ∂_1A_2 + [A_1, A_2] = [A_1, A_2]
        Phi_a = expm(u2 * A2) @ expm(u1 * A1)  # 経路1: u^1 方向に進んでから u^2 方向
        Phi_b = expm(u1 * A1) @ expm(u2 * A2)  # 経路2: u^2 方向に進んでから u^1 方向
        diff = np.linalg.norm(Phi_a - Phi_b)
        assert (np.linalg.norm(Om) > 1e-9) == (diff > 1e-9), "Ω_12 ≠ 0 と経路依存性が対応しない"

        ax = fig.add_subplot(2, 2, 1 + c)
        ax.add_patch(Rectangle((0, 0), 1, 1, fc="#f6f8fc", ec="#8aa0c8", lw=1.5, zorder=0))

        def seg(p, q, col, off=(0, 0)):
            ax.add_patch(FancyArrowPatch((p[0] + off[0], p[1] + off[1]), (q[0] + off[0], q[1] + off[1]),
                                         arrowstyle="-|>", mutation_scale=20, color=col, lw=3.2, zorder=3))

        seg((0.02, -0.03), (0.98, -0.03), C_R1)
        seg((1.03, 0.02), (1.03, 0.98), C_R1)
        seg((-0.03, 0.02), (-0.03, 0.98), C_TAN)
        seg((0.02, 1.03), (0.98, 1.03), C_TAN)
        ax.plot(0, 0, "ko", ms=6)
        ax.plot(1, 1, "ko", ms=6)
        ax.text(-0.09, -0.13, r"$\Phi_0$", fontsize=15)
        ax.text(0.5, -0.17, r"$\partial_1\Phi=A_1\Phi$", color=C_R1, ha="center", fontsize=13)
        ax.text(1.09, 0.5, r"$\partial_2\Phi=A_2\Phi$", color=C_R1, va="center", fontsize=13)
        ax.text(-0.09, 0.5, r"$\partial_2\Phi=A_2\Phi$", color=C_TAN, va="center", ha="right", fontsize=13)
        ax.text(0.5, 1.09, r"$\partial_1\Phi=A_1\Phi$", color=C_TAN, ha="center", fontsize=13)
        ax.text(1.08, 1.06, r"$\Phi_a$（青の経路）", color=C_R1, fontsize=13)
        ax.text(1.08, 0.96, r"$\Phi_b$（橙の経路）", color=C_TAN, fontsize=13, va="top")
        ax.set_xlim(-0.75, 1.9)
        ax.set_ylim(-0.32, 1.25)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_xlabel("")
        ax.set_title(title, fontsize=13)
        ax.text(0.5, 0.5, r"$u^2$" + "\n↑\n" + r"$\to\ u^1$", ha="center", va="center", fontsize=13, color="#888")

        bx = fig.add_subplot(2, 2, 3 + c, projection="3d")
        cols = ["#d62728", "#2ca02c", "#1f77b4"]
        for k in range(3):
            v = Phi_a[:, k]
            bx.quiver(0, 0, 0, *v, color=cols[k], lw=5, arrow_length_ratio=0.15, alpha=0.75)
        for k in range(3):
            v = Phi_b[:, k]
            bx.quiver(0, 0, 0, *v, color="k", lw=1.6, arrow_length_ratio=0.12)
        bx.set_xlim(-1, 1)
        bx.set_ylim(-1, 1)
        bx.set_zlim(-1, 1)
        bx.set_box_aspect((1, 1, 1), zoom=1.45)
        bx.view_init(elev=20, azim=35)
        bx.set_axis_off()
        verdict = ("経路で結果が違う → 解 $\\Phi$ は存在しない" if diff > 1e-9 else "経路によらず一致 → 解 $\\Phi$ が存在する（B-5）")
        bx.set_title(f"$\\Omega_{{12}}=[A_1,A_2]$ {'≠' if diff > 1e-9 else '='} 0：{verdict}\n"
                     f"（太い色の3本＝$\\Phi_a$ の列、細い黒の3本＝$\\Phi_b$ の列、差 $\\|\\Phi_a-\\Phi_b\\|={diff:.2f}$）", fontsize=12.5)
    fig.text(0.5, 0.045,
             r"$\Omega_{12}=\partial_2A_1-\partial_1A_2+[A_1,A_2]=0$ が、長方形を2通りの経路で回っても $\Phi$ が食い違わない条件"
             "（$A_1,A_2$ が定数の例。赤・緑・青は $\\Phi$ の第1・2・3列）。",
             ha="center", fontsize=11)
    fig.text(0.5, 0.012, "曲面の場合は、この条件がガウス方程式とコダッツィ方程式になる（B-4-2）。", ha="center", fontsize=12)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.10, hspace=0.12, wspace=0.05)
    fig.savefig(OUT / "fig17_integrability.png", dpi=150)
    plt.close(fig)


# ======================================================================== 図18
def fig18():
    c = 1.0

    def plane(s, z):
        return np.array([s, z, 0 * s])

    def cyl(s, z):
        return np.array([c * np.cos(s / c), c * np.sin(s / c), z])

    Rz = expm(0.6 * np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]]))
    Rx = expm(0.9 * np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]]))
    Rm = Rx @ Rz
    shift = np.array([0.3, 0.5, 0.2])

    def moved(s, z):
        p = cyl(s, z)
        sh = p.shape
        q = (Rm @ p.reshape(3, -1)).reshape(sh)
        return q + shift.reshape(3, *([1] * (len(sh) - 1)))

    def normal(kind, s):
        if kind == "plane":
            return np.array([0.0, 0.0, 1.0])
        n = np.array([np.cos(s / c), np.sin(s / c), 0.0])
        return n if kind == "cyl" else Rm @ n

    # g と L が本文（B-6-1）どおりであることを数値で確認: 円柱で L_ss = -1/c、g = δ
    s0, z0, h = 0.9, 0.4, 1e-4
    rs = (cyl(s0 + h, z0) - cyl(s0 - h, z0)) / (2 * h)
    rz = (cyl(s0, z0 + h) - cyl(s0, z0 - h)) / (2 * h)
    rss = (cyl(s0 + h, z0) - 2 * cyl(s0, z0) + cyl(s0 - h, z0)) / h**2
    n0 = normal("cyl", s0)
    assert np.allclose([rs @ rs, rz @ rz, rs @ rz], [1, 1, 0], atol=1e-6)
    assert abs(rss @ n0 - (-1 / c)) < 1e-4

    fig = plt.figure(figsize=(15, 5.4))
    S, Zg = np.meshgrid(np.linspace(0, 2.2, 40), np.linspace(0, 1.2, 20))
    panels = [
        ("平面", plane, "plane", r"$g_{ij}=\delta_{ij},\quad L_{ij}=0$"),
        ("円柱", cyl, "cyl", r"$g_{ij}=\delta_{ij},\quad L_{ss}=-1/c,\ L_{sz}=L_{zz}=0$"),
        ("円柱を回転・平行移動", moved, "moved", r"$g_{ij}=\delta_{ij},\quad L_{ss}=-1/c,\ \dots$（上と同じ $(g,L)$）"),
    ]
    for k, (name, fn, kind, sub) in enumerate(panels):
        ax = fig.add_subplot(1, 3, 1 + k, projection="3d")
        P = fn(S, Zg)
        ax.plot_surface(P[0], P[1], P[2], color="#dfe8f5", alpha=0.75, linewidth=0, shade=True)
        for sv in np.linspace(0, 2.2, 9):
            q = fn(sv + 0 * np.linspace(0, 1.2, 30), np.linspace(0, 1.2, 30))
            ax.plot(*q, color=C_R1, lw=1.0)
        for zv in np.linspace(0, 1.2, 5):
            q = fn(np.linspace(0, 2.2, 60), zv + 0 * np.linspace(0, 2.2, 60))
            ax.plot(*q, color=C_R2, lw=1.0)
        for sv in (0.3, 1.1, 1.9):
            p0 = fn(np.array(sv), np.array(0.6))
            nv = normal(kind, sv)
            ax.quiver(*p0, *(0.5 * nv), color=C_N, lw=2.6, arrow_length_ratio=0.25)
            ax.plot(*p0, "ko", ms=3)
        ax.set_axis_off()
        allp = np.concatenate([P.reshape(3, -1), (P.reshape(3, -1)[:, :1] + 0.6 * normal(kind, 1.0).reshape(3, 1))], axis=1)
        mid = allp.mean(axis=1)
        rad = 1.5
        ax.set_xlim(mid[0] - rad, mid[0] + rad)
        ax.set_ylim(mid[1] - rad, mid[1] + rad)
        ax.set_zlim(mid[2] - rad, mid[2] + rad)
        ax.set_box_aspect((1, 1, 1), zoom=1.75)
        ax.view_init(elev=22, azim=-58)
        ax.set_title(name + "\n" + sub, fontsize=13)
    fig.text(0.34, 0.5, "≠", fontsize=34, ha="center", va="center", color=RED, fontweight="bold")
    fig.text(0.665, 0.5, "＝", fontsize=30, ha="center", va="center", color=GREEN if (GREEN := "#2a8a2a") else "k")
    fig.text(0.5, 0.06,
             "青・緑の線は $s,z$ 一定の線（$g=\\delta$：どの曲面でも格子は同じ長さの直角格子）。紫の矢印は単位法線 $\\mathbf{n}$。",
             ha="center", fontsize=12)
    fig.text(0.5, 0.015,
             "左＝中：同じ $g$ でも $L$ が違えば別の曲面（$g$ だけでは決まらない）。中＝右：同じ $(g,L)$ なら、回転と平行移動を除いて同じ曲面（ボネの定理）。",
             ha="center", fontsize=12)
    fig.subplots_adjust(left=0.0, right=1.0, top=0.88, bottom=0.11, wspace=0.0)
    fig.savefig(OUT / "fig18_bonnet_uniqueness.png", dpi=150)
    plt.close(fig)


# ======================================================================== 図19
def fig19():
    def eta(u, v):
        return u[0] * v[0] - u[1] * v[1]  # (x, t) 成分、計量 dx^2 - dt^2

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
    for ax, kind in zip(axes, ("space", "time")):
        # 光円錐（点 P から）
        if kind == "space":
            xs = np.linspace(-2.6, 2.6, 300)
            curve = lambda x: 0.32 * np.sin(0.9 * x)
            dcurve = lambda x: 0.32 * 0.9 * np.cos(0.9 * x)
            x0 = 0.4
            P = np.array([x0, curve(x0)])
            sl = dcurve(x0)
            T = np.array([1.0, sl]) / np.sqrt(1 - sl**2)   # 接ベクトル（空間的）
            n = np.array([sl, 1.0]) / np.sqrt(1 - sl**2)   # 法線（時間的）
            ax.plot(xs, curve(xs), color="k", lw=2.8)
            ax.text(1.0, curve(1.0) - 0.5, r"$\Sigma$（空間的超曲面）", fontsize=13.5)
            tcol, ncol = C_SPACE, C_TIME
            tname, nname = r"接ベクトル $e_i$：空間的（$\bar g(e_i,e_i)>0$）", r"法線 $n$：時間的（$\varepsilon=\bar g(n,n)=-1$）"
            title = "空間的超曲面：接する方向はすべて空間的、法線は時間的（$\\varepsilon=-1$）"
        else:
            ts = np.linspace(-1.55, 2.4, 300)
            xcurve = lambda t: 0.6 * np.sin(0.8 * t)
            dx = lambda t: 0.6 * 0.8 * np.cos(0.8 * t)
            t0 = 0.4
            P = np.array([xcurve(t0), t0])
            v = dx(t0)
            T = np.array([v, 1.0]) / np.sqrt(1 - v**2)     # 接ベクトル（時間的）
            n = np.array([1.0, v]) / np.sqrt(1 - v**2)     # 法線（空間的）
            ax.plot(xcurve(ts), ts, color="k", lw=2.8)
            ax.text(xcurve(-1.5) + 0.35, -1.45, "時間的超曲面\n（世界線の面）", fontsize=13.5, va="center")
            tcol, ncol = C_TIME, C_SPACE
            tname, nname = r"接ベクトル：時間的（$\bar g<0$）", r"法線 $n$：空間的（$\varepsilon=\bar g(n,n)=+1$）"
            title = "（対比）時間的な面：接する方向に時間的なものがあり、法線は空間的（$\\varepsilon=+1$）"
        assert abs(eta(n, n) - (-1 if kind == "space" else 1)) < 1e-12
        assert abs(eta(T, n)) < 1e-12  # n は面に「垂直」（ローレンツ計量の意味で）
        assert abs(eta(T, T) - (1 if kind == "space" else -1)) < 1e-12
        c = 1.6
        ax.fill([P[0], P[0] - c, P[0] + c], [P[1], P[1] + c, P[1] + c], color="#fff2b3", alpha=0.65, zorder=0)
        ax.fill([P[0], P[0] - c, P[0] + c], [P[1], P[1] - c, P[1] - c], color="#fff2b3", alpha=0.65, zorder=0)
        for sgn in (1, -1):
            ax.plot([P[0] - c, P[0] + c], [P[1] - sgn * c, P[1] + sgn * c], color=C_NULL, lw=1.3, zorder=1)
        ax.text(P[0] + c + 0.05, P[1] + c - 0.1, "光円錐\n（$\\bar g=0$）", color=C_NULL, fontsize=12, ha="left", va="top")
        ax.add_patch(FancyArrowPatch(P, P + 1.05 * T, arrowstyle="-|>", mutation_scale=22, color=tcol, lw=3.2, zorder=5))
        ax.add_patch(FancyArrowPatch(P, P + 1.05 * n, arrowstyle="-|>", mutation_scale=22, color=ncol, lw=3.2, zorder=5))
        ax.plot(*P, "ko", ms=6, zorder=6)
        # 分類の凡例（左の図にだけ載せる。右の図でも同じ分類）
        if kind == "space":
            ax.text(0.02, 0.98,
                    "ベクトル $v$ の分類（$\\bar g(v,v)$ の符号）\n"
                    "　$<0$：時間的（光円錐の内側）\n　$=0$：光的（光円錐の上）\n　$>0$：空間的（光円錐の外側）",
                    transform=ax.transAxes, va="top", fontsize=11.5, bbox=dict(boxstyle="round", fc="white", ec="#888", alpha=0.95),
                    zorder=10)
        ax.text(0.02, 0.02, f"■ {tname}", transform=ax.transAxes, color=tcol, fontsize=12.5, va="bottom")
        ax.text(0.02, 0.075, f"■ {nname}", transform=ax.transAxes, color=ncol, fontsize=12.5, va="bottom")
        ax.set_aspect("equal")
        ax.set_xlim(-2.6, 2.6)
        ax.set_ylim(-2.3, 2.7)
        ax.set_xlabel("空間 $x$")
        ax.set_ylabel("時間 $t$")
        ax.set_title(title, fontsize=12.5)
    fig.text(0.5, 0.005,
             "$(x,t)$ の平坦な時空図（計量 $dx^2-dt^2$）。「垂直」はローレンツ計量の意味で、見た目の直角ではなく、45° の線に関する鏡映の関係になる。",
             ha="center", fontsize=11.5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    fig.savefig(OUT / "fig19_spacelike_hypersurface.png", dpi=150)
    plt.close(fig)


# ======================================================================== 図20
def fig20():
    a = 1.0
    fig = plt.figure(figsize=(14, 6.4))

    # ---- 球面（ε = +1）
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, w = np.meshgrid(np.linspace(0, 1.25, 40), np.linspace(0, 2 * np.pi, 80))
    X, Y, Z = a * np.sin(u) * np.cos(w), a * np.sin(u) * np.sin(w), a * np.cos(u)
    ax.plot_surface(X, Y, Z, color="#ef9f99", alpha=0.55, linewidth=0, shade=True)
    for uu in np.linspace(0.25, 1.25, 5):
        q = np.linspace(0, 2 * np.pi, 100)
        ax.plot(a * np.sin(uu) * np.cos(q), a * np.sin(uu) * np.sin(q), a * np.cos(uu) + 0 * q, color=RED, lw=0.8)
    for ww in np.linspace(0, 2 * np.pi, 13)[:-1]:
        q = np.linspace(0, 1.25, 40)
        ax.plot(a * np.sin(q) * np.cos(ww), a * np.sin(q) * np.sin(ww), a * np.cos(q), color=RED, lw=0.8)
    for (uu, ww) in [(0.7, 0.5), (0.9, 2.3), (0.55, 4.2)]:
        Xp = a * np.array([np.sin(uu) * np.cos(ww), np.sin(uu) * np.sin(ww), np.cos(uu)])
        ax.quiver(*Xp, *(0.5 * Xp / a), color=C_N, lw=2.8, arrow_length_ratio=0.25)
        ax.plot(*Xp, "ko", ms=3)
    ax.set_box_aspect((1, 1, 0.8), zoom=1.45)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_zlim(0, 1.6)
    ax.set_axis_off()
    ax.view_init(elev=24, azim=-55)
    ax.set_title("球面（$\\mathbb{R}^3$ の中、$\\varepsilon=+1$）\n" r"$K_{ij}=-g_{ij}/a\ \Rightarrow\ K_{\mathrm{G}}=+1/a^2$", fontsize=13.5)
    ax.text2D(0.5, 0.02, r"$X=a(\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta)$", transform=ax.transAxes, ha="center", fontsize=12)

    # ---- 双曲面（ε = -1）: X(χ,φ) = a (cosh χ, sinh χ cos φ, sinh χ sin φ) in (t, x, y)
    bx = fig.add_subplot(1, 2, 2, projection="3d")

    def hyp(chi, phi):
        return a * np.array([np.sinh(chi) * np.cos(phi), np.sinh(chi) * np.sin(phi), np.cosh(chi)])  # (x, y, t)

    # 本文（C-1-4）の値を数値で確認: g_χχ = a², g_φφ = a² sinh²χ、K_ij = -g_ij/a、K_G = -1/a²
    def eta3(p, q):  # 計量 diag(+1, +1, -1)（順序は (x, y, t)）
        return p[0] * q[0] + p[1] * q[1] - p[2] * q[2]

    chi0, phi0, h = 0.8, 0.6, 1e-4
    ec = (hyp(chi0 + h, phi0) - hyp(chi0 - h, phi0)) / (2 * h)
    ep = (hyp(chi0, phi0 + h) - hyp(chi0, phi0 - h)) / (2 * h)
    X0 = hyp(chi0, phi0)
    assert abs(eta3(X0, X0) + a**2) < 1e-12
    assert abs(eta3(ec, ec) - a**2) < 1e-6 and abs(eta3(ep, ep) - a**2 * np.sinh(chi0) ** 2) < 1e-6 and abs(eta3(ec, ep)) < 1e-6
    n0 = X0 / a
    assert abs(eta3(n0, n0) + 1) < 1e-12 and abs(eta3(n0, ec)) < 1e-6 and abs(eta3(n0, ep)) < 1e-6
    Xcc = (hyp(chi0 + h, phi0) - 2 * X0 + hyp(chi0 - h, phi0)) / h**2
    assert abs(eta3(Xcc, n0) - (-a)) < 1e-4  # K_χχ = ḡ(∂_χ∂_χ X, n) = -a

    ch, ph = np.meshgrid(np.linspace(0, 1.25, 40), np.linspace(0, 2 * np.pi, 80))
    P = hyp(ch, ph)
    bx.plot_surface(P[0], P[1], P[2], color="#86b6ef", alpha=0.55, linewidth=0, shade=True)
    for cc in np.linspace(0.25, 1.25, 5):
        q = np.linspace(0, 2 * np.pi, 100)
        pp = hyp(cc + 0 * q, q)
        bx.plot(*pp, color=BLUE, lw=0.8)
    for pw in np.linspace(0, 2 * np.pi, 13)[:-1]:
        q = np.linspace(0, 1.25, 40)
        pp = hyp(q, pw + 0 * q)
        bx.plot(*pp, color=BLUE, lw=0.8)
    # 光円錐 t = sqrt(x^2 + y^2)
    rr, pc = np.meshgrid(np.linspace(0.6, 1.7, 2), np.linspace(0, 2 * np.pi, 60))  # 下端は切って描く
    bx.plot_surface(rr * np.cos(pc), rr * np.sin(pc), rr, color="#fff2b3", alpha=0.25, linewidth=0, shade=False)
    for (cc, pw) in [(0.7, 0.5), (0.9, 2.3), (0.55, 4.2)]:
        Xp = hyp(cc, pw)
        bx.quiver(*Xp, *(0.5 * Xp / a), color=C_N, lw=2.8, arrow_length_ratio=0.25)
        bx.plot(*Xp, "ko", ms=3)
    bx.set_box_aspect((1, 1, 0.8), zoom=1.45)
    bx.set_xlim(-1.7, 1.7)
    bx.set_ylim(-1.7, 1.7)
    bx.set_zlim(0.6, 2.3)
    bx.set_axis_off()
    bx.view_init(elev=24, azim=-55)
    bx.set_title("双曲面（ミンコフスキー空間の中、$\\varepsilon=-1$）\n" r"$K_{ij}=-g_{ij}/a\ \Rightarrow\ K_{\mathrm{G}}=-1/a^2$", fontsize=13.5)
    bx.text2D(0.5, 0.02, r"$X=a(\cosh\chi,\ \sinh\chi\cos\phi,\ \sinh\chi\sin\phi)$（黄：光円錐、$-t^2+x^2+y^2=-a^2$）",
              transform=bx.transAxes, ha="center", fontsize=11.5)
    fig.text(0.5, 0.02,
             "紫の矢印は単位法線 $n=X/a$。球面では $\\bar g(n,n)=+1$、双曲面では $-1$ で、同じ形の $K_{ij}=-g_{ij}/a$ から、"
             "$\\varepsilon$ の符号によってガウス曲率の符号が反転する（C-1-4）。",
             ha="center", fontsize=12)
    fig.subplots_adjust(left=0.0, right=1.0, top=0.88, bottom=0.09, wspace=0.0)
    fig.savefig(OUT / "fig20_sphere_vs_hyperboloid.png", dpi=150)
    plt.close(fig)


# ======================================================================== 図21
def fig21():
    cv = Canvas(1500, 1160)
    EC = "#3b6fb6"
    GRAY = "#444444"

    def m(s, col=GRAY):
        return (s, col, "m")

    cv.card(30, 1120, 1440, 870, "拘束条件と発展方程式：アインシュタインテンソル $\\bar G_{\\mu\\nu}$ を、$n$ 方向と $\\Sigma$ の方向に分ける", ec=EC)

    # ブロック行列 (n, e_i)×(n, e_i)
    x0, y0 = 100, 950  # 左上
    wn, wi, hn, hi = 170, 420, 120, 250
    C_HAM, C_MOM, C_EVO = "#f3d34a", "#f0a15a", "#9cc3ef"

    def block(x, y, w, h, fc):
        cv.ax.add_patch(Rectangle((x, y - h), w, h, fc=fc, ec="#555", lw=2, zorder=1))

    block(x0, y0, wn, hn, C_HAM)
    block(x0 + wn, y0, wi, hn, C_MOM)
    block(x0, y0 - hn, wn, hi, C_MOM)
    block(x0 + wn, y0 - hn, wi, hi, C_EVO)
    cv.ax.text(x0 + wn / 2, y0 + 25, r"$n$", ha="center", fontsize=22)
    cv.ax.text(x0 + wn + wi / 2, y0 + 25, r"$e_i$", ha="center", fontsize=22)
    cv.ax.text(x0 - 28, y0 - hn / 2, r"$n$", ha="center", va="center", fontsize=22)
    cv.ax.text(x0 - 28, y0 - hn - hi / 2, r"$e_i$", ha="center", va="center", fontsize=22)
    cv.ax.text(x0 + wn / 2, y0 - hn / 2, r"$\bar G_{nn}$", ha="center", va="center", fontsize=20)
    cv.ax.text(x0 + wn + wi / 2, y0 - hn / 2, r"$\bar G_{ni}$", ha="center", va="center", fontsize=20)
    cv.ax.text(x0 + wn / 2, y0 - hn - hi / 2, r"$\bar G_{in}$", ha="center", va="center", fontsize=20)
    cv.ax.text(x0 + wn + wi / 2, y0 - hn - hi / 2, r"$\bar G_{ij}$", ha="center", va="center", fontsize=20)
    cv.ax.text(x0, y0 + 75, r"成分（$\bar G_{\mu\nu}$ は対称）", fontsize=13, color=GRAY, ha="left")

    # 右: 各ブロックの意味
    xr = 790
    cv.rich(xr, 945, [("ハミルトン拘束", "#8a6d00"), ("（1本）", GRAY)], size=17)
    cv.rich(xr, 907, [m(r"R+(\operatorname{tr}K)^2-K_{ij}K^{ij}=16\pi G_{\mathrm{N}}\,\mathcal{E}", GRAY)], size=17)
    cv.rich(xr, 871, [("← ガウス方程式（C.5）を縮約した ", GRAY), m(r"\bar G_{nn}", GRAY)], size=14)
    cv.arrow((xr - 15, 920), (x0 + wn - 8, y0 - hn / 2 + 8), "#8a6d00", lw=2.4, rad=0.1)

    cv.rich(xr, 790, [("運動量拘束", "#b35a00"), ("（空間の次元ぶん：3本）", GRAY)], size=17)
    cv.rich(xr, 752, [m(r"D_i(\operatorname{tr}K)-D^jK_{ij}=8\pi G_{\mathrm{N}}\,j_i", GRAY)], size=17)
    cv.rich(xr, 716, [("← コダッツィ方程式（C.6）を縮約した ", GRAY), m(r"\bar G_{ni}=\bar G_{in}", GRAY)], size=14)
    cv.arrow((xr - 15, 770), (x0 + wn + wi - 10, y0 - hn / 2 - 12), "#b35a00", lw=2.4, rad=0.1)

    cv.rich(xr, 650, [("発展方程式", "#1f5fa8"), ("（空間の対称2階テンソルぶん：6本）", GRAY)], size=17)
    cv.rich(xr, 612, [m(r"\partial_tK_{ij}=\cdots", GRAY), ("（時間微分 ", GRAY), m(r"\partial_tK_{ij}", GRAY), (" を含む）", GRAY)], size=17)
    cv.rich(xr, 576, [("← ", GRAY), m(r"\bar G_{ij}", GRAY), ("（C-3-2）：時間発展を決める", GRAY)], size=14)
    cv.arrow((xr - 15, 628), (x0 + wn + wi - 10, y0 - hn - hi / 2), "#1f5fa8", lw=2.4, rad=0.1)

    # 下: 意味
    cv.rich(60, 480, [("拘束条件（黄・橙）", "#8a6d00"), ("は、ある時刻の断面 ", GRAY), m(r"\Sigma", GRAY), (" の上だけで閉じた条件で、", GRAY),
                      m(r"K_{ij}", GRAY), (" の時間変化を含まない。", GRAY)], size=16)
    cv.rich(60, 435, [("初期データ ", GRAY), m(r"(g_{ij},K_{ij})", GRAY), (" は、この 1+3=4 本を満たさなければならない。", GRAY)], size=16)
    cv.rich(60, 385, [("発展方程式（青）", "#1f5fa8"), ("で時間発展させると、拘束条件は自動的に保たれる（C-3-3、縮約ビアンキ恒等式）。", GRAY)], size=16)
    cv.rich(60, 335, [("合計 ", GRAY), m(r"1+3+6=10", GRAY), (" は、4次元時空の対称2階テンソルの独立成分の数と一致。", GRAY)], size=16)
    cv.rich(60, 285, [("付録B との対応：外側が平坦（", GRAY), m(r"\bar G=0", GRAY), ("）なら、拘束条件は B-7 の縮約した2式（ガウス・コダッツィ）そのもの。", GRAY)],
            size=16)

    cv.save("fig21_constraint_blocks.png")


# ======================================================================== 図22
def fig22():
    fig, ax = plt.subplots(figsize=(13.5, 7.4))
    S = 1.0  # 初期データを与える区間 |x| <= S（t=0）
    # 依存領域 D+(S): |x| <= S - t, 0 <= t <= S
    ax.fill([-S, S, 0], [0, 0, S], color="#d6ecd2", alpha=0.9, zorder=0)
    ax.plot([-S, 0, S], [0, S, 0], color="#2a8a2a", lw=1.8, ls="--")
    ax.axhline(0, color="#999", lw=1)
    ax.plot([-S, S], [0, 0], color="k", lw=6, solid_capstyle="butt", zorder=5)
    ax.text(0, -0.1, r"初期面 $\Sigma$（$t=0$）：区間 $S$ 上に、初期データ $(g_{ij},K_{ij})$ を与える", ha="center", fontsize=13.5, va="top")
    # ガウス正規座標：法線方向の測地線と、断面 Σ_t
    for x in np.linspace(-0.9, 0.9, 10):
        ax.plot([x, x], [0, S - abs(x)], color="#2563a8", lw=0.9, alpha=0.7, zorder=3)
    for tt in (0.25, 0.5, 0.75):
        xs = S - tt
        ax.plot([-xs, xs], [tt, tt], color="#2563a8", lw=2.4, zorder=4)
        ax.text(xs + 0.04, tt, rf"$\Sigma_{{t={tt}}}$", color="#2563a8", fontsize=12.5, va="center")
    # 説明（左側）
    ax.text(-1.25, 0.95, "ガウス正規座標\n（断面から法線方向に測地線を伸ばす。青）", color="#2563a8", fontsize=12, va="center", ha="right")
    ax.text(-1.25, 0.45, "$S$ の外側の初期データは\n$D^+(S)$ に影響しない\n（信号は光速を超えない）", ha="right", va="center", fontsize=12,
            color="#555")
    # D+ の説明（頂点の上）
    ax.text(0, 1.1, r"$D^+(S)$：区間 $S$ 上の初期データだけで時空が決まる領域", ha="center", va="bottom", fontsize=13.5, color="#1f5f1f")
    # 光円錐（S の外の 1 点）
    p = np.array([2.35, 0.0])
    ax.fill([p[0], p[0] - 0.9, p[0] + 0.9], [p[1], p[1] + 0.9, p[1] + 0.9], color="#fff2b3", alpha=0.85, zorder=0)
    ax.plot(p[0], p[1], "ko", ms=5)
    ax.text(p[0], p[1] + 1.0, "$S$ の外の点の光円錐\n（影響が届く範囲）", ha="center", fontsize=11.5, color="#8a7400")
    # 拘束条件の保存
    ax.text(0.0, -0.75,
            "拘束条件は初期面で満たせば、発展方程式のもとで時間発展しても保たれる（C-3-3）。\n"
            "初期データと拘束条件から、調和座標の波動方程式の初期値問題として解が存在する（C-3-4）。",
            ha="center", fontsize=12, va="center", bbox=dict(boxstyle="round", fc="white", ec="#888"))
    ax.set_aspect("equal")
    ax.set_xlim(-3.9, 3.4)
    ax.set_ylim(-1.2, 1.5)
    ax.set_xlabel("空間 $x$")
    ax.set_ylabel("時間 $t$")
    ax.set_title("初期値問題（C-3-4）：拘束条件を満たす初期データから、アインシュタイン方程式の解（時空）が決まる", fontsize=13.5)
    fig.text(0.5, 0.005,
             "$(x,t)$ の時空図（光円錐は 45°）。緑の領域 $D^+(S)$ が、区間 $S$ 上の初期データだけで決まる範囲（ショケ＝ブリュアの定理の骨格）。",
             ha="center", fontsize=11.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT / "fig22_cauchy_problem.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    for fn in (fig14, fig15, fig16, fig17, fig18, fig19, fig20, fig21, fig22):
        fn()
    print("saved to", OUT)
