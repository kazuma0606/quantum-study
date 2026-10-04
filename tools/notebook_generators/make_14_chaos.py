"""notebooks/learning/14_chaos の2冊のノートブックを生成する（学習ロードマップの候補14：カオスと力学系）。"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path("notebooks/learning/14_chaos")
OUT.mkdir(parents=True, exist_ok=True)
ROADMAP = "../../../docs/learning_roadmap.md"
DET = "../../../研究ノート/04_群論・代数/det_exp_trace_proof.md"
LIE = "../../../研究ノート/02_微分幾何/lie_derivative.md"


def save(name, cells):
    for i, cell in enumerate(cells):
        cell.id = f"{Path(name).stem[:2]}-{i:02d}"   # 作り直しても差分が出ないよう、セルの ID を固定する
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nbformat.write(nb, OUT / name)
    print("書き出し:", OUT / name)


def md(text):
    return new_markdown_cell(text.replace("ROADMAP", ROADMAP).replace("DETNOTE", DET).replace("LIENOTE", LIE))


code = new_code_cell

# ============================================================================================ 01
nb1 = [
md(r"""# カオス 1：ロジスティック写像 ―決定論なのに予測できない

[学習ロードマップ](ROADMAP)の候補14（カオスと力学系）を、**ノートブックから**始めます。式の導出は後でノートにまとめるので、ここではまず計算して、結果を見て考えます。各節の最後に「**考えてみよう**」という問いを置きました。

扱うのは、いちばん単純なカオスの例である**ロジスティック写像**

$$
x_{n+1}=r\,x_n(1-x_n)\qquad(0\le x_n\le1,\ 0\le r\le4)
$$

です。$x_n$ は「生き物の数（最大を 1 とした割合）」、$r$ は増え方の強さ、という解釈がよく使われます。式は1行で、乱数も使っていません（**決定論的**）。それでも、$r$ によっては先が読めなくなります。

**中心になる量**は**リアプノフ指数** $\lambda$ です。近い2つの初期値の差が $|\delta_n|\approx|\delta_0|\,e^{\lambda n}$ と広がる速さで、$\lambda>0$ がカオスの目印になります。

**使い方**：上から順に実行します。`assert` は、計算結果が既知の値と合っていることを確かめるものです。"""),

code(r'''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from numpy.typing import NDArray
from plotly.subplots import make_subplots

Floats = NDArray[np.float64]   # 実数の配列（型ヒント用の別名）
# 注意：FigureWidget（スライダーで描き直す図）には、numpy 配列ではなくリストを渡す（NB-02 を参照）


def logistic(r: float | Floats, x: float | Floats) -> float | Floats:
    """ロジスティック写像 f(x) = r x (1 − x)"""
    return r * x * (1 - x)


def orbit(r: float, x0: float, n: int) -> Floats:
    """x0, x1, …, x_{n−1}（初期値 x0 から n 個）"""
    xs = np.empty(n)
    xs[0] = x0
    for k in range(1, n):
        xs[k] = logistic(r, xs[k - 1])
    return xs'''),

md(r"""## 1. $r$ を変えると、振る舞いが変わる

4つの $r$ で、$x_0=0.2$ から 60 回くり返した時系列を描きます。"""),

code(r'''cases = [(2.8, "r = 2.8"), (3.2, "r = 3.2"), (3.5, "r = 3.5"), (3.9, "r = 3.9")]
fig = make_subplots(rows=2, cols=2, subplot_titles=[t for _, t in cases], shared_yaxes=True)
for k, (r, title) in enumerate(cases):
    xs = orbit(r, 0.2, 60)
    fig.add_trace(go.Scatter(y=xs.tolist(), mode="lines+markers", marker=dict(size=4), showlegend=False),
                  row=k // 2 + 1, col=k % 2 + 1)
fig.update_layout(height=500, width=900, margin=dict(t=40, l=40, r=20, b=30))
fig.update_xaxes(title_text="n")

# 十分くり返した後の最後の 64 回で、何種類の値が現れるか（周期）を数える
for r, title in cases:
    tail = np.round(orbit(r, 0.2, 2000)[-64:], 6)
    print(f"{title}：くり返す値の種類 = {len(np.unique(tail))}")
fig'''),

md(r"""**考えてみよう**

