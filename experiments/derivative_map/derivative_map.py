"""微分の地図ノート（研究ノート/01_基礎・ベクトル解析/derivative_map.md）の主張を、数値と記号計算で確かめる。

層1（定義の強さ）: ガトー微分とフレシェ微分の差を示す反例
層2（対象と構造）: 汎関数微分（離散化と計量）、弱微分、ヤコビアンと面積要素、リー括弧の関数線形性、
                  伊藤とストラトノビッチ、分数階微分、ウィルティンガー微分
層3（計算法）  : 差分の誤差と自動微分、パラメータシフト則

使い方:
    uv run python experiments/derivative_map/derivative_map.py     # 値を表示する
    uv run pytest experiments/derivative_map -q                    # 検算
"""

import math

import jax
import jax.numpy as jnp
import numpy as np
import sympy as sp
from scipy import integrate
from scipy.linalg import expm

jax.config.update("jax_enable_x64", True)


# ===================================================================== 層1：反例
def f_nonadditive(x, y):
    """f = x³/(x²+y²)（原点で 0）。原点で全方向の方向微分があるが、方向について加法的でない。"""
    r2 = x**2 + y**2
    return 0.0 if r2 == 0 else x**3 / r2


def f_partials_only(x, y):
    """f = xy/(x²+y²)（原点で 0）。原点で偏微分は存在するが、ほかの方向の方向微分は存在しない。"""
    r2 = x**2 + y**2
    return 0.0 if r2 == 0 else x * y / r2


def f_gateaux_zero(x, y):
    """f = x³y/(x⁶+y²)（原点で 0）。原点の方向微分は全方向で 0（線形）だが、曲線 y=x³ に沿って 1/2 のまま。"""
    d = x**6 + y**2
    return 0.0 if d == 0 else x**3 * y / d


def directional_quotient(f, v, t):
    """(f(t v) − f(0)) / t。"""
    return (f(t * v[0], t * v[1]) - f(0.0, 0.0)) / t


def gateaux_differential_nonadditive(v):
    """f_nonadditive の原点での方向微分の厳密な式 v1³/(v1²+v2²)。"""
    return v[0] ** 3 / (v[0] ** 2 + v[1] ** 2)


# ===================================================================== 層2
def functional_gradient_ratio(n=400):
    """J[u]=∫₀¹ (u')²/2 dx を離散化し、自動微分した成分を dx で割る。−u'' に近づく（成分は dx·(−u'')）。

    戻り値：(自動微分の成分, 成分/dx, −u'' の厳密値, dx)
    """
    dx = 1.0 / (n + 1)
    x = jnp.linspace(dx, 1 - dx, n)

    def J(u_inner):
        u = jnp.concatenate([jnp.zeros(1), u_inner, jnp.zeros(1)])
        du = (u[1:] - u[:-1]) / dx
        return jnp.sum(0.5 * du**2) * dx

    u0 = jnp.sin(jnp.pi * x)
    g = np.asarray(jax.grad(J)(u0))
    exact = np.asarray(jnp.pi**2 * jnp.sin(jnp.pi * x))  # −u'' = π² sin(πx)
    return g, g / dx, exact, dx


def bump(x):
    """コンパクト台の滑らかな試験関数。"""
    return math.exp(-1.0 / (1.0 - x * x)) if abs(x) < 1 else 0.0


def dbump(x):
    return bump(x) * (-2.0 * x / (1.0 - x * x) ** 2) if abs(x) < 1 else 0.0


SHIFT = 0.3  # 試験関数の山を 0.3 だけずらす（x=0 の折れ目が台の中で非対称になる）


