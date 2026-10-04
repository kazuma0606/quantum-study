"""normalizing_flows_introduction.md（正規化フロー入門）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/06_確率・統計/figures/make_normalizing_flow_figures.py          # すべて
    uv run python 研究ノート/06_確率・統計/figures/make_normalizing_flow_figures.py nf02     # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    nf01_change_of_variables_1d.png   Part I   1次元の変数変換：正規分布 → 対数正規分布、一様分布 → 指数分布（逆関数法）
    nf02_coupling_banana.png          Part III カップリング層：正規分布をバナナ形に変形し、公式の密度とヒストグラムを比べる
    nf03_linear_flow_trace.png        Part III 連続時間のフロー：線形の流れで log p が −t tr A だけ変わる
    nf04_base_choice.png              Part IV  基底分布の選び方：裾の重さ（正規分布 vs t 分布）と、つながり方の制約
    nf05_diffusion_probability_flow.png  Part VI 拡散：確率微分方程式と、同じ分布を運ぶ決定論的な流れ
    nf06_quantum_probability_current.png Part VI 自由粒子のガウス波束：確率の流れ j と、それに乗った軌跡

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.linalg import expm

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"
rng = np.random.default_rng(0)


def hist_density(samples: np.ndarray, edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h, e = np.histogram(samples, bins=edges, density=False)
    width = np.diff(e)
    return (e[:-1] + e[1:]) / 2, h / (len(samples) * width)


# ------------------------------------------------------------------------------------- nf01
def nf01():
    """(a) z ~ N(0,1)、x = e^z の密度 φ(ln x)/x（式 (I-3)）。(b) u ~ U(0,1)、x = −ln(1−u) は指数分布（式 (I-5)）。"""
    n = 400_000
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))

    ax = axes[0]
    x = np.exp(rng.standard_normal(n))
    edges = np.linspace(0.02, 6, 120)
    c, d = hist_density(x, edges)
    formula = stats.norm.pdf(np.log(c)) / c
    assert np.max(np.abs(d - formula)) < 0.03                       # ヒストグラムと公式が一致
    ax.bar(c, d, width=np.diff(edges), color=C_A, alpha=0.35, label="$x=e^z$ のヒストグラム（$z\\sim N(0,1)$）")
    ax.plot(c, formula, color=C_BAD, lw=2, label="公式 $p_x(x)=\\varphi(\\ln x)\\cdot\\frac{1}{x}$")
    ax.set_xlabel("$x$")
    ax.set_title("(a) 正規分布を $e^z$ で写すと、対数正規分布", fontsize=11)
    ax.legend(fontsize=9)

    ax = axes[1]
    u = rng.uniform(size=n)
    x = -np.log(1 - u)
    edges = np.linspace(0, 6, 120)
    c, d = hist_density(x, edges)
    assert np.max(np.abs(d - np.exp(-c))) < 0.03
    ax.bar(c, d, width=np.diff(edges), color=C_B, alpha=0.35, label="$x=-\\ln(1-u)$ のヒストグラム（$u\\sim U(0,1)$）")
    ax.plot(c, np.exp(-c), color=C_BAD, lw=2, label="指数分布 $e^{-x}$")
    ax.set_xlabel("$x$")
    ax.set_title("(b) 一様分布を累積分布関数の逆関数で写すと、狙った分布", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "nf01_change_of_variables_1d.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- nf02
def s_fn(z1):
    return 0.3 * z1


def t_fn(z1):
    return 0.8 * z1**2 - 1.5


def coupling_forward(z):
    z1, z2 = z[..., 0], z[..., 1]
    return np.stack([z1, z2 * np.exp(s_fn(z1)) + t_fn(z1)], axis=-1)


def coupling_inverse(x):
    x1, x2 = x[..., 0], x[..., 1]
    return np.stack([x1, (x2 - t_fn(x1)) * np.exp(-s_fn(x1))], axis=-1)


def coupling_density(x):
    """p_x(x) = φ(z1) φ(z2) · |det J_f(z)|^{-1}、det J_f = e^{s(z1)}（式 (III-3)）。"""
    z = coupling_inverse(x)
    return stats.norm.pdf(z[..., 0]) * stats.norm.pdf(z[..., 1]) * np.exp(-s_fn(z[..., 0]))


def nf02():
    """カップリング層で、正規分布をバナナ形に変形する。"""
    # 逆写像が正しいこと
    zt = rng.standard_normal((1000, 2))
    assert np.allclose(coupling_inverse(coupling_forward(zt)), zt)
    # ヤコビ行列の行列式を数値微分で確認：det J = e^{s(z1)}
    for z in zt[:5]:
        h = 1e-6
        J = np.stack([(coupling_forward(z + h * e) - coupling_forward(z - h * e)) / (2 * h) for e in np.eye(2)], axis=1)
        assert np.isclose(np.linalg.det(J), np.exp(s_fn(z[0])), rtol=1e-6)
        assert abs(J[0, 1]) < 1e-9                                  # 三角（右上が 0）
    # 密度の全体の積分が 1
    g1, g2 = np.meshgrid(np.linspace(-5, 5, 401), np.linspace(-6, 20, 1041))
    dens = coupling_density(np.stack([g1, g2], axis=-1))
    area = (g1[0, 1] - g1[0, 0]) * (g2[1, 0] - g2[0, 0])
    assert abs(dens.sum() * area - 1) < 1e-3

    n = 200_000
    z = rng.standard_normal((n, 2))
    x = coupling_forward(z)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    axes[0].scatter(z[:3000, 0], z[:3000, 1], s=2, color=C_A, alpha=0.5)
    axes[0].set_title("(a) $\\mathbf{z}\\sim N(0,I)$", fontsize=11)
    axes[1].scatter(x[:3000, 0], x[:3000, 1], s=2, color=C_B, alpha=0.5)
    axes[1].set_title("(b) $\\mathbf{x}=\\mathbf{f}(\\mathbf{z})$：カップリング層で写したもの", fontsize=11)
    # 公式の密度と、ヒストグラムの比較（等高線）
    H, xe, ye = np.histogram2d(x[:, 0], x[:, 1], bins=[60, 60], range=[[-3.5, 3.5], [-2.5, 6.5]])
    H = H / (n * (xe[1] - xe[0]) * (ye[1] - ye[0]))                # 範囲外のサンプルも含めた全体で割る
    xc, yc = (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2
    X, Y = np.meshgrid(xc, yc, indexing="ij")
    D = coupling_density(np.stack([X, Y], axis=-1))
    assert np.max(np.abs(H - D)) < 0.025
    levels = [0.01, 0.03, 0.06, 0.1]
    axes[2].contour(X, Y, H, levels=levels, colors=C_B, linewidths=1.2)
    axes[2].contour(X, Y, D, levels=levels, colors=C_BAD, linestyles="--", linewidths=1.2)
    axes[2].plot([], [], color=C_B, label="サンプルのヒストグラム")
    axes[2].plot([], [], color=C_BAD, ls="--", label="公式 $p_{\\mathbf{z}}(\\mathbf{z})\\,e^{-s(z_1)}$")
    axes[2].legend(fontsize=9, loc="upper center")
    axes[2].set_title("(c) 密度の等高線：公式とサンプルが一致", fontsize=11)
    for ax in axes:
        ax.set_xlim(-3.5, 3.5)
        ax.set_xlabel("1番目の成分")
    axes[0].set_ylim(-3.5, 3.5)
    axes[1].set_ylim(-2.5, 6.5)
    axes[2].set_ylim(-2.5, 6.5)
    axes[0].set_ylabel("2番目の成分")
    fig.tight_layout()
    fig.savefig(OUT / "nf02_coupling_banana.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- nf03
def nf03():
    """線形の流れ dx/dt = A x：log p(x(t), t) − log p(x(0), 0) = −t tr A（式 (III-7)）。"""
    A = np.array([[-0.35, 1.2], [-1.2, -0.35]])                   # 回りながら縮む（tr A = −0.7）
    trA = np.trace(A)
    ts = np.linspace(0, 3, 31)
    for t in ts:
        assert np.isclose(np.log(np.linalg.det(expm(t * A))), t * trA)   # log det e^{tA} = t tr A
    # ハッチンソンのトレース推定：E[ε^T A ε] = tr A
    eps = rng.choice([-1.0, 1.0], size=(200_000, 2))
    est = np.mean(np.einsum("ni,ij,nj->n", eps, A, eps))
    assert abs(est - trA) < 0.01

    z = rng.standard_normal((2000, 2))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    ax = axes[0]
    for t, col in ((0.0, C_A), (1.0, C_B), (2.5, C_BAD)):
        x = z @ expm(t * A).T
        ax.scatter(x[:, 0], x[:, 1], s=2, color=col, alpha=0.4, label=f"$t={t:g}$")
    ax.set_aspect("equal")
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.legend(fontsize=9, markerscale=5)
    ax.set_title("(a) $\\dot{\\mathbf{x}}=A\\mathbf{x}$ で運ばれる点（回りながら縮む）", fontsize=11)
    ax = axes[1]
    ax.plot(ts, -ts * trA, color=C_A, lw=2.5, label="$-t\\,\\mathrm{tr}A$")
    ax.plot(ts, [-np.log(np.linalg.det(expm(t * A))) for t in ts], "o", color=C_BAD, ms=4,
            label="$-\\log\\det e^{tA}$（変数変換の公式）")
    ax.set_xlabel("$t$")
    ax.set_ylabel("$\\log p(\\mathbf{x}(t),t)-\\log p(\\mathbf{x}(0),0)$")
    ax.set_title(f"(b) 密度は $e^{{-t\\,\\mathrm{{tr}}A}}$ 倍（$\\mathrm{{tr}}A={trA:g}$ なので濃くなる）", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "nf03_linear_flow_trace.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- nf04
def nf04():
    """(a) 裾の重さ：正規分布と t 分布の裾。(b) 連続な逆写像は、1つの塊を2つに切り離せない（細い橋が残る）。"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    ax = axes[0]
    xs = np.linspace(0, 12, 300)
    ax.semilogy(xs, stats.norm.sf(xs), color=C_A, lw=2.2, label="正規分布：$P(X>x)$")
    ax.semilogy(xs, stats.t.sf(xs, df=2), color=C_BAD, lw=2.2, label="$t$ 分布（自由度 2）：$P(X>x)$")
    assert stats.norm.sf(8) < 1e-15 and stats.t.sf(8, df=2) > 5e-3   # 約 6e-16 と約 7.6e-3
    ax.set_ylim(1e-30, 1)
    ax.set_xlabel("$x$")
    ax.set_title("(a) 裾の重さ：$x=8$ を越える確率は 約 $6\\times10^{-16}$ 対 約 $8\\times10^{-3}$", fontsize=11)
    ax.legend(fontsize=9)

    ax = axes[1]
    # 1次元で、正規分布を2つの山に写す単調な写像（逆関数法）：2つの山の間に必ず密度の「橋」が残る
    mix = lambda x: 0.5 * stats.norm.pdf(x, -2.5, 0.5) + 0.5 * stats.norm.pdf(x, 2.5, 0.5)
    xs = np.linspace(-5, 5, 2001)
    cdf = np.cumsum(mix(xs)) * (xs[1] - xs[0])
    z = rng.standard_normal(200_000)
    x = np.interp(stats.norm.cdf(z), cdf / cdf[-1], xs)             # x = F_mix^{-1}(Φ(z))
    edges = np.linspace(-5, 5, 101)
    c, d = hist_density(x, edges)
    assert np.max(np.abs(d - mix(c))) < 0.03
    ax.bar(c, d, width=np.diff(edges), color=C_B, alpha=0.35, label="$F^{-1}(\\Phi(z))$ のヒストグラム")
    ax.plot(xs, mix(xs), color=C_BAD, lw=2, label="目標：2つの山")
    ax.set_xlabel("$x$")
    ax.set_title("(b) 1つの山を2つの山へ：間を薄くできても、写像は急勾配になる", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "nf04_base_choice.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- nf05
def nf05():
    """純粋な拡散 dx = √(2D) dW と、同じ密度を運ぶ決定論的な流れ dx/dt = D x / σ(t)²（式 (VI-6)〜(VI-8)）。"""
    D, s0, T, n_steps = 0.5, 0.5, 2.0, 400
    dt = T / n_steps
    ts = np.linspace(0, T, n_steps + 1)
    sig = np.sqrt(s0**2 + 2 * D * ts)                               # σ(t)² = σ0² + 2Dt
    n = 100_000
    x0 = rng.normal(0, s0, n)
    # 確率微分方程式（オイラー・丸山法）
    xs = x0.copy()
    paths_sde = [xs[:12].copy()]
    for _ in range(n_steps):
        xs = xs + np.sqrt(2 * D * dt) * rng.standard_normal(n)
        paths_sde.append(xs[:12].copy())
    paths_sde = np.array(paths_sde)
    # 決定論的な流れ：x(t) = x0 σ(t)/σ0
    xf = x0 * sig[-1] / s0
    paths_flow = np.outer(sig / s0, x0[:12])
    # 速度場が dx/dt = D x / σ² を満たすこと（数値微分）
    v_num = np.gradient(paths_flow, ts, axis=0)
    assert np.allclose(v_num[1:-1], D * paths_flow[1:-1] / sig[1:-1, None] ** 2, rtol=1e-3)
    # 時刻 T の分布：どちらも N(0, σ(T)²)
    for samples in (xs, xf):
        assert abs(samples.std() - sig[-1]) < 0.01 and abs(samples.mean()) < 0.01

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    ax = axes[0]
    ax.plot(ts, paths_sde, color=C_A, lw=0.8, alpha=0.8)
    ax.plot(ts, sig, "k--", lw=1)
    ax.plot(ts, -sig, "k--", lw=1)
    ax.set_title("(a) 確率微分方程式：1粒ずつはランダムに揺れる", fontsize=11)
    ax.set_xlabel("$t$")
    ax = axes[1]
    ax.plot(ts, paths_flow, color=C_B, lw=1.2)
    ax.plot(ts, sig, "k--", lw=1, label="$\\pm\\sigma(t)$")
    ax.plot(ts, -sig, "k--", lw=1)
    ax.set_title("(b) 確率フロー：$\\dot x=Dx/\\sigma(t)^2$ でなめらかに広がる", fontsize=11)
    ax.set_xlabel("$t$")
    ax.legend(fontsize=9)
    for a in axes[:2]:
        a.set_ylim(-3.5, 3.5)
    ax = axes[2]
    edges = np.linspace(-4, 4, 81)
    for samples, col, lab in ((xs, C_A, "(a) の時刻 $T$ の分布"), (xf, C_B, "(b) の時刻 $T$ の分布")):
        c, d = hist_density(samples, edges)
        ax.step(c, d, where="mid", color=col, lw=1.5, label=lab)
    xx = np.linspace(-4, 4, 300)
    ax.plot(xx, stats.norm.pdf(xx, 0, sig[-1]), "k--", lw=1.2, label=f"$N(0,\\sigma(T)^2)$、$\\sigma(T)={sig[-1]:.2f}$")
    ax.set_title("(c) 軌跡は違っても、分布は一致する", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "nf05_diffusion_probability_flow.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- nf06
def nf06():
    """自由粒子のガウス波束（ħ = m = 1）：|ψ|² の連続の式と、確率の流れに乗った軌跡（式 (VI-11)〜(VI-15)）。"""
    s0 = 1.0
    L, N = 80.0, 4096
    x = np.linspace(-L / 2, L / 2, N, endpoint=False)
    dx = x[1] - x[0]
    k = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    psi0 = (2 * np.pi * s0**2) ** (-0.25) * np.exp(-x**2 / (4 * s0**2))

    def evolve(t):
        return np.fft.ifft(np.exp(-1j * k**2 * t / 2) * np.fft.fft(psi0))   # 自由粒子の厳密な時間発展

    def current(psi):
        dpsi = np.fft.ifft(1j * k * np.fft.fft(psi))
        return np.imag(np.conj(psi) * dpsi)                               # j = Im(ψ* ψ')

    sigma = lambda t: s0 * np.sqrt(1 + (t / (2 * s0**2)) ** 2)            # σ(t)² = σ0²(1 + (t/2σ0²)²)
    # 連続の式 ∂ρ/∂t = −∂j/∂x を数値で確認
    t, h = 3.0, 1e-4
    rho_dot = (np.abs(evolve(t + h)) ** 2 - np.abs(evolve(t - h)) ** 2) / (2 * h)
    j = current(evolve(t))
    dj = np.real(np.fft.ifft(1j * k * np.fft.fft(j)))
    assert np.max(np.abs(rho_dot + dj)) < 1e-6
    # 速度場 v = j/ρ が x σ'(t)/σ(t) に等しい（中心付近、ρ が小さすぎない所）
    rho = np.abs(evolve(t)) ** 2
    mask = rho > 1e-6
    sp_ = (sigma(t + h) - sigma(t - h)) / (2 * h)
    assert np.allclose(j[mask] / rho[mask], (x * sp_ / sigma(t))[mask], atol=1e-6)
    # 幅が σ(t) で広がること
    for tt in (0.0, 2.0, 6.0):
        r = np.abs(evolve(tt)) ** 2
        assert abs(np.sqrt(np.sum(x**2 * r) * dx) - sigma(tt)) < 1e-6

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    ax = axes[0]
    for tt, col in ((0.0, C_A), (3.0, C_B), (8.0, C_BAD)):
        ax.plot(x, np.abs(evolve(tt)) ** 2, color=col, lw=2, label=f"$t={tt:g}$")
    ax.set_xlim(-12, 12)
    ax.set_xlabel("$x$")
    ax.set_title("(a) $|\\psi(x,t)|^2$：自由粒子の波束は広がる", fontsize=11)
    ax.legend(fontsize=9)
    ax = axes[1]
    ts = np.linspace(0, 8, 200)
    for q in np.linspace(-1.6, 1.6, 9):
        ax.plot(ts, q * s0 * sigma(ts) / s0, color=C_B, lw=1.2)
    ax.plot(ts, sigma(ts), "k--", lw=1, label="$\\pm\\sigma(t)$")
    ax.plot(ts, -sigma(ts), "k--", lw=1)
    ax.set_xlabel("$t$")
    ax.set_title("(b) 確率の流れ $v=j/|\\psi|^2$ に乗った軌跡", fontsize=11)
    ax.legend(fontsize=9)
    ax = axes[2]
    ts = np.linspace(0, 8, 200)
    ax.plot(ts, sigma(ts), color=C_BAD, lw=2.2, label="量子の波束：$\\sigma_0\\sqrt{1+(t/2\\sigma_0^2)^2}$（やがて $\\propto t$）")
    ax.plot(ts, np.sqrt(s0**2 + 2 * 0.5 * ts), color=C_A, lw=2.2, label="拡散（$D=0.5$）：$\\sqrt{\\sigma_0^2+2Dt}$（$\\propto\\sqrt{t}$）")
    ax.set_xlabel("$t$")
    ax.set_ylabel("幅 $\\sigma(t)$")
    ax.set_title("(c) 広がり方の違い：量子は直線的、拡散は $\\sqrt{t}$", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "nf06_quantum_probability_current.png", dpi=150)
    plt.close(fig)


FIGS = {"nf01": nf01, "nf02": nf02, "nf03": nf03, "nf04": nf04, "nf05": nf05, "nf06": nf06}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGS:
        FIGS[name]()
        print("保存:", name)
