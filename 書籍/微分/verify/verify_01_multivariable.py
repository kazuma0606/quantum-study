"""「1 多変数の微分」（01_多変数の微分.md）に出てくる式と数値の検算。

実行: uv run --no-sync python 書籍/微分/verify/verify_01_multivariable.py
"""

import math
import sys

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
x, y, h, k, t = sp.symbols("x y h k t", real=True)
results = []


def check(name, cond):
    assert cond, name
    results.append(name)


# 例の地形 f(x, y) = 10 - x² - 2y²、点 (1, 1)
f = 10 - x**2 - 2 * y**2
check("f(1,1) = 7", f.subs({x: 1, y: 1}) == 7)
fx, fy = sp.diff(f, x), sp.diff(f, y)
check("∂f/∂x = -2x", fx == -2 * x)
check("∂f/∂y = -4y", fy == -4 * y)
check("(1,1) で ∂f/∂x = -2", fx.subs({x: 1, y: 1}) == -2)
check("(1,1) で ∂f/∂y = -4", fy.subs({x: 1, y: 1}) == -4)
# 偏微分を極限で：(f(1+h,1) - f(1,1))/h = -2 - h → -2
check("x 方向の差分商 = -2 - h", sp.simplify((f.subs({x: 1 + h, y: 1}) - 7) / h - (-2 - h)) == 0)
check("y 方向の差分商 = -4 - 2h", sp.simplify((f.subs({x: 1, y: 1 + h}) - 7) / h - (-4 - 2 * h)) == 0)

# §2 接平面による近似と、誤差
approx = 7 + (-2) * h + (-4) * k
exact = f.subs({x: 1 + h, y: 1 + k})
check("誤差 = 近似 - 実際 = h² + 2k²", sp.expand(approx - exact) == h**2 + 2 * k**2)
check("(0.1, 0.05) で近似 6.6", approx.subs({h: sp.Rational(1, 10), k: sp.Rational(1, 20)}) == sp.Rational(33, 5))
check("(0.1, 0.05) で実際 6.585", exact.subs({h: sp.Rational(1, 10), k: sp.Rational(1, 20)}) == sp.Rational(6585, 1000))
check("(0.1, 0.05) で誤差 0.015", (approx - exact).subs({h: sp.Rational(1, 10), k: sp.Rational(1, 20)}) == sp.Rational(15, 1000))
check("(0.05, 0.025) で誤差 0.00375（約 1/4）",
      (approx - exact).subs({h: sp.Rational(1, 20), k: sp.Rational(1, 40)}) == sp.Rational(375, 100000))
# 誤差 / 長さ → 0
hh = sp.symbols("hh", positive=True)
th0 = sp.symbols("th0", real=True)
err_over_len = (approx - exact).subs({h: hh * sp.cos(th0), k: hh * sp.sin(th0)}) / hh
check("誤差 / |(h,k)| → 0（どの向きから近づいても）", sp.limit(err_over_len, hh, 0) == 0)

# §2 方向微分：単位ベクトル u の向きの傾き = f_x u1 + f_y u2
for u1, u2, slope in [(1, 0, -2), (0, 1, -4)]:
    check(f"向き ({u1},{u2}) の傾きは {slope}",
          sp.limit((f.subs({x: 1 + t * u1, y: 1 + t * u2}) - 7) / t, t, 0) == slope)
u = sp.Matrix([-1, -2]) / sp.sqrt(5)
slope_u = sp.limit((f.subs({x: 1 + t * u[0], y: 1 + t * u[1]}) - 7) / t, t, 0)
check("向き (-1,-2)/√5 の傾きは 2√5", sp.simplify(slope_u - 2 * sp.sqrt(5)) == 0)
check("2√5 ≈ 4.47", abs(float(2 * sp.sqrt(5)) - 4.472) < 1e-3)
check("向き (1,1)/√2 の傾きは -6/√2 = -3√2", sp.simplify(
    sp.limit((f.subs({x: 1 + t / sp.sqrt(2), y: 1 + t / sp.sqrt(2)}) - 7) / t, t, 0) + 3 * sp.sqrt(2)) == 0)
# 傾きの最大は |(f_x, f_y)| で、その向き (コーシー・シュワルツ)：単位ベクトル (cos a, sin a) で -2cos a - 4 sin a の最大
a = sp.symbols("a", real=True)
g_a = -2 * sp.cos(a) - 4 * sp.sin(a)
vals = [-2 * math.cos(2 * math.pi * j / 100000) - 4 * math.sin(2 * math.pi * j / 100000) for j in range(100000)]
check("いちばん急な上りの傾きは 2√5（約 4.47、向きを細かく調べる）", abs(max(vals) - 2 * math.sqrt(5)) < 1e-6)
check("いちばん急な下りの傾きは -2√5", abs(min(vals) + 2 * math.sqrt(5)) < 1e-6)
# 振幅の式：-2cos a - 4 sin a = 2√5 cos(a - a*) の形（最大は √(2²+4²)）
check("√(2² + 4²) = 2√5", sp.sqrt(2**2 + 4**2) == 2 * sp.sqrt(5))

