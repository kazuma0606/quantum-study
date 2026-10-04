"""notebooks/foundations/00_taylor_series の3冊のノートブックを生成する。"""
import re
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path("notebooks/foundations/00_taylor_series")
OUT.mkdir(parents=True, exist_ok=True)
R = "../../../研究ノート/"
LINKS = {
    "FLMNOTE": R + "01_基礎・ベクトル解析/functions_linear_maps_derivatives_integrals.md",
    "CPLXNOTE": R + "04_群論・代数/complex_numbers_geometry.md",
    "DETNOTE": R + "04_群論・代数/det_exp_trace_proof.md",
    "MANINOTE": R + "03_多様体・微分形式・トポロジー/manifolds_introduction.md",
    "LEANDET": "../../../lean4/QuantumStudy/DetExpTrace.lean",
    "LEANSCHUR": "../../../lean4/QuantumStudy/Schur.lean",
    "CHAOSNB": "../../learning/14_chaos/02_lorenz.ipynb",
    "NB02": "../../02_su2_rotation/02_bloch_rotation.ipynb",
    "PAULINOTE": R + "04_群論・代数/pauli_matrices_derivation_and_group.md",
    "LEANPAULI": "../../../lean4/QuantumStudy/Pauli.lean",
    "PSNOTE": R + "01_基礎・ベクトル解析/power_series_radius_of_convergence.md",
    "MEXPNOTE": R + "04_群論・代数/matrix_exponential_commutator_bch_trotter.md",
}


def save(name, cells):
    for i, cell in enumerate(cells):
        cell.id = f"{Path(name).stem[:2]}-{i:02d}"   # 作り直しても差分が出ないよう、セルの ID を固定する
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nbformat.write(nb, OUT / name)
    print("書き出し:", OUT / name)


def md(text):
    for k, v in LINKS.items():
        text = text.replace(k, v)
    return new_markdown_cell(text)


def code(src):
    # plotly の凡例・軸ラベルは TeX の波かっこを表示できないので、e^{…} を e^(…) と書く
    return new_code_cell(re.sub(r"e\^\{([^}]*)\}", r"e^(\1)", src))

HEADER = r'''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from math import factorial
from numpy.typing import NDArray
from plotly.subplots import make_subplots

Floats = NDArray[np.float64]       # 実数の配列（型ヒント用の別名）
Complexes = NDArray[np.complex128]
# 注意：FigureWidget（スライダーで描き直す図）には、numpy 配列ではなくリストを渡す（NB-02 を参照）'''

