"""「はじめに」に出てくる式の検算。

1. 球座標 (r, θ, φ) の計量は g = diag(1, r², r² sin²θ) で、√|g| = r² sinθ。
2. ラプラス・ベルトラミの公式 Δf = (1/√|g|) ∂_i(√|g| g^{ij} ∂_j f) に 1. を入れると、
   球座標のラプラシアン
       Δf = (1/r²)∂_r(r² ∂_r f) + (1/(r² sinθ))∂_θ(sinθ ∂_θ f) + (1/(r² sin²θ))∂_φ² f
   になる。
3. 2. の式は、直交座標のラプラシアン f_xx + f_yy + f_zz と一致する（具体的な関数で確かめる）。

実行: uv run --no-sync python 書籍/微分/verify/verify_00_introduction.py
"""

import sys

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")

r, th, ph = sp.symbols("r theta phi", positive=True)
x = r * sp.sin(th) * sp.cos(ph)
y = r * sp.sin(th) * sp.sin(ph)
z = r * sp.cos(th)
q = [r, th, ph]

# 1. 計量 g = J^T J
J = sp.Matrix([x, y, z]).jacobian(q)
g = sp.simplify(J.T * J)
assert g == sp.diag(1, r**2, r**2 * sp.sin(th) ** 2), g
sqrt_g = sp.sqrt(sp.factor(g.det()))
sqrt_g = sp.simplify(sqrt_g.subs(sp.sqrt(sp.sin(th) ** 2), sp.sin(th)))
assert sp.simplify(sqrt_g - r**2 * sp.sin(th)) == 0, sqrt_g
ginv = g.inv()

# 2. ラプラス・ベルトラミの公式と、球座標のラプラシアンの式
f = sp.Function("f")(r, th, ph)
lb = sum(
    sp.diff(sqrt_g * sum(ginv[i, j] * sp.diff(f, q[j]) for j in range(3)), q[i])
    for i in range(3)
) / sqrt_g
spherical = (
    sp.diff(r**2 * sp.diff(f, r), r) / r**2
    + sp.diff(sp.sin(th) * sp.diff(f, th), th) / (r**2 * sp.sin(th))
    + sp.diff(f, ph, 2) / (r**2 * sp.sin(th) ** 2)
)
assert sp.simplify(lb - spherical) == 0

# 3. 直交座標のラプラシアンとの一致（具体的な関数で）
X, Y, Z = sp.symbols("X Y Z", real=True)
tests = [X**2 * Y + Z**3, sp.exp(X) * sp.sin(Y) * Z, X * Y * Z / (1 + X**2 + Y**2 + Z**2)]
for F in tests:
    cart = sp.diff(F, X, 2) + sp.diff(F, Y, 2) + sp.diff(F, Z, 2)
    Fs = F.subs({X: x, Y: y, Z: z})
    lap_s = (
        sp.diff(r**2 * sp.diff(Fs, r), r) / r**2
        + sp.diff(sp.sin(th) * sp.diff(Fs, th), th) / (r**2 * sp.sin(th))
        + sp.diff(Fs, ph, 2) / (r**2 * sp.sin(th) ** 2)
    )
    assert sp.simplify(lap_s - cart.subs({X: x, Y: y, Z: z})) == 0, F

print("すべて一致：計量、√|g|、ラプラス・ベルトラミ → 球座標のラプラシアン、直交座標との一致（3関数）")