- $r=2.8$ では1つの値に落ち着き、$3.2$ では2つの値、$3.5$ では4つの値を交互にくり返します。$3.9$ ではどうでしょうか。
- 1つの値に落ち着くとき、その値は $x=r x(1-x)$ の解（**不動点**）のはずです。$r=2.8$ で計算して、上の図と比べてみましょう。"""),

md(r"""## 2. 初期値への敏感さ：差は指数関数的に広がる

$r=4$ で、$10^{-10}$ だけ違う2つの初期値から始めます。差 $|x_n-y_n|$ を対数目盛りで描くと、直線（指数関数的な増加）になり、その傾きがリアプノフ指数です。$r=4$ では $\lambda=\ln2$（1回ごとに差が約2倍）であることが知られています。"""),

code(r'''r, x0, d0, N = 4.0, 0.3, 1e-10, 60
xa, xb = orbit(r, x0, N), orbit(r, x0 + d0, N)
diff = np.abs(xa - xb)
n = np.arange(N)

# 差が 1e-3 以下の範囲で、log|δ_n| の傾きを最小二乗で求める
mask = diff < 1e-3
slope = np.polyfit(n[mask], np.log(diff[mask]), 1)[0]
print(f"傾き（リアプノフ指数の推定）= {slope:.3f}、ln 2 = {np.log(2):.3f}")
assert abs(slope - np.log(2)) < 0.15

fig = go.Figure([go.Scatter(x=n.tolist(), y=diff.tolist(), mode="lines+markers", name="|x_n − y_n|（計算）"),
                 go.Scatter(x=n.tolist(), y=(d0 * np.exp(np.log(2) * n)).tolist(), mode="lines",
                            line=dict(dash="dash"), name="10⁻¹⁰ · 2ⁿ（λ = ln 2）")])
fig.update_layout(height=380, width=800, yaxis_type="log", xaxis_title="n", yaxis_title="差",
                  margin=dict(t=20), yaxis=dict(range=[-11, 0.5]))
fig'''),

md(r"""**考えてみよう**

- 差は約 35 回で、$x$ の範囲（$0\sim1$）と同じ大きさまで広がり、そこで頭打ちになります。なぜ頭打ちになるのでしょうか。
- 初期値の違いを $10^{-10}$ から $10^{-15}$ に減らすと、頭打ちになるまでの回数は何回延びるでしょうか（§4 で確かめます）。
- コンピュータの数（倍精度）は、約 $10^{-16}$ の丸め誤差を含みます。$r=4$ で 60 回くり返した $x_{60}$ は、どこまで信用できるでしょうか。"""),

md(r"""## 3. リアプノフ指数と分岐図

差が1回で何倍になるかは、写像の傾き $|f'(x_n)|=|r(1-2x_n)|$ です。$n$ 回の積の対数を平均すると、リアプノフ指数

$$
\lambda=\lim_{N\to\infty}\frac1N\sum_{n=0}^{N-1}\ln|r(1-2x_n)|
$$

になります（微分は「最良の線形近似」なので、小さな差は傾き倍される）。$r$ を細かく変えて、上に**分岐図**（十分くり返した後の $x_n$ の値）、下にリアプノフ指数を描きます。"""),

code(r'''def lyapunov(rs: Floats, x0: float = 0.3, transient: int = 1000, n: int = 3000) -> Floats:
    """r の配列それぞれについて、λ = (1/N) Σ ln|r(1−2x_n)| をまとめて計算する"""
    x = np.full_like(rs, x0)
    for _ in range(transient):            # 最初の変化を捨てる
        x = logistic(rs, x)
    total = np.zeros_like(rs)
    for _ in range(n):
        total += np.log(np.abs(rs * (1 - 2 * x)) + 1e-300)
        x = logistic(rs, x)
    return total / n


def bifurcation(rs: Floats, keep: int = 120, transient: int = 1000) -> tuple[Floats, Floats]:
    x = np.full_like(rs, 0.3)
    for _ in range(transient):
        x = logistic(rs, x)
    R, X = [], []
    for _ in range(keep):
        x = logistic(rs, x)
        R.append(rs.copy())
        X.append(x.copy())
    return np.concatenate(R), np.concatenate(X)


rs = np.linspace(2.5, 4.0, 1200)
lam = lyapunov(rs)
R, X = bifurcation(rs)

lam4 = lyapunov(np.array([4.0]), n=200000)[0]
print(f"r = 4 のリアプノフ指数 = {lam4:.4f}（ln 2 = {np.log(2):.4f}）")
assert abs(lam4 - np.log(2)) < 1e-2
for r_, sign in [(3.2, -1), (3.5, -1), (3.7, +1), (3.83, -1), (3.9, +1)]:
    v = lyapunov(np.array([r_]))[0]
    print(f"r = {r_}：λ = {v:+.3f}")
    assert np.sign(v) == sign

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.05)
fig.add_trace(go.Scattergl(x=R.tolist(), y=X.tolist(), mode="markers", marker=dict(size=1, color="#1f77b4"),
                           name="分岐図"), row=1, col=1)
fig.add_trace(go.Scatter(x=rs.tolist(), y=lam.tolist(), mode="lines", line=dict(color="#d62728", width=1),
                         name="リアプノフ指数 λ"), row=2, col=1)
fig.add_hline(y=0, line_color="#555", row=2, col=1)
fig.update_yaxes(title_text="十分くり返した後の x", row=1, col=1)
fig.update_yaxes(title_text="λ", range=[-2, 1], row=2, col=1)
fig.update_xaxes(title_text="r", row=2, col=1)
fig.update_layout(height=650, width=900, margin=dict(t=20, l=60, r=20, b=40), showlegend=False)
fig'''),

md(r"""**考えてみよう**

