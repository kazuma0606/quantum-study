"""「準備2 1変数の微分」（P2_1変数の微分.md）に出てくる式と数値の検算。

実行: uv run --no-sync python 書籍/微分/verify/verify_P2_derivative.py
"""

import math
import sys

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
x, h, a, m, R, d = sp.symbols("x h a m R d", real=True)
results = []


def check(name, cond):
    assert cond, name
    results.append(name)


# §1 地球の表面：接線からの落ち込み R - √(R² - d²) ≈ d²/(2R)
Rp = sp.symbols("Rp", positive=True)
drop = Rp - sp.sqrt(Rp**2 - d**2)
check("落ち込みの d² の係数は 1/(2R)", sp.simplify(sp.series(drop, d, 0, 4).removeO() - d**2 / (2 * Rp)) == 0)
R_earth = 6371.0  # km
for dist_km, approx_m in [(1, 0.0785), (10, 7.85), (100, 785.0)]:
    exact_m = (R_earth - math.sqrt(R_earth**2 - dist_km**2)) * 1000
    check(f"{dist_km} km 先で約 {approx_m} m 落ち込む（厳密な値との差 1% 未満）",
          abs(exact_m - approx_m) / approx_m < 0.01)
    check(f"{dist_km} km 先の近似 d²/(2R) も約 {approx_m} m",
          abs(dist_km**2 / (2 * R_earth) * 1000 - approx_m) / approx_m < 0.01)

# §2 微分係数と接線、誤差は h より速く小さくなる
f = sp.sqrt(x)
check("√x の x=4 での微分係数は 1/4", sp.diff(f, x).subs(x, 4) == sp.Rational(1, 4))
approx = 2 + sp.Rational(1, 4) * sp.Rational(1, 10)
check("√4.1 の接線による近似は 2.025", approx == sp.Rational(2025, 1000))
check("√4.1 = 2.024845…（小数第6位までの桁）", math.floor(math.sqrt(4.1) * 10**6) == 2024845)
# 学習率が大きすぎると、かえって高い所へ行く例：f(x) = (x-3)²、x=0、η=1.5 → x=9、f は 9 から 36 へ
x_big = 0 - 1.5 * 2 * (0 - 3)
check("学習率 1.5 では、x=0 から x=9 へ飛び、f は 9 から 36 に増える", x_big == 9 and (x_big - 3) ** 2 == 36)
check("√4.1 の近似の誤差は約 0.00015", abs((2.025 - math.sqrt(4.1)) - 0.000154) < 0.000002)
# 誤差 / h の表（h = 0.1, 0.01, 0.001）
for hv, err_expect, ratio in [(0.1, 0.000154, 0.00154), (0.01, 0.00000156, 0.000156), (0.001, 0.0000000156, 0.0000156)]:
    err = 2 + hv / 4 - math.sqrt(4 + hv)
    check(f"h={hv} で 誤差 ≈ {err_expect}", abs(err - err_expect) / err_expect < 0.02)
    check(f"h={hv} で 誤差/h ≈ {ratio}", abs(err / hv - ratio) / ratio < 0.02)
# 接線以外の傾き m では、誤差/h が 0 に近づかない
err_m = (sp.sqrt(4 + h) - 2 - m * h) / h
check("傾き m の直線の誤差/h → 1/4 - m", sp.limit(err_m, h, 0) == sp.Rational(1, 4) - m)
check("x² の差分 = 2xh + h²", sp.expand((x + h) ** 2 - x**2) == 2 * x * h + h**2)

# §2 |x| は x=0 で微分できない（右からの傾き 1、左からの傾き -1）
check("|x| の右からの差分商 → 1", sp.limit(sp.Abs(h) / h, h, 0, "+") == 1)
check("|x| の左からの差分商 → -1", sp.limit(sp.Abs(h) / h, h, 0, "-") == -1)

