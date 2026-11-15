"""「準備1 極限と収束」（P1_極限と収束.md）に出てくる式と数値の検算。

実行: uv run --no-sync python 書籍/微分/verify/verify_P1_limits.py
"""

import sys

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
n, N, k, x, h, m = sp.symbols("n N k x h m", positive=True)
results = []


def check(name, cond):
    assert cond, name
    results.append(name)


# §1 数列の収束
check("1/n → 0", sp.limit(1 / n, n, sp.oo) == 0)
check("1 - 1/10^n → 1（0.9, 0.99, 0.999, …）", sp.limit(1 - sp.Rational(1, 10) ** n, n, sp.oo) == 1)
check("0.9 + 0.09 + … の部分和は 1 - 1/10^N",
      sp.simplify(sp.summation(9 / sp.Integer(10) ** k, (k, 1, N)) - (1 - sp.Rational(1, 10) ** N)) == 0)
# ε-N：N > 1/ε なら、n ≥ N で |1/n - 0| < ε（いくつかの ε で、N を具体的に選んで確かめる）
for eps in [sp.Rational(1, 10), sp.Rational(1, 100), sp.Rational(3, 1000)]:
    Nchoice = sp.floor(1 / eps) + 1
    check(f"ε={eps} で N={Nchoice} を選ぶと 1/N < ε", 1 / Nchoice < eps)

# §2 発散と振動
check("n² → ∞", sp.limit(n**2, n, sp.oo) == sp.oo)
check("(-1)^n は 1 と -1 を交互にとる", [(-1) ** j for j in range(1, 7)] == [-1, 1, -1, 1, -1, 1])

# §3 級数
xs = sp.symbols("xs")
# 等比級数の部分和：S_N - x S_N = 1 - x^(N+1) を、N を記号のまま確かめる
S_sym = sum(xs**j for j in range(0, 8))  # N=7 で、項を書き出して確かめる
check("N=7 で S_N - x S_N = 1 - x^(N+1)", sp.expand(S_sym - xs * S_sym) == 1 - xs**8)
for xv in [sp.Rational(1, 2), sp.Rational(1, 3), sp.Integer(2)]:
    lhs = sum(xv**j for j in range(0, 11))
    check(f"x={xv}, N=10 で S_N の公式が一致", lhs == (1 - xv**11) / (1 - xv))
check("1/2 + 1/4 + … の部分和は 1 - (1/2)^N",
      sp.simplify(sp.summation(sp.Rational(1, 2) ** k, (k, 1, N)) - (1 - sp.Rational(1, 2) ** N)) == 0)
check("1/2 + 1/4 + … → 1", sp.limit(1 - sp.Rational(1, 2) ** N, N, sp.oo) == 1)
# 本文の数え方：最初の N 個（2^0 から 2^(N-1) まで）の和
check("1 + 2 + 4 + … の最初の N 個の和は 2^N - 1",
      sp.simplify(sp.summation(2**k, (k, 0, N - 1)) - (2**N - 1)) == 0)
check("最初の 1, 2, 3 個の和は 1, 3, 7", [sum(2**j for j in range(c)) for c in (1, 2, 3)] == [1, 3, 7])
# 半分ずつ・0.9 ずつの級数も、本文の数え方（最初の N 個）と合っているか、N=1,2,3 で確かめる
check("1/2 + … の最初の N 個の和 = 1 - 1/2^N（N=1,2,3）",
      all(sum(sp.Rational(1, 2**j) for j in range(1, c + 1)) == 1 - sp.Rational(1, 2**c) for c in (1, 2, 3)))
check("0.9 + 0.09 + … の最初の N 個の和 = 1 - 1/10^N（N=1,2,3）",
      all(sum(sp.Rational(9, 10**j) for j in range(1, c + 1)) == 1 - sp.Rational(1, 10**c) for c in (1, 2, 3)))
# 調和級数：1 + 1/2 + … + 1/2^m ≥ 1 + m/2
for mv in range(0, 15):
    H = sum(sp.Rational(1, j) for j in range(1, 2**mv + 1))
    check(f"H_(2^{mv}) ≥ 1 + {mv}/2", H >= 1 + sp.Rational(mv, 2))
