"""NB-03（notebooks/03_angular_momentum）の2冊のノートブックを生成する。"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path("notebooks/03_angular_momentum")
OUT.mkdir(parents=True, exist_ok=True)
NOTE = "../../研究ノート/05_量子力学/angular_momentum_ladder_operators.md"
PAULI = "../../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md"


def save(name, cells):
    for i, cell in enumerate(cells):
        cell.id = f"{Path(name).stem[:2]}-{i:02d}"   # 作り直しても差分が出ないよう、セルの ID を固定する
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nbformat.write(nb, OUT / name)
    print("書き出し:", OUT / name)


def md(text):
    return new_markdown_cell(text.replace("NOTE", NOTE).replace("PAULI", PAULI))


code = new_code_cell

SETUP = r'''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from fractions import Fraction
from numpy.typing import NDArray
from plotly.subplots import make_subplots
from scipy.linalg import expm

np.set_printoptions(precision=4, suppress=True)

# 型の別名（型ヒントを読みやすくするため。実行時には何も確かめない）
Matrix = NDArray[np.complex128]   # (2j+1)×(2j+1) の複素行列
Floats = NDArray[np.float64]      # 実数の配列

# 単位：ħ = 1 とする（ノートの式で ħ を 1 に置き換えたもの）
# 注意：FigureWidget（スライダーで描き直す図）には、numpy 配列ではなく Python のリストを渡す
# （numpy 配列だと、スライダーを動かしたときに plotly が ValueError を出すことがある。NB-02 を参照）


def m_values(j: float) -> Floats:
    """m = j, j−1, …, −j（上から順。2j+1 個）"""
    return np.arange(j, -j - 1e-9, -1.0)


def spin_matrices(j: float) -> dict[str, Matrix]:
    """ノートの Part VI の公式から、角運動量 j の行列を作る（基底 |j,m⟩ を m の大きい順に並べる）"""
    ms = m_values(j)
    d = len(ms)
    Jz = np.diag(ms).astype(complex)
    Jp = np.zeros((d, d), dtype=complex)
    for k in range(1, d):                                   # J+|j,m⟩ = √(j(j+1) − m(m+1)) |j,m+1⟩
        m = ms[k]
        Jp[k - 1, k] = np.sqrt(j * (j + 1) - m * (m + 1))
    Jm = Jp.conj().T                                        # J− = J+†（ノートの Part II）
    Jx = (Jp + Jm) / 2                                      # J± = Jx ± iJy を解いたもの
    Jy = (Jp - Jm) / 2j
    return {"x": Jx, "y": Jy, "z": Jz, "+": Jp, "-": Jm}


def comm(A: Matrix, B: Matrix) -> Matrix:
    """交換子 [A, B] = AB − BA"""
    return A @ B - B @ A


def frac(x: float) -> str:
    """0.5 → 1/2 のように、半整数を分数で表す（表示用）"""
    return str(Fraction(x).limit_denominator(2))'''

# ============================================================================================ 01
nb1 = [
md(r"""# NB-03-1 ラダー演算子：一般の $j$ の行列を作り、梯子を見る

[角運動量のラダー演算子のノート](NOTE)では、交換関係 $[J_x,J_y]=i\hbar J_z$ だけから、

$$
J_\pm|j,m\rangle=\hbar\sqrt{j(j+1)-m(m\pm1)}\ |j,m\pm1\rangle
$$

を導きました（Part VI）。このノートブックでは、この公式から**任意の $j$ の行列** $J_x,J_y,J_z,J_\pm$ を作り、ノートの各 Part の式を行列計算で確かめます。$j=\frac12$ では[パウリ行列のノート](PAULI)の Part III の $\vec S=\frac\hbar2\vec\sigma$ に戻ります。最後に、「$j$ が整数か半整数でなければならない」理由（ノートの Part VIII で結果だけ述べたもの）を、梯子の係数から確かめます。

**単位**：$\hbar=1$ とします。

**使い方**：上から順に実行します。各セルの `assert` が、ノートの式と計算結果の一致を確かめます。"""),

code(SETUP),

md(r"""## 1. $j=\frac12$ と $j=1$ の行列

