"""power_series_radius_of_convergence.md（べき級数と収束半径）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_power_series_figures.py          # すべて
    uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_power_series_figures.py ps02     # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    ps01_radius_singularity.png   Part II  1/(1+x²) の収束半径は複素平面の ±i で決まる（中心 0 なら 1、中心 1 なら √2）
    ps02_continuation.png         Part III 1/(1−z) の解析接続（円板の鎖で z = 1 を避けて z = 2 へ）と、x = 2 での部分和
    ps03_abel_eta.png             Part III 1 − 2 + 3 − 4 + … のアーベル和 1/4（ζ(−1) = −1/12 への道）
    ps04_flat_function.png        Part IV  e^{−1/x²}：テイラー級数は 0、虚軸の上では爆発する
    ps05_rearrangement.png        付録A    リーマンの再配列定理：並べ替えで和が ln 2 → ln 2 / 2、1.5 に変わる

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from matplotlib.patches import Circle

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"


def coeffs_rational(a: float, K: int) -> np.ndarray:
    """1/(1+z²) を z = a のまわりで展開した係数 c_k（式 (II-3)）。"""
    k = np.arange(K)
    return ((-1 / (1j - a) ** (k + 1) + 1 / (-1j - a) ** (k + 1)) / 2j).real


# ------------------------------------------------------------------------------------- ps01
def ps01():
    """1/(1+x²) の収束半径：中心 0 なら 1、中心 1 なら √2（どちらも ±i までの距離）。"""
    # 係数の確認：中心 0 では 1, 0, −1, 0, 1, …
    assert np.allclose(coeffs_rational(0.0, 6), [1, 0, -1, 0, 1, 0])
    # 根判定法 |c_k|^{−1/k} → R
    for a, R in ((0.0, 1.0), (1.0, np.sqrt(2))):
        c = coeffs_rational(a, 400)
        ks = np.arange(300, 400)
        ks = ks[np.abs(c[ks]) > 1e-12 * np.abs(c[ks]).max()]          # 0 になる係数（奇数次など）は除く
        est = np.abs(c[ks]) ** (-1.0 / ks)
        assert abs(np.median(est) - R) < 0.01, (a, np.median(est))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    for a, R, col in ((0.0, 1.0, C_A), (1.0, np.sqrt(2), C_B)):
        ax.add_patch(Circle((a, 0), R, fc=col, alpha=0.12, ec=col, lw=2))
        ax.plot(a, 0, "o", color=col)
        ax.annotate(f"中心 {a:g}、半径 {R:.3g}", (a, 0), (a - 0.55, -R - 0.32), color=col, fontsize=10)
    for b in (1, -1):
        ax.plot(0, b, "x", color=C_BAD, ms=12, mew=3)
        ax.annotate(f"$z={'' if b > 0 else '-'}i$（分母が 0）", (0, b), (0.12, b + 0.12 * b), color=C_BAD, fontsize=10)
    ax.plot([1, 0], [0, 1], color=C_B, ls=":", lw=1.5)
    ax.axhline(0, color="#ccc", lw=0.8)
    ax.axvline(0, color="#ccc", lw=0.8)
    ax.set_xlim(-1.8, 2.8)
    ax.set_ylim(-2.0, 1.9)
    ax.set_aspect("equal")
    ax.set_xlabel("実部")
    ax.set_ylabel("虚部")
    ax.set_title("(a) 複素平面：収束する円板は、一番近い $\\pm i$ で止まる", fontsize=11)

    ax = axes[1]
    xs = np.linspace(-1.6, 3.0, 600)
    ax.plot(xs, 1 / (1 + xs**2), color="#aaa", lw=5, label="$1/(1+x^2)$")
    for a, R, col in ((0.0, 1.0, C_A), (1.0, np.sqrt(2), C_B)):
        c = coeffs_rational(a, 41)
        S = sum(c[k] * (xs - a) ** k for k in range(41))
        ax.plot(xs, np.clip(S, -1, 2), color=col, lw=1.8, label=f"中心 {a:g} の40次までの部分和")
        ax.axvspan(a - R, a + R, color=col, alpha=0.08)
    ax.set_ylim(-0.3, 1.3)
    ax.set_xlabel("$x$（実数）")
    ax.set_title("(b) 実軸の上：部分和が合うのは、円板と実軸が重なる区間だけ", fontsize=11)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "ps01_radius_singularity.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- ps02
def ps02():
    """1/(1−z) の解析接続：円板の鎖で z = 1 を避けて z = 2 へ。x = 2 での部分和は発散。"""
    f = lambda z: 1 / (1 - z)
    # 中心 a のまわりの展開 1/(1−z) = Σ (z−a)^k / (1−a)^{k+1}（式 (III-3)）、半径 |1−a|
    centers = [0.0, 0.6j, 1.0 + 0.9j, 1.7 + 0.6j, 2.0 + 0.0j]
    for a, b in zip(centers[:-1], centers[1:]):
        assert abs(b - a) < abs(1 - a), (a, b)                       # 次の中心は、今の円板の内側
        S = sum((b - a) ** k / (1 - a) ** (k + 1) for k in range(400))
        assert abs(S - f(b)) < 1e-8                                    # 今の級数で、次の中心での値が正しく出る
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    cols = plt.cm.viridis(np.linspace(0.1, 0.85, len(centers)))
    for a, col in zip(centers, cols):
        R = abs(1 - a)
        ax.add_patch(Circle((a.real, a.imag), R, fc=col, alpha=0.10, ec=col, lw=1.8))
        ax.plot(a.real, a.imag, "o", color=col)
    ax.plot([c.real for c in centers], [c.imag for c in centers], "-", color="#555", lw=1)
    ax.plot(1, 0, "x", color=C_BAD, ms=13, mew=3)
    ax.annotate("$z=1$（分母が 0）", (1, 0), (1.05, -0.35), color=C_BAD, fontsize=10)
    ax.annotate("出発：中心 0、半径 1", (0, 0), (-1.0, -1.25), fontsize=10, color=cols[0])
    ax.annotate("到着：$z=2$ で値 $-1$", (2, 0), (1.6, -1.25), fontsize=10, color=cols[-1])
    ax.axhline(0, color="#ccc", lw=0.8)
    ax.set_xlim(-1.3, 3.3)
    ax.set_ylim(-1.5, 2.3)
    ax.set_aspect("equal")
    ax.set_xlabel("実部")
    ax.set_ylabel("虚部")
    ax.set_title("(a) 円板の鎖で $z=1$ を避けて、$z=2$ まで関数を延ばす", fontsize=11)

    ax = axes[1]
    N = np.arange(0, 21)
    partial = np.cumsum(2.0 ** N)
    assert partial[-1] == 2**21 - 1
    ax.semilogy(N, partial, "o-", color=C_A, label="部分和 $1+2+4+\\cdots+2^N=2^{N+1}-1$（発散）")
    ax.axhline(1, color=C_BAD, ls="--", label="関数の値 $1/(1-2)=-1$ の絶対値")
    ax.set_xlabel("$N$")
    ax.set_title("(b) $x=2$ では、級数は発散するが、関数には値がある", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "ps02_continuation.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- ps03
def ps03():
    """1 − 2 + 3 − 4 + … のアーベル和：Σ (−1)^{n+1} n x^{n−1} = 1/(1+x)² → 1/4。"""
    xs = np.linspace(0, 0.999, 300)
    exact = 1 / (1 + xs) ** 2
    n = np.arange(1, 20001)
    series = np.array([np.sum((-1.0) ** (n + 1) * n * x ** (n - 1)) for x in xs[::30]])
    assert np.allclose(series, exact[::30], atol=1e-6)               # 式 (III-6)
    assert abs(1 / (1 + 1) ** 2 - 0.25) < 1e-15
    # ζ(−1) = η(−1)/(1 − 2^{2}) = (1/4)/(−3) = −1/12（式 (III-8)）
    assert sp.zeta(-1) == sp.Rational(-1, 12)
    assert sp.Rational(1, 4) / (1 - 2**2) == sp.Rational(-1, 12)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    N = np.arange(1, 21)
    ps = np.cumsum((-1.0) ** (N + 1) * N)
    ax.plot(N, ps, "o-", color=C_A, label="部分和 $1-2+3-4+\\cdots\\pm N$")
    ax.axhline(0.25, color=C_BAD, ls="--", label="アーベル和 $1/4$")
    ax.set_xlabel("$N$")
    ax.set_title("(a) 部分和は $1,-1,2,-2,3,\\dots$ と振れて収束しない", fontsize=11)
    ax.legend(fontsize=9)
    ax = axes[1]
    ax.plot(xs, exact, color=C_A, lw=2.5, label="$\\sum_{n\\geq 1}(-1)^{n+1}nx^{n-1}=\\frac{1}{(1+x)^2}$")
    ax.plot(xs[::30], series, "o", color=C_B, label="級数を数値で足したもの")
    ax.plot(1, 0.25, "o", color=C_BAD, ms=9)
    ax.annotate("$x\\to1$ で $1/4$", (1, 0.25), (0.62, 0.42), color=C_BAD, fontsize=11,
                arrowprops=dict(arrowstyle="-|>", color=C_BAD))
    ax.set_xlabel("$x$")
    ax.set_title("(b) $x<1$ では収束し、$x\\to1$ の極限は $1/4$", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "ps03_abel_eta.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- ps04
def ps04():
    """e^{−1/x²}：実軸ではなめらかで、テイラー級数は 0。虚軸の上では e^{+1/y²} と爆発する。"""
    x = sp.symbols("x", real=True)
    f = sp.exp(-1 / x**2)
    for k in range(1, 5):
        assert sp.limit(sp.diff(f, x, k), x, 0) == 0                 # k 回微分の x → 0 の極限は 0
    # f'(x) = (2/x³) e^{−1/x²}（式 (IV-2)）
    assert sp.simplify(sp.diff(f, x) - 2 / x**3 * f) == 0

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    xs = np.linspace(-2.5, 2.5, 600)
    with np.errstate(divide="ignore"):
        ys = np.where(xs == 0, 0.0, np.exp(-1 / xs**2))
    ax.plot(xs, ys, color=C_A, lw=2.5, label="$f(x)=e^{-1/x^2}$（$f(0)=0$）")
    ax.plot(xs, 0 * xs, color=C_BAD, ls="--", lw=2, label="$x=0$ でのテイラー級数（すべての項が 0）")
    ax.set_xlabel("$x$")
    ax.set_title("(a) 級数はどこでも収束するが、$f$ とは違う関数（0）", fontsize=11)
    ax.legend(fontsize=9, loc="upper center")
    ax.set_ylim(-0.1, 1.0)

    ax = axes[1]
    t = np.linspace(0.25, 2.0, 300)
    real_axis = np.exp(-1 / t**2)                                   # z = t（実軸）
    imag_axis = np.abs(np.exp(-1 / (1j * t) ** 2))                  # z = it（虚軸）：e^{+1/t²}
    assert np.allclose(imag_axis, np.exp(1 / t**2))
    ax.semilogy(t, real_axis, color=C_A, lw=2.5, label="実軸 $z=t$：$e^{-1/t^2}\\to0$")
    ax.semilogy(t, imag_axis, color=C_BAD, lw=2.5, label="虚軸 $z=it$：$|e^{-1/z^2}|=e^{+1/t^2}\\to\\infty$")
    ax.set_xlabel("原点からの距離 $t$")
    ax.set_title("(b) 複素数で見ると、$z=0$ は激しい特異点", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "ps04_flat_function.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- ps05
def rearranged_partial_sums(target: float, n_terms: int) -> np.ndarray:
    """1 − 1/2 + 1/3 − … の項を並べ替えて target に近づける（付録A の手順）。"""
    pos, neg = 1, 2                                      # 次に使う正の項 1/pos（奇数）、負の項 −1/neg（偶数）
    s, out = 0.0, []
    for _ in range(n_terms):
        if s <= target:
            s += 1 / pos
            pos += 2
        else:
            s -= 1 / neg
            neg += 2
        out.append(s)
    return np.array(out)


def ps05():
    """リーマンの再配列定理：同じ項の並べ替えで、和が ln 2、ln 2 / 2、1.5 などに変わる。"""
    K = 3000
    k = np.arange(1, K + 1)
    original = np.cumsum((-1.0) ** (k + 1) / k)
    assert abs(original[-1] - np.log(2)) < 1e-3
    # 正1つ・負2つの順：1 − 1/2 − 1/4 + 1/3 − 1/6 − 1/8 + …（式 (A-1)）
    terms = []
    for j in range(1, K // 3 + 1):
        terms += [1 / (2 * j - 1), -1 / (4 * j - 2), -1 / (4 * j)]
    half = np.cumsum(terms)
    assert abs(half[-1] - np.log(2) / 2) < 1e-3
    to15 = rearranged_partial_sums(1.5, 20000)
    assert abs(to15[-1] - 1.5) < 1e-2

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    n = 300
    ax.plot(np.arange(1, n + 1), original[:n], color=C_A, lw=1.2, label="元の順：$1-\\frac{1}{2}+\\frac{1}{3}-\\frac{1}{4}+\\cdots\\to\\ln2$")
    ax.plot(np.arange(1, n + 1), half[:n], color=C_B, lw=1.2, label="正1つ・負2つの順 $\\to\\frac{1}{2}\\ln2$")
    ax.plot(np.arange(1, n + 1), to15[:n], color=C_C, lw=1.2, label="目標 $1.5$ を越えたら負、下回ったら正 $\\to1.5$")
    for y, col in ((np.log(2), C_A), (np.log(2) / 2, C_B), (1.5, C_C)):
        ax.axhline(y, color=col, ls="--", lw=0.8)
    ax.set_xlabel("足した項の数")
    ax.set_ylabel("部分和")
    ax.set_ylim(0, 1.8)
    ax.set_title("同じ項（$\\pm1/n$ をすべて1回ずつ）でも、並べる順番で和が変わる", fontsize=11)
    ax.legend(fontsize=9, loc="center right")
    fig.tight_layout()
    fig.savefig(OUT / "ps05_rearrangement.png", dpi=150)
    plt.close(fig)


FIGS = {"ps01": ps01, "ps02": ps02, "ps03": ps03, "ps04": ps04, "ps05": ps05}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGS:
        FIGS[name]()
        print("保存:", name)
