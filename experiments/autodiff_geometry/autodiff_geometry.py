"""自動微分（JAX・PyTorch・TensorFlow）が返すものを、極座標・再パラメータ化・複素数の例で確かめる。

何を確かめるか（README の表と対応）:
  (a) grad が返すのは dL（余接ベクトル）の成分で、計量を使った勾配ベクトルではない
  (b) 自動微分の2階微分（ヘッセ行列）は座標の2階偏微分。クリストッフェル記号で補正しないと、
      その和はラプラシアンにならない。計量だけから作るラプラス・ベルトラミ作用素も、自動微分で書ける
  (c) 勾配降下法は再パラメータ化で別の方法になる。計量で補正した（自然）勾配なら、座標の取り方によらない
  (d) 複素数の勾配の規約（共役の向き）がライブラリで違う

使い方:
    uv run python experiments/autodiff_geometry/autodiff_geometry.py     # 値を表示する
    uv run pytest experiments/autodiff_geometry -q                       # 検算

TensorFlow は dependency group `tf` に入れてある（`uv sync --group tf`）。
"""

import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import jax
import jax.numpy as jnp
import numpy as np
import tensorflow as tf
import torch

jax.config.update("jax_enable_x64", True)
torch.set_default_dtype(torch.float64)

LIBS = ("jax", "torch", "tf")
R0, TH0 = 2.0, 0.7  # 例の点（r, θ）


# ---------------------------------------------------------------------------- 例の関数
def f_jax(q):
    return q[0] ** 2 * jnp.sin(q[1])


def f_torch(q):
    return q[0] ** 2 * torch.sin(q[1])


def f_tf(q):
    return q[0] ** 2 * tf.sin(q[1])


# ---------------------------------------------------------------------------- (a) 勾配
def grad_of_f(lib, q):
    """f(r,θ)=r² sinθ の自動微分の出力（numpy 配列）。"""
    q = np.asarray(q, dtype=float)
    if lib == "jax":
        return np.asarray(jax.grad(f_jax)(jnp.array(q)))
    if lib == "torch":
        x = torch.tensor(q, requires_grad=True)
        return torch.autograd.grad(f_torch(x), x)[0].numpy()
    if lib == "tf":
        x = tf.constant(q, dtype=tf.float64)
        with tf.GradientTape() as tape:
            tape.watch(x)
            y = f_tf(x)
        return tape.gradient(y, x).numpy()
    raise ValueError(lib)


def df_exact(q):
    """手計算の dL の成分 (∂f/∂r, ∂f/∂θ) = (2 r sinθ, r² cosθ)。"""
    r, th = q
    return np.array([2 * r * np.sin(th), r**2 * np.cos(th)])


def metric_polar(q):
    """極座標の計量 g = diag(1, r²)（JAX で書く。クリストッフェル記号の自動微分に使う）。"""
    return jnp.diag(jnp.array([1.0, q[0] ** 2]))


def gradient_vector_coord(q):
    """座標基底での勾配ベクトルの成分 g^{ij} ∂_j f。"""
    g = np.asarray(metric_polar(jnp.array(q)))
    return np.linalg.inv(g) @ df_exact(q)


def gradient_orthonormal(q):
    """正規直交基底 (e_r, e_θ/r 方向の単位ベクトル) での成分 = (∂r f, (1/r)∂θ f)。"""
    r, _ = q
    d = df_exact(q)
    return np.array([d[0], d[1] / r])


# ---------------------------------------------------------------------------- (b) 2階微分
def hessian_of_f(lib, q):
    """各ライブラリの「ヘッセ行列」（座標の2階偏微分の行列）。"""
    q = np.asarray(q, dtype=float)
    if lib == "jax":
        return np.asarray(jax.hessian(f_jax)(jnp.array(q)))
    if lib == "torch":
        return torch.autograd.functional.hessian(f_torch, torch.tensor(q)).numpy()
    if lib == "tf":
        x = tf.constant(q, dtype=tf.float64)
        with tf.GradientTape() as outer:
            outer.watch(x)
            with tf.GradientTape() as inner:
                inner.watch(x)
                y = f_tf(x)
            g = inner.gradient(y, x)
        return outer.jacobian(g, x).numpy()
    raise ValueError(lib)


