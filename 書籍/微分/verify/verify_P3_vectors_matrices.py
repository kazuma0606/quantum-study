"""「準備3 ベクトルと行列」（P3_ベクトルと行列.md）に出てくる式と数値の検算。

実行: uv run --no-sync python 書籍/微分/verify/verify_P3_vectors_matrices.py
"""

import sys

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
results = []


def check(name, cond):
    assert cond, name
    results.append(name)


# §1 ベクトルの足し算・定数倍・長さ・内積
a = sp.Matrix([3, 1])
b = sp.Matrix([1, 2])
check("(3,1) + (1,2) = (4,3)", a + b == sp.Matrix([4, 3]))
check("2·(3,1) = (6,2)", 2 * a == sp.Matrix([6, 2]))
check("(3,4) の長さは 5", sp.sqrt(3**2 + 4**2) == 5)
check("(3,1)·(1,2) = 5", a.dot(b) == 5)
check("-1·(3,1) = (-3,-1)（逆向き）", -1 * a == sp.Matrix([-3, -1]))
# (1,0),(0,1),(1,1) はすべてのベクトルを作れるが、組み立て方が一通りでない：(1,1) = 1·(1,1) = (1,0)+(0,1)
check("(1,1) は 1·(1,1) とも (1,0)+(0,1) とも書ける", sp.Matrix([1, 0]) + sp.Matrix([0, 1]) == sp.Matrix([1, 1]))
check("e1, e2 を並べた行列の零空間は {0}（組み立て方は一通り）", sp.Matrix.hstack(e1 := sp.Matrix([1, 0]), sp.Matrix([0, 1])).nullspace() == [])
check("(1,0),(0,1),(1,1) を並べた行列の零空間は 0 でない（組み立て方が一通りでない）",
      len(sp.Matrix([[1, 0, 1], [0, 1, 1]]).nullspace()) == 1)
check("(1,2)·(-2,1) = 0（直交）", sp.Matrix([1, 2]).dot(sp.Matrix([-2, 1])) == 0)
# a·b = |a||b|cosθ：(1,0) と (1,1) のなす角は 45°
u, v = sp.Matrix([1, 0]), sp.Matrix([1, 1])
check("(1,0) と (1,1) のなす角は 45°", sp.acos(u.dot(v) / (u.norm() * v.norm())) == sp.pi / 4)
check("a·a = |a|²", a.dot(a) == a.norm() ** 2)
# 余弦定理からの内積の式：|a-b|² = |a|² + |b|² - 2 a·b
check("|a-b|² = |a|² + |b|² - 2 a·b", (a - b).dot(a - b) == a.dot(a) + b.dot(b) - 2 * a.dot(b))

# §2 線形写像
x1, x2, y1, y2, c = sp.symbols("x1 x2 y1 y2 c", real=True)
X, Y = sp.Matrix([x1, x2]), sp.Matrix([y1, y2])
A = sp.Matrix([[2, 1], [0, 1]])
check("行列の写像は足し算を保つ", sp.simplify(A * (X + Y) - (A * X + A * Y)) == sp.zeros(2, 1))
check("行列の写像は定数倍を保つ", sp.simplify(A * (c * X) - c * (A * X)) == sp.zeros(2, 1))
check("x ↦ x+1 は 0 を 1 に写すので線形でない", (lambda t: t + 1)(0) == 1)
check("x ↦ x² は (1+1)² = 4 ≠ 1² + 1² = 2", (1 + 1) ** 2 == 4 and 1**2 + 1**2 == 2)

# §3 行列：列は基底の行き先
e1, e2 = sp.Matrix([1, 0]), sp.Matrix([0, 1])
M = sp.Matrix([[2, 1], [1, 3]])
check("M e1 は M の第1列", M * e1 == M[:, 0])
check("M e2 は M の第2列", M * e2 == M[:, 1])
check("M (x1, x2) = x1·(第1列) + x2·(第2列)", sp.simplify(M * X - (x1 * M[:, 0] + x2 * M[:, 1])) == sp.zeros(2, 1))
check("(2 1; 1 3)(1, 2) = (4, 7)", M * sp.Matrix([1, 2]) == sp.Matrix([4, 7]))
th, al, be = sp.symbols("theta alpha beta", real=True)


