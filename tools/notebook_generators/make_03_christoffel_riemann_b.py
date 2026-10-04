"""インタラクティブな Jupyter ノートブック3本（03〜05）を生成する（出力なしで保存する）。"""
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell as cd, new_markdown_cell as md, new_notebook

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
NOTE = "../../../研究ノート/02_微分幾何/christoffel_riemann_intro.md"


def save(name, cells):
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbformat.write(nb, OUT / name)
    print("書き出し:", OUT / name)


# =====================================================================================
# 3. 極座標の基底ベクトルと Γ
# =====================================================================================
nb3 = [
    md(f"""# 極座標の基底ベクトルと、クリストッフェル記号 $\\Gamma$

[クリストッフェル記号とリーマン曲率テンソルのノート]({NOTE}#p6)（Part VI）の計算を、点を動かして確かめます。

**クリストッフェル記号の定義**は、基底ベクトルの変化率を、基底で展開した係数でした：

$$
\\frac{{\\partial\\mathbf e_i}}{{\\partial q^j}}=\\Gamma^k{{}}_{{ij}}\\,\\mathbf e_k
$$

極座標 $(r,\\theta)$ では、$\\mathbf e_r=(\\cos\\theta,\\sin\\theta)$、$\\mathbf e_\\theta=r(-\\sin\\theta,\\cos\\theta)$ で、ゼロでない $\\Gamma$ は
$\\Gamma^r{{}}_{{\\theta\\theta}}=-r$、$\\Gamma^\\theta{{}}_{{r\\theta}}=\\Gamma^\\theta{{}}_{{\\theta r}}=1/r$ の3つだけです。

**使い方**：スライダーで点 $P$ を動かし、「動かす方向」を切り替えます。矢印の見方は、図の下に書いてあります。このノートブックは、ウィジェットを使うので、カーネルを動かして実行してください。"""),
    cd("""import numpy as np
import sympy as sp
import plotly.graph_objects as go
import ipywidgets as W
from IPython.display import display"""),
    md("""## 検算 1：$\\Gamma$ を、基底ベクトルの微分から求める

SymPy で、定義 $\\partial_j\\mathbf e_i=\\Gamma^k{}_{ij}\\mathbf e_k$ から $\\Gamma$ を計算します。"""),
    cd("""r, th = sp.symbols("r theta", positive=True)
X = sp.Matrix([r * sp.cos(th), r * sp.sin(th)])
e = [X.diff(r), X.diff(th)]                  # e_r, e_θ（デカルト成分）
Jm = sp.Matrix.hstack(*e)                    # 列が基底ベクトル
coords, names = [r, th], ["r", "θ"]

Gamma = {}
for j, q in enumerate(coords):
    for i in range(2):
        coef = sp.simplify(Jm.inv() * e[i].diff(q))   # ∂_j e_i を (e_r, e_θ) で展開した係数 = Γ^k_{ij}
        for k in range(2):
            Gamma[(k, i, j)] = coef[k]

for (k, i, j), val in Gamma.items():
    if val != 0:
        print(f"Γ^{names[k]}_{{{names[i]}{names[j]}}} = {val}")

assert Gamma[(0, 1, 1)] == -r and Gamma[(1, 0, 1)] == 1 / r and Gamma[(1, 1, 0)] == 1 / r
assert sum(1 for v in Gamma.values() if v != 0) == 3"""),
    md("""## 検算 2：数値でも確かめる

基底ベクトルを数値的に微分（中心差分）して、$\\Gamma$ による展開と一致することを、いくつかの点で確かめます。"""),
    cd("""def basis(r0, t0):
    return np.array([np.cos(t0), np.sin(t0)]), r0 * np.array([-np.sin(t0), np.cos(t0)])


def gamma_expansion(r0, t0, j):
    \"\"\"∂_j e_i = Γ^k_{ij} e_k を、解析的な Γ で作る（i = r, θ の2つを返す）\"\"\"
    er, eth = basis(r0, t0)
    Gv = {(0, 1, 1): -r0, (1, 0, 1): 1 / r0, (1, 1, 0): 1 / r0}
    E = [er, eth]
    return [sum(Gv.get((k, i, j), 0.0) * E[k] for k in range(2)) for i in range(2)]


rng = np.random.default_rng(0)
h = 1e-6
for _ in range(5):
    r0, t0 = rng.uniform(0.5, 3), rng.uniform(0, 2 * np.pi)
    for j in range(2):
        dr, dt = (h, 0) if j == 0 else (0, h)
        num = [(a - b) / (2 * h) for a, b in zip(basis(r0 + dr, t0 + dt), basis(r0 - dr, t0 - dt))]
        exp = gamma_expansion(r0, t0, j)
        for i in range(2):
            assert np.allclose(num[i], exp[i], atol=1e-6), (r0, t0, i, j)
print("数値微分と Γ による展開が、すべての点で一致しました")"""),
    md("""## 点を動かして見る

- **青**：$\\mathbf e_r$（長さ 1）　**赤**：$\\mathbf e_\\theta$（長さ $r$）
- **緑**：$\\mathbf e_r$ の変化率 $\\partial_j\\mathbf e_r$　**紫**：$\\mathbf e_\\theta$ の変化率 $\\partial_j\\mathbf e_\\theta$（どちらも、対応する基底ベクトルの先端から描いています）
- 変化率の矢印は、基底の言葉に直すと、$\\Gamma$ を係数とする組み合わせです。図の下に、その係数を表示します。"""),
    cd("""MODES = ["θ 方向に動く（∂_θ）", "r 方向に動く（∂_r）"]


def arrow(p, q):
    return [p[0], q[0]], [p[1], q[1]]


def state(r0, t0, mode):
    \"\"\"各トレースの座標と、説明文を返す\"\"\"
    P = np.array([r0 * np.cos(t0), r0 * np.sin(t0)])
    er, eth = basis(r0, t0)
    j = 1 if mode == MODES[0] else 0                       # 動かす方向の添字（0: r, 1: θ）
    d_er, d_eth = gamma_expansion(r0, t0, j)               # ∂_j e_r, ∂_j e_θ
    ang = np.linspace(0, 2 * np.pi, 200)
    coords = [
        (r0 * np.cos(ang), r0 * np.sin(ang)),                                 # r = 一定の円
        ([0, 3.4 * np.cos(t0)], [0, 3.4 * np.sin(t0)]),                       # θ = 一定の半直線
        arrow(P, P + er), arrow(P, P + eth),
        arrow(P + er, P + er + d_er), arrow(P + eth, P + eth + d_eth),
    ]
    if j == 1:
        text = (f"∂_θ e_r = Γ^θ_{{rθ}} e_θ = (1/r) e_θ = {1 / r0:+.3f} e_θ　　　"
                f"∂_θ e_θ = Γ^r_{{θθ}} e_r = −r e_r = {-r0:+.3f} e_r")
    else:
        text = (f"∂_r e_r = 0　　　"
                f"∂_r e_θ = Γ^θ_{{θr}} e_θ = (1/r) e_θ = {1 / r0:+.3f} e_θ")
    return coords, f"<b>r = {r0:.2f}, θ = {np.degrees(t0):.0f}°</b>　{text}"


def new_arrow_trace(color, name):
    return go.Scatter(x=[0, 0], y=[0, 0], mode="lines+markers", line=dict(color=color, width=4),
                      marker=dict(symbol="arrow", size=[0, 14], angleref="previous", color=color), name=name)


fig = go.FigureWidget(data=[
    go.Scatter(x=[], y=[], mode="lines", line=dict(color="#aaa", dash="dot"), name="r = 一定", hoverinfo="skip"),
    go.Scatter(x=[], y=[], mode="lines", line=dict(color="#aaa", dash="dash"), name="θ = 一定", hoverinfo="skip"),
    new_arrow_trace("#1f77b4", "e_r"),
    new_arrow_trace("#d62728", "e_θ（長さ r）"),
    new_arrow_trace("#2ca02c", "e_r の変化率"),
    new_arrow_trace("#9467bd", "e_θ の変化率"),
])
fig.add_trace(go.Scatter(x=[-3.6, 3.6], y=[0, 0], mode="lines", line=dict(color="#ddd", width=1), showlegend=False, hoverinfo="skip"))
fig.add_trace(go.Scatter(x=[0, 0], y=[-3.6, 3.6], mode="lines", line=dict(color="#ddd", width=1), showlegend=False, hoverinfo="skip"))
fig.update_layout(height=560, width=620, margin=dict(l=20, r=20, t=20, b=20),
                  xaxis=dict(range=[-3.6, 3.6], zeroline=False), yaxis=dict(range=[-3.6, 3.6], scaleanchor="x", zeroline=False),
                  legend=dict(orientation="h", y=-0.05))

r_slider = W.FloatSlider(value=1.5, min=0.4, max=2.5, step=0.05, description="r", continuous_update=True)
t_slider = W.FloatSlider(value=40, min=0, max=360, step=5, description="θ [度]", continuous_update=True)
mode_sel = W.ToggleButtons(options=MODES, description="動かす方向")
label = W.HTML()


def update(*_):
    coords, text = state(r_slider.value, np.radians(t_slider.value), mode_sel.value)
    with fig.batch_update():
        for tr, (x, y) in zip(fig.data[:6], coords):
            tr.x, tr.y = list(x), list(y)
    label.value = text


for w in (r_slider, t_slider, mode_sel):
    w.observe(update, names="value")
update()
display(W.VBox([mode_sel, r_slider, t_slider, fig, label]))"""),
    md("""## 観察のポイント

- **θ 方向に動く**：緑の矢印（$\\partial_\\theta\\mathbf e_r$）は、$\\mathbf e_\\theta$ と同じ向きです。点が円に沿って動くと、$\\mathbf e_r$ の向きは、円の接線方向へ回ります。係数は $\\Gamma^\\theta{}_{r\\theta}=1/r$ で、$r$ が小さいほど速く回ります。
- **θ 方向に動く**：紫の矢印（$\\partial_\\theta\\mathbf e_\\theta$）は、原点を向きます（$-r\\,\\mathbf e_r$）。これが $\\Gamma^r{}_{\\theta\\theta}=-r$ で、ノートの Part VI §1 の計算です。
- **r 方向に動く**：$\\mathbf e_r$ は変わらず（$\\partial_r\\mathbf e_r=0$）、$\\mathbf e_\\theta$ は向きを変えずに長くなります（$\\partial_r\\mathbf e_\\theta=\\mathbf e_\\theta/r$）。
- 平面は平坦です。$\\Gamma\\ne0$ でも、曲率は 0 です（Part VI §3）。基底ベクトルが回って見えるのは、座標の取り方のせいです。"""),
]
save("03_polar_basis_christoffel.ipynb", nb3)

