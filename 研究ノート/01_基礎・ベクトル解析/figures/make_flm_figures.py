"""functions_linear_maps_derivatives_integrals.md（関数・線形写像・微分・積分のノート）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_flm_figures.py            # すべて
    uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_flm_figures.py flm02      # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    flm01_injective_surjective.png   Part I §4 単射・全射・全単射の矢印図
    flm02_restriction_inverse.png    Part I §7 制限して全単射にし、逆写像を作る（√, arcsin, ln）
    flm03_polar_map.png              Part I §8 極座標の写像：どこで単射が崩れるか
    flm04_kernel_image.png           Part II 正則・非正則な行列、核と像、Ax=b の解の集合

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


FIGS = dict(flm01=flm01, flm02=flm02, flm03=flm03, flm04=flm04)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
