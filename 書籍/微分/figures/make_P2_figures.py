"""「準備2 1変数の微分」（P2_1変数の微分.md）の図を作る。

実行: uv run --no-sync python 書籍/微分/figures/make_P2_figures.py [dif01 dif02]

出力:
    dif01_zoom.png      §1・§2 拡大すると、なめらかな曲線は直線に見える。
                        上段：y = √x の x=4 のまわりを、幅 4・0.4・0.04 で拡大（灰色の破線は接線）。
                        下段：y = |x| の x=0 のまわりを、同じように拡大（いくら拡大しても角は残る）。
    dif02_uses.png      §1・§4・§5 (a) 地球の表面（円）と接線、落ち込み d²/(2R)（大きく誇張して描く）。
                        (b) 勾配降下法：y = (x-3)² の上で、x=0 から学習率 0.1 で 5 歩進む。
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


def dif01():
    fig, axs = plt.subplots(2, 3, figsize=(12, 7.2))
    for col, w in enumerate([4.0, 0.4, 0.04]):
        # 上段：√x の x=4 のまわり
        ax = axs[0, col]
        xs = np.linspace(4 - w / 2, 4 + w / 2, 400)
        ax.plot(xs, np.sqrt(xs), color=C_A, lw=2, label=r"$y=\sqrt{x}$")
        ax.plot(xs, 2 + (xs - 4) / 4, color=C_GRAY, lw=1.2, ls="--", label="接線")
        ax.plot([4], [2], "o", color=C_BAD, ms=4)
        # 拡大の幅が 1/10 になると、曲線と接線のずれ（の最大）はおよそ 1/100 になる
        gap = np.max(np.abs(np.sqrt(xs) - (2 + (xs - 4) / 4)))
        # 幅が十分小さい所（0.4 → 0.04）では、ずれはほぼ 1/100 になる（幅 4 では、まだ曲がりが大きく、比はずれる）
        if col == 2:
            assert 0.009 < gap / prev_gap < 0.011, gap / prev_gap
        prev_gap = gap
        ax.set_title(f"$y=\\sqrt{{x}}$、幅 {w:g}（ずれの最大 {gap:.1e}）", fontsize=10)
        ax.set_xticks([4 - w / 2, 4, 4 + w / 2])
        ax.tick_params(labelsize=8)
        if col == 0:
            ax.legend(fontsize=9, loc="upper left")
        # 下段：|x| の x=0 のまわり
        ax = axs[1, col]
        xs = np.linspace(-w / 2, w / 2, 401)
        ax.plot(xs, np.abs(xs), color=C_B, lw=2, label="$y=|x|$")
        ax.plot([0], [0], "o", color=C_BAD, ms=4)
        ax.set_title(f"$y=|x|$、幅 {w:g}", fontsize=10)
        ax.set_xticks([-w / 2, 0, w / 2])
        ax.set_aspect("equal")
        ax.tick_params(labelsize=8)
        if col == 0:
            ax.legend(fontsize=9, loc="upper center")
    fig.suptitle("拡大していくと：なめらかな曲線は直線（接線）に重なっていくが、$|x|$ の角はいつまでも残る", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "dif01_zoom.png", dpi=150)
    plt.close(fig)
    print("dif01_zoom.png")


def dif02():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # (a) 円と接線（誇張）
    Rr = 1.0
    th = np.linspace(np.pi / 2 - 0.9, np.pi / 2 + 0.9, 400)
    ax1.plot(Rr * np.cos(th), Rr * np.sin(th), color=C_A, lw=2, label="地球の表面（円）")
    ax1.plot([-0.85, 0.85], [Rr, Rr], color=C_GRAY, ls="--", label="足もとの接線")
    dd = 0.6
    yy = math.sqrt(Rr**2 - dd**2)
    ax1.plot([dd, dd], [yy, Rr], color=C_BAD, lw=2)
    ax1.text(dd + 0.04, (yy + Rr) / 2, "落ち込み\n$R-\\sqrt{R^2-d^2}\\approx\\frac{d^2}{2R}$",
             fontsize=10, ha="left", va="center", color=C_BAD)
    ax1.annotate("", xy=(dd, Rr + 0.04), xytext=(0, Rr + 0.04), arrowprops=dict(arrowstyle="<->", color="k"))
    ax1.text(dd / 2, Rr + 0.06, "$d$", ha="center", fontsize=11)
    ax1.plot([0], [Rr], "o", color="k", ms=4)
    ax1.set_xlim(-0.9, 1.25)
    ax1.set_ylim(0.45, 1.15)
    ax1.set_aspect("equal")
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.legend(fontsize=9, loc="lower left")
    ax1.set_title("(a) 足もとの接線から、地球の表面はどれだけ落ち込むか\n（落ち込みは大きく誇張して描いています）", fontsize=11)

    # (b) 勾配降下法
    xs = np.linspace(-0.5, 4.5, 400)
    ax2.plot(xs, (xs - 3) ** 2, color=C_A, lw=2, label="$y=(x-3)^2$")
    pts = [0.0]
    for _ in range(5):
        pts.append(pts[-1] - 0.1 * 2 * (pts[-1] - 3))
    assert abs(pts[1] - 0.6) < 1e-12 and abs(pts[2] - 1.08) < 1e-12  # 本文の値
    for j, p in enumerate(pts):
        ax2.plot([p], [(p - 3) ** 2], "o", color=C_BAD, ms=6, zorder=3)
        ax2.annotate(f"{j}", (p, (p - 3) ** 2), xytext=(4, 6), textcoords="offset points", fontsize=9)
        if j + 1 < len(pts):
            q = pts[j + 1]
            ax2.annotate("", xy=(q, (q - 3) ** 2), xytext=(p, (p - 3) ** 2),
                         arrowprops=dict(arrowstyle="->", color=C_BAD, lw=1))
    ax2.plot([3], [0], "*", color=C_C, ms=14, label="最小の点 $x=3$", zorder=3)
    ax2.set_xlabel("$x$")
    ax2.set_ylabel("$y$")
    ax2.legend(fontsize=9, loc="upper right")
    ax2.set_title("(b) 勾配降下法：傾きの逆向きに少しずつ進むと、最小の点に近づく\n（$x=0$ から、学習率 0.1 で5歩）", fontsize=11)

    fig.tight_layout()
    fig.savefig(OUT / "dif02_uses.png", dpi=150)
    plt.close(fig)
    print("dif02_uses.png")


FIGS = {"dif01": dif01, "dif02": dif02}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(FIGS)
    for key in keys:
        FIGS[key]()