- 分岐図で、1本の線が2本、4本、8本…と分かれていく所（**周期倍分岐**）で、$\lambda$ はちょうど $0$ に触れています。なぜでしょうか（ヒント：安定な周期軌道の上では、差は縮む。安定かどうかの境目では？）。
- $r\approx3.83$ には、カオスの中に急に3本だけになる「窓」があり、$\lambda<0$ です。カオスの中に、規則的な領域が埋まっています。
- 分岐が起きる $r$ の間隔は、だんだん縮まります。その比は $4.669\ldots$（**ファイゲンバウム定数**）に近づき、この値は写像の細かい形によらないことが知られています（このノートブックでは扱いません）。"""),

md(r"""## 4. スライダー：蜘蛛の巣図で、くり返しを見る

**蜘蛛の巣図**は、くり返しを図で追う方法です。$x_n$ から縦に放物線 $y=f(x)$ まで進み、横に対角線 $y=x$ まで進むと、そこが $x_{n+1}$ です。$r$ のスライダーを動かして、落ち着く・振動する・カオスになる様子を見ます。"""),

code(r'''def cobweb(r: float, x0: float, n: int) -> tuple[list[float], list[float]]:
    xs, ys = [x0], [0.0]
    x = x0
    for _ in range(n):
        y = float(logistic(r, x))
        xs += [x, y]
        ys += [y, y]
        x = y
    return xs, ys


fig_web = go.FigureWidget(make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55],
                                    subplot_titles=("蜘蛛の巣図", "時系列 x_n")))
grid = np.linspace(0, 1, 200)
fig_web.add_trace(go.Scatter(x=grid.tolist(), y=grid.tolist(), mode="lines", line=dict(color="#999", dash="dot"), name="y = x"), 1, 1)
fig_web.add_trace(go.Scatter(x=[], y=[], mode="lines", line=dict(color="#1f77b4"), name="y = r x (1−x)"), 1, 1)
fig_web.add_trace(go.Scatter(x=[], y=[], mode="lines", line=dict(color="#d62728", width=1), name="くり返し"), 1, 1)
fig_web.add_trace(go.Scatter(x=[], y=[], mode="lines+markers", marker=dict(size=4), line=dict(color="#d62728"), name="x_n"), 1, 2)
fig_web.update_layout(height=430, width=950, margin=dict(t=40, l=40, r=20, b=40), showlegend=False,
                  xaxis=dict(range=[0, 1]), yaxis=dict(range=[0, 1], scaleanchor="x"), yaxis2=dict(range=[0, 1]))
r_slider = W.FloatSlider(value=3.2, min=2.5, max=4.0, step=0.01, description="r")
x0_slider = W.FloatSlider(value=0.2, min=0.01, max=0.99, step=0.01, description="x₀")
info = W.HTML()


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、蜘蛛の巣図・時系列・λ を描き直す"""
    r, x0 = r_slider.value, x0_slider.value
    cx, cy = cobweb(r, x0, 80)
    xs = orbit(r, x0, 100)
    lam_r = float(lyapunov(np.array([r]))[0])
    with fig_web.batch_update():
        fig_web.data[1].x, fig_web.data[1].y = grid.tolist(), logistic(r, grid).tolist()
        fig_web.data[2].x, fig_web.data[2].y = cx, cy
        fig_web.data[3].x, fig_web.data[3].y = list(range(100)), xs.tolist()
    kind = "カオス（λ > 0）" if lam_r > 1e-3 else ("周期倍分岐の付近（λ ≈ 0）" if lam_r > -1e-2 else "周期的（λ < 0）")
    info.value = f"r = {r:.2f}：リアプノフ指数 λ = {lam_r:+.3f} → {kind}"