# §3 C¹ なら微分可能の、2段の分け方
F = sp.Function("F")
a0, b0 = sp.symbols("a0 b0", real=True)
check("差の2段の分け方（恒等式）",
      sp.simplify((F(a0 + h, b0 + k) - F(a0, b0 + k)) + (F(a0, b0 + k) - F(a0, b0)) - (F(a0 + h, b0 + k) - F(a0, b0))) == 0)

# §4 Jacobian：極座標
r, th = sp.symbols("r theta", positive=True)
Pm = sp.Matrix([r * sp.cos(th), r * sp.sin(th)])
J = Pm.jacobian([r, th])
check("極座標の Jacobian", J == sp.Matrix([[sp.cos(th), -r * sp.sin(th)], [sp.sin(th), r * sp.cos(th)]]))
# 一般の F: R² → R³ の例 (u,v) ↦ (u+v, uv, u²) の Jacobian は 3×2
uu, vv = sp.symbols("u v", real=True)
G3 = sp.Matrix([uu + vv, uu * vv, uu**2])
check("(u+v, uv, u²) の Jacobian は 3×2 の (1 1; v u; 2u 0)",
      G3.jacobian([uu, vv]) == sp.Matrix([[1, 1], [vv, uu], [2 * uu, 0]]))
# f の Jacobian は 1×2 の行列 (f_x  f_y)
check("f の Jacobian は (−2x  −4y)", sp.Matrix([f]).jacobian([x, y]) == sp.Matrix([[-2 * x, -4 * y]]))

# §5 連鎖律：g(r,θ) = f(r cosθ, r sinθ) で、(∂g/∂r, ∂g/∂θ) = (f_x, f_y) J
fq = x**2 + y**2
gq = fq.subs({x: r * sp.cos(th), y: r * sp.sin(th)})
row = sp.Matrix([[sp.diff(fq, x), sp.diff(fq, y)]]).subs({x: r * sp.cos(th), y: r * sp.sin(th)})
prod = sp.simplify(row * J)
check("x²+y² を極座標で：g = r²", sp.simplify(gq - r**2) == 0)
check("(f_x, f_y) J = (2r, 0)", prod == sp.Matrix([[2 * r, 0]]))
check("∂g/∂r = 2r、∂g/∂θ = 0（直接の微分と一致）",
      sp.simplify(sp.diff(gq, r) - 2 * r) == 0 and sp.simplify(sp.diff(gq, th)) == 0)
# 例の地形 f = 10 - x² - 2y² で、連鎖律と直接の微分が一致
g2 = f.subs({x: r * sp.cos(th), y: r * sp.sin(th)})
row2 = sp.Matrix([[fx, fy]]).subs({x: r * sp.cos(th), y: r * sp.sin(th)})
check("地形 f でも (∂g/∂r, ∂g/∂θ) = (f_x, f_y) J",
      sp.simplify(row2 * J - sp.Matrix([[sp.diff(g2, r), sp.diff(g2, th)]])) == sp.zeros(1, 2))
check("地形 f で ∂g/∂r = -2r cos²θ - 4r sin²θ",
      sp.simplify(sp.diff(g2, r) - (-2 * r * sp.cos(th) ** 2 - 4 * r * sp.sin(th) ** 2)) == 0)
check("地形 f で ∂g/∂θ = -2r² sinθ cosθ",
      sp.simplify(sp.diff(g2, th) - (-2 * r**2 * sp.sin(th) * sp.cos(th))) == 0)
# 一般の 2×2 の連鎖律（記号の関数で）
p1, p2 = sp.Function("p1"), sp.Function("p2")
q1, q2 = sp.Function("q1"), sp.Function("q2")
s1, s2 = sp.symbols("s1 s2", real=True)
inner = sp.Matrix([p1(s1, s2), p2(s1, s2)])
X1, X2 = sp.symbols("X1 X2", real=True)
outer = sp.Matrix([q1(X1, X2), q2(X1, X2)])
comp = outer.subs({X1: inner[0], X2: inner[1]})
lhs = comp.jacobian([s1, s2])
rhs = outer.jacobian([X1, X2]).subs({X1: inner[0], X2: inner[1]}) * inner.jacobian([s1, s2])
check("一般の 2×2 で J_{G∘F} = J_G J_F", sp.simplify(lhs - rhs) == sp.zeros(2, 2))
# 1変数の場合は準備2の連鎖律
check("1変数：(sin(x²))' = cos(x²)·2x", sp.diff(sp.sin(x**2), x) == sp.cos(x**2) * 2 * x)

