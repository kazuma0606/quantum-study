"""matrix_exponential_commutator_bch_trotter.md（行列の指数関数と交換子）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/04_群論・代数/figures/make_matrix_exp_commutator_figures.py          # すべて
    uv run python 研究ノート/04_群論・代数/figures/make_matrix_exp_commutator_figures.py mexp02   # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    mexp01_jordan.png              Part II  ジョルダン細胞：e^{tN} はずれ（面積を保つ）、臨界減衰の t e^{λt}
    mexp02_group_commutator.png    Part III 群の交換子：x 軸・z 軸まわりの回転を行って戻ると、閉じない（ずれ ≈ st）
    mexp03_bch_orders.png          Part IV  BCH の公式を 1・2・3 次で打ち切った誤差（傾き 2・3・4）
    mexp04_trotter_strang.png      Part VI  トロッター分解とストラング分解の誤差と、本文の上限

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import expm, logm

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"

SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]])
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def comm(a, b):
    return a @ b - b @ a


# ------------------------------------------------------------------------------------- mexp01
def mexp01():
    """ジョルダン細胞：(a) e^{tN} = [[1, t], [0, 1]] で正方形がずれる、(b) 臨界減衰 x'' + 2x' + x = 0。"""
    N = np.array([[0.0, 1.0], [0.0, 0.0]])
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))

    ax = axes[0]
    square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=float).T
    for t, col in ((0.0, C_GRAY), (0.5, C_A), (1.0, C_B), (2.0, C_BAD)):
        M = expm(t * N)
        assert np.allclose(M, [[1, t], [0, 1]])                       # 式 (II-3)：e^{tN} = I + tN
        assert np.isclose(np.linalg.det(M), 1.0)                      # det e^{tN} = e^{tr(tN)} = 1
        P = M @ square
        ax.fill(P[0], P[1], alpha=0.18, color=col)
        ax.plot(P[0], P[1], color=col, lw=2, label=f"$t={t:g}$（面積 1）")
    ax.set_aspect("equal")
    ax.set_xlim(-0.3, 3.3)
    ax.set_ylim(-0.3, 1.5)
    ax.set_title("(a) $e^{tN}=I+tN$：正方形が横にずれる（面積は 1 のまま）")
    ax.legend(loc="upper right", fontsize=9)

    ax = axes[1]
    # x'' + 2x' + x = 0 を (x, v) の1階系にすると、行列 A = [[0, 1], [-1, -2]]。固有値 −1 が重なり、対角化できない
    A = np.array([[0.0, 1.0], [-1.0, -2.0]])
    Nn = A + np.eye(2)
    assert np.allclose(Nn @ Nn, 0)                                    # A = −I + N、N² = 0
    ts = np.linspace(0, 8, 300)
    xs = np.array([(expm(t * A) @ np.array([1.0, 0.0]))[0] for t in ts])
    assert np.allclose(xs, (1 + ts) * np.exp(-ts))                    # 式 (II-6)：x(t) = (1 + t) e^{−t}
    ax.plot(ts, xs, color=C_A, lw=2.5, label="$x(t)=(1+t)e^{-t}$（$e^{tA}$ の第1成分）")
    ax.plot(ts, np.exp(-ts), color=C_GRAY, lw=1.5, ls="--", label="$e^{-t}$（固有値だけで決まる部分）")
    ax.plot(ts, ts * np.exp(-ts), color=C_B, lw=1.5, ls=":", label="$te^{-t}$（ジョルダン細胞から出る項）")
    ax.set_xlabel("$t$")
    ax.set_title("(b) 臨界減衰 $x''+2x'+x=0$、$x(0)=1,\\ x'(0)=0$")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "mexp01_jordan.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mexp02
