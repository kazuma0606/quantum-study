"""NB-01（notebooks/01_pauli_bloch）の2冊のノートブックを生成する。"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path("notebooks/01_pauli_bloch")
OUT.mkdir(parents=True, exist_ok=True)
NOTE = "../../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md"


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

# ============================================================================================ 01
nb1 = [
md(f"""# NB-01-1 パウリ行列の性質を、行列計算で確かめる

[パウリ行列のノート]({NOTE})の Part II・IV・V で手で計算した性質を、NumPy の行列計算で確かめます。最後に、同じことを Qiskit の `quantum_info` でも確かめて、答え合わせをします。

**確かめること**

1. パウリ行列は、トレースゼロのエルミート行列の一般形から取り出せる（ノートの Part II §3）
2. 基本性質の表：エルミート、$\\sigma^2=I$、ユニタリ、トレース $0$、行列式 $-1$、固有値 $\\pm1$（Part II §6）
3. 積の表 $\\sigma_i\\sigma_j=\\delta_{{ij}}I+i\\varepsilon_{{ijk}}\\sigma_k$、交換関係、反交換関係（Part IV・V）
4. ベクトルとの積 $(\\vec a\\cdot\\vec\\sigma)(\\vec b\\cdot\\vec\\sigma)=(\\vec a\\cdot\\vec b)I+i(\\vec a\\times\\vec b)\\cdot\\vec\\sigma$（Part V §3。スライダーで $\\vec b$ を動かせます）
5. 任意の $2\\times2$ 行列の展開 $M=\\frac12\\operatorname{{tr}}(M)I+\\sum_i\\frac12\\operatorname{{tr}}(\\sigma_iM)\\sigma_i$（Part II §5）

**使い方**：上から順に実行します。各セルの `assert` が、ノートの式と計算結果の一致を確かめます（一致しなければエラーで止まります）。"""),

code('''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from numpy.typing import NDArray
from plotly.subplots import make_subplots

np.set_printoptions(precision=4, suppress=True)

# 型の別名（型ヒントを読みやすくするため。実行時には何も確かめない）
Matrix = NDArray[np.complex128]   # 2×2 の複素行列
Vector = NDArray[np.float64]      # 3次元の実ベクトル


def traceless_hermitian(nx: float, ny: float, nz: float) -> Matrix:
    """ノートの Part II §3：トレースゼロのエルミート行列の一般形"""
    return np.array([[nz, nx - 1j * ny], [nx + 1j * ny, -nz]])


# 係数を1つずつ 1 にすると、パウリ行列が取り出せる
sx = traceless_hermitian(1, 0, 0)
sy = traceless_hermitian(0, 1, 0)
sz = traceless_hermitian(0, 0, 1)
I2: Matrix = np.eye(2, dtype=complex)
NAMES = "xyz"
S: list[Matrix] = [sx, sy, sz]

for name, M in zip(NAMES, S):
    print(f"σ{name} =\\n{M}\\n")'''),

md("""## 1. 基本性質の表

ノートの Part II §6 の表を、1行ずつ確かめます。固有ベクトルは、表に書いた形（$\\sigma_x$ なら $\\frac1{\\sqrt2}(1,\\pm1)$ など）で、本当に固有値 $\\pm1$ の固有ベクトルになっているかを、$\\sigma\\mathbf v=\\pm\\mathbf v$ で確かめます。"""),

code('''EIGVEC: dict[str, tuple[list[complex], list[complex]]] = {"x": ([1, 1], [1, -1]), "y": ([1, 1j], [1, -1j]), "z": ([1, 0], [0, 1])}

for name, M in zip(NAMES, S):
    herm = np.allclose(M, M.conj().T)
    square = np.allclose(M @ M, I2)
    unitary = np.allclose(M.conj().T @ M, I2)
    tr, det = np.trace(M).real, np.linalg.det(M).real
    eig = np.linalg.eigvalsh(M)
    vp, vm = (np.array(v, dtype=complex) / np.linalg.norm(v) for v in EIGVEC[name])
    print(f"σ{name}: エルミート {herm}、σ²=I {square}、ユニタリ {unitary}、tr = {tr:+.0f}、det = {det:+.0f}、固有値 {eig}")
    assert herm and square and unitary and np.isclose(tr, 0) and np.isclose(det, -1)
    assert np.allclose(eig, [-1, 1])
    assert np.allclose(M @ vp, vp) and np.allclose(M @ vm, -vm)

# iσ は SU(2) に入る（det = 1）が、σ 自身は入らない（det = −1）
assert all(np.isclose(np.linalg.det(1j * M), 1) for M in S)
print("\\nすべての性質を確認しました")'''),

md("""## 2. 積の表と、交換関係・反交換関係