# §6 たくさんの変数での勾配降下法：f2 = (x-1)² + 2(y+1)²、η = 0.1、(0,0) から
f2 = (x - 1) ** 2 + 2 * (y + 1) ** 2
check("f2 の偏微分 (2(x-1), 4(y+1))", (sp.diff(f2, x), sp.diff(f2, y)) == (2 * (x - 1), 4 * (y + 1)))
pt = (sp.Integer(0), sp.Integer(0))
pts = [pt]
for _ in range(10):
    px, py = pts[-1]
    pts.append((px - sp.Rational(1, 10) * 2 * (px - 1), py - sp.Rational(1, 10) * 4 * (py + 1)))
check("1歩目は (0.2, -0.4)", pts[1] == (sp.Rational(1, 5), -sp.Rational(2, 5)))
check("2歩目は (0.36, -0.64)", pts[2] == (sp.Rational(9, 25), -sp.Rational(16, 25)))
check("n 歩目は (1 - 0.8^n, -1 + 0.6^n)（n=0〜10）",
      all(pts[j] == (1 - sp.Rational(4, 5) ** j, -1 + sp.Rational(3, 5) ** j) for j in range(11)))
check("10 歩目は約 (0.893, -0.994)", abs(float(pts[10][0]) - 0.8926) < 1e-3 and abs(float(pts[10][1]) + 0.9940) < 1e-3)

# コラム：xy/(x²+y²)
fc = x * y / (x**2 + y**2)
check("x 軸の上では 0：偏微分 ∂f/∂x(0,0) = 0", sp.limit(fc.subs(y, 0).subs(x, h) / h, h, 0) == 0)
check("y 軸の上では 0：偏微分 ∂f/∂y(0,0) = 0", sp.limit(fc.subs(x, 0).subs(y, h) / h, h, 0) == 0)
check("直線 y = x の上では 1/2", sp.simplify(fc.subs(y, x)) == sp.Rational(1, 2))
check("直線 y = -x の上では -1/2", sp.simplify(fc.subs(y, -x)) == -sp.Rational(1, 2))
check("直線 y = mx の上では m/(1+m²)", sp.simplify(fc.subs(y, sp.Symbol("m") * x) - sp.Symbol("m") / (1 + sp.Symbol("m") ** 2)) == 0)
check("x≠0 で ∂f/∂x = y(y²-x²)/(x²+y²)²", sp.simplify(sp.diff(fc, x) - y * (y**2 - x**2) / (x**2 + y**2) ** 2) == 0)
check("y 軸の上（x=0、y≠0）で ∂f/∂x = 1/y", sp.simplify(sp.diff(fc, x).subs(x, 0) - 1 / y) == 0)
check("直線 y=x に沿った差分商 (1/2)/t は t → +0 で発散（斜めの方向微分はない）",
      sp.limit(sp.Rational(1, 2) / t, t, 0, "+") == sp.oo)
check("頂上 (0,0) では偏微分のベクトルは 0", (fx.subs({x: 0, y: 0}), fy.subs({x: 0, y: 0})) == (0, 0))
check("勾配降下法の最小の点 (1,-1) では偏微分のベクトルは 0",
      (sp.diff(f2, x).subs({x: 1, y: -1}), sp.diff(f2, y).subs({x: 1, y: -1})) == (0, 0))
check("1/y は y → -0 で -∞（絶対値が限りなく大きくなる）", sp.limit(1 / y, y, 0, "-") == -sp.oo)
check("東へ 1 進むと高さは -3 変わる（傾き -2 とは違う）", f.subs({x: 2, y: 1}) - f.subs({x: 1, y: 1}) == -3)
# 評価点の大切さ：F1(x)=x+1、F2(x)=x²、ℓ(x)=x の合成の導関数は 2(x+1)
z0 = sp.Symbol("z0")
check("合成 (x+1)² の導関数は 2(x+1)：J_F2 は z1 = x+1 で評価する",
      sp.diff((z0 + 1) ** 2, z0) == 2 * (z0 + 1) and sp.diff(z0**2, z0).subs(z0, z0 + 1) * 1 == 2 * (z0 + 1))
check("1/y は y → 0 で発散（偏微分は原点で連続でない）", sp.limit(1 / y, y, 0, "+") == sp.oo)

print(f"すべて一致：{len(results)} 件")
