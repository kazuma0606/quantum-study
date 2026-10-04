"""NB-02（notebooks/02_su2_rotation）の2冊のノートブックを生成する。"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path("notebooks/02_su2_rotation")
OUT.mkdir(parents=True, exist_ok=True)
PAULI = "../../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md"
UNITARY = "../../研究ノート/04_群論・代数/unitary_matrix_full_decomposition.md"


def save(name, cells):
    for i, cell in enumerate(cells):
        cell.id = f"{Path(name).stem[:2]}-{i:02d}"   # 作り直しても差分が出ないよう、セルの ID を固定する
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nbformat.write(nb, OUT / name)
    print("書き出し:", OUT / name)


md = new_markdown_cell
code = new_code_cell

SETUP = '''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from numpy.typing import NDArray
from scipy.linalg import expm

np.set_printoptions(precision=4, suppress=True)

# 型の別名（型ヒントを読みやすくするため。実行時には何も確かめない）
Matrix = NDArray[np.complex128]   # 2×2 の複素行列
Ket = NDArray[np.complex128]      # 長さ 2 の複素ベクトル（状態ベクトル）
Vector = NDArray[np.float64]      # 3次元の実ベクトル
Rot3 = NDArray[np.float64]        # 3×3 の実行列（3次元の回転）

sx: Matrix = np.array([[0, 1], [1, 0]], dtype=complex)
sy: Matrix = np.array([[0, -1j], [1j, 0]])
sz: Matrix = np.array([[1, 0], [0, -1]], dtype=complex)
S: tuple[Matrix, Matrix, Matrix] = (sx, sy, sz)
I2: Matrix = np.eye(2, dtype=complex)


def dot_sigma(v: Vector) -> Matrix:
    return v[0] * sx + v[1] * sy + v[2] * sz


def unit(theta: float, phi: float) -> Vector:
    """球座標の単位ベクトル（θ：北極からの角度、φ：経度。ラジアン）"""
    return np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])


def U_rot(n: Vector, theta: float) -> Matrix:
    """ノートの Part VII §2 の閉じた形 exp(−iθ n·σ/2) = cos(θ/2) I − i sin(θ/2) n·σ（n は単位ベクトル）"""
    return np.cos(theta / 2) * I2 - 1j * np.sin(theta / 2) * dot_sigma(n)


def Rz(a: float) -> Matrix:
    return U_rot(np.array([0.0, 0.0, 1.0]), a)


def Ry(a: float) -> Matrix:
    return U_rot(np.array([0.0, 1.0, 0.0]), a)


def Rx(a: float) -> Matrix:
    return U_rot(np.array([1.0, 0.0, 0.0]), a)'''

# ============================================================================================ 01
nb1 = [
md(f"""# NB-02-1 $SU(2)$ の指数関数：$e^{{-i\\theta\\,\\hat n\\cdot\\vec\\sigma/2}}$ を実装する

