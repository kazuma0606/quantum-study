"""ノート2（受理確率は多項式になる）の式と数値例の検算。

対象のノート：研究ノート/09_論文読解/aaronson_ambainis/02_acceptance_probability_polynomial.md

一般の式は、N=1..3、作業レジスタの次元 W=1,2、クエリの回数 T=0..3 で、
乱数のユニタリ行列と初期状態を作り、すべての入力 X で確かめる。
多項式は、単項式の指数の組 → 係数（複素数）の辞書で表し、ノートの式（クエリの式と、
ユニタリ行列を掛ける式）だけで振幅の多項式を作る。それを {0,1}^N の点で評価した値を、
行列の積で直接求めた振幅と比べる。
数値例は、本文に書いた値と照らす（分数で書ける値は Fraction、√2 を含む値は sympy）。
検査ごとに「一致」「不一致」を表示し、不一致が1件でもあれば、終了コード 1 で終わる。

実行（リポジトリのルートから）:
    uv run python experiments/aaronson_ambainis/verify_note2.py
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F

import numpy as np
import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")  # Windows の既定の文字コードでは表示できない記号があるため
rng = np.random.default_rng(20261111)
TOL = 1e-10

ok = []


def check(name, cond):
    ok.append((name, bool(cond)))
    print(("一致  " if cond else "不一致 ") + name)


# ---------- 多項式（指数の組 → 係数） ----------
def padd(p, q, a=1, b=1):
    out = {}
    for m, c in p.items():
        out[m] = out.get(m, 0) + a * c
    for m, c in q.items():
        out[m] = out.get(m, 0) + b * c
    return {m: c for m, c in out.items() if abs(c) > TOL}


def pmul(p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + b for a, b in zip(m1, m2))
            out[m] = out.get(m, 0) + c1 * c2
    return {m: c for m, c in out.items() if abs(c) > TOL}


def pscale(p, a):
    return {m: a * c for m, c in p.items() if abs(a * c) > TOL}


def pconst(c, N):
    return {(0,) * N: c} if abs(c) > TOL else {}


def pvar(i, N):  # X_i（i は 1 から）
    return {tuple(1 if j == i - 1 else 0 for j in range(N)): 1.0}


def deg(p):
    return max((sum(m) for m in p), default=-1)  # 零の多項式は -1（どの d でも「d 以下」）


def peval(p, X):
    return sum(c * np.prod([x ** e for x, e in zip(X, m)]) for m, c in p.items())


def multilinear(p):
    out = {}
    for m, c in p.items():
        mm = tuple(min(e, 1) for e in m)
        out[mm] = out.get(mm, 0) + c
    return {m: c for m, c in out.items() if abs(c) > TOL}


def random_unitary(d):
    z = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / np.abs(np.diag(r)))


# ---------- 模型 ----------
def labels(N, W):  # (i,b,z) を i, b, z の順に並べる
    return [(i, b, z) for i in range(1, N + 1) for b in (0, 1) for z in range(1, W + 1)]


def oracle(X, N, W):
    L = labels(N, W)
    idx = {k: n for n, k in enumerate(L)}
    O = np.zeros((len(L), len(L)))
    for (i, b, z) in L:
        O[idx[(i, b ^ X[i - 1], z)], idx[(i, b, z)]] = 1
    return O


def query_on_polys(a, N, W):
    """ノートの式（クエリの式）で、振幅の多項式を更新する。"""
    L = labels(N, W)
    idx = {k: n for n, k in enumerate(L)}
    out = [None] * len(L)
    for i in range(1, N + 1):
        Xi = pvar(i, N)
        one_minus = padd(pconst(1.0, N), Xi, 1, -1)
        for z in range(1, W + 1):
            a0, a1 = a[idx[(i, 0, z)]], a[idx[(i, 1, z)]]
            out[idx[(i, 0, z)]] = padd(pmul(one_minus, a0), pmul(Xi, a1))
            out[idx[(i, 1, z)]] = padd(pmul(Xi, a0), pmul(one_minus, a1))
    return out


def unitary_on_polys(U, a):
    """ユニタリ行列を掛ける式：a'_k = Σ_l U_{kl} a_l。"""
    out = []
    for k in range(U.shape[0]):
        acc = {}
        for l in range(U.shape[1]):
            acc = padd(acc, pscale(a[l], U[k, l]))
        out.append(acc)
    return out


# ---------- 一般の式 ----------
# XOR の性質
check("II: (b⊕c)⊕c=b（b,c∈{0,1}）", all((b ^ c) ^ c == b for b in (0, 1) for c in (0, 1)))
check("II: b↦b⊕c は {0,1} の全単射", all(sorted(b ^ c for b in (0, 1)) == [0, 1] for c in (0, 1)))