レヴィ＝チヴィタ記号 $\\varepsilon_{ijk}$ を、「$(i,j,k)$ を並べ替える置換の符号」として計算し、9通りの積がすべて $\\sigma_i\\sigma_j=\\delta_{ij}I+i\\varepsilon_{ijk}\\sigma_k$ になることを確かめます（ノートの Part IV §5 の表）。"""),

code('''def eps(i: int, j: int, k: int) -> int:
    """レヴィ＝チヴィタ記号（x, y, z を 0, 1, 2 とする）。置換行列の行列式が置換の符号"""
    if len({i, j, k}) < 3:
        return 0
    return int(round(np.linalg.det(np.eye(3)[[i, j, k]])))


def label(M: Matrix) -> str:
    """行列を I, ±iσk のどれかの名前で表す（積の表の表示用）"""
    if np.allclose(M, I2):
        return "I".center(6)
    for k in range(3):
        for c, s in [(1j, "+iσ"), (-1j, "-iσ")]:
            if np.allclose(M, c * S[k]):
                return f"{s}{NAMES[k]}".center(6)
    return "?".center(6)


print("σiσj |" + "".join(f"σ{n}".center(6) for n in NAMES))
for i in range(3):
    row = []
    for j in range(3):
        P = S[i] @ S[j]
        formula = (i == j) * I2 + 1j * sum(eps(i, j, k) * S[k] for k in range(3))
        assert np.allclose(P, formula)
        row.append(label(P))
    print(f" σ{NAMES[i]}  |" + "".join(row))

for i in range(3):
    for j in range(3):
        comm = S[i] @ S[j] - S[j] @ S[i]
        anti = S[i] @ S[j] + S[j] @ S[i]
        assert np.allclose(comm, 2j * sum(eps(i, j, k) * S[k] for k in range(3)))   # [σi, σj] = 2i ε σk
        assert np.allclose(anti, 2 * (i == j) * I2)                                # {σi, σj} = 2δ I
print("\\n積の表、交換関係、反交換関係を確認しました")'''),

md("""## 3. ベクトルとの積：内積と外積

$\\vec a\\cdot\\vec\\sigma=a_x\\sigma_x+a_y\\sigma_y+a_z\\sigma_z$ と書きます。まず、ランダムなベクトルで公式と系（2乗・交換子・反交換子）を確かめます。"""),

code('''def dot_sigma(v: Vector) -> Matrix:
    return v[0] * sx + v[1] * sy + v[2] * sz


def coefficients(M: Matrix) -> NDArray[np.complex128]:
    """2×2 行列を I, σx, σy, σz で展開した係数（ノートの Part II §5：½tr で取り出す）"""
    return np.array([np.trace(M) / 2] + [np.trace(Sk @ M) / 2 for Sk in S])


rng = np.random.default_rng(1)
for _ in range(100):
    a, b = rng.normal(size=3), rng.normal(size=3)
    A, B = dot_sigma(a), dot_sigma(b)
    assert np.allclose(A @ B, np.dot(a, b) * I2 + 1j * dot_sigma(np.cross(a, b)))   # 公式
    assert np.allclose(A @ A, np.dot(a, a) * I2)                                   # (a·σ)² = |a|² I
    assert np.allclose(A @ B - B @ A, 2j * dot_sigma(np.cross(a, b)))               # 交換子は外積
    assert np.allclose(A @ B + B @ A, 2 * np.dot(a, b) * I2)                        # 反交換子は内積
c = coefficients(A @ B)
print("最後の例：I の係数", np.round(c[0], 4), " a·b =", round(np.dot(a, b), 4))
print("          σ の係数の虚部", np.round(c[1:].imag, 4), " a×b =", np.round(np.cross(a, b), 4), "（実部は", np.round(c[1:].real, 12), "）")'''),

md("""### スライダーで $\\vec b$ を動かす

