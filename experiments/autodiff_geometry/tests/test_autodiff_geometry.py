"""自動微分が返すものについての主張を、JAX・PyTorch・TensorFlow の3つで検算する（README の表の各行に対応）。"""

import sys
from pathlib import Path

import jax.numpy as jnp
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import autodiff_geometry as ag  # noqa: E402

Q = np.array([ag.R0, ag.TH0])


# ---------------------------------------------------------------- (a) grad は dL を返す
@pytest.mark.parametrize("lib", ag.LIBS)
def test_grad_is_dL_components(lib):
    assert np.allclose(ag.grad_of_f(lib, Q), ag.df_exact(Q))


def test_gradient_vector_is_a_different_object_from_dL():
    df = ag.df_exact(Q)
    # 座標基底の勾配ベクトル g^{ij}∂_j f は、r 成分は同じだが θ 成分は 1/r² 倍
    assert np.allclose(ag.gradient_vector_coord(Q), [df[0], df[1] / ag.R0**2])
    # 正規直交基底での成分は 1/r 倍
    assert np.allclose(ag.gradient_orthonormal(Q), [df[0], df[1] / ag.R0])
    assert not np.allclose(ag.gradient_vector_coord(Q), df)


def test_hand_values_at_r2_theta0():
    # 本文の例：r=2, θ=0 で dL=(0,4)、座標基底の勾配ベクトル=(0,1)、正規直交基底の成分=(0,2)
    q0 = np.array([2.0, 0.0])
    assert np.allclose(ag.grad_of_f("jax", q0), [0.0, 4.0])
    assert np.allclose(ag.gradient_vector_coord(q0), [0.0, 1.0])
    assert np.allclose(ag.gradient_orthonormal(q0), [0.0, 2.0])


# ---------------------------------------------------------------- (b) 2階微分とラプラシアン
def test_hessians_agree_across_libraries():
    h = {lib: ag.hessian_of_f(lib, Q) for lib in ag.LIBS}
    for lib in ag.LIBS:
        assert np.allclose(h[lib], h["jax"])


@pytest.mark.parametrize("lib", ag.LIBS)
def test_naive_sum_of_second_derivatives_is_not_the_laplacian(lib):
    naive = ag.laplacian_naive(lib, Q)
    assert abs(naive - ag.laplacian_true(Q)) > 1.0
    # (2 − r²) sinθ に等しい
    assert np.isclose(naive, (2 - ag.R0**2) * np.sin(ag.TH0))


def test_true_laplacian_matches_cartesian_autodiff():
    assert np.isclose(ag.laplacian_true(Q), ag.laplacian_cartesian_autodiff(Q))


def test_christoffel_symbols_from_autodiff_of_metric():
    gamma = ag.christoffel_from_metric(ag.metric_polar, Q)
    r = ag.R0
    assert np.isclose(gamma[0, 1, 1], -r)  # Γ^r_θθ = −r
    assert np.isclose(gamma[1, 0, 1], 1 / r) and np.isclose(gamma[1, 1, 0], 1 / r)  # Γ^θ_rθ = 1/r
    mask = np.ones((2, 2, 2), bool)
    for idx in [(0, 1, 1), (1, 0, 1), (1, 1, 0)]:
        mask[idx] = False
    assert np.allclose(gamma[mask], 0.0)  # 残りはすべて 0


def test_covariant_hessian_trace_is_the_laplacian():
    assert np.isclose(ag.laplacian_covariant(Q), ag.laplacian_true(Q))


@pytest.mark.parametrize("q", [Q, np.array([1.3, 1.1]), np.array([0.6, 2.5])])
def test_laplace_beltrami_built_from_metric_only(q):
    assert np.isclose(ag.laplace_beltrami(ag.f_jax, ag.metric_polar, q), ag.laplacian_true(q))


def test_laplace_beltrami_on_the_sphere_surface():
    # 単位球面（θ, φ）上で f = cosθ は Δf = −2 cosθ（l=1 の球面調和関数）
    metric = lambda p: jnp.diag(jnp.array([1.0, jnp.sin(p[0]) ** 2]))
    f = lambda p: jnp.cos(p[0])
    q = np.array([0.9, 0.4])
    assert np.isclose(ag.laplace_beltrami(f, metric, q), -2 * np.cos(0.9))


# ---------------------------------------------------------------- (c) 再パラメータ化
@pytest.mark.parametrize("lib", ag.LIBS)
def test_gradient_descent_depends_on_parametrization(lib):
    exact = ag.w_exact_gradient_flow()
    w_w = ag.descent_end_w(lib, "w")
    w_phi = ag.descent_end_w(lib, "phi")
    w_nat = ag.descent_end_w(lib, "phi_natural")
    assert abs(w_w - exact) < 2e-3  # w 座標の勾配降下法は勾配流に近い
    assert abs(w_phi - exact) > 0.5  # φ 座標の勾配降下法は、同じ損失・同じ学習率でも別の軌跡
    assert abs(w_nat - exact) < 2e-3  # 計量で補正すると、w 座標の結果に（学習率の1次の差で）一致


def test_descent_results_agree_across_libraries():
    for kind in ("w", "phi", "phi_natural"):
        vals = [ag.descent_end_w(lib, kind) for lib in ag.LIBS]
        assert np.allclose(vals, vals[0], atol=1e-9)


def test_natural_gradient_converges_to_flow_as_lr_shrinks():
    e1 = abs(ag.descent_end_w("jax", "phi_natural", lr=1e-3, steps=1000) - ag.w_exact_gradient_flow())
    e2 = abs(ag.descent_end_w("jax", "phi_natural", lr=1e-4, steps=10000) - ag.w_exact_gradient_flow())
    assert e2 < e1 / 5  # 誤差は学習率にほぼ比例して小さくなる


# ---------------------------------------------------------------- (d) 複素数の規約
def test_complex_gradient_conventions():
    z0 = 1.0 + 2.0j
    got = {lib: ag.complex_grad_abs2(lib, z0) for lib in ag.LIBS}
    assert np.isclose(got["torch"], 2 * z0)  # ∂f/∂x + i ∂f/∂y（最急上昇の向き）
    assert np.isclose(got["tf"], 2 * z0)
    assert np.isclose(got["jax"], 2 * np.conj(z0))  # ∂f/∂x − i ∂f/∂y（共役）