基底を $|j,j\rangle,|j,j-1\rangle,\dots,|j,-j\rangle$ の順に並べると、$J_z$ は対角行列 $\operatorname{diag}(j,j-1,\dots,-j)$、$J_+$ は対角線の1つ上だけに係数が並ぶ行列になります。$j=\frac12$ では、$J_+$ の係数は $1$（ノートの Part VII §1）で、$\vec J=\frac12\vec\sigma$ です。"""),

code(r'''sx = np.array([[0, 1], [1, 0]], dtype=complex)
sy = np.array([[0, -1j], [1j, 0]])
sz = np.array([[1, 0], [0, -1]], dtype=complex)

half = spin_matrices(0.5)
assert np.allclose(half["x"], sx / 2) and np.allclose(half["y"], sy / 2) and np.allclose(half["z"], sz / 2)
assert np.allclose(half["+"], [[0, 1], [0, 0]]) and np.allclose(half["-"], [[0, 0], [1, 0]])   # S+|↓⟩ = |↑⟩ など
print("j = 1/2：J+ =\n", half["+"].real, "\n→ S = σ/2（パウリ行列のノートの Part III と一致）\n")

one = spin_matrices(1)
for name in ("z", "+", "x", "y"):
    print(f"j = 1：J{name} =\n{one[name]}\n")'''),

md(r"""## 2. ノートの式を、$j=0,\frac12,1,\dots,5$ で確かめる

| 確かめる式 | ノートの場所 |
|---|---|
| $[J_x,J_y]=iJ_z$ とその巡回 | Part I |
| $J^2=J_x^2+J_y^2+J_z^2=j(j+1)\,I$ | Part I |
| $J_-=J_+^\dagger$、$J_x,J_y,J_z$ はエルミート | Part II |
| $[J_z,J_\pm]=\pm J_\pm$ | Part III |
| $J_+J_-=J^2-J_z^2+J_z$、$J_-J_+=J^2-J_z^2-J_z$ | Part V |

あわせて、$J_x$ と $J_y$ の固有値も $J_z$ と同じ $m=j,\dots,-j$ になることを確かめます。どの軸の方向に測っても、取りうる値は同じ、ということです。"""),

code(r'''for twice_j in range(0, 11):
    j = twice_j / 2
    J = spin_matrices(j)
    I = np.eye(twice_j + 1)
    J2 = J["x"] @ J["x"] + J["y"] @ J["y"] + J["z"] @ J["z"]
    assert np.allclose(comm(J["x"], J["y"]), 1j * J["z"])                       # Part I
    assert np.allclose(comm(J["y"], J["z"]), 1j * J["x"])
    assert np.allclose(comm(J["z"], J["x"]), 1j * J["y"])
    assert np.allclose(J2, j * (j + 1) * I)                                    # Part I
    assert np.allclose(J["-"], J["+"].conj().T)                                # Part II
    assert all(np.allclose(J[a], J[a].conj().T) for a in "xyz")
    assert np.allclose(comm(J["z"], J["+"]), J["+"])                           # Part III
    assert np.allclose(comm(J["z"], J["-"]), -J["-"])
    assert np.allclose(J["+"] @ J["-"], J2 - J["z"] @ J["z"] + J["z"])         # Part V
    assert np.allclose(J["-"] @ J["+"], J2 - J["z"] @ J["z"] - J["z"])
    for a in "xy":
        assert np.allclose(np.sort(np.linalg.eigvalsh(J[a])), np.sort(m_values(j)))
    print(f"j = {frac(j):>3}：{twice_j + 1:2d}×{twice_j + 1:<2d} の行列で、すべての式を確認")'''),

md(r"""## 3. 梯子を見る（スライダーで $j$ を変える）

左の図は、$J_z$ の固有値 $m$ を段にした梯子です。段と段の間の数字は、$J_+$ で1段上がるときの係数 $\sqrt{j(j+1)-m(m+1)}$ です。右の図は、同じ係数を棒グラフにしたものです。

