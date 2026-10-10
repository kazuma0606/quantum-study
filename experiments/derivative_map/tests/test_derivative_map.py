"""微分の地図ノートの主張の検算（反例、離散化と計量、弱微分、ヤコビアン、リー括弧、確率微分、分数階微分、複素微分、差分と自動微分）。"""

import math
import sys
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import derivative_map as dm  # noqa: E402


# ------------------------------------------------------------- 層1：反例
def test_directional_derivative_exists_but_is_not_additive():
    v = {"e1": (1.0, 0.0), "e2": (0.0, 1.0), "sum": (1.0, 1.0), "diag": (2.0, -1.0)}
    got = {k: dm.directional_quotient(dm.f_nonadditive, w, 1e-9) for k, w in v.items()}
    for k, w in v.items():
        assert np.isclose(got[k], dm.gateaux_differential_nonadditive(w), atol=1e-6)
    assert np.isclose(got["e1"] + got["e2"], 1.0) and np.isclose(got["sum"], 0.5)  # 1+0 ≠ 1/2
    # 斉次性（α 倍）は成り立つ
    assert np.isclose(dm.directional_quotient(dm.f_nonadditive, (3.0, 3.0), 1e-9), 3 * got["sum"], atol=1e-6)


def test_partial_derivatives_exist_but_other_directions_do_not():
    for axis in [(1.0, 0.0), (0.0, 1.0)]:
        assert dm.directional_quotient(dm.f_partials_only, axis, 1e-6) == 0.0  # 偏微分は 0
    q1 = dm.directional_quotient(dm.f_partials_only, (1.0, 1.0), 1e-2)
    q2 = dm.directional_quotient(dm.f_partials_only, (1.0, 1.0), 1e-4)
    assert np.isclose(q1, 50.0) and np.isclose(q2, 5000.0)  # 1/(2t) で発散


def test_linear_gateaux_derivative_but_not_differentiable():
    dirs = [(1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, -2.0), (-1.0, 0.5)]
    for w in dirs:
        assert abs(dm.directional_quotient(dm.f_gateaux_zero, w, 1e-4)) < 1e-3  # 全方向で 0（線形）
    # しかし、曲線 y=x³ に沿って f は 1/2 のまま（原点で連続ですらない）
    for x in [1e-1, 1e-2, 1e-3]:
        assert np.isclose(dm.f_gateaux_zero(x, x**3), 0.5)


# ------------------------------------------------------------- 層2
def test_autodiff_of_discretized_functional_is_dx_times_functional_derivative():
    g, ratio, exact, dx = dm.functional_gradient_ratio(n=400)
    assert np.abs(ratio - exact).max() < 1e-3  # g/dx → −u''（汎関数微分）
    assert np.abs(g - exact).max() > 1.0  # 自動微分の成分そのものは、dx 倍だけ小さい（計量 g=dx·I の逆を掛ける前）
    _, ratio2, exact2, _ = dm.functional_gradient_ratio(n=800)
    assert np.abs(ratio2 - exact2).max() < np.abs(ratio - exact).max() / 3  # 誤差は O(dx²) で減る


def test_weak_derivative_pairings():
    a, b, c, d = dm.weak_derivative_pairing()
    assert abs(a) > 1e-3 and np.isclose(a, b, atol=1e-9)  # |x| の弱微分は sign
    assert abs(d) > 1e-3 and np.isclose(c, d, atol=1e-9)  # sign の超関数微分は 2δ


def test_jacobian_is_density_of_pulled_back_measure():
    assert np.isclose(dm.gaussian_integral_in_polar(), math.pi, atol=1e-8)
    for (u, v) in [(0.0, 0.0), (0.3, -0.7), (1.2, 0.5)]:
        ad, exact = dm.paraboloid_area_element(u, v)
        assert np.isclose(ad, exact)  # 非正方ヤコビ行列では √det(JᵀJ)


def test_lie_derivative_is_not_function_linear_in_X():
    assert dm.lie_bracket_function_linearity() == [0, 0]  # [fX,Y] = f[X,Y] − Y(f)X


def test_ito_vs_stratonovich():
    ito, strat, qv, WT = dm.ito_stratonovich()
    assert np.allclose(strat, WT**2 / 2)  # 中点は望遠鏡和で W_T²/2（通常の連鎖律）
    assert np.allclose(ito, (WT**2 - qv) / 2)  # 左端点は 2次変動の分だけずれる
    assert abs(ito.mean()) < 0.05 and abs(strat.mean() - 0.5) < 0.05
    assert abs((strat - ito).mean() - 0.5) < 0.01  # 差は 2次変動 ≈ T/2


def test_fractional_derivatives_differ_in_initial_values():
    rl_const, rl_x, caputo_const, x = dm.fractional_derivatives()
    assert sp.simplify(rl_const - 1 / sp.sqrt(sp.pi * x)) == 0  # RL: 定数の 1/2 階微分は 0 でない
    assert sp.simplify(rl_x - sp.gamma(2) / sp.gamma(sp.Rational(3, 2)) * sp.sqrt(x)) == 0  # Γ(2)/Γ(3/2) x^{1/2}
    assert caputo_const == 0  # Caputo: 定数の微分は 0


def test_wirtinger_derivatives():
    out, (x, y) = dm.wirtinger_examples()
    z, zb = x + sp.I * y, x - sp.I * y
    assert sp.simplify(out["zbar"][0]) == 0 and sp.simplify(out["zbar"][1] - 1) == 0  # f=z̄: ∂_z=0, ∂_z̄=1
    assert sp.simplify(out["z2"][1]) == 0 and sp.simplify(out["z2"][0] - 2 * z) == 0  # 正則: ∂_z̄=0
    assert sp.simplify(out["abs2"][0] - zb) == 0 and sp.simplify(out["abs2"][1] - z) == 0  # |z|²


