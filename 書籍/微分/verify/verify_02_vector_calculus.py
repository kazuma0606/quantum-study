"""「2 ベクトル微分」（02_ベクトル微分.md）に出てくる式と数値の検算。

実行: uv run --no-sync python 書籍/微分/verify/verify_02_vector_calculus.py
"""

import math
import sys

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
x, y, z = sp.symbols("x y z", real=True)
results = []


def check(name, cond):
    assert cond, name
    results.append(name)


def grad(f, v=(x, y, z)):
    return sp.Matrix([sp.diff(f, s) for s in v])


def div(F, v=(x, y, z)):
    return sum(sp.diff(F[i], v[i]) for i in range(len(v)))


def rot(F):
    P, Q, R = F
    return sp.Matrix([sp.diff(R, y) - sp.diff(Q, z), sp.diff(P, z) - sp.diff(R, x), sp.diff(Q, x) - sp.diff(P, y)])


# §1 grad：1章の山 f = 10 - x² - 2y²
f = 10 - x**2 - 2 * y**2
gf = grad(f, (x, y))
check("grad f = (-2x, -4y)", gf == sp.Matrix([-2 * x, -4 * y]))
check("(1,1) で grad f = (-2, -4)", gf.subs({x: 1, y: 1}) == sp.Matrix([-2, -4]))
# 等高線 x² + 2y² = 3 の (1,1) での接線の向き (2, -1)
check("等高線の接線 (2,-1) と grad f は直交", gf.subs({x: 1, y: 1}).dot(sp.Matrix([2, -1])) == 0)
# 等高線に沿う曲線 c(t) で f(c(t)) は一定 → 連鎖律で grad f · c'(t) = 0（楕円のパラメータ表示で確かめる）
tt = sp.symbols("t", real=True)
c = sp.Matrix([sp.sqrt(3) * sp.cos(tt), sp.sqrt(sp.Rational(3, 2)) * sp.sin(tt)])
check("楕円 x²+2y²=3 の上で f は一定（=7）", sp.simplify(f.subs({x: c[0], y: c[1]}) - 7) == 0)
check("その上で grad f · c'(t) = 0", sp.simplify(gf.subs({x: c[0], y: c[1]}).dot(c.diff(tt))) == 0)

# §2・§3 ベクトル場の例
V = sp.Matrix([x, y])
W = sp.Matrix([-y, x])


def div2(F):
    return sp.diff(F[0], x) + sp.diff(F[1], y)


def rot2(F):
    return sp.diff(F[1], x) - sp.diff(F[0], y)


check("湧き出す流れ (x, y)：div = 2", div2(V) == 2)
check("湧き出す流れ (x, y)：rot = 0", rot2(V) == 0)
check("回る流れ (-y, x)：div = 0", div2(W) == 0)
check("回る流れ (-y, x)：rot = 2", rot2(W) == 2)
check("まっすぐな流れ (0, x)：rot = 1（流れの線は直線でも 0 でない）", rot2(sp.Matrix([0, x])) == 1)
xs0, ys0, as0 = sp.symbols("xs0 ys0 as0", positive=True)
# 左回りに一周：下の辺（y 成分 0 の流れなので x 方向の寄与 0）、右の辺 x=xs0+as0 で上向きに Q=x、上の辺 0、左の辺 x=xs0 で下向き
circ_shear = sp.integrate(xs0 + as0, (y, ys0, ys0 + as0)) - sp.integrate(xs0, (y, ys0, ys0 + as0))
check("(0, x) の流れで、一辺 a の正方形を一周した循環 = a²", sp.simplify(circ_shear - as0**2) == 0)
check("一様な流れ (1, 0)：div = rot = 0", div2(sp.Matrix([1, 0])) == 0 and rot2(sp.Matrix([1, 0])) == 0)
# 3次元の rot の z 成分は2次元の rot と同じ
check("3次元の rot(-y, x, 0) = (0, 0, 2)", rot([-y, x, 0]) == sp.Matrix([0, 0, 2]))
# 小さな正方形を出入りする量：(x,y) の流れで、一辺 a の正方形 [x0, x0+a]×[y0, y0+a] の正味の流出 = 2a²
x0, y0, aa = sp.symbols("x0 y0 a", positive=True)
out_flux = (sp.integrate(V[0].subs(x, x0 + aa), (y, y0, y0 + aa)) - sp.integrate(V[0].subs(x, x0), (y, y0, y0 + aa))
            + sp.integrate(V[1].subs(y, y0 + aa), (x, x0, x0 + aa)) - sp.integrate(V[1].subs(y, y0), (x, x0, x0 + aa)))