# ============================================================================================ 01
nb1 = [
md(r"""# テイラー展開 1：多項式で関数を近似する ―オイラーの公式まで

関数 $f$ を、点 $0$ のまわりで多項式

$$
f(x)=f(0)+f'(0)\,x+\frac{f''(0)}{2!}x^2+\frac{f'''(0)}{3!}x^3+\cdots=\sum_{k=0}^\infty\frac{f^{(k)}(0)}{k!}x^k
$$

で表すのが**マクローリン展開**（点 $a$ のまわりなら**テイラー展開**）です。このノートブックでは、

1. 次数を上げると近似が広がる様子（スライダー）
2. 近似がどこまでも広がるとは限らない例（収束半径）
3. 誤差の大きさ
4. **オイラーの公式** $e^{i\theta}=\cos\theta+i\sin\theta$ と $e^{i\pi}=-1$ を、級数から導く
5. テイラー展開できない「なめらかな関数」
6. 級数をそのまま足すと、丸め誤差で答えが崩れる例

を、計算して見ます。次のノートブックでは、同じ級数の $x$ に**行列**を入れます。"""),

code(HEADER),

md(r"""## 1. 次数を上げると、近似が広がる

よく使う関数のマクローリン展開です。

$$
e^x=\sum_{k\ge0}\frac{x^k}{k!},\qquad \sin x=\sum_{k\ge0}\frac{(-1)^kx^{2k+1}}{(2k+1)!},\qquad \cos x=\sum_{k\ge0}\frac{(-1)^kx^{2k}}{(2k)!}
$$

$$
\ln(1+x)=\sum_{k\ge1}\frac{(-1)^{k+1}x^k}{k},\qquad \frac1{1+x^2}=\sum_{k\ge0}(-1)^kx^{2k}
$$

関数と次数 $N$ を選び、$N$ 次までの部分和（青）が元の関数（灰色）にどう近づくかを見ます。"""),

code(r'''def series_terms(name: str, x: Floats, N: int) -> Floats:
    """N 次までの各項を並べた配列（行が項、列が x の点）"""
    terms = []
    for k in range(N + 1):
        if name == "exp":
            c = 1 / factorial(k)
        elif name == "sin":
            c = 0.0 if k % 2 == 0 else (-1) ** ((k - 1) // 2) / factorial(k)
        elif name == "cos":
            c = 0.0 if k % 2 == 1 else (-1) ** (k // 2) / factorial(k)
        elif name == "log1p":
            c = 0.0 if k == 0 else (-1) ** (k + 1) / k
        else:  # "rational" = 1/(1+x²)
            c = 0.0 if k % 2 == 1 else (-1) ** (k // 2)
        terms.append(c * x**k)
    return np.array(terms)


FUNCS = {"exp": ("e^x", np.exp), "sin": ("sin x", np.sin), "cos": ("cos x", np.cos),
         "log1p": ("ln(1+x)", np.log1p), "rational": ("1/(1+x²)", lambda x: 1 / (1 + x**2))}


def partial_sum(name: str, x: Floats, N: int) -> Floats:
    return series_terms(name, x, N).sum(axis=0)


assert abs(partial_sum("sin", np.array([1.0]), 15)[0] - np.sin(1.0)) < 1e-12
assert abs(partial_sum("exp", np.array([2.0]), 30)[0] - np.exp(2.0)) < 1e-12
assert abs(partial_sum("log1p", np.array([0.5]), 60)[0] - np.log1p(0.5)) < 1e-12

xs = np.linspace(-4, 4, 400)
fig_taylor = go.FigureWidget([go.Scatter(x=xs.tolist(), y=[], mode="lines", line=dict(color="#aaa", width=5), name="元の関数"),
                              go.Scatter(x=xs.tolist(), y=[], mode="lines", line=dict(color="#1f77b4", width=2), name="N 次までの部分和")])
fig_taylor.update_layout(height=420, width=820, margin=dict(t=20), yaxis=dict(range=[-3, 3]), xaxis_title="x")
func_dd = W.Dropdown(options=[(v[0], k) for k, v in FUNCS.items()], value="sin", description="関数")
N_slider = W.IntSlider(value=5, min=0, max=30, description="次数 N")
info = W.HTML()


def update(*_: object) -> None:
    """関数と次数が変わるたびに、部分和を描き直す"""
    name, N = func_dd.value, N_slider.value
    f = FUNCS[name][1]
    with np.errstate(invalid="ignore", divide="ignore"):
        exact = f(xs)
    approx = partial_sum(name, xs, N)
    with fig_taylor.batch_update():
        fig_taylor.data[0].y = np.where(np.isfinite(exact), np.clip(exact, -50, 50), np.nan).tolist()
        fig_taylor.data[1].y = np.clip(approx, -50, 50).tolist()
    ok = np.abs(approx - exact) < 0.01
    inside = xs[ok & np.isfinite(exact)]
    span = f"誤差 0.01 以内の範囲：x ≈ {inside.min():.2f} 〜 {inside.max():.2f}" if len(inside) else "誤差 0.01 以内の点なし"
    info.value = f"{FUNCS[name][0]} の {N} 次までの部分和：{span}"


for w in (func_dd, N_slider):
    w.observe(update, "value")
update()
W.VBox([W.HBox([func_dd, N_slider]), info, fig_taylor])'''),

md(r"""**考えてみよう**

- $e^x$、$\sin x$、$\cos x$ は、$N$ を上げるほど、近似できる範囲がどこまでも広がります。
- $\ln(1+x)$ と $1/(1+x^2)$ は、$N$ をいくら上げても、$|x|<1$ の外では近似が良くなりません（むしろ暴れます）。$1/(1+x^2)$ は実数全体でなめらかなのに、なぜでしょうか（次の節）。"""),

md(r"""## 2. 収束半径：近似が届く範囲には限りがある

$x=0.5$（内側）と $x=1.5$（外側）で、次数 $N$ を上げたときの誤差を比べます。"""),

code(r'''Ns = np.arange(1, 41)
fig = go.Figure()
for name in ("log1p", "rational"):
    for x0, dash in ((0.5, "solid"), (1.5, "dash")):
        err = [abs(partial_sum(name, np.array([x0]), int(N))[0] - FUNCS[name][1](np.array([x0]))[0]) for N in Ns]
        fig.add_trace(go.Scatter(x=Ns.tolist(), y=err, mode="lines", line=dict(dash=dash),
                                 name=f"{FUNCS[name][0]}、x = {x0}"))
fig.update_layout(height=380, width=800, yaxis_type="log", xaxis_title="次数 N", yaxis_title="誤差", margin=dict(t=20))

# 内側では誤差 → 0、外側では誤差が増える
assert abs(partial_sum("rational", np.array([0.5]), 40)[0] - 0.8) < 1e-10
assert abs(partial_sum("rational", np.array([1.5]), 40)[0]) > 1e6
fig'''),

md(r"""**理由（複素数の世界を見ると分かる）**：$1/(1+x^2)$ は、実数の範囲ではどこでもなめらかですが、$x$ を複素数 $z$ に広げると、$z=\pm i$ で分母が $0$ になります。マクローリン展開が届く範囲は、**複素平面で原点から一番近い「壊れる点」までの距離**（この場合 $|\pm i|=1$）で決まり、これを**収束半径**と呼びます。$\ln(1+x)$ も $x=-1$ で壊れるので、収束半径は $1$ です。$e^x,\sin x,\cos x$ はどこでも壊れないので、収束半径は無限大です。

実数だけを見ていては分からない理由が、複素数で見ると分かる。これは、学習ロードマップの候補17（複素解析）への入口です。収束半径の求め方、中心を変えると半径が変わること（中心 $1$ なら $\sqrt2$）、収束半径の外へ関数を延ばす解析接続（「$1+2+4+\cdots=-1$」「$1+2+3+\cdots=-\frac1{12}$」の意味）は、[べき級数と収束半径のノート](PSNOTE)の Part I〜III にまとめました。"""),

md(r"""## 3. 誤差の大きさ：ラグランジュの剰余項

$N$ 次で打ち切ったときの誤差は、$0$ と $x$ の間のある $\xi$ を使って

$$
R_N(x)=\frac{f^{(N+1)}(\xi)}{(N+1)!}\,x^{N+1}
$$

と書けます（**ラグランジュの剰余項**）。$e^x$ なら $f^{(N+1)}(\xi)=e^\xi\le e^{|x|}$ なので、誤差は $e^{|x|}\,\frac{|x|^{N+1}}{(N+1)!}$ 以下です。$(N+1)!$ は指数関数よりずっと速く大きくなるので、誤差はやがて急速に小さくなります。"""),

code(r'''x0 = 3.0
Ns = np.arange(0, 31)
err = np.array([abs(partial_sum("exp", np.array([x0]), int(N))[0] - np.exp(x0)) for N in Ns])
bound = np.array([np.exp(x0) * x0 ** (N + 1) / factorial(int(N) + 1) for N in Ns])
mask = err > 1e-12
assert np.all(err[mask] <= bound[mask] * (1 + 1e-9))       # 誤差は剰余項の上限以下
fig = go.Figure([go.Scatter(x=Ns.tolist(), y=err.tolist(), mode="lines+markers", name="実際の誤差（x = 3）"),
                 go.Scatter(x=Ns.tolist(), y=bound.tolist(), mode="lines", line=dict(dash="dash"), name="剰余項による上限")])
fig.update_layout(height=360, width=780, yaxis_type="log", xaxis_title="次数 N", yaxis_title="誤差", margin=dict(t=20))
fig'''),

md(r"""## 4. オイラーの公式：$e^{i\theta}=\cos\theta+i\sin\theta$

$e^x$ の級数の $x$ に $i\theta$ を入れます。$i^2=-1$、$i^3=-i$、$i^4=1$ と4つごとにくり返すので、項を実部と虚部に分けると

$$
e^{i\theta}=\Big(1-\frac{\theta^2}{2!}+\frac{\theta^4}{4!}-\cdots\Big)+i\Big(\theta-\frac{\theta^3}{3!}+\frac{\theta^5}{5!}-\cdots\Big)=\cos\theta+i\sin\theta
$$

で、実部が $\cos$ の級数、虚部が $\sin$ の級数そのものです。$\theta=\pi$ とすると $e^{i\pi}=\cos\pi+i\sin\pi=-1$ です。

下の図は、部分和 $S_N=\sum_{k=0}^{N}\frac{(i\theta)^k}{k!}$ を複素平面に描いたものです。項を1つ足すごとに $i$ 倍の向き（$90^\circ$ 回転）に進むので、部分和は渦を巻きながら $e^{i\theta}$（単位円の上の点）に近づきます。"""),

code(r'''def euler_partial_sums(theta: float, N: int) -> Complexes:
    terms = np.array([(1j * theta) ** k / factorial(k) for k in range(N + 1)])
    return np.cumsum(terms)


# 実部 = cos の級数、虚部 = sin の級数
for theta in (0.7, np.pi, 2.5):
    S = euler_partial_sums(theta, 40)[-1]
    assert np.isclose(S.real, partial_sum("cos", np.array([theta]), 40)[0])
    assert np.isclose(S.imag, partial_sum("sin", np.array([theta]), 40)[0])
    assert np.isclose(S, np.exp(1j * theta))
print("e^{iπ} の部分和（30 次）=", np.round(euler_partial_sums(np.pi, 30)[-1], 12))

t = np.linspace(0, 2 * np.pi, 200)
fig_euler = go.FigureWidget([go.Scatter(x=np.cos(t).tolist(), y=np.sin(t).tolist(), mode="lines", line=dict(color="#ccc"), name="単位円"),
                             go.Scatter(x=[], y=[], mode="lines+markers", line=dict(color="#1f77b4"), marker=dict(size=6), name="部分和 S₀, S₁, …"),
                             go.Scatter(x=[], y=[], mode="markers", marker=dict(size=14, color="#d62728", symbol="x"), name="e^{iθ}")])
fig_euler.update_layout(height=520, width=620, margin=dict(t=20), xaxis=dict(range=[-4, 2.5], title="実部"),
                        yaxis=dict(range=[-3, 3.5], scaleanchor="x", title="虚部"))
theta_s = W.FloatSlider(value=180, min=0, max=360, step=5, description="θ [度]")
N_s = W.IntSlider(value=8, min=0, max=30, description="次数 N")
info2 = W.HTML()


def update_euler(*_: object) -> None:
    """θ と次数が変わるたびに、部分和の道を描き直す"""
    theta, N = np.radians(theta_s.value), N_s.value
    S = euler_partial_sums(theta, N)
    target = np.exp(1j * theta)
    with fig_euler.batch_update():
        fig_euler.data[1].x, fig_euler.data[1].y = S.real.tolist(), S.imag.tolist()
        fig_euler.data[2].x, fig_euler.data[2].y = [float(target.real)], [float(target.imag)]
    info2.value = (f"S_{N} = {S[-1].real:+.6f} {S[-1].imag:+.6f} i、e^(iθ) = {target.real:+.6f} {target.imag:+.6f} i、"
                   f"差 = {abs(S[-1] - target):.2e}")


for w in (theta_s, N_s):
    w.observe(update_euler, "value")
update_euler()
W.VBox([W.HBox([theta_s, N_s]), info2, fig_euler])'''),

md(r"""**考えてみよう**

- $\theta=\pi$ で $N$ を上げていくと、部分和は $-1$ に近づきます。$N$ が小さいうちは単位円から大きく外れるのに、最後は円の上の点に収まります。
- $\theta$ を $0$ から動かすと、ゴール $e^{i\theta}$ は単位円の上を回ります。$e^{i\theta}$ は「回転」を表し、[複素数の幾何学のノート](CPLXNOTE)の Part II・IV で扱った「複素数の掛け算＝回転」とつながります。次のノートブックでは、これを行列で書きます。"""),

md(r"""## 5. テイラー展開できない「なめらかな関数」

$$
f(x)=\begin{cases}e^{-1/x^2}&(x\ne0)\\0&(x=0)\end{cases}
$$

は、何回でも微分できますが、$x=0$ での微分係数が**すべて $0$** です。そのため、マクローリン展開はすべての項が $0$ で、展開した級数は $0$ という関数になります。ところが $f(x)$ 自身は $x\neq0$ で $0$ ではありません。**「何回でも微分できる」だけでは、テイラー展開が元の関数に一致するとは限らない**という例です（一致する関数を**解析的**な関数と呼びます）。微分係数がすべて $0$ になることの証明と、複素数で見ると $z=0$ が激しい特異点になる理由は、[べき級数と収束半径のノート](PSNOTE)の Part IV にあります。"""),

code(r'''import sympy as sp

xsym = sp.symbols("x", real=True)
f = sp.exp(-1 / xsym**2)
for k in range(1, 5):
    dk = sp.diff(f, xsym, k)
    assert sp.limit(dk, xsym, 0) == 0                 # k 回微分の、x → 0 での極限は 0
print("1〜4 回微分の、x = 0 での値（極限）はすべて 0")

xs5 = np.linspace(-2, 2, 400)
with np.errstate(divide="ignore"):
    ys5 = np.where(xs5 == 0, 0.0, np.exp(-1 / xs5**2))
fig = go.Figure([go.Scatter(x=xs5.tolist(), y=ys5.tolist(), mode="lines", name="e^{−1/x²}"),
                 go.Scatter(x=xs5.tolist(), y=[0.0] * len(xs5), mode="lines", line=dict(dash="dash"), name="マクローリン展開（すべての項が 0）")])
fig.update_layout(height=340, width=760, xaxis_title="x", margin=dict(t=20))
fig'''),

md(r"""## 6. 丸め誤差：級数をそのまま足すと、答えが崩れる

$e^{-x}=\sum\frac{(-x)^k}{k!}$ を、$x=20$ でそのまま足してみます。正しい値は $e^{-20}\approx2.06\times10^{-9}$ です。"""),

code(r'''def exp_series_naive(x: float, N: int = 150) -> float:
    total, term = 0.0, 1.0
    for k in range(N):
        total += term
        term *= x / (k + 1)
    return total


rows = []
for x in (1, 5, 10, 15, 20, 25):
    naive = exp_series_naive(-x)                     # e^{−x} の級数をそのまま足す
    better = 1 / exp_series_naive(x)                 # e^{x} を足してから逆数を取る
    true = np.exp(-x)
    rows.append((x, true, naive, abs(naive - true) / true, abs(better - true) / true))
    print(f"x = {x:2d}：正しい値 {true:.3e}、そのまま {naive:+.3e}（相対誤差 {abs(naive - true) / true:.1e}）、"
          f"逆数 {better:.3e}（相対誤差 {abs(better - true) / true:.1e}）")
assert rows[4][3] > 0.1 and rows[4][4] < 1e-12       # x = 20：そのままでは崩れ、逆数なら正確

terms = np.array([20.0**k / factorial(k) for k in range(80)])
fig = make_subplots(rows=1, cols=2, subplot_titles=("x と相対誤差", "x = 20 の各項の大きさ |(−20)^k / k!|"))
X = [r[0] for r in rows]
fig.add_trace(go.Scatter(x=X, y=[r[3] for r in rows], mode="lines+markers", name="そのまま足す"), 1, 1)
fig.add_trace(go.Scatter(x=X, y=[max(r[4], 1e-17) for r in rows], mode="lines+markers", name="e^x を足して逆数（0 は 10⁻¹⁷ で表示）"), 1, 1)
fig.add_trace(go.Scatter(x=list(range(80)), y=terms.tolist(), mode="lines", name="各項の大きさ"), 1, 2)
fig.add_trace(go.Scatter(x=[0, 79], y=[np.exp(-20)] * 2, mode="lines", line=dict(dash="dot", color="#333"), name="答え e^{−20}"), 1, 2)
fig.update_yaxes(type="log")
fig.update_xaxes(title_text="x", row=1, col=1)
fig.update_xaxes(title_text="k", row=1, col=2)
fig.update_layout(height=380, width=950, margin=dict(t=40))
fig'''),

md(r"""**理由**：$x=20$ では、項の大きさが $k=20$ 付近で約 $4\times10^{7}$ まで大きくなり、正負が交互に打ち消し合って、最後に $2\times10^{-9}$ が残ります。コンピュータの数（倍精度）は、それぞれの数の約 $10^{-16}$ 倍の誤差を含むので、$4\times10^{7}$ の項の誤差は約 $4\times10^{-9}$ で、答えそのものより大きくなります（**桁落ち**）。$e^{20}$ を計算すると、項はすべて正で打ち消し合いが起きないので正確で、その逆数を取れば正しい値が得られます。

数学的に正しい式でも、計算の順序によって、数値は大きく狂うことがあります。カオスのノートブックで見た「丸め誤差が拡大する」話の、もっと身近な例です。

## 観察のポイント（まとめ）

- テイラー展開は「点のまわりの、多項式による近似」で、次数を上げると近似の範囲が広がる。ただし、届く範囲（収束半径）は、複素平面での一番近い特異点で決まる。
- $e^x$ の級数に $i\theta$ を入れると、実部と虚部がそれぞれ $\cos$ と $\sin$ の級数になり、オイラーの公式が出る。
- 何回でも微分できても、テイラー展開が元の関数に一致するとは限らない。
- 正しい級数でも、足し方によっては丸め誤差で崩れる。

**次のノートブック**：[02_matrix_exponential.ipynb](02_matrix_exponential.ipynb) で、級数の $x$ に行列を入れます。"""),
]