def rot(t):
    return sp.Matrix([[sp.cos(t), -sp.sin(t)], [sp.sin(t), sp.cos(t)]])


check("回転 R(θ) は e1 を (cos θ, sin θ) に写す", rot(th) * e1 == sp.Matrix([sp.cos(th), sp.sin(th)]))
check("回転 R(θ) は e2 を (-sin θ, cos θ) に写す", rot(th) * e2 == sp.Matrix([-sp.sin(th), sp.cos(th)]))
check("90° の回転は (1, 0) を (0, 1) に", rot(sp.pi / 2) * e1 == e2)
check("回転は長さを変えない", sp.simplify((rot(th) * X).norm() ** 2 - X.norm() ** 2) == 0)
S = sp.Matrix([[1, 1], [0, 1]])
check("せん断 (1 1; 0 1) は (0,1) を (1,1) に写す", S * e2 == sp.Matrix([1, 1]))
check("拡大 diag(2, 1/2) は (1,1) を (2, 1/2) に", sp.diag(2, sp.Rational(1, 2)) * sp.Matrix([1, 1]) == sp.Matrix([2, sp.Rational(1, 2)]))

# §4 合成は行列の積、順番で結果が変わる
Rq = rot(sp.pi / 2)
check("せん断のあと90°回転 = (0 -1; 1 1)", Rq * S == sp.Matrix([[0, -1], [1, 1]]))
check("90°回転のあとせん断 = (1 -1; 1 0)", S * Rq == sp.Matrix([[1, -1], [1, 0]]))
check("2つの順番で結果が違う", Rq * S != S * Rq)
check("(BA)x = B(Ax)（具体例）", (Rq * S) * sp.Matrix([1, 2]) == Rq * (S * sp.Matrix([1, 2])))
check("せん断のあと回転で (1,2) は (-2,3) に", (Rq * S) * sp.Matrix([1, 2]) == sp.Matrix([-2, 3]))
check("回転のあとせん断で (1,2) は (-1,1) に", (S * Rq) * sp.Matrix([1, 2]) == sp.Matrix([-1, 1]))
B2 = sp.Matrix(2, 2, sp.symbols("b11 b12 b21 b22"))
A2 = sp.Matrix(2, 2, sp.symbols("a11 a12 a21 a22"))
pp, qq, uu, ww, aa, bb, cc, dd = sp.symbols("p q u w a b c d")
check("積の公式 (p q; u w)(a b; c d) = (pa+qc pb+qd; ua+wc ub+wd)",
      sp.Matrix([[pp, qq], [uu, ww]]) * sp.Matrix([[aa, bb], [cc, dd]])
      == sp.Matrix([[pp * aa + qq * cc, pp * bb + qq * dd], [uu * aa + ww * cc, uu * bb + ww * dd]]))
check("一般の 2×2 で (BA)x = B(Ax)", sp.simplify((B2 * A2) * X - B2 * (A2 * X)) == sp.zeros(2, 1))

# §5 行列式＝面積の倍率
check("det(a b; c d) = ad - bc", sp.Matrix([[sp.Symbol("a"), sp.Symbol("b")], [sp.Symbol("c"), sp.Symbol("d")]]).det()
      == sp.Symbol("a") * sp.Symbol("d") - sp.Symbol("b") * sp.Symbol("c"))
check("det(2 1; 1 3) = 5", M.det() == 5)
check("回転の行列式は 1", sp.simplify(rot(th).det()) == 1)
check("せん断の行列式は 1", S.det() == 1)
check("diag(2, 1/2) の行列式は 1", sp.diag(2, sp.Rational(1, 2)).det() == 1)
check("diag(2, 3) の行列式は 6", sp.diag(2, 3).det() == 6)
check("(1 2; 2 4) の行列式は 0", sp.Matrix([[1, 2], [2, 4]]).det() == 0)
check("(1 2; 2 4) は (2,-1) を 0 に写す", sp.Matrix([[1, 2], [2, 4]]) * sp.Matrix([2, -1]) == sp.zeros(2, 1))
check("(1 2; 2 4) の行き先は (1,2) の方向だけ", sp.simplify(sp.Matrix([[1, 2], [2, 4]]) * X - (x1 + 2 * x2) * sp.Matrix([1, 2])) == sp.zeros(2, 1))
check("左右を入れ替える (0 1; 1 0) の行列式は -1", sp.Matrix([[0, 1], [1, 0]]).det() == -1)
check("det(BA) = det B · det A", sp.expand((B2 * A2).det() - B2.det() * A2.det()) == 0)
# 単位正方形の像の平行四辺形の面積 = |det|（2つの列ベクトルの張る平行四辺形）
p, q = M[:, 0], M[:, 1]
check("列 (2,1)、(1,3) の張る平行四辺形の面積は 5", abs(p[0] * q[1] - p[1] * q[0]) == 5)
# 逆行列
check("(2 1; 1 3) の逆行列は (3 -1; -1 2)/5", M.inv() == sp.Matrix([[3, -1], [-1, 2]]) / 5)
check("M M^{-1} = I", M * M.inv() == sp.eye(2))