for w in (r_slider, x0_slider):
    w.observe(update, "value")
update()
W.VBox([W.HBox([r_slider, x0_slider]), info, fig_web])'''),

md(r"""**考えてみよう**

- $r<3$ では、蜘蛛の巣は放物線と対角線の交点（不動点）に吸い込まれます。$r=3$ を超えると、交点のまわりを回り続けるようになります。交点での放物線の傾き $f'(x^*)$ に注目すると、境目は $|f'(x^*)|=1$ のはずです。確かめてみましょう。
- $r=3.83$ 付近で、周期3の動きを探してみましょう。"""),

md(r"""### 補足：落ち着く速さを決めるのは、$x_0$ より $r$（不動点での傾き）

蜘蛛の巣図を動かすと、$x_0$ によって落ち着きにくく見えることがあります。$x_0$ を変えて、不動点 $x^*=1-\frac1r$ にほぼ落ち着く（ずれが $10^{-6}$ 以下になる）までの回数を数えてみます。"""),

code(r"""def steps_to_settle(r: float, x0: float, tol: float = 1e-6, max_n: int = 100000) -> int:
    x_star = 1 - 1 / r
    x = x0
    for n in range(max_n):
        if abs(x - x_star) < tol:
            return n
        x = logistic(r, x)
    return max_n


x0s = [0.05, 0.2, 0.5, 0.8, 0.99]
print("  r    |f'(x*)| = |2−r|   " + "  ".join(f"x0={x0:<4}" for x0 in x0s))
for r in (2.8, 2.95, 2.99):
    counts = [steps_to_settle(r, x0) for x0 in x0s]
    print(f"{r:5.2f}        {abs(2 - r):.2f}          " + "  ".join(f"{c:7d}" for c in counts))
    assert max(counts) < 1.3 * min(counts)          # x0 による違いは小さい
assert steps_to_settle(2.99, 0.2) > 15 * steps_to_settle(2.8, 0.2)   # r が 3 に近いと、桁違いに遅い"""),

md(r"""- **$x_0$ による違いはわずか**です。$r=2.8$ なら、どこから始めても約 50 回で同じ値に落ち着きます。
- **効くのは $r$ が 3 に近いかどうか**です。不動点からのずれは、1回ごとに不動点での傾き $|f'(x^*)|=|2-r|$ 倍になります。$r=2.8$ なら 0.8 倍ずつ縮みますが、$r=2.99$ では 0.99 倍ずつなので、なかなか縮みません。
- $r=3$ で倍率がちょうど 1 になり、それを超えるとずれが縮まなくなって、周期2に移ります。これが §3 の「周期倍分岐で $\lambda$ がちょうど 0 に触れる」理由です（$\lambda$ は倍率の対数の平均で、倍率 1 なら $\ln1=0$）。
- $x_0=0.99$ のように端に近い値から始めると、最初の1回で $x_1=r\cdot0.99\cdot0.01\approx0.03$ と 0 の近くへ飛び、戻るまでに数回かかります。蜘蛛の巣図で「落ち着きにくい」と見えるのは、この最初の遠回りです。"""),

md(r"""## 5. 予測できる時間

差が $\delta_0$ から許せる大きさ $\Delta$ になるまでの回数は、$\delta_0e^{\lambda n}=\Delta$ から

$$
n^*\approx\frac1\lambda\ln\frac{\Delta}{\delta_0}
$$

です。初期の精度を1桁（10倍）よくしても、予測できる回数は $\frac{\ln10}{\lambda}$（$r=4$ なら約 $3.3$ 回）しか延びません。ランダムに選んだ 300 個の初期値で平均して確かめます。"""),

code(r'''def steps_to_diverge(r: float, d0: float, tol: float = 0.1, trials: int = 300, max_n: int = 200) -> float:
    rng = np.random.default_rng(0)
    x = rng.uniform(0.05, 0.95, trials)
    y = x + d0
    steps = np.full(trials, max_n, dtype=float)
    alive = np.ones(trials, dtype=bool)
    for k in range(max_n):
        x, y = logistic(r, x), logistic(r, y)
        hit = alive & (np.abs(x - y) > tol)
        steps[hit] = k + 1
        alive &= ~hit
    return float(steps.mean())


