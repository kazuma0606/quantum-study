"""functions_linear_maps_derivatives_integrals.md（関数・線形写像・微分・積分のノート）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_flm_figures.py            # すべて
    uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_flm_figures.py flm02      # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    flm01_injective_surjective.png   Part I §4 単射・全射・全単射の矢印図
    flm02_restriction_inverse.png    Part I §7 制限して全単射にし、逆写像を作る（√, arcsin, ln）
    flm03_polar_map.png              Part I §8 極座標の写像：どこで単射が崩れるか
    flm04_kernel_image.png           Part II 正則・非正則な行列、核と像、Ax=b の解の集合
    flm05_inverse_function.png       Part III 逆関数定理の条件と、局所と大域の違い
    flm06_change_of_variables.png    Part V 変数変換 dx dy = r dr dθ の意味
    flm07_matrix_exponential.png     Part VIII 行列指数関数：局所と大域、det e^{tA} = e^{t tr A}

各図は、描く値が本文の主張と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_ARROW, C_BAD = "#1f77b4", "#e67e00", "#555555", "#d62728"


# ------------------------------------------------------------------------------------- flm01
def flm01():
    """有限集合の矢印図。逆像の要素の個数（≤1 / ≥1 / =1）で分類する。"""
    cases = [
        ("単射でも全射でもない", [0, 0, 2], 3, [1, 3]),
        ("単射（全射でない）", [0, 1, 3], 4, []),
        ("全射（単射でない）", [0, 1, 1, 2], 3, []),
        ("全単射", [2, 0, 1], 3, []),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.6))
    for ax, (title, f, nB, _) in zip(axes, cases):
        nA = len(f)
        yA = np.linspace(0.8, 0.2, nA) if nA > 1 else [0.5]
        yB = np.linspace(0.8, 0.2, nB)
        ax.add_patch(Ellipse((0.2, 0.5), 0.26, 0.9, fc="#e8f1fa", ec=C_A, lw=1.5))
        ax.add_patch(Ellipse((0.8, 0.5), 0.26, 0.9, fc="#fdf0e2", ec=C_B, lw=1.5))
        ax.text(0.2, 0.99, "$A$（定義域）", ha="center", fontsize=11)
        ax.text(0.8, 0.99, "$B$（終域）", ha="center", fontsize=11)
        counts = np.bincount(f, minlength=nB)
        for i, j in enumerate(f):
            ax.add_patch(FancyArrowPatch((0.24, yA[i]), (0.76, yB[j]), arrowstyle="-|>", mutation_scale=14, color=C_ARROW, lw=1.4))
        for i in range(nA):
            ax.plot(0.2, yA[i], "o", color=C_A, ms=9)
        for j in range(nB):
            bad = counts[j] != 1
            ax.plot(0.8, yB[j], "o", color=C_BAD if bad else C_B, ms=9)
            ax.text(0.87, yB[j], f"{counts[j]}", va="center", fontsize=11, color=C_BAD if bad else "#333")
        injective = counts.max() <= 1
        surjective = counts.min() >= 1
        expect = {"単射でも全射でもない": (False, False), "単射（全射でない）": (True, False),
                  "全射（単射でない）": (False, True), "全単射": (True, True)}[title]
        assert (injective, surjective) == expect
        ax.set_title(title, fontsize=13, pad=22)
        ax.set_xlim(0, 1.0), ax.set_ylim(0, 1.05), ax.axis("off")
    fig.suptitle("右の数字は、$B$ の各要素の逆像の要素の個数。単射 ⇔ すべて $\\leq1$、全射 ⇔ すべて $\\geq1$、全単射 ⇔ すべて $=1$（赤は条件を破る要素）",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "flm01_injective_surjective.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- flm02
def flm02():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.4))
    specs = [
        ("$x^2$ を $[0,\\infty)$ に制限 → 逆写像 $\\sqrt{x}$", lambda x: x**2, np.sqrt, (-2, 2), (0, 2), (0, 4),
         "$\\mathbb{R}$ 全体では $x$ と $-x$ が同じ値", (-2.2, 4.2)),
        ("$\\sin x$ を $[-\\pi/2,\\pi/2]$ に制限 → 逆写像 $\\arcsin x$", np.sin, np.arcsin, (-np.pi, np.pi), (-np.pi / 2, np.pi / 2), (-1, 1),
         "周期的なので、$\\mathbb{R}$ 全体では単射でない", (-3.4, 3.4)),
        ("$e^x$ の終域を $(0,\\infty)$ にする → 逆写像 $\\ln x$", np.exp, np.log, (-2.5, 1.4), (-2.5, 1.4), (np.exp(-2.5), np.exp(1.4)),
         "終域 $\\mathbb{R}$ では、$0$ 以下の値を取らない", (-2.8, 4.2)),
    ]
    for ax, (title, f, finv, full, dom, img, note, lim) in zip(axes, specs):
        xs = np.linspace(*full, 400)
        ax.plot(xs, f(xs), color="#bbbbbb", lw=2, label="元の写像（全体）")
        xr = np.linspace(*dom, 300)
        ax.plot(xr, f(xr), color=C_A, lw=3, label="制限した写像（全単射）")
        yr = np.linspace(img[0] + 1e-9, img[1], 300)
        ax.plot(yr, finv(yr), color=C_B, lw=3, label="逆写像")
        assert np.allclose(f(finv(yr)), yr) and np.allclose(finv(f(xr)), xr, atol=1e-7)   # 互いに逆
        t = np.linspace(*lim, 2)
        ax.plot(t, t, color="#999", ls="--", lw=1, label="$y=x$（グラフの折り返しの軸）")
        ax.axhline(0, color="#ddd", lw=1, zorder=0), ax.axvline(0, color="#ddd", lw=1, zorder=0)
        ax.set_xlim(*lim), ax.set_ylim(*lim), ax.set_aspect("equal")
        ax.set_title(title, fontsize=11)
        ax.text(0.03, 0.97, note, transform=ax.transAxes, fontsize=10, va="top", color="#555")
        ax.legend(fontsize=9, loc="lower right")
    fig.suptitle("定義域を制限するか終域を取り替えて全単射にすると、逆写像が作れる。逆写像のグラフは、$y=x$ に関する折り返し（Part I §7）",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(OUT / "flm02_restriction_inverse.png", dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


# ------------------------------------------------------------------------------------- flm03
def flm03():
    P = lambda r, th: (r * np.cos(th), r * np.sin(th))
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw=dict(width_ratios=[1.15, 1]))

    # 左：(r, θ) 平面
    ax.axvspan(-np.pi, np.pi, color="#e8f1fa", zorder=0)
    for th0 in np.linspace(-2 * np.pi, 2 * np.pi, 17):
        ax.plot([th0, th0], [0, 2], color="#cccccc", lw=0.8)
    for r0 in np.linspace(0, 2, 9):
        ax.plot([-2 * np.pi, 2 * np.pi], [r0, r0], color="#cccccc", lw=0.8)
    ax.plot([-2 * np.pi - 0.3, 2 * np.pi + 0.8], [0, 0], color=C_BAD, lw=3, label="$r=0$ の線（すべて原点に写る）")
    pts = [(np.pi / 6, 1.2, "o"), (np.pi / 6 + 2 * np.pi, 1.2, "o"), (np.pi / 6 - 2 * np.pi, 1.2, "o")]
    for th0, r0, m in pts:
        ax.plot(th0, r0, m, color=C_B, ms=9)
    ax.plot([], [], "o", color=C_B, ms=9, label="$\\theta$ が $2\\pi$ ずつ違う点（同じ点に写る）")
    ax.plot([np.pi, np.pi], [0, 2], color="#7b2fbf", lw=2.5, ls="--", label="$\\theta=\\pm\\pi$（除く半直線に写る）")
    ax.plot([-np.pi, -np.pi], [0, 2], color="#7b2fbf", lw=2.5, ls="--")
    ax.text(0, 1.88, "制限した範囲\n$r>0,\\ -\\pi<\\theta<\\pi$", ha="center", va="top", fontsize=10, color=C_A)
    ax.set_xlim(-2 * np.pi - 0.3, 2 * np.pi + 0.8), ax.set_ylim(-0.15, 2.0)
    ax.set_xticks(np.arange(-2, 3) * np.pi), ax.set_xticklabels(["$-2\\pi$", "$-\\pi$", "$0$", "$\\pi$", "$2\\pi$"])
    ax.set_xlabel("$\\theta$"), ax.set_ylabel("$r$")
    ax.legend(fontsize=9, loc="lower left", bbox_to_anchor=(0.0, 0.08))
    ax.set_title("定義域：$(r,\\theta)$ 平面", fontsize=12)

    # 右：(x, y) 平面
    for th0 in np.linspace(-np.pi, np.pi, 9):
        x, y = P(np.linspace(0, 2, 50), th0)
        bx.plot(x, y, color="#cccccc", lw=0.8)
    for r0 in np.linspace(0.25, 2, 8):
        x, y = P(r0, np.linspace(-np.pi, np.pi, 200))
        bx.plot(x, y, color="#cccccc", lw=0.8)
    x, y = P(1.2, np.pi / 6)
    bx.plot(x, y, "o", color=C_B, ms=9)
    bx.annotate("3つの点が\nすべてここに写る", (x, y), (x + 0.15, y + 0.45), fontsize=10, color=C_B,
                arrowprops=dict(arrowstyle="-", color=C_B))
    bx.plot(0, 0, "o", color=C_BAD, ms=10)
    bx.text(0.1, -0.42, "$r=0$ の線\n全体がここに", fontsize=10, color=C_BAD)
    bx.plot([-2, 0], [0, 0], color="#7b2fbf", lw=3, ls="--", label="除く半直線（$\\theta$ が $\\pi$ と $-\\pi$ で跳ぶ）")
    # 逆写像の確認：除いた範囲の外では、(x, y) → (r, θ) → (x, y) が元に戻る
    rng = np.random.default_rng(1)
    for _ in range(200):
        xx, yy = rng.uniform(-2, 2, 2)
        if yy == 0 and xx <= 0:
            continue
        r, th = np.hypot(xx, yy), np.arctan2(yy, xx)
        assert r > 0 and -np.pi < th <= np.pi and np.allclose(P(r, th), (xx, yy))
    bx.set_xlim(-2.2, 2.2), bx.set_ylim(-2.2, 2.2), bx.set_aspect("equal")
    bx.set_xlabel("$x$"), bx.set_ylabel("$y$")
    bx.legend(fontsize=9, loc="lower right")
    bx.set_title("終域：$(x,y)$ 平面", fontsize=12)
    fig.suptitle("極座標の写像 $(r,\\theta)\\mapsto(r\\cos\\theta,\\ r\\sin\\theta)$：単射が崩れる場所と、全単射にするための制限（Part I §8）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "flm03_polar_map.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- flm04
def flm04():
    """Part II：正則な行列（面積が |det| 倍）、正則でない行列（核と像）、Ax=b の解の集合（特解＋核）。"""
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6))
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], float)
    g = np.linspace(-3, 3, 13)

    # (a) 正則
    ax = axes[0]
    A = np.array([[2.0, 1.0], [0.5, 1.5]])
    for c in g:
        for P in (np.c_[np.full(50, c), np.linspace(-3, 3, 50)], np.c_[np.linspace(-3, 3, 50), np.full(50, c)]):
            Q = P @ A.T
            ax.plot(Q[:, 0], Q[:, 1], color="#dddddd", lw=0.8)
    ax.fill(sq[:, 0], sq[:, 1], color=C_A, alpha=0.35)
    S = sq @ A.T
    ax.fill(S[:, 0], S[:, 1], color=C_B, alpha=0.45)
    area = 0.5 * abs(np.dot(S[:-1, 0], np.roll(S[:-1, 1], -1)) - np.dot(S[:-1, 1], np.roll(S[:-1, 0], -1)))
    assert np.isclose(area, abs(np.linalg.det(A)))
    ax.text(0.5, 0.5, "面積 1", ha="center", va="center", fontsize=10)
    ax.text(*(S[:-1].mean(axis=0) + [0.35, 0.25]), f"面積 $|\\det A|={abs(np.linalg.det(A)):g}$", ha="center", fontsize=10)
    ax.set_title("$\\det A\\neq0$：全単射。正方形は平行四辺形に写り、\n面積は $|\\det A|$ 倍", fontsize=11)
    ax.set_xlim(-1, 4), ax.set_ylim(-1, 3), ax.set_aspect("equal")
    ax.text(0.02, 0.02, "$A$ の行：$(2,\\ 1)$、$(0.5,\\ 1.5)$", transform=ax.transAxes, fontsize=11)

    # (b) 正則でない：核と像
    ax = axes[1]
    B = np.array([[1.0, 2.0], [2.0, 4.0]])
    assert abs(np.linalg.det(B)) < 1e-12
    k = np.array([-2.0, 1.0]) / np.sqrt(5)       # 核の向き
    im = np.array([1.0, 2.0]) / np.sqrt(5)       # 像の向き
    assert np.allclose(B @ k, 0)
    ts = np.linspace(-4, 4, 2)
    ax.plot(ts * k[0], ts * k[1], color=C_BAD, lw=3, label="核 $\\ker B$（すべて $0$ に写る）")
    ax.plot(ts * im[0], ts * im[1], color=C_B, lw=3, label="像 $\\mathrm{im}\\,B$（平面全体がこの直線に）")
    S = sq @ B.T
    ax.fill(sq[:, 0], sq[:, 1], color=C_A, alpha=0.35, label="正方形")
    ax.plot(S[:, 0], S[:, 1], color=C_B, lw=6, alpha=0.5, solid_capstyle="round")
    for s in [-1.5, -0.75, 0.75, 1.5]:
        ax.plot(*(s * k), "o", color=C_BAD, ms=6)
    ax.plot(0, 0, "o", color="#222", ms=7)
    ax.set_title("$\\det B=0$：単射でも全射でもない。核の方向が\nつぶれ、平面が直線に写る（面積 0）", fontsize=11)
    ax.set_xlim(-2.5, 3.5), ax.set_ylim(-2, 3), ax.set_aspect("equal")
    ax.legend(fontsize=9, loc="lower right")
    ax.text(0.02, 0.92, "$B$ の行：$(1,\\ 2)$、$(2,\\ 4)$", transform=ax.transAxes, fontsize=11)

    # (c) Bx = b の解の集合
    ax = axes[2]
    b = np.array([3.0, 6.0])
    xp = np.array([3.0, 0.0])
    assert np.allclose(B @ xp, b)
    for s in np.linspace(-2, 2, 5):
        assert np.allclose(B @ (xp + s * np.array([-2.0, 1.0])), b)
    ts = np.linspace(-8, 8, 2)
    ax.plot(ts * k[0], ts * k[1], color=C_BAD, lw=2, ls="--", label="核（$Bx=0$ の解）")
    line = xp + np.outer(np.linspace(-8, 8, 2), k)
    ax.plot(line[:, 0], line[:, 1], color="#7b2fbf", lw=3, label="$Bx=b$ の解（特解＋核）")
    ax.plot(*xp, "o", color="#7b2fbf", ms=8)
    ax.annotate("特解 $x_p=(3,0)$", xp, xp + [0.1, 0.5], fontsize=10, color="#7b2fbf")
    ax.annotate("", xy=xp, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#7b2fbf", lw=1.5))
    ax.plot(0, 0, "o", color="#222", ms=6)
    ax.set_title("$Bx=b$（$b=(3,6)$）の解は、核を特解の分だけ\n平行移動した直線", fontsize=11)
    ax.set_xlim(-2.5, 4.5), ax.set_ylim(-2, 3), ax.set_aspect("equal")
    ax.legend(fontsize=9, loc="lower left")
    for ax in axes:
        ax.axhline(0, color="#eee", lw=1, zorder=0), ax.axvline(0, color="#eee", lw=1, zorder=0)
    fig.tight_layout()
    fig.savefig(OUT / "flm04_kernel_image.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- flm05
def flm05():
    """Part III：逆関数定理の条件と、局所と大域の違い。"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 11))

    # (a) f(x) = x + 2x^2 sin(1/x) の導関数
    ax = axes[0, 0]
    fp = lambda x: 1 + 4 * x * np.sin(1 / x) - 2 * np.cos(1 / x)
    xs = np.concatenate([np.linspace(-0.1, -1e-5, 400001), np.linspace(1e-5, 0.1, 400001)])
    ax.plot(xs, fp(xs), color=C_A, lw=0.4)
    ax.plot(0, 1, "o", color=C_BAD, ms=8, zorder=5)
    ax.axhline(0, color="#333", lw=1)
    for n in (5, 10, 20):
        xn = 1 / (2 * np.pi * n)
        assert np.isclose(fp(xn), -1.0)          # 0 のいくらでも近くで f' = -1 < 0
    ax.annotate("$f'(0)=1$", (0, 1), (0.02, 2.2), fontsize=12, color=C_BAD, arrowprops=dict(arrowstyle="-|>", color=C_BAD))
    ax.set_xlim(-0.1, 0.1), ax.set_ylim(-1.6, 3.6)
    ax.set_xlabel("$x$"), ax.set_ylabel("$f'(x)$")
    ax.set_title("(a) $f(x)=x+2x^2\\sin(1/x)$ の導関数：$f'(0)=1$ だが、\n$0$ のすぐ近くで $f'<0$ になる（$C^1$ でない → 局所的にも単射でない）", fontsize=11)

    # (b) x^3 と 立方根
    ax = axes[0, 1]
    xx = np.linspace(-1.4, 1.4, 400)
    ax.plot(xx, xx**3, color=C_A, lw=3, label="$f(x)=x^3$（$f'(0)=0$）")
    yy = np.linspace(-1.4, 1.4, 4001)
    ax.plot(yy, np.cbrt(yy), color=C_B, lw=3, label="逆写像 $\\sqrt[3]{y}$（$y=0$ で微分できない）")
    assert np.allclose(np.cbrt(yy) ** 3, yy)
    ax.plot([0, 0], [-0.5, 0.5], color=C_BAD, lw=2, ls=":", label="$y=0$ での接線は垂直")
    ax.plot(xx, xx, color="#999", ls="--", lw=1)
    ax.axhline(0, color="#ddd", lw=1, zorder=0), ax.axvline(0, color="#ddd", lw=1, zorder=0)
    ax.set_xlim(-1.4, 1.4), ax.set_ylim(-1.4, 1.4), ax.set_aspect("equal")
    ax.legend(fontsize=9, loc="lower right")
    ax.set_title("(b) $\\det J=0$ でも全単射のことはある。\nただし逆写像は微分できない（逆関数定理の結論が崩れる）", fontsize=11)

    # (c)(d) 複素指数関数 (u, v) -> (e^u cos v, e^u sin v)
    E = lambda u, v: (np.exp(u) * np.cos(v), np.exp(u) * np.sin(v))
    ax, bx = axes[1, 0], axes[1, 1]
    us = np.linspace(-1.0, 0.6, 9)
    strips = [((-np.pi, np.pi), C_A, "-"), ((np.pi, 3 * np.pi), C_B, "--")]
    for (v0, v1), col, ls in strips:
        ax.fill_between([-1.0, 0.6], v0, v1, color=col, alpha=0.15)
        for vv in np.linspace(v0, v1, 9):
            ax.plot([-1.0, 0.6], [vv, vv], color=col, lw=0.8)
            X, Y = E(np.linspace(-1.0, 0.6, 60), vv)
            bx.plot(X, Y, color=col, lw=1.4 if ls == "-" else 1.0, ls=ls)
        for u0 in us:
            ax.plot([u0, u0], [v0, v1], color=col, lw=0.8)
            X, Y = E(u0, np.linspace(v0, v1, 200))
            bx.plot(X, Y, color=col, lw=1.4 if ls == "-" else 1.0, ls=ls)
    p = (0.2, 0.7)
    q = (0.2, 0.7 + 2 * np.pi)
    ax.plot(*p, "o", color=C_A, ms=9), ax.plot(*q, "o", color=C_B, ms=9)
    assert np.allclose(E(*p), E(*q))
    bx.plot(*E(*p), "o", color="#222", ms=9)
    bx.annotate("2つの点が\n同じ点に写る", E(*p), (E(*p)[0] + 0.3, E(*p)[1] + 0.5), fontsize=10,
                arrowprops=dict(arrowstyle="-|>", color="#222"))
    ax.set_xlabel("$u$"), ax.set_ylabel("$v$")
    ax.set_yticks(np.arange(-1, 4) * np.pi), ax.set_yticklabels(["$-\\pi$", "$0$", "$\\pi$", "$2\\pi$", "$3\\pi$"])
    ax.set_title("(c) 定義域：高さ $2\\pi$ の帯（青と橙）", fontsize=11)
    bx.set_aspect("equal"), bx.set_xlim(-2.1, 2.1), bx.set_ylim(-2.1, 2.1)
    bx.set_title("(d) $(u,v)\\mapsto(e^u\\cos v,\\ e^u\\sin v)$：どちらの帯も、同じ円環を覆う\n$\\det J=e^{2u}\\neq0$（どこでも局所的に全単射）だが、全体では単射でない", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "flm05_inverse_function.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- flm06
def flm06():
    """Part V：変数変換。(r, θ) の小さな長方形は、面積 ≈ r Δr Δθ の小片に写る。"""
    P = lambda r, th: np.stack([r * np.cos(th), r * np.sin(th)], -1)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw=dict(width_ratios=[1, 1.05]))
    dr, dth = 0.25, np.pi / 12
    rs = np.arange(0, 2.0 + 1e-9, dr)
    ths = np.arange(0, np.pi / 2 + 1e-9, dth)
    for r0 in rs:
        ax.plot([0, np.pi / 2], [r0, r0], color="#cccccc", lw=0.8)
        Q = P(r0, np.linspace(0, np.pi / 2, 100))
        bx.plot(Q[:, 0], Q[:, 1], color="#cccccc", lw=0.8)
    for t0 in ths:
        ax.plot([t0, t0], [0, 2], color="#cccccc", lw=0.8)
        Q = P(np.linspace(0, 2, 50), t0)
        bx.plot(Q[:, 0], Q[:, 1], color="#cccccc", lw=0.8)
    cells = [(0.25, 2 * dth, C_A), (1.0, 2 * dth, C_B), (1.75, 2 * dth, C_BAD), (1.0, 4 * dth, "#2ca02c")]
    rows = []
    for r0, t0, col in cells:
        s = np.linspace(0, 1, 60)
        edge = np.concatenate([np.c_[r0 + s * dr, np.full(60, t0)], np.c_[np.full(60, r0 + dr), t0 + s * dth],
                               np.c_[r0 + dr - s * dr, np.full(60, t0 + dth)], np.c_[np.full(60, r0), t0 + dth - s * dth]])
        ax.fill(edge[:, 1], edge[:, 0], color=col, alpha=0.6)
        img = P(edge[:, 0], edge[:, 1])
        bx.fill(img[:, 0], img[:, 1], color=col, alpha=0.6)
        area = shoelace_area(img)
        rc = r0 + dr / 2
        assert abs(area - rc * dr * dth) < 1e-6           # 面積は (中心の r) × Δr × Δθ（極座標では、ちょうど一致する）
        rows.append((r0, col, area, rc * dr * dth))
        c = img.mean(axis=0)
        bx.annotate(f"{area:.3f}", c, c + np.array([0.18, 0.12]), fontsize=10, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.8))
    ax.text(0.03, 1.93, f"どの長方形も面積 $\\Delta r\\,\\Delta\\theta={dr * dth:.3f}$", fontsize=10, va="top")
    ax.set_xlim(0, np.pi / 2), ax.set_ylim(0, 2)
    ax.set_xticks([0, np.pi / 6, np.pi / 3, np.pi / 2]), ax.set_xticklabels(["$0$", "$\\pi/6$", "$\\pi/3$", "$\\pi/2$"])
    ax.set_xlabel("$\\theta$"), ax.set_ylabel("$r$")
    ax.set_title("定義域 $(r,\\theta)$：同じ大きさの長方形", fontsize=12)
    bx.set_xlim(-0.05, 2.1), bx.set_ylim(-0.05, 2.1), bx.set_aspect("equal")
    bx.set_xlabel("$x$"), bx.set_ylabel("$y$")
    txt = "写った小片の面積（数字）$=r\\,\\Delta r\\,\\Delta\\theta$\n$r$ は小片の中心の半径。原点に近いほど小さい"
    bx.text(0.03, 0.97, txt, transform=bx.transAxes, fontsize=10, va="top", bbox=dict(boxstyle="round", fc="white", ec="#ccc"))
    bx.set_title("像 $(x,y)$：面積は $|\\det J|=r$ 倍になる", fontsize=12)
    fig.suptitle("変数変換 $dx\\,dy=r\\,dr\\,d\\theta$ の意味（Part V §5）", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "flm06_change_of_variables.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- flm07
def flm07():
    """Part VIII：行列指数関数。回転の生成子での局所と大域、det e^{tA} = e^{t tr A}。"""
    from scipy.linalg import expm, logm

    J = np.array([[0.0, -1.0], [1.0, 0.0]])
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.4))

    # (a) t ↦ e^{tJ} の成分
    ax = axes[0]
    ts = np.linspace(0, 4 * np.pi, 600)
    E = np.array([expm(t * J) for t in ts])
    assert np.allclose(E[:, 0, 0], np.cos(ts)) and np.allclose(E[:, 1, 0], np.sin(ts))
    ax.plot(ts, E[:, 0, 0], color=C_A, lw=2.5, label="$(e^{tJ})_{11}=\\cos t$")
    ax.plot(ts, E[:, 1, 0], color=C_B, lw=2.5, label="$(e^{tJ})_{21}=\\sin t$")
    for k in range(3):
        assert np.allclose(expm(2 * np.pi * k * J), np.eye(2))
        ax.plot(2 * np.pi * k, 1, "o", color=C_BAD, ms=9, zorder=5)
    ax.text(2 * np.pi, 1.12, "$t=0,\\ 2\\pi,\\ 4\\pi$ で、どれも $e^{tJ}=I$", ha="center", fontsize=10, color=C_BAD)
    ax.set_xticks(np.arange(0, 5) * np.pi), ax.set_xticklabels(["$0$", "$\\pi$", "$2\\pi$", "$3\\pi$", "$4\\pi$"])
    ax.set_ylim(-1.3, 1.4), ax.set_xlabel("$t$")
    ax.legend(fontsize=9, loc="lower left")
    ax.set_title("(a) $t\\mapsto e^{tJ}$（回転）：$e^{2\\pi J}=e^{0}=I$ で、\n$\\exp$ は全体では単射でない", fontsize=11)

    # (b) log(e^{tJ}) の係数
    ax = axes[1]
    ts2 = np.linspace(-2 * np.pi + 0.01, 2 * np.pi - 0.01, 801)
    coef = np.array([logm(expm(t * J)).real[1, 0] for t in ts2])
    inside = np.abs(ts2) < np.pi - 1e-6
    assert np.allclose(coef[inside], ts2[inside], atol=1e-6)            # (-π, π) では log(e^{tJ}) = tJ
    ax.axvspan(-np.pi, np.pi, color="#cde6c7", alpha=0.6, label="$\\log(e^{tJ})=tJ$ となる範囲 $|t|<\\pi$")
    ax.plot(ts2, ts2, color="#999", ls="--", lw=1, label="$t$（元の係数）")
    jump = np.where(np.abs(np.diff(coef)) > 1)[0]
    segs = np.split(np.arange(len(ts2)), jump + 1)
    for i, sg in enumerate(segs):
        ax.plot(ts2[sg], coef[sg], color=C_A, lw=2.5, label="$\\log(e^{tJ})$ の係数（主値）" if i == 0 else None)
    ax.set_xticks(np.arange(-2, 3) * np.pi), ax.set_xticklabels(["$-2\\pi$", "$-\\pi$", "$0$", "$\\pi$", "$2\\pi$"])
    ax.set_yticks(np.arange(-2, 3) * np.pi), ax.set_yticklabels(["$-2\\pi$", "$-\\pi$", "$0$", "$\\pi$", "$2\\pi$"])
    ax.set_xlabel("$t$"), ax.legend(fontsize=9, loc="upper left")
    ax.set_title("(b) 対数は、$0$ の近くでだけ $\\exp$ の逆写像になる\n（逆関数定理の「局所的な」逆写像）", fontsize=11)

    # (c) det e^{tA} と e^{t tr A}
    ax = axes[2]
    rng = np.random.default_rng(7)
    A = rng.normal(size=(3, 3)) * 0.6
    ts3 = np.linspace(-1.5, 1.5, 200)
    d1 = np.array([np.linalg.det(expm(t * A)) for t in ts3])
    d2 = np.exp(ts3 * np.trace(A))
    assert np.allclose(d1, d2, rtol=1e-9)
    ax.plot(ts3, d1, color=C_A, lw=5, alpha=0.5, label="$\\det e^{tA}$")
    ax.plot(ts3, d2, color=C_BAD, lw=1.8, ls="--", label="$e^{t\\,\\mathrm{tr}A}$")
    ax.plot(ts3, 1 + ts3 * np.trace(A), color="#7b2fbf", lw=1.5, ls=":", label="$t=0$ での接線 $1+t\\,\\mathrm{tr}A$")
    ax.set_xlabel("$t$"), ax.set_ylim(0, max(d1.max(), 1) * 1.05)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_title(f"(c) $\\det e^{{tA}}=e^{{t\\,\\mathrm{{tr}}A}}$（ランダムな $3\\times3$ 行列、$\\mathrm{{tr}}A={np.trace(A):.2f}$）。\n$t=0$ での傾き $\\mathrm{{tr}}A$ が $D\\det_I[A]$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "flm07_matrix_exponential.png", dpi=150)
    plt.close(fig)


def shoelace_area(Pts):
    x, y = Pts[:, 0], Pts[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


FIGS = dict(flm01=flm01, flm02=flm02, flm03=flm03, flm04=flm04, flm05=flm05, flm06=flm06, flm07=flm07)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