# §3 導関数の表
table = {
    x**3: 3 * x**2,
    x**5: 5 * x**4,
    sp.sin(x): sp.cos(x),
    sp.cos(x): -sp.sin(x),
    sp.exp(x): sp.exp(x),
    sp.log(x): 1 / x,
    1 / x: -1 / x**2,
}
for fx, dfx in table.items():
    check(f"({fx})' = {dfx}", sp.simplify(sp.diff(fx, x) - dfx) == 0)
n = sp.symbols("n", positive=True, integer=True)
check("(x^n)' = n x^(n-1)", sp.simplify(sp.diff(x**n, x) - n * x ** (n - 1)) == 0)
# 二項展開による (x^n)' の導出の要：(x+h)^n - x^n = n x^(n-1) h + (h² 以上の項)
for nv in range(1, 7):
    diff_ = sp.expand((x + h) ** nv - x**nv)
    check(f"n={nv}：(x+h)^n - x^n の h の1次の係数は n x^(n-1)", sp.expand(diff_.coeff(h, 1) - nv * x ** (nv - 1)) == 0)
# sin h / h → 1、(cos h - 1)/h → 0、(e^h - 1)/h → 1
check("sin h / h → 1", sp.limit(sp.sin(h) / h, h, 0) == 1)
check("(cos h - 1)/h → 0", sp.limit((sp.cos(h) - 1) / h, h, 0) == 0)
check("(e^h - 1)/h → 1", sp.limit((sp.exp(h) - 1) / h, h, 0) == 1)
for hv, val in [(0.1, 0.99833), (0.01, 0.99998)]:
    check(f"h={hv} で sin h / h ≈ {val}", abs(math.sin(hv) / hv - val) < 1e-5)
# 加法定理による sin の差分の分解
check("sin(x+h) - sin x = sin x (cos h - 1) + cos x sin h",
      sp.simplify(sp.expand_trig(sp.sin(x + h)) - sp.sin(x) - (sp.sin(x) * (sp.cos(h) - 1) + sp.cos(x) * sp.sin(h))) == 0)
# a^x の x=0 での傾き (a^h - 1)/h：a=2 で約 0.693、a=3 で約 1.099、a=e でちょうど 1
for av, slope in [(2, 0.693), (3, 1.099)]:
    check(f"a={av} の x=0 での傾きは約 {slope}", abs(float(sp.limit((av**h - 1) / h, h, 0)) - slope) < 1e-3)
check("e = 2.71828…", abs(math.e - 2.71828) < 1e-5)

# §3 積の微分と合成関数の微分（連鎖律）
u = sp.Function("u")(x)
v = sp.Function("v")(x)
check("(uv)' = u'v + uv'", sp.simplify(sp.diff(u * v, x) - (sp.diff(u, x) * v + u * sp.diff(v, x))) == 0)
check("(u+v)' = u' + v'", sp.simplify(sp.diff(u + v, x) - (sp.diff(u, x) + sp.diff(v, x))) == 0)
check("((x²+1)^5)' = 5(x²+1)^4 · 2x", sp.simplify(sp.diff((x**2 + 1) ** 5, x) - 5 * (x**2 + 1) ** 4 * 2 * x) == 0)
check("(sin(x²))' = cos(x²) · 2x", sp.simplify(sp.diff(sp.sin(x**2), x) - sp.cos(x**2) * 2 * x) == 0)
# 積の微分の導出の要：u(x+h)v(x+h) - u(x)v(x) = (u(x+h)-u(x))v(x+h) + u(x)(v(x+h)-v(x))
U1, U0, V1, V0 = sp.symbols("U1 U0 V1 V0")
check("積の差分の分け方", sp.expand((U1 - U0) * V1 + U0 * (V1 - V0) - (U1 * V1 - U0 * V0)) == 0)
# 燃費の例：時速 60 km、1 km あたり 0.05 L → 1 時間あたり 3 L
check("時速 60 km × 1 km あたり 0.05 L = 1 時間あたり 3 L", abs(60 * 0.05 - 3) < 1e-12)
# log の微分（e^(log x) = x を微分する）
check("e^(log x) = x", sp.simplify(sp.exp(sp.log(sp.Symbol("xp", positive=True)))) == sp.Symbol("xp", positive=True))