def weak_derivative_pairing():
    """∫|x| φ' dx と −∫ sign(x) φ dx（|x| の弱微分が sign）、∫ sign φ' dx と −2φ(0)（sign の超関数微分が 2δ）。

    φ(x)=bump(x−0.3)（台は (−0.7, 1.3)）。山が x=0 に対して対称だと、左辺も右辺も自明に 0 になるのでずらす。
    """
    phi = lambda x: bump(x - SHIFT)
    dphi = lambda x: dbump(x - SHIFT)
    lo, hi = -1 + SHIFT, 1 + SHIFT
    a = integrate.quad(lambda x: abs(x) * dphi(x), lo, hi, points=[0.0])[0]
    b = -integrate.quad(lambda x: np.sign(x) * phi(x), lo, hi, points=[0.0])[0]
    c = integrate.quad(lambda x: np.sign(x) * dphi(x), lo, hi, points=[0.0])[0]
    return a, b, c, -2 * phi(0.0)


def gaussian_integral_in_polar():
    """∬ exp(−(x²+y²)) dx dy = π を、ヤコビアン r を掛けた極座標の積分で確かめる。"""
    val = integrate.dblquad(lambda r, th: math.exp(-r * r) * r, 0, 2 * math.pi, 0, 12)[0]
    return val


def paraboloid_area_element(u, v):
    """面 (u, v, u²+v²) の面積要素 √det(JᵀJ) を、自動微分のヤコビ行列から求める。"""
    phi = lambda p: jnp.array([p[0], p[1], p[0] ** 2 + p[1] ** 2])
    J = jax.jacfwd(phi)(jnp.array([u, v]))
    return float(jnp.sqrt(jnp.linalg.det(J.T @ J))), math.sqrt(1 + 4 * u * u + 4 * v * v)


def lie_bracket_function_linearity():
    """[fX, Y] = f[X, Y] − Y(f) X を、一般の関数で記号的に確かめる（リー微分は X について関数線形でない）。"""
    x, y = sp.symbols("x y")
    f = sp.Function("f")(x, y)
    X = [sp.Function("X1")(x, y), sp.Function("X2")(x, y)]
    Y = [sp.Function("Y1")(x, y), sp.Function("Y2")(x, y)]
    coords = [x, y]

    def bracket(A, B):
        return [sum(A[j] * sp.diff(B[i], coords[j]) - B[j] * sp.diff(A[i], coords[j]) for j in range(2)) for i in range(2)]

    fX = [f * c for c in X]
    lhs = bracket(fX, Y)
    br = bracket(X, Y)
    Yf = sum(Y[j] * sp.diff(f, coords[j]) for j in range(2))
    rhs = [f * br[i] - Yf * X[i] for i in range(2)]
    return [sp.simplify(lhs[i] - rhs[i]) for i in range(2)]


def ito_stratonovich(T=1.0, n=4096, paths=4000, seed=0):
    """∫₀ᵀ W dW を、左端点（伊藤）と中点（ストラトノビッチ）で近似する。"""
    rng = np.random.default_rng(seed)
    dW = rng.normal(0.0, math.sqrt(T / n), size=(paths, n))
    W = np.concatenate([np.zeros((paths, 1)), np.cumsum(dW, axis=1)], axis=1)
    ito = np.sum(W[:, :-1] * dW, axis=1)
    strat = np.sum(0.5 * (W[:, :-1] + W[:, 1:]) * dW, axis=1)
    qv = np.sum(dW**2, axis=1)  # 2次変動
    return ito, strat, qv, W[:, -1]


def fractional_derivatives():
    """Riemann–Liouville 分数階微分（α=1/2）と Caputo 微分。f=1 で前者は 1/√(πx)、後者は 0。f=x で RL は 2√(x/π)。"""
    x, s = sp.symbols("x s", positive=True)
    alpha = sp.Rational(1, 2)

    def rl_integral(expr):
        return sp.simplify(sp.integrate((x - s) ** (-alpha) * expr, (s, 0, x)) / sp.gamma(alpha))

    rl_const = sp.simplify(sp.diff(rl_integral(sp.Integer(1)), x))
    rl_x = sp.simplify(sp.diff(rl_integral(s), x))
    caputo_const = sp.simplify(rl_integral(sp.Integer(0)))  # I^{1/2} f' = I^{1/2} 0
    return rl_const, rl_x, caputo_const, x


