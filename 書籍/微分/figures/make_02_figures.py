"""「2 ベクトル微分」（02_ベクトル微分.md）の図を作る。

実行: uv run --no-sync python 書籍/微分/figures/make_02_figures.py [vec01 vec02]

出力:
    vec01_grad_div_rot.png  §1〜§3
                            (a) 1章の山 f = 10 - x² - 2y² の等高線と grad f の矢印（等高線に直交する）。
                            (b) 湧き出す流れ (x, y)：div = 2、rot = 0。
                            (c) 回る流れ (-y, x)：div = 0、rot = 2。
    vec02_metric.png        §5・§6
                            (a) 極座標の網と、座標の基底ベクトル b_r（長さ 1）、b_θ（長さ r）。
                            (b) 地球の経度 1° の東西の長さと緯度（R = 6371 km）。
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


def vec01():
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    # (a) grad
    ax = axs[0]
    xs = np.linspace(-2, 2, 200)
    ys = np.linspace(-1.6, 1.6, 200)
    X, Y = np.meshgrid(xs, ys)
    F = 10 - X**2 - 2 * Y**2
    cs = ax.contour(X, Y, F, levels=np.arange(1, 11, 1), cmap="viridis", linewidths=1)
    ax.clabel(cs, fontsize=7, fmt="%d")
    pts = [(1, 1), (-1, 0.5), (1.5, -0.5), (0, -1), (-1.4, -0.8), (0.5, 0.2)]
    for px, py in pts:
        g = np.array([-2 * px, -4 * py])
        n = np.linalg.norm(g)
        d = g / n * 0.45
        ax.annotate("", xy=(px + d[0], py + d[1]), xytext=(px, py), arrowprops=dict(arrowstyle="->", color=C_BAD, lw=1.8))
        ax.plot([px], [py], "o", color=C_BAD, ms=3)
    # (1,1) で grad と等高線の接線 (2,-1) は直交
    assert abs(np.dot([-2, -4], [2, -1])) < 1e-12
    ax.set_aspect("equal")
    ax.set_title("(a) 山の等高線と grad $f$（赤）\n矢印は、等高線に直交して、上りの向きを指す", fontsize=11)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    # (b)(c) 流れ
    g1 = np.linspace(-1.5, 1.5, 11)
    U, Vv = np.meshgrid(g1, g1)
    for ax, (fu, fv, title) in zip(axs[1:], [
        (U, Vv, "(b) 湧き出す流れ $(x,\\ y)$\ndiv $=2$、rot $=0$"),
        (-Vv, U, "(c) 回る流れ $(-y,\\ x)$\ndiv $=0$、rot $=2$"),
    ]):
        ax.quiver(U, Vv, fu, fv, color=C_A, angles="xy", scale_units="xy", scale=4, width=0.005)
        sq = np.array([[0.4, 0.9, 0.9, 0.4, 0.4], [0.4, 0.4, 0.9, 0.9, 0.4]])
        ax.plot(*sq, color=C_B, lw=2)
        ax.set_aspect("equal")
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
    box = dict(fc="white", alpha=0.85, ec="none")
    axs[1].text(0.95, 1.0, "小さな正方形から\n出ていく量 ＞ 入る量", fontsize=9, color=C_B, bbox=box)
    axs[2].text(0.95, 1.0, "小さな正方形の\nまわりを回る", fontsize=9, color=C_B, bbox=box)
    fig.tight_layout()
    fig.savefig(OUT / "vec01_grad_div_rot.png", dpi=150)
    plt.close(fig)
    print("vec01_grad_div_rot.png")


def vec02():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    # (a) 極座標の網と基底
    for rr in [0.5, 1, 1.5, 2, 2.5]:
        t = np.linspace(0, np.pi / 2, 100)
        ax1.plot(rr * np.cos(t), rr * np.sin(t), color=C_GRAY, lw=0.6)
    for tt in np.linspace(0, np.pi / 2, 7):
        ax1.plot([0, 2.7 * np.cos(tt)], [0, 2.7 * np.sin(tt)], color=C_GRAY, lw=0.6)
    sc = 0.35  # 見やすさのための縮尺（b_r と b_θ に同じ縮尺を掛ける）
    for rr, tt in [(1, np.pi / 6), (2, np.pi / 6), (1, np.pi / 3), (2, np.pi / 3)]:
        p = np.array([rr * np.cos(tt), rr * np.sin(tt)])
        br = np.array([np.cos(tt), np.sin(tt)])
        bt = np.array([-rr * np.sin(tt), rr * np.cos(tt)])
        assert abs(np.linalg.norm(br) - 1) < 1e-12 and abs(np.linalg.norm(bt) - rr) < 1e-12
        ax1.annotate("", xy=p + sc * br, xytext=p, arrowprops=dict(arrowstyle="->", color=C_BAD, lw=2))
        ax1.annotate("", xy=p + sc * bt, xytext=p, arrowprops=dict(arrowstyle="->", color=C_C, lw=2))
        ax1.plot(*p, "o", color="k", ms=3)
    ax1.text(2.05, 1.32, r"$r=2$ では $\boldsymbol{b}_\theta$ が長い", fontsize=9, color=C_C)
    ax1.plot([], [], color=C_BAD, label=r"$\boldsymbol{b}_r$（長さ 1）")
    ax1.plot([], [], color=C_C, label=r"$\boldsymbol{b}_\theta$（長さ $r$）")
    ax1.legend(fontsize=9, loc="upper right")
    ax1.set_aspect("equal")
    ax1.set_xlim(-0.1, 3.0)
    ax1.set_ylim(-0.1, 2.9)
    ax1.set_xlabel("$x$")
    ax1.set_ylabel("$y$")
    ax1.set_title("(a) 極座標の基底ベクトル（どちらも同じ縮尺で描いています）", fontsize=11)
    # (b) 経度 1° の長さ
    R = 6371.0
    lat = np.linspace(0, 90, 200)
    L = R * np.cos(np.radians(lat)) * math.pi / 180
    ax2.plot(lat, L, color=C_A, lw=2)
    for la, lab in [(0, "赤道"), (35, "東京のあたり"), (60, "ヘルシンキのあたり")]:
        v = R * math.cos(math.radians(la)) * math.pi / 180
        ax2.plot([la], [v], "o", color=C_BAD)
        ax2.annotate(f"{lab}\n約 {v:.0f} km", (la, v), xytext=(6, 4), textcoords="offset points", fontsize=9)
    assert abs(R * math.cos(math.radians(60)) * math.pi / 180 - 55.6) < 0.1
    ax2.set_xlabel("緯度（度）")
    ax2.set_ylabel("経度 1° の東西の長さ（km）")
    ax2.set_xlim(0, 92)
    ax2.set_ylim(0, 125)
    ax2.set_title("(b) 地球の経度 1° の長さは、緯度で変わる（$\\propto\\cos$ 緯度）", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "vec02_metric.png", dpi=150)
    plt.close(fig)
    print("vec02_metric.png")


FIGS = {"vec01": vec01, "vec02": vec02}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(FIGS)
    for key in keys:
        FIGS[key]()