# §4 傾きで増減と最小を調べる・勾配降下法
g = (x - 3) ** 2
check("(x-3)² の導関数は 2(x-3)", sp.simplify(sp.diff(g, x) - 2 * (x - 3)) == 0)
eta = sp.Rational(1, 10)
xs = [sp.Integer(0)]
for _ in range(10):
    xs.append(xs[-1] - eta * sp.diff(g, x).subs(x, xs[-1]))
check("勾配降下法の最初の3歩は 0, 0.6, 1.08", xs[:3] == [0, sp.Rational(3, 5), sp.Rational(27, 25)])
check("勾配降下法の n 歩目は 3 - 3·0.8^n（n=0〜10）",
      all(xs[j] == 3 - 3 * sp.Rational(4, 5) ** j for j in range(11)))
check("0.8^n → 0 なので、x_n → 3", sp.limit(3 - 3 * sp.Rational(4, 5) ** n, n, sp.oo) == 3)
check("10 歩目は約 2.68", abs(float(xs[10]) - 2.678) < 1e-3)
check("1 歩で 3 との差は 0.8 倍", all(sp.simplify((3 - xs[j + 1]) / (3 - xs[j])) == sp.Rational(4, 5) for j in range(10)))

# §5 2階微分と曲がり具合：円の頂上 y = R - √(R² - x²) では y''(0) = 1/R
yc = Rp - sp.sqrt(Rp**2 - x**2)
check("円の頂上で y'(0) = 0", sp.diff(yc, x).subs(x, 0) == 0)
check("円の頂上で y''(0) = 1/R", sp.simplify(sp.diff(yc, x, 2).subs(x, 0) - 1 / Rp) == 0)
check("x² の2階微分は 2", sp.diff(x**2, x, 2) == 2)
check("2次までの近似：f(a+h) ≈ f(a) + f'(a)h + f''(a)h²/2 は、円で d²/(2R) を与える",
      sp.simplify(yc.subs(x, 0) + sp.diff(yc, x).subs(x, 0) * d + sp.diff(yc, x, 2).subs(x, 0) * d**2 / 2 - d**2 / (2 * Rp)) == 0)
# √x の2次までの近似で √4.1 の誤差が小さくなる
f2 = 2 + sp.Rational(1, 4) * sp.Rational(1, 10) + (-sp.Rational(1, 32)) / 2 * sp.Rational(1, 10) ** 2
check("√x の x=4 での2階微分は -1/32", sp.diff(sp.sqrt(x), x, 2).subs(x, 4) == -sp.Rational(1, 32))
check("2次までの近似は 2.025 - 0.00015625 = 2.02484375", f2 == sp.Rational(202484375, 10**8))
check("2次までの近似の誤差は約 0.000002（1次の約 0.00015 から小さくなる）",
      1.5e-6 < abs(float(f2) - math.sqrt(4.1)) < 2.5e-6)

# コラム：x² sin(1/x)（x=0 では 0）
F = x**2 * sp.sin(1 / x)
check("x=0 での差分商 h sin(1/h) → 0（微分係数は 0）", sp.limit(h * sp.sin(1 / h), h, 0) == 0)
check("x≠0 での導関数は 2x sin(1/x) - cos(1/x)",
      sp.simplify(sp.diff(F, x) - (2 * x * sp.sin(1 / x) - sp.cos(1 / x))) == 0)
dF = 2 * x * sp.sin(1 / x) - sp.cos(1 / x)
for j in range(1, 6):
    check(f"x=1/(2·{j}π) で導関数は -1", sp.simplify(dF.subs(x, 1 / (2 * j * sp.pi))) == -1)
    check(f"x=1/((2·{j}+1)π) で導関数は 1", sp.simplify(dF.subs(x, 1 / ((2 * j + 1) * sp.pi))) == 1)
check("|h sin(1/h)| ≤ |h|（h=0.001 で確かめる）", abs(0.001 * math.sin(1000)) <= 0.001)

print(f"すべて一致：{len(results)} 件")