def wirtinger_examples():
    """f=z̄、f=z²、f=|z|² のウィルティンガー微分 ∂/∂z=(∂x−i∂y)/2、∂/∂z̄=(∂x+i∂y)/2。"""
    x, y = sp.symbols("x y", real=True)
    z = x + sp.I * y
    zb = x - sp.I * y

    def dz(f):
        return sp.simplify((sp.diff(f, x) - sp.I * sp.diff(f, y)) / 2)

    def dzb(f):
        return sp.simplify((sp.diff(f, x) + sp.I * sp.diff(f, y)) / 2)

    out = {}
    for name, f in {"zbar": zb, "z2": z**2, "abs2": sp.expand(z * zb)}.items():
        out[name] = (dz(f), dzb(f))
    return out, (x, y)


# ===================================================================== 層3
def finite_difference_errors(h_list, x0=1.0):
    """sin の微分を、前進差分・中心差分・自動微分で求めたときの誤差。"""
    exact = math.cos(x0)
    ad = float(jax.grad(jnp.sin)(x0))
    rows = []
    for h in h_list:
        fwd = (math.sin(x0 + h) - math.sin(x0)) / h
        cen = (math.sin(x0 + h) - math.sin(x0 - h)) / (2 * h)
        rows.append((h, abs(fwd - exact), abs(cen - exact)))
    return rows, abs(ad - exact)


def parameter_shift_example(theta):
    """RY(θ)|0⟩ の ⟨Z⟩ = cosθ の θ 微分を、パラメータシフト則 ½[f(θ+π/2) − f(θ−π/2)] で求める。"""
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    def expval(t):
        state = expm(-1j * t / 2 * Y) @ np.array([1, 0], dtype=complex)
        return float(np.real(state.conj() @ Z @ state))

    shift = 0.5 * (expval(theta + math.pi / 2) - expval(theta - math.pi / 2))
    return shift, -math.sin(theta), expval(theta), math.cos(theta)


# ===================================================================== 交換子・反交換子（関数の側）
_X = sp.symbols("x")


def composition_commutator(f, g):
    """合成の差 [f,g] := f∘g − g∘f（f, g は sympy.Lambda）。"""
    return sp.simplify(f(g(_X)) - g(f(_X)))


def near_ring_examples():
    """関数の全体 (写像, 点ごとの和, 合成) の分配法則。右分配 (f+g)∘h = f∘h + g∘h は成り立ち、左分配 f∘(g+h) は成り立たない。
    また 0∘x = 0 だが x∘0 は 0 と限らない。"""
    f = sp.Lambda(_X, _X**2)
    g = sp.Lambda(_X, _X + 1)
    h = sp.Lambda(_X, sp.cos(_X))
    right = sp.simplify((f(_X) + g(_X)).subs(_X, h(_X)) - (f(h(_X)) + g(h(_X))))  # (f+g)∘h − (f∘h+g∘h)
    left = sp.simplify(f(g(_X) + h(_X)) - (f(g(_X)) + f(h(_X))))  # f∘(g+h) − (f∘g+f∘h)
    zero = sp.Lambda(_X, sp.Integer(0))
    zero_then_h = sp.simplify(zero(h(_X)))  # 0∘h = 0
    h_then_zero = sp.simplify(h(zero(_X)))  # h∘0 = h(0) = 1
    return right, left, zero_then_h, h_then_zero