check("1/(1-x) に x=2 を入れると -1", (1 / (1 - x)).subs(x, 2) == -1)
check("x=1/2 で 1/(1-x) = 2（1 + 1/2 + 1/4 + … = 1 + 1）", (1 / (1 - x)).subs(x, sp.Rational(1, 2)) == 2)
# 調和級数の部分和が初めて 10 を超えるのは 12367 項目（分数で厳密に確かめる）
H = sp.Rational(0)
first = None
for j in range(1, 13000):
    H += sp.Rational(1, j)
    if H > 10:
        first = j
        break
check("調和級数の部分和が初めて 10 を超えるのは 12367 項目", first == 12367)
# H_12366 = 9.99996…、H_12367 = 10.00004…（分数で足した値を小数にする）
H12367 = H
H12366 = H - sp.Rational(1, 12367)
check("H_12366 = 9.99996…", sp.floor(H12366 * 10**5) == 999996)
check("H_12367 = 10.00004…", sp.floor(H12367 * 10**5) == 1000004)
# H_n ≈ log n + γ：e^(10-γ) ≈ 12367.0
check("e^(10-γ) を小数第1位で丸めると 12367.0",
      round(float(sp.exp(10 - sp.EulerGamma)), 1) == 12367.0)
check("H_n - (log n + γ) は n=12367 で 1/(2n) 程度（差 < 1e-4）",
      abs(float(H12367 - sp.log(12367) - sp.EulerGamma)) < 1e-4)
check("log 10 ≈ 2.3", abs(float(sp.log(10)) - 2.3) < 0.01)
check("e^10 ≈ 2 万 2 千", 22000 < float(sp.exp(10)) < 22100)
check("1 + 1/4 + 1/9 + … = π²/6（バーゼル問題）", sp.summation(1 / k**2, (k, 1, sp.oo)) == sp.pi**2 / 6)

# §4 関数の極限
f = (x**2 - 1) / (x - 1)
xx = sp.symbols("xx", real=True)
fr = (xx**2 - 1) / (xx - 1)
check("(x²-1)/(x-1) → 2（x → 1、左右の両側から）", sp.limit(fr, xx, 1, "+-") == 2)
check("√x → 0（x → +0）で √0 = 0：x=0 で連続", sp.limit(sp.sqrt(xx), xx, 0, "+") == 0 == sp.sqrt(0))
check("(x²-1)/(x-1) = x + 1（x ≠ 1）", sp.simplify(f - (x + 1)) == 0)
xr = sp.symbols("xr", real=True)
check("1/x → +∞（右から）", sp.limit(1 / xr, xr, 0, "+") == sp.oo)
check("1/x → -∞（左から）", sp.limit(1 / xr, xr, 0, "-") == -sp.oo)
phi = sp.symbols("phi", real=True)
y = sp.log(sp.tan(sp.pi / 4 + phi / 2))
check("メルカトル図法の y は、緯度 φ → 90° で +∞", sp.limit(y, phi, sp.pi / 2, "-") == sp.oo)
for deg, expect in [(60, 1.317), (80, 2.436), (89, 4.741), (89.9, 7.044)]:
    val = float(y.subs(phi, sp.rad(deg)))
    check(f"緯度 {deg}° で y ≈ {expect}", abs(val - expect) < 1e-3)
# sin(1/x)：0 に近づく2つの数列で、違う値に近づく
for j in range(1, 6):
    check(f"x=1/({j}π) で sin(1/x)=0", sp.sin(j * sp.pi) == 0)
    check(f"x=1/(2·{j}π+π/2) で sin(1/x)=1", sp.sin(2 * j * sp.pi + sp.pi / 2) == 1)
# ε-δ：|f(x) - 2| = |x - 1|
check("x ≠ 1 で |f(x) - 2| = |x - 1|", sp.simplify(sp.Abs(f - 2) - sp.Abs(x - 1)) == 0)

# §5 連続：段差の関数（x<0 で 0、x≥0 で 1）は x=0 で左右の極限が違う
def step(t):
    return 0 if t < 0 else 1