- 一番上の段（$m=j$）から上には行けません（係数 $0$。ノートの Part VII §2）。
- 係数は梯子の真ん中で一番大きく、両端で小さくなります。$m$ から $m+1$ への係数は、$m+1$ から $m$ への $J_-$ の係数と同じです。"""),

code(r'''fig = go.FigureWidget(make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58],
                                    subplot_titles=("J_z の固有値の梯子（数字は J+ の係数）", "J+ の係数 √(j(j+1) − m(m+1))")))
fig.add_trace(go.Scatter(x=[], y=[], mode="lines", line=dict(color="#1f77b4", width=4), hoverinfo="skip", name="段"), 1, 1)
fig.add_trace(go.Scatter(x=[], y=[], mode="text", textposition="middle left", textfont=dict(size=13), hoverinfo="skip", name="m"), 1, 1)
fig.add_trace(go.Scatter(x=[], y=[], mode="text", textfont=dict(size=12, color="#d62728"), hoverinfo="skip", name="係数"), 1, 1)
fig.add_trace(go.Bar(x=[], y=[], marker_color="#d62728", name="係数"), 1, 2)
fig.update_layout(height=470, width=900, showlegend=False, margin=dict(l=20, r=20, t=40, b=40),
                  xaxis=dict(visible=False, range=[-0.9, 1.5]), yaxis=dict(title="m", range=[-4.6, 4.6]),
                  xaxis2=dict(title="出発する段 m（m → m+1）"), yaxis2=dict(range=[0, 4.8]))

j_slider = W.SelectionSlider(options=[(frac(k / 2), k / 2) for k in range(0, 9)], value=1.5, description="j")
info = W.HTML()


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、梯子と棒グラフを描き直す"""
    j = j_slider.value
    ms = m_values(j)
    J = spin_matrices(j)
    coef = [float(np.sqrt(j * (j + 1) - m * (m + 1))) for m in ms[1:]]        # m = j−1, …, −j から1段上へ
    assert np.allclose(coef, np.diag(J["+"], 1).real)
    xs: list[float | None] = []
    ys: list[float | None] = []
    for m in ms:
        xs += [0.0, 1.0, None]
        ys += [float(m), float(m), None]
    with fig.batch_update():
        fig.data[0].x, fig.data[0].y = xs, ys
        fig.data[1].x, fig.data[1].y = [-0.05] * len(ms), [float(m) for m in ms]
        fig.data[1].text = [f"m = {frac(m)}" for m in ms]
        fig.data[2].x, fig.data[2].y = [1.25] * len(coef), [float(m) + 0.5 for m in ms[1:]]
        fig.data[2].text = [f"↑ {c:.3f}" for c in coef]
        fig.data[3].x, fig.data[3].y = [frac(m) for m in ms[1:]], coef
    info.value = (f"j = {frac(j)}：段の数 2j+1 = {len(ms)}、J² の固有値 j(j+1) = {j * (j + 1):.2f}、"
                  f"係数の最大 {max(coef, default=0):.3f}（梯子の真ん中）")


j_slider.observe(update, "value")
update()
W.VBox([j_slider, info, fig])'''),

md(r"""## 4. なぜ $j$ は整数か半整数なのか

ノートの Part VIII では「$j$ は $0,\frac12,1,\frac32,\dots$ だけが許される」と結果だけを述べました。これは、Part VI のノルムの式から導けます。

1. $J^2-J_z^2=J_x^2+J_y^2$ の期待値は $0$ 以上なので、$m^2\le j(j+1)$ で、$m$ には上限があります。一番上の段を $m_{\max}$ とすると $J_+|j,m_{\max}\rangle=0$ で、ノルムの式 $j(j+1)-m_{\max}(m_{\max}+1)=0$ から $m_{\max}=j$ です。
2. 一番上から $J_-$ で下りていきます。$J_-|j,m\rangle$ のノルムの2乗は
$$
\big\|J_-|j,m\rangle\big\|^2=j(j+1)-m(m-1)=(j+m)(j-m+1)
$$
です。ノルムの2乗は負になれないので、どこかで**ちょうど $0$**（$m=-j$）になって梯子が止まらなければなりません。
3. $m=j,j-1,j-2,\dots$ が $-j$ に届くのは、$2j$ が整数のときだけです。そうでなければ、$m$ が $-j$ を飛び越えた所で $(j+m)<0$ となり、ノルムの2乗が負になって矛盾します。

下のスライダーで、$j$ を $0.05$ 刻みで動かして確かめます。棒は、一番上から順に $J_-$ を掛けたときのノルムの2乗です（緑：正、灰：ちょうど $0$ で止まる、赤：負で矛盾）。"""),

code(r'''def lowering_norms(j: float, extra: int = 2) -> tuple[Floats, Floats]:
    """一番上 m = j から J− で下りるときの、‖J−|j,m⟩‖² = (j+m)(j−m+1)（m = j, j−1, … の順）"""
    steps = int(np.floor(2 * j + 1e-9)) + 1 + extra
    ms = j - np.arange(steps)
    return ms, (j + ms) * (j - ms + 1)