digits = np.arange(2, 15)
n_star = np.array([steps_to_diverge(4.0, 10.0 ** (-d)) for d in digits])
slope = np.polyfit(digits, n_star, 1)[0]
print(f"初期の精度 1 桁あたりの延び = {slope:.2f} 回（理論 ln10 / ln2 = {np.log(10) / np.log(2):.2f} 回）")
assert abs(slope - np.log(10) / np.log(2)) < 0.4

fig = go.Figure([go.Scatter(x=digits.tolist(), y=n_star.tolist(), mode="lines+markers", name="計算（300 個の平均）")])
fig.update_layout(height=360, width=700, xaxis_title="初期の精度（小数点以下の桁数、δ₀ = 10^−桁）",
                  yaxis_title="差が 0.1 を超えるまでの回数", margin=dict(t=20))
fig'''),

md(r"""## 観察のポイント（まとめ）

- カオスは「発散する」のではありません。$r=3.9$ でも $x$ は $0.1\sim0.97$ くらいの範囲に収まっています。特徴は次の3つがそろうことです：(1) 範囲は限られている、(2) 1つの値にも周期にも落ち着かない、(3) 近い2点の**差**が指数関数的に広がる（頭打ちになるまで）。
- 1行の決定論的な式でも、$r$ によっては (3) が起き、先が読めなくなります。差が広がる速さがリアプノフ指数 $\lambda$ で、「1回で差が何倍になるか（傾き）」の対数の平均です。倍率が 1 より小さければ落ち着き（$\lambda<0$）、1 より大きい状態が続けばカオス（$\lambda>0$）です。
- 予測できる時間は、初期の精度の**対数**にしか比例しません。精度を上げても、予測できる時間はほとんど延びません。「全てを知る悪魔なら未来を完全に予測できる」というラプラスの悪魔への、定量的な反論です。
- $\lambda$ は「傾き（微分）の積の対数の平均」です。1次元では傾き、多次元ではヤコビ行列の積になります（次のノートブック）。

**次のノートブック**：[02_lorenz.ipynb](02_lorenz.ipynb) で、3次元の連続な系（ローレンツ系）を扱います。"""),
]

# ============================================================================================ 02
nb2 = [
md(r"""# カオス 2：ローレンツ系 ―ストレンジアトラクタと、3つのリアプノフ指数

1963年に気象学者ローレンツが、大気の対流を極端に簡単にしたモデルとして調べた微分方程式です：

$$
\dot x=\sigma(y-x),\qquad \dot y=x(\rho-z)-y,\qquad \dot z=xy-\beta z
$$

標準的なパラメータ $\sigma=10,\ \rho=28,\ \beta=8/3$ で、カオスになります。ロジスティック写像（1冊目）との違いは、**連続時間**で**3次元**であることです。差の広がり方は、1次元の「傾き」の代わりに**ヤコビ行列**で決まり、リアプノフ指数は3つになります。

[学習ロードマップ](ROADMAP)の候補14、ノートブック先行。各節の「考えてみよう」は、後でノートにまとめる材料です。"""),

code(r'''import numpy as np
import plotly.graph_objects as go
import ipywidgets as W
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

Floats = NDArray[np.float64]   # 実数の配列（型ヒント用の別名）
# 注意：FigureWidget（スライダーで描き直す図）には、numpy 配列ではなくリストを渡す（NB-02 を参照）

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0


def lorenz(t: float, v: Floats, sigma: float = SIGMA, rho: float = RHO, beta: float = BETA) -> Floats:
    x, y, z = v
    return np.array([sigma * (y - x), x * (rho - z) - y, x * y - beta * z])