# =====================================================================================
# 4. 球面と双曲面の比較
# =====================================================================================
nb4 = [
    md(f"""# 球面と双曲面：$\\varepsilon=\\pm1$ でガウス曲率の符号が変わる

[ノート]({NOTE}#C-1-4)（付録C-1-4）の比較を、3Dで見ます。

どちらも、第二基本形式が $K_{{ij}}=-g_{{ij}}/a$ という同じ形ですが、

- **球面**（$\\mathbb R^3$ の中、$\\varepsilon=\\bar g(n,n)=+1$）：$K_{{\\mathrm G}}=+1/a^2$
- **双曲面**（ミンコフスキー空間 $(t,x,y)$ の中、$\\varepsilon=-1$）：$K_{{\\mathrm G}}=-1/a^2$

です。法線の長さの符号が、ガウス曲率の符号を決めています。

**使い方**：下部のスライダーで $a$ を変えます。3D の図は、ドラッグで回転、ホイールで拡大できます。"""),
    cd("""import numpy as np
import sympy as sp
import plotly.graph_objects as go
from plotly.subplots import make_subplots"""),
    md("""## 検算：同じ手順で、2つの曲面の $\\varepsilon$ と $K_{\\mathrm G}$ を求める

どちらの曲面も、埋め込み $X(u,v)$ と、外側の計量 $G$（球面は単位行列、双曲面は $\\mathrm{diag}(-1,1,1)$）を与えるだけで、次を SymPy が計算します。

1. 誘導計量 $g_{ij}=G(e_i,e_j)$、法線 $n=X/a$ と $\\varepsilon=G(n,n)$
2. 外的曲率 $K_{ij}=G(\\partial_i\\partial_jX,\\ n)$
3. ガウス方程式（外側が平坦）から $K_{\\mathrm G}=\\varepsilon\\,\\det K/\\det g$
4. 計量だけからのクリストッフェル記号とリーマン曲率テンソルによる $K_{\\mathrm G}$（独立な計算）

3 と 4 が一致すること、さらにハミルトン拘束 $\\varepsilon R=(\\operatorname{tr}K)^2-K_{ij}K^{ij}$（外側が平坦なので、$\\bar G_{{nn}}=0$）が成り立つことを確かめます。"""),
    cd("""a_ = sp.symbols("a", positive=True)
u, v = sp.symbols("u v", real=True)


def analyze(X, G, label):
    X = sp.Matrix(X)
    G = sp.Matrix(G)
    e = [X.diff(u), X.diff(v)]
    ip = lambda p, q: sp.simplify((p.T * G * q)[0])
    g = sp.Matrix(2, 2, lambda i, j: ip(e[i], e[j]))
    n = X / a_
    eps = ip(n, n)
    assert ip(n, e[0]) == 0 and ip(n, e[1]) == 0
    K = sp.Matrix(2, 2, lambda i, j: ip(X.diff([u, v][i]).diff([u, v][j]), n))
    KG_gauss = sp.simplify(eps * K.det() / g.det())
    # 計量だけから（Christoffel → Riemann）
    ginv, q = g.inv(), [u, v]
    Gam = [[[sp.simplify(sum(ginv[k, l] * (g[l, i].diff(q[j]) + g[l, j].diff(q[i]) - g[i, j].diff(q[l])) for l in range(2)) / 2)
             for j in range(2)] for i in range(2)] for k in range(2)]
    def Riem(l, k, i, j):
        t = Gam[l][j][k].diff(q[i]) - Gam[l][i][k].diff(q[j])
        t += sum(Gam[l][i][m] * Gam[m][j][k] - Gam[l][j][m] * Gam[m][i][k] for m in range(2))
        return sp.simplify(t)
    R1212 = sp.simplify(sum(g[0, m] * Riem(m, 1, 0, 1) for m in range(2)))
    KG_metric = sp.simplify(R1212 / g.det())
    Ric = sp.Matrix(2, 2, lambda k, j: sp.simplify(sum(Riem(i, k, i, j) for i in range(2))))
    R = sp.simplify(sum(ginv[i, j] * Ric[i, j] for i in range(2) for j in range(2)))
    S = ginv * K
    trK = sp.simplify(S.trace())
    KK = sp.simplify((S * S).trace())
    assert sp.simplify(KG_gauss - KG_metric) == 0
    assert sp.simplify(eps * R - (trK**2 - KK)) == 0
    print(f"{label}:  ε = {eps},  K_G = {KG_gauss}（ガウス方程式）= {KG_metric}（計量だけ）,  "
          f"R = {R},  tr K = {trK},  K_ij K^ij = {KK}")
    return eps, KG_gauss


th_, ph_, chi_ = sp.symbols("theta phi chi", real=True)
u, v = th_, ph_
eps_s, KG_s = analyze([a_ * sp.sin(u) * sp.cos(v), a_ * sp.sin(u) * sp.sin(v), a_ * sp.cos(u)], sp.eye(3), "球面（R^3）")
u, v = chi_, ph_
eps_h, KG_h = analyze([a_ * sp.cosh(u), a_ * sp.sinh(u) * sp.cos(v), a_ * sp.sinh(u) * sp.sin(v)], sp.diag(-1, 1, 1), "双曲面（ミンコフスキー空間）")
assert eps_s == 1 and eps_h == -1 and sp.simplify(KG_s - 1 / a_**2) == 0 and sp.simplify(KG_h + 1 / a_**2) == 0"""),
    md("""## スライダーで動かす

左が球面（$\\mathbb R^3$）、右が双曲面（ミンコフスキー空間。縦軸が時間 $t$、黄色は光円錐）です。紫の矢印は、点 $X$ での単位法線 $n=X/a$ です。"""),
    cd("""a_vals = np.round(np.arange(0.6, 2.01, 0.1), 2)
ph = np.linspace(0, 2 * np.pi, 60)


def surfaces(a):
    uu, pp = np.meshgrid(np.linspace(0, np.pi, 40), ph, indexing="ij")
    S = (a * np.sin(uu) * np.cos(pp), a * np.sin(uu) * np.sin(pp), a * np.cos(uu))
    cc, pp = np.meshgrid(np.linspace(0, 1.0, 30), ph, indexing="ij")
    H = (a * np.sinh(cc) * np.cos(pp), a * np.sinh(cc) * np.sin(pp), a * np.cosh(cc))     # (x, y, t)
    return S, H


def normals(a):
    \"\"\"双曲面・球面の上の数点での単位法線 n = X/a（長さ 0.6 の線分に描く）\"\"\"
    pts_s, pts_h = [], []
    for t_, p_ in [(0.9, 0.3), (1.6, 2.0), (2.3, 4.0)]:
        X = a * np.array([np.sin(t_) * np.cos(p_), np.sin(t_) * np.sin(p_), np.cos(t_)])
        pts_s.append((X, X + 0.6 * X / a))
    for c_, p_ in [(0.3, 0.3), (0.6, 2.0), (0.95, 4.0)]:
        X = a * np.array([np.sinh(c_) * np.cos(p_), np.sinh(c_) * np.sin(p_), np.cosh(c_)])
        pts_h.append((X, X + 0.6 * X / a))
    def gaps(rows):
        xs, ys, zs = [], [], []
        for p, q in rows:
            xs += [p[0], q[0], None]; ys += [p[1], q[1], None]; zs += [p[2], q[2], None]
        return xs, ys, zs
    return gaps(pts_s), gaps(pts_h)


def traces(a):
    (Sx, Sy, Sz), (Hx, Hy, Hz) = surfaces(a)
    ns, nh = normals(a)
    return [
        go.Surface(x=Sx, y=Sy, z=Sz, surfacecolor=np.ones_like(Sx), colorscale=[[0, "#8ec1e8"], [1, "#8ec1e8"]], showscale=False, opacity=0.85),
        go.Scatter3d(x=ns[0], y=ns[1], z=ns[2], mode="lines", line=dict(color="#7b2fbf", width=6), showlegend=False),
        go.Surface(x=Hx, y=Hy, z=Hz, surfacecolor=np.ones_like(Hx), colorscale=[[0, "#f0a35e"], [1, "#f0a35e"]], showscale=False, opacity=0.9),
        go.Scatter3d(x=nh[0], y=nh[1], z=nh[2], mode="lines", line=dict(color="#7b2fbf", width=6), showlegend=False),
    ]


# 光円錐（固定）
rr, pp = np.meshgrid(np.linspace(0, 3.4, 12), ph, indexing="ij")
cone_top = go.Surface(x=rr * np.cos(pp), y=rr * np.sin(pp), z=rr, opacity=0.15, showscale=False,
                      colorscale=[[0, "#f2d600"], [1, "#f2d600"]], hoverinfo="skip")

frames, steps = [], []
for a in a_vals:
    name = f"{a:.1f}"
    frames.append(go.Frame(data=traces(a), traces=[0, 1, 3, 4], name=name,
                           layout=go.Layout(title_text=f"a = {a:.1f}：球面 ε=+1, K_G=+{1 / a**2:.2f}　　双曲面 ε=−1, K_G=−{1 / a**2:.2f}")))
    steps.append(dict(method="animate", label=name,
                      args=[[name], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))]))

k0 = int(np.argmin(np.abs(a_vals - 1.0)))
fig = make_subplots(rows=1, cols=2, specs=[[{"type": "scene"}, {"type": "scene"}]],
                    subplot_titles=["球面（R³）", "双曲面（ミンコフスキー空間, 縦軸 t）"])
t0 = traces(a_vals[k0])
fig.add_trace(t0[0], row=1, col=1); fig.add_trace(t0[1], row=1, col=1)
fig.add_trace(cone_top, row=1, col=2)
fig.add_trace(t0[2], row=1, col=2); fig.add_trace(t0[3], row=1, col=2)
fig.frames = frames
rng_ = dict(range=[-2.8, 2.8], visible=False)
fig.update_layout(
    title_text=frames[k0].layout.title.text,
    sliders=[dict(active=k0, currentvalue=dict(prefix="a = "), pad=dict(t=30), steps=steps)],
    scene=dict(aspectmode="cube", xaxis=rng_, yaxis=rng_, zaxis=rng_, camera=dict(eye=dict(x=1.4, y=1.2, z=0.9))),
    scene2=dict(aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.7), xaxis=rng_, yaxis=rng_,
                zaxis=dict(range=[-0.3, 3.6], visible=False), camera=dict(eye=dict(x=1.5, y=1.3, z=0.8))),
    height=650, margin=dict(l=0, r=0, t=90, b=0),
)
fig.show()"""),
    md("""## 観察のポイント

- 球面では、単位法線 $n=X/a$ は外向きで、$\\bar g(n,n)=+1$ です。双曲面では、$n=X/a$ は時間方向（光円錐の内側）で、$\\bar g(n,n)=-1$ です。
- 検算の出力のとおり、どちらも $K_{ij}=-g_{ij}/a$ の形ですが、ガウス方程式（C.5）の $KK$ の項に $\\varepsilon$ が付くので、$K_{\\mathrm G}$ の符号が変わります。
- $a$ を大きくすると、どちらも曲率 $|K_{\\mathrm G}|=1/a^2$ が小さくなり、平面に近づきます。
- ハミルトン拘束（外側が平坦）の $\\varepsilon R=(\\operatorname{tr}K)^2-K_{ij}K^{ij}$ が、球面と双曲面の両方で成り立つことも、検算セルで確かめました。"""),
]
save("04_sphere_vs_hyperboloid.ipynb", nb4)