for N in (1, 2, 3):
    for W in (1, 2):
        D = 2 * N * W
        Xs = list(itertools.product((0, 1), repeat=N))
        # O_X は置換行列で、ユニタリ、O_X^2=I
        c_unit = all(np.allclose(oracle(X, N, W).T @ oracle(X, N, W), np.eye(D)) for X in Xs)
        c_inv = all(np.allclose(oracle(X, N, W) @ oracle(X, N, W), np.eye(D)) for X in Xs)
        check(f"II: N={N},W={W}: O_X はユニタリで O_X^2=I", c_unit and c_inv)
        # クエリの式（β の式）を、乱数の α で、すべての X で
        L = labels(N, W)
        idx = {k: n for n, k in enumerate(L)}
        good = True
        for _ in range(5):
            alpha = rng.normal(size=D) + 1j * rng.normal(size=D)
            for X in Xs:
                beta = oracle(X, N, W) @ alpha
                for (i, b, z) in L:
                    a0, a1 = alpha[idx[(i, 0, z)]], alpha[idx[(i, 1, z)]]
                    xi = X[i - 1]
                    want = (1 - xi) * a0 + xi * a1 if b == 0 else xi * a0 + (1 - xi) * a1
                    good &= abs(beta[idx[(i, b, z)]] - want) < TOL
                    good &= abs(beta[idx[(i, b, z)]] - alpha[idx[(i, b ^ xi, z)]]) < TOL
        check(f"III: N={N},W={W}: クエリの式（係数は α_(i,b⊕X_i,z)、(1-X_i),X_i の形）", good)
        # ノルムを保つ
        normok = all(
            abs(np.linalg.norm(oracle(X, N, W) @ v) - np.linalg.norm(v)) < TOL
            for X in Xs
            for v in [rng.normal(size=D) + 1j * rng.normal(size=D) for _ in range(3)]
        )
        check(f"IV: N={N},W={W}: O_X はノルムを保つ", normok)

        for T in range(0, 4):
            for trial in range(3):
                Us = [random_unitary(D) for _ in range(T + 1)]
                s = rng.normal(size=D) + 1j * rng.normal(size=D)
                s /= np.linalg.norm(s)
                B = [k for k in range(D) if rng.random() < 0.5]
                # 多項式で
                a = [pconst(c, N) for c in Us[0] @ s]
                degs_ok = all(deg(p) <= 0 for p in a)
                for t in range(1, T + 1):
                    a = unitary_on_polys(Us[t], query_on_polys(a, N, W))
                    degs_ok &= all(deg(p) <= t for p in a)
                # 直接
                vals_ok, prob_ok, range_ok, ml_ok, real_ok = True, True, True, True, True
                prob = {}
                for k in B:
                    r = {m: c.real for m, c in a[k].items() if abs(c.real) > TOL}
                    si = {m: c.imag for m, c in a[k].items() if abs(c.imag) > TOL}
                    prob = padd(prob, padd(pmul(r, r), pmul(si, si)))
                    real_ok &= deg(r) <= T and deg(si) <= T
                pdeg_ok = deg(prob) <= 2 * T and all(isinstance(c, float) for c in prob.values())
                ml = multilinear(prob)
                ml_ok = deg(ml) <= 2 * T and all(max(m, default=0) <= 1 for m in ml)
                for X in Xs:
                    psi = Us[0] @ s
                    for t in range(1, T + 1):
                        psi = Us[t] @ (oracle(X, N, W) @ psi)
                    vals_ok &= all(abs(peval(a[k], X) - psi[k]) < 1e-8 for k in range(D))
                    pdirect = sum(abs(psi[k]) ** 2 for k in B)
                    prob_ok &= abs(peval(prob, X) - pdirect) < 1e-8 and abs(peval(ml, X) - pdirect) < 1e-8
                    range_ok &= -1e-12 <= pdirect <= 1 + 1e-12 and abs(np.linalg.norm(psi) - 1) < 1e-10
                check(
                    f"III/IV/V: N={N},W={W},T={T},#{trial}: 振幅は次数≤t、値が一致、r,s の次数≤T、"
                    f"受理確率は実係数で次数≤2T、多重線形にしても値と次数≤2T、値は[0,1]",
                    degs_ok and vals_ok and real_ok and pdeg_ok and prob_ok and ml_ok and range_ok,
                )

# 次数の性質：積、一次結合（乱数の多項式）
good = True
for _ in range(200):
    N = 3
    def rp(dmax):
        p = {}
        for m in itertools.product(range(dmax + 1), repeat=N):
            if sum(m) <= dmax and rng.random() < 0.5:
                p[m] = complex(rng.integers(-3, 4), rng.integers(-3, 4))
        return {m: c for m, c in p.items() if abs(c) > TOL}
    d1, d2 = rng.integers(0, 3), rng.integers(0, 3)
    p, q = rp(d1), rp(d2)
    good &= deg(pmul(p, q)) <= d1 + d2
    good &= deg(padd(p, q, complex(1, 2), -3)) <= max(d1, d2)
    good &= deg(pmul(pvar(2, N), p)) <= d1 + 1
    good &= deg(multilinear(p)) <= max(deg(p), -1)
    for X in itertools.product((0, 1), repeat=N):
        good &= abs(peval(multilinear(p), X) - peval(p, X)) < 1e-9