def jacobian(v: Floats, sigma: float = SIGMA, rho: float = RHO, beta: float = BETA) -> Floats:
    """ローレンツ系のヤコビ行列 ∂(ẋ, ẏ, ż)/∂(x, y, z)"""
    x, y, z = v
    return np.array([[-sigma, sigma, 0.0], [rho - z, -1.0, -x], [y, x, -beta]])


def trajectory(v0: Floats, T: float, rho: float = RHO, n: int = 8000) -> Floats:
    """時刻 0〜T の軌道（行が時刻、列が x, y, z）"""
    sol = solve_ivp(lorenz, (0, T), v0, args=(SIGMA, rho, BETA), t_eval=np.linspace(0, T, n),
                    rtol=1e-10, atol=1e-12)
    return sol.y.T'''),

md(r"""## 1. ストレンジアトラクタ

$(1,1,1)$ から $t=50$ まで追った軌道を、3次元で描きます（マウスで回転できます）。"""),

code(r'''P = trajectory(np.array([1.0, 1.0, 1.0]), 50.0)
fig = go.Figure(go.Scatter3d(x=P[:, 0].tolist(), y=P[:, 1].tolist(), z=P[:, 2].tolist(), mode="lines",
                             line=dict(color=np.linspace(0, 1, len(P)).tolist(), colorscale="Viridis", width=2)))
fig.update_layout(height=550, width=700, margin=dict(l=0, r=0, t=10, b=0),
                  scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"))
fig'''),

md(r"""**考えてみよう**

- 軌道は2つの「目」のまわりを回り、ときどき反対側に乗り移ります。乗り移るタイミングに、規則は見えるでしょうか。
- 軌道は決して交わりません（同じ点からは同じ未来しかない、という微分方程式の性質）。それなのに、有限の範囲に永遠に収まっています。どうしてそんなことが可能なのでしょうか（§4 の体積の縮みと、§1 の折りたたまれた形がヒントです）。"""),

md(r"""## 2. 近い2つの軌道は、指数関数的に離れる

アトラクタの上の点（$(1,1,1)$ から $t=20$ まで進めた点）と、そこから $10^{-9}$ だけずらした点の2つから始め、距離を対数目盛りで描きます。直線の部分の傾きが、最大のリアプノフ指数 $\lambda_1$ です（文献値は約 $0.906$）。"""),

code(r'''d0 = 1e-9
v0 = trajectory(np.array([1.0, 1.0, 1.0]), 20.0)[-1]   # アトラクタの上の点から始める
Pa = trajectory(v0, 40.0)
Pb = trajectory(v0 + np.array([d0, 0, 0]), 40.0)
t = np.linspace(0, 40.0, len(Pa))
dist = np.linalg.norm(Pa - Pb, axis=1)

mask = (t > 1) & (dist < 1e-1)
slope = np.polyfit(t[mask], np.log(dist[mask]), 1)[0]
print(f"傾き（λ₁ の推定）= {slope:.3f}（文献値 ≈ 0.906）")
assert 0.6 < slope < 1.2

fig = go.Figure(go.Scatter(x=t.tolist(), y=dist.tolist(), mode="lines", name="距離"))
fig.update_layout(height=360, width=750, yaxis_type="log", xaxis_title="時刻 t", yaxis_title="2つの軌道の距離",
                  margin=dict(t=20))
fig'''),

md(r"""## 3. 3つのリアプノフ指数（ベネッティンの方法）

小さな差 $\delta\mathbf v$ は、ヤコビ行列 $J$ で $\dot{\delta\mathbf v}=J(\mathbf v(t))\,\delta\mathbf v$ と運ばれます。3つの方向の差をまとめて行列 $Q$ に入れて運び、ときどき **QR 分解**で直交化し直します（そのままだと、すべての方向が最も伸びる方向に揃ってしまうため）。$R$ の対角成分の対数の平均が、3つのリアプノフ指数 $\lambda_1\ge\lambda_2\ge\lambda_3$ です。"""),

code(r'''def lyapunov_spectrum(v0: Floats, dt: float = 0.01, steps: int = 60000, renorm: int = 10,
                      transient: int = 2000) -> Floats:
    """軌道と接ベクトルを同時に 4 次のルンゲ・クッタで進め、QR 分解で直交化しながら指数を求める"""
    def rhs(v: Floats, Q: Floats) -> tuple[Floats, Floats]:
        return lorenz(0.0, v), jacobian(v) @ Q

    v, Q = v0.astype(float), np.eye(3)
    for _ in range(transient):                        # まずアトラクタの上に乗せる
        k1 = lorenz(0, v); k2 = lorenz(0, v + dt / 2 * k1); k3 = lorenz(0, v + dt / 2 * k2); k4 = lorenz(0, v + dt * k3)
        v = v + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    sums = np.zeros(3)
    for k in range(steps):
        a1 = rhs(v, Q)
        a2 = rhs(v + dt / 2 * a1[0], Q + dt / 2 * a1[1])
        a3 = rhs(v + dt / 2 * a2[0], Q + dt / 2 * a2[1])
        a4 = rhs(v + dt * a3[0], Q + dt * a3[1])
        v = v + dt / 6 * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0])
        Q = Q + dt / 6 * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1])
        if (k + 1) % renorm == 0:
            Q, R = np.linalg.qr(Q)
            sums += np.log(np.abs(np.diag(R)))
    return sums / (steps * dt)