$\\vec a=\\hat x$（青）を固定し、$\\vec b$（橙）の向きをスライダーで変えます。左の図に $\\vec a\\times\\vec b$（赤）、右の図に積 $(\\vec a\\cdot\\vec\\sigma)(\\vec b\\cdot\\vec\\sigma)$ を行列として計算し、$\\frac12\\operatorname{tr}$ で取り出した係数を描きます。黒い横線は、公式から計算した $\\vec a\\cdot\\vec b$ と $\\vec a\\times\\vec b$ の成分です。"""),

code('''a: Vector = np.array([1.0, 0.0, 0.0])


def vec_b(theta_deg: float, phi_deg: float) -> Vector:
    t, p = np.radians(theta_deg), np.radians(phi_deg)
    return np.array([np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t)])


def arrow3d(v: Vector, color: str, name: str) -> go.Scatter3d:
    return go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines+markers", name=name,
                        line=dict(color=color, width=7), marker=dict(size=[0, 5], color=color))


fig = go.FigureWidget(make_subplots(rows=1, cols=2, specs=[[{"type": "scene"}, {"type": "xy"}]],
                                    column_widths=[0.55, 0.45], subplot_titles=("ベクトル", "積の係数（½tr で取り出す）")))
fig.add_trace(arrow3d(a, "#1f77b4", "a"), 1, 1)
fig.add_trace(arrow3d(a, "#e67e00", "b"), 1, 1)
fig.add_trace(arrow3d(a, "#d62728", "a×b"), 1, 1)
fig.add_trace(go.Bar(x=["I（実部）", "σx（虚部）", "σy（虚部）", "σz（虚部）"], y=[0, 0, 0, 0],
                     marker_color=["#1f77b4", "#d62728", "#d62728", "#d62728"], name="係数"), 1, 2)
fig.add_trace(go.Scatter(x=["I（実部）", "σx（虚部）", "σy（虚部）", "σz（虚部）"], y=[0, 0, 0, 0], mode="markers",
                         marker=dict(symbol="line-ew", size=40, line=dict(width=3, color="black")), name="公式"), 1, 2)
fig.update_layout(height=480, width=900, margin=dict(l=10, r=10, t=40, b=10),
                  scene=dict(xaxis=dict(range=[-1, 1]), yaxis=dict(range=[-1, 1]), zaxis=dict(range=[-1, 1]), aspectmode="cube",
                             camera=dict(eye=dict(x=1.5, y=-1.4, z=0.8))),
                  yaxis=dict(range=[-1.1, 1.1]))

theta_b = W.FloatSlider(value=60, min=0, max=180, step=5, description="b の θ")
phi_b = W.FloatSlider(value=40, min=-180, max=180, step=5, description="b の φ")
info = W.HTML()


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、図と文字の表示を描き直す"""
    b = vec_b(theta_b.value, phi_b.value)
    cr = np.cross(a, b)
    c = coefficients(dot_sigma(a) @ dot_sigma(b))
    assert np.isclose(c[0], np.dot(a, b)) and np.allclose(c[1:], 1j * cr)
    with fig.batch_update():
        for k, v in [(1, b), (2, cr)]:
            fig.data[k].x, fig.data[k].y, fig.data[k].z = [0, v[0]], [0, v[1]], [0, v[2]]
        fig.data[3].y = [c[0].real, *c[1:].imag]
        fig.data[4].y = [np.dot(a, b), *cr]
    info.value = (f"a·b = {np.dot(a, b):+.3f}、a×b = ({cr[0]:+.3f}, {cr[1]:+.3f}, {cr[2]:+.3f})　"
                  f"→ b が a に平行なら外積が 0、垂直なら内積が 0")


theta_b.observe(update, "value")
phi_b.observe(update, "value")
update()
W.VBox([W.HBox([theta_b, phi_b]), info, fig])'''),

md("""## 4. 任意の $2\\times2$ 行列の展開と、Qiskit での答え合わせ

ランダムな複素行列 $M$ を、$\\frac12\\operatorname{tr}$ で $\\{I,\\sigma_x,\\sigma_y,\\sigma_z\\}$ に展開して元に戻ることを確かめ、Qiskit の `SparsePauliOp.from_operator` が同じ係数を返すことを確かめます。ノートの Part II §4 の例 $M=\\begin{pmatrix}1&2-i\\\\2+i&-1\\end{pmatrix}=2\\sigma_x+\\sigma_y+\\sigma_z$ も確かめます。"""),

code('''from qiskit.quantum_info import Operator, Pauli, SparsePauliOp

examples = {"ランダムな複素行列": rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)),
            "ノートの例": np.array([[1, 2 - 1j], [2 + 1j, -1]])}