def mexp02():
    """群の交換子：回転 e^{sLx}, e^{tLz}, e^{−sLx}, e^{−tLz} を順に行うと、出発点に戻らない。"""
    Lx = np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)   # x 軸まわりの回転の生成子
    Ly = np.array([[0, 0, 1], [0, 0, 0], [-1, 0, 0]], dtype=float)
    Lz = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
    assert np.allclose(comm(Lz, Lx), Ly)                             # [Lz, Lx] = Ly（[Lx, Lz] = −Ly）

    fig = plt.figure(figsize=(11.5, 4.8))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, 40), np.linspace(0, np.pi, 20))
    ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="#ddd", lw=0.5)
    s = t = 0.8
    p0 = np.array([1.0, 0.0, 1.0]) / np.sqrt(2)
    steps = [(Lx, s, "① $x$ 軸まわり $+s$"), (Lz, t, "② $z$ 軸まわり $+t$"),
             (Lx, -s, "③ $x$ 軸まわり $-s$"), (Lz, -t, "④ $z$ 軸まわり $-t$")]
    cols = [C_A, C_B, C_C, "#9467bd"]
    p = p0.copy()
    for (L, ang, lab), col in zip(steps, cols):
        arc = np.array([expm(a * L) @ p for a in np.linspace(0, ang, 40)])
        ax.plot(arc[:, 0], arc[:, 1], arc[:, 2], color=col, lw=2.5, label=lab)
        p = arc[-1]
    ax.scatter(*p0, color="k", s=40)
    ax.scatter(*p, color=C_BAD, s=40)
    ax.plot([p0[0], p[0]], [p0[1], p[1]], [p0[2], p[2]], color=C_BAD, lw=2, ls="--", label="ずれ（閉じない）")
    ax.set_box_aspect((1, 1, 1))
    for setter in (ax.set_xticks, ax.set_yticks, ax.set_zticks):
        setter([-1, 0, 1])
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_zlabel("$z$")
    ax.view_init(elev=22, azim=35)
    ax.set_title("(a) 行って戻る4つの回転（$s=t=0.8$）", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")

    ax = fig.add_subplot(1, 2, 2)
    eps = np.logspace(-3, -0.3, 20)
    gaps, preds = [], []
    for e in eps:
        G = expm(e * Lx) @ expm(e * Lz) @ expm(-e * Lx) @ expm(-e * Lz)
        gaps.append(np.linalg.norm(G - np.eye(3), 2))
        preds.append(np.linalg.norm(e * e * comm(Lx, Lz), 2))           # 式 (III-5)：G ≈ I + st[X, Y]
    gaps, preds = np.array(gaps), np.array(preds)
    slope = np.polyfit(np.log(eps[:10]), np.log(gaps[:10]), 1)[0]
    assert abs(slope - 2) < 0.02 and abs(gaps[0] / preds[0] - 1) < 1e-2
    ax.loglog(eps, gaps, "o-", color=C_A, label="$\\|e^{sL_x}e^{tL_z}e^{-sL_x}e^{-tL_z}-I\\|$")
    ax.loglog(eps, preds, "--", color=C_GRAY, label="$st\\,\\|[L_x,L_z]\\|$")
    ax.set_xlabel("$s=t$")
    ax.set_title(f"(b) ずれは $st$ に比例（傾き {slope:.2f}）", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "mexp02_group_commutator.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mexp03
def mexp03():
    """BCH の公式を 1・2・3 次で打ち切った誤差。"""
    rng = np.random.default_rng(3)
    X0 = rng.normal(size=(3, 3)) * 0.5
    Y0 = rng.normal(size=(3, 3)) * 0.5
    ts = np.logspace(-2.5, -0.5, 15)
    errs = {1: [], 2: [], 3: []}
    for t in ts:
        X, Y = t * X0, t * Y0
        Z = logm(expm(X) @ expm(Y)).real
        z1 = X + Y
        z2 = z1 + comm(X, Y) / 2
        z3 = z2 + (comm(X, comm(X, Y)) + comm(Y, comm(Y, X))) / 12        # 式 (IV-5)
        for k, zk in ((1, z1), (2, z2), (3, z3)):
            errs[k].append(np.linalg.norm(Z - zk, 2))
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    labels = {1: "$X+Y$ まで", 2: "$+\\frac{1}{2}[X,Y]$ まで", 3: "$+\\frac{1}{12}([X,[X,Y]]+[Y,[Y,X]])$ まで"}
    for k, col in ((1, C_BAD), (2, C_B), (3, C_A)):
        e = np.array(errs[k])
        slope = np.polyfit(np.log(ts[:10]), np.log(e[:10]), 1)[0]
        assert abs(slope - (k + 1)) < 0.1                                 # k 次まで正しければ、誤差は t^{k+1}
        ax.loglog(ts, e, "o-", color=col, label=f"{labels[k]}（傾き {slope:.2f}）")
    ax.set_xlabel("$t$（$X=tX_0,\\ Y=tY_0$）")
    ax.set_ylabel("$\\|\\log(e^Xe^Y)-$ 打ち切り$\\|$")
    ax.set_title("BCH の公式：項を1つ足すごとに、誤差の次数が1つ上がる", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "mexp03_bch_orders.png", dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mexp04
def mexp04():
    """H = σx + σz、t = 1 の時間発展のトロッター分解・ストラング分解の誤差と、本文の上限。"""
    t = 1.0
    A, B = -1j * t * SX, -1j * t * SZ                                    # e^{−iHt} = e^{A + B}
    U = expm(A + B)
    ns = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256])
    lie, strang = [], []
    for n in ns:
        lie.append(np.linalg.norm(np.linalg.matrix_power(expm(A / n) @ expm(B / n), n) - U, 2))
        S = expm(A / (2 * n)) @ expm(B / n) @ expm(A / (2 * n))
        strang.append(np.linalg.norm(np.linalg.matrix_power(S, n) - U, 2))
    lie, strang = np.array(lie), np.array(strang)
    bound_lie = np.linalg.norm(comm(A, B), 2) / (2 * ns)                  # 式 (VI-4)
    E3 = -comm(A, comm(A, B)) / 24 + comm(B, comm(B, A)) / 12
    bound_strang = np.linalg.norm(E3, 2) / ns**2                          # 式 (VI-7)
    assert np.all(lie[3:] <= bound_lie[3:] * 1.02)
    assert np.all(strang[3:] <= bound_strang[3:] * 1.02)
    s1 = np.polyfit(np.log(ns[3:]), np.log(lie[3:]), 1)[0]
    s2 = np.polyfit(np.log(ns[3:]), np.log(strang[3:]), 1)[0]
    assert abs(s1 + 1) < 0.05 and abs(s2 + 2) < 0.05
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.loglog(ns, lie, "o-", color=C_A, label=f"トロッター（傾き {s1:.2f}）")
    ax.loglog(ns, bound_lie, "--", color=C_A, alpha=0.6, label="上限 $\\|[A,B]\\|/2n$")
    ax.loglog(ns, strang, "s-", color=C_B, label=f"ストラング（傾き {s2:.2f}）")
    ax.loglog(ns, bound_strang, "--", color=C_B, alpha=0.6, label="上限の目安 $\\|E_3\\|/n^2$")
    ax.set_xlabel("分割数 $n$")
    ax.set_ylabel("$\\|$近似$-e^{-iHt}\\|$")
    ax.set_title("$H=\\sigma_x+\\sigma_z,\\ t=1$ の時間発展", fontsize=11)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "mexp04_trotter_strang.png", dpi=150)
    plt.close(fig)


FIGS = {"mexp01": mexp01, "mexp02": mexp02, "mexp03": mexp03, "mexp04": mexp04}

if __name__ == "__main__":
    for name in sys.argv[1:] or FIGS:
        FIGS[name]()
        print("保存:", name)
