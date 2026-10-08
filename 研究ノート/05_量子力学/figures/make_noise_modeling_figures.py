"""ノート「雑音をモデルにする」（noise_modeling_through_mri.md）の図。

実行（リポジトリのルートから）:
    uv run python 研究ノート/05_量子力学/figures/make_noise_modeling_figures.py        # すべて
    uv run python 研究ノート/05_量子力学/figures/make_noise_modeling_figures.py nmb01  # 1枚だけ
出力:
    nmb01_posterior_shots.png   Part IV：ショット数を増やすと事後分布が細くなる（回転の角度 θ の推定、式 (IV-5)）
    nmb02_ridge_and_peaks.png   Part IV：データが決めない方向（細長い尾根）と、符号が決まらない2つの山
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"


def nmb01() -> None:
    """RX(θ) のあとで測った「1」の回数から θ を推定する。事後分布の幅は 1/√N（式 (IV-5)）。"""
    theta_true = 0.6
    grid = np.linspace(0.2, 1.0, 8001)
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for N, c in ((100, C_GRAY), (1000, C_B), (10000, C_A)):
        n1 = rng.binomial(N, np.sin(theta_true / 2) ** 2)
        pr = np.sin(grid / 2) ** 2
        logL = n1 * np.log(pr) + (N - n1) * np.log(1 - pr)          # 事前分布は一様（この範囲）
        post = np.exp(logL - logL.max())
        post /= np.trapezoid(post, grid)
        mean = np.trapezoid(grid * post, grid)
        sd = np.sqrt(np.trapezoid((grid - mean) ** 2 * post, grid))
        assert abs(sd * np.sqrt(N) - 1) < 0.06, (N, sd)              # 式 (IV-5)：幅 ≈ 1/√N
        ax.plot(grid, post, color=c, lw=1.8, label=f"N = {N}（幅 {sd:.3f}）")
    ax.axvline(theta_true, color="k", ls="--", lw=0.8, label="正解 θ = 0.6")
    ax.set_xlabel("回転の角度 θ（rad）")
    ax.set_ylabel("事後分布（確率密度）")
    ax.set_title("ショット数 N を増やすと、事後分布が細くなる（幅 ≈ 1/√N）", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "nmb01_posterior_shots.png", dpi=150)
    plt.close(fig)


def nmb02() -> None:
    """(a) データが a+b だけで決まるとき、事後分布は a−b の方向に事前分布の幅のまま伸びる（尾根）。
    (b) データが d の符号をほとんど区別しないとき、事後分布は ±d の2つの山になる。"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    # (a) 尾根：P(1) = (1 − sin(10(a+b)))/2（a+b の符号も区別できる測り方）、正解 a+b = 0.02、N = 4000、事前分布 a, b ～ N(0, 0.05)
    s_true, N, prior = 0.02, 4000, 0.05
    rng = np.random.default_rng(1)
    n1 = rng.binomial(N, (1 - np.sin(10 * s_true)) / 2)
    a = np.linspace(-0.15, 0.15, 601)
    A, B = np.meshgrid(a, a)
    pr = np.clip((1 - np.sin(10 * (A + B))) / 2, 1e-12, 1 - 1e-12)
    logp = n1 * np.log(pr) + (N - n1) * np.log(1 - pr) - (A**2 + B**2) / (2 * prior**2)
    post = np.exp(logp - logp.max())
    post /= post.sum()
    u, v = (A + B), (A - B)
    mu_u, mu_v = (post * u).sum(), (post * v).sum()
    sd_u, sd_v = np.sqrt((post * (u - mu_u) ** 2).sum()), np.sqrt((post * (v - mu_v) ** 2).sum())
    assert abs(mu_u - s_true) < 3 * sd_u and sd_u < 0.005           # 和 a+b はデータが決める
    assert abs(sd_v / (prior * np.sqrt(2)) - 1) < 0.1               # 差 a−b は事前分布の幅（0.05√2）のまま
    ax = axes[0]
    ax.contourf(A, B, post, levels=12, cmap="Blues")
    ax.plot(a, s_true - a, color=C_BAD, lw=0.8, ls="--", label="a + b = 0.02（データが決める線）")
    ax.set_aspect("equal")
    ax.set_xlabel("a（rad）")
    ax.set_ylabel("b（rad）")
    ax.set_title(f"(a) データが a+b だけで決まる：細長い尾根\n和の幅 {sd_u:.4f}、差の幅 {sd_v:.3f}（事前分布のまま）", fontsize=10.5)
    ax.legend(fontsize=8.5, loc="upper right")
    # (b) 2つの山：主な測定は cos(10d) だけで決まり（d の符号を区別しない）、弱い測定が sin(d) を少しだけ見る
    d_true = 0.05
    d = np.linspace(-0.15, 0.15, 3001)
    rng = np.random.default_rng(2)
    n_main = rng.binomial(4000, np.sin(10 * d_true / 2) ** 2)
    p_main = np.clip(np.sin(10 * d / 2) ** 2, 1e-12, 1 - 1e-12)
    y_weak = np.sin(d_true) + rng.normal(0, 0.04)                    # 符号の手がかり（雑音が大きい）
    logp = n_main * np.log(p_main) + (4000 - n_main) * np.log(1 - p_main) - (y_weak - np.sin(d)) ** 2 / (2 * 0.04**2) - d**2 / (2 * prior**2)
    post = np.exp(logp - logp.max())
    post /= np.trapezoid(post, d)
    w_pos = np.trapezoid(post[d > 0], d[d > 0])
    assert 0.5 < w_pos < 0.99 and np.trapezoid(post[d < 0], d[d < 0]) > 0.01   # 2つの山があり、正の側がやや重い
    ax = axes[1]
    ax.plot(d, post, color=C_A, lw=1.8)
    ax.axvline(d_true, color="k", ls="--", lw=0.8, label="正解 d = +0.05")
    ax.axvline(-d_true, color=C_GRAY, ls=":", lw=0.8, label="符号だけ逆 d = −0.05")
    ax.set_xlabel("d（rad）")
    ax.set_ylabel("事後分布（確率密度）")
    ax.set_title(f"(b) 符号がほとんど区別できない：2つの山\n正の山の重み {w_pos:.2f}、負の山の重み {1 - w_pos:.2f}", fontsize=10.5)
    ax.legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "nmb02_ridge_and_peaks.png", dpi=150)
    plt.close(fig)
    print(f"nmb02：和の幅 {sd_u:.4f}、差の幅 {sd_v:.4f}、正の山の重み {w_pos:.3f}")


FIGS = {"nmb01": nmb01, "nmb02": nmb02}

if __name__ == "__main__":
    for name in (sys.argv[1:] or FIGS):
        FIGS[name]()
        print(f"作成：{name}")