# §6 特に重要：極座標の Jacobian
r = sp.symbols("r", positive=True)
F = sp.Matrix([r * sp.cos(th), r * sp.sin(th)])
J = F.jacobian([r, th])
check("極座標の Jacobian = (cos θ, -r sin θ; sin θ, r cos θ)",
      J == sp.Matrix([[sp.cos(th), -r * sp.sin(th)], [sp.sin(th), r * sp.cos(th)]]))
check("det J = r", sp.simplify(J.det()) == r)
# r=2、θ=π/6 で、(dr, dθ) = (0.01, 0.02) の小さな変化：Jacobian による近似と実際の変化
r0, t0 = 2, sp.pi / 6
dr, dt = sp.Rational(1, 100), sp.Rational(2, 100)
approx = J.subs({r: r0, th: t0}) * sp.Matrix([dr, dt])
exact = F.subs({r: r0 + dr, th: t0 + dt}) - F.subs({r: r0, th: t0})
check("近似の変化 ≈ (-0.0113, 0.0396)",
      abs(float(approx[0]) + 0.01134) < 1e-4 and abs(float(approx[1]) - 0.03964) < 1e-4)
check("実際の変化との差は 0.001 未満（変化の大きさの約 1%）", float((exact - approx).norm()) < 1e-3)
# 小さな変化を半分にすると、近似のずれは約 1/4
dr2, dt2 = dr / 2, dt / 2
approx2 = J.subs({r: r0, th: t0}) * sp.Matrix([dr2, dt2])
exact2 = F.subs({r: r0 + dr2, th: t0 + dt2}) - F.subs({r: r0, th: t0})
ratio = float((exact2 - approx2).norm() / (exact - approx).norm())
check("変化を半分にすると、近似のずれは約 1/4", 0.24 < ratio < 0.26)
check("θ を止めて r だけ動かす：(cos θ, sin θ) 方向に dr", J[:, 0] == sp.Matrix([sp.cos(th), sp.sin(th)]))
check("r を止めて θ だけ動かす：(-r sin θ, r cos θ) 方向", J[:, 1] == sp.Matrix([-r * sp.sin(th), r * sp.cos(th)]))
check("その長さは r", sp.simplify(J[:, 1].norm() - r) == 0)
check("2つの列は直交", sp.simplify(J[:, 0].dot(J[:, 1])) == 0)
# 小さな長方形の面積 dr·dθ は、写すと約 r·dr·dθ（r=2 なら約 2 倍）
check("r=2 では面積の倍率 det J は 2", J.det().subs({r: 2, th: t0}).simplify() == 2)
# 球座標の Jacobian：行列式は r² sinθ（はじめにの √|g| と同じ）
ph = sp.symbols("phi", real=True)
th_s = sp.symbols("theta_s", positive=True)  # 0 < θ < π を想定（sinθ > 0）
Fs = sp.Matrix([r * sp.sin(th_s) * sp.cos(ph), r * sp.sin(th_s) * sp.sin(ph), r * sp.cos(th_s)])
Js = Fs.jacobian([r, th_s, ph])
check("球座標の Jacobian の行列式は r² sinθ", sp.simplify(Js.det() - r**2 * sp.sin(th_s)) == 0)
g_s = sp.simplify(Js.T * Js)
check("計量 g = JᵀJ = diag(1, r², r² sin²θ)", g_s == sp.diag(1, r**2, r**2 * sp.sin(th_s) ** 2))
check("det g = (det J)²", sp.simplify(g_s.det() - Js.det() ** 2) == 0)
# 計量の成分は、J の列（基底のベクトル）どうしの内積
check("g の (2,2) 成分 = J の第2列どうしの内積 = r²", sp.simplify(Js[:, 1].dot(Js[:, 1]) - r**2) == 0)

