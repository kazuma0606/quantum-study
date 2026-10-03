"""laplace_beltrami_from_jacobian_matrix.md（ヤコビ行列から見るラプラス・ベルトラミ作用素）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/02_微分幾何/figures/make_lb_figures.py          # すべて
    uv run python 研究ノート/02_微分幾何/figures/make_lb_figures.py lb01     # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    lb01_tangent_vs_gradient.png   Part I §2 極座標：J の列（接ベクトル）と A=J^{-1} の行（勾配）、∂x/∂r と ∂r/∂x
    lb02_oblique_coordinates.png   Part III 斜交座標 u=x, v=y+x^2：接ベクトルと勾配、∇q^j·e_k=δ_jk
    lb03_polar_cell_flux.png       Part IV 極座標のセルを出入りする流れと、発散の式の √g

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


def num_jacobian(f, p, h=1e-6):
    """f: R^n → R^n の、点 p でのヤコビ行列（中心差分）"""
    p = np.asarray(p, float)
    cols = [(np.asarray(f(p + h * e)) - np.asarray(f(p - h * e))) / (2 * h) for e in np.eye(len(p))]
    return np.stack(cols, axis=1)


def arrow(ax, p, v, color, lw=2.2, ls="-", alpha=1.0, z=3):
    ax.annotate("", xy=(p[0] + v[0], p[1] + v[1]), xytext=(p[0], p[1]),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, alpha=alpha, mutation_scale=14), zorder=z)


# ------------------------------------------------------------------------------------- lb01
def lb01():
    """極座標：J の列 e_r, e_θ と、A=J^{-1} の行 ∇r, ∇θ。∂x/∂r と ∂r/∂x。"""
    X = lambda q: np.array([q[0] * np.cos(q[1]), q[0] * np.sin(q[1])])          # (r, θ) → (x, y)
    Q = lambda p: np.array([np.hypot(p[0], p[1]), np.arctan2(p[1], p[0])])      # (x, y) → (r, θ)
    fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.4))
    s = 0.35                                                                    # (a)(b) 共通の矢印の縮尺
    pts = [(r, np.radians(t)) for r in (0.6, 1.2, 1.8) for t in (25, 145, 265)]

    for ax in axes[:2]:
        tt = np.linspace(0, 2 * np.pi, 200)
        for r in (0.6, 1.2, 1.8):
            ax.plot(r * np.cos(tt), r * np.sin(tt), color="#d0d0d0", lw=1)
        for a in np.radians(np.arange(0, 360, 30)):
            ax.plot([0, 2.2 * np.cos(a)], [0, 2.2 * np.sin(a)], color="#e3e3e3", lw=0.8, zorder=0)
        ax.set_aspect("equal"), ax.set_xlim(-2.4, 2.4), ax.set_ylim(-2.4, 2.4)
        ax.set_xlabel("$x$"), ax.set_ylabel("$y$")

    for r, th in pts:
        J = num_jacobian(X, [r, th])                                            # 列：e_r, e_θ
        p = X([r, th])
        A = num_jacobian(Q, p)                                                  # 行：∇r, ∇θ
        assert np.allclose(A @ J, np.eye(2), atol=1e-6)                         # AJ = I
        assert np.allclose(J[:, 1], r * np.array([-np.sin(th), np.cos(th)]), atol=1e-6)        # |e_θ| = r
        assert np.allclose(A[1], np.array([-np.sin(th), np.cos(th)]) / r, atol=1e-6)            # |∇θ| = 1/r
        assert np.isclose(A[1] @ J[:, 1], 1, atol=1e-6)
        for ax, v1, v2 in [(axes[0], J[:, 0], J[:, 1]), (axes[1], A[0], A[1])]:
            ax.plot(*p, "o", color="#222", ms=4, zorder=4)
            arrow(ax, p, s * v1, C_A)
            arrow(ax, p, s * v2, C_B)
    axes[0].plot([], [], color=C_A, lw=2.2, label="$\\mathbf{e}_r=\\partial\\mathbf{x}/\\partial r$（長さ 1）")
    axes[0].plot([], [], color=C_B, lw=2.2, label="$\\mathbf{e}_\\theta=\\partial\\mathbf{x}/\\partial\\theta$（長さ $r$）")
    axes[1].plot([], [], color=C_A, lw=2.2, label="$\\nabla r$（長さ 1）")
    axes[1].plot([], [], color=C_B, lw=2.2, label="$\\nabla\\theta$（長さ $1/r$）")
    for ax in axes[:2]:
        ax.legend(fontsize=9.5, loc="lower left")
    axes[0].set_title("(a) $J$ の列：接ベクトル $\\mathbf{e}_r,\\ \\mathbf{e}_\\theta$\n外側ほど $\\mathbf{e}_\\theta$ が長い", fontsize=11)
    axes[1].set_title("(b) $A=J^{-1}$ の行：勾配 $\\nabla r,\\ \\nabla\\theta$（等高線に垂直）\n外側ほど $\\nabla\\theta$ が短い。$\\nabla\\theta\\cdot\\mathbf{e}_\\theta=1$", fontsize=11)

    # (c) ∂x/∂r と ∂r/∂x
    ax = axes[2]
    r0, th0, L = 2.0, np.radians(50), 0.35
    P = X([r0, th0])
    c = np.cos(th0)
    assert np.isclose(num_jacobian(X, [r0, th0])[0, 0], c) and np.isclose(num_jacobian(Q, P)[0, 0], c)   # どちらも cosθ
    ax.plot([0, 2.5 * np.cos(th0)], [0, 2.5 * np.sin(th0)], color="#bbbbbb", lw=1.2)
    ax.plot([0, 2.5], [0, 0], color="#dddddd", lw=1)
    aa = np.linspace(0, th0, 50)
    ax.plot(0.45 * np.cos(aa), 0.45 * np.sin(aa), color="#555", lw=1)
    ax.text(0.5 * np.cos(th0 / 2), 0.5 * np.sin(th0 / 2), "$\\theta$", fontsize=12, va="center")
    ax.plot(0, 0, "o", color="#222", ms=4), ax.text(0.05, -0.12, "原点", fontsize=9)
    # θ 固定で r を L 動かす：Δx = L cosθ
    T1 = P + L * np.array([np.cos(th0), np.sin(th0)])
    arrow(ax, P, T1 - P, C_A, lw=2.6)
    ax.plot([P[0], T1[0]], [P[1], P[1]], color=C_A, lw=1.4, ls="--")
    ax.plot([T1[0], T1[0]], [P[1], T1[1]], color=C_A, lw=1, ls=":")
    ax.text(T1[0] + 0.04, T1[1] + 0.02, "$\\theta$ 固定で $r$ を $L$ 動かす", color=C_A, fontsize=10)
    ax.text((P[0] + T1[0]) / 2, P[1] - 0.04, "$\\Delta x=L\\cos\\theta$", color=C_A, fontsize=10, ha="center", va="top")
    # y 固定で x を L 動かす：Δr ≈ L cosθ（見やすいよう、同じ構成を少し下の点 Pd に描く）
    Pd = P - np.array([0, 0.55])
    rd, thd = Q(Pd)
    T2 = Pd + np.array([L, 0])
    arrow(ax, Pd, T2 - Pd, C_B, lw=2.6)
    rT = np.hypot(*T2)
    aa = np.linspace(np.arctan2(T2[1], T2[0]) - 0.05, thd + 0.08, 50)
    ax.plot(rT * np.cos(aa), rT * np.sin(aa), color=C_B, lw=1.2, ls="--")       # r 一定の円弧
    ray = np.array([np.cos(thd), np.sin(thd)])
    ax.plot([0, 2.6 * ray[0]], [0, 2.6 * ray[1]], color="#dddddd", lw=1, zorder=0)
    ax.plot(*(rT * ray), "o", color=C_B, ms=4)
    ax.plot([Pd[0], rT * ray[0]], [Pd[1], rT * ray[1]], color=C_B, lw=3.2, alpha=0.5)
    assert abs((rT - rd) - L * np.cos(thd)) < 0.1 * L                           # Δr ≈ L cosθ（L が小さいとき）
    ax.text(T2[0] + 0.04, T2[1] - 0.06, "$y$ 固定で $x$ を $L$ 動かす", color=C_B, fontsize=10)
    ax.text(rT * ray[0] - 0.08, rT * ray[1] + 0.05, "$\\Delta r\\approx L\\cos\\theta$", color=C_B, fontsize=10, ha="right")
    ax.plot(*P, "o", color="#222", ms=5), ax.plot(*Pd, "o", color="#222", ms=5)
    ax.set_aspect("equal"), ax.set_xlim(-0.1, 2.5), ax.set_ylim(-0.25, 2.3)
    ax.set_xlabel("$x$"), ax.set_ylabel("$y$")
    ax.set_title("(c) $\\partial x/\\partial r$ も $\\partial r/\\partial x$ も $\\cos\\theta$：\n固定するものが違うので、逆数（$1/\\cos\\theta$）にならない", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "lb01_tangent_vs_gradient.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lb02
def lb02():
    """斜交座標 u = x, v = y + x^2：接ベクトル e_u, e_v と勾配 ∇u, ∇v。"""
    X = lambda q: np.array([q[0], q[1] - q[0] ** 2])                            # (u, v) → (x, y)
    Q = lambda p: np.array([p[0], p[1] + p[0] ** 2])                            # (x, y) → (u, v)
    fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.6), gridspec_kw=dict(width_ratios=[1, 1, 1.05]))
    s = 0.42
    pts = [(u, v) for u in (-1.0, 0.0, 1.0) for v in (0.5, 2.0)]
    for ax in axes[:2]:
        for c in np.arange(-1.5, 1.51, 0.5):
            ax.plot([c, c], [-1.6, 2.6], color="#d0d0d0", lw=1)                   # u 一定
        xs = np.linspace(-1.7, 1.7, 200)
        for v in np.arange(-1.0, 3.01, 0.5):
            ax.plot(xs, v - xs**2, color="#d0d0d0", lw=1)                         # v 一定
        ax.set_aspect("equal"), ax.set_xlim(-1.7, 1.7), ax.set_ylim(-1.6, 2.6)
        ax.set_xlabel("$x$"), ax.set_ylabel("$y$")
    for u, v in pts:
        J = num_jacobian(X, [u, v])
        p = X([u, v])
        A = num_jacobian(Q, p)
        assert np.allclose(A @ J, np.eye(2), atol=1e-6)
        assert np.allclose(J, [[1, 0], [-2 * u, 1]], atol=1e-6) and np.allclose(A, [[1, 0], [2 * u, 1]], atol=1e-6)
        assert np.isclose(J[:, 0] @ J[:, 1], -2 * u, atol=1e-6)                # g_uv = −2u
        for ax, v1, v2 in [(axes[0], J[:, 0], J[:, 1]), (axes[1], A[0], A[1])]:
            ax.plot(*p, "o", color="#222", ms=4, zorder=4)
            arrow(ax, p, s * v1, C_A)
            arrow(ax, p, s * v2, C_B)
    axes[0].plot([], [], color=C_A, lw=2.2, label="$\\mathbf{e}_u=(1,\\,-2u)$：放物線（$v$ 一定）の接線")
    axes[0].plot([], [], color=C_B, lw=2.2, label="$\\mathbf{e}_v=(0,\\,1)$：鉛直線（$u$ 一定）の接線")
    axes[1].plot([], [], color=C_A, lw=2.2, label="$\\nabla u=(1,\\,0)$：鉛直線に垂直")
    axes[1].plot([], [], color=C_B, lw=2.2, label="$\\nabla v=(2u,\\,1)$：放物線に垂直")
    for ax in axes[:2]:
        ax.legend(fontsize=9, loc="lower center")
    axes[0].set_title("(a) $J$ の列：接ベクトル $\\mathbf{e}_u,\\ \\mathbf{e}_v$\n（座標曲線の接線方向）", fontsize=11)
    axes[1].set_title("(b) $A=J^{-1}$ の行：勾配 $\\nabla u,\\ \\nabla v$\n（等高線に垂直）", fontsize=11)

    # (c) u = 1 の点で 4 本を重ねる
    ax = axes[2]
    u0, v0 = 1.0, 2.0
    p = X([u0, v0])
    eu, ev = np.array([1, -2 * u0]), np.array([0, 1.0])
    gu, gv = np.array([1, 0.0]), np.array([2 * u0, 1])
    assert np.isclose(gu @ ev, 0) and np.isclose(gv @ eu, 0) and np.isclose(gu @ eu, 1) and np.isclose(gv @ ev, 1)
    ang = np.degrees(np.arccos(eu @ ev / np.linalg.norm(eu) / np.linalg.norm(ev)))
    assert np.isclose(ang, 153.43, atol=0.01)
    ax.plot([p[0], p[0]], [p[1] - 2.4, p[1] + 1.4], color="#d0d0d0", lw=1)
    xs = np.linspace(p[0] - 1.3, p[0] + 1.0, 100)
    ax.plot(xs, v0 - xs**2, color="#d0d0d0", lw=1)
    k = 0.55
    arrow(ax, p, k * eu, C_A, lw=2.6)
    arrow(ax, p, k * ev, C_B, lw=2.6)
    arrow(ax, p, k * gu, C_A, lw=2.2, ls="--")
    arrow(ax, p, k * gv, C_B, lw=2.2, ls="--")

    def right_angle(a, b, size=0.12):
        a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
        ax.plot(*np.array([p + size * a, p + size * (a + b), p + size * b]).T, color="#333", lw=1)

    right_angle(gu, ev)
    right_angle(gv, eu)
    ax.text(*(p + k * eu + [0.05, -0.05]), "$\\mathbf{e}_u$", color=C_A, fontsize=13)
    ax.text(*(p + k * ev + [0.05, 0.02]), "$\\mathbf{e}_v$", color=C_B, fontsize=13)
    ax.text(*(p + k * gu + [0.05, -0.03]), "$\\nabla u$", color=C_A, fontsize=13)
    ax.text(*(p + k * gv + [0.05, 0.0]), "$\\nabla v$", color=C_B, fontsize=13)
    ax.text(p[0] - 1.25, p[1] - 1.45,
            f"$\\nabla u\\perp\\mathbf{{e}}_v,\\ \\nabla v\\perp\\mathbf{{e}}_u$\n"
            f"$\\nabla u\\cdot\\mathbf{{e}}_u=\\nabla v\\cdot\\mathbf{{e}}_v=1$（$AJ=I$）\n"
            f"$\\mathbf{{e}}_u$ と $\\mathbf{{e}}_v$ の角度 $={ang:.1f}^\\circ$（$g_{{uv}}=-2u=-2$）\n"
            f"$\\nabla u$ と $\\mathbf{{e}}_u$ も向きがずれる（斜交座標に特有）",
            fontsize=10, va="top")
    ax.plot(*p, "o", color="#222", ms=5)
    ax.set_aspect("equal"), ax.set_xlim(p[0] - 1.35, p[0] + 1.5), ax.set_ylim(p[1] - 2.6, p[1] + 1.1)
    ax.set_xlabel("$x$"), ax.set_ylabel("$y$")
    ax.set_title("(c) $u=1,\\ v=2$ の点で4本を重ねる\n（実線：$J$ の列、破線：$A$ の行）", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "lb02_oblique_coordinates.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- lb03
def lb03():
    """極座標のセルを出入りする流れ：発散 (1/√g) ∂_j(√g V^j) の √g は、セルの辺の長さと面積。"""
    fig, axes = plt.subplots(1, 3, figsize=(18.5, 6.2))
    r0, dr, th0, dth = 1.5, 0.6, np.radians(25), np.radians(25)

    def cell_outline():
        a = np.linspace(th0, th0 + dth, 60)
        return np.concatenate([np.stack([r0 * np.cos(a), r0 * np.sin(a)], 1),
                               np.stack([(r0 + dr) * np.cos(a[::-1]), (r0 + dr) * np.sin(a[::-1])], 1)])

    def net_flux(Vr):
        """半径方向の場 V = Vr(r) e_r について、セルの周りの線積分（外向き）で出入りの差を計算する"""
        a = np.linspace(th0, th0 + dth, 2001)
        outer = np.trapezoid(Vr(r0 + dr) * (r0 + dr) * np.ones_like(a), a)
        inner = np.trapezoid(Vr(r0) * r0 * np.ones_like(a), a)
        return outer - inner, outer, inner                                         # 動径方向の辺では V ⟂ 法線で 0

    def div_polar(Vr, r, h=1e-6):
        return ((r + h) * Vr(r + h) - (r - h) * Vr(r - h)) / (2 * h) / r          # (1/√g) ∂_r(√g V^r)、√g = r

    def div_cart(Vr, x, y, h=1e-6):
        F = lambda x, y: Vr(np.hypot(x, y)) * np.array([x, y]) / np.hypot(x, y)
        return (F(x + h, y)[0] - F(x - h, y)[0] + F(x, y + h)[1] - F(x, y - h)[1]) / (2 * h)

    # (a) セルの形
    ax = axes[0]
    tt = np.linspace(0, np.pi / 2, 100)
    for r in (0.5, 1.0, 1.5, 2.1, 2.6):
        ax.plot(r * np.cos(tt), r * np.sin(tt), color="#e0e0e0", lw=1)
    for a in np.radians(np.arange(0, 91, 12.5)):
        ax.plot([0, 2.8 * np.cos(a)], [0, 2.8 * np.sin(a)], color="#ececec", lw=0.8, zorder=0)
    ax.fill(*cell_outline().T, color=C_A, alpha=0.25)
    ax.plot(*np.vstack([cell_outline(), cell_outline()[:1]]).T, color=C_A, lw=2)
    for (rr, lab, off) in [(r0, "$r\\,d\\theta$", -0.2), (r0 + dr, "$(r+dr)\\,d\\theta$", 0.12)]:
        am = th0 + dth / 2
        ax.text((rr + off) * np.cos(am), (rr + off) * np.sin(am), lab, fontsize=12, ha="center", va="center", rotation=np.degrees(am) - 90)
    ax.text((r0 + dr / 2) * np.cos(th0) + 0.05, (r0 + dr / 2) * np.sin(th0) - 0.16, "$dr$", fontsize=12)
    ax.text(0.15, 2.45, "面積 $\\approx r\\,dr\\,d\\theta=\\sqrt{g}\\,dr\\,d\\theta$", fontsize=11)
    ax.plot(0, 0, "o", color="#222", ms=4)
    ax.set_aspect("equal"), ax.set_xlim(-0.1, 2.8), ax.set_ylim(-0.1, 2.8), ax.set_xlabel("$x$"), ax.set_ylabel("$y$")
    ax.set_title("(a) 極座標の小さなセル：外側の辺ほど長い\n（辺の長さ $\\sqrt{g}\\,d\\theta$、面積 $\\sqrt{g}\\,dr\\,d\\theta$）", fontsize=11)

    # (b)(c) 2つの半径方向の場
    for ax, Vr, name, expect, title in [
        (axes[1], lambda r: 1 / r, "$V=\\mathbf{e}_r/r$", 0.0,
         "(b) $V=\\mathbf{e}_r/r$：外側ほど弱いが、外側の辺が長いので\n出る量＝入る量。$\\operatorname{div}V=\\frac{1}{r}\\partial_r\\!\\left(r\\cdot\\frac{1}{r}\\right)=0$"),
        (axes[2], lambda r: np.ones_like(r), "$V=\\mathbf{e}_r$", None,
         "(c) $V=\\mathbf{e}_r$：大きさは一定だが、外側の辺が長いので\n出る量が多い。$\\operatorname{div}V=\\frac{1}{r}\\partial_r(r\\cdot1)=\\frac{1}{r}$")]:
        net, out, inn = net_flux(Vr)
        rr = np.linspace(r0, r0 + dr, 2001)
        area_int = np.trapezoid(div_polar(Vr, rr) * rr, rr) * dth                # ∬ div V √g dr dθ
        assert np.isclose(net, area_int, atol=1e-6)                              # 出入りの差 = ∬ div V dA
        for x, y in [(1.1, 0.4), (0.3, 1.7), (2.0, 1.1)]:
            assert np.isclose(div_cart(Vr, x, y), div_polar(Vr, np.hypot(x, y)), atol=1e-5)   # デカルトの div と一致
        if expect is not None:
            assert abs(net) < 1e-9
        else:
            assert np.isclose(net, dr * dth, rtol=1e-6)                          # ∬ (1/r) r dr dθ = dr dθ
        for r in (0.6, 1.0, 1.4, 1.8, 2.2, 2.6):
            for a in np.radians(np.arange(5, 90, 10)):
                p = r * np.array([np.cos(a), np.sin(a)])
                arrow(ax, p, 0.22 * Vr(np.array(r)) * p / r, "#9bbbd6", lw=1.2, z=1)
        ax.fill(*cell_outline().T, color=C_A, alpha=0.2)
        ax.plot(*np.vstack([cell_outline(), cell_outline()[:1]]).T, color=C_A, lw=2)
        am = th0 + dth / 2
        d = np.array([np.cos(am), np.sin(am)])
        for rr_, col in [(r0, C_B), (r0 + dr, C_BAD)]:
            ln = 0.6 * float(Vr(np.array(rr_)))                                  # 矢印の長さ ∝ V^r。辺の上に中央をそろえる
            arrow(ax, rr_ * d - 0.5 * ln * d, ln * d, col, lw=2.8, z=5)
        ax.text(0.12, 2.62, f"入る量 $r_0\\,V^r(r_0)\\,d\\theta$ = {inn:.3f}\n出る量 $(r_0+dr)\\,V^r(r_0+dr)\\,d\\theta$ = {out:.3f}",
                fontsize=10, va="top", bbox=dict(fc="white", ec="#cccccc"))
        ax.set_aspect("equal"), ax.set_xlim(-0.1, 2.8), ax.set_ylim(-0.1, 2.8), ax.set_xlabel("$x$"), ax.set_ylabel("$y$")
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "lb03_polar_cell_flux.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(lb01=lb01, lb02=lb02, lb03=lb03)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