def composition_commutator_examples():
    """合成の差の例と、双線形でないこと、ヤコビ恒等式が成り立たないこと。"""
    f = sp.Lambda(_X, _X + 1)
    g = sp.Lambda(_X, _X**2)
    example = composition_commutator(f, g)  # −2x

    # 第1引数について加法的でない：[f1+f2, g] ≠ [f1,g] + [f2,g]
    f1 = sp.Lambda(_X, _X)
    f2 = sp.Lambda(_X, sp.Integer(1))
    f12 = sp.Lambda(_X, f1(_X) + f2(_X))
    additivity_gap = sp.simplify(composition_commutator(f12, g) - (composition_commutator(f1, g) + composition_commutator(f2, g)))

    # ヤコビ恒等式
    def br(a, b):
        return sp.Lambda(_X, a(b(_X)) - b(a(_X)))

    a, b, c = sp.Lambda(_X, _X**2), sp.Lambda(_X, _X + 1), sp.Lambda(_X, _X**3)
    jacobi = sp.simplify(br(br(a, b), c)(_X) + br(br(b, c), a)(_X) + br(br(c, a), b)(_X))
    return example, additivity_gap, jacobi


def composition_jacobi_pieces():
    """ノートの手計算の途中結果：a=x², b=x+1, c=x³ の合成の差 [a,b]、[b,c]、[c,a] と、二重の括弧 3 つ。"""

    def br(u, v):
        return sp.Lambda(_X, sp.expand(u(v(_X)) - v(u(_X))))

    a, b, c = sp.Lambda(_X, _X**2), sp.Lambda(_X, _X + 1), sp.Lambda(_X, _X**3)
    ab, bc, ca = br(a, b), br(b, c), br(c, a)
    return {
        "[a,b]": ab(_X), "[b,c]": bc(_X), "[c,a]": ca(_X),
        "[[a,b],c]": br(ab, c)(_X), "[[b,c],a]": br(bc, a)(_X), "[[c,a],b]": br(ca, b)(_X),
    }


def group_commutator_of_affine_maps():
    """f(x)=x+1、g(x)=2x の群の交換子 f∘g∘f⁻¹∘g⁻¹。x−1（平行移動）になる。可換な平行移動どうしでは恒等写像。"""
    f = sp.Lambda(_X, _X + 1)
    g = sp.Lambda(_X, 2 * _X)
    f_inv = sp.Lambda(_X, _X - 1)
    g_inv = sp.Lambda(_X, _X / 2)
    nontrivial = sp.simplify(f(g(f_inv(g_inv(_X)))))
    t1 = sp.Lambda(_X, _X + 3)
    t2 = sp.Lambda(_X, _X + 5)
    t1_inv = sp.Lambda(_X, _X - 3)
    t2_inv = sp.Lambda(_X, _X - 5)
    trivial = sp.simplify(t1(t2(t1_inv(t2_inv(_X)))))
    return nontrivial, trivial


def matrix_commutator_is_a_lie_bracket(seed=0):
    """線形写像（行列）では、積 AB が双線形なので [A,B]=AB−BA は双線形でヤコビ恒等式を満たす。"""
    rng = np.random.default_rng(seed)
    A, B, C = (rng.normal(size=(3, 3)) for _ in range(3))
    br = lambda P, Q: P @ Q - Q @ P
    jacobi = br(br(A, B), C) + br(br(B, C), A) + br(br(C, A), B)
    bilinear = br(2 * A + 3 * B, C) - (2 * br(A, C) + 3 * br(B, C))
    return np.abs(jacobi).max(), np.abs(bilinear).max()


def group_commutator_coefficients():
    """e^{tA} e^{sB} e^{-tA} e^{-sB} を t, s の3次まで展開し、各係数を調べる（一般の 2×2 行列 A, B）。"""
    t, s = sp.symbols("t s")
    A = sp.Matrix(2, 2, sp.symbols("a0:4"))
    B = sp.Matrix(2, 2, sp.symbols("b0:4"))

    def E(M, order=3):
        out = sp.zeros(2)
        for k in range(order + 1):
            out += M**k / sp.factorial(k)
        return out

    P = (E(t * A) * E(s * B) * E(-t * A) * E(-s * B)).applyfunc(sp.expand)

    def coeff(mono):
        return P.applyfunc(lambda e: sp.Poly(e, t, s).coeff_monomial(mono))

    comm = A * B - B * A
    return {
        "const": sp.simplify(coeff(1) - sp.eye(2)),
        "t": coeff(t),
        "s": coeff(s),
        "t2": coeff(t**2),
        "s2": coeff(s**2),
        "ts": sp.simplify(coeff(t * s) - comm),
    }