check("段差の関数：左から近づくと値はずっと 0", all(step(-sp.Rational(1, 10**j)) == 0 for j in range(1, 10)))
check("段差の関数：右から近づくと値はずっと 1", all(step(sp.Rational(1, 10**j)) == 1 for j in range(1, 10)))
check("段差の関数：x=0 での値は 1", step(0) == 1)

# §6 差分商
q = ((1 + h) ** 2 - 1**2) / h
check("f(x)=x² の x=1 での差分商は 2 + h", sp.simplify(q - (2 + h)) == 0)
hr = sp.symbols("hr", real=True)
qr = ((1 + hr) ** 2 - 1) / hr
check("差分商 2 + h → 2（h → 0、左右の両側から）", sp.limit(qr, hr, 0, "+-") == 2)
for hv, expect in [(sp.Rational(1, 10), sp.Rational(21, 10)), (sp.Rational(1, 100), sp.Rational(201, 100)),
                   (sp.Rational(1, 1000), sp.Rational(2001, 1000))]:
    check(f"h={hv} で差分商 = {expect}", q.subs(h, hv) == expect)

# コラム「北極とδ関数」
eps = sp.symbols("epsilon", positive=True)
t, kk = sp.symbols("t k", real=True)
g = sp.exp(-t**2 / (2 * eps**2)) / (eps * sp.sqrt(2 * sp.pi))  # 幅 ε の山（ガウス関数）
S = (1 + sp.erf(t / (eps * sp.sqrt(2)))) / 2  # なめらかな坂
check("なめらかな坂の傾きは山：S'(x) = g(x)", sp.simplify(sp.diff(S, t) - g) == 0)
check("山の面積は 1（坂の高さと同じ）", sp.simplify(sp.integrate(g, (t, -sp.oo, sp.oo))) == 1)
check("坂は、左の端で 0、右の端で 1",
      sp.limit(S, t, -sp.oo) == 0 and sp.limit(S, t, sp.oo) == 1)
check("x=0 での坂の値は、どの ε でも 1/2", sp.simplify(S.subs(t, 0)) == sp.Rational(1, 2))
check("x>0 を固定して ε → 0 にすると、坂の値は 1 に近づく", sp.limit(S.subs(t, sp.Rational(1, 10)), eps, 0, "+") == 1)
check("x<0 を固定して ε → 0 にすると、坂の値は 0 に近づく", sp.limit(S.subs(t, -sp.Rational(1, 10)), eps, 0, "+") == 0)
check("x≠0 を固定して ε → 0 にすると、山の高さは 0 に近づく", sp.limit(g.subs(t, sp.Rational(1, 10)), eps, 0, "+") == 0)
check("x=0 での山の高さ 1/(ε√(2π)) は、ε → 0 で無限大", sp.limit(g.subs(t, 0), eps, 0, "+") == sp.oo)
# なめらかな関数 φ との「重みつきの面積」は、ε → 0 で φ(0) に近づく（φ = cos、e^x で確かめる）
for phi_f, phi0 in [(sp.cos(t), 1), (sp.exp(t), 1), (t**2 + 3, 3)]:
    val = sp.simplify(sp.integrate(g * phi_f, (t, -sp.oo, sp.oo)))
    check(f"∫ g·({phi_f}) dx → φ(0) = {phi0}", sp.limit(val, eps, 0, "+") == phi0)
# フーリエ変換（F(k) = ∫ f(x) e^{-ikx} dx）：山のフーリエ変換は e^{-ε²k²/2} で、ε → 0 で 1 に近づく
F = sp.simplify(sp.integrate(g * sp.exp(-sp.I * kk * t), (t, -sp.oo, sp.oo)))
check("幅 ε の山のフーリエ変換は e^{-ε²k²/2}", sp.simplify(F - sp.exp(-eps**2 * kk**2 / 2)) == 0)
check("ε → 0 で、フーリエ変換はすべての k で 1 に近づく", sp.limit(sp.exp(-eps**2 * kk**2 / 2), eps, 0, "+") == 1)

print(f"すべて一致：{len(results)} 件")