# ============================================================================================ 02
nb2 = [
md(r"""# テイラー展開 2：行列の指数関数

$e^x=\sum\frac{x^k}{k!}$ の $x$ に**正方行列** $A$ を入れたものが、行列の指数関数

$$
e^A=\sum_{k=0}^\infty\frac{A^k}{k!}=I+A+\frac{A^2}{2!}+\frac{A^3}{3!}+\cdots
$$

です（行列の掛け算と足し算だけで書けるので、そのまま意味を持ちます）。[関数・線形写像・微分・積分のノート](FLMNOTE)で扱い、パウリ行列・$SU(2)$ のノートで何度も使ってきました。このノートブックでは、

1. 級数の部分和が収束する様子
2. 行列版のオイラーの公式：$e^{\theta J}$ は回転行列
3. 挟み込み $Pe^AP^{-1}=e^{PAP^{-1}}$ と、対角化による計算
4. 微分は1次の近似：行列式の場合（$O(\varepsilon^2)$ の意味）
5. $\det(e^A)=e^{\operatorname{tr}A}$ と、Lean による証明
6. $e^{A+B}\ne e^Ae^B$（交換しないとき）
7. トロッター分解：量子コンピュータで時間発展を作る方法

を見ます。"""),

code(HEADER + r'''
from scipy.linalg import expm

Matrix = NDArray[np.complex128]    # 正方行列（型ヒント用の別名）


def exp_series(A: Matrix, N: int) -> Matrix:
    """N 次までの部分和 Σ_{k=0}^{N} A^k / k!"""
    total = np.zeros_like(A, dtype=complex)
    term = np.eye(A.shape[0], dtype=complex)
    for k in range(N + 1):
        total = total + term
        term = term @ A / (k + 1)
    return total'''),

md(r"""## 1. 部分和は収束する

ランダムな $3\times3$ 行列で、部分和と scipy の `expm`（行列の指数関数を精度よく計算する関数）の差を、次数 $N$ に対して描きます。行列の「大きさ」（ノルム）が大きいほど、収束に多くの項が必要です。"""),

code(r'''rng = np.random.default_rng(0)
A_small = rng.normal(size=(3, 3)) * 0.5
A_large = rng.normal(size=(3, 3)) * 3.0
Ns = np.arange(0, 61)
fig = go.Figure()
for A, label in ((A_small, "小さい行列（ノルム ≈ %.1f）" % np.linalg.norm(A_small, 2)),
                 (A_large, "大きい行列（ノルム ≈ %.1f）" % np.linalg.norm(A_large, 2))):
    err = [float(np.linalg.norm(exp_series(A, int(N)) - expm(A))) for N in Ns]
    fig.add_trace(go.Scatter(x=Ns.tolist(), y=err, mode="lines", name=label))
    assert np.allclose(exp_series(A, 60), expm(A))
fig.update_layout(height=360, width=780, yaxis_type="log", xaxis_title="次数 N", yaxis_title="expm との差", margin=dict(t=20))
fig'''),

md(r"""## 2. 行列版のオイラーの公式：$e^{\theta J}$ は回転行列

$J=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ は $J^2=-I$ を満たし、複素数の $i$ と同じ役割をします（[複素数の幾何学のノート](CPLXNOTE)の Part III・IV）。$e^x$ の級数で $x=\theta J$ とすると、$J^2=-I$ から偶数次と奇数次に分かれて

$$
e^{\theta J}=\cos\theta\,I+\sin\theta\,J=\begin{pmatrix}\cos\theta&-\sin\theta\\ \sin\theta&\cos\theta\end{pmatrix}
$$

と、**回転行列**になります。1冊目のオイラーの公式 $e^{i\theta}=\cos\theta+i\sin\theta$ の、行列版です。スライダーで $\theta$ を変え、級数で計算した $e^{\theta J}$ で正方形を回します。"""),

code(r'''J = np.array([[0, -1], [1, 0]], dtype=complex)
assert np.allclose(J @ J, -np.eye(2))
for theta in np.linspace(0, 2 * np.pi, 9):
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    assert np.allclose(exp_series(theta * J, 40), rot)

square = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=float).T
fig_rot = go.FigureWidget([go.Scatter(x=square[0].tolist(), y=square[1].tolist(), fill="toself", mode="lines",
                                      line=dict(color="#aaa"), name="元の正方形"),
                           go.Scatter(x=[], y=[], fill="toself", mode="lines", line=dict(color="#1f77b4"), name="e^{θJ} で回したもの")])
fig_rot.update_layout(height=460, width=520, margin=dict(t=20), xaxis=dict(range=[-1.6, 1.6]),
                      yaxis=dict(range=[-1.6, 1.6], scaleanchor="x"))
theta_r = W.FloatSlider(value=40, min=0, max=360, step=5, description="θ [度]")
N_r = W.IntSlider(value=3, min=0, max=20, description="次数 N")
info_r = W.HTML()


def update_rot(*_: object) -> None:
    """θ と次数が変わるたびに、部分和で回した正方形を描き直す"""
    theta, N = np.radians(theta_r.value), N_r.value
    M = exp_series(theta * J, N).real
    P = M @ square
    with fig_rot.batch_update():
        fig_rot.data[1].x, fig_rot.data[1].y = P[0].tolist(), P[1].tolist()
    info_r.value = (f"N = {N} 次までの部分和：det = {np.linalg.det(M):.4f}（回転なら 1）、"
                    f"回転行列との差 = {np.linalg.norm(M - expm(theta * J).real):.2e}")


for w in (theta_r, N_r):
    w.observe(update_rot, "value")
update_rot()
W.VBox([W.HBox([theta_r, N_r]), info_r, fig_rot])'''),

md(r"""**考えてみよう**：次数 $N$ が小さいと、正方形は回るだけでなく、伸びたり歪んだりします（行列式が $1$ からずれる）。$N$ を上げると、ちょうど回転になります。パウリ行列の $e^{-i\theta\sigma/2}=\cos\frac\theta2I-i\sin\frac\theta2\sigma$（[NB-02](NB02)）も、$\sigma^2=I$ を使った同じ仕組みです。"""),

md(r"""## 3. 挟み込み：$Pe^AP^{-1}=e^{PAP^{-1}}$

$P$ を正則な行列とすると、$P^{-1}P=I$ が間で消えるので

$$
(PAP^{-1})^k=PAP^{-1}\,PAP^{-1}\cdots PAP^{-1}=PA^kP^{-1}
$$

です。級数の各項でこれを使うと

$$
e^{PAP^{-1}}=\sum_k\frac{PA^kP^{-1}}{k!}=P\Big(\sum_k\frac{A^k}{k!}\Big)P^{-1}=Pe^AP^{-1}
$$

です。特に $A=PDP^{-1}$（$D$ は固有値を並べた対角行列）と対角化できれば、$e^A=Pe^DP^{-1}=P\operatorname{diag}(e^{\lambda_1},\dots,e^{\lambda_n})P^{-1}$ と、固有値の指数関数だけで計算できます（[det のノート](DETNOTE)の証明1）。対角化できない場合（ジョルダン標準形）の考え方と計算は、[行列の指数関数と交換子のノート](MEXPNOTE)の Part II にまとめました。"""),

code(r'''A = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
P = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
Pinv = np.linalg.inv(P)
for k in range(6):
    assert np.allclose(np.linalg.matrix_power(P @ A @ Pinv, k), P @ np.linalg.matrix_power(A, k) @ Pinv)
assert np.allclose(P @ expm(A) @ Pinv, expm(P @ A @ Pinv))

lam, V = np.linalg.eig(A)                            # A = V diag(λ) V⁻¹
via_diag = V @ np.diag(np.exp(lam)) @ np.linalg.inv(V)
assert np.allclose(via_diag, expm(A))
print("固有値 λ =", np.round(lam, 3))
print("V diag(e^λ) V⁻¹ と expm(A) の差 =", f"{np.linalg.norm(via_diag - expm(A)):.1e}")

# 対角化できない行列（ジョルダン細胞）：A = λI + N、N² = 0 なので e^A = e^λ (I + N)
lam0 = 0.7
Jd = np.array([[lam0, 1], [0, lam0]], dtype=complex)
assert np.allclose(expm(Jd), np.exp(lam0) * np.array([[1, 1], [0, 1]]))
print("ジョルダン細胞 [[0.7, 1], [0, 0.7]] の e^A =\n", np.round(expm(Jd).real, 4), "= e^0.7 × [[1, 1], [0, 1]]")'''),

md(r"""## 4. 微分は1次の近似：行列式の場合

微分は「1次の線形近似の係数」です：

$$
f(x+\varepsilon)=f(x)+f'(x)\,\varepsilon+O(\varepsilon^2)
$$

$O(\varepsilon^2)$（ランダウの記号、「オーダー・イプシロン2乗」）は、$\varepsilon^2$ と同じかそれより速く $0$ に近づく量です。行列式で確かめます。$\det(M+\varepsilon X)$ を $\varepsilon$ の多項式として展開すると、

- **0次**：$\det M$
- **1次**：$\varepsilon\cdot d(\det M)$。[det のノート](DETNOTE)の Jacobi の公式で、$d(\det M)=\det M\cdot\operatorname{tr}(M^{-1}X)$
- **2次以上**：$X$ の成分どうしの積を含む「余分な項」。微分（1次の近似）では捨てる部分

です。$2\times2$ では、2次の項がちょうど $\det X$ になり、$\det(M+X)-\det M-\det X=d(\det M)$ が**近似でなく、ぴったり**成り立ちます。$3\times3$ 以上では、2次から $(n-1)$次の「混ざった項」も出て、$\det X$ は最も高い $n$次の項になります。"""),

code(r'''import sympy as sp

eps = sp.symbols("varepsilon")
for n in (2, 3):
    M = sp.Matrix(n, n, lambda i, j: sp.Symbol(f"m{i + 1}{j + 1}"))
    X = sp.Matrix(n, n, lambda i, j: sp.Symbol(f"x{i + 1}{j + 1}"))
    poly = sp.Poly(sp.expand((M + eps * X).det()), eps)
    c = [sp.expand(poly.coeff_monomial(eps**k)) for k in range(n + 1)]
    assert sp.expand(c[0] - M.det()) == 0                                   # 0次 = det M
    assert sp.expand(c[1] - (M.adjugate() * X).trace()) == 0                # 1次 = tr(adj(M) X) = det M tr(M⁻¹X)
    assert sp.expand(c[n] - X.det()) == 0                                   # 最高次 = det X
    print(f"{n}×{n}：")
    for k in range(n + 1):
        name = {0: "det M", 1: "d(det M) = tr(adj(M) X)", n: "det X"}.get(k, "混ざった項")
        print(f"  ε^{k} の係数（{name}）：項の数 {len(sp.Add.make_args(c[k]))}")
    if n == 2:
        print("  → 2×2 では 2次の項 = det X なので、det(M+X) − det M − det X = d(det M) がぴったり成り立つ")
    else:
        print("  2次の項の例：", sp.Add.make_args(c[2])[:3], "…（M と X の成分が混ざる）")'''),

code(r'''# 1次の近似の誤差が ε² で小さくなること（両対数で傾き 2）
Mn = rng.normal(size=(3, 3))
Xn = rng.normal(size=(3, 3))
d_det = np.linalg.det(Mn) * np.trace(np.linalg.inv(Mn) @ Xn)               # Jacobi の公式
eps_vals = np.logspace(-6, -1, 20)
err = np.array([abs(np.linalg.det(Mn + e * Xn) - np.linalg.det(Mn) - e * d_det) for e in eps_vals])
slope = np.polyfit(np.log(eps_vals), np.log(err), 1)[0]
print(f"両対数の傾き = {slope:.3f}（O(ε²) なら 2）")
assert abs(slope - 2) < 0.1
fig = go.Figure([go.Scatter(x=eps_vals.tolist(), y=err.tolist(), mode="lines+markers", name="|det(M+εX) − det M − ε d(det M)|"),
                 go.Scatter(x=eps_vals.tolist(), y=(err[-1] * (eps_vals / eps_vals[-1]) ** 2).tolist(), mode="lines",
                            line=dict(dash="dash"), name="ε² に比例する線")])
fig.update_layout(height=360, width=780, xaxis_type="log", yaxis_type="log", xaxis_title="ε", yaxis_title="1次の近似の誤差",
                  margin=dict(t=20))
fig'''),

md(r"""## 5. $\det(e^A)=e^{\operatorname{tr}A}$

[det のノート](DETNOTE)で2通りに証明した公式を、対角化できない行列や複素行列も含めて数値で確かめます。$\operatorname{tr}A=0$ なら $\det e^A=1$ で、これが $SU(n)$ の生成子がトレースゼロになる理由でした。

この公式は、Lean 4 + Mathlib でも証明しました（Mathlib の v4.28.0 ではまだ TODO になっている定理です）：

- [DetExpTrace.lean](LEANDET) の `det_exp`：ノートの証明2の道筋（$f(t)=\det e^{tA}$ が $f'=(\operatorname{tr}A)f$ を満たす。上の §4 の「行列式の1次の近似」を、単位行列の場所で使う）
- [Schur.lean](LEANSCHUR) の `det_exp_via_schur`：シューア分解 $A=UTU^*$（$T$ は上三角）を使う道筋

```lean
theorem det_exp (A : Matrix n n ℂ) : (exp A).det = Complex.exp A.trace
```"""),

code(r'''for trial in range(200):
    A = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
    assert np.isclose(np.linalg.det(expm(A)), np.exp(np.trace(A)))
assert np.isclose(np.linalg.det(expm(Jd)), np.exp(np.trace(Jd)))            # 対角化できない行列でも
H = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
H = H + H.conj().T
H = H - np.trace(H) / 3 * np.eye(3)                                          # トレースゼロのエルミート行列
assert np.isclose(np.linalg.det(expm(1j * H)), 1)
print("ランダムな 4×4 複素行列 200 個、ジョルダン細胞、トレースゼロのエルミート行列で確認しました")'''),

md(r"""## 6. $e^{A+B}\neq e^Ae^B$（交換しないとき）

数なら $e^{a+b}=e^ae^b$ ですが、行列では次のようになります。

- $AB=BA$（$[A,B]=0$）なら、$e^{A+B}=e^Ae^B$ が必ず成り立ちます（**十分条件**。数のときと同じく、二項展開がそのまま使えるから）。
- **すべての $t$ で** $e^{t(A+B)}=e^{tA}e^{tB}$ が成り立つのは、$[A,B]=0$ のときだけです。両辺を $t$ で展開して $t^2$ の係数を比べると、$\frac12(A+B)^2$ と $\frac12A^2+AB+\frac12B^2$ の差が $\frac12[A,B]$ だからです。
- ただし、**特定の1点（たとえば $t=1$）だけなら、交換しなくても偶然成り立つ**ことがあります（下の反例）。

**交換子 $[A,B]=AB-BA$ と量子力学**：交換子は、量子力学の中心にある量です。物理量（行列・演算子）が交換しないことが、不確定性関係や、測定の順序で結果が変わることの源です。パウリ行列（スピン、1量子ビットの演算子）では

$$
[\sigma_x,\sigma_y]=2i\sigma_z,\qquad[\sigma_y,\sigma_z]=2i\sigma_x,\qquad[\sigma_z,\sigma_x]=2i\sigma_y\qquad\big(\text{まとめて}\ [\sigma_i,\sigma_j]=2i\varepsilon_{ijk}\sigma_k\big)
$$

で、反交換子 $\{A,B\}=AB+BA$ は $\{\sigma_i,\sigma_j\}=2\delta_{ij}I$ です（クリフォード代数の関係）。$AB=\frac12\{A,B\}+\frac12[A,B]$ なので、2つを合わせると、積がまるごと

$$
\sigma_i\sigma_j=\delta_{ij}I+i\varepsilon_{ijk}\sigma_k
$$

と書けます（$\varepsilon_{ijk}$ はレヴィ・チヴィタ記号）。導出は[パウリ行列のノート](PAULINOTE)の Part IV・V、Lean による証明は [Pauli.lean](LEANPAULI) にあります。下の計算で $A=\sigma_x$、$B=\sigma_z$ を使うのは、$[\sigma_x,\sigma_z]=-2i\sigma_y\ne0$ と、交換しない一番簡単な例だからです。量子コンピュータでは、交換しない項の和のハミルトニアン（$\sigma_x+\sigma_z$ など）の時間発展を作るときに、このずれが問題になります（§7）。

小さな $t$ では

$$
e^{tA}e^{tB}=e^{t(A+B)+\frac{t^2}2[A,B]+O(t^3)}
$$

（ベイカー・キャンベル・ハウスドルフの公式の最初の項。導出は[行列の指数関数と交換子のノート](MEXPNOTE)の Part IV と付録B）なので、ずれは $\frac{t^2}2\|[A,B]\|$ 程度です。パウリ行列 $A=\sigma_x$、$B=\sigma_z$ で確かめます。

**反例（$t=1$ だけで偶然成り立つ）**：$A=\begin{pmatrix}0&0\\0&2\pi i\end{pmatrix}$、$B=\begin{pmatrix}0&1\\0&2\pi i\end{pmatrix}$ は $AB\ne BA$ ですが、どれも固有値が $0$ と $2\pi i$ の倍数で対角化できるので、$e^A=e^B=e^{A+B}=I$ です。$e^{2\pi i}=1$ という周期のしわざで、[det のノート](DETNOTE)の「1つの $U$ からは $\operatorname{tr}=0$ は出ない」反例と同じ仕組みです。$t$ を少しずらすと成り立たなくなります。"""),

code(r'''sx = np.array([[0, 1], [1, 0]], dtype=complex)
sz = np.array([[1, 0], [0, -1]], dtype=complex)
sy = np.array([[0, -1j], [1j, 0]])
comm = sx @ sz - sz @ sx
# パウリ行列：σiσj = δij I + i ε_ijk σk（反交換子 + 交換子）
sig = [sx, sy, sz]
eps3 = np.zeros((3, 3, 3))
for (i, j, k) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
    eps3[i, j, k], eps3[j, i, k] = 1, -1
for i in range(3):
    for j in range(3):
        anti = sig[i] @ sig[j] + sig[j] @ sig[i]
        com = sig[i] @ sig[j] - sig[j] @ sig[i]
        assert np.allclose(anti, 2 * (i == j) * np.eye(2))                                   # {σi, σj} = 2δij I
        assert np.allclose(com, 2j * sum(eps3[i, j, k] * sig[k] for k in range(3)))          # [σi, σj] = 2i ε_ijk σk
        assert np.allclose(sig[i] @ sig[j], (i == j) * np.eye(2) + 1j * sum(eps3[i, j, k] * sig[k] for k in range(3)))
assert np.allclose(comm, -2j * sy)
ts = np.logspace(-3, -0.5, 15)
gap = np.array([np.linalg.norm(expm(t * sx) @ expm(t * sz) - expm(t * (sx + sz)), 2) for t in ts])
pred = ts**2 / 2 * np.linalg.norm(comm, 2)
slope = np.polyfit(np.log(ts[:8]), np.log(gap[:8]), 1)[0]
print(f"ずれの両対数の傾き = {slope:.3f}（t² に比例なら 2）、t = 0.001 でのずれ / (t²/2 ‖[A,B]‖) = {gap[0] / pred[0]:.4f}")
assert abs(slope - 2) < 0.05 and abs(gap[0] / pred[0] - 1) < 1e-2
# 交換する場合（B = 2A + I）はぴったり一致
B2 = 2 * sx + np.eye(2)
assert np.allclose(expm(sx) @ expm(B2), expm(sx + B2))
# 反例：交換しないのに、t = 1 だけで e^{A+B} = e^A e^B
Ac = np.array([[0, 0], [0, 2j * np.pi]])
Bc = np.array([[0, 1], [0, 2j * np.pi]])
assert not np.allclose(Ac @ Bc, Bc @ Ac)
assert np.allclose(expm(Ac), np.eye(2)) and np.allclose(expm(Bc), np.eye(2)) and np.allclose(expm(Ac + Bc), np.eye(2))
assert not np.allclose(expm(0.9 * Ac) @ expm(0.9 * Bc), expm(0.9 * (Ac + Bc)))      # t = 0.9 では成り立たない
print("反例：AB ≠ BA なのに e^A = e^B = e^{A+B} = I（t = 0.9 にずらすと不一致）")
fig = go.Figure([go.Scatter(x=ts.tolist(), y=gap.tolist(), mode="lines+markers", name="‖e^{tA}e^{tB} − e^{t(A+B)}‖"),
                 go.Scatter(x=ts.tolist(), y=pred.tolist(), mode="lines", line=dict(dash="dash"), name="(t²/2)‖[A,B]‖")])
fig.update_layout(height=360, width=780, xaxis_type="log", yaxis_type="log", xaxis_title="t", margin=dict(t=20))
fig'''),

md(r"""## 7. トロッター分解：細かく刻んで交互に掛ける

§6 のずれは $t^2$ に比例するので、時間 $t$ を $n$ 等分すると、1回あたりのずれは $(t/n)^2$ 程度、$n$ 回分で $t^2/n$ 程度になります。したがって

$$
e^{(A+B)t}\approx\big(e^{At/n}e^{Bt/n}\big)^n\qquad(\text{誤差}\propto1/n)
$$

で、$n$ を増やせばいくらでも正確になります（**トロッター分解**）。さらに $e^{At/2n}e^{Bt/n}e^{At/2n}$ と対称に並べると、誤差は $1/n^2$ で小さくなります（**ストラング分解**、2次のスズキ・トロッター分解）。

**量子コンピュータでの役割**：ハミルトニアン $H$ が $H=H_1+H_2$ のような和で、それぞれの $e^{-iH_kt}$ は簡単なゲート（[NB-02](NB02) の回転ゲート）で作れるとき、全体の時間発展 $e^{-iHt}$ をトロッター分解で回路にします。ここでは $H=\sigma_x+\sigma_z$ とし、Qiskit の `PauliEvolutionGate` と `LieTrotter`・`SuzukiTrotter` で作った回路とも比べます。誤差の上限の導出、ストラング分解で2次の誤差が消える理由、$e^{-iHt}$ がユニタリである理由は、[行列の指数関数と交換子のノート](MEXPNOTE)の Part VI にあります。"""),

code(r'''from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Operator, SparsePauliOp
from qiskit.synthesis import LieTrotter, SuzukiTrotter

t_total = 1.0
U_exact = expm(-1j * t_total * (sx + sz))


def lie_trotter(n: int) -> Matrix:
    d = t_total / n
    return np.linalg.matrix_power(expm(-1j * d * sz) @ expm(-1j * d * sx), n)      # 先に σx、次に σz


def strang(n: int) -> Matrix:
    d = t_total / n
    return np.linalg.matrix_power(expm(-1j * d / 2 * sx) @ expm(-1j * d * sz) @ expm(-1j * d / 2 * sx), n)


def qiskit_trotter(synthesis: object) -> Matrix:
    qc = QuantumCircuit(1)
    qc.append(PauliEvolutionGate(SparsePauliOp(["X", "Z"], [1.0, 1.0]), time=t_total, synthesis=synthesis), [0])
    return Operator(qc.decompose().decompose()).data


def same_up_to_phase(U: Matrix, V: Matrix) -> bool:
    return bool(np.isclose(abs(np.trace(U.conj().T @ V)), U.shape[0]))


ns = np.array([1, 2, 4, 8, 16, 32, 64, 128])
err_lie = np.array([np.linalg.norm(lie_trotter(int(n)) - U_exact, 2) for n in ns])
err_strang = np.array([np.linalg.norm(strang(int(n)) - U_exact, 2) for n in ns])
for n in (2, 8, 32):
    assert same_up_to_phase(qiskit_trotter(LieTrotter(reps=n)), lie_trotter(n))
    assert same_up_to_phase(qiskit_trotter(SuzukiTrotter(order=2, reps=n)), strang(n))
s1 = np.polyfit(np.log(ns[3:]), np.log(err_lie[3:]), 1)[0]
s2 = np.polyfit(np.log(ns[3:]), np.log(err_strang[3:]), 1)[0]
print(f"誤差の傾き：トロッター {s1:.2f}（理論 −1）、ストラング {s2:.2f}（理論 −2）")
print("Qiskit の LieTrotter・SuzukiTrotter(order=2) の回路は、自前の計算と（大域位相を除いて）一致")
assert abs(s1 + 1) < 0.1 and abs(s2 + 2) < 0.1
fig = go.Figure([go.Scatter(x=ns.tolist(), y=err_lie.tolist(), mode="lines+markers", name="トロッター（誤差 ∝ 1/n）"),
                 go.Scatter(x=ns.tolist(), y=err_strang.tolist(), mode="lines+markers", name="ストラング（誤差 ∝ 1/n²）")])
fig.update_layout(height=380, width=780, xaxis_type="log", yaxis_type="log", xaxis_title="分割数 n",
                  yaxis_title="‖近似 − e^{−iHt}‖", margin=dict(t=20))
fig'''),

md(r"""## 観察のポイント（まとめ）

- 行列の指数関数は、$e^x$ の級数に行列を入れたもので、部分和は必ず収束する（行列が大きいほど、多くの項が必要）。
- $J^2=-I$ の $J$ では $e^{\theta J}$ が回転行列になり、オイラーの公式の行列版になる。
- $(PAP^{-1})^k=PA^kP^{-1}$ から $Pe^AP^{-1}=e^{PAP^{-1}}$ が出て、対角化できれば固有値の指数関数だけで計算できる。
- 微分は1次の近似で、捨てる部分は $O(\varepsilon^2)$。行列式の1次の係数が Jacobi の公式で、$\det(e^A)=e^{\operatorname{tr}A}$ の証明の要になる。
- 交換しない行列では $e^{A+B}\ne e^Ae^B$ で、ずれは $\frac{t^2}2[A,B]$ から始まる。細かく刻めば（トロッター分解）、いくらでも正確に近似でき、量子回路で時間発展を作る基本になる。

**次のノートブック**：[03_jacobian_linearization.ipynb](03_jacobian_linearization.ipynb) で、多変数の1次の近似（ヤコビ行列）と、それが壊れる場所（$\det J=0$）を見ます。"""),
]