check("(x,y) の流れで、一辺 a の正方形からの正味の流出 = 2a²（= div × 面積）", sp.simplify(out_flux - 2 * aa**2) == 0)
# 回る流れの周回：一辺 a の正方形を左回りに一周した循環 = 2a²（= rot × 面積）
circ = (sp.integrate(W[0].subs(y, y0), (x, x0, x0 + aa)) + sp.integrate(W[1].subs(x, x0 + aa), (y, y0, y0 + aa))
        - sp.integrate(W[0].subs(y, y0 + aa), (x, x0, x0 + aa)) - sp.integrate(W[1].subs(x, x0), (y, y0, y0 + aa)))
check("(-y,x) の流れで、一辺 a の正方形を一周した循環 = 2a²（= rot × 面積）", sp.simplify(circ - 2 * aa**2) == 0)

# §4 恒等式
phi = sp.Function("phi")(x, y, z)
P, Q, R = [sp.Function(n)(x, y, z) for n in ("P", "Q", "R")]
check("rot grad = 0", sp.simplify(rot(list(grad(phi)))) == sp.zeros(3, 1))
check("div rot = 0", sp.simplify(div(rot([P, Q, R]))) == 0)
check("div grad = ラプラシアン", sp.simplify(div(grad(phi)) - (phi.diff(x, 2) + phi.diff(y, 2) + phi.diff(z, 2))) == 0)
check("1章の山のラプラシアン = -6", div2(gf) == -6)
# なめらかでない反例：h = xy(x²-y²)/(x²+y²)（原点で 0）。原点での2階偏微分の順番で値が違う
hfun = x * y * (x**2 - y**2) / (x**2 + y**2)
s_ = sp.symbols("s_", real=True)
hx_on_yaxis = sp.limit(sp.diff(hfun, x).subs(x, s_), s_, 0)  # x → 0 での ∂h/∂x（y≠0 の y 軸の上）
hy_on_xaxis = sp.limit(sp.diff(hfun, y).subs(y, s_), s_, 0)  # y → 0 での ∂h/∂y（x≠0 の x 軸の上）
check("y 軸の上で ∂h/∂x = -y", sp.simplify(hx_on_yaxis + y) == 0)
check("x 軸の上で ∂h/∂y = x", sp.simplify(hy_on_xaxis - x) == 0)
h_xy = sp.diff(hx_on_yaxis, y)  # 先に x、次に y
h_yx = sp.diff(hy_on_xaxis, x)  # 先に y、次に x
check("原点で、x で微分してから y で微分すると -1", h_xy == -1)
check("原点で、y で微分してから x で微分すると 1", h_yx == 1)
check("原点で rot(grad h) の第3成分 = ∂(∂h/∂y)/∂x - ∂(∂h/∂x)/∂y = 2", h_yx - h_xy == 2)
# grad の式の導出：W^i g_ij = ∂f/∂q^j を解くと W^i = g^{ij} ∂f/∂q^j（極座標）
W = sp.symbols("W1 W2")
sol = sp.solve([sum(W[i] * g_p_tmp for i, g_p_tmp in enumerate(row)) - rhs_
                for row, rhs_ in zip((sp.Matrix([[1, 0], [0, sp.Symbol('rr', positive=True) ** 2]])).T.tolist(),
                                     (sp.Symbol("Gr"), sp.Symbol("Gt")))], W)
check("W^i g_ij = ∂f/∂q^j の解は (G_r, G_θ/r²)", sol == {W[0]: sp.Symbol("Gr"), W[1]: sp.Symbol("Gt") / sp.Symbol("rr", positive=True) ** 2})
check("θ を 1 動かしたときの弦の長さは 2r sin(1/2) ≈ 0.959r（弧の長さ r とは違う）", abs(2 * math.sin(0.5) - 0.95885) < 1e-5)