[パウリ行列のノート]({PAULI}#p7)の Part VII §2 で導いた閉じた形

$$
e^{{-i\\frac\\theta2\\,\\hat n\\cdot\\vec\\sigma}}=\\cos\\frac\\theta2\\,I-i\\sin\\frac\\theta2\\,\\hat n\\cdot\\vec\\sigma
$$

を実装し、行列の指数関数の定義（級数）と比べます。さらに、$SU(2)$ の元から回転軸と角度を取り出す計算、Qiskit の回転ゲート（`RXGate` など）との関係、二重被覆（$\\theta=2\\pi$ で $-I$）を確かめます。$R_z,R_y$ の具体形は、[ユニタリ行列のノート]({UNITARY})の Part VIII でも計算しています。

**使い方**：上から順に実行します。各セルの `assert` が、ノートの式と計算結果の一致を確かめます。"""),

code(SETUP),

md("""## 1. 閉じた形と、級数の定義を比べる

行列の指数関数の定義は級数 $e^X=\\sum_{m=0}^\\infty\\frac{X^m}{m!}$ です。$X=-i\\frac\\theta2\\hat n\\cdot\\vec\\sigma$ について、$N$ 項までの部分和と閉じた形の差（行列のノルム）を描きます。$(\\hat n\\cdot\\vec\\sigma)^2=I$ なので、偶数次と奇数次がそれぞれ $\\cos\\frac\\theta2$、$\\sin\\frac\\theta2$ のテイラー展開になり、$N$ を増やすと差は $0$ に近づきます。scipy の `expm` とも比べます。"""),

code('''def partial_sum(X: Matrix, N: int) -> Matrix:
    """級数 Σ_{m=0}^{N} X^m / m! の部分和"""
    total, term = np.zeros_like(X), np.eye(2, dtype=complex)
    for m in range(N + 1):
        total = total + term
        term = term @ X / (m + 1)
    return total


rng = np.random.default_rng(0)
for _ in range(50):
    n = rng.normal(size=3)
    n /= np.linalg.norm(n)
    th = rng.uniform(-10, 10)
    X = -1j * th / 2 * dot_sigma(n)
    assert np.allclose(U_rot(n, th), expm(X))              # 閉じた形 = scipy の expm
    assert np.allclose(U_rot(n, th), partial_sum(X, 60))   # 閉じた形 = 級数（60 項）

n0 = unit(1.0, 0.4)
fig = go.Figure()
for th in (1.0, 3.0, 6.0):
    errs = [np.linalg.norm(partial_sum(-1j * th / 2 * dot_sigma(n0), N) - U_rot(n0, th)) for N in range(0, 26)]
    fig.add_trace(go.Scatter(x=list(range(0, 26)), y=errs, mode="lines+markers", name=f"θ = {th}"))
fig.update_layout(height=380, width=700, yaxis_type="log", xaxis_title="部分和の項数 N", yaxis_title="閉じた形との差（ノルム）",
                  margin=dict(t=20))
fig'''),

md("""## 2. $SU(2)$ の元から、回転軸と角度を取り出す

閉じた形 $U=\\cos\\frac\\theta2I-i\\sin\\frac\\theta2\\,\\hat n\\cdot\\vec\\sigma$ に、パウリ行列の直交性（ノートの Part II §4）を使うと、

$$
\\cos\\frac\\theta2=\\frac12\\operatorname{tr}U,\\qquad \\sin\\frac\\theta2\\;n_k=\\frac i2\\operatorname{tr}(\\sigma_kU)
$$

で、$U$ から $\\theta\\in[0,2\\pi]$ と $\\hat n$ を取り出せます（ノートの Part I §4「どの元も $e^{iA}$ と書ける」の具体的な計算です）。ランダムな $SU(2)$ の元で、取り出した $(\\theta,\\hat n)$ から $U$ が元に戻ることを確かめます。"""),

code('''from qiskit.quantum_info import random_unitary


def to_su2(V: Matrix) -> Matrix:
    """U(2) の元を、大域位相で割って SU(2) の元にする（det = 1）"""
    return V / np.sqrt(np.linalg.det(V))


def axis_angle(U: Matrix) -> tuple[Vector, float]:
    """SU(2) の元 U から、回転軸 n と角度 θ ∈ [0, 2π] を取り出す"""
    c = np.clip(np.trace(U).real / 2, -1, 1)
    theta = 2 * np.arccos(c)
    if np.isclose(np.sin(theta / 2), 0):
        return np.array([0.0, 0.0, 1.0]), theta          # U = ±I：軸は決まらない（どの軸でもよい）
    n = np.array([(0.5j * np.trace(Sk @ U)).real for Sk in S]) / np.sin(theta / 2)
    return n, theta


for seed in range(100):
    U = to_su2(random_unitary(2, seed=seed).data)
    assert np.allclose(U.conj().T @ U, I2) and np.isclose(np.linalg.det(U), 1)
    assert np.isclose(U[1, 1], np.conj(U[0, 0])) and np.isclose(U[0, 1], -np.conj(U[1, 0]))   # [[a, −b*], [b, a*]]
    n, th = axis_angle(U)
    assert np.isclose(np.linalg.norm(n), 1) and np.allclose(U_rot(n, th), U)

print("例：U =\\n", U)
print(f"回転軸 n = {n}、角度 θ = {np.degrees(th):.2f}°")'''),

md("""## 3. Qiskit の回転ゲートとの関係

Qiskit の `RXGate(θ)`、`RYGate(θ)`、`RZGate(θ)` は、そのまま $e^{-i\\theta\\sigma/2}$ です。一方、よく使う `PhaseGate(λ)`（$P(\\lambda)=\\operatorname{diag}(1,e^{i\\lambda})$）と `UGate(θ, φ, λ)` は、$R_z,R_y$ と**大域位相だけ**違います：

$$
P(\\lambda)=e^{i\\lambda/2}R_z(\\lambda),\\qquad U(\\theta,\\phi,\\lambda)=e^{i(\\phi+\\lambda)/2}\\,R_z(\\phi)\\,R_y(\\theta)\\,R_z(\\lambda)
$$

大域位相はブロッホ球の上では見えないので、$P(\\lambda)$ と $R_z(\\lambda)$ は同じ回転を表します（$\\det P(\\lambda)=e^{i\\lambda}$ なので、$P(\\lambda)$ は $SU(2)$ の元ではありません）。"""),

code('''from qiskit.circuit.library import PhaseGate, RXGate, RYGate, RZGate, UGate

for th in np.linspace(-7, 7, 15):
    assert np.allclose(RXGate(th).to_matrix(), Rx(th))
    assert np.allclose(RYGate(th).to_matrix(), Ry(th))
    assert np.allclose(RZGate(th).to_matrix(), Rz(th))
    assert np.allclose(PhaseGate(th).to_matrix(), np.exp(1j * th / 2) * Rz(th))

for t, p, l in rng.uniform(-np.pi, np.pi, size=(30, 3)):
    assert np.allclose(UGate(t, p, l).to_matrix(), np.exp(1j * (p + l) / 2) * Rz(p) @ Ry(t) @ Rz(l))

lam = 0.9
print("P(λ) =\\n", PhaseGate(lam).to_matrix(), "\\ndet P(λ) =", np.round(np.linalg.det(PhaseGate(lam).to_matrix()), 4),
      " ← e^{iλ}。大域位相 e^{iλ/2} を除くと R_z(λ)")'''),

md("""## 4. 二重被覆：$\\theta=2\\pi$ で $-I$

閉じた形で $\\theta=2\\pi$ とすると $U=\\cos\\pi\\,I-i\\sin\\pi\\,\\hat n\\cdot\\vec\\sigma=-I$ で、$I$ に戻るのは $\\theta=4\\pi$ です。どの軸でも同じであることを確かめ、$\\frac12\\operatorname{tr}U(\\theta)=\\cos\\frac\\theta2$（周期 $4\\pi$）を描きます。ブロッホ球の上の回転（次のノートブック）は、周期 $2\\pi$ です。"""),

code('''for seed in range(20):
    n = rng.normal(size=3)
    n /= np.linalg.norm(n)
    assert np.allclose(U_rot(n, 2 * np.pi), -I2) and np.allclose(U_rot(n, 4 * np.pi), I2)
    assert np.allclose(RXGate(2 * np.pi).to_matrix(), -I2)

thetas = np.linspace(0, 4 * np.pi, 400)
fig2 = go.Figure([go.Scatter(x=thetas / np.pi, y=[np.trace(U_rot(n0, t)).real / 2 for t in thetas], mode="lines",
                             name="½ tr U(θ) = cos(θ/2)")])
fig2.add_vline(x=2, line_dash="dot", annotation_text="θ = 2π：U = −I")
fig2.add_vline(x=4, line_dash="dot", annotation_text="θ = 4π：U = I")
fig2.update_layout(height=360, width=700, xaxis_title="θ / π", yaxis_title="½ tr U", margin=dict(t=30))
fig2'''),

md("""## 観察のポイント

- 級数の部分和は、$\\theta$ が大きいほど収束に多くの項が必要ですが、閉じた形は $\\theta$ によらず2項（$I$ と $\\hat n\\cdot\\vec\\sigma$）で済みます。$(\\hat n\\cdot\\vec\\sigma)^2=I$ のおかげです。
- $SU(2)$ のどの元も、軸 $\\hat n$ と角度 $\\theta$ の組で書けます（$\\theta$ を $4\\pi-\\theta$、$\\hat n$ を $-\\hat n$ に変えても同じ元）。
- Qiskit の `PhaseGate` と `RZGate` は大域位相だけ違い、同じ回転を表します。回路を組むとき（Phase 2）に、どちらを使っても測定結果は変わりません。

**次のノートブック**：[02_bloch_rotation.ipynb](02_bloch_rotation.ipynb) で、$U$ がブロッホ球をどう回すかを、スライダーで見ます。"""),
]

# ============================================================================================ 02
SPHERE = '''# 注意：FigureWidget（スライダーで描き直す図）には、numpy 配列ではなく Python のリストを渡す。
# numpy 配列を渡すと、ブラウザから戻ってくる差分の処理で
# 「ValueError: The truth value of an array ... is ambiguous」になることがある（plotly 7.1 の FigureWidget）。
def sphere_traces() -> list[BaseTraceType]:
    u, w = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 60))
    tr: list[BaseTraceType] = [go.Surface(x=(np.sin(u) * np.cos(w)).tolist(), y=(np.sin(u) * np.sin(w)).tolist(), z=np.cos(u).tolist(), opacity=0.12,
                                          showscale=False, colorscale=[[0, "#9ecae1"], [1, "#9ecae1"]], hoverinfo="skip")]
    t = np.linspace(0, 2 * np.pi, 200)
    tr.append(go.Scatter3d(x=np.cos(t).tolist(), y=np.sin(t).tolist(), z=(0 * t).tolist(), mode="lines", line=dict(color="#bbb"), hoverinfo="skip", showlegend=False))
    for e in np.eye(3):
        tr.append(go.Scatter3d(x=[-1.25 * e[0], 1.25 * e[0]], y=[-1.25 * e[1], 1.25 * e[1]], z=[-1.25 * e[2], 1.25 * e[2]],
                               mode="lines", line=dict(color="#ccc"), hoverinfo="skip", showlegend=False))
    names = {(0, 0, 1): "|0⟩", (0, 0, -1): "|1⟩", (1, 0, 0): "|+⟩", (-1, 0, 0): "|−⟩", (0, 1, 0): "|+i⟩", (0, -1, 0): "|−i⟩"}
    pts = np.array(list(names))
    tr.append(go.Scatter3d(x=(1.12 * pts[:, 0]).tolist(), y=(1.12 * pts[:, 1]).tolist(), z=(1.12 * pts[:, 2]).tolist(), mode="text", text=list(names.values()),
                           textfont=dict(size=13, color="#1f77b4"), hoverinfo="skip", showlegend=False))
    return tr


def scene_layout() -> dict[str, object]:
    ax = dict(range=[-1.3, 1.3], showbackground=False, showticklabels=False, title="")
    return dict(xaxis=ax, yaxis=ax, zaxis=ax, aspectmode="cube", camera=dict(eye=dict(x=1.3, y=-1.5, z=0.6)))


def line3d(P: NDArray[np.float64], color: str, name: str, width: int = 6, dash: str = "solid", legend: bool = True) -> go.Scatter3d:
    return go.Scatter3d(x=P[:, 0].tolist(), y=P[:, 1].tolist(), z=P[:, 2].tolist(), mode="lines", line=dict(color=color, width=width, dash=dash),
                        name=name, showlegend=legend, hoverinfo="skip")


def set_xyz(trace: go.Scatter3d, P: NDArray[np.float64]) -> None:
    """点の列 P（N×3）を、トレースの座標にリストとして入れる（上の注意を参照）"""
    trace.x, trace.y, trace.z = P[:, 0].tolist(), P[:, 1].tolist(), P[:, 2].tolist()'''

nb2 = [
md(f"""# NB-02-2 $U$ はブロッホ球を回す：回転・順序・ZYZ 分解

[パウリ行列のノート]({PAULI}#p7)の Part VII §3〜§4 で導いたように、$U=e^{{-i\\theta\\,\\hat n\\cdot\\vec\\sigma/2}}$ を状態に掛けると、ブロッホベクトルは軸 $\\hat n$ のまわりに角度 $\\theta$ だけ回ります（ロドリゲスの回転公式）。このノートブックでは、

1. $U$ から3次元の回転行列 $R$ を作り、ロドリゲスの公式・回転の合成・$R(-U)=R(U)$ を確かめる
2. 軸・角度・初期状態をスライダーで変えて、回転を見る
3. 回転の順序を入れ替えると結果が変わることを見る（$R_x$ と $R_y$）
4. どの $U$ も $e^{{i\\alpha}}R_z(\\beta)R_y(\\gamma)R_z(\\delta)$ と書ける（ZYZ 分解。[ユニタリ行列のノート]({UNITARY})の Part IX）ことを、自前の計算と Qiskit の `OneQubitEulerDecomposer` で確かめ、3つの回転を順に進めて見る

を扱います。量子回路はまだ使いません（Phase 2 の NB-07 で扱います）。"""),

code(SETUP + '''


from plotly.basedatatypes import BaseTraceType


def bloch(psi: Ket) -> Vector:
    """ブロッホベクトル（⟨σx⟩, ⟨σy⟩, ⟨σz⟩）"""
    return np.array([np.vdot(psi, Sk @ psi).real for Sk in S])


def rotation_matrix(U: Matrix) -> Rot3:
    """U が引き起こすブロッホ球の回転：U(r·σ)U† = (R r)·σ から、R_ij = ½ tr(σ_i U σ_j U†)"""
    return np.array([[0.5 * np.trace(S[i] @ U @ S[j] @ U.conj().T).real for j in range(3)] for i in range(3)])


def rodrigues(n: Vector, theta: float, r: Vector) -> Vector:
    """ロドリゲスの回転公式：r を軸 n のまわりに θ 回す"""
    return np.cos(theta) * r + np.sin(theta) * np.cross(n, r) + (1 - np.cos(theta)) * np.dot(n, r) * n


STATES: dict[str, Ket] = {"|0⟩": np.array([1, 0], complex), "|1⟩": np.array([0, 1], complex),
                          "|+⟩": np.array([1, 1], complex) / np.sqrt(2), "|−⟩": np.array([1, -1], complex) / np.sqrt(2),
                          "|+i⟩": np.array([1, 1j]) / np.sqrt(2), "|−i⟩": np.array([1, -1j]) / np.sqrt(2)}


''' + SPHERE),

md("""## 1. 数値で確認する

ランダムな軸・角度で、次を確かめます。

- $R(U)$ は回転行列（$R^TR=I$、$\\det R=1$）で、ロドリゲスの公式と一致する
- 状態 $|\\psi\\rangle$ に $U$ を掛けると、ブロッホベクトルは $R\\,\\vec r$ になる
- 回転の合成：$R(U_1U_2)=R(U_1)R(U_2)$（準同型）
- 二重被覆：$R(-U)=R(U)$"""),

code('''rng = np.random.default_rng(1)
for _ in range(200):
    n = rng.normal(size=3)
    n /= np.linalg.norm(n)
    th = rng.uniform(-7, 7)
    U = U_rot(n, th)
    R = rotation_matrix(U)
    assert np.allclose(R.T @ R, np.eye(3)) and np.isclose(np.linalg.det(R), 1)          # 回転行列
    r = rng.normal(size=3)
    assert np.allclose(R @ r, rodrigues(n, th, r))                                       # ロドリゲスの公式
    psi = rng.normal(size=2) + 1j * rng.normal(size=2)
    psi /= np.linalg.norm(psi)
    assert np.allclose(bloch(U @ psi), R @ bloch(psi))                                   # 状態の回転
    m = rng.normal(size=3)
    m /= np.linalg.norm(m)
    U2 = U_rot(m, rng.uniform(-7, 7))
    assert np.allclose(rotation_matrix(U @ U2), R @ rotation_matrix(U2))                 # 準同型
    assert np.allclose(rotation_matrix(-U), R)                                           # R(−U) = R(U)
print("回転行列・ロドリゲスの公式・合成・二重被覆を、ランダムな 200 組で確認しました")
print("例：R_z(π/2) の回転行列（z 軸のまわりに 90°）=\\n", np.round(rotation_matrix(Rz(np.pi / 2)), 6))'''),

md("""## 2. スライダーで回転を見る

- **軸の θ, φ**：回転軸 $\\hat n$（赤）の向き
- **回転角 θ**：$U=e^{-i\\theta\\,\\hat n\\cdot\\vec\\sigma/2}$ の角度。橙の線が、角度 $0$ から $\\theta$ までに状態が通る道（$\\hat n$ を軸とする円の一部）、灰色の点線が一周分の円です
- **初期状態**：回す前の状態

下の表示で、$U$ の行列と $\\frac12\\operatorname{tr}U=\\cos\\frac\\theta2$ を確かめてください。回転角が $360^\\circ$ を超えると、ブロッホ球の上では一周して戻るのに、$U$ の符号は逆（$-U$）になっています。"""),

code('''fig = go.FigureWidget(data=sphere_traces())
fig.add_trace(line3d(np.zeros((2, 3)), "#d62728", "回転軸 n", width=7))
fig.add_trace(line3d(np.zeros((2, 3)), "#999", "一周分の円", width=3, dash="dot"))
fig.add_trace(line3d(np.zeros((2, 3)), "#e67e00", "通った道（0 → θ）", width=7))
fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[1], mode="markers", marker=dict(size=6, color="#555"), name="初期状態"))
fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[1], mode="markers", marker=dict(size=8, color="#e67e00"), name="回した後の状態"))
fig.update_layout(height=560, width=640, margin=dict(l=0, r=0, t=10, b=0), scene=scene_layout(), legend=dict(y=0.02))

ax_th = W.FloatSlider(value=50, min=0, max=180, step=5, description="軸の θ")
ax_ph = W.FloatSlider(value=20, min=-180, max=180, step=5, description="軸の φ")
rot = W.FloatSlider(value=120, min=0, max=720, step=5, description="回転角 θ")
init = W.Dropdown(options=list(STATES), value="|0⟩", description="初期状態")
info = W.HTML()


def fmt(z: complex) -> str:
    return f"{z.real:+.3f}{z.imag:+.3f}i"


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、図と文字の表示を描き直す"""
    n = unit(np.radians(ax_th.value), np.radians(ax_ph.value))
    th = np.radians(rot.value)
    r0 = bloch(STATES[init.value])
    U = U_rot(n, th)
    full = np.array([rodrigues(n, t, r0) for t in np.linspace(0, 2 * np.pi, 120)])
    path = np.array([rodrigues(n, t, r0) for t in np.linspace(0, th, 200)])
    r1 = bloch(U @ STATES[init.value])
    assert np.allclose(r1, path[-1])
    with fig.batch_update():
        set_xyz(fig.data[-5], np.array([[0, 0, 0], 1.3 * n]))
        set_xyz(fig.data[-4], full)
        set_xyz(fig.data[-3], path)
        set_xyz(fig.data[-2], r0[None, :])
        set_xyz(fig.data[-1], r1[None, :])
    info.value = (f"<b>U</b> = [[{fmt(U[0, 0])}, {fmt(U[0, 1])}], [{fmt(U[1, 0])}, {fmt(U[1, 1])}]]　"
                  f"½ tr U = cos(θ/2) = {np.trace(U).real / 2:+.3f}<br>"
                  f"回した後のブロッホベクトル = ({r1[0]:+.3f}, {r1[1]:+.3f}, {r1[2]:+.3f})")


for w in (ax_th, ax_ph, rot, init):
    w.observe(update, "value")
update()
W.VBox([W.HBox([ax_th, ax_ph]), W.HBox([rot, init]), info, fig])'''),

md("""## 3. 回転の順序で、結果が変わる

状態に「$R_x(\\alpha)$ を掛けてから $R_y(\\alpha)$」と「$R_y(\\alpha)$ を掛けてから $R_x(\\alpha)$」を比べます（行列では $R_y(\\alpha)R_x(\\alpha)$ と $R_x(\\alpha)R_y(\\alpha)$。右の行列が先に作用します）。$[\\sigma_x,\\sigma_y]=2i\\sigma_z\\neq0$ なので、2つの結果は一致しません。

**小さな角度でのずれ**：$A=-i\\frac\\alpha2\\sigma_x$、$B=-i\\frac\\alpha2\\sigma_y$ とすると、$e^Ae^B\\approx e^{A+B+\\frac12[A,B]}$ なので、2つの順序の違いは、2次までで $e^{\\pm[A,B]}$、つまり **$z$ 軸のまわりの角度 $\\alpha^2$ の回転**です（$[A,B]=-\\frac{\\alpha^2}4[\\sigma_x,\\sigma_y]=-i\\frac{\\alpha^2}2\\sigma_z$）。

- 初期状態が $z$ 軸から離れていれば（$|{+}\\rangle$ など）、ずれは $\\alpha^2$ に比例します。
- 初期状態が $z$ 軸上の $|0\\rangle$ なら、$z$ 軸のまわりの回転では動かないので、2次のずれが消え、ずれは $\\alpha^3$ に比例します。

下のセルで、両方を数値で確かめます。"""),

code('''def two_step_path(first: Matrix, second: Matrix, psi: Ket, steps: int = 80) -> NDArray[np.float64]:
    """first を少しずつ掛けてから second を少しずつ掛けたときの、ブロッホベクトルの道"""
    out = []
    for f in (first, second):
        n, th = axis_angle_of(f)
        out += [bloch(U_rot(n, t) @ psi) for t in np.linspace(0, th, steps)]
        psi = f @ psi
    return np.array(out)


def axis_angle_of(U: Matrix) -> tuple[Vector, float]:
    c = np.clip(np.trace(U).real / 2, -1, 1)
    th = 2 * np.arccos(c)
    if np.isclose(np.sin(th / 2), 0):
        return np.array([0.0, 0.0, 1.0]), th
    return np.array([(0.5j * np.trace(Sk @ U)).real for Sk in S]) / np.sin(th / 2), th


def order_gap(psi: Ket, a: float) -> float:
    """2つの順序（Rx → Ry と Ry → Rx）で回した後の、ブロッホベクトルのずれ"""
    return float(np.linalg.norm(bloch(Ry(a) @ Rx(a) @ psi) - bloch(Rx(a) @ Ry(a) @ psi)))


for name in ("|+⟩", "|0⟩"):
    print(f"初期状態 {name}")
    for a in (0.01, 0.02, 0.04):
        d = order_gap(STATES[name], a)
        print(f"  α = {a:.2f}：ずれ = {d:.2e}、ずれ / α² = {d / a**2:.3f}、ずれ / α³ = {d / a**3:.3f}")
    a = 0.01
    if name == "|+⟩":
        assert abs(order_gap(STATES[name], a) / a**2 - 1) < 1e-2          # α² に比例（係数 1）
    else:
        assert abs(order_gap(STATES[name], a) / a**3 - 1 / np.sqrt(2)) < 1e-2   # α³ に比例

# 2つの順序の違い（Ry Rx)(Rx Ry)^{-1} は、z 軸のまわりの角度 ≈ α² の回転
a = 0.01
n_d, th_d = axis_angle_of(Ry(a) @ Rx(a) @ np.linalg.inv(Rx(a) @ Ry(a)))
assert abs(th_d / a**2 - 1) < 1e-3 and abs(abs(n_d[2]) - 1) < 1e-2
print(f"\\n2つの順序の違い：回転角 / α² = {th_d / a**2:.4f}、回転軸 = {np.round(n_d, 3)}（z 軸）")

fig3 = go.FigureWidget(data=sphere_traces())
fig3.add_trace(line3d(np.zeros((2, 3)), "#1f77b4", "Rx(α) → Ry(α)", width=7))
fig3.add_trace(line3d(np.zeros((2, 3)), "#d62728", "Ry(α) → Rx(α)", width=7))
fig3.update_layout(height=520, width=600, margin=dict(l=0, r=0, t=10, b=0), scene=scene_layout(), legend=dict(y=0.02))
alpha = W.FloatSlider(value=90, min=0, max=180, step=5, description="α [度]")
init3 = W.Dropdown(options=list(STATES), value="|0⟩", description="初期状態")
info3 = W.HTML()


def update3(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、2つの順序の道を描き直す"""
    a = np.radians(alpha.value)
    psi0 = STATES[init3.value]
    p1 = two_step_path(Rx(a), Ry(a), psi0)
    p2 = two_step_path(Ry(a), Rx(a), psi0)
    assert np.allclose(p1[-1], bloch(Ry(a) @ Rx(a) @ psi0)) and np.allclose(p2[-1], bloch(Rx(a) @ Ry(a) @ psi0))
    with fig3.batch_update():
        set_xyz(fig3.data[-2], p1)
        set_xyz(fig3.data[-1], p2)
    info3.value = (f"Rx → Ry の後：({p1[-1][0]:+.3f}, {p1[-1][1]:+.3f}, {p1[-1][2]:+.3f})　"
                   f"Ry → Rx の後：({p2[-1][0]:+.3f}, {p2[-1][1]:+.3f}, {p2[-1][2]:+.3f})")


for w in (alpha, init3):
    w.observe(update3, "value")
update3()
W.VBox([W.HBox([alpha, init3]), info3, fig3])'''),

md("""## 4. ZYZ 分解：どの $U$ も $e^{i\\alpha}R_z(\\beta)R_y(\\gamma)R_z(\\delta)$

**自前の計算**：大域位相 $e^{i\\alpha}$（$\\alpha=\\frac12\\arg\\det U$）で割って $SU(2)$ の元 $\\begin{pmatrix}a&-b^*\\\\b&a^*\\end{pmatrix}$ にします。一方、

$$
R_z(\\beta)R_y(\\gamma)R_z(\\delta)=\\begin{pmatrix}e^{-i(\\beta+\\delta)/2}\\cos\\frac\\gamma2&-e^{-i(\\beta-\\delta)/2}\\sin\\frac\\gamma2\\\\ e^{i(\\beta-\\delta)/2}\\sin\\frac\\gamma2&e^{i(\\beta+\\delta)/2}\\cos\\frac\\gamma2\\end{pmatrix}
$$

なので、$\\gamma=2\\arctan\\frac{|b|}{|a|}$、$\\beta=\\arg b-\\arg a$、$\\delta=-\\arg a-\\arg b$ です。[ユニタリ行列のノート]({UNITARY})の Part IX の形 $U=e^{i\\phi/2}R_z(\\beta-\\alpha)R(\\theta)R_z(\\phi-\\beta-\\alpha)$ は、$R(\\theta)=R_y(2\\theta)$ として、同じ分解を別の記号で書いたものです。

ランダムな $U$ で、自前の分解と Qiskit の `OneQubitEulerDecomposer("ZYZ")` が、どちらも $U$ を再現することを確かめます（角度そのものは、$2\\pi$ の違いや $\\beta,\\delta$ の選び方で一致しないことがあります）。""".replace("{UNITARY}", UNITARY)),

code('''from qiskit.quantum_info import random_unitary
from qiskit.synthesis import OneQubitEulerDecomposer


def zyz(U: Matrix) -> tuple[float, float, float, float]:
    """U = e^{iα} R_z(β) R_y(γ) R_z(δ) の (α, β, γ, δ) を返す"""
    alpha = np.angle(np.linalg.det(U)) / 2
    V = U * np.exp(-1j * alpha)                       # det V = 1
    a, b = V[0, 0], V[1, 0]
    gamma = 2 * np.arctan2(abs(b), abs(a))
    arg_a = np.angle(a) if abs(a) > 1e-12 else 0.0
    arg_b = np.angle(b) if abs(b) > 1e-12 else 0.0
    return alpha, arg_b - arg_a, gamma, -arg_a - arg_b


decomposer = OneQubitEulerDecomposer("ZYZ")
for seed in range(200):
    U = random_unitary(2, seed=seed).data
    al, be, ga, de = zyz(U)
    assert np.allclose(np.exp(1j * al) * Rz(be) @ Ry(ga) @ Rz(de), U)                   # 自前の分解
    th_q, ph_q, la_q, gp_q = decomposer.angles_and_phase(U)
    assert np.allclose(np.exp(1j * gp_q) * Rz(ph_q) @ Ry(th_q) @ Rz(la_q), U)           # Qiskit の分解
print("自前の分解（α, β, γ, δ）=", np.round([al, be, ga, de], 4))
print("Qiskit  （位相, φ, θ, λ）=", np.round([gp_q, ph_q, th_q, la_q], 4), " ← U = e^{i位相} Rz(φ) Ry(θ) Rz(λ)")'''),

md("""### 3つの回転を順に進めて見る

ランダムな $U$ を ZYZ に分解し、$|0\\rangle$ に $R_z(\\delta)$ → $R_y(\\gamma)$ → $R_z(\\beta)$ の順に（行列の右から）掛けていきます。スライダー **進み具合** を $0$ から $3$ まで動かすと、3つの回転を1つずつ進めます（$|0\\rangle$ は $z$ 軸上にあるので、最初の $R_z(\\delta)$ では動きません。初期状態を変えると、3つとも見えます）。最後の点は、$U|0\\rangle$ のブロッホベクトル（黒）に一致します。"""),

code('''U_demo = random_unitary(2, seed=7).data
al, be, ga, de = zyz(U_demo)
steps = [(np.array([0.0, 0.0, 1.0]), de, "#2ca02c"), (np.array([0.0, 1.0, 0.0]), ga, "#9467bd"), (np.array([0.0, 0.0, 1.0]), be, "#e67e00")]

fig4 = go.FigureWidget(data=sphere_traces())
for _, _, color in steps:
    fig4.add_trace(line3d(np.zeros((2, 3)), color, "", width=7, legend=False))
fig4.add_trace(go.Scatter3d(x=[0], y=[0], z=[1], mode="markers", marker=dict(size=7, color="#e67e00"), name="途中の状態"))
fig4.add_trace(go.Scatter3d(x=[0], y=[0], z=[1], mode="markers", marker=dict(size=9, color="black", symbol="x"), name="U|ψ⟩（ゴール）"))
fig4.update_layout(height=520, width=600, margin=dict(l=0, r=0, t=10, b=0), scene=scene_layout(), legend=dict(y=0.02))
for k, name in enumerate(["Rz(δ)", "Ry(γ)", "Rz(β)"]):
    fig4.data[len(fig4.data) - 5 + k].name = name
    fig4.data[len(fig4.data) - 5 + k].showlegend = True

progress = W.FloatSlider(value=3, min=0, max=3, step=0.05, description="進み具合")
init4 = W.Dropdown(options=list(STATES), value="|0⟩", description="初期状態")
info4 = W.HTML(f"分解：U = e^{{i·{al:.3f}}} Rz({be:.3f}) Ry({ga:.3f}) Rz({de:.3f})")


def update4(*_: object) -> None:
    """進み具合に応じて、3つの回転の道を描き直す"""
    psi = STATES[init4.value]
    r = bloch(psi)
    for k, (n, ang, _) in enumerate(steps):
        frac = np.clip(progress.value - k, 0, 1)
        path = np.array([rodrigues(n, t, r) for t in np.linspace(0, frac * ang, 100)])
        set_xyz(fig4.data[len(fig4.data) - 5 + k], path)
        r = path[-1]
    goal = bloch(U_demo @ psi)
    if progress.value >= 3:
        assert np.allclose(r, goal)                   # 3つの回転の後 = U|ψ⟩
    with fig4.batch_update():
        set_xyz(fig4.data[-2], r[None, :])
        set_xyz(fig4.data[-1], goal[None, :])


for w in (progress, init4):
    w.observe(update4, "value")
update4()
W.VBox([W.HBox([progress, init4]), info4, fig4])'''),

md("""## 観察のポイント

- 回転角を $360^\\circ$ にすると、ブロッホ球の上では元の点に戻りますが、$\\frac12\\operatorname{tr}U=-1$（$U=-I$）です。$720^\\circ$ で $U=I$ に戻ります（二重被覆）。
- 回転軸を初期状態の向きにそろえると、状態は動きません（軸の上の点は回転で動かない）。$|0\\rangle$ を $z$ 軸のまわりに回しても、大域位相が変わるだけです。
- 回転の順序を入れ替えると、結果が変わります。その違いは、小さな角度では $z$ 軸のまわりの角度 $\\alpha^2$ の回転で、交換子 $[\\sigma_x,\\sigma_y]=2i\\sigma_z$ がそのまま現れています。$|0\\rangle$ から始めると、この回転が効かないので、ずれは $\\alpha^3$ まで小さくなります。
- どんな1量子ビットのゲートも、$z$ 軸と $y$ 軸のまわりの回転を3つ並べて作れます（ZYZ 分解）。Qiskit の `UGate(θ, φ, λ)` は、まさにこの形です。

**次に試すこと**：ZYZ の代わりに ZXZ 分解（`OneQubitEulerDecomposer("ZXZ")`）を試してみましょう。ユニタリ行列のノートの Part IX §5 では、ZYZ と ZXZ が $R_z(\\pm\\pi/2)$ による共役で結ばれていることを示しています。

**次のノートブック（NB-03）**：[../03_angular_momentum/01_ladder_operators.ipynb](../03_angular_momentum/01_ladder_operators.ipynb) で、スピン $\\frac12$ を一般の角運動量 $j$ に広げます。$2\\pi$ 回転が $-I$ になるのは半整数の $j$ だけであることも、そこで確かめます。"""),
]

save("01_su2_exponential.ipynb", nb1)
save("02_bloch_rotation.ipynb", nb2)