def derivative_as_commutator():
    """[D, f·] h = f' h、[D, x] = 1（h は一般の関数）。"""
    f = sp.Function("f")(_X)
    h = sp.Function("h")(_X)
    D = lambda u: sp.diff(u, _X)
    gap_f = sp.simplify(D(f * h) - f * D(h) - sp.diff(f, _X) * h)
    gap_x = sp.simplify(D(_X * h) - _X * D(h) - h)
    return gap_f, gap_x


def lie_bracket_is_first_order():
    """X(Yf) − Y(Xf) = Σ (X(Y^i) − Y(X^i)) ∂_i f（2階微分の項が消える）。X, Y, f は一般の関数（2次元）。"""
    x, y = sp.symbols("x y")
    co = [x, y]
    f = sp.Function("f")(x, y)
    X = [sp.Function("X1")(x, y), sp.Function("X2")(x, y)]
    Y = [sp.Function("Y1")(x, y), sp.Function("Y2")(x, y)]
    apply = lambda V, u: sum(V[i] * sp.diff(u, co[i]) for i in range(2))
    lhs = apply(X, apply(Y, f)) - apply(Y, apply(X, f))
    comps = [apply(X, Y[i]) - apply(Y, X[i]) for i in range(2)]
    rhs = sum(comps[i] * sp.diff(f, co[i]) for i in range(2))
    return sp.simplify(sp.expand(lhs - rhs))


def cartan_formula_on_one_forms():
    """カルタンの公式 L_X ω = d(ι_X ω) + ι_X(dω) を、2次元の1-形式で成分ごとに確かめる。
    リー微分の成分は (L_X ω)_j = X^i ∂_i ω_j + ω_i ∂_j X^i。"""
    x, y = sp.symbols("x y")
    co = [x, y]
    X = [sp.Function("X1")(x, y), sp.Function("X2")(x, y)]
    w = [sp.Function("w1")(x, y), sp.Function("w2")(x, y)]
    lie = [sum(X[i] * sp.diff(w[j], co[i]) + w[i] * sp.diff(X[i], co[j]) for i in range(2)) for j in range(2)]
    i_X_w = sum(X[i] * w[i] for i in range(2))
    d_iXw = [sp.diff(i_X_w, co[j]) for j in range(2)]
    F = sp.diff(w[1], x) - sp.diff(w[0], y)  # dω = F dx∧dy
    iX_dw = [-F * X[1], F * X[0]]  # ι_X(dx∧dy) = X^x dy − X^y dx
    return [sp.simplify(sp.expand(lie[j] - d_iXw[j] - iX_dw[j])) for j in range(2)]


def dirac_operator_squared():
    """(σ·∇)² ψ − ∇² ψ = 0（ψ は一般の2成分スピノル、3次元）。{σ_i,σ_j}=2δ_ij と ∂ の可換性による。"""
    x, y, z = sp.symbols("x y z")
    co = [x, y, z]
    sx = sp.Matrix([[0, 1], [1, 0]])
    sy = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sz = sp.Matrix([[1, 0], [0, -1]])
    sig = [sx, sy, sz]
    psi = sp.Matrix([sp.Function("p1")(x, y, z), sp.Function("p2")(x, y, z)])
    op = lambda v: sum((sig[i] * v.diff(co[i]) for i in range(3)), sp.zeros(2, 1))
    lap = lambda v: sum((v.diff(c, 2) for c in co), sp.zeros(2, 1))
    return (op(op(psi)) - lap(psi)).applyfunc(sp.simplify)


def anticommutator_check():
    """{σ_i,σ_j} = 2δ_ij I と [σ_i,σ_j] = 2i ε_ijk σ_k。"""
    sx = sp.Matrix([[0, 1], [1, 0]])
    sy = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sz = sp.Matrix([[1, 0], [0, -1]])
    sig = [sx, sy, sz]
    anti = [[(sig[i] * sig[j] + sig[j] * sig[i]) - 2 * (1 if i == j else 0) * sp.eye(2) for j in range(3)] for i in range(3)]
    comm_xy = sig[0] * sig[1] - sig[1] * sig[0] - 2 * sp.I * sz
    return anti, comm_xy