for title, M in examples.items():
    c = coefficients(M)
    assert np.allclose(c[0] * I2 + sum(ck * Sk for ck, Sk in zip(c[1:], S)), M)     # 元に戻る
    op = SparsePauliOp.from_operator(Operator(M))
    qiskit_coef = dict(zip(op.paulis.to_labels(), op.coeffs))
    for k, label_ in enumerate("IXYZ"):
        assert np.isclose(qiskit_coef.get(label_, 0), c[k])
    print(f"{title}：自前の係数 {np.round(c, 4)}")
    print(f"{' ' * len(title)}  Qiskit     {op}\\n")'''),

md("""## 5. Qiskit の `Pauli` で答え合わせ（積の順序に注意）

Qiskit の `Pauli` オブジェクトは、位相（$\\pm1,\\pm i$）まで込めてパウリ行列を扱います。行列が自前の定義と一致すること、積と交換関係が同じになることを確かめます。

**注意**：`P.dot(Q)`（と `P @ Q`）は行列の積 $PQ$ ですが、`P.compose(Q)` は「$P$ を作用させてから $Q$ を作用させる」という意味で、行列としては $QP$ です。"""),

code('''PX, PY, PZ = Pauli("X"), Pauli("Y"), Pauli("Z")
for P, M in zip((PX, PY, PZ), S):
    assert np.allclose(P.to_matrix(), M)

print("X.dot(Y)     =", PX.dot(PY), "  （行列の積 σxσy = iσz）")
print("X @ Y        =", PX @ PY)
print("X.compose(Y) =", PX.compose(PY), "  （作用の順：X の次に Y、つまり σyσx = −iσz）")
assert np.allclose(PX.dot(PY).to_matrix(), sx @ sy)
assert np.allclose(PX.compose(PY).to_matrix(), sy @ sx)
assert PX.dot(PY) == Pauli("iZ")

print("\\nX と Y は交換する？", PX.commutes(PY), "／反交換する？", PX.anticommutes(PY))
assert PX.anticommutes(PY) and PX.commutes(PX)'''),

md("""## 観察のポイント

- パウリ行列は「発明された行列」ではなく、トレースゼロのエルミート行列の一般形から、係数を1つずつ取り出しただけのものです（最初のセル）。
- 積の表は、$x\\to y\\to z\\to x$ の向きに掛けると $+i$、逆向きなら $-i$ で、その符号が $\\varepsilon_{ijk}$ です。
- スライダーで $\\vec b$ を $\\vec a$ に平行にすると、積は $(\\vec a\\cdot\\vec b)I$ だけになり（外積が $0$）、垂直にすると $i(\\vec a\\times\\vec b)\\cdot\\vec\\sigma$ だけになります（内積が $0$）。
- Qiskit の `compose` は作用の順で、行列の積とは逆順です。Phase 2 で回路を組むときに、つまずきやすいところです。

**次に試すこと**：`traceless_hermitian` の代わりに、右上の成分の虚部を $n_y$ とする定義（$\\sigma_y$ の符号が逆）にすると、どのセルの `assert` が止まるでしょうか（ノートの Part II §3 の「$\\sigma_y$ の符号について」）。

**次のノートブック**：[02_bloch_sphere.ipynb](02_bloch_sphere.ipynb) で、$\\hat n\\cdot\\vec\\sigma$ の固有ベクトルとブロッホ球を扱います。"""),
]

# ============================================================================================ 02
nb2 = [
md("""# NB-01-2 ブロッホ球：量子ビットの状態を球面上の点として見る

[パウリ行列のノート](NOTE_P6)の Part VI（$\\hat n\\cdot\\vec\\sigma$ の固有ベクトルとブロッホ球）を、数値計算とスライダーで確かめます。Qiskit の `Statevector` と `DensityMatrix` でも答え合わせをします（量子回路は使いません。回路は Phase 2 の NB-07 で扱います）。

**確かめること**

1. $|{+}\\hat n\\rangle=\\cos\\frac\\theta2|0\\rangle+e^{i\\phi}\\sin\\frac\\theta2|1\\rangle$ は $\\hat n\\cdot\\vec\\sigma$ の固有値 $+1$ の固有ベクトルで、どの状態も（大域位相を除いて）この形になる（Part VI §2・§3）
2. パウリ行列の期待値は $\\hat n$、射影は $\\frac12(I+\\hat n\\cdot\\vec\\sigma)$（§4）
3. 重なり $|\\langle{+}\\hat m|{+}\\hat n\\rangle|^2=\\frac12(1+\\hat m\\cdot\\hat n)$、つまり直交する状態は対蹠点（§5）
4. 測定の確率 $P(0)=\\cos^2\\frac\\theta2$ を、Qiskit のサンプリングで確かめる
5. 混合状態はブロッホ球の内側にあり、純度は $\\frac12(1+|\\vec r|^2)$（§6）

**使い方**：上から順に実行します。3次元の図は、マウスのドラッグで回転、ホイールで拡大できます。""".replace("NOTE_P6", NOTE + "#p6")),

code('''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from numpy.typing import NDArray
from plotly.basedatatypes import BaseTraceType
from qiskit.quantum_info import DensityMatrix, Pauli, Statevector