# §5 極座標
r, th = sp.symbols("r theta", positive=True)
X = sp.Matrix([r * sp.cos(th), r * sp.sin(th)])
J = X.jacobian([r, th])
b_r, b_th = J[:, 0], J[:, 1]
e_r = sp.Matrix([sp.cos(th), sp.sin(th)])
e_th = sp.Matrix([-sp.sin(th), sp.cos(th)])
check("座標の基底ベクトル b_r = e_r（長さ 1）", b_r == e_r)
check("座標の基底ベクトル b_θ = r e_θ（長さ r）", sp.simplify(b_th - r * e_th) == sp.zeros(2, 1))
# 一般の関数での grad の書き直し：grad f = g_r e_r + (1/r) g_θ e_θ（テスト関数で）
tests = [x**2 * y + y**3, sp.exp(x) * sp.sin(y), x * y / (1 + x**2 + y**2), 10 - x**2 - 2 * y**2]
for F_ in tests:
    G = sp.simplify(F_.subs({x: X[0], y: X[1]}))
    lhs = grad(F_, (x, y)).subs({x: X[0], y: X[1]})
    rhs = sp.diff(G, r) * e_r + sp.diff(G, th) / r * e_th
    check(f"grad の極座標の式（{F_}）", sp.simplify(lhs - rhs) == sp.zeros(2, 1))
    lap_c = (sp.diff(F_, x, 2) + sp.diff(F_, y, 2)).subs({x: X[0], y: X[1]})
    lap_p = sp.diff(G, r, 2) + sp.diff(G, r) / r + sp.diff(G, th, 2) / r**2
    check(f"ラプラシアンの極座標の式（{F_}）", sp.simplify(lap_c - lap_p) == 0)
# 1章の山を極座標で：G = 10 - r²cos²θ - 2r²sin²θ
G_m = sp.simplify((10 - x**2 - 2 * y**2).subs({x: X[0], y: X[1]}))
check("1章の山を極座標で書くと 10 - r² - r² sin²θ", sp.simplify(G_m - (10 - r**2 - r**2 * sp.sin(th) ** 2)) == 0)
# 素朴な式（θ 方向に 1/r を付けない）は間違い：(1,1) すなわち r=√2、θ=π/4 で比べる
Gr = sp.diff(G_m, r).subs({r: sp.sqrt(2), th: sp.pi / 4})
Gt = sp.diff(G_m, th).subs({r: sp.sqrt(2), th: sp.pi / 4})
check("(1,1) で ∂G/∂r = -3√2", sp.simplify(Gr + 3 * sp.sqrt(2)) == 0)
check("(1,1) で ∂G/∂θ = -2", sp.simplify(Gt + 2) == 0)
check("(1,1) での正しい grad の長さは 2√5", sp.simplify(sp.sqrt(Gr**2 + (Gt / sp.sqrt(2)) ** 2) - 2 * sp.sqrt(5)) == 0)
check("素朴な式の長さ √(18 + 4) = √22 は 2√5 と違う", sp.simplify(sp.sqrt(Gr**2 + Gt**2) - sp.sqrt(22)) == 0)
check("√22 ≈ 4.69、2√5 ≈ 4.47", abs(math.sqrt(22) - 4.690) < 1e-3 and abs(2 * math.sqrt(5) - 4.472) < 1e-3)

# §6 計量
g_p = sp.simplify(J.T * J)
check("極座標の計量 g = JᵀJ = diag(1, r²)", g_p == sp.diag(1, r**2))
dr, dth = sp.symbols("dr dtheta", real=True)
dxy = J * sp.Matrix([dr, dth])
check("ds² = dx² + dy² = dr² + r² dθ²", sp.simplify(dxy.dot(dxy) - (dr**2 + r**2 * dth**2)) == 0)
ph = sp.symbols("phi_", real=True)
ths = sp.symbols("theta_s", positive=True)
Xs = sp.Matrix([r * sp.sin(ths) * sp.cos(ph), r * sp.sin(ths) * sp.sin(ph), r * sp.cos(ths)])
Js = Xs.jacobian([r, ths, ph])
g_s = sp.simplify(Js.T * Js)
check("球座標の計量 diag(1, r², r² sin²θ)", g_s == sp.diag(1, r**2, r**2 * sp.sin(ths) ** 2))
check("|g| = (r² sinθ)²（0<θ<π では sinθ>0 なので √|g| = r² sinθ）", sp.simplify(g_s.det() - (r**2 * sp.sin(ths)) ** 2) == 0)
# 地球の経度 1° の長さ：R = 6371 km、緯度 λ で R cosλ · π/180
Rk = 6371.0
for lat, km in [(0, 111.2), (35, 91.1), (60, 55.6)]:
    L_ = Rk * math.cos(math.radians(lat)) * math.pi / 180
    check(f"緯度 {lat}° で経度 1° の長さ ≈ {km} km", abs(L_ - km) < 0.1)
check("緯線方向の長さの係数 r sinθ は、緯度 λ = 90° - θ で r cosλ", sp.simplify(sp.sin(sp.pi / 2 - sp.Symbol("lam")) - sp.cos(sp.Symbol("lam"))) == 0)

