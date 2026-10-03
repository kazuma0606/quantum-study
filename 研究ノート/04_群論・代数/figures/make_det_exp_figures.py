"""det_exp_trace_proof.md（det(e^A) = e^{tr A} の証明）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/04_群論・代数/figures/make_det_exp_figures.py          # すべて
    uv run python 研究ノート/04_群論・代数/figures/make_det_exp_figures.py det01    # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    det01_leibniz_terms.png        証明2 ステップ1 det(I+εX) の6つの項（3×3）と、ε の次数
    det02_jordan_and_phase.png     証明2 ステップ5・注意 ジョルダン細胞の面積、複素行列の det(e^{tA}) の軌跡
    det03_su2_one_parameter.png    この公式の意味 1パラメータの族 det(e^{itH}) = e^{it tr H}

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import itertools
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.linalg import expm

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY = "#1f77b4", "#e67e00", "#d62728", "#888888"


# ------------------------------------------------------------------------------------- det01
def det01():
    """det(I+εX) の6つの項：恒等置換だけが ε の1次を含む。"""
    eps = sp.symbols("varepsilon")
    X = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f"X{i + 1}{j + 1}"))
    M = sp.eye(3) + eps * X
    perms = list(itertools.permutations(range(3)))
    names = {(0, 1, 2): "恒等置換", (1, 0, 2): "互換 (1 2)", (2, 1, 0): "互換 (1 3)", (0, 2, 1): "互換 (2 3)",
             (1, 2, 0): "巡回置換 (1 2 3)", (2, 0, 1): "巡回置換 (1 3 2)"}
    order = [(0, 1, 2), (1, 0, 2), (2, 1, 0), (0, 2, 1), (1, 2, 0), (2, 0, 1)]
    total = 0
    terms = {}
    for p in perms:
        sign = sp.combinatorics.Permutation(list(p)).signature()
        term = sign * sp.prod([M[i, p[i]] for i in range(3)])
        total += term
        poly = sp.Poly(sp.expand(term), eps)
        low = min(m[0] for m in poly.monoms())
        n_off = sum(1 for i in range(3) if p[i] != i)
        assert low == n_off                                                      # 最低次数 = 非対角成分の数
        terms[p] = (sign, low)
    assert sp.expand(total - M.det()) == 0                                       # 6項の和 = det
    assert sp.expand(sp.Poly(sp.expand(M.det()), eps).coeff_monomial(eps) - X.trace()) == 0   # 1次の係数 = tr X

    fig, axes = plt.subplots(2, 3, figsize=(13, 8.6))
    for ax, p in zip(axes.flat, order):
        sign, low = terms[p]
        for i in range(3):
            for j in range(3):
                picked = p[i] == j
                fc = (C_A if i == j else C_B) if picked else "white"
                ax.add_patch(plt.Rectangle((j, 2 - i), 1, 1, fc=fc, ec="#555", lw=1.2, alpha=0.85 if picked else 1))
                lab = f"$1+\\varepsilon X_{{{i + 1}{j + 1}}}$" if i == j else f"$\\varepsilon X_{{{i + 1}{j + 1}}}$"
                ax.text(j + 0.5, 2 - i + 0.5, lab, ha="center", va="center", fontsize=10,
                        color="white" if picked else "#999999")
        sgn = "+" if sign > 0 else "−"
        order_txt = "$\\varepsilon^0$ と $\\varepsilon^1$ を含む" if low == 0 else f"$\\varepsilon^{low}$ から"
        ax.set_title(f"{names[p]}（符号 {sgn}）\n{order_txt}", fontsize=11,
                     color=C_A if low == 0 else "#333")
        ax.set_xlim(-0.05, 3.05), ax.set_ylim(-0.05, 3.05), ax.set_aspect("equal"), ax.axis("off")
    fig.suptitle("$\\det(I+\\varepsilon X)$ の6つの項（青：対角成分、橙：非対角成分）\n"
                 "恒等置換以外は非対角成分を2つ以上含むので $O(\\varepsilon^2)$ → 1次の項は $\\varepsilon\\,\\mathrm{tr}\\,X$ だけ",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / "det01_leibniz_terms.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- det02
def det02():
    """(a) ジョルダン細胞で単位正方形を運ぶ、(b) 複素行列の det(e^{tA}) の軌跡。"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.6))

    # (a) ジョルダン細胞
    ax = axes[0]
    lam = 0.3
    A = np.array([[lam, 1.0], [0.0, lam]])
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], float).T
    cols = ["#999999", C_A, C_B, C_BAD]
    for t, c in zip([0, 1, 2, 3], cols):
        E = expm(t * A)
        assert np.allclose(E, np.exp(lam * t) * np.array([[1, t], [0, 1]]))           # e^{tA} = e^{λt}(I + tN)
        P = E @ sq
        area = abs(np.linalg.det(E))
        assert np.isclose(area, np.exp(t * np.trace(A)))                               # 面積 = e^{t tr A}
        shoelace = 0.5 * abs(np.dot(P[0, :-1], P[1, 1:]) - np.dot(P[1, :-1], P[0, 1:]))
        assert np.isclose(shoelace, area)
        ax.fill(P[0], P[1], color=c, alpha=0.18)
        ax.plot(P[0], P[1], color=c, lw=2, label=f"$t={t}$：面積 $e^{{0.6t}}={area:.2f}$")
    ax.set_aspect("equal"), ax.set_xlim(-0.3, 10.5), ax.set_ylim(-0.3, 3.0)
    ax.set_xlabel("$x$"), ax.set_ylabel("$y$"), ax.legend(fontsize=10, loc="upper left")
    ax.set_title("(a) ジョルダン細胞 $A=0.3\\,I+N$（$N$：右上だけ $1$、$N^2=0$、対角化できない）で\n単位正方形を $e^{tA}$ で運ぶ：面積は $e^{t\\,\\mathrm{tr}A}=e^{0.6t}$ 倍",
                 fontsize=11)

    # (b) 複素行列
    ax = axes[1]
    A = np.array([[0.1 + 1.0j, 0.5], [-0.3j, 0.05 + 1.2j]])
    trA = np.trace(A)
    assert np.isclose(trA, 0.15 + 2.2j)
    ts = np.linspace(0, 3, 400)
    curve = np.exp(ts * trA)
    tt = np.linspace(0, 3, 13)
    dets = np.array([np.linalg.det(expm(t * A)) for t in tt])
    assert np.allclose(dets, np.exp(tt * trA))                                          # det e^{tA} = e^{t tr A}
    th = np.linspace(0, 2 * np.pi, 200)
    for r in (1, np.exp(0.15 * 3)):
        ax.plot(r * np.cos(th), r * np.sin(th), color="#dddddd", lw=1, zorder=0)
    ax.plot(curve.real, curve.imag, color=C_A, lw=2, label="$e^{t\\,\\mathrm{tr}A}$（$0\\leq t\\leq3$）")
    ax.plot(dets.real, dets.imag, "o", color=C_BAD, ms=6, label="$\\det e^{tA}$（行列指数関数を数値計算）")
    tq = 2.0
    z = np.exp(tq * trA)
    ax.plot([0, z.real], [0, z.imag], color=C_B, lw=1.6, ls="--")
    ax.annotate("", xy=(z.real, z.imag), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C_B, lw=1.6))
    ax.text(z.real * 0.5 - 0.05, z.imag * 0.5 + 0.08, f"$|\\det|=e^{{0.15t}}$\n（$\\ln|\\det|$ で分かる）", color=C_B, fontsize=10, ha="right")
    aa = np.linspace(0, np.angle(z) % (2 * np.pi), 60)
    ax.plot(0.35 * np.cos(aa), 0.35 * np.sin(aa), color="#555", lw=1.2)
    ax.text(-0.72, 0.5, f"偏角 $2.2t$（$t={tq:g}$ で ${np.degrees(2.2 * tq) % 360:.0f}^\\circ$）\n$\\ln|\\det|$ では分からない", fontsize=10)
    ax.plot(0, 0, "+", color="#333", ms=10), ax.plot(1, 0, "s", color="#333", ms=5)
    ax.text(1.04, 0.05, "$t=0$", fontsize=10)
    ax.set_aspect("equal"), ax.set_xlim(-2.1, 2.1), ax.set_ylim(-2.1, 2.1)
    ax.set_xlabel("実部"), ax.set_ylabel("虚部"), ax.legend(fontsize=9.5, loc="upper left")
    ax.set_title("(b) 複素行列（$\\mathrm{tr}A=0.15+2.2i$）の $\\det e^{tA}$：\n絶対値と回転の両方が $e^{t\\,\\mathrm{tr}A}$ に一致する", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "det02_jordan_and_phase.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- det03
def det03():
    """1パラメータの族 det(e^{itH}) = e^{it tr H}：tr H = 0 ならすべての t で 1。"""
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]])
    sz = np.diag([1.0 + 0j, -1.0])
    H0 = 0.3 * sx - 1.1 * sy + 0.7 * sz                      # tr H0 = 0
    c = 0.5
    H1 = H0 + (c / 2) * np.eye(2)                            # tr H1 = c
    assert np.isclose(np.trace(H0), 0) and np.isclose(np.trace(H1), c)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), gridspec_kw=dict(width_ratios=[1, 1.35]))
    T = 4 * np.pi / c
    ts = np.linspace(0, T, 600)
    d0 = np.array([np.linalg.det(expm(1j * t * H0)) for t in ts[::20]])
    d1 = np.array([np.linalg.det(expm(1j * t * H1)) for t in ts[::20]])
    assert np.allclose(d0, 1) and np.allclose(d1, np.exp(1j * ts[::20] * c))
    for t in np.linspace(-5, 5, 11):                                               # e^{itH0} は SU(2) に入る
        U = expm(1j * t * H0)
        assert np.allclose(U.conj().T @ U, np.eye(2)) and np.isclose(np.linalg.det(U), 1)

    ax = axes[0]
    th = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(th), np.sin(th), color="#cccccc", lw=1)
    sc = ax.scatter(d1.real, d1.imag, c=ts[::20], cmap="Oranges", s=30, vmin=-T * 0.2, label="$\\mathrm{tr}H=0.5$")
    ax.plot(1, 0, "o", color=C_A, ms=14, mfc="none", mew=3, label="$\\mathrm{tr}H=0$（すべての $t$ で $1$）")
    ax.set_aspect("equal"), ax.set_xlim(-1.4, 1.6), ax.set_ylim(-1.4, 1.4)
    ax.set_xlabel("実部"), ax.set_ylabel("虚部"), ax.legend(fontsize=9.5, loc="lower left")
    ax.set_title("(a) 複素平面：$\\det e^{itH}=e^{it\\,\\mathrm{tr}H}$\n（橙の点は、色が濃いほど $t$ が大きい）", fontsize=11)

    ax = axes[1]
    ax.plot(ts, np.zeros_like(ts), color=C_A, lw=3, label="$\\mathrm{tr}H=0$：偏角はいつも $0$")
    arg1 = np.angle(np.exp(1j * ts * c))
    jumps = np.where(np.abs(np.diff(arg1)) > np.pi)[0]
    segs = np.split(np.arange(len(ts)), jumps + 1)
    for k, sgi in enumerate(segs):
        ax.plot(ts[sgi], np.degrees(arg1[sgi]), color=C_B, lw=2, label="$\\mathrm{tr}H=0.5$：偏角 $0.5t$" if k == 0 else None)
    for k in (1, 2):
        tk = 2 * np.pi * k / c
        assert np.isclose(np.exp(1j * tk * c), 1)
        ax.plot(tk, 0, "o", color=C_BAD, ms=9, zorder=5)
        ax.annotate(f"$t=2\\pi\\cdot{k}/0.5$ で $\\det=1$", xy=(tk, 0), xytext=(tk - 8.5, 120 if k == 1 else -140),
                    fontsize=10, color=C_BAD, arrowprops=dict(arrowstyle="-|>", color=C_BAD))
    ax.set_xlim(0, T + 1.2), ax.set_ylim(-200, 200), ax.set_yticks([-180, -90, 0, 90, 180])
    ax.set_xlabel("$t$"), ax.set_ylabel("$\\det e^{itH}$ の偏角 [度]"), ax.legend(fontsize=9.5, loc="upper right")
    ax.set_title("(b) 偏角：$\\mathrm{tr}H\\neq0$ でも、とびとびの $t$ では $\\det=1$ になる\n→ 1つの $U$ から $\\mathrm{tr}H=0$ は言えない。すべての $t$ で $1$ なら $\\mathrm{tr}H=0$", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "det03_su2_one_parameter.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(det01=det01, det02=det02, det03=det03)

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if a in FIGS] or list(FIGS)
    for name in names:
        FIGS[name]()
        print("書き出し:", name)