lams = lyapunov_spectrum(np.array([1.0, 1.0, 1.0]))
print("リアプノフ指数 (λ₁, λ₂, λ₃) =", np.round(lams, 3), "（文献値 ≈ 0.906, 0, −14.57）")
print(f"指数の和 = {lams.sum():.4f}、−(σ + 1 + β) = {-(SIGMA + 1 + BETA):.4f}")
assert abs(lams[0] - 0.906) < 0.05 and abs(lams[1]) < 0.05
assert abs(lams.sum() + (SIGMA + 1 + BETA)) < 1e-2'''),

md(r"""**考えてみよう**

- 3つの指数は「正・ゼロ・負」です。正は「差が広がる方向」、負は「アトラクタに吸い寄せられる方向」です。ゼロの方向は何でしょうか（ヒント：同じ軌道の上で、時刻を少しずらした点との差）。
- 指数の和が $-(\sigma+1+\beta)$ にぴったり一致しました。次の節で理由を見ます。"""),

md(r"""## 4. 体積は縮み続ける：指数の和 = 発散

3つの方向の差が張る小さな箱の体積は、$\det Q$ に比例し、$\frac{d}{dt}\ln\det Q=\operatorname{tr}J$ で変わります（[det のノート](DETNOTE)の Jacobi の公式と補足2「トレースは体積の変化率」）。ローレンツ系のヤコビ行列のトレース（ベクトル場の発散）は、場所によらず

$$
\operatorname{tr}J=-\sigma-1-\beta=-13.67
$$

なので、体積は $e^{-13.67\,t}$ で縮みます。リアプノフ指数の和は、この縮む速さそのものです（[リー微分のノート](LIENOTE)の Part VIII「発散＝体積の変化率」の非線形版）。

下のセルで、アトラクタ上の点のまわりの小さな立方体（3本の辺）を運び、辺が張る平行六面体の体積（行列式）が縮む様子を、短い時間で確かめます。"""),

code(r'''# 小さな立方体の8つの頂点を運び、体積（平行六面体）の変化を測る
h = 1e-6
base = trajectory(np.array([1.0, 1.0, 1.0]), 20.0)[-1]          # アトラクタの上の点
edges = np.eye(3) * h
T_short, n_t = 0.3, 61
ts = np.linspace(0, T_short, n_t)
sol0 = solve_ivp(lorenz, (0, T_short), base, t_eval=ts, rtol=1e-12, atol=1e-14).y.T
vols = []
cols = [solve_ivp(lorenz, (0, T_short), base + e, t_eval=ts, rtol=1e-12, atol=1e-14).y.T for e in edges]
for k in range(n_t):
    M = np.stack([c[k] - sol0[k] for c in cols], axis=1)
    vols.append(abs(np.linalg.det(M)))
vols = np.array(vols) / h**3
rate = np.polyfit(ts, np.log(vols), 1)[0]
print(f"体積の対数の傾き = {rate:.3f}、tr J = −(σ+1+β) = {-(SIGMA + 1 + BETA):.3f}")
assert abs(rate + (SIGMA + 1 + BETA)) < 0.1

