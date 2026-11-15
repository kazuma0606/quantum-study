"""「1 多変数の微分」（01_多変数の微分.md）の図を作る。

実行: uv run --no-sync python 書籍/微分/figures/make_01_figures.py [mv01 mv02]

出力:
    mv01_tangent_plane.png  §1・§2 地形 z = 10 - x² - 2y²。
                            (a) 曲面と、点 (1, 1, 7) での接平面。
                            (b) 等高線の地図と、点 (1, 1) での3つの向き（東、北、いちばん急な上り）。
    mv02_descent_counter.png §6・コラム
                            (a) f = (x-1)² + 2(y+1)² の等高線と、(0, 0) から学習率 0.1 で10歩の勾配降下法。
                            (b) コラムの関数 xy/(x²+y²) の値の地図（原点を通る直線の上で値が一定）。
"""

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"


def f(x, y):
    return 10 - x**2 - 2 * y**2


def mv01():
    fig = plt.figure(figsize=(12, 5.6))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    xs = np.linspace(-2, 2, 60)
    ys = np.linspace(-1.6, 1.6, 60)
    X, Y = np.meshgrid(xs, ys)
    ax1.plot_surface(X, Y, f(X, Y), cmap="viridis", alpha=0.6, linewidth=0)
    # 接平面 z = 7 - 2(x-1) - 4(y-1)、(1,1) のまわりだけ
    px, py = np.meshgrid(np.linspace(0.4, 1.6, 10), np.linspace(0.5, 1.5, 10))
    pz = 7 - 2 * (px - 1) - 4 * (py - 1)
    # 接平面の上で、点 (1,1) では曲面と一致し、傾きは偏微分と一致する
    assert abs(7 - f(1, 1)) < 1e-12
    ax1.plot_surface(px, py, pz, color=C_B, alpha=0.7)
    ax1.scatter([1], [1], [7], color=C_BAD, s=30)
    ax1.set_xlabel("$x$（東）")
    ax1.set_ylabel("$y$（北）")
    ax1.set_zlabel("高さ $z$")
    ax1.set_xticks([-2, 0, 2])
    ax1.set_yticks([-1, 0, 1])
    ax1.set_zticks([0, 5, 10])
    ax1.view_init(elev=22, azim=-145)
    ax1.set_title("(a) 曲面 $z=10-x^2-2y^2$ と、点 $(1,1,7)$ での接平面（橙）", fontsize=11)

    ax2 = fig.add_subplot(1, 2, 2)
    cs = ax2.contour(X, Y, f(X, Y), levels=np.arange(0, 11, 1), cmap="viridis")
    ax2.clabel(cs, fontsize=8, fmt="%d")
    ax2.plot([1], [1], "o", color=C_BAD, ms=6)
    L = 0.6
    ax2.annotate("", xy=(1 + L, 1), xytext=(1, 1), arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=2))
    ax2.text(1 + L + 0.05, 1.02, "東：傾き $-2$", fontsize=9)
    ax2.annotate("", xy=(1, 1 + L), xytext=(1, 1), arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=2))
    ax2.text(1.05, 1 + L + 0.02, "北：傾き $-4$", fontsize=9)
    u = np.array([-1, -2]) / math.sqrt(5)
    ax2.annotate("", xy=(1 + L * u[0], 1 + L * u[1]), xytext=(1, 1), arrowprops=dict(arrowstyle="->", color=C_BAD, lw=2))
    ax2.text(1 + L * u[0] - 0.9, 1 + L * u[1] - 0.15, "いちばん急な上り\n傾き $2\\sqrt{5}\\approx4.47$", fontsize=9, color=C_BAD)
    # いちばん急な上りの向きは、等高線に直交する（等高線の接線 (2, -1)/√5 との内積 0）
    assert abs(np.dot(u, np.array([2, -1]) / math.sqrt(5))) < 1e-12
    ax2.set_aspect("equal")
    ax2.set_xlim(-2, 2.3)
    ax2.set_ylim(-1.6, 1.9)
    ax2.set_xlabel("$x$（東）")
    ax2.set_ylabel("$y$（北）")
    ax2.set_title("(b) 等高線の地図と、点 $(1,1)$ での向きごとの傾き", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mv01_tangent_plane.png", dpi=150)
    plt.close(fig)
    print("mv01_tangent_plane.png")


def mv02():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    xs = np.linspace(-0.5, 1.8, 200)
    ys = np.linspace(-1.6, 0.4, 200)
    X, Y = np.meshgrid(xs, ys)
    F2 = (X - 1) ** 2 + 2 * (Y + 1) ** 2
    ax1.contour(X, Y, F2, levels=[0.05, 0.2, 0.5, 1, 1.5, 2, 3], cmap="viridis")
    pts = [(0.0, 0.0)]
    for _ in range(10):
        px, py = pts[-1]
        pts.append((px - 0.1 * 2 * (px - 1), py - 0.1 * 4 * (py + 1)))
    for j, (px, py) in enumerate(pts):
        assert abs(px - (1 - 0.8**j)) < 1e-12 and abs(py - (-1 + 0.6**j)) < 1e-12  # 本文の式
    P = np.array(pts)
    ax1.plot(P[:, 0], P[:, 1], "o-", color=C_BAD, ms=4)
    ax1.annotate("出発 $(0,0)$", (0, 0), xytext=(-0.45, 0.2), fontsize=9)
    ax1.plot([1], [-1], "*", color=C_C, ms=14)
    ax1.annotate("最小の点 $(1,-1)$", (1, -1), xytext=(1.05, -1.35), fontsize=9)
    ax1.set_aspect("equal")
    ax1.set_xlabel("$x$")
    ax1.set_ylabel("$y$")
    ax1.set_title("(a) 勾配降下法：$f=(x-1)^2+2(y+1)^2$、学習率 0.1 で10歩", fontsize=11)

    xs = np.linspace(-1, 1, 401)
    X, Y = np.meshgrid(xs, xs)
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = X * Y / (X**2 + Y**2)
    im = ax2.pcolormesh(X, Y, Z, cmap="coolwarm", vmin=-0.5, vmax=0.5, shading="auto")
    fig.colorbar(im, ax=ax2, shrink=0.85, label="値")
    for m, lab in [(1, "$y=x$ の上で $\\frac{1}{2}$"), (-1, "$y=-x$ の上で $-\\frac{1}{2}$")]:
        ax2.plot([-1, 1], [-m, m], color="k", lw=0.8, ls="--")
    ax2.text(0.05, 0.82, "$y=x$ の上で $\\frac{1}{2}$", fontsize=10, bbox=dict(fc="white", alpha=0.8, ec="none"))
    ax2.text(0.05, -0.88, "$y=-x$ の上で $-\\frac{1}{2}$", fontsize=10, bbox=dict(fc="white", alpha=0.8, ec="none"))
    ax2.text(0.45, 0.05, "軸の上で 0", fontsize=10, bbox=dict(fc="white", alpha=0.8, ec="none"))
    ax2.set_aspect("equal")
    ax2.set_xlabel("$x$")
    ax2.set_ylabel("$y$")
    ax2.set_title(r"(b) コラムの関数 $\frac{xy}{x^2+y^2}$：原点を通る直線ごとに値が違う", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mv02_descent_counter.png", dpi=150)
    plt.close(fig)
    print("mv02_descent_counter.png")


FIGS = {"mv01": mv01, "mv02": mv02}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(FIGS)
    for key in keys:
        FIGS[key]()
