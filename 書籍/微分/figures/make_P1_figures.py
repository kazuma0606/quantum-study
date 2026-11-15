"""「準備1 極限と収束」（P1_極限と収束.md）の図を作る。

実行: uv run --no-sync python 書籍/微分/figures/make_P1_figures.py [lim01]

出力:
    lim01_limits.png   4つの極限の様子を並べた図。
                       (a) 数列 1/n は 0 に近づく（§1）
                       (b) メルカトル図法の縦の座標 y は、緯度 90° に近づくと限りなく大きくなる（§4）
                       (c) (x²-1)/(x-1) は x=1 で値がないが、近づくと 2 に近づく（§4）
                       (d) sin(1/x) は x → 0 で振れ続け、1つの値に近づかない（§4）
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


def lim01():
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))

    # (a) 1/n
    ax = axs[0, 0]
    ns = np.arange(1, 31)
    ax.plot(ns, 1 / ns, "o", color=C_A, ms=4)
    ax.axhline(0, color=C_BAD, lw=1, ls="--")
    assert abs(1 / ns[-1] - 1 / 30) < 1e-15
    ax.set_xlabel("$n$")
    ax.set_ylabel("$1/n$")
    ax.set_title("(a) 数列 $1/n$ は 0 に近づく", fontsize=11)

    # (b) メルカトル図法の y
    ax = axs[0, 1]
    deg = np.linspace(0, 89.5, 400)
    y = np.log(np.tan(np.pi / 4 + np.radians(deg) / 2))
    assert abs(math.log(math.tan(math.pi / 4 + math.radians(60) / 2)) - 1.317) < 1e-3  # 本文の表
    ax.plot(deg, y, color=C_A)
    ax.axvline(90, color=C_BAD, lw=1, ls="--")
    ax.set_xlim(0, 92)
    ax.set_xlabel("緯度（度）")
    ax.set_ylabel("地図の上での高さ $y$")
    ax.set_title("(b) メルカトル図法：北極（90°）に近づくと\n地図の上での高さ $y$ は限りなく大きくなる", fontsize=11)

    # (c) (x²-1)/(x-1)
    ax = axs[1, 0]
    xs = np.linspace(-0.5, 2.5, 400)
    xs = xs[np.abs(xs - 1) > 1e-9]
    ax.plot(xs, (xs**2 - 1) / (xs - 1), color=C_A)
    ax.plot([1], [2], "o", ms=8, mfc="white", mec=C_A, mew=1.5, zorder=3)
    ax.annotate("$x=1$ では値がない\n（でも、近づくと 2 に近づく）", (1, 2), xytext=(-0.45, 2.9),
                arrowprops=dict(arrowstyle="->", color=C_GRAY), fontsize=10)
    assert abs((1.001**2 - 1) / (1.001 - 1) - 2.001) < 1e-9
    ax.set_xlabel("$x$")
    ax.set_ylabel("値")
    ax.set_title(r"(c) $\frac{x^2-1}{x-1}$ は $x\to1$ で 2 に近づく", fontsize=11)

    # (d) sin(1/x)
    ax = axs[1, 1]
    xs = np.linspace(0.005, 0.5, 20000)
    ax.plot(xs, np.sin(1 / xs), color=C_A, lw=0.7)
    ax.set_xlim(0, 0.5)
    ax.set_xlabel("$x$")
    ax.set_ylabel(r"$\sin(1/x)$")
    ax.set_title(r"(d) $\sin(1/x)$ は $x\to0$ で振れ続ける", fontsize=11)

    fig.tight_layout()
    fig.savefig(OUT / "lim01_limits.png", dpi=150)
    plt.close(fig)
    print("lim01_limits.png")


def lim02():
    """コラム「北極とδ関数」：なめらかな坂と、その傾き（山）。幅 ε を小さくしていく。"""
    from math import erf, sqrt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    xs = np.linspace(-2, 2, 2001)
    colors = [C_GRAY, C_B, C_A]
    for eps, col in zip([0.5, 0.2, 0.05], colors):
        S = np.array([(1 + erf(v / (eps * sqrt(2)))) / 2 for v in xs])
        g = np.exp(-xs**2 / (2 * eps**2)) / (eps * np.sqrt(2 * np.pi))
        # 山の面積はどれも 1（台形公式で確かめる）
        area = np.sum((g[1:] + g[:-1]) / 2 * np.diff(xs))
        assert abs(area - 1) < 1e-3, area
        # 坂の傾き（差分）が山と一致する
        slope = np.gradient(S, xs)
        assert np.max(np.abs(slope - g)) < 0.05 * g.max(), eps
        ax1.plot(xs, S, color=col, label=f"幅 ε = {eps}")
        ax2.plot(xs, g, color=col, label=f"幅 ε = {eps}（高さ {g.max():.1f}）")
    ax1.plot([-2, 0], [0, 0], color="k", lw=1, ls="--")
    ax1.plot([0, 2], [1, 1], color="k", lw=1, ls="--", label="段差の関数")
    ax1.set_title("(a) 段差の関数を、なめらかな坂に置き換える", fontsize=11)
    ax1.set_xlabel("$x$")
    ax1.legend(fontsize=9, loc="upper left")
    ax2.set_ylim(0, 8.5)
    ax2.set_title("(b) 坂の傾きは山の形。坂を急にすると、山は細く高くなる\n（山の面積は、どれも 1）", fontsize=11)
    ax2.set_xlabel("$x$")
    ax2.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "lim02_step_delta.png", dpi=150)
    plt.close(fig)
    print("lim02_step_delta.png")


FIGS = {"lim01": lim01, "lim02": lim02}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(FIGS)
    for key in keys:
        FIGS[key]()