# 型の別名（型ヒントを読みやすくするため。実行時には何も確かめない）
Matrix = NDArray[np.complex128]   # 2×2 の複素行列（演算子・密度行列）
Ket = NDArray[np.complex128]      # 長さ 2 の複素ベクトル（状態ベクトル）
Vector = NDArray[np.float64]      # 3次元の実ベクトル（ブロッホベクトル）

sx: Matrix = np.array([[0, 1], [1, 0]], dtype=complex)
sy: Matrix = np.array([[0, -1j], [1j, 0]])
sz: Matrix = np.array([[1, 0], [0, -1]], dtype=complex)
S: tuple[Matrix, Matrix, Matrix] = (sx, sy, sz)
I2: Matrix = np.eye(2, dtype=complex)


def nvec(theta: float, phi: float) -> Vector:
    """球座標の単位ベクトル（θ：北極からの角度、φ：経度。ラジアン）"""
    return np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])


def ket(theta: float, phi: float) -> Ket:
    """ノートの Part VI §2：n·σ の固有値 +1 の固有ベクトル"""
    return np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])


def bloch(psi_or_rho: Ket | Matrix) -> Vector:
    """ブロッホベクトル（⟨σx⟩, ⟨σy⟩, ⟨σz⟩）。状態ベクトルでも密度行列でもよい"""
    rho = psi_or_rho if np.ndim(psi_or_rho) == 2 else np.outer(psi_or_rho, psi_or_rho.conj())
    return np.array([np.trace(rho @ Sk).real for Sk in S])


def angles(psi: Ket) -> tuple[float, float]:
    """大域位相をそろえて（α を 0 以上の実数にして）、(θ, φ) を求める（Part VI §3）"""
    psi = psi / np.linalg.norm(psi)
    psi = psi * np.exp(-1j * np.angle(psi[0])) if abs(psi[0]) > 1e-12 else psi * np.exp(-1j * np.angle(psi[1]))
    return 2 * np.arccos(np.clip(psi[0].real, -1, 1)), np.angle(psi[1])'''),

md("""## 1. 数値で確認する

ランダムな状態で、Part VI の式をまとめて確かめます。Qiskit の `Statevector.expectation_value` が返す期待値も、自前の計算と比べます。"""),

code('''rng = np.random.default_rng(0)
for _ in range(200):
    th, ph = rng.uniform(0, np.pi), rng.uniform(-np.pi, np.pi)
    n, v = nvec(th, ph), ket(th, ph)
    N = n[0] * sx + n[1] * sy + n[2] * sz
    assert np.allclose(N @ v, v)                                                    # 固有値 +1 の固有ベクトル
    assert np.allclose(bloch(v), n)                                                 # ⟨σ⟩ = n
    assert np.allclose(np.outer(v, v.conj()), 0.5 * (I2 + N))                       # 射影 ½(I + n·σ)
    sv = Statevector(v)
    assert np.allclose([sv.expectation_value(Pauli(p)).real for p in "XYZ"], n)     # Qiskit とも一致
    # どの状態も、大域位相を除いて ket(θ, φ)
    psi = rng.normal(size=2) + 1j * rng.normal(size=2)
    t2, p2 = angles(psi)
    assert np.isclose(abs(np.vdot(ket(t2, p2), psi / np.linalg.norm(psi))), 1)
    # 重なり ½(1 + m·n)、軸 m で測って +1 が出る確率も同じ式
    m = nvec(t2, p2)
    assert np.isclose(abs(np.vdot(ket(t2, p2), v)) ** 2, 0.5 * (1 + m @ n))
    Pm = 0.5 * (I2 + m[0] * sx + m[1] * sy + m[2] * sz)
    assert np.isclose(np.vdot(v, Pm @ v).real, 0.5 * (1 + m @ n))
