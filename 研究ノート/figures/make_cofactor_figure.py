"""Part III §4（余因子行列）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/figures/make_cofactor_figure.py

出力: 研究ノート/figures/fig9_cofactor_matrix.png
    3x3 の J に対して、余因子行列 J~ の 9 成分を J~ の配置に並べ、
    各成分 J~_ij を作るために「J の j 行 i 列を消す」様子を示す。
    （転置のため、J~_ij は J の (i, j) ではなく (j, i) を消す）
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from make_christoffel_figures import OUT  # rcParams（日本語フォントなど）も設定される

C_KEEP = "#d62728"
C_DROP = "#9a9a9a"
C_POS = "#1f77b4"
C_NEG = "#9467bd"


def cofactor_rule(i, j):
    """J~_ij の作り方: J の j 行 i 列を消して、残りの 2x2 の (主対角 - 反対角) に符号を付ける。

    戻り値: (符号, 残る行 (r1, r2), 残る列 (c1, c2))
    """
    rows = [r for r in (1, 2, 3) if r != j]
    cols = [c for c in (1, 2, 3) if c != i]
    return (-1) ** (i + j), rows, cols


def check_rule_against_numpy():
    """図に使う規則が、実際の余因子行列（随伴行列）と一致することを乱数で確認する。"""
    rng = np.random.default_rng(0)
    for _ in range(20):
        J = rng.normal(size=(3, 3))
        Jt = np.zeros((3, 3))
        for i in (1, 2, 3):
            for j in (1, 2, 3):
                s, (r1, r2), (c1, c2) = cofactor_rule(i, j)
                Jt[i - 1, j - 1] = s * (J[r1 - 1, c1 - 1] * J[r2 - 1, c2 - 1]
                                        - J[r1 - 1, c2 - 1] * J[r2 - 1, c1 - 1])
        assert np.allclose(Jt, np.linalg.det(J) * np.linalg.inv(J)), "規則が随伴行列と一致しない"
        assert np.allclose(J @ Jt, np.linalg.det(J) * np.eye(3))


def draw_panel(ax, i, j):
    sign, (r1, r2), (c1, c2) = cofactor_rule(i, j)
    color = C_POS if sign > 0 else C_NEG

    ax.set_xlim(0.3, 3.7)
    ax.set_ylim(-3.95, -0.3)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(color)
        sp.set_linewidth(2.4)

    # 消す行 j と列 i：帯と、行・列を貫く十字線
    ax.add_patch(Rectangle((0.4, -j - 0.42), 3.2, 0.84, fc="#ececec", ec="none", zorder=0))
    ax.add_patch(Rectangle((i - 0.42, -3.85), 0.84, 3.4, fc="#ececec", ec="none", zorder=0))
    ax.plot([0.45, 3.55], [-j, -j], color="#7a7a7a", lw=2.2, zorder=1)
    ax.plot([i, i], [-3.8, -0.5], color="#7a7a7a", lw=2.2, zorder=1)

    # 残る 2x2 を赤で強調
    for r in (r1, r2):
        for c in (c1, c2):
            ax.add_patch(FancyBboxPatch((c - 0.36, -r - 0.32), 0.72, 0.64,
                                        boxstyle="round,pad=0.02,rounding_size=0.12",
                                        fc="#fbe0e0", ec=C_KEEP, lw=1.6, zorder=2))
    for r in (1, 2, 3):
        for c in (1, 2, 3):
            keep = r in (r1, r2) and c in (c1, c2)
            # 消す成分は、十字線に重なって読めなくならないよう、帯と同じ色の背景を敷く
            ax.text(c, -r, rf"$J_{{{r}{c}}}$", ha="center", va="center", zorder=3,
                    fontsize=14 if keep else 12,
                    color=C_KEEP if keep else "#6f6f6f",
                    fontweight="bold" if keep else "normal",
                    bbox=None if keep else dict(fc="#ececec", ec="none", pad=2.0))

    ax.set_title(
        rf"$\tilde{{J}}_{{{i}{j}}}={'+' if sign > 0 else '-'}"
        rf"(J_{{{r1}{c1}}}J_{{{r2}{c2}}}-J_{{{r1}{c2}}}J_{{{r2}{c1}}})$",
        fontsize=11.5, color=color, pad=6)
    ax.set_xlabel(f"{j}行{i}列を消す", fontsize=11.5, labelpad=4)


def main():
    check_rule_against_numpy()
    fig, axes = plt.subplots(3, 3, figsize=(12.5, 13.2))
    for i in (1, 2, 3):
        for j in (1, 2, 3):
            draw_panel(axes[i - 1, j - 1], i, j)

    fig.suptitle(r"余因子行列 $\tilde{J}$ の9成分：$\tilde{J}_{ij}$ は $J$ の「$j$ 行 $i$ 列」を消して作る",
                 fontsize=16, y=0.995)
    fig.text(0.5, 0.012,
             "灰色の十字：消す行と列　　赤：残った 2×2 →（主対角の積）−（反対角の積）\n"
             r"枠の色：符号 $(-1)^{i+j}$ が $+$（青）か $-$（紫）か。"
             r"$J^{-1}=\tilde{J}/\det J$。$\tilde{J}_{ij}$ が消すのは $J$ の $(j,i)$ 側（転置）で、"
             "対角成分だけは $i=j$ なので違いが見えない",
             ha="center", fontsize=11.5)
    fig.tight_layout(rect=(0, 0.045, 1, 0.975), h_pad=1.6, w_pad=1.2)
    fig.savefig(OUT / "fig9_cofactor_matrix.png", dpi=150)
    plt.close(fig)
    print("saved", OUT / "fig9_cofactor_matrix.png")


if __name__ == "__main__":
    main()