def poisson_checks():
    """ポアソン括弧 {f,g} = f_q g_p − f_p g_q（1自由度）。{q,p}=1、ヤコビ、ライプニッツ、
    X_f := {·, f} とすると [X_f, X_g] = −X_{{f,g}}（符号は流儀による）。"""
    q, p = sp.symbols("q p")
    PB = lambda f, g: sp.diff(f, q) * sp.diff(g, p) - sp.diff(f, p) * sp.diff(g, q)
    f, g, h = q**2 * p, p**2 + q**3, q * p + sp.sin(q)
    jacobi = sp.simplify(PB(PB(f, g), h) + PB(PB(g, h), f) + PB(PB(h, f), g))
    leibniz = sp.simplify(PB(f * g, h) - (f * PB(g, h) + PB(f, h) * g))
    H = sp.Function("H")(q, p)
    Xf = lambda u: PB(u, f)
    Xg = lambda u: PB(u, g)
    XPB = lambda u: PB(u, PB(f, g))
    lie = sp.simplify(sp.expand(Xf(Xg(H)) - Xg(Xf(H)) + XPB(H)))  # [X_f,X_g]H + X_{{f,g}}H = 0 なら符号は −
    return sp.simplify(PB(q, p)), jacobi, leibniz, lie


def main():
    print("(層1) f=x³/(x²+y²): 方向 (1,0),(0,1),(1,1) の方向微分",
          [round(directional_quotient(f_nonadditive, v, 1e-8), 6) for v in [(1, 0), (0, 1), (1, 1)]])
    print("      加法的なら (1,1) は 1+0=1 のはずだが、実際は 0.5")
    print("(層1) f=xy/(x²+y²): 方向 (1,1) の差商 t=1e-2,1e-4:",
          [directional_quotient(f_partials_only, (1, 1), t) for t in (1e-2, 1e-4)])
    print("(層1) f=x³y/(x⁶+y²): 全方向の方向微分は 0（t=1e-4）:",
          [round(directional_quotient(f_gateaux_zero, v, 1e-4), 8) for v in [(1, 0), (0, 1), (1, 1), (1, -2)]],
          " 曲線 y=x³ 上の f(x,x³) =", f_gateaux_zero(1e-3, 1e-9))
    g, ratio, exact, dx = functional_gradient_ratio()
    print("(層2) 離散化した汎関数の勾配の成分を dx で割ると −u'' に近づく: 最大誤差", np.abs(ratio - exact).max(), " dx =", dx)
    print("(層2) 弱微分のペアリング ∫|x|φ' vs −∫sign φ:", weak_derivative_pairing()[:2],
          "  ∫sign φ' vs −2φ(0):", weak_derivative_pairing()[2:])
    print("(層2) ∬exp(−r²) =", gaussian_integral_in_polar(), "(π =", math.pi, ")")
    print("(層2) 放物面の面積要素 √det(JᵀJ):", paraboloid_area_element(0.3, -0.7))
    print("(層2) リー括弧の関数線形性の差（0 のはず）:", lie_bracket_function_linearity())
    ito, strat, qv, WT = ito_stratonovich()
    print("(層2) ∫W dW 伊藤の平均", ito.mean(), "ストラトノビッチの平均", strat.mean(), "（T/2 =0.5）  差の平均", (strat - ito).mean())
    print("(層2) 分数階微分", fractional_derivatives())
    print("(層3) 差分の誤差（h, 前進, 中心）と自動微分の誤差:", finite_difference_errors([1e-2, 1e-4, 1e-6, 1e-8, 1e-10]))
    print("(層3) パラメータシフト則:", parameter_shift_example(0.7))


if __name__ == "__main__":
    main()