check("III/V: 積の次数 ≤ 和、一次結合の次数 ≤ 大きい方、X_i を掛けると +1 以下、多重線形化で値と次数", good)

# ---------- 数値例 ----------
X1, X2 = sp.symbols("X1 X2")
I = sp.I
r2 = sp.sqrt(2)

# Part III §1 の例：q=(1+i)X1+2
q = (1 + I) * X1 + 2
check("III: X2 q = (1+i)X1X2 + 2X2", sp.expand(X2 * q - ((1 + I) * X1 * X2 + 2 * X2)) == 0)
check("III: (1-X2) q = (1+i)X1 + 2 - (1+i)X1X2 - 2X2", sp.expand((1 - X2) * q - ((1 + I) * X1 + 2 - (1 + I) * X1 * X2 - 2 * X2)) == 0)
check("III: 次数 1, 2, 2", sp.Poly(q, X1, X2).total_degree() == 1 and sp.Poly(sp.expand(X2 * q), X1, X2).total_degree() == 2 and sp.Poly(sp.expand((1 - X2) * q), X1, X2).total_degree() == 2)

h = (1 + I) * X1 + X2
check("III: g-h = 2 - X2（X1 の係数が消える、次数 1）", sp.expand(q - h - (2 - X2)) == 0 and sp.Poly(sp.expand(q - h), X1, X2).total_degree() == 1)
# Part III §3 の例：H (1,2)
Hm = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
v12 = sp.Matrix([1, 2])
cols = 1 * Hm[:, 0] + 2 * Hm[:, 1]
check("III: (III-3) の例 列の和 = 行の和 = (3/√2, -1/√2)",
      all(sp.simplify(cols[n] - (Hm * v12)[n]) == 0 for n in range(2)) and sp.simplify(cols[0] - 3 / sp.sqrt(2)) == 0 and sp.simplify(cols[1] + 1 / sp.sqrt(2)) == 0)

# Part II の例：N=2, W=1, X=(0,1) の O_X
Lab = [(1, 0), (1, 1), (2, 0), (2, 1)]
Ox01 = oracle((0, 1), 2, 1)
check("II: X=(0,1) の O_X の行列", np.array_equal(Ox01, np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])))

# Part III/IV の例：1回のクエリで X1⊕X2 を求める回路
H = sp.Matrix([[1, 1], [1, -1]]) / r2
U0 = sp.kronecker_product(H, H)
U1 = sp.kronecker_product(H, sp.eye(2))
s = sp.Matrix([0, 1, 0, 0])  # |1,1⟩
check("II: U0 の行 (2,1)、列 (1,1)（4行2列）= H[2,1]·H[2,2] = -1/2", U0[3, 1] == -sp.Rational(1, 2) and sp.simplify(H[1, 0] * H[1, 1] + sp.Rational(1, 2)) == 0)
check("II: U0, U1 の成分（本文の行列）",
      sp.simplify(U0 - sp.Matrix([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]) / 2) == sp.zeros(4, 4)
      and sp.simplify(U1 - sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, -1, 0], [0, 1, 0, -1]]) / r2) == sp.zeros(4, 4))
psi0 = U0 * s
check("III: ψ_0 の振幅 = (1/2, -1/2, 1/2, -1/2)", list(psi0) == [sp.Rational(1, 2), -sp.Rational(1, 2), sp.Rational(1, 2), -sp.Rational(1, 2)])
al = {lab: psi0[n] for n, lab in enumerate(Lab)}
Xv = {1: X1, 2: X2}
beta = {}
for i in (1, 2):
    beta[(i, 0)] = sp.expand((1 - Xv[i]) * al[(i, 0)] + Xv[i] * al[(i, 1)])
    beta[(i, 1)] = sp.expand(Xv[i] * al[(i, 0)] + (1 - Xv[i]) * al[(i, 1)])
check("III: クエリの後 β_(i,0)=(1-2X_i)/2, β_(i,1)=-(1-2X_i)/2",
      all(sp.simplify(beta[(i, 0)] - (1 - 2 * Xv[i]) / 2) == 0 and sp.simplify(beta[(i, 1)] + (1 - 2 * Xv[i]) / 2) == 0 for i in (1, 2)))