# §7 一般の座標での grad と div、ラプラス・ベルトラミ
gi = g_p.inv()
Gf = sp.Function("G")(r, th)
grad_comp = gi * sp.Matrix([sp.diff(Gf, r), sp.diff(Gf, th)])
check("grad の成分（座標の基底で）は (∂G/∂r, (1/r²)∂G/∂θ)", sp.simplify(grad_comp - sp.Matrix([sp.diff(Gf, r), sp.diff(Gf, th) / r**2])) == sp.zeros(2, 1))
check("座標の基底で書いた grad = 単位ベクトルで書いた grad",
      sp.simplify(grad_comp[0] * b_r + grad_comp[1] * b_th - (sp.diff(Gf, r) * e_r + sp.diff(Gf, th) / r * e_th)) == sp.zeros(2, 1))
sqrtg = r


def div_curv(Vr, Vt):
    return (sp.diff(sqrtg * Vr, r) + sp.diff(sqrtg * Vt, th)) / sqrtg


check("湧き出す流れ (x,y) = r b_r：div = (1/r)∂_r(r·r) = 2", sp.simplify(div_curv(r, 0)) == 2)
check("回る流れ (-y,x) = b_θ：div = (1/r)∂_θ(r·1) = 0", sp.simplify(div_curv(0, 1)) == 0)
check("(x,y) = r b_r", sp.simplify(r * b_r - X) == sp.zeros(2, 1))
check("(-y,x) = b_θ", sp.simplify(b_th - sp.Matrix([-X[1], X[0]])) == sp.zeros(2, 1))
# div の式の考え方：det(V¹b₁+V²b₂, b₂) = V¹ det(b₁,b₂)、det(b_r, b_θ) = r = √|g|
V1s, V2s = sp.symbols("V1 V2", real=True)
check("det(V¹b_r+V²b_θ, b_θ) = V¹ det(b_r, b_θ)",
      sp.simplify(sp.Matrix.hstack(V1s * b_r + V2s * b_th, b_th).det() - V1s * sp.Matrix.hstack(b_r, b_th).det()) == 0)
check("det(b_r, b_θ) = r = √|g|", sp.simplify(sp.Matrix.hstack(b_r, b_th).det() - r) == 0)
check("右の辺 s=(0,dy) から出ていく量 det(V, s) = P dy",
      sp.Matrix([[sp.Symbol("P"), 0], [sp.Symbol("Q"), sp.Symbol("dy")]]).det() == sp.Symbol("P") * sp.Symbol("dy"))
LB = div_curv(grad_comp[0], grad_comp[1])
check("ラプラス・ベルトラミ（極座標）= G_rr + G_r/r + G_θθ/r²",
      sp.simplify(LB - (sp.diff(Gf, r, 2) + sp.diff(Gf, r) / r + sp.diff(Gf, th, 2) / r**2)) == 0)
# 球座標でも、div(grad) の形がラプラス・ベルトラミの式（はじめにの検算と同じ結果）
Hs = sp.Function("H")(r, ths, ph)
gis = g_s.inv()
sg = r**2 * sp.sin(ths)
qs = [r, ths, ph]
LBs = sum(sp.diff(sg * sum(gis[i, j] * sp.diff(Hs, qs[j]) for j in range(3)), qs[i]) for i in range(3)) / sg
std = (sp.diff(r**2 * sp.diff(Hs, r), r) / r**2 + sp.diff(sp.sin(ths) * sp.diff(Hs, ths), ths) / (r**2 * sp.sin(ths))
       + sp.diff(Hs, ph, 2) / (r**2 * sp.sin(ths) ** 2))
check("球座標のラプラス・ベルトラミ = 球座標のラプラシアンの標準形", sp.simplify(LBs - std) == 0)
# 3つの項を1つずつ：かっこの中の約分
check("θ の項：r² sinθ · (1/r²) = sinθ", sp.simplify(r**2 * sp.sin(ths) / r**2 - sp.sin(ths)) == 0)
check("φ の項：r² sinθ · 1/(r² sin²θ) = 1/sinθ", sp.simplify(r**2 * sp.sin(ths) / (r**2 * sp.sin(ths) ** 2) - 1 / sp.sin(ths)) == 0)
# 原点と極での基底ベクトル
check("原点 r=0 では θ・φ の向きの基底ベクトルが2本とも 0",
      Js[:, 1].subs(r, 0) == sp.zeros(3, 1) and Js[:, 2].subs(r, 0) == sp.zeros(3, 1))
check("北極 θ=0 では φ の向きの基底ベクトルが 0", Js[:, 2].subs(ths, 0) == sp.zeros(3, 1))

print(f"すべて一致：{len(results)} 件")