for j in (0.5, 1.0, 1.5, 2.0):                    # 2j が整数：m = −j でちょうど 0、それより上はすべて正
    ms, n2 = lowering_norms(j, extra=0)
    assert np.isclose(n2[-1], 0) and np.all(n2[:-1] > 0) and np.isclose(ms[-1], -j)
for j in (0.3, 0.7, 1.3, 2.25):                   # 2j が整数でない：0 を飛び越えて負になる
    ms, n2 = lowering_norms(j)
    assert not np.any(np.isclose(n2, 0)) and np.any(n2 < 0)

fig2 = go.FigureWidget([go.Bar(x=[], y=[], marker_color=[])])
fig2.add_hline(y=0, line_color="#555")
fig2.update_layout(height=400, width=820, margin=dict(l=40, r=20, t=30, b=40),
                   xaxis_title="出発する段 m（一番上 m = j から順に）", yaxis_title="‖J−|j,m⟩‖² = (j+m)(j−m+1)")
j_cont = W.FloatSlider(value=0.7, min=0.0, max=3.0, step=0.05, description="j")
info2 = W.HTML()


def update2(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、ノルムの2乗の棒を描き直す"""
    j = round(j_cont.value, 2)
    ms, n2 = lowering_norms(j)
    zero = np.isclose(n2, 0)
    stop = int(np.argmax(zero)) if zero.any() else None
    if stop is not None:                           # 梯子が止まったら、その先は描かない
        ms, n2, zero = ms[: stop + 1], n2[: stop + 1], zero[: stop + 1]
    colors = ["#999999" if z else ("#2ca02c" if v > 0 else "#d62728") for v, z in zip(n2, zero)]
    with fig2.batch_update():
        fig2.data[0].x = [f"{m:.2f}" for m in ms]
        fig2.data[0].y = [float(v) for v in n2]
        fig2.data[0].marker.color = colors
    if stop is not None:
        info2.value = f"j = {j}：2j = {2 * j:.2f} は整数 → m = {-j:.2f} でちょうど 0 になり、梯子は 2j+1 = {stop + 1} 段で止まる"
    else:
        info2.value = f"j = {j}：2j = {2 * j:.2f} は整数でない → 0 を飛び越えてノルムの2乗が負になり、矛盾（この j は許されない）"


j_cont.observe(update2, "value")
update2()
W.VBox([j_cont, info2, fig2])'''),

md(r"""## 観察のポイント

- $j=\frac12$ の行列は、パウリ行列の半分です。ノートの Part VII の4つの式（$S_+|{\downarrow}\rangle=|{\uparrow}\rangle$ など）は、$J_\pm$ の行列の成分そのものです。
- どの $j$ でも、$J^2$ は単位行列の $j(j+1)$ 倍です。$J^2$ の固有値が $j^2$ ではなく $j(j+1)$ になるのは、$J_x^2+J_y^2$ が $0$ にならない（$x,y$ 方向の値が確定しない）からです。
- 梯子が止まる条件から、$2j$ は整数でなければなりません。$j$ が許される値を「選ぶ」のは、実験ではなく、交換関係とノルムが負になれないことです（どの $j$ が実際の粒子に現れるかは、また別の話です）。

**次のノートブック**：[02_spin_rotation_and_qubits.ipynb](02_spin_rotation_and_qubits.ipynb) で、スピン $j$ の回転と、量子ビットを並べたときの合成スピンを扱います。"""),
]

# ============================================================================================ 02
nb2 = [
md(r"""# NB-03-2 スピン $j$ の回転と、量子ビットの合成スピン

[角運動量のラダー演算子のノート](NOTE)の行列（NB-03-1）を使って、

1. スピン $j$ を回転させたときの、$J_z$ の測定確率（$j=\frac12$ では NB-01 の $\cos^2\frac\theta2$）
2. $2\pi$ 回転が $(-1)^{2j}$ になること（NB-02 の二重被覆の一般化）
3. $n$ 個の量子ビット（スピン $\frac12$）を並べたときの合成スピン（Qiskit の `SparsePauliOp` で作る）

を確かめます。3 は、ノートの範囲の少し先（角運動量の合成）で、Phase 2 の複数量子ビットへの橋渡しです。

**単位**：$\hbar=1$ とします。"""),

code(SETUP),

md(r"""## 1. 回転したスピンを測る

一番上の状態 $|j,j\rangle$（$z$ 軸の向き）を、$y$ 軸のまわりに角度 $\theta$ 回して（$e^{-i\theta J_y}$）から $J_z$ を測ると、$m'$ が出る確率は

$$
P(m')=\binom{2j}{j+m'}\cos^{2(j+m')}\frac\theta2\ \sin^{2(j-m')}\frac\theta2
$$

の二項分布になります（スピン $j$ を、同じ向きのスピン $\frac12$ が $2j$ 個そろったものと見ると、それぞれが確率 $\cos^2\frac\theta2$ で上向きになる、という形です。§3 も参照）。$j=\frac12$ では $P(+\frac12)=\cos^2\frac\theta2$ で、NB-01 の測定確率と一致します。期待値は $\langle J_z\rangle=j\cos\theta$ です。"""),

code(r'''from math import comb


def rotated_probabilities(j: float, theta: float) -> Floats:
    """e^{−iθJy}|j,j⟩ で J_z を測ったときの、m' = j, …, −j の確率（行列の指数関数で計算）"""
    psi = expm(-1j * theta * spin_matrices(j)["y"])[:, 0]
    return np.abs(psi) ** 2


def binomial_formula(j: float, theta: float) -> Floats:
    n = int(round(2 * j))
    return np.array([comb(n, int(round(j + m))) * np.cos(theta / 2) ** (2 * (j + m)) * np.sin(theta / 2) ** (2 * (j - m))
                     for m in m_values(j)])


for twice_j in range(1, 11):
    j = twice_j / 2
    for theta in np.linspace(0, 2 * np.pi, 13):
        p = rotated_probabilities(j, theta)
        assert np.allclose(p, binomial_formula(j, theta))
        assert np.isclose(p @ m_values(j), j * np.cos(theta))              # ⟨J_z⟩ = j cos θ
assert np.isclose(rotated_probabilities(0.5, 1.2)[0], np.cos(0.6) ** 2)   # j = 1/2：cos²(θ/2)
print("二項分布の式と ⟨J_z⟩ = j cos θ を、j = 1/2 〜 5、13 個の角度で確認しました")

fig = go.FigureWidget([go.Bar(x=[], y=[], name="行列の指数関数で計算", marker_color="#1f77b4"),
                       go.Scatter(x=[], y=[], mode="markers", name="二項分布の式",
                                  marker=dict(symbol="line-ew", size=30, line=dict(width=3, color="black")))])
fig.update_layout(height=400, width=820, margin=dict(l=40, r=20, t=30, b=40), yaxis=dict(range=[0, 1.05]),
                  xaxis_title="測定値 m'", yaxis_title="確率 P(m')", legend=dict(x=0.65, y=0.98))
j_rot = W.SelectionSlider(options=[(frac(k / 2), k / 2) for k in range(1, 11)], value=2.0, description="j")
theta_rot = W.FloatSlider(value=60, min=0, max=360, step=5, description="θ [度]")
info = W.HTML()


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、確率の棒を描き直す"""
    j, theta = j_rot.value, np.radians(theta_rot.value)
    p = rotated_probabilities(j, theta)
    labels = [frac(m) for m in m_values(j)]
    with fig.batch_update():
        fig.data[0].x, fig.data[0].y = labels, [float(v) for v in p]
        fig.data[1].x, fig.data[1].y = labels, [float(v) for v in binomial_formula(j, theta)]
    info.value = f"⟨J_z⟩ = {float(p @ m_values(j)):+.3f}（= j cos θ = {j * np.cos(theta):+.3f}）"


for w in (j_rot, theta_rot):
    w.observe(update, "value")
update()
W.VBox([W.HBox([j_rot, theta_rot]), info, fig])'''),

md(r"""## 2. $2\pi$ 回転は $(-1)^{2j}$

$e^{-i\theta J_z}$ は対角行列 $\operatorname{diag}(e^{-i\theta m})$ なので、$\theta=2\pi$ では $e^{-2\pi im}=(-1)^{2m}=(-1)^{2j}$（$m$ と $j$ は整数だけ違う）が並び、

$$
e^{-2\pi iJ_z}=(-1)^{2j}\,I
$$

です。半整数の $j$ では $-I$（NB-02 の二重被覆。$j=\frac12$ がその例）、整数の $j$ では $I$ です。下の図は、回転のトレースを次元で割ったもの $\chi_j(\theta)/(2j+1)$ で、$\chi_j(\theta)=\operatorname{tr}e^{-i\theta J_z}=\dfrac{\sin\frac{(2j+1)\theta}2}{\sin\frac\theta2}$ です。整数の $j$ は周期 $2\pi$、半整数の $j$ は周期 $4\pi$ です。"""),

code(r'''for twice_j in range(0, 11):
    j = twice_j / 2
    Jz = spin_matrices(j)["z"]
    assert np.allclose(expm(-2j * np.pi * Jz), (-1) ** twice_j * np.eye(twice_j + 1))
    for t in (0.7, 2.3, 5.1, 9.0):
        assert np.isclose(np.trace(expm(-1j * t * Jz)).real, np.sin((2 * j + 1) * t / 2) / np.sin(t / 2))
print("2π 回転 = (−1)^{2j} I と、トレースの式を確認しました")

thetas = np.linspace(1e-3, 4 * np.pi, 600)
fig_c = go.Figure()
for j, color, dash in [(0.5, "#d62728", "solid"), (1.5, "#e67e00", "dot"), (1.0, "#1f77b4", "solid"), (2.0, "#2ca02c", "dot")]:
    chi = np.sin((2 * j + 1) * thetas / 2) / np.sin(thetas / 2) / (2 * j + 1)
    fig_c.add_trace(go.Scatter(x=(thetas / np.pi).tolist(), y=chi.tolist(), mode="lines", name=f"j = {frac(j)}",
                               line=dict(color=color, dash=dash)))
fig_c.add_vline(x=2, line_dash="dash", line_color="#888", annotation_text="θ = 2π")
fig_c.update_layout(height=380, width=820, margin=dict(l=40, r=20, t=30, b=40),
                    xaxis_title="θ / π", yaxis_title="χ_j(θ) / (2j+1)")
fig_c'''),

md(r"""## 3. 量子ビットを並べると、大きなスピンになる（Qiskit）

$n$ 個の量子ビットの全スピンを

$$
S_a=\frac12\sum_{k=1}^{n}\sigma_a^{(k)}\qquad(a=x,y,z)
$$

とします（$\sigma_a^{(k)}$ は $k$ 番目の量子ビットだけに作用するパウリ行列。Qiskit の `SparsePauliOp` で作ります）。$S_a$ も角運動量の交換関係を満たすので、$S^2$ の固有値は $j(j+1)$ の形で、$j$ は $\frac n2,\frac n2-1,\dots$ です。それぞれの $j$ が現れる回数は $\binom{n}{n/2-j}-\binom{n}{n/2-j-1}$ です（2個なら $j=1$ が1組と $j=0$ が1組）。

さらに、全員が上向き $|00\cdots0\rangle$（$|0\rangle$ は $\sigma_z=+1$）から $S_-$ で下りていくと、$j=\frac n2$ の梯子ができます。その梯子の上で $S_a$ の行列を作ると、NB-03-1 の `spin_matrices(n/2)` と一致します。これが、§1 で「スピン $j$ は、スピン $\frac12$ が $2j$ 個そろったもの」と言った意味です。"""),

code(r'''from collections import Counter

from qiskit.quantum_info import SparsePauliOp, Statevector


def total_spin(n: int) -> dict[str, Matrix]:
    """n 量子ビットの全スピン S_a = ½ Σ_k σ_a^(k) を、SparsePauliOp で作って行列にする"""
    S = {a: SparsePauliOp.from_sparse_list([(a.upper(), [k], 0.5) for k in range(n)], num_qubits=n) for a in "xyz"}
    return {a: op.to_matrix() for a, op in S.items()}


def copies(n: int, j: float) -> int:
    """n 個のスピン ½ の中に、合成スピン j が現れる回数"""
    k = int(round(n / 2 - j))
    return comb(n, k) - (comb(n, k - 1) if k >= 1 else 0)


for n in range(1, 7):
    S = total_spin(n)
    assert np.allclose(comm(S["x"], S["y"]), 1j * S["z"])                     # 角運動量の交換関係
    S2 = S["x"] @ S["x"] + S["y"] @ S["y"] + S["z"] @ S["z"]
    ev = np.linalg.eigvalsh(S2)
    js = Counter(round(float((-1 + np.sqrt(1 + 4 * e)) / 2) * 2) / 2 for e in ev)   # 固有値 j(j+1) から j を逆算
    for j, count in js.items():
        assert count == copies(n, j) * (2 * j + 1)                             # 次元 = 回数 × (2j+1)
    desc = "、".join(f"j = {frac(j)} が {copies(n, j)} 組" for j in sorted(js, reverse=True))
    print(f"n = {n}：{desc}")'''),

code(r'''def symmetric_ladder(n: int) -> list[Matrix]:
    """|00…0⟩ から S− で下りてできる、j = n/2 の梯子（規格化した状態の列）"""
    S = total_spin(n)
    Sm = S["x"] - 1j * S["y"]
    v = np.zeros(2**n, dtype=complex)
    v[0] = 1.0                                                                 # |00…0⟩：全員が上向き
    ladder = [v]
    for _ in range(n):
        v = Sm @ v
        v = v / np.linalg.norm(v)
        ladder.append(v)
    return ladder


for n in range(1, 6):
    S = total_spin(n)
    B = np.array(symmetric_ladder(n)).T                                        # 列が梯子の状態
    for a in "xyz":
        assert np.allclose(B.conj().T @ S[a] @ B, spin_matrices(n / 2)[a])     # 梯子の上の行列 = spin_matrices(n/2)
print("|00…0⟩ から S− で下りた梯子の上で、S_a の行列は spin_matrices(n/2) と一致しました（n = 1〜5）\n")

for n in (2, 3):
    print(f"n = {n} の梯子（j = {frac(n / 2)}）：")
    for k, v in enumerate(symmetric_ladder(n)):
        terms = {b: complex(c) for b, c in Statevector(v).to_dict().items() if abs(c) > 1e-12}
        text = " + ".join(f"{c.real:.3f}|{b}⟩" for b, c in terms.items())
        print(f"  m = {frac(n / 2 - k):>4}：{text}")'''),

md(r"""## 観察のポイント

- 回転したスピンの測定確率は二項分布です。$j$ が大きいほど分布は鋭くなり、$\langle J_z\rangle=j\cos\theta$ のまわりに集まります（古典的なコマの向きに近づく）。
- $2\pi$ 回すと、半整数の $j$ では状態の符号が反転し、整数の $j$ では元に戻ります。NB-02 の二重被覆は、$j=\frac12$ の場合でした。
- 2つの量子ビットの全スピンは、$j=1$（3状態）と $j=0$（1状態）に分かれます。$j=1$ の真ん中の状態 $\frac1{\sqrt2}(|01\rangle+|10\rangle)$ は、もつれた状態です。Phase 2 でベル状態として扱います。

**次に試すこと**：§3 で、$j=0$ の状態（1重項）を探してみましょう。$S^2$ の固有値 $0$ の固有ベクトルを求めると、$\frac1{\sqrt2}(|01\rangle-|10\rangle)$ になるはずです。"""),
]

save("01_ladder_operators.ipynb", nb1)
save("02_spin_rotation_and_qubits.ipynb", nb2)