# コラム：回転を2回 → 加法定理
check("R(α)R(β) = R(α+β) の (1,1) 成分：cos α cos β - sin α sin β = cos(α+β)",
      sp.simplify((rot(al) * rot(be))[0, 0] - sp.cos(al + be)) == 0)
check("R(α)R(β) = R(α+β) の (2,1) 成分：sin α cos β + cos α sin β = sin(α+β)",
      sp.simplify((rot(al) * rot(be))[1, 0] - sp.sin(al + be)) == 0)
check("R(α)R(β) = R(β)R(α)（回転どうしは順番によらない）", sp.simplify(rot(al) * rot(be) - rot(be) * rot(al)) == sp.zeros(2, 2))
check("R(α)R(β) の成分の積の展開", sp.expand((rot(al) * rot(be))[0, 0]) == sp.cos(al) * sp.cos(be) - sp.sin(al) * sp.sin(be))

# コラム：サラスの公式
sa, sb, sc_, sd, se, sf, sg, sh, si = sp.symbols("a b c d e f g h i")
M3 = sp.Matrix([[sa, sb, sc_], [sd, se, sf], [sg, sh, si]])
check("サラスの公式 = 3×3 の行列式",
      sp.expand(M3.det() - (sa * se * si + sb * sf * sg + sc_ * sd * sh - sc_ * se * sg - sb * sd * si - sa * sf * sh)) == 0)
# 4×4 で同じ「斜め」の方法を使うと、行列式にならない例（単位行列でない置換の行列）
P4 = sp.Matrix([[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]])


def sarus_like(Mx):
    n_ = Mx.shape[0]
    down = sum(sp.prod([Mx[k, (j + k) % n_] for k in range(n_)]) for j in range(n_))
    up = sum(sp.prod([Mx[k, (j - k) % n_] for k in range(n_)]) for j in range(n_))
    return down - up


check("4×4 では斜めの方法は行列式と一致しない（例：巡回置換の行列）", sarus_like(P4) != P4.det())
check("3×3 では斜めの方法が行列式と一致", sp.expand(sarus_like(M3) - M3.det()) == 0)
# 球座標の Jacobian の6つの項
a_, b_, c_ = Js[0, 0], Js[0, 1], Js[0, 2]
d_, e_, f_ = Js[1, 0], Js[1, 1], Js[1, 2]
g_, h_, i_ = Js[2, 0], Js[2, 1], Js[2, 2]
check("i = 0", i_ == 0)
check("bfg = r² sinθ cos²θ cos²φ", sp.simplify(b_ * f_ * g_ - r**2 * sp.sin(th_s) * sp.cos(th_s) ** 2 * sp.cos(ph) ** 2) == 0)
check("cdh = r² sin³θ sin²φ", sp.simplify(c_ * d_ * h_ - r**2 * sp.sin(th_s) ** 3 * sp.sin(ph) ** 2) == 0)
check("ceg = -r² sinθ cos²θ sin²φ", sp.simplify(c_ * e_ * g_ + r**2 * sp.sin(th_s) * sp.cos(th_s) ** 2 * sp.sin(ph) ** 2) == 0)
check("afh = -r² sin³θ cos²φ", sp.simplify(a_ * f_ * h_ + r**2 * sp.sin(th_s) ** 3 * sp.cos(ph) ** 2) == 0)
check("サラスの公式で det J = r² sinθ",
      sp.simplify(a_ * e_ * i_ + b_ * f_ * g_ + c_ * d_ * h_ - c_ * e_ * g_ - b_ * d_ * i_ - a_ * f_ * h_ - r**2 * sp.sin(th_s)) == 0)
check("単位立方体の像の体積 = |det|（diag(2,3,4) で 24）", sp.diag(2, 3, 4).det() == 24)

print(f"すべて一致：{len(results)} 件")