fig = go.Figure([go.Scatter(x=ts.tolist(), y=vols.tolist(), mode="lines+markers", name="体積（計算）"),
                 go.Scatter(x=ts.tolist(), y=np.exp(-(SIGMA + 1 + BETA) * ts).tolist(), mode="lines",
                            line=dict(dash="dash"), name="e^{tr J · t}")])
fig.update_layout(height=360, width=750, yaxis_type="log", xaxis_title="時刻 t", yaxis_title="体積（最初を 1 とする）",
                  margin=dict(t=20))
fig'''),

md(r"""**考えてみよう**

- 体積は縮み続けるのに、ある方向（$\lambda_1>0$）には伸び続けます。伸びながら全体としては縮むので、形は薄く引き伸ばされ、折りたたまれていきます。§1 のアトラクタの形を、この見方で眺め直してみましょう。
- ハミルトン系（摩擦のない力学系）では体積が保存され（リウヴィルの定理）、指数の和は $0$ になります。ローレンツ系の $\sigma,\ 1,\ \beta$ は、何に相当するでしょうか。"""),

md(r"""## 5. スライダー：$\rho$ を変えると

$\rho$（温度差の強さ）を変えると、振る舞いが変わります。

- $\rho<1$：原点に落ち着く
- $1<\rho<24.74$ くらい：2つの「目」の中心（不動点 $C_\pm$）のどちらかに、渦を巻きながら落ち着く（$\rho$ が 13.9 を超えると、しばらく迷走してから落ち着く）
- $\rho=28$：カオス"""),

code(r'''fig_rho = go.FigureWidget(go.Scatter3d(x=[], y=[], z=[], mode="lines", line=dict(color="#1f77b4", width=2)))
fig_rho.add_trace(go.Scatter3d(x=[], y=[], z=[], mode="markers", marker=dict(size=4, color="#d62728"), name="不動点 C±"))
fig_rho.update_layout(height=520, width=650, margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
                  scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z",
                             xaxis=dict(range=[-25, 25]), yaxis=dict(range=[-30, 30]), zaxis=dict(range=[0, 55])))
rho_slider = W.FloatSlider(value=28.0, min=0.5, max=35.0, step=0.5, description="ρ")
info = W.HTML()


def update(*_: object) -> None:
    """スライダーが動くたびに呼ばれ、軌道を計算し直す"""
    rho = rho_slider.value
    P = trajectory(np.array([1.0, 1.0, 1.0]), 40.0, rho=rho, n=4000)
    with fig_rho.batch_update():
        fig_rho.data[0].x, fig_rho.data[0].y, fig_rho.data[0].z = P[:, 0].tolist(), P[:, 1].tolist(), P[:, 2].tolist()
        if rho > 1:
            c = float(np.sqrt(BETA * (rho - 1)))
            fig_rho.data[1].x, fig_rho.data[1].y, fig_rho.data[1].z = [c, -c], [c, -c], [rho - 1, rho - 1]
        else:
            fig_rho.data[1].x, fig_rho.data[1].y, fig_rho.data[1].z = [0.0], [0.0], [0.0]
    end = P[-1]
    info.value = f"ρ = {rho}：最後の点 ({end[0]:+.2f}, {end[1]:+.2f}, {end[2]:+.2f})"


rho_slider.observe(update, "value")
update()
W.VBox([rho_slider, info, fig_rho])'''),

md(r"""## 観察のポイント（まとめ）

- 連続時間の3次元の系でも、近い軌道は指数関数的に離れます（$\lambda_1\approx0.906$）。
- 差の広がりはヤコビ行列で決まり、3つの方向の伸び縮みが、3つのリアプノフ指数になります。そのうち1つはゼロ（軌道に沿った方向）です。
- 指数の和は、ヤコビ行列のトレース（発散）の平均＝体積が縮む速さで、ローレンツ系では $-(\sigma+1+\beta)$ にぴったり一致しました。行列の「トレース＝体積の変化率」（det のノート）が、カオスの解析でも中心的な役割を果たしています。
- 伸びる方向と縮む方向があるので、軌道は有限の範囲に収まったまま、引き伸ばされて折りたたまれ、複雑な形（ストレンジアトラクタ）を作ります。

**この後**：これらの観察を、ノート（リアプノフ指数の定義、ヤコビ行列による線形化、体積の変化）にまとめます。"""),
]

save("01_logistic_map.ipynb", nb1)
save("02_lorenz.ipynb", nb2)