bvec = sp.Matrix([beta[lab] for lab in Lab])
gam = sp.expand(U1 * bvec)
want = [(1 - X1 - X2) / r2, -(1 - X1 - X2) / r2, (X2 - X1) / r2, -(X2 - X1) / r2]
check("III: 最後の振幅 γ = ((1-X1-X2)/√2, -(1-X1-X2)/√2, (X2-X1)/√2, -(X2-X1)/√2)",
      all(sp.simplify(gam[n] - want[n]) == 0 for n in range(4)))
# 次数
check("III: γ の次数はどれも 1 以下", all(sp.Poly(g, X1, X2).total_degree() <= 1 for g in gam))
# 直接の計算と一致
good = True
for X in itertools.product((0, 1), repeat=2):
    O = sp.Matrix(oracle(X, 2, 1).astype(int))
    direct = U1 * O * U0 * s
    good &= all(sp.simplify(direct[n] - gam[n].subs({X1: X[0], X2: X[1]})) == 0 for n in range(4))
check("III: 4つの X で、振幅の多項式の値 = 行列の積で求めた振幅", good)
# 受理確率
p = sp.expand(gam[2] ** 2 + gam[3] ** 2)
check("IV: 受理確率 = (X1-X2)^2 = X1^2 - 2X1X2 + X2^2", sp.expand(p - (X1 - X2) ** 2) == 0 and sp.expand(p - (X1**2 - 2 * X1 * X2 + X2**2)) == 0)
check("IV: q=(X1-X2)^2 は X=(2,0) で 4（{0,1}^2 の外では [0,1] に入らない）", p.subs({X1: 2, X2: 0}) == 4)
check("IV: 受理確率の値 0,1,1,0", [p.subs({X1: a, X2: b}) for a, b in itertools.product((0, 1), repeat=2)] == [0, 1, 1, 0])
check("IV: 受理しない確率 = (1-X1-X2)^2 で値 1,0,0,1", [sp.expand(gam[0] ** 2 + gam[1] ** 2).subs({X1: a, X2: b}) for a, b in itertools.product((0, 1), repeat=2)] == [1, 0, 0, 1])
check("IV: |γ_(2,0)|^2 = (X1-X2)^2/2", sp.expand(gam[2] ** 2 - (X1 - X2) ** 2 / 2) == 0)
pml = X1 + X2 - 2 * X1 * X2
check("V: 多重線形にすると X1 + X2 - 2X1X2（値も同じ）", all(pml.subs({X1: a, X2: b}) == p.subs({X1: a, X2: b}) for a, b in itertools.product((0, 1), repeat=2)))
check("V: 次数 2 = 2T", sp.Poly(pml, X1, X2).total_degree() == 2)
check("V: X1⊕X2 と一致", all(pml.subs({X1: a, X2: b}) == (a ^ b) for a, b in itertools.product((0, 1), repeat=2)))
check("V: Inf_1 = Inf_2 = 1, Var = 1/4（ノート1 の定義で）",
      all(sum(F(int((pml.subs({X1: X[0], X2: X[1]}) - pml.subs({X1: Y[0], X2: Y[1]})) ** 2)) for X in itertools.product((0, 1), repeat=2) for Y in [tuple(1 - X[j - 1] if j == i else X[j - 1] for j in (1, 2))]) / 4 == 1 for i in (1, 2))
      and sum((F(int(pml.subs({X1: a, X2: b}))) - F(1, 2)) ** 2 for a, b in itertools.product((0, 1), repeat=2)) / 4 == F(1, 4))

# Part IV §1 の例：a=(X1+iX2)/√2
a = (X1 + I * X2) / r2
r, si = X1 / r2, X2 / r2
check("IV: a = r + i s（r=X1/√2, s=X2/√2）", sp.simplify(a - (r + I * si)) == 0)
check("IV: r^2+s^2 = (X1^2+X2^2)/2", sp.expand(r**2 + si**2 - (X1**2 + X2**2) / 2) == 0)
check("IV: 4つの点で |a|^2 = r^2+s^2 = 0, 1/2, 1/2, 1",
      [sp.simplify(sp.Abs(a.subs({X1: u, X2: v})) ** 2) for u, v in itertools.product((0, 1), repeat=2)] == [0, sp.Rational(1, 2), sp.Rational(1, 2), 1]
      and [(r**2 + si**2).subs({X1: u, X2: v}) for u, v in itertools.product((0, 1), repeat=2)] == [0, sp.Rational(1, 2), sp.Rational(1, 2), 1])
check("IV: a*a（共役を取らない積）= (X1^2 - X2^2 + 2i X1X2)/2 は実数でない", sp.expand(a * a - (X1**2 - X2**2 + 2 * I * X1 * X2) / 2) == 0)

bad = [n for n, v in ok if not v]
print(f"\n合計 {len(ok)} 件、不一致 {len(bad)} 件")
for n in bad:
    print("  不一致:", n)
sys.exit(1 if bad else 0)