print("Part VI の式を、ランダムな 200 個の状態で確認しました")
print("例：θ = 60°, φ = 45° の状態", np.round(ket(np.pi / 3, np.pi / 4), 4), "のブロッホベクトル", np.round(bloch(ket(np.pi / 3, np.pi / 4)), 4))'''),

md("""## 2. スライダーで状態を動かす

- **θ, φ**：状態 $\\cos\\frac\\theta2|0\\rangle+e^{i\\phi}\\sin\\frac\\theta2|1\\rangle$ を決めます。赤い矢印がブロッホベクトル $\\hat n$、灰色の点が直交する状態（対蹠点）です。
- **大域位相 γ**：状態全体に $e^{i\\gamma}$ を掛けます。振幅（下の表示）は変わりますが、ブロッホ球の点は動きません。大域位相は観測できない、ということです（Part VI §3）。"""),

code('''# 注意：FigureWidget（スライダーで描き直す図）には、numpy 配列ではなく Python のリストを渡す。
# numpy 配列を渡すと、ブラウザから戻ってくる差分の処理で
# 「ValueError: The truth value of an array ... is ambiguous」になることがある（plotly 7.1 の FigureWidget）。
def sphere_traces() -> list[BaseTraceType]:
    u, w = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 60))
    tr = [go.Surface(x=(np.sin(u) * np.cos(w)).tolist(), y=(np.sin(u) * np.sin(w)).tolist(), z=np.cos(u).tolist(), opacity=0.12, showscale=False,
                     colorscale=[[0, "#9ecae1"], [1, "#9ecae1"]], hoverinfo="skip")]
    t = np.linspace(0, 2 * np.pi, 200)
    tr.append(go.Scatter3d(x=np.cos(t).tolist(), y=np.sin(t).tolist(), z=(0 * t).tolist(), mode="lines", line=dict(color="#bbb"), hoverinfo="skip", showlegend=False))
    for e in np.eye(3):
        tr.append(go.Scatter3d(x=[-1.25 * e[0], 1.25 * e[0]], y=[-1.25 * e[1], 1.25 * e[1]], z=[-1.25 * e[2], 1.25 * e[2]],
                               mode="lines", line=dict(color="#ccc"), hoverinfo="skip", showlegend=False))
    names = {(0, 0, 1): "|0⟩", (0, 0, -1): "|1⟩", (1, 0, 0): "|+⟩", (-1, 0, 0): "|−⟩", (0, 1, 0): "|+i⟩", (0, -1, 0): "|−i⟩"}
    pts = np.array(list(names))
    tr.append(go.Scatter3d(x=(1.12 * pts[:, 0]).tolist(), y=(1.12 * pts[:, 1]).tolist(), z=(1.12 * pts[:, 2]).tolist(), mode="text", text=list(names.values()),
                           textfont=dict(size=14, color="#1f77b4"), hoverinfo="skip", showlegend=False))
    return tr


def scene_layout() -> dict[str, object]:
    ax = dict(range=[-1.3, 1.3], showbackground=False, showticklabels=False, title="")
    return dict(xaxis=ax, yaxis=ax, zaxis=ax, aspectmode="cube", camera=dict(eye=dict(x=1.3, y=-1.5, z=0.6)))


fig = go.FigureWidget(data=sphere_traces())
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], mode="lines+markers", line=dict(color="#d62728", width=8),
                           marker=dict(size=[0, 6], color="#d62728"), name="ブロッホベクトル n"))
fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[-1], mode="markers", marker=dict(size=6, color="#777"), name="直交する状態（−n）"))
fig.add_trace(go.Scatter3d(x=[0, 0, 0], y=[0, 0, 0], z=[0, 0, 0], mode="lines", line=dict(color="#d62728", dash="dot", width=3),
                           showlegend=False, hoverinfo="skip"))
fig.update_layout(height=560, width=640, margin=dict(l=0, r=0, t=10, b=0), scene=scene_layout(), legend=dict(y=0.02))

theta = W.FloatSlider(value=60, min=0, max=180, step=1, description="θ [度]")
phi = W.FloatSlider(value=45, min=-180, max=180, step=1, description="φ [度]")
gamma = W.FloatSlider(value=0, min=0, max=360, step=5, description="大域位相 γ")
info = W.HTML()


