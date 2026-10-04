"""インタラクティブな Jupyter ノートブック2本を生成する（出力なしで保存する）。"""
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
NOTE = "../../../研究ノート/02_微分幾何/christoffel_riemann_intro.md"


def save(name, cells):
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nbformat.write(nb, OUT / name)
    print("書き出し:", OUT / name)


# =====================================================================================
# 1. 球面上の並行移動
# =====================================================================================
md = new_markdown_cell
cd = new_code_cell

nb1 = [
    md(f"""# 球面上の並行移動：スライダーで回転角を見る

[クリストッフェル記号とリーマン曲率テンソルのノート]({NOTE}#p7-3)（Part VII §3）の並行移動を、スライダーで動かして確かめます。

**設定**（単位球）：北極 N → 赤道上の点 A（経度 0）→ 赤道上の点 B（経度 Δφ）→ 北極 N と、測地線（大円）だけで三角形を一周します。ベクトルは、各ステップで新しい点の接平面に射影し、長さを1に戻す方法で運びます（離散的な並行移動）。

**確かめること**：一周して戻ったベクトルの回転角は、三角形の面積 × ガウス曲率（単位球なら $K=1$）に一致します。この三角形の面積は、球面三角形の角の和の余りから Δφ です。

**使い方**：下の図の下部にあるスライダーで、Δφ を変えます。3D の図は、マウスのドラッグで回転、ホイールで拡大できます。"""),
    cd("""import numpy as np
import plotly.graph_objects as go


def sph(th, ph):
    \"\"\"単位球面上の点（th: 北極からの角、ph: 経度）\"\"\"
    return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])


def triangle_path(dphi, n=400):
    \"\"\"N → A（赤道, 経度0）→ B（赤道, 経度 dphi）→ N。各区間を n 分割した点列を返す\"\"\"
    pts = [sph(s, 0.0) for s in np.linspace(0, np.pi / 2, n, endpoint=False)]
    pts += [sph(np.pi / 2, s) for s in np.linspace(0, dphi, n, endpoint=False)]
    pts += [sph(s, dphi) for s in np.linspace(np.pi / 2, 0, n + 1)]
    return np.array(pts)


def transport(P, v0):
    \"\"\"各ステップで、ベクトルを新しい点の接平面に射影して正規化する\"\"\"
    V = [v0]
    for p in P[1:]:
        v = V[-1] - np.dot(V[-1], p) * p
        V.append(v / np.linalg.norm(v))
    return np.array(V)


def holonomy(v0, v1, normal=np.array([0.0, 0.0, 1.0])):
    \"\"\"v0 から v1 への、normal の周りの符号付き回転角（外側から見て反時計回りが正）\"\"\"
    return np.arctan2(normal @ np.cross(v0, v1), v0 @ v1)


def initial_vector(psi):
    \"\"\"北極 N での接ベクトル。psi は x 軸（A の方向）からの角\"\"\"
    return np.array([np.cos(psi), np.sin(psi), 0.0])"""),
    md("""## 数値で確認する

まず、スライダーを使わずに、回転角が Δφ（= $K$ × 面積）に一致することと、初期ベクトルの向き ψ に依らないことを確かめます。離散化の誤差は、分割数を増やすと小さくなります。"""),
    cd("""print("   Δφ      ψ     回転角   K×面積   差")
for dphi in [0.5, 1.0, np.pi / 2, 2.5]:
    for psi in [0.0, 0.7, 2.0]:
        P = triangle_path(dphi, n=1500)
        v0 = initial_vector(psi)
        V = transport(P, v0)
        hol = holonomy(v0, V[-1])
        print(f"{dphi:6.3f}  {psi:5.2f}  {hol:7.4f}  {dphi:7.4f}  {hol - dphi:+.4f}")
        assert abs(hol - dphi) < 3e-3"""),
    md("""## スライダーで動かす

下の図で、Δφ のスライダーを動かします。

- **青い矢印**：北極 N から出発するときのベクトル
- **赤い矢印**：一周して N に戻ってきたときのベクトル
- **橙の矢印**：経路の途中の、運ばれているベクトル
- 図の題名に、回転角と $K\\times$面積 を表示します"""),
    cd("""PSI = 0.7  # 出発時のベクトルの向き（x 軸からの角）。変えても回転角は変わらない
dphis = np.sort(np.append(np.arange(0.3, 3.01, 0.1), np.pi / 2))


def with_gaps(rows):
    \"\"\"[(始点, 終点), ...] を、線が途切れる None を挟んだ座標列にする\"\"\"
    xs, ys, zs = [], [], []
    for a, b in rows:
        xs += [a[0], b[0], None]
        ys += [a[1], b[1], None]
        zs += [a[2], b[2], None]
    return xs, ys, zs


def frame_traces(dphi, n=1200, stride=150, L=0.28):
    P = triangle_path(dphi, n)
    v0 = initial_vector(PSI)
    V = transport(P, v0)
    hol = holonomy(v0, V[-1])
    idx = np.arange(0, len(P), stride)
    shafts = with_gaps([(P[k], P[k] + L * V[k]) for k in idx])
    tips = np.array([P[k] + L * V[k] for k in idx])
    N = np.array([0.0, 0.0, 1.0])
    a_vec = (N, N + 0.55 * v0)
    b_vec = (N, N + 0.55 * V[-1])
    verts = np.array([N, sph(np.pi / 2, 0.0), sph(np.pi / 2, dphi)])
    title = (f"Δφ = {np.degrees(dphi):.0f}°　回転角 = {np.degrees(hol):.1f}°　"
             f"（K×面積 = {np.degrees(dphi):.1f}°）")
    traces = [
        go.Scatter3d(x=P[:, 0], y=P[:, 1], z=P[:, 2], mode="lines", line=dict(color="#222", width=4), name="経路"),
        go.Scatter3d(x=shafts[0], y=shafts[1], z=shafts[2], mode="lines", line=dict(color="#e67e00", width=5),
                     name="運ばれるベクトル"),
        go.Scatter3d(x=tips[:, 0], y=tips[:, 1], z=tips[:, 2], mode="markers",
                     marker=dict(size=2, color="#e67e00"), showlegend=False),
        go.Scatter3d(x=[a_vec[0][0], a_vec[1][0]], y=[a_vec[0][1], a_vec[1][1]], z=[a_vec[0][2], a_vec[1][2]],
                     mode="lines+markers", line=dict(color="#1f77b4", width=8),
                     marker=dict(size=[0, 5], color="#1f77b4"), name="出発時"),
        go.Scatter3d(x=[b_vec[0][0], b_vec[1][0]], y=[b_vec[0][1], b_vec[1][1]], z=[b_vec[0][2], b_vec[1][2]],
                     mode="lines+markers", line=dict(color="#d62728", width=8),
                     marker=dict(size=[0, 5], color="#d62728"), name="一周後"),
        go.Scatter3d(x=verts[:, 0], y=verts[:, 1], z=verts[:, 2], mode="markers+text", text=["N", "A", "B"],
                     textposition="top center", marker=dict(size=4, color="#222"), showlegend=False),
    ]
    return traces, title


# 球面（固定）
u, v = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(0, 2 * np.pi, 80), indexing="ij")
sphere = go.Surface(x=np.sin(u) * np.cos(v), y=np.sin(u) * np.sin(v), z=np.cos(u), opacity=0.3,
                    colorscale=[[0, "#cfd8e3"], [1, "#cfd8e3"]], showscale=False, hoverinfo="skip")

frames, steps = [], []
for k, dphi in enumerate(dphis):
    traces, title = frame_traces(dphi)
    name = f"{np.degrees(dphi):.0f}°"
    frames.append(go.Frame(data=traces, traces=list(range(1, 1 + len(traces))), name=name,
                           layout=go.Layout(title_text=title)))
    steps.append(dict(method="animate", label=name,
                      args=[[name], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))]))

k0 = int(np.argmin(np.abs(dphis - np.pi / 2)))
traces0, title0 = frame_traces(dphis[k0])
fig = go.Figure(data=[sphere] + traces0, frames=frames)
fig.update_layout(
    title_text=frames[k0].layout.title.text,
    sliders=[dict(active=k0, currentvalue=dict(prefix="Δφ = "), pad=dict(t=30), steps=steps)],
    scene=dict(aspectmode="data", camera=dict(eye=dict(x=1.1, y=0.8, z=0.6)),
               xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)),
    height=700, margin=dict(l=0, r=0, t=60, b=0),
)
fig.show()"""),
    md("""## 観察のポイント

- Δφ = 90° のとき、回転角はちょうど 90° です。ノートの図2・anim01（1/8 球面）と同じ値です。
- Δφ を大きくすると、三角形の面積が増え、回転角も同じだけ増えます。**回転角 = $K$ × 面積**です。
- 上の数値確認のとおり、出発時のベクトルの向き（`PSI`）を変えても、回転角は変わりません。曲率が決めるのは、ベクトルの向きではなく、経路で決まるずれです。
- 半径 $a$ の球面なら、$K=1/a^2$、面積は $a^2\\Delta\\varphi$ なので、回転角は同じ Δφ になります。

**次に試すこと**：`triangle_path` を、測地線ではない経路（緯線など）に変えると、どうなるでしょうか。その場合は、ノートの Part VII §3 の議論（経路を細かい四角形に分ける）で、同じ結果が出ます。"""),
]
save("01_parallel_transport_sphere.ipynb", nb1)

