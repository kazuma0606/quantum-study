"""「準備3 ベクトルと行列」（P3_ベクトルと行列.md）の図を作る。

実行: uv run --no-sync python 書籍/微分/figures/make_P3_figures.py [mat01 mat02]

出力:
    mat01_linear_maps.png   §3・§5 4つの行列で、方眼と単位正方形（青）を写したもの（橙）。
                            回転 30°、拡大 diag(2, 1/2)、せん断 (1 1; 0 1)、つぶす (1 2; 2 4)。
                            タイトルに行列式（面積の倍率）を書く。
    mat02_polar_jacobian.png §6 極座標 (r, θ) の小さな長方形を、(x, y) に写したもの。
                            実際の像（青の曲がった四角形）と、Jacobian で写した平行四辺形（橙の破線）。
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


def mat01():
    c, s = math.cos(math.pi / 6), math.sin(math.pi / 6)
    mats = [
        ("回転 30°", np.array([[c, -s], [s, c]])),
        ("拡大・縮小 diag(2, 1/2)", np.array([[2, 0], [0, 0.5]])),
        ("せん断", np.array([[1, 1], [0, 1]])),
        ("つぶす", np.array([[1, 2], [2, 4]])),
    ]
    fig, axs = plt.subplots(1, 4, figsize=(15, 4.4))
    for ax, (name, A) in zip(axs, mats):
        # 方眼を写す
        for t in np.arange(-2, 3):
            pts = np.array([[t, u] for u in np.linspace(-2, 2, 2)]).T
            ax.plot(*(A @ pts), color=C_GRAY, lw=0.5)
            pts = np.array([[u, t] for u in np.linspace(-2, 2, 2)]).T
            ax.plot(*(A @ pts), color=C_GRAY, lw=0.5)
        sq = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]])
        ax.fill(*sq, color=C_A, alpha=0.35)
        ax.plot(*sq, color=C_A, lw=1.5)
        img = A @ sq
        ax.fill(*img, color=C_B, alpha=0.45)
        ax.plot(*img, color=C_B, lw=2)
        # 列ベクトル（e1, e2 の行き先）
        for j, col in enumerate([C_BAD, C_C]):
            ax.annotate("", xy=A[:, j], xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col, lw=2))
        det = np.linalg.det(A)
        # 平行四辺形の面積（靴ひも公式）と行列式の絶対値が一致する
        xs, ys = img[0, :4], img[1, :4]
        area = 0.5 * abs(np.dot(xs, np.roll(ys, -1)) - np.dot(ys, np.roll(xs, -1)))
        assert abs(area - abs(det)) < 1e-9, (name, area, det)
        ax.set_title(f"{name}\n行列式 {det:.2g}" if abs(det) > 1e-12 else f"{name}\n行列式 0", fontsize=11)
        ax.set_xlim(-2.5, 3.5)
        ax.set_ylim(-2.5, 5.5)
        ax.set_aspect("equal")
        ax.tick_params(labelsize=8)
    fig.suptitle("行列で写す：青の正方形が橙の図形に、灰色の方眼がゆがんだ方眼に移る（赤と緑の矢印は、行列の第1列と第2列）", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "mat01_linear_maps.png", dpi=150)
    plt.close(fig)
    print("mat01_linear_maps.png")


def mat02():
    r0, t0 = 2.0, math.pi / 6
    dr, dt = 0.3, 0.25  # 見やすいように大きめにとる
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.3]})
    # 左：(r, θ) の長方形
    ax1.fill([r0, r0 + dr, r0 + dr, r0, r0], [t0, t0, t0 + dt, t0 + dt, t0], color=C_A, alpha=0.35)
    ax1.plot([r0, r0 + dr, r0 + dr, r0, r0], [t0, t0, t0 + dt, t0 + dt, t0], color=C_A, lw=1.5)
    ax1.annotate("$dr$", (r0 + dr / 2, t0 - 0.03), ha="center", va="top", fontsize=12)
    ax1.annotate(r"$d\theta$", (r0 - 0.03, t0 + dt / 2), ha="right", va="center", fontsize=12)
    ax1.set_xlim(r0 - 0.4, r0 + dr + 0.3)
    ax1.set_ylim(t0 - 0.2, t0 + dt + 0.15)
    ax1.set_xlabel("$r$")
    ax1.set_ylabel(r"$\theta$")
    ax1.set_title(r"(a) $(r,\theta)$ の小さな長方形", fontsize=11)
    # 右：(x, y) での像
    rs = np.linspace(r0, r0 + dr, 50)
    ts = np.linspace(t0, t0 + dt, 50)
    edge = np.concatenate([
        np.stack([rs, np.full_like(rs, t0)]),
        np.stack([np.full_like(ts, r0 + dr), ts]),
        np.stack([rs[::-1], np.full_like(rs, t0 + dt)]),
        np.stack([np.full_like(ts, r0), ts[::-1]]),
    ], axis=1)
    X, Y = edge[0] * np.cos(edge[1]), edge[0] * np.sin(edge[1])
    ax2.fill(X, Y, color=C_A, alpha=0.35, label="実際の像（少し曲がった四角形）")
    ax2.plot(X, Y, color=C_A, lw=1.5)
    J = np.array([[math.cos(t0), -r0 * math.sin(t0)], [math.sin(t0), r0 * math.cos(t0)]])
    assert abs(np.linalg.det(J) - r0) < 1e-12  # 本文：det J = r
    P0 = np.array([r0 * math.cos(t0), r0 * math.sin(t0)])
    v1, v2 = J @ np.array([dr, 0]), J @ np.array([0, dt])
    para = np.array([P0, P0 + v1, P0 + v1 + v2, P0 + v2, P0]).T
    ax2.plot(*para, color=C_B, lw=2, ls="--", label="Jacobian で写した平行四辺形")
    ax2.annotate("", xy=P0 + v1, xytext=P0, arrowprops=dict(arrowstyle="->", color=C_BAD, lw=2))
    ax2.annotate("", xy=P0 + v2, xytext=P0, arrowprops=dict(arrowstyle="->", color=C_C, lw=2))
    ax2.text(*(P0 + v1 + np.array([0.03, -0.06])), r"$J$ の第1列 $\times\,dr$", color=C_BAD, fontsize=10)
    ax2.text(*(P0 + v2 + np.array([-0.55, 0.03])), r"$J$ の第2列 $\times\,d\theta$", color=C_C, fontsize=10)
    ax2.plot([0, P0[0]], [0, P0[1]], color=C_GRAY, lw=0.8, ls=":")
    ax2.plot([0], [0], "o", color="k", ms=3)
    ax2.text(0.03, -0.12, "原点", fontsize=9)
    ax2.set_aspect("equal")
    ax2.set_xlim(-0.1, 2.6)
    ax2.set_ylim(-0.2, 1.9)
    ax2.set_xlabel("$x$")
    ax2.set_ylabel("$y$")
    ax2.legend(fontsize=9, loc="upper left")
    ax2.set_title(r"(b) $x=r\cos\theta,\ y=r\sin\theta$ で写すと", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "mat02_polar_jacobian.png", dpi=150)
    plt.close(fig)
    print("mat02_polar_jacobian.png")


FIGS = {"mat01": mat01, "mat02": mat02}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(FIGS)
    for key in keys:
        FIGS[key]()