def fmt(z: complex) -> str:
    return f"{z.real:+.3f}{z.imag:+.3f}i"


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、図と文字の表示を描き直す"""
    th, ph, ga = np.radians(theta.value), np.radians(phi.value), np.radians(gamma.value)
    psi = np.exp(1j * ga) * ket(th, ph)
    n = bloch(psi)
    assert np.allclose(n, nvec(th, ph))                                     # 大域位相によらない
    with fig.batch_update():
        arrow, anti, proj = fig.data[-3], fig.data[-2], fig.data[-1]
        arrow.x, arrow.y, arrow.z = [0, n[0]], [0, n[1]], [0, n[2]]
        anti.x, anti.y, anti.z = [-n[0]], [-n[1]], [-n[2]]
        proj.x, proj.y, proj.z = [0, n[0], n[0]], [0, n[1], n[1]], [0, 0, n[2]]
    p0 = abs(psi[0]) ** 2
    info.value = (f"<b>状態</b> α|0⟩ + β|1⟩：α = {fmt(psi[0])}、β = {fmt(psi[1])}<br>"
                  f"<b>測定の確率</b> P(0) = |α|² = {p0:.3f}（= cos²(θ/2)）、P(1) = {1 - p0:.3f}<br>"
                  f"<b>期待値</b> (⟨σx⟩, ⟨σy⟩, ⟨σz⟩) = ({n[0]:+.3f}, {n[1]:+.3f}, {n[2]:+.3f}) = n")


for s in (theta, phi, gamma):
    s.observe(update, "value")
update()
W.VBox([W.HBox([theta, phi, gamma]), info, fig])'''),

md("""## 3. 測定をサンプリングで確かめる

状態 $|{+}\\hat n\\rangle$ で $\\sigma_z$ を測ると、$|0\\rangle$（$+1$）が出る確率は $\\cos^2\\frac\\theta2$ です（Part VI §5）。Qiskit の `Statevector.sample_counts` で、各 $\\theta$ について 400 回ずつ測定をサンプリングし、出た割合を理論の曲線と比べます（量子回路は使わず、状態ベクトルから直接サンプリングします）。"""),

code('''shots = 400
thetas: Vector = np.radians(np.arange(0, 181, 10))
freq: list[float] = []
for k, th in enumerate(thetas):
    sv = Statevector(ket(th, 0.3))
    sv.seed(100 + k)                                   # 再現できるように乱数の種を固定
    counts = sv.sample_counts(shots)
    freq.append(counts.get("0", 0) / shots)
    assert np.isclose(sv.probabilities()[0], np.cos(th / 2) ** 2)
freq = np.array(freq)
assert np.all(np.abs(freq - np.cos(thetas / 2) ** 2) < 4 * np.sqrt(0.25 / shots))     # 統計誤差（4σ）の範囲

tt = np.linspace(0, np.pi, 200)
fig_m = go.Figure([go.Scatter(x=np.degrees(tt), y=np.cos(tt / 2) ** 2, mode="lines", name="理論 cos²(θ/2)"),
                   go.Scatter(x=np.degrees(thetas), y=freq, mode="markers", marker=dict(size=9, color="#d62728"),
                              name=f"サンプリング（{shots} 回ずつ）")])
fig_m.update_layout(height=380, width=700, xaxis_title="θ [度]", yaxis_title="|0⟩ が出た割合", margin=dict(t=20))
fig_m'''),

md("""## 4. 混合状態：ブロッホ球の内側

2つの純粋状態 $\\hat n_1$（北極 $|0\\rangle$）と $\\hat n_2$ を、確率 $p$ と $1-p$ で混ぜた密度行列 $\\rho=p|\\psi_1\\rangle\\langle\\psi_1|+(1-p)|\\psi_2\\rangle\\langle\\psi_2|$ のブロッホベクトルは、$\\vec r=p\\,\\hat n_1+(1-p)\\,\\hat n_2$ です（2点を結ぶ線分の上）。

- **p**：混ぜる割合
- **Θ**：$\\hat n_1$ と $\\hat n_2$ のなす角。$\\Theta=180^\\circ$（直交する状態）で $p=0.5$ にすると、球の中心（完全な混合状態 $\\rho=I/2$）になります。