# ------------------------------------------------------------- 層3
def test_finite_difference_orders_and_autodiff():
    rows, ad_err = dm.finite_difference_errors([1e-2, 1e-4, 1e-6, 1e-8, 1e-10])
    by_h = {h: (fe, ce) for h, fe, ce in rows}
    assert np.isclose(by_h[1e-4][0] / 1e-4, math.sin(1.0) / 2, rtol=1e-3)  # 前進差分は O(h)：f''/2
    assert np.isclose(by_h[1e-4][1] / 1e-8, math.cos(1.0) / 6, rtol=1e-3)  # 中心差分は O(h²)：f'''/6
    assert min(ce for _, _, ce in rows) > 1e-12  # 丸め誤差で、差分は頭打ち
    assert ad_err < 1e-15  # 自動微分は丸め誤差の程度


def test_parameter_shift_rule_is_exact():
    for th in [0.0, 0.7, 2.1, -1.3]:
        shift, exact, val, val_exact = dm.parameter_shift_example(th)
        assert np.isclose(shift, exact, atol=1e-12) and np.isclose(val, val_exact, atol=1e-12)


# ------------------------------------------------------------- 交換子・反交換子（関数の側）
def test_composition_difference_example():
    x = sp.symbols("x")
    f, g = sp.Lambda(x, x + 1), sp.Lambda(x, x**2)
    assert sp.simplify(dm.composition_commutator(f, g) - (-2 * x)) == 0  # x²+1 − (x+1)² = −2x


def test_near_ring_distributivity():
    right, left, zero_then_h, h_then_zero = dm.near_ring_examples()
    x = sp.symbols("x")
    assert right == 0  # (f+g)∘h = f∘h + g∘h
    assert sp.simplify(left - (2 * x + 2) * sp.cos(x)) == 0  # f∘(g+h) − (f∘g+f∘h) = 2gh ≠ 0（f=x², g=x+1, h=cos x）
    assert zero_then_h == 0 and h_then_zero == 1  # 0∘h = 0 だが h∘0 = h(0) = 1


def test_composition_difference_is_not_bilinear_and_fails_jacobi():
    x = sp.symbols("x")
    example, additivity_gap, jacobi = dm.composition_commutator_examples()
    assert sp.simplify(example + 2 * x) == 0
    assert sp.simplify(additivity_gap + 2 * x) == 0  # [x+1, x²] = −2x だが [x,x²]+[1,x²] = 0
    assert sp.simplify(jacobi - (-12 * x**4 - 24 * x**3 - 12 * x**2 - 1)) == 0  # ヤコビ恒等式が成り立たない


def test_hand_computation_of_the_jacobi_counterexample():
    x = sp.symbols("x")
    p = dm.composition_jacobi_pieces()
    expect = {
        "[a,b]": 2 * x, "[b,c]": -3 * x**2 - 3 * x, "[c,a]": sp.Integer(0),
        "[[a,b],c]": -6 * x**3, "[[b,c],a]": -12 * x**4 - 18 * x**3 - 12 * x**2, "[[c,a],b]": sp.Integer(-1),
    }
    for k, v in expect.items():
        assert sp.simplify(p[k] - v) == 0, k


def test_matrix_commutator_is_a_lie_bracket():
    jac, bil = dm.matrix_commutator_is_a_lie_bracket()
    assert jac < 1e-12 and bil < 1e-12


def test_group_commutator_of_maps():
    x = sp.symbols("x")
    nontrivial, trivial = dm.group_commutator_of_affine_maps()
    assert sp.simplify(nontrivial - (x - 1)) == 0  # f=x+1, g=2x：f∘g∘f⁻¹∘g⁻¹ = x−1
    assert sp.simplify(trivial - x) == 0  # 平行移動どうしは可換


def test_group_commutator_expansion_gives_matrix_commutator():
    c = dm.group_commutator_coefficients()
    zero = sp.zeros(2)
    for key in ("const", "t", "s", "t2", "s2", "ts"):
        assert c[key] == zero, key  # 定数項は I、t, s, t², s² の係数は 0、ts の係数は [A,B]


def test_derivative_is_commutator_with_D():
    assert dm.derivative_as_commutator() == (0, 0)  # [D, f·]h = f'h、[D, x] = 1


def test_lie_bracket_is_a_first_order_operator():
    assert dm.lie_bracket_is_first_order() == 0


def test_cartan_formula_on_one_forms():
    assert dm.cartan_formula_on_one_forms() == [0, 0]  # L_X ω = d ι_X ω + ι_X dω


def test_dirac_operator_squares_to_laplacian():
    assert all(e == 0 for e in dm.dirac_operator_squared())  # (σ·∇)² = ∇²


def test_pauli_anticommutation_and_commutation():
    anti, comm_xy = dm.anticommutator_check()
    assert all(m == sp.zeros(2) for row in anti for m in row)  # {σ_i,σ_j} = 2δ_ij I
    assert comm_xy == sp.zeros(2)  # [σ_x,σ_y] = 2iσ_z


def test_poisson_bracket_properties():
    qp, jacobi, leibniz, lie = dm.poisson_checks()
    assert qp == 1 and jacobi == 0 and leibniz == 0
    assert lie == 0  # [X_f, X_g] = −X_{{f,g}}（X_f = {·, f}）
