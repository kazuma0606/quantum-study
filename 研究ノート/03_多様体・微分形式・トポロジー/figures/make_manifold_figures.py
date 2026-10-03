"""manifolds_introduction.md（多様体入門）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/03_多様体・微分形式・トポロジー/figures/make_manifold_figures.py            # すべて
    uv run python 研究ノート/03_多様体・微分形式・トポロジー/figures/make_manifold_figures.py mani01     # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    mani01_charts.png          Part I §4・§5 円の2枚の地図、球面の立体射影と座標変換 u ↦ u/|u|²
    mani02_not_manifolds.png   Part I §7 多様体でない例（2本の直線の交点、二重円錐の頂点）
    mani03_regular_value.png   Part II 正則値定理：等位集合、球面の接平面、正則値は十分条件
    mani04_tissot.png          Part VI ティソーの指示楕円（メルカトル図法とランベルト正積図法）
    mani05_riemann_sphere.png  Part V §3 リーマン球面：ζ 平面の格子、座標変換 1/ζ̄（裏返る）と 1/ζ（正則）
    mani06_theorema_egregium.png  Part VI §6 円柱は広げられるが球面は広げられない（三角形の内角、舟形の隙間）
    mani07_singularities.png   Part IX §1 座標特異点と真の特異点（球面の極、シュワルツシルト時空の地平線と中心）

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


# ------------------------------------------------------------------------------------- mani03
def mani03():
    """Part II：正則値定理。等位集合 x²−z²=c、球面の接平面 = ker DF、正則値は十分条件。"""
    fig = plt.figure(figsize=(17, 5.8))

    # (a) F(x,z) = x^2 - z^2 の等位集合
    ax = fig.add_subplot(1, 3, 1)
    xs = np.linspace(-2, 2, 400)
    X, Z = np.meshgrid(xs, xs)
    Fv = X**2 - Z**2
    levels = [-1.5, -0.75, 0.75, 1.5]
    cs = ax.contour(X, Z, Fv, levels=levels, colors=[C_B, C_B, C_A, C_A], linewidths=1.8)
    ax.clabel(cs, fmt=lambda v: f"$c={v:g}$", fontsize=9)
    ax.plot([-2, 2], [-2, 2], color=C_BAD, lw=2.5)
    ax.plot([-2, 2], [2, -2], color=C_BAD, lw=2.5, label="$c=0$：交わる2本の直線（多様体でない）")
    ax.plot(0, 0, "o", color=C_BAD, ms=9)
    for (px, pz) in [(1.2247, 0.0), (0.0, 1.2247), (1.0, 0.5)]:
        g = np.array([2 * px, -2 * pz])
        assert np.linalg.norm(g) > 0
        ax.annotate("", xy=(px + 0.25 * g[0], pz + 0.25 * g[1]), xytext=(px, pz),
                    arrowprops=dict(arrowstyle="-|>", color="#555", lw=1.4))
    ax.text(0.08, -0.35, "原点で $DF=0$", color=C_BAD, fontsize=10)
    ax.set_aspect("equal"), ax.set_xlim(-2, 2), ax.set_ylim(-2, 2)
    ax.set_xlabel("$x$"), ax.set_ylabel("$z$")
    ax.legend(fontsize=9, loc="lower center", bbox_to_anchor=(0.5, -0.02))
    ax.set_title("(a) $F=x^2-z^2$ の等位集合 $F^{-1}(c)$：\n$c\\neq0$ は滑らかな曲線（矢印は勾配）", fontsize=11)

    # (b) 球面の接平面 = ker DF
    ax = fig.add_subplot(1, 3, 2, projection="3d")
    u, v = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 60))
    ax.plot_surface(np.sin(u) * np.cos(v), np.sin(u) * np.sin(v), np.cos(u), color="#dbe6f2", alpha=0.4, linewidth=0)
    p = np.array([1.0, 2.0, 2.0]) / 3
    grad = 2 * p
    e1 = np.array([-2.0, 1.0, 0.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(p, e1)
    assert abs(grad @ e1) < 1e-12 and abs(grad @ e2) < 1e-12        # 接平面 = ker DF_p = {v : p·v = 0}
    s, tt = np.meshgrid(np.linspace(-0.6, 0.6, 2), np.linspace(-0.6, 0.6, 2))
    P = p[:, None, None] + e1[:, None, None] * s + e2[:, None, None] * tt
    ax.plot_surface(*P, color=C_A, alpha=0.35, linewidth=0)
    ax.quiver(*p, *(0.5 * grad), color=C_BAD, linewidth=2, arrow_length_ratio=0.2)
    ax.quiver(*p, *(0.5 * e1), color="#222", linewidth=1.5, arrow_length_ratio=0.2)
    ax.quiver(*p, *(0.5 * e2), color="#222", linewidth=1.5, arrow_length_ratio=0.2)
    ax.text(*(p + 0.55 * grad), "$\\nabla F=2p$", color=C_BAD, fontsize=11)
    ax.set_xlim(-1, 1), ax.set_ylim(-1, 1), ax.set_zlim(-1, 1)
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=20, azim=20)
    ax.set_title("(b) 球面 $F^{-1}(1)$（$F=|x|^2$）の接平面（青）：\n$T_pS^2=\\ker DF_p=\\{v:\\ p\\cdot v=0\\}$", fontsize=11)

    # (c) 正則値は十分条件
    ax = fig.add_subplot(1, 3, 3)
    r = np.linspace(0, 1.6, 400)
    ax.plot(r, r**2 - 1, color=C_A, lw=2.5, label="$F_1=r^2-1$：$r=1$ で傾き $2\\neq0$")
    ax.plot(r, (r**2 - 1) ** 2, color=C_B, lw=2.5, label="$F_2=(r^2-1)^2$：$r=1$ で傾き $0$")
    ax.axhline(0, color="#333", lw=1)
    ax.plot(1, 0, "o", color=C_BAD, ms=9)
    ax.set_xlabel("$r=\\sqrt{x^2+y^2}$"), ax.set_ylim(-1.1, 2.0)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_title("(c) どちらも $F^{-1}(0)$ は同じ単位円（多様体）。\n$F_2$ では $0$ は正則値でないが、それでも多様体", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mani03_regular_value.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mani04
def sphere_circle(lat0, lon0, rho, n=120):
    """中心（緯度 lat0、経度 lon0）から角距離 rho の、球面上の小円を (lat, lon) の配列で返す"""
    c = np.array([np.cos(lat0) * np.cos(lon0), np.cos(lat0) * np.sin(lon0), np.sin(lat0)])
    e = np.cross([0, 0, 1.0], c)
    e = e / np.linalg.norm(e) if np.linalg.norm(e) > 1e-9 else np.array([1.0, 0, 0])
    f = np.cross(c, e)
    t = np.linspace(0, 2 * np.pi, n)
    P = np.cos(rho) * c[:, None] + np.sin(rho) * (np.cos(t) * e[:, None] + np.sin(t) * f[:, None])
    assert np.allclose(np.arccos(np.clip(c @ P, -1, 1)), rho)          # 中心からの角距離が一定（球面上の円）
    return np.arcsin(P[2]), np.arctan2(P[1], P[0])


def mani04():
    """Part VI：ティソーの指示楕円。メルカトル図法（正角）とランベルト正積図法。"""
    merc = lambda lat, lon: (lon, np.log(np.tan(np.pi / 4 + lat / 2)))      # Y = -ln tan(θ/2)、θ = π/2 − 緯度
    lamb = lambda lat, lon: (lon, np.sin(lat))                              # Y = cos θ = sin(緯度)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.4), gridspec_kw=dict(width_ratios=[1, 1, 0.85]))
    rho = np.radians(7)
    centers = [(np.radians(la), np.radians(lo)) for la in (0, 30, 60, 75) for lo in (-120, -40, 40, 120)]
    for ax, proj, title, ylim in [(axes[0], merc, "(a) メルカトル図法（正角）：円は円のまま、\n高緯度ほど大きくなる", (-2.7, 2.7)),
                                  (axes[1], lamb, "(b) ランベルト正積図法：面積は同じだが、\n高緯度ほど南北につぶれる", (-1.05, 1.05))]:
        for lo in np.radians(np.arange(-180, 181, 30)):
            la = np.radians(np.linspace(-80, 80, 100))
            X, Yv = proj(la, np.full_like(la, lo))
            ax.plot(X, Yv, color="#dddddd", lw=0.8)
        for la0 in np.radians(np.arange(-75, 76, 15)):
            lo = np.radians(np.linspace(-180, 180, 200))
            X, Yv = proj(np.full_like(lo, la0), lo)
            ax.plot(X, Yv, color="#dddddd", lw=0.8)
        areas = []
        for la0, lo0 in centers:
            la, lo = sphere_circle(la0, lo0, rho)
            X, Yv = proj(la, lo)
            ax.fill(X, Yv, color=C_BAD, alpha=0.55)
            areas.append(0.5 * abs(np.dot(X, np.roll(Yv, -1)) - np.dot(Yv, np.roll(X, -1))))
        areas = np.array(areas)
        if proj is lamb:
            assert np.ptp(areas) / areas.mean() < 1e-2          # 正積：どの緯度でも面積が同じ
        else:
            eq = areas[:4].mean()
            assert abs(areas[4:8].mean() / eq - 1 / np.cos(np.radians(30)) ** 2) < 0.05   # 面積は sec²(緯度) 倍
        ax.set_xlim(-np.pi, np.pi), ax.set_ylim(*ylim)
        ax.set_xticks(np.radians([-180, -90, 0, 90, 180])), ax.set_xticklabels(["-180°", "-90°", "0°", "90°", "180°"])
        ax.set_xlabel("経度 $X=\\phi$"), ax.set_title(title, fontsize=11)
        ax.set_aspect("equal")
    axes[0].set_ylabel("$Y=\\ln\\tan(\\pi/4+\\lambda/2)$")
    axes[1].set_ylabel("$Y=\\sin\\lambda$")

    ax = axes[2]
    lat = np.linspace(0, 80, 200)
    sec = 1 / np.cos(np.radians(lat))
    ax.plot(lat, sec, color=C_A, lw=2.5, label="メルカトル：長さの倍率 $\\sec\\lambda$（東西＝南北）")
    ax.plot(lat, sec**2, color=C_A, lw=2.5, ls="--", label="メルカトル：面積の倍率 $\\sec^2\\lambda$")
    ax.plot(lat, sec, color=C_B, lw=2, ls=":", label="ランベルト：東西の倍率 $\\sec\\lambda$")
    ax.plot(lat, 1 / sec, color=C_B, lw=2, ls="-.", label="ランベルト：南北の倍率 $\\cos\\lambda$（積は1）")
    ax.axvline(72, color="#999", lw=1)
    ax.text(71, 20, "グリーンランド付近\n（緯度 72°）", fontsize=9, color="#555", ha="right")
    ax.set_yscale("log"), ax.set_xlim(0, 80), ax.set_ylim(0.15, 40)
    ax.set_xlabel("緯度 $\\lambda$ [度]"), ax.legend(fontsize=8.5, loc="upper left")
    ax.set_title("(c) 赤道に対する倍率（対数目盛り）", fontsize=11)
    fig.suptitle("ティソーの指示楕円：球面上の同じ大きさの円（半径 7°）を、それぞれの地図に写したもの（Part VI §5）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "mani04_tissot.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mani05
def mani05():
    """Part V §3：リーマン球面。ζ 平面の格子は北極を通る円になる。1/ζ̄ は裏返し、1/ζ は向きを保つ。"""
    fig = plt.figure(figsize=(20, 5.6))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.35, 1, 1, 1])

    # (a) ζ 平面の直線 u1 = c、u2 = c を球面に写す
    ax = fig.add_subplot(gs[0, 0], projection="3d")
    a, b = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(0, 2 * np.pi, 80))
    ax.plot_surface(np.sin(a) * np.cos(b), np.sin(a) * np.sin(b), np.cos(a), color="#eef2f7", alpha=0.25, linewidth=0)
    s = np.tan(np.linspace(-np.pi / 2 + 1e-3, np.pi / 2 - 1e-3, 600))      # 直線全体（両端は北極に近づく）
    Np = np.array([0, 0, 1.0])
    for c in [-2, -1, -0.5, 0, 0.5, 1, 2]:
        for k, col in [(0, C_A), (1, C_B)]:
            u = np.zeros((len(s), 2))
            u[:, k], u[:, 1 - k] = c, s
            P = sigma_N_inv(u)
            nrm = np.cross(P[100] - Np, P[400] - Np)
            assert np.allclose((P - Np) @ nrm, 0, atol=1e-9)              # 北極を通る平面の上 → 球面上の円
            ax.plot(*P.T, color=col, lw=1.3, alpha=0.9)
    ax.scatter(*Np, color=C_BAD, s=40, depthshade=False)
    ax.text(0.05, 0, 1.12, "$N$（$\\zeta=\\infty$）", color=C_BAD, fontsize=11)
    ax.scatter(0, 0, -1, color="#222", s=25, depthshade=False)
    ax.text(0.05, 0, -1.25, "$S$（$\\zeta=0$）", fontsize=10)
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=18, azim=-55)
    ax.set_title("(a) $\\zeta$ 平面の格子（青：$u_1$ 一定、橙：$u_2$ 一定）を\n球面に写すと、北極 $N$ を通る円になり、直角に交わる", fontsize=11)

    # (b)〜(d) 正方形の格子と文字 F を、1/ζ̄ と 1/ζ で写す
    z0, side = 1.6j, 0.6                       # 虚軸の上：1/ζ は拡大縮小だけ、1/ζ̄ は上下の反転（の近似）
    loc = lambda p, q: z0 + side * ((p - 0.5) + 1j * (q - 0.5))
    tt = np.linspace(0, 1, 60)
    grid = [loc(np.full_like(tt, g), tt) for g in np.linspace(0, 1, 5)] + [loc(tt, np.full_like(tt, g)) for g in np.linspace(0, 1, 5)]
    glyph = [loc(np.full_like(tt, 0.3), 0.15 + 0.7 * tt), loc(0.3 + 0.45 * tt, np.full_like(tt, 0.85)), loc(0.3 + 0.3 * tt, np.full_like(tt, 0.5))]
    edge = np.concatenate([loc(tt, 0 * tt), loc(1 + 0 * tt, tt), loc(1 - tt, 1 + 0 * tt), loc(0 * tt, 1 - tt)])   # 反時計回り

    # 座標変換の確認：1/ζ̄ は σ_S∘σ_N^{-1}、1/ζ は南極側を裏返した地図 η=(x−iy)/(1+z)
    U = np.stack([edge.real, edge.imag], axis=-1)
    P = sigma_N_inv(U)
    assert np.allclose(sigma_S(P) @ [1, 1j], 1 / np.conj(edge))
    assert np.allclose((P[:, 0] - 1j * P[:, 1]) / (1 + P[:, 2]), 1 / edge)
    assert np.isclose(-1 / z0**2, abs(1 / z0**2))                     # z0 での 1/ζ の微分は正の実数（回転なし）
    area = lambda w: 0.5 * np.sum(w.real * np.roll(w.imag, -1) - w.imag * np.roll(w.real, -1))
    assert area(edge) > 0 and area(1 / edge) > 0 and area(1 / np.conj(edge)) < 0      # 1/ζ̄ だけ向きが逆
    h = 1e-6
    for zz in edge[::25]:
        for fn, sgn in [(lambda w: 1 / w, 1), (lambda w: 1 / np.conj(w), -1)]:
            du, dv = (fn(zz + h) - fn(zz)) / h, (fn(zz + 1j * h) - fn(zz)) / h
            Jm = np.array([[du.real, dv.real], [du.imag, dv.imag]])
            assert np.isclose(abs(du), abs(dv), rtol=1e-4) and abs(np.vdot(du, dv).real) < 1e-4 * abs(du) ** 2   # 角度を保つ
            assert np.sign(np.linalg.det(Jm)) == sgn

    for ax_i, fn, title, col in [(2, lambda w: w, "(b) $\\zeta$ 平面の正方形の格子と、文字 F", "#333"),
                                 (3, lambda w: 1 / np.conj(w), "(c) $\\sigma_S$ のままの座標変換 $1/\\bar{\\zeta}$：\n角度は保つが、F が裏返る（正則でない）", C_BAD),
                                 (4, lambda w: 1 / w, "(d) 裏返した地図 $\\eta$ への座標変換 $\\eta=1/\\zeta$：\nF は裏返らない（正則）", C_A)]:
        ax = fig.add_subplot(gs[0, ax_i - 1])
        for g in grid:
            w = fn(g)
            ax.plot(w.real, w.imag, color="#aaaaaa", lw=1)
        for g in glyph:
            w = fn(g)
            ax.plot(w.real, w.imag, color=col, lw=3.5, solid_capstyle="round")
        w = fn(edge)
        cx, cy, span = w.real.mean(), w.imag.mean(), 0.62 * max(np.ptp(w.real), np.ptp(w.imag))
        ax.set_xlim(cx - span, cx + span), ax.set_ylim(cy - span, cy + span), ax.set_aspect("equal")
        ax.set_xlabel("実部"), ax.set_ylabel("虚部")
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mani05_riemann_sphere.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mani06
def mani06():
    """Part VI §6：円柱は平面に広げられるが、球面は広げられない（舟形の隙間、三角形の内角の和）。"""
    fig = plt.figure(figsize=(17, 11.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.9])

    # (a) 円柱と、その上の螺旋（測地線）
    R, cpitch, H = 1.0, 2.6 / (2 * np.pi), 2.6
    ax = fig.add_subplot(gs[0, 0], projection="3d")
    a, hh = np.meshgrid(np.linspace(0, 2 * np.pi, 60), np.linspace(0, H, 2))
    ax.plot_surface(R * np.cos(a), R * np.sin(a), hh, color="#dbe6f2", alpha=0.35, linewidth=0)
    for h0 in np.linspace(0, H, 5):
        ax.plot(R * np.cos(a[0]), R * np.sin(a[0]), np.full(60, h0), color="#aaaaaa", lw=0.8)
    for a0 in np.linspace(0, 2 * np.pi, 9)[:-1]:
        ax.plot([R * np.cos(a0)] * 2, [R * np.sin(a0)] * 2, [0, H], color="#aaaaaa", lw=0.8)
    ax.plot([R, R], [0, 0], [0, H], color=C_BAD, lw=2.5)
    s = np.linspace(0, 2 * np.pi, 300)
    helix = np.stack([R * np.cos(s), R * np.sin(s), cpitch * s], axis=-1)
    ax.plot(*helix.T, color=C_A, lw=2.5)
    ax.set_box_aspect((1, 1, 1.2)), ax.set_axis_off(), ax.view_init(elev=15, azim=-50)
    ax.set_title("(a) 円柱を、赤い線で切り開く。\n青い螺旋は、円柱の上の測地線", fontsize=11)

    # 円柱の計量：座標 (s, h) で ds² = R² ds² + dh²（平坦）、螺旋の長さは広げても同じ
    J = np.stack([np.stack([-R * np.sin(s), R * np.cos(s), 0 * s], -1), np.stack([0 * s, 0 * s, 1 + 0 * s], -1)], -2)
    G = np.einsum("nia,nja->nij", J, J)
    assert np.allclose(G, np.diag([R**2, 1.0]))
    L3 = np.sum(np.linalg.norm(np.diff(helix, axis=0), axis=1))
    assert np.isclose(L3, 2 * np.pi * np.hypot(R, cpitch), rtol=1e-4)

    # (b) 広げた円柱：長方形、螺旋は直線
    ax = fig.add_subplot(gs[0, 1])
    for h0 in np.linspace(0, H, 5):
        ax.plot([0, 2 * np.pi * R], [h0, h0], color="#aaaaaa", lw=0.8)
    for a0 in np.linspace(0, 2 * np.pi, 9):
        ax.plot([R * a0] * 2, [0, H], color="#aaaaaa", lw=0.8)
    ax.plot([0, 0], [0, H], color=C_BAD, lw=2.5), ax.plot([2 * np.pi * R] * 2, [0, H], color=C_BAD, lw=2.5)
    ax.plot(R * s, cpitch * s, color=C_A, lw=2.5)
    ax.set_aspect("equal"), ax.set_xlim(-0.3, 2 * np.pi * R + 0.3), ax.set_ylim(-0.3, H + 0.3)
    ax.set_xlabel("$R\\phi$（円周に沿った長さ）"), ax.set_ylabel("高さ $h$")
    ax.set_title("(b) 広げると、隙間も重なりもない長方形になり、\n螺旋は直線になる（長さもそのまま。$K=0$）", fontsize=11)

    # (c) 球面の三角形（八分円）
    ax = fig.add_subplot(gs[0, 2], projection="3d")
    a, b = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(0, 2 * np.pi, 80))
    ax.plot_surface(np.sin(a) * np.cos(b), np.sin(a) * np.sin(b), np.cos(a), color="#eef2f7", alpha=0.25, linewidth=0)
    a, b = np.meshgrid(np.linspace(0, np.pi / 2, 20), np.linspace(0, np.pi / 2, 20))
    ax.plot_surface(np.sin(a) * np.cos(b), np.sin(a) * np.sin(b), np.cos(a), color=C_B, alpha=0.6, linewidth=0)
    V = np.eye(3)
    angles = []
    for i in range(3):
        p, q, r_ = V[i], V[(i + 1) % 3], V[(i + 2) % 3]
        tt = np.linspace(0, np.pi / 2, 60)
        arc = np.cos(tt)[:, None] * p + np.sin(tt)[:, None] * q        # 大円の弧
        ax.plot(*arc.T, color="#333", lw=2)
        tq, tr = q - (q @ p) * p, r_ - (r_ @ p) * p                    # 頂点 p での、2辺の接ベクトル
        angles.append(np.degrees(np.arccos(tq @ tr / np.linalg.norm(tq) / np.linalg.norm(tr))))
    th_ = np.linspace(0, np.pi / 2, 400)
    area = np.trapezoid(np.sin(th_), th_) * (np.pi / 2)                  # ∬ sinθ dθ dφ
    assert np.allclose(angles, 90) and np.isclose(area, np.pi / 2, rtol=1e-5)
    assert np.isclose(np.radians(sum(angles)) - np.pi, 1.0 * area, rtol=1e-5)   # 内角の和 − π = K × 面積
    ax.set_box_aspect((1, 1, 1)), ax.set_axis_off(), ax.view_init(elev=22, azim=40)
    ax.set_title("(c) 球面の三角形（八分円）：3つの角がすべて直角で、\n内角の和は $270^\\circ$。超過分 $90^\\circ=K\\times$面積（$K=1$、面積 $\\pi/2$）", fontsize=11)

    # (d) 舟形（ゴア）に切って広げた球面
    ax = fig.add_subplot(gs[1, :])
    n = 12
    w = np.pi / n                                                       # 舟形の半分の幅
    lam = np.linspace(-np.pi / 2, np.pi / 2, 400)
    total_area = 0.0
    for k in range(n):
        xc = -np.pi + (2 * k + 1) * w
        ax.fill(np.concatenate([xc + w * np.cos(lam), xc - w * np.cos(lam[::-1])]), np.concatenate([lam, lam[::-1]]),
                color=C_A, alpha=0.35, lw=0)
        ax.plot(xc + w * np.cos(lam), lam, color=C_A, lw=1), ax.plot(xc - w * np.cos(lam), lam, color=C_A, lw=1)
        ax.plot([xc, xc], [-np.pi / 2, np.pi / 2], color="#888", lw=0.6)
        for la0 in np.radians([-60, -30, 0, 30, 60]):
            ax.plot([xc - w * np.cos(la0), xc + w * np.cos(la0)], [la0, la0], color="#888", lw=0.6)
        total_area += np.trapezoid(2 * w * np.cos(lam), lam)
    assert np.isclose(total_area, 4 * np.pi, rtol=1e-4)                 # 面積の合計は球面の面積 4π
    edge_len = np.trapezoid(np.sqrt(1 + (w * np.sin(lam)) ** 2), lam)
    assert edge_len > np.pi                                             # 舟形の縁の経線は、本当の長さ π より長い
    for la0 in [30, 60]:
        gap = 2 * np.pi - n * 2 * w * np.cos(np.radians(la0))
        assert np.isclose(gap, 2 * np.pi * (1 - np.cos(np.radians(la0))))   # 隙間の合計は枚数によらない
    ax.annotate("", xy=(-np.pi + 2 * w, np.radians(60)), xytext=(-np.pi + 2 * w + 0.45, np.radians(101)),
                arrowprops=dict(arrowstyle="-|>", color=C_BAD, lw=1.4))
    ax.text(-np.pi + 2 * w + 0.5, np.radians(101), "隙間（緯度 $60^\\circ$ で合計 $2\\pi(1-\\cos 60^\\circ)=\\pi$）", color=C_BAD, fontsize=10, va="center")
    ax.set_aspect("equal"), ax.set_xlim(-np.pi - 0.1, np.pi + 0.1), ax.set_ylim(-np.pi / 2 - 0.1, np.pi / 2 + 0.38)
    ax.set_xticks(np.radians([-180, -90, 0, 90, 180])), ax.set_xticklabels(["-180°", "-90°", "0°", "90°", "180°"])
    ax.set_yticks(np.radians([-90, -60, -30, 0, 30, 60, 90])), ax.set_yticklabels(["-90°", "-60°", "-30°", "0°", "30°", "60°", "90°"])
    ax.set_xlabel("経度"), ax.set_ylabel("緯度")
    ax.set_title("(d) 球面を 12 枚の舟形に切って広げたもの（各舟形の中央の経線と、緯線の長さ、面積は正しい）：\n"
                 "高緯度ほど隙間が開く。隙間の合計は緯度 $\\lambda$ で $2\\pi(1-\\cos\\lambda)$ で、舟形を細くしても減らない", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mani06_theorema_egregium.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mani07
def mani07():
    """Part IX §1：座標特異点と真の特異点。球面の極と、シュワルツシルト時空の地平線・中心。"""
    fig, axes = plt.subplots(1, 3, figsize=(21, 5.8), gridspec_kw=dict(width_ratios=[1.15, 1, 1]))

    # (a) 球面：√|g| は地図ごとに違うが、K=1 はどこでも同じ
    ax = axes[0]
    th = np.linspace(1e-3, np.pi - 1e-3, 400)
    sph, nN, nS = np.sin(th), 4 * np.sin(th / 2) ** 4, 4 * np.cos(th / 2) ** 4

    def vol(inv, u, h=1e-6):
        Ju = (inv(u + [h, 0]) - inv(u - [h, 0])) / (2 * h)
        Jv = (inv(u + [0, h]) - inv(u - [0, h])) / (2 * h)
        return np.sqrt(np.sum(Ju**2, -1) * np.sum(Jv**2, -1) - np.sum(Ju * Jv, -1) ** 2)

    sigma_S_inv = lambda v: (lambda s: np.concatenate([2 * v / (s + 1), (1 - s) / (s + 1)], axis=-1))(np.sum(v**2, axis=-1, keepdims=True))
    P = np.stack([np.sin(th), 0 * th, np.cos(th)], -1)
    assert np.allclose(sigma_S_inv(sigma_S(P)), P)
    assert np.allclose(vol(sigma_N_inv, sigma_N(P)), nN, rtol=1e-4, atol=1e-6)    # σ_N の地図：4/(1+|u|²)² = 4 sin⁴(θ/2)
    assert np.allclose(vol(sigma_S_inv, sigma_S(P)), nS, rtol=1e-4, atol=1e-6)    # σ_S の地図：4 cos⁴(θ/2)
    deg = np.degrees(th)
    ax.plot(deg, sph, color="#333", lw=2.5, label="球座標 $(\\theta,\\phi)$：$\\sin\\theta$（両極で 0）")
    ax.plot(deg, nN, color=C_A, lw=2.2, ls="--", label="地図 $\\sigma_N$：$4\\sin^4(\\theta/2)$（北極は地図の外）")
    ax.plot(deg, nS, color=C_B, lw=2.2, ls="-.", label="地図 $\\sigma_S$：$4\\cos^4(\\theta/2)$（南極は地図の外）")
    ax.axhline(1, color=C_BAD, lw=2.5, label="ガウス曲率 $K=1$（座標によらない）")
    ax.set_xlim(0, 180), ax.set_ylim(-0.1, 4.9), ax.set_xticks([0, 45, 90, 135, 180])
    ax.set_xticklabels(["0°\n北極", "45°", "90°\n赤道", "135°", "180°\n南極"])
    ax.set_xlabel("北極からの角度 $\\theta$"), ax.legend(fontsize=9, loc="upper center")
    ax.set_title("(a) 単位球面：体積要素 $\\sqrt{|g|}$ は地図ごとに違い、0 になる点も違う。\n"
                 "どの点も、どれかの地図では普通の点で、$K$ も一定 → 極は座標特異点", fontsize=11)

    # (b) シュワルツシルト時空（r_s = 1 の単位）
    ax = axes[1]
    f = lambda r: 1 - 1 / r
    rng = np.random.default_rng(1)
    for _ in range(20):
        r0, dv, dr = rng.uniform(0.3, 3), rng.normal(), rng.normal()
        dt = dv - dr / f(r0)                                            # EF 座標 v = t + r*（dr*/dr = 1/f）
        assert np.isclose(-f(r0) * dt**2 + dr**2 / f(r0), -f(r0) * dv**2 + 2 * dv * dr)
    for r in [np.linspace(0.3, 0.995, 200), np.linspace(1.005, 3, 300)]:
        ax.plot(r, 1 / f(r), color=C_B, lw=2.5, label="シュワルツシルト座標の $g_{rr}=1/(1-r_s/r)$" if r[0] > 1 else None)
    r = np.linspace(0.3, 3, 400)
    ax.plot(r, -f(r), color=C_A, lw=2.2, ls="--", label="EF 座標の $g_{vv}=-(1-r_s/r)$（$g_{vr}=1$）：有限")
    ax.axvline(1, color="#777", lw=1.2, ls=":")
    ax.text(1.04, -4.6, "地平線 $r=r_s$", color="#555", fontsize=10)
    ax.set_xlim(0.3, 3), ax.set_ylim(-5.5, 8), ax.axhline(0, color="#ccc", lw=0.8)
    ax.set_xlabel("$r/r_s$"), ax.legend(fontsize=9, loc="upper right")
    ax.set_title("(b) シュワルツシルト時空の計量の成分（$r_s=1$ の単位）：\n"
                 "$g_{rr}$ は地平線で発散するが、EF 座標の成分は有限 → 座標特異点", fontsize=11)

    # (c) 曲率の不変量（対数目盛り）
    ax = axes[2]
    r = np.geomspace(0.05, 3, 400)
    kr = 12 / r**6
    assert np.isclose(np.interp(1.0, r, kr), 12, rtol=1e-3)
    ax.loglog(r, kr, color=C_BAD, lw=2.5, label="$R_{abcd}R^{abcd}=12r_s^2/r^6$（どの座標でも同じ値）")
    ax.axvline(1, color="#777", lw=1.2, ls=":")
    ax.plot(1, 12, "o", color=C_BAD, ms=8)
    ax.text(0.92, 2.5, "地平線 $r=r_s$ で $12/r_s^4$（有限）", color="#555", fontsize=10, ha="right")
    ax.text(0.12, 3e7, "$r\\to0$ で発散", color=C_BAD, fontsize=10)
    ax.set_xlim(0.05, 3), ax.set_xlabel("$r/r_s$（対数目盛り）"), ax.legend(fontsize=9, loc="upper right")
    ax.set_title("(c) 曲率の不変量（対数目盛り）：$r=r_s$ では有限、\n$r\\to0$ で発散 → 真の特異点は $r=0$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mani07_singularities.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(mani01=mani01, mani02=mani02, mani03=mani03, mani04=mani04, mani05=mani05, mani06=mani06, mani07=mani07)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