def christoffel_from_metric(metric, q):
    """計量 g_{jk}(q) の自動微分から Γ^k_{ij} を作る。戻り値は Gamma[k, i, j]。"""
    q = jnp.asarray(q, dtype=jnp.float64)
    g = np.asarray(metric(q))
    gi = np.linalg.inv(g)
    dg = np.asarray(jax.jacfwd(metric)(q))  # dg[j, k, l] = ∂_l g_{jk}
    n = len(q)
    gamma = np.zeros((n, n, n))
    for k in range(n):
        for i in range(n):
            for j in range(n):
                gamma[k, i, j] = 0.5 * sum(
                    gi[k, l] * (dg[j, l, i] + dg[i, l, j] - dg[i, j, l]) for l in range(n)
                )
    return gamma


def covariant_hessian(hess, df, gamma):
    """共変ヘッセ ∇_i ∂_j f = ∂i∂j f − Γ^k_{ij} ∂k f。"""
    return hess - np.einsum("kij,k->ij", gamma, df)


def laplacian_naive(lib, q):
    """座標ごとの2階偏微分の和（誤った使い方）。"""
    return float(np.trace(hessian_of_f(lib, q)))


def laplacian_true(q):
    """手計算の真のラプラシアン。(1/r)∂r(r ∂r f) + (1/r²)∂θ² f = 3 sinθ。"""
    return 3 * np.sin(q[1])


def laplacian_cartesian_autodiff(q):
    """デカルト座標 f = y √(x²+y²) を自動微分したラプラシアン（独立な確認）。"""
    x0, y0 = q[0] * np.cos(q[1]), q[0] * np.sin(q[1])
    fc = lambda p: p[1] * jnp.sqrt(p[0] ** 2 + p[1] ** 2)
    return float(np.trace(np.asarray(jax.hessian(fc)(jnp.array([x0, y0])))))


def laplacian_covariant(q):
    """共変ヘッセのトレース g^{ij}(∂i∂j f − Γ^k_ij ∂k f)。"""
    gi = np.linalg.inv(np.asarray(metric_polar(jnp.array(q))))
    gamma = christoffel_from_metric(metric_polar, q)
    hc = covariant_hessian(hessian_of_f("jax", q), df_exact(q), gamma)
    return float(np.einsum("ij,ij->", gi, hc))


def laplace_beltrami(f, metric, q):
    """計量 g だけから作るラプラス・ベルトラミ作用素 (1/√g) ∂_j(√g g^{jk} ∂_k f)（JAX の自動微分）。"""
    q = jnp.asarray(q, dtype=jnp.float64)

    def flux(p):  # V^j = √g g^{jk} ∂_k f
        g = metric(p)
        return jnp.sqrt(jnp.linalg.det(g)) * jnp.linalg.inv(g) @ jax.grad(f)(p)

    div = jnp.trace(jax.jacfwd(flux)(q))
    return float(div / jnp.sqrt(jnp.linalg.det(metric(q))))


# ---------------------------------------------------------------------------- (c) 再パラメータ化
W_INIT, LR, STEPS = 0.5, 1e-3, 1000  # 時間 T = LR*STEPS = 1


def _loss_w_np(w):
    return 0.5 * (w - 3.0) ** 2


def dL_dphi(lib, phi):
    """L(w)=½(w−3)², w=φ³ の dL/dφ を各ライブラリの自動微分で求める。"""
    if lib == "jax":
        return float(jax.grad(lambda p: 0.5 * (p**3 - 3.0) ** 2)(phi))
    if lib == "torch":
        p = torch.tensor(phi, requires_grad=True)
        torch.autograd.backward(0.5 * (p**3 - 3.0) ** 2)
        return float(p.grad)
    if lib == "tf":
        p = tf.constant(phi, dtype=tf.float64)
        with tf.GradientTape() as tape:
            tape.watch(p)
            y = 0.5 * (p**3 - 3.0) ** 2
        return float(tape.gradient(y, p))
    raise ValueError(lib)


