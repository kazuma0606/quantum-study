"""measurement_projection_born_rule.md（射影演算子による測定確率の計算）用の図を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/08_量子コンピュータ/figures/make_measurement_projection_figures.py          # すべて
    uv run python 研究ノート/08_量子コンピュータ/figures/make_measurement_projection_figures.py mp01    # 1つだけ

出力（このスクリプトと同じ figures/ ディレクトリ）:
    mp01_flow.png               Part I   回路の流れ：U_f → M_x* = P ⊗ I → ノルムの2乗
    mp02_block_matrix.png       Part VIII  P_11 ⊗ I_2 の行列（8×8、右下の 2×2 ブロックだけが I_2）
    mp03_amplitudes.png         Part VIII  |Ψ⟩ の8成分、M_11|Ψ⟩、入力ごとの確率
    mp04_post_measurement.png   付録A  測定後の状態（入力を測る・結果を測る）と、誤差のある測定（POVM）
    mp05_coefficient_matrices.png  付録B  係数行列 c_{x,y} の階数と、エンタングルメント
    mp06_qiskit_order.png       付録C  教科書と Qiskit のラベルの並び順、CNOT の行列
    mp07_reduced_states.png     partial_trace ノート Part IV  縮約密度行列 ρ_A = CC†（3つの関数）
    mp08_interference_visibility.png  partial_trace ノート Part V  環境の重なりと干渉の見えやすさ

各図は、描く値が本文の式と一致することを assert で確認してから保存する。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "measurement_projection"))
import measurement_projection as mp  # noqa: E402

OUT = Path(__file__).resolve().parent

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"

F_EX = lambda x: 1 if x == 3 else 0
KETS3 = ["000", "001", "010", "011", "100", "101", "110", "111"]


def ketlabel(s):
    return r"$|" + s + r"\rangle$"


# ------------------------------------------------------------------------------------- mp01
def mp01():
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ys = {"in": 3.0, "out": 1.2}
    # 配線
    for key, y in ys.items():
        ax.plot([0.6, 10.4], [y, y], color=C_GRAY, lw=1.2, zorder=1)
    ax.text(0.5, ys["in"], "入力レジスタ\n" + r"$\frac{1}{\sqrt{N}}\sum_i|x_i\rangle$", ha="right", va="center", fontsize=10)
    ax.text(0.5, ys["out"], "結果レジスタ\n" + r"$|0\cdots0\rangle$", ha="right", va="center", fontsize=10)

    def box(x0, x1, y0, y1, text, color, fs=11):
        ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.05", fc=color, ec="k", lw=1.2, alpha=0.85, zorder=3))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center", fontsize=fs, zorder=4)

    box(1.5, 3.1, 0.7, 3.5, r"$U_f$", "#cfe2f3")
    ax.text(3.8, 3.75, r"$|\Psi\rangle=\frac{1}{\sqrt{N}}\sum_i|x_i\rangle|f(x_i)\rangle$", ha="center", fontsize=11)
    ax.plot([3.8, 3.8], [0.8, 3.5], color=C_BAD, lw=1.0, ls="--")
    box(4.6, 6.2, 2.7, 3.3, r"$P_{x^*}=|x^*\rangle\langle x^*|$", "#fde9c8", fs=10)
    box(4.6, 6.2, 0.9, 1.5, r"$I$", "#e6e6e6")
    ax.text(5.4, 0.35, r"$M_{x^*}=P_{x^*}\otimes I$", ha="center", fontsize=11)
    ax.add_patch(Rectangle((4.45, 0.7), 1.9, 2.8, fill=False, ec=C_B, lw=1.5, ls="--", zorder=2))
    ax.text(7.5, 3.75, r"$M_{x^*}|\Psi\rangle=\frac{1}{\sqrt{N}}|x^*\rangle|f(x^*)\rangle$", ha="center", fontsize=11)
    ax.plot([7.5, 7.5], [0.8, 3.5], color=C_BAD, lw=1.0, ls="--")
    box(8.5, 10.2, 1.4, 3.0, r"$\|\cdot\|^2$" + "\n" + r"$=P(x^*)=\frac{1}{N}$", "#d9ead3", fs=11)
    ax.text(5.4, 4.05, "Part III", ha="center", fontsize=9, color=C_GRAY)
    ax.text(2.3, 4.05, "Part I", ha="center", fontsize=9, color=C_GRAY)
    ax.text(9.35, 3.35, "Part IV〜VI", ha="center", fontsize=9, color=C_GRAY)
    # 値の確認（本文の式）
    psi = mp.psi_state(F_EX, 2, 1)
    assert np.isclose(mp.prob_input(psi, 3, 4, 2), 1 / 4)
    assert np.allclose(mp.M_op(3, 4, 2) @ psi, 0.5 * mp.ket(7, 8))
    fig.savefig(OUT / "mp01_flow.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp02
def mp02():
    P = mp.proj(3, 4).real
    I = np.eye(2)
    M = mp.M_op(3, 4, 2).real
    assert np.allclose(M, np.kron(P, I)) and np.allclose(np.diag(M), [0] * 6 + [1, 1])  # Part VIII §3
    fig = plt.figure(figsize=(12, 4.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[4, 2, 8], wspace=0.55)

    def show(ax, A, rowl, coll, title, block=None):
        ax.imshow(A, cmap="Blues", vmin=0, vmax=1.2)
        n = A.shape[0]
        for i in range(n):
            for j in range(n):
                if A[i, j] != 0:
                    ax.text(j, i, f"{A[i, j]:.0f}", ha="center", va="center", fontsize=11, color="w")
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(coll, fontsize=8, rotation=90)
        ax.set_yticklabels(rowl, fontsize=8)
        ax.set_title(title, fontsize=11)
        ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
        ax.grid(which="minor", color="#cccccc", lw=0.6)
        ax.tick_params(which="minor", length=0)
        if block:
            for k in range(0, n + 1, block):
                ax.axhline(k - 0.5, color=C_B, lw=1.4)
                ax.axvline(k - 0.5, color=C_B, lw=1.4)

    k2 = [r"$|" + s + r"\rangle$" for s in ["00", "01", "10", "11"]]
    k1 = [r"$|0\rangle$", r"$|1\rangle$"]
    k3 = [r"$|" + s + r"\rangle$" for s in KETS3]
    show(fig.add_subplot(gs[0]), P, k2, k2, r"$P_{11}=|11\rangle\langle11|$")
    show(fig.add_subplot(gs[1]), I, k1, k1, r"$I_2$")
    ax = fig.add_subplot(gs[2])
    show(ax, M, k3, k3, r"$M_{11}=P_{11}\otimes I_2$  （$P_{11}$ の各成分に $I_2$ を掛けて並べた $8\times8$）", block=2)
    ax.add_patch(Rectangle((5.5, 5.5), 2, 2, fill=False, ec=C_BAD, lw=2.5))
    ax.text(-0.2, 1.0, r"橙の線：$2\times2$ のブロックの境目" + "\n" + r"（$P_{11}$ の1成分が1ブロック）", ha="left", fontsize=9, color=C_B)
    ax.text(-0.2, 3.2, r"右下の $2\times2$（赤）だけ $1\cdot I_2$" + "\n" + r"（入力が $11$ の2つの基底）", ha="left", fontsize=9, color=C_BAD)
    fig.text(0.31, 0.5, r"$\otimes$", fontsize=28, ha="center", va="center")
    fig.savefig(OUT / "mp02_block_matrix.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp03
def mp03():
    psi = mp.psi_state(F_EX, 2, 1).real
    post = (mp.M_op(3, 4, 2) @ psi.astype(complex)).real
    probs = [mp.prob_input(psi.astype(complex), x, 4, 2) for x in range(4)]
    assert np.allclose(psi, 0.5 * np.array([1, 0, 1, 0, 1, 0, 0, 1])) and np.allclose(post, 0.5 * mp.ket(7, 8).real)  # Part VIII §2, §4
    assert np.allclose(probs, 0.25) and np.isclose(sum(probs), 1)  # Part VIII §6
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.8), gridspec_kw={"width_ratios": [4, 4, 2.6]})
    xs = np.arange(8)
    cols = [C_B if k in (6, 7) else C_A for k in range(8)]
    axs[0].bar(xs, psi, color=cols)
    axs[0].set_title(r"$|\Psi\rangle$ の成分（橙：入力が $11$）", fontsize=11)
    axs[1].bar(xs, post, color=cols)
    axs[1].set_title(r"$M_{11}|\Psi\rangle=\frac{1}{2}|111\rangle$", fontsize=11)
    for ax in axs[:2]:
        ax.set_xticks(xs)
        ax.set_xticklabels([ketlabel(s) for s in KETS3], rotation=90, fontsize=8)
        ax.set_ylim(0, 0.62)
        ax.axhline(0.5, color=C_GRAY, lw=0.8, ls=":")
        ax.set_ylabel("振幅", fontsize=9)
    axs[2].bar(range(4), probs, color=C_C)
    axs[2].set_xticks(range(4))
    axs[2].set_xticklabels([ketlabel(s) for s in ["00", "01", "10", "11"]], fontsize=9)
    axs[2].set_ylim(0, 0.4)
    axs[2].set_title(r"入力 $x$ の確率 $P(x)$", fontsize=11)
    axs[2].axhline(0.25, color=C_BAD, lw=1.0, ls="--")
    axs[2].text(3.4, 0.262, r"$\frac{1}{N}=\frac{1}{4}$", fontsize=10, color=C_BAD, ha="right")
    fig.tight_layout()
    fig.savefig(OUT / "mp03_amplitudes.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp04
def mp04():
    rng = np.random.default_rng(5)
    p_in = np.array([0.1, 0.2, 0.3, 0.4])
    alpha = np.sqrt(p_in) * np.exp(1j * rng.uniform(0, 2 * np.pi, 4))
    psi = mp.psi_state(F_EX, 2, 1, alpha)
    post_in, p10 = mp.post_measurement_state(psi, 2, 4, 2)  # 入力 10 を測る
    post_out, py0 = mp.result_register_collapse(psi, 0, 4, 2)  # 結果 0 を測る
    assert np.isclose(p10, 0.3) and np.isclose(py0, 0.6)  # 付録A-3、付録B-2 の確率
    assert np.allclose(np.abs(post_in), mp.ket(4, 8).real)  # |10⟩|0⟩（添字 4。位相 α_x は残る）
    eps_list = [0.0, 0.1, 0.3]
    th = np.linspace(0, np.pi, 200)

    fig, axs = plt.subplots(2, 2, figsize=(11.5, 7))
    xs = np.arange(8)
    xl = [ketlabel(s) for s in KETS3]

    def bars(ax, v, title, hi=None):
        cols = [C_BAD if (hi is not None and k in hi) else C_A for k in range(8)]
        ax.bar(xs, np.abs(v) ** 2, color=cols)
        ax.set_xticks(xs)
        ax.set_xticklabels(xl, rotation=90, fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_title(title, fontsize=10.5)
        ax.set_ylabel(r"$|c|^2$", fontsize=9)

    bars(axs[0, 0], psi, r"測定前：$\sum_i\alpha_i|x_i\rangle|f(x_i)\rangle$（$|\alpha_i|^2=0.1,0.2,0.3,0.4$）")
    bars(axs[0, 1], post_in, r"入力を測って $10$：$M_{10}|\Psi\rangle/\sqrt{P(10)}=|10\rangle|0\rangle$（$P=0.3$）", hi=[4])
    bars(axs[1, 0], post_out, r"結果を測って $0$：$|00\rangle,|01\rangle,|10\rangle$ の重ね合わせ（$P=0.6$）", hi=[0, 2, 4])
    ax = axs[1, 1]
    for eps, c in zip(eps_list, [C_A, C_B, C_C]):
        K0, K1 = mp.unsharp_measurement_kraus(eps)
        p0 = np.array([np.linalg.norm(K0 @ np.array([np.cos(t / 2), np.sin(t / 2)])) ** 2 for t in th])
        assert np.allclose(p0, (1 - eps) * np.cos(th / 2) ** 2 + eps * np.sin(th / 2) ** 2)  # 付録A-5 の式
        ax.plot(th, p0, color=c, lw=2, label=rf"$\epsilon={eps}$" + ("（射影測定）" if eps == 0 else ""))
    ax.set_xlabel(r"$\theta$（状態 $\cos\frac{\theta}{2}|0\rangle+\sin\frac{\theta}{2}|1\rangle$）", fontsize=9)
    ax.set_ylabel(r"結果 $0$ の確率", fontsize=9)
    ax.set_xticks([0, np.pi / 2, np.pi])
    ax.set_xticklabels(["0", r"$\pi/2$", r"$\pi$"])
    ax.set_title(r"誤差 $\epsilon$ のある $Z$ 測定（POVM）：確率が $1,0$ に届かない", fontsize=10.5)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "mp04_post_measurement.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp05
def mp05():
    cases = [("定数関数  $f(x)=0$", lambda x: 0, 1, 4, 2), ("例（Part VIII） $f(x)=1\\Leftrightarrow x=11$", F_EX, 1, 4, 2), ("1対1  $f(x)=x$", lambda x: x, 2, 4, 4)]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, (title, f, n_out, N, M) in zip(axs, cases):
        M = 2**n_out
        psi = mp.psi_state(f, 2, n_out)
        C = mp.coefficient_matrix(psi, N, M).real
        s2 = mp.schmidt_probabilities(psi, N, M)
        rank = int(np.linalg.matrix_rank(C))
        ent = abs(mp.entropy_bits(s2))
        ax.imshow(C, cmap="Blues", vmin=0, vmax=0.55)
        for i in range(N):
            for j in range(M):
                if C[i, j] != 0:
                    ax.text(j, i, f"{C[i, j]:.2f}", ha="center", va="center", color="w", fontsize=10)
        ax.set_yticks(range(N))
        ax.set_yticklabels([ketlabel(s) for s in ["00", "01", "10", "11"]])
        ax.set_xticks(range(M))
        ax.set_xticklabels([ketlabel(format(j, f"0{n_out}b")) for j in range(M)])
        ax.set_xlabel("結果 $y$", fontsize=9)
        ax.set_ylabel("入力 $x$", fontsize=9)
        ax.set_title(title + "\n" + rf"階数 {rank}、エントロピー {ent:.3f} bit", fontsize=10.5)
        ax.set_xticks(np.arange(-0.5, M, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, N, 1), minor=True)
        ax.grid(which="minor", color="#cccccc", lw=0.6)
        ax.tick_params(which="minor", length=0)
    # 付録B-3 の値
    assert [int(np.linalg.matrix_rank(mp.coefficient_matrix(mp.psi_state(f, 2, k), 4, 2**k))) for _, f, k, _, _ in cases] == [1, 2, 4]
    s_ex = mp.schmidt_probabilities(mp.psi_state(F_EX, 2, 1), 4, 2)
    assert np.allclose(sorted(s_ex), [0.25, 0.75]) and np.isclose(mp.entropy_bits(s_ex), 0.8113, atol=1e-4)
    fig.suptitle(r"係数行列 $C=(c_{x,y})$：階数 $1$ ⇔ 積状態（エンタングルメントの量はエントロピーで測る）", fontsize=11.5, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "mp05_coefficient_matrices.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp06
def mp06():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    cx10, cx01 = QuantumCircuit(2), QuantumCircuit(2)
    cx10.cx(1, 0)
    cx01.cx(0, 1)
    A10, A01 = np.round(Operator(cx10).data.real), np.round(Operator(cx01).data.real)
    assert np.allclose(A10, mp.CNOT.real) and not np.allclose(A01, mp.CNOT.real)  # 付録C-1

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_axes([0.02, 0.5, 0.96, 0.46])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.text(0.2, 3.6, "教科書", fontsize=12, va="center", fontweight="bold")
    ax.text(0.2, 1.2, "Qiskit", fontsize=12, va="center", fontweight="bold")
    xs = [3.0, 5.0, 7.0]
    for x, t in zip(xs, ["第1（入力）", "第2（入力）", "第3（結果）"]):
        ax.add_patch(Rectangle((x - 0.8, 3.2), 1.6, 0.8, fc="#cfe2f3", ec="k"))
        ax.text(x, 3.6, t, ha="center", va="center", fontsize=10)
    ax.text(9.6, 3.6, r"ラベル $|x_1x_2y\rangle$：左が第1", fontsize=10, va="center")
    for x, t in zip(xs, [r"$q_2$", r"$q_1$", r"$q_0$"]):
        ax.add_patch(Rectangle((x - 0.8, 0.8), 1.6, 0.8, fc="#fde9c8", ec="k"))
        ax.text(x, 1.2, t, ha="center", va="center", fontsize=12)
    ax.text(9.6, 1.2, r"ラベル $|q_2q_1q_0\rangle$：右端が $q_0$", fontsize=10, va="center")
    for x in xs:
        ax.annotate("", xy=(x, 1.65), xytext=(x, 3.15), arrowprops=dict(arrowstyle="<->", color=C_BAD, lw=1.6))
    ax.text(9.6, 2.4, "教科書の「第 $k$」は、Qiskit では\n番号の大きい方から順に対応させる", ha="left", va="center", fontsize=10.5, color=C_BAD)
    ax.text(3.0, 0.3, "添字 $=4q_2+2q_1+q_0$", fontsize=10)

    for k, (A, title) in enumerate([(A10, r"教科書の CNOT（制御が左＝第1）" + "\n" + r"= Qiskit の cx(1, 0)"), (A01, "Qiskit の cx(0, 1)（別の行列）")]):
        a = fig.add_axes([0.14 + 0.45 * k, 0.04, 0.30, 0.38])
        a.imshow(A, cmap="Blues", vmin=0, vmax=1.2)
        for i in range(4):
            for j in range(4):
                if A[i, j] != 0:
                    a.text(j, i, f"{A[i, j]:.0f}", ha="center", va="center", color="w", fontsize=11)
        lab = [ketlabel(s) for s in ["00", "01", "10", "11"]]
        a.set_xticks(range(4))
        a.set_yticks(range(4))
        a.set_xticklabels(lab, fontsize=9)
        a.set_yticklabels(lab, fontsize=9)
        a.set_title(title, fontsize=10.5)
    fig.savefig(OUT / "mp06_qiskit_order.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp07
def mp07():
    cases = [("定数関数 $f(x)=0$", lambda x: 0, 1), (r"例  $f(x)=1\Leftrightarrow x=11$", F_EX, 1), ("1対1  $f(x)=x$", lambda x: x, 2)]
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.4))
    labels = [ketlabel(s) for s in ["00", "01", "10", "11"]]
    for ax, (title, f, n_out) in zip(axs, cases):
        M = 2**n_out
        psi = mp.psi_state(f, 2, n_out)
        rho = mp.partial_trace(mp.density(psi), 4, M, "A")
        C = mp.coefficient_matrix(psi, 4, M)
        assert np.allclose(rho, C @ C.conj().T)  # 部分トレース = C C†（付録・Part III）
        ev = np.sort(np.linalg.eigvalsh(rho))[::-1]
        ax.imshow(rho.real, cmap="Blues", vmin=0, vmax=1.0)
        for i in range(4):
            for j in range(4):
                if abs(rho[i, j]) > 1e-12:
                    ax.text(j, i, f"{rho[i, j].real:.2f}", ha="center", va="center", color="w" if rho[i, j].real > 0.45 else "k", fontsize=10)
        ax.set_xticks(range(4))
        ax.set_yticks(range(4))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_yticklabels(labels, fontsize=9)
        ev_txt = ", ".join(f"{e:.2f}" for e in ev if e > 1e-12)
        ax.set_title(title + "\n" + rf"$\rho_A$ の固有値：{ev_txt}", fontsize=10.5)
        ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
        ax.grid(which="minor", color="#cccccc", lw=0.6)
        ax.tick_params(which="minor", length=0)
    # Part IV の値
    psi = mp.psi_state(F_EX, 2, 1)
    rho = mp.partial_trace(mp.density(psi), 4, 2, "A")
    assert np.allclose(rho, 0.25 * np.array([[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 0], [0, 0, 0, 1]]))
    assert np.allclose(np.sort(np.linalg.eigvalsh(rho))[::-1][:2], [0.75, 0.25])
    fig.suptitle(r"入力レジスタの縮約密度行列 $\rho_A=\mathrm{Tr}_B|\Psi\rangle\langle\Psi|=CC^\dagger$（結果レジスタをトレースアウト）", fontsize=11.5, y=1.03)
    fig.tight_layout()
    fig.savefig(OUT / "mp07_reduced_states.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


# ------------------------------------------------------------------------------------- mp08
def mp08():
    th = np.linspace(0, np.pi, 181)
    coh, p0, ent = [], [], []
    for t_ in th:
        phi = mp.two_qubit_state(t_)
        rho = mp.partial_trace(mp.density(phi), 2, 2, "A")
        coh.append(2 * abs(rho[0, 1]))
        H = mp.hadamard_all(1)
        p0.append((H @ rho @ H.conj().T)[0, 0].real)
        ent.append(mp.entropy_bits(np.linalg.eigvalsh(rho)))
    coh, p0, ent = map(np.array, (coh, p0, ent))
    assert np.allclose(coh, np.abs(np.cos(th))) and np.allclose(p0, (1 + np.cos(th)) / 2)  # Part V の式
    assert np.isclose(ent[90], 1.0) and np.isclose(ent[0], 0.0, atol=1e-9)  # θ=π/2 でベル状態（1 bit）、θ=0 で積状態

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [4.2, 3]})
    ax = axs[0]
    ax.plot(th, p0, color=C_A, lw=2.2, label=r"$H$ をかけて $0$ が出る確率 $\frac{1+\cos\theta}{2}$")
    ax.plot(th, coh, color=C_B, lw=2.2, label=r"コヒーレンス $2|\rho_{01}|=|\cos\theta|$")
    ax.plot(th, ent, color=C_BAD, lw=2.2, ls="--", label=r"エンタングルメントエントロピー（bit）")
    ax.set_xticks([0, np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi])
    ax.set_xticklabels(["0", r"$\pi/4$", r"$\pi/2$", r"$3\pi/4$", r"$\pi$"])
    ax.set_xlabel(r"結果レジスタの2つの状態の角度 $\theta$（重なり $\langle e_0|e_1\rangle=\cos\theta$）", fontsize=10)
    ax.set_title(r"$|\Phi_\theta\rangle=\frac{1}{\sqrt{2}}\left(|0\rangle|e_0\rangle+|1\rangle|e_1\rangle\right)$：結果レジスタが入力を「覚える」ほど、干渉が消える", fontsize=10.5)
    ax.annotate("積状態（干渉は完全）", xy=(0, 1.0), xytext=(0.05, 1.08), fontsize=9)
    ax.annotate("ベル状態（干渉なし）", xy=(np.pi / 2, 1.0), xytext=(np.pi / 2 - 0.55, 1.08), fontsize=9)
    ax.set_ylim(-0.02, 1.15)
    ax.legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    ax2 = axs[1]
    probs = []
    for f, n_out in [(lambda x: 0, 1), (F_EX, 1), (lambda x: x, 2)]:
        psi = mp.psi_state(f, 2, n_out)
        rho = mp.partial_trace(mp.density(psi), 4, 2**n_out, "A")
        probs.append(mp.prob_all_zero_after_hadamard(rho, 2))
    assert np.allclose(probs, [1.0, 5 / 8, 0.25])  # Part V の値
    ax2.bar(range(3), probs, color=[C_C, C_B, C_A])
    ax2.axhline(0.25, color=C_GRAY, lw=1.0, ls=":")
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(["定数\n(積状態)", "例\n(エンタングル)", "1対1\n(最大)"], fontsize=9)
    for i, v in enumerate(probs):
        ax2.text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=10)
    ax2.set_ylim(0, 1.15)
    ax2.set_title(r"入力に $H^{\otimes2}$ をかけて $00$ が出る確率" + "\n" + r"（$\frac{1}{N}\sum_{x,x'}\rho_{xx'}$）", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(OUT / "mp08_interference_visibility.png", dpi=150, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)


FIGS = dict(mp01=mp01, mp02=mp02, mp03=mp03, mp04=mp04, mp05=mp05, mp06=mp06, mp07=mp07, mp08=mp08)

if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        FIGS[n]()
        print("saved", n)