# ============================================================================================ 03
nb3 = [
md(r"""# テイラー展開 3：線形近似とヤコビ行列 ―$\det J=0$ で何が起きるか

多変数の写像 $\mathbf f:\mathbb R^2\to\mathbb R^2$ のテイラー展開の1次の項は、**ヤコビ行列** $J$ です：

$$
\mathbf f(\mathbf p+\mathbf h)=\mathbf f(\mathbf p)+J(\mathbf p)\,\mathbf h+O(|\mathbf h|^2),\qquad J_{ij}=\frac{\partial f_i}{\partial x_j}
$$

ヤコビ行列は、これまでのノート（計量テンソル、クリストッフェル記号、ラプラス・ベルトラミ、多様体）で何度も出てきました。このノートブックでは、

1. ヤコビ行列が1次の近似であること（誤差が $O(|\mathbf h|^2)$）
2. 逆写像のヤコビ行列は、ヤコビ行列の逆行列（逆関数定理）
3. **$\det J=0$ のとき、逆写像が作れなくなる3つの典型**（スライダーで点を動かす）
4. ニュートン法：1次の近似をくり返して方程式を解く

を見ます。"""),

code(HEADER + r'''

Vec = NDArray[np.float64]          # 2次元のベクトル


def jacobian_numeric(f, p: Vec, h: float = 1e-6) -> NDArray[np.float64]:
    """中心差分によるヤコビ行列（列が ∂f/∂x_j）"""
    cols = [(f(p + h * e) - f(p - h * e)) / (2 * h) for e in np.eye(len(p))]
    return np.stack(cols, axis=1)


def polar(p: Vec) -> Vec:
    r, th = p
    return np.array([r * np.cos(th), r * np.sin(th)])


def polar_J(p: Vec) -> NDArray[np.float64]:
    r, th = p
    return np.array([[np.cos(th), -r * np.sin(th)], [np.sin(th), r * np.cos(th)]])'''),

md(r"""## 1. ヤコビ行列は1次の近似

極座標 $(r,\theta)\mapsto(x,y)=(r\cos\theta,r\sin\theta)$ で、$\mathbf f(\mathbf p+\mathbf h)-\mathbf f(\mathbf p)-J\mathbf h$ の大きさを $|\mathbf h|$ に対して描きます。両対数で傾き 2（$O(|\mathbf h|^2)$）なら、$J$ が1次の近似の係数です。"""),

code(r'''p0 = np.array([1.5, 0.6])
assert np.allclose(jacobian_numeric(polar, p0), polar_J(p0), atol=1e-8)
direction = np.array([0.6, -0.8])
hs = np.logspace(-5, -0.5, 15)
err = np.array([np.linalg.norm(polar(p0 + h * direction) - polar(p0) - polar_J(p0) @ (h * direction)) for h in hs])
slope = np.polyfit(np.log(hs), np.log(err), 1)[0]
print(f"両対数の傾き = {slope:.3f}（O(|h|²) なら 2）")
assert abs(slope - 2) < 0.1
fig = go.Figure([go.Scatter(x=hs.tolist(), y=err.tolist(), mode="lines+markers", name="|f(p+h) − f(p) − J h|")])
fig.update_layout(height=340, width=720, xaxis_type="log", yaxis_type="log", xaxis_title="|h|", margin=dict(t=20))
fig'''),

md(r"""## 2. 逆写像のヤコビ行列は、ヤコビ行列の逆行列

$\det J(\mathbf p)\ne0$ なら、$\mathbf p$ の近くで逆写像 $\mathbf f^{-1}$ があり、そのヤコビ行列は $J(\mathbf p)^{-1}$ です（**逆関数定理**。[関数・線形写像・微分・積分のノート](FLMNOTE)の Part III §9、証明は付録B）。極座標の逆写像 $(x,y)\mapsto(r,\theta)=(\sqrt{x^2+y^2},\operatorname{atan2}(y,x))$ で確かめます。極座標では $\det J=r$ です。"""),

code(r'''def polar_inv(q: Vec) -> Vec:
    return np.array([np.hypot(q[0], q[1]), np.arctan2(q[1], q[0])])


for p in (np.array([1.5, 0.6]), np.array([0.3, 2.5]), np.array([2.0, -1.0])):
    J_f = polar_J(p)
    J_inv_map = jacobian_numeric(polar_inv, polar(p))
    assert np.isclose(np.linalg.det(J_f), p[0])                                # det J = r
    assert np.allclose(J_inv_map, np.linalg.inv(J_f), atol=1e-6)               # 逆写像のヤコビ行列 = J⁻¹
    print(f"r = {p[0]}, θ = {p[1]}：det J = {np.linalg.det(J_f):.3f}、逆写像のヤコビ行列 = J⁻¹ を確認")'''),

md(r"""## 3. $\det J=0$ で何が起きるか：3つの典型

**ヤコビ行列は、点ごとの「局所的なゆがみ」**：ある行列の行列式は1つに決まりますが、ヤコビ行列 $J(\mathbf p)$ は**点 $\mathbf p$ ごとに違う行列**です。たとえば極座標では

$$
J(r,\theta)=\begin{pmatrix}\cos\theta&-r\sin\theta\\ \sin\theta&r\cos\theta\end{pmatrix},\qquad \det J(r,\theta)=r
$$

で、成分が $r,\theta$ によって変わります。$\mathbf p$ のごく近くだけを見ると、写像は線形写像 $J(\mathbf p)$ とみなせる（§1）ので、

- $\mathbf p$ のまわりの小さな円は、$J(\mathbf p)$ で決まる**楕円**に写る（どの向きに何倍伸びるか、どれだけ回るか）
- その面積の比が $|\det J(\mathbf p)|$、符号が向き（裏返るかどうか）

です。つまり $\det J(\mathbf p)$ は「点 $\mathbf p$ のまわりで、面積が何倍になるか」を表す、**点の関数**です。線形写像なら $J$ はどこでも同じ行列なので $\det J$ は定数ですが、非線形な写像では場所によって変わり、「$\det J(\mathbf p)=0$ となる点の集合」が、線になったり、平面全体になったりします。

$\det J(\mathbf p)=0$ の点では逆行列が作れず、逆関数定理が使えません。そこでは、写像は次のどれかの形で「壊れて」います。

| 写像 | $\det J(\mathbf p)$ | 壊れ方 |
|---|---|---|
| 極座標 $(r,\theta)\mapsto(r\cos\theta,r\sin\theta)$ | $r$ | $r=0$ の線全体が原点1点に**つぶれる**（座標特異点。[多様体のノート](MANINOTE)の「極は座標特異点」） |
| 折り返し $(x,y)\mapsto(x^2,y)$ | $2x$ | $x=0$ を境に**折り返し**、左右の2点が同じ点に写る（2対1） |
| 一方向につぶす $(x,y)\mapsto(x+y,\ 2x+2y)$ | $0$（どこでも） | 平面全体が1本の直線に**つぶれる** |

左の図は元の平面（格子と、点 $\mathbf p$ のまわりの小さな円）、右の図は写した先です。格子の点は $\det J$ の符号で色分けしています（青：正、赤：負、黒：ほぼ $0$）。点 $\mathbf p$ のスライダーを動かして、小さな円が写った先（$J(\mathbf p)$ で決まる楕円）がつぶれる様子を見ます。円と像の面積の比も表示するので、$|\det J(\mathbf p)|$ と比べてください（円が小さいほどよく一致します）。"""),

code(r'''def fold(p: Vec) -> Vec:
    return np.array([p[0] ** 2, p[1]])


def squash(p: Vec) -> Vec:
    return np.array([p[0] + p[1], 2 * p[0] + 2 * p[1]])


MAPS = {
    "polar": ("極座標 (r, θ) → (r cos θ, r sin θ)", polar, (0.0, 2.0), (0.0, 2 * np.pi)),
    "fold": ("折り返し (x, y) → (x², y)", fold, (-1.5, 1.5), (-1.5, 1.5)),
    "squash": ("一方向につぶす (x, y) → (x + y, 2x + 2y)", squash, (-1.5, 1.5), (-1.5, 1.5)),
}
assert np.isclose(np.linalg.det(jacobian_numeric(fold, np.array([0.7, 0.2]))), 1.4)
assert abs(np.linalg.det(jacobian_numeric(squash, np.array([0.3, -0.4])))) < 1e-9


def grid_lines(f, xr: tuple[float, float], yr: tuple[float, float], k: int = 13) -> tuple[list, list, list, list]:
    """元の平面の格子線と、写した先の格子線（None で区切った座標の列）"""
    dx, dy, ix, iy = [], [], [], []
    for a in np.linspace(*xr, k):
        ys = np.linspace(*yr, 60)
        pts = np.array([[a, b] for b in ys])
        img = np.array([f(q) for q in pts])
        dx += pts[:, 0].tolist() + [None]; dy += pts[:, 1].tolist() + [None]
        ix += img[:, 0].tolist() + [None]; iy += img[:, 1].tolist() + [None]
    for b in np.linspace(*yr, k):
        xs = np.linspace(*xr, 60)
        pts = np.array([[a, b] for a in xs])
        img = np.array([f(q) for q in pts])
        dx += pts[:, 0].tolist() + [None]; dy += pts[:, 1].tolist() + [None]
        ix += img[:, 0].tolist() + [None]; iy += img[:, 1].tolist() + [None]
    return dx, dy, ix, iy


fig_jac = go.FigureWidget(make_subplots(rows=1, cols=2, subplot_titles=("元の平面", "写した先")))
for col in (1, 2):
    fig_jac.add_trace(go.Scatter(x=[], y=[], mode="lines", line=dict(color="#ccc", width=1), hoverinfo="skip", showlegend=False), 1, col)
    fig_jac.add_trace(go.Scatter(x=[], y=[], mode="markers", marker=dict(size=5), hoverinfo="skip", showlegend=False), 1, col)
    fig_jac.add_trace(go.Scatter(x=[], y=[], mode="lines", line=dict(color="#e67e00", width=3), showlegend=False), 1, col)
    fig_jac.add_trace(go.Scatter(x=[], y=[], mode="markers", marker=dict(size=9, color="#222"), showlegend=False), 1, col)
fig_jac.update_layout(height=480, width=980, margin=dict(t=40, l=40, r=20, b=40))
map_dd = W.Dropdown(options=[(v[0], k) for k, v in MAPS.items()], value="polar", description="写像", layout=W.Layout(width="420px"))
px_s = W.FloatSlider(value=0.8, min=0.0, max=1.0, step=0.01, description="p の位置 1")
py_s = W.FloatSlider(value=0.3, min=0.0, max=1.0, step=0.01, description="p の位置 2")
info3 = W.HTML()


def update_jac(*_: object) -> None:
    """写像と点 p が変わるたびに、格子・小さな円・ヤコビ行列を描き直す"""
    name, f, xr, yr = MAPS[map_dd.value]
    p = np.array([xr[0] + px_s.value * (xr[1] - xr[0]), yr[0] + py_s.value * (yr[1] - yr[0])])
    dx, dy, ix, iy = grid_lines(f, xr, yr)
    gx, gy = np.meshgrid(np.linspace(*xr, 17), np.linspace(*yr, 17))
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    dets = np.array([np.linalg.det(jacobian_numeric(f, q)) for q in pts])
    colors = ["#222" if abs(d) < 1e-6 else ("#1f77b4" if d > 0 else "#d62728") for d in dets]
    img_pts = np.array([f(q) for q in pts])
    rad = 0.12 * (xr[1] - xr[0])
    ang = np.linspace(0, 2 * np.pi, 80)
    circle = np.stack([p[0] + rad * np.cos(ang), p[1] + rad * np.sin(ang)], axis=1)
    circle_img = np.array([f(q) for q in circle])
    J_p = jacobian_numeric(f, p)
    det_p = float(np.linalg.det(J_p))
    area = 0.5 * abs(np.dot(circle_img[:, 0], np.roll(circle_img[:, 1], -1)) - np.dot(circle_img[:, 1], np.roll(circle_img[:, 0], -1)))
    ratio = area / (np.pi * rad**2)                     # 像の面積 ÷ 円の面積（靴ひも公式）
    with fig_jac.batch_update():
        fig_jac.data[0].x, fig_jac.data[0].y = dx, dy
        fig_jac.data[1].x, fig_jac.data[1].y = pts[:, 0].tolist(), pts[:, 1].tolist()
        fig_jac.data[1].marker.color = colors
        fig_jac.data[2].x, fig_jac.data[2].y = circle[:, 0].tolist(), circle[:, 1].tolist()
        fig_jac.data[3].x, fig_jac.data[3].y = [float(p[0])], [float(p[1])]
        fig_jac.data[4].x, fig_jac.data[4].y = ix, iy
        fig_jac.data[5].x, fig_jac.data[5].y = img_pts[:, 0].tolist(), img_pts[:, 1].tolist()
        fig_jac.data[5].marker.color = colors
        fig_jac.data[6].x, fig_jac.data[6].y = circle_img[:, 0].tolist(), circle_img[:, 1].tolist()
        fq = f(p)
        fig_jac.data[7].x, fig_jac.data[7].y = [float(fq[0])], [float(fq[1])]
    Jtxt = f"[[{J_p[0, 0]:+.2f}, {J_p[0, 1]:+.2f}], [{J_p[1, 0]:+.2f}, {J_p[1, 1]:+.2f}]]"
    if abs(det_p) > 1e-6:
        Ji = np.linalg.inv(J_p)
        inv_txt = f"逆行列 J⁻¹ = [[{Ji[0, 0]:+.2f}, {Ji[0, 1]:+.2f}], [{Ji[1, 0]:+.2f}, {Ji[1, 1]:+.2f}]] → p の近くに逆写像がある"
    else:
        inv_txt = "<b>det J = 0：逆行列が作れない</b>（小さな円が線分につぶれる。p の近くで逆写像が作れない）"
    info3.value = (f"p = ({p[0]:.2f}, {p[1]:.2f})：J(p) = {Jtxt}、det J(p) = {det_p:+.3f}、"
                   f"面積の比（像 ÷ 円）≈ {ratio:.3f}<br>{inv_txt}")


for w in (map_dd, px_s, py_s):
    w.observe(update_jac, "value")
update_jac()
W.VBox([map_dd, W.HBox([px_s, py_s]), info3, fig_jac])'''),

md(r"""**考えてみよう**

- **極座標**：「p の位置 1」（$r$）を $0$ に近づけると、小さな円の像が細長くつぶれていき、$r=0$ で線分になります。$\theta$ がいくつでも、$r=0$ なら原点です。逆写像（角度 $\theta$ を求める）が決まらなくなるのは、そのためです。
- **折り返し**：$x$ を $0$ に近づけると、像の楕円が横につぶれ、$x=0$ で線分になります。$x<0$（赤）と $x>0$（青）の格子が、右の図で重なっている（2対1）ことも確かめましょう。行列式の符号が変わるのは、向きが反転するからです。
- **一方向につぶす**：どこに $\mathbf p$ を置いても、像は線分です。$J$ が定数行列（線形写像）なので、$\det J(\mathbf p)=0$ が一部の線の上ではなく、平面全体で起きている場合です。"""),

md(r"""## 4. ニュートン法：1次の近似をくり返す

方程式 $\mathbf f(\mathbf x)=\mathbf y$ を解くために、今の推定 $\mathbf x_k$ のまわりで1次の近似 $\mathbf f(\mathbf x_k)+J(\mathbf x_k)(\mathbf x-\mathbf x_k)=\mathbf y$ を解き、それを次の推定にします：

$$
\mathbf x_{k+1}=\mathbf x_k-J(\mathbf x_k)^{-1}\big(\mathbf f(\mathbf x_k)-\mathbf y\big)
$$

1次の近似の誤差は $O(|\mathbf h|^2)$ なので、解の近くでは**誤差が1回ごとにおよそ2乗になる**（桁数が倍々に増える）速さで収束します。ただし $J$ の逆行列を使うので、$\det J$ が $0$ に近い所から始めると、1歩が大きく飛んでしまいます。極座標で $(x,y)=(1,1)$ になる $(r,\theta)$（答えは $(\sqrt2,\pi/4)$）を探します。"""),

code(r'''def newton(f, Jf, y: Vec, x0: Vec, steps: int = 8) -> list[Vec]:
    xs = [x0]
    for _ in range(steps):
        x = xs[-1]
        xs.append(x - np.linalg.solve(Jf(x), f(x) - y))
    return xs


target = np.array([1.0, 1.0])
answer = np.array([np.sqrt(2), np.pi / 4])
good = newton(polar, polar_J, target, np.array([1.0, 0.5]))
errs = [float(np.linalg.norm(x - answer)) for x in good]
print("良い出発点 (1.0, 0.5) からの誤差：", ["%.1e" % e for e in errs[:6]])
for k in range(1, 4):                                   # 誤差がおよそ 2 乗になる
    assert errs[k + 1] < 2 * errs[k] ** 2 + 1e-14
bad = newton(polar, polar_J, target, np.array([0.02, 0.5]), steps=3)
print("det J ≈ 0（r = 0.02）から始めた最初の1歩：", np.round(bad[0], 3), "→", np.round(bad[1], 2),
      f"（det J = {np.linalg.det(polar_J(bad[0])):.2f} なので J⁻¹ が大きく、遠くへ飛ぶ）")
assert np.linalg.norm(bad[1] - bad[0]) > 10'''),

md(r"""## 観察のポイント（まとめ）

- ヤコビ行列は、多変数のテイラー展開の1次の項（最良の線形近似）で、誤差は $O(|\mathbf h|^2)$。点ごとに違う行列で、その点のまわりの「局所的なゆがみ」（小さな円 → 楕円）を表し、$|\det J(\mathbf p)|$ は面積の倍率（[関数・線形写像・微分・積分のノート](FLMNOTE)の Part III §5）。
- $\det J\ne0$ なら、その点の近くで逆写像があり、そのヤコビ行列は $J^{-1}$（逆関数定理）。
- $\det J=0$ の点では、写像が「つぶれる」か「折り返す」かしていて、逆写像が作れない。極座標の原点（座標特異点）は、その典型。
- ニュートン法は1次の近似のくり返しで、解の近くでは誤差がおよそ2乗ずつ減るが、$\det J\approx0$ の所では大きく飛ぶ。
- カオスのノートブック（[ローレンツ系](CHAOSNB)）でも、近い軌道の差の広がりを、ヤコビ行列（1次の近似）で調べました。"""),
]

save("01_taylor_euler.ipynb", nb1)
save("02_matrix_exponential.ipynb", nb2)
save("03_jacobian_linearization.ipynb", nb3)