純度は Qiskit の `DensityMatrix.purity()` でも計算して、$\\frac12(1+|\\vec r|^2)$ と比べます。"""),

code('''fig_r = go.FigureWidget(data=sphere_traces())
fig_r.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[1, -1], mode="lines+markers", line=dict(color="#e67e00", dash="dash", width=4),
                             marker=dict(size=5, color="#e67e00"), name="混ぜる2つの純粋状態"))
fig_r.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 0.4], mode="lines+markers", line=dict(color="#d62728", width=8),
                             marker=dict(size=[0, 7], color="#d62728"), name="ブロッホベクトル r"))
fig_r.update_layout(height=520, width=600, margin=dict(l=0, r=0, t=10, b=0), scene=scene_layout(), legend=dict(y=0.02))

p_slider = W.FloatSlider(value=0.7, min=0, max=1, step=0.05, description="p")
Th_slider = W.FloatSlider(value=180, min=0, max=180, step=5, description="Θ [度]")
info_r = W.HTML()


def update_r(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、図と文字の表示を描き直す"""
    p, Th = p_slider.value, np.radians(Th_slider.value)
    n1, n2 = nvec(0, 0), nvec(Th, 0)
    v1, v2 = ket(0, 0), ket(Th, 0)
    rho = p * np.outer(v1, v1.conj()) + (1 - p) * np.outer(v2, v2.conj())
    r = bloch(rho)
    assert np.allclose(r, p * n1 + (1 - p) * n2)
    R = np.linalg.norm(r)
    purity = np.trace(rho @ rho).real
    assert np.isclose(purity, 0.5 * (1 + R**2)) and np.isclose(DensityMatrix(rho).purity().real, purity)
    lam = np.linalg.eigvalsh(rho)
    assert np.allclose(sorted(lam), [(1 - R) / 2, (1 + R) / 2])
    with fig_r.batch_update():
        pair, arrow = fig_r.data[-2], fig_r.data[-1]
        pair.x, pair.y, pair.z = [n1[0], n2[0]], [n1[1], n2[1]], [n1[2], n2[2]]
        arrow.x, arrow.y, arrow.z = [0, r[0]], [0, r[1]], [0, r[2]]
    info_r.value = (f"|r| = {R:.3f}、純度 tr ρ² = {purity:.3f}（= (1+|r|²)/2、Qiskit の purity() とも一致）、"
                    f"固有値 = ({lam[0]:.3f}, {lam[1]:.3f}) = (1 ∓ |r|)/2")


for s in (p_slider, Th_slider):
    s.observe(update_r, "value")
update_r()
W.VBox([W.HBox([p_slider, Th_slider]), info_r, fig_r])'''),

md("""## 5. Qiskit の描画と比べる

θ = 60°、φ = 90° の状態を、Qiskit の `plot_bloch_multivector`（状態ベクトルから）と `plot_bloch_vector`（ブロッホベクトルから）で描きます。上のスライダーの図で θ = 60°、φ = 90° にしたときと同じ点になっていることを確かめてください（Qiskit の図は、$x$ 軸が手前、$y$ 軸が右向きです）。"""),

code('''import matplotlib.pyplot as plt
from qiskit.visualization import plot_bloch_multivector, plot_bloch_vector

plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]   # 図のタイトルの日本語用（Windows のフォント）

th, ph = np.radians(60), np.radians(90)
sv = Statevector(ket(th, ph))
display(plot_bloch_multivector(sv, title="θ = 60°, φ = 90°（状態ベクトルから）"))
display(plot_bloch_vector(list(bloch(ket(th, ph))), title="同じ点（ブロッホベクトルから）"))'''),

md("""## 観察のポイント

- θ を 0 から 180° まで動かすと、状態は $|0\\rangle$ から $|1\\rangle$ まで変わり、$P(0)=\\cos^2\\frac\\theta2$ が 1 から 0 まで減ります。ブロッホ球の角度 θ に対して、状態の振幅には半分の角度 θ/2 が現れます（Part VI §5）。
- 北極・南極では、φ を動かしても点が動きません。極は座標特異点です（Part VI §3 の補足）。
- 大域位相 γ を動かしても、ブロッホ球の点も測定の確率も変わりません。
- 混合状態のブロッホベクトルは、混ぜた純粋状態を結ぶ線分の上にあり、球の内側に入ります。純粋状態だけが球面上にあります。

**次に試すこと**：混合状態のセルで、Θ = 90°（たとえば $|0\\rangle$ と $|{+}\\rangle$）にすると、$p$ をどう選んでも球の中心には届きません。中心に届くのは、どんな2状態を混ぜたときでしょうか。

**次のノートブック（NB-02）**：[../02_su2_rotation/01_su2_exponential.ipynb](../02_su2_rotation/01_su2_exponential.ipynb) と [02_bloch_rotation.ipynb](../02_su2_rotation/02_bloch_rotation.ipynb) で、$e^{-i\\theta\\,\\hat n\\cdot\\vec\\sigma/2}$ でブロッホベクトルが回る様子（ノートの Part VII）を扱います。"""),
]

save("01_pauli_algebra.ipynb", nb1)
save("02_bloch_sphere.ipynb", nb2)