# =====================================================================================
# 5. ガウス正規座標
# =====================================================================================
nb5 = [
    md(f"""# ガウス正規座標：断面の曲がり具合と、測地線の間隔

[ノート]({NOTE}#C-3-1)（付録C-3-1）の、外的曲率 $K_{{ij}}=-\\tfrac12\\partial_\\tau g_{{ij}}$ を、動かして確かめます。

平坦な時空 $(y,t)$（計量 $dy^2-dt^2$）で、曲がった断面 $\\Sigma:\\ t=\\kappa y^2$ を取り、断面の各点から**法線方向に測地線**（直線）を伸ばします。隣り合う測地線の間隔が、固有時間 $\\tau$ とともにどう変わるかが、外的曲率 $K$ です。

**使い方**：下部のスライダーで、断面の曲がり具合 $\\kappa$ を変えます。"""),
    cd("""import numpy as np
import sympy as sp
import plotly.graph_objects as go
from plotly.subplots import make_subplots"""),
    md("""## 検算：$K=-\\tfrac12\\partial_\\tau g$ を、SymPy で確かめる

断面 $X(y)=(y,\\kappa y^2)$（成分は $(y,t)$）、計量 $G=\\mathrm{diag}(1,-1)$、単位法線 $n\\propto(2\\kappa y,\\ 1)$ から、測地線 $F(y,\\tau)=X(y)+\\tau\\,n(y)$ を作ります。

- 外的曲率の定義：$K=G(X'',\\,n)$
- ガウス正規座標の誘導計量：$g(y,\\tau)=G(\\partial_yF,\\partial_yF)$

が、$K=-\\tfrac12\\partial_\\tau g|_{\\tau=0}$ を満たすことを確かめます。"""),
    cd("""y, tau, kap = sp.symbols("y tau kappa", real=True)
G = sp.diag(1, -1)
ip = lambda p, q: sp.simplify((p.T * G * q)[0])
X = sp.Matrix([y, kap * y**2])
e = X.diff(y)
n = sp.Matrix([2 * kap * y, 1]) / sp.sqrt(1 - 4 * kap**2 * y**2)
assert sp.simplify(ip(n, e)) == 0 and sp.simplify(ip(n, n) + 1) == 0     # 法線は断面と直交し、ε = −1

K = ip(X.diff(y, 2), n)
F = X + tau * n
g_tau = sp.simplify(ip(F.diff(y), F.diff(y)))
dg = sp.simplify(g_tau.diff(tau).subs(tau, 0))
print("K =", sp.simplify(K))
print("g(y, τ) =", g_tau)
assert sp.simplify(K + dg / 2) == 0
print("K = −(1/2) ∂τ g が一致しました")
g0 = sp.simplify(g_tau.subs(y, 0))
print("y = 0 では g(τ) =", sp.factor(g0))
assert sp.simplify(g0 - (1 + 2 * kap * tau) ** 2) == 0"""),
    md("""## スライダーで動かす

- **左**：$(y,t)$ の時空図です。黒が断面 $\\Sigma$、青が法線方向の測地線、灰色の曲線が $\\tau=0.5,1.0,\\dots$ の断面です。
- **右**：$y=0$ の隣り合う測地線の間隔 $g(\\tau)=(1+2\\kappa\\tau)^2$ です。点線は $\\tau=0$ での接線で、傾きが $-2K=4\\kappa$ です。
- $\\kappa<0$ では、測地線がやがて交わります（焦点 $\\tau=1/(2|\\kappa|)$）。この点で $g=0$ となり、ガウス正規座標は、その手前までしか使えません。"""),
    cd("""kappas = np.round(np.arange(-0.5, 0.501, 0.05), 2) + 0.0     # −0.00 の表示を避ける
ys = np.linspace(-0.8, 0.8, 9)
T = 1.6


def Fxy(kappa, y0, tau):
    nrm = np.sqrt(1 - 4 * kappa**2 * y0**2)
    return y0 + tau * 2 * kappa * y0 / nrm, kappa * y0**2 + tau / nrm


def gaps(rows):
    xs, zs = [], []
    for xx, zz in rows:
        xs += list(xx) + [None]; zs += list(zz) + [None]
    return xs, zs


def build(kappa):
    yy = np.linspace(-0.8, 0.8, 200)
    sigma = (yy, kappa * yy**2)
    taus = np.linspace(0, T, 50)
    geo = gaps([Fxy(kappa, y0, taus) for y0 in ys])
    slices = gaps([Fxy(kappa, yy, tt) for tt in [0.5, 1.0, 1.5]])
    gtau = (1 + 2 * kappa * taus) ** 2
    slope = (1 + 4 * kappa * taus)
    left = [
        go.Scatter(x=geo[0], y=geo[1], mode="lines", line=dict(color="#1f77b4", width=1.5), name="法線方向の測地線"),
        go.Scatter(x=slices[0], y=slices[1], mode="lines", line=dict(color="#999", width=1), name="τ = 一定の断面"),
        go.Scatter(x=sigma[0], y=sigma[1], mode="lines", line=dict(color="#222", width=4), name="断面 Σ"),
    ]
    right = [
        go.Scatter(x=taus, y=gtau, mode="lines", line=dict(color="#d62728", width=3), name="g(τ)"),
        go.Scatter(x=taus, y=slope, mode="lines", line=dict(color="#444", dash="dot"), name="τ=0 での接線（傾き −2K）"),
    ]
    K = -2 * kappa
    title = f"κ = {kappa:+.2f}　K = −2κ = {K:+.2f}　∂τg(0) = −2K = {-2 * K:+.2f}"
    if kappa < 0:
        title += f"　焦点 τ = {1 / (2 * abs(kappa)):.2f}"
    return left + right, title


frames, steps = [], []
for kp in kappas:
    tr, title = build(kp)
    name = f"{kp:+.2f}"
    frames.append(go.Frame(data=tr, traces=[0, 1, 2, 3, 4], name=name, layout=go.Layout(title_text=title)))
    steps.append(dict(method="animate", label=name,
                      args=[[name], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))]))

k0 = int(np.argmin(np.abs(kappas - 0.4)))
tr0, title0 = build(kappas[k0])
fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.1,
                    subplot_titles=["(y, t) 時空図", "y = 0 の測地線の間隔 g(τ)"])
for t_ in tr0[:3]:
    fig.add_trace(t_, row=1, col=1)
for t_ in tr0[3:]:
    fig.add_trace(t_, row=1, col=2)
fig.frames = frames
fig.update_xaxes(title_text="y", range=[-1.2, 1.2], row=1, col=1)
fig.update_yaxes(title_text="t", range=[-0.6, 2.4], scaleanchor="x", scaleratio=1, row=1, col=1)
fig.update_xaxes(title_text="τ", range=[0, T], row=1, col=2)
fig.update_yaxes(title_text="g", range=[0, 7], row=1, col=2)
fig.update_layout(title_text=title0, sliders=[dict(active=k0, currentvalue=dict(prefix="κ = "), pad=dict(t=30), steps=steps)],
                  height=600, margin=dict(l=40, r=20, t=90, b=0), legend=dict(orientation="h", y=-0.28))
fig.show()"""),
    md("""## 観察のポイント

- $\\kappa>0$（断面が上に曲がる）では、測地線が外へ広がり、$g(\\tau)$ は増えます。$\\partial_\\tau g>0$ なので、$K=-\\tfrac12\\partial_\\tau g<0$ です。ノートのアニメ（anim06、$\\kappa=0.4$）と同じ値 $K=-0.8$ です。
- $\\kappa<0$ では、測地線が集まり、$g(\\tau)$ が 0 に向かいます。
- $\\kappa=0$（平らな断面）では、測地線は平行で、$g(\\tau)=1$ のままです。$K=0$ です。
- 外的曲率 $K_{ij}$ は、「断面が、時間方向へどれだけ広がるか」を測る量です。付録Cの拘束条件と発展方程式は、この量 $K_{ij}$ を、時間発展する変数として扱います。"""),
]
save("05_gaussian_normal_coordinates.ipynb", nb5)