def dL_dw(lib, w):
    if lib == "jax":
        return float(jax.grad(lambda x: 0.5 * (x - 3.0) ** 2)(w))
    if lib == "torch":
        x = torch.tensor(w, requires_grad=True)
        torch.autograd.backward(0.5 * (x - 3.0) ** 2)
        return float(x.grad)
    if lib == "tf":
        x = tf.constant(w, dtype=tf.float64)
        with tf.GradientTape() as tape:
            tape.watch(x)
            y = 0.5 * (x - 3.0) ** 2
        return float(tape.gradient(y, x))
    raise ValueError(lib)


def descent_end_w(lib, kind, lr=LR, steps=STEPS):
    """勾配降下法を steps 回行った後の w。
    kind="w"          : w 座標でそのまま勾配降下法
    kind="phi"        : φ 座標（w=φ³）でそのまま勾配降下法
    kind="phi_natural": φ 座標で、計量 g_φφ=(dw/dφ)²=9φ⁴ の逆数を掛けた（自然）勾配降下法
    """
    if kind == "w":
        w = W_INIT
        for _ in range(steps):
            w = w - lr * dL_dw(lib, w)
        return w
    phi = W_INIT ** (1 / 3)
    for _ in range(steps):
        g = dL_dphi(lib, phi)
        if kind == "phi_natural":
            g = g / (9 * phi**4)
        phi = phi - lr * g
    return phi**3


def w_exact_gradient_flow(t=LR * STEPS):
    """w 座標の勾配流 ẇ = −(w−3) の厳密解。"""
    return 3 - (3 - W_INIT) * np.exp(-t)


# ---------------------------------------------------------------------------- (d) 複素数の勾配
def complex_grad_abs2(lib, z0):
    """f(z)=|z|² の「勾配」。実部・虚部で書けば f=x²+y²。"""
    if lib == "jax":
        return complex(jax.grad(lambda z: jnp.abs(z) ** 2)(jnp.array(z0)))
    if lib == "torch":
        z = torch.tensor(z0, requires_grad=True)
        torch.abs(z).pow(2).backward()
        return complex(z.grad)
    if lib == "tf":
        z = tf.constant(z0, dtype=tf.complex128)
        with tf.GradientTape() as tape:
            tape.watch(z)
            y = tf.abs(z) ** 2
        return complex(tape.gradient(y, z).numpy())
    raise ValueError(lib)


def main():
    q = np.array([R0, TH0])
    print("(a) f=r² sinθ の dL: 手計算", df_exact(q))
    for lib in LIBS:
        print(f"    {lib:6s}", grad_of_f(lib, q))
    print("    座標基底の勾配ベクトル g^{-1}df:", gradient_vector_coord(q), " 正規直交基底:", gradient_orthonormal(q))
    print("(b) ラプラシアン  真値", laplacian_true(q), " デカルトで自動微分", laplacian_cartesian_autodiff(q))
    for lib in LIBS:
        print(f"    座標の2階偏微分の和 {lib:6s}", laplacian_naive(lib, q))
    print("    共変ヘッセのトレース", laplacian_covariant(q))
    print("    計量だけから作ったラプラス・ベルトラミ", laplace_beltrami(f_jax, metric_polar, q))
    print("(c) T=1 の w  厳密", w_exact_gradient_flow())
    for lib in LIBS:
        print(
            f"    {lib:6s} w座標GD {descent_end_w(lib, 'w'):.6f}  φ座標GD {descent_end_w(lib, 'phi'):.6f}"
            f"  φ座標の自然勾配 {descent_end_w(lib, 'phi_natural'):.6f}"
        )
    z0 = 1.0 + 2.0j
    print("(d) f=|z|², z=1+2i  2z =", 2 * z0, " 2conj(z) =", 2 * np.conj(z0))
    for lib in LIBS:
        print(f"    {lib:6s}", complex_grad_abs2(lib, z0))


if __name__ == "__main__":
    main()