# =====================================================================================
# 2. トーラスのガウス曲率
# =====================================================================================
nb2 = [
    md(f"""# トーラスのガウス曲率：3Dで回して、$b/a$ を動かす

[クリストッフェル記号とリーマン曲率テンソルのノート]({NOTE}#B-2)（付録B-2）のトーラスを、3Dで見ます。

**設定**：管の半径 $a=1$、中心軸から管の中心線までの距離 $b$（$b>a$）とし、

$$
\\mathbf r(\\theta,\\phi)=\\big((b+a\\cos\\theta)\\cos\\phi,\\ (b+a\\cos\\theta)\\sin\\phi,\\ a\\sin\\theta\\big)
$$

です。ガウス曲率は、$\\rho:=b+a\\cos\\theta$ として $K=\\dfrac{{\\cos\\theta}}{{a\\rho}}$ でした。外側（$\\cos\\theta>0$）は $K>0$（赤）、内側は $K<0$（青）です。

**使い方**：下部のスライダーで $b/a$ を変えます。3D の図は、ドラッグで回転、ホイールで拡大できます。"""),
    cd("""import numpy as np
import sympy as sp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

a = 1.0"""),
    md("""## 公式を、第一・第二基本形式から検算する

ノートの結果 $K=\\cos\\theta/(a\\rho)$ を、SymPy で $K=\\det L/\\det g$ から計算し直して、一致することを確かめます。"""),
    cd("""th, ph = sp.symbols("theta phi", real=True)
sa, sb = sp.symbols("a b", positive=True)
rho = sb + sa * sp.cos(th)
r = sp.Matrix([rho * sp.cos(ph), rho * sp.sin(ph), sa * sp.sin(th)])
r_th, r_ph = r.diff(th), r.diff(ph)
n = r_th.cross(r_ph)
n = sp.simplify(n / sp.sqrt(sp.simplify(n.dot(n))))
g = sp.Matrix([[r_th.dot(r_th), r_th.dot(r_ph)], [r_ph.dot(r_th), r_ph.dot(r_ph)]]).applyfunc(sp.simplify)
L = sp.Matrix([[r.diff(th, 2).dot(n), r.diff(th, ph).dot(n)], [r.diff(th, ph).dot(n), r.diff(ph, 2).dot(n)]]).applyfunc(sp.simplify)
K_sym = sp.simplify(L.det() / g.det())
print("K = det L / det g =", K_sym)
assert sp.simplify(K_sym - sp.cos(th) / (sa * (sb + sa * sp.cos(th)))) == 0
print("ノートの結果 cosθ/(aρ) と一致しました")"""),
    md("""## ガウス・ボネの定理の確認

トーラスのオイラー標数は 0 なので、$\\iint K\\,dA=0$ のはずです。面積要素は $\\sqrt{\\det g}=a\\rho$ なので、$K\\sqrt{\\det g}=\\cos\\theta$ となり、$\\theta$ で積分すると 0 になります。$b/a$ の値に依らず、数値でも確かめます。"""),
    cd("""def torus_data(b, nth=48, nph=96):
    th = np.linspace(-np.pi, np.pi, nth)
    ph = np.linspace(0, 2 * np.pi, nph)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    rho = b + a * np.cos(TH)
    return rho * np.cos(PH), rho * np.sin(PH), a * np.sin(TH), np.cos(TH) / (a * rho)


for b in [1.2, 2.4, 4.0]:
    th_f = np.linspace(-np.pi, np.pi, 4001)
    rho_f = b + a * np.cos(th_f)
    K_f = np.cos(th_f) / (a * rho_f)
    integral = 2 * np.pi * np.trapezoid(K_f * a * rho_f, th_f)   # ∬ K dA = ∫∫ K a ρ dθ dφ
    print(f"b/a = {b / a:.1f}:  ∬K dA = {integral:+.2e}")
    assert abs(integral) < 1e-9"""),
    md("""## スライダーで動かす

左が3Dの図（色が $K$、赤が正・青が負）、右が $K$ と $K\\sqrt{\\det g}=\\cos\\theta$ のグラフです。

- $b/a$ を小さくすると、内側（$\\theta=\\pm180°$）の負の曲率が急に強くなります。
- ただし、面積で重みを付けた $K\\sqrt{\\det g}=\\cos\\theta$ は、$b/a$ に依らないので、正と負の面積はいつも打ち消し合います。"""),
    cd("""bs = np.round(np.arange(1.2, 4.01, 0.1), 2)
th_deg = np.degrees(np.linspace(-np.pi, np.pi, 48))


def torus_traces(b):
    X, Y, Z, K = torus_data(b)
    surf = go.Surface(x=X, y=Y, z=Z, surfacecolor=K, colorscale="RdBu_r", cmid=0,
                      colorbar=dict(title="K", x=0.45, len=0.7))
    line = go.Scatter(x=th_deg, y=K[:, 0], mode="lines", line=dict(color="#d62728", width=3), name="K(θ)")
    return surf, line


frames, steps = [], []
for b in bs:
    surf, line = torus_traces(b)
    name = f"{b:.1f}"
    R = b + a + 0.3
    Kmin, Kmax = -1 / (a * (b - a)), 1 / (a * (b + a))
    frames.append(go.Frame(
        data=[surf, line], traces=[0, 1], name=name,
        layout=go.Layout(title_text=f"b/a = {b / a:.1f}　内側の最小値 K = {Kmin:.2f}",
                         scene=dict(xaxis=dict(range=[-R, R]), yaxis=dict(range=[-R, R]), zaxis=dict(range=[-R, R])),
                         yaxis2=dict(range=[min(-1.15, 1.1 * Kmin), 1.15]))))
    steps.append(dict(method="animate", label=name,
                      args=[[name], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))]))

k0 = int(np.argmin(np.abs(bs - 2.4)))
surf0, line0 = torus_traces(bs[k0])
R0 = bs[k0] + a + 0.3
fig = make_subplots(rows=1, cols=2, specs=[[{"type": "scene"}, {"type": "xy"}]], column_widths=[0.6, 0.4])
fig.add_trace(surf0, row=1, col=1)
fig.add_trace(line0, row=1, col=2)
fig.add_trace(go.Scatter(x=th_deg, y=np.cos(np.radians(th_deg)), mode="lines",
                         line=dict(color="#444", dash="dash"), name="K√det g = cosθ"), row=1, col=2)
fig.frames = frames
fig.update_xaxes(title_text="θ [度]", range=[-180, 180], dtick=90, row=1, col=2)
fig.update_yaxes(title_text="K", range=[min(-1.15, -1.1 / (a * (bs[k0] - a))), 1.15], row=1, col=2)
fig.update_layout(
    title_text=frames[k0].layout.title.text,
    sliders=[dict(active=k0, currentvalue=dict(prefix="b/a = "), pad=dict(t=30), steps=steps)],
    scene=dict(aspectmode="cube", xaxis=dict(visible=False, range=[-R0, R0]), yaxis=dict(visible=False, range=[-R0, R0]),
               zaxis=dict(visible=False, range=[-R0, R0]), camera=dict(eye=dict(x=1.1, y=0.9, z=0.8))),
    height=650, margin=dict(l=0, r=0, t=60, b=0), legend=dict(orientation="h", x=0.58, y=1.07),
)
fig.show()"""),
    md("""## 観察のポイント

- 赤（$K>0$）は外側、青（$K<0$）は内側です。上端と下端の円周（$\\theta=\\pm90°$）は $K=0$ で、白く見えます。
- 内側の最小値は $K=-1/(a(b-a))$ で、$b\\to a$ で発散します。
- 右のグラフの破線（$K\\sqrt{\\det g}=\\cos\\theta$）は、スライダーを動かしても変わりません。正の部分と負の部分の面積が等しいので、$\\iint K\\,dA=0=2\\pi\\chi$（$\\chi=0$）が成り立ちます。"""),
]
save("02_torus_gauss_curvature.ipynb", nb2)
