"""ノート1（離散立方体上の関数と多項式）の式と数値例の検算。

対象のノート：研究ノート/09_論文読解/aaronson_ambainis/01_functions_on_discrete_cube.md

一般の式は、n=0..4 のすべての点と部分集合、乱数の関数で確かめる。
数値例は、分数（Fraction）で、本文に書いた値と照らす。
検査ごとに「一致」「不一致」を表示し、不一致が1件でもあれば、終了コード 1 で終わる。

実行（リポジトリのルートから）:
    uv run python experiments/aaronson_ambainis/verify_note1.py
"""
from __future__ import annotations

import itertools
import random
import sys
from fractions import Fraction as F

sys.stdout.reconfigure(encoding="utf-8")  # Windows の既定の文字コードでは表示できない記号があるため
random.seed(20261111)


def cube(n):
    return list(itertools.product([1, -1], repeat=n))


def subsets(n):
    idx = range(1, n + 1)
    return [frozenset(c) for r in range(n + 1) for c in itertools.combinations(idx, r)]


def flip(x, S):
    return tuple(-v if (i + 1) in S else v for i, v in enumerate(x))


def chi(T, x):
    out = 1
    for i in T:
        out *= x[i - 1]
    return out


def E(g, n):
    pts = cube(n)
    return sum(F(g(x)) for x in pts) / len(pts)


def Var(g, n):
    m = E(g, n)
    return E(lambda x: (F(g(x)) - m) ** 2, n)


ok = []


def check(name, cond):
    ok.append((name, bool(cond)))
    print(("一致  " if cond else "不一致 ") + name)


# ---------- 一般の式 ----------
for n in range(0, 5):
    pts, subs = cube(n), subsets(n)
    full = frozenset(range(1, n + 1))
    assert len(pts) == 2 ** n and len(subs) == 2 ** n
    # (II-2) (x^S)^T = x^{S△T}
    c1 = all(flip(flip(x, S), T) == flip(x, S ^ T) for x in pts for S in subs for T in subs)
    # (2.1)
    def Delta(x, z):
        return frozenset(i + 1 for i in range(n) if x[i] != z[i])
    def ag(x, z):
        return frozenset(i + 1 for i in range(n) if x[i] == z[i])
    c2 = all(flip(x, Delta(x, z)) == z and flip(flip(x, full), ag(x, z)) == z for x in pts for z in pts)
    c3 = all(Delta(x, flip(x, S)) == S and ag(flip(x, full), flip(x, S)) == S for x in pts for S in subs)
    c3b = all(flip(x, full) == tuple(-v for v in x) for x in pts)
    # 全単射と平均
    c4 = all(sorted(flip(x, S) for x in pts) == sorted(pts) for S in subs)
    g = {x: F(random.randint(-9, 9), random.randint(1, 5)) for x in pts}
    c5 = all(E(lambda x: g[flip(x, S)], n) == E(lambda x: g[x], n) for S in subs)
    # (III-2) χ_T χ_U = χ_{T△U}
    c6 = all(chi(T, x) * chi(U, x) == chi(T ^ U, x) for x in pts for T in subs for U in subs)
    # (III-3)(III-4)
    c7 = all(E(lambda x: chi(V, x), n) == (1 if not V else 0) for V in subs)
    c8 = all(E(lambda x: chi(T, x) * chi(U, x), n) == (1 if T == U else 0) for T in subs for U in subs)
    # (U2) Σ_T χ_T(w)
    c9 = all(sum(chi(T, w) for T in subs) == (2 ** n if all(v == 1 for v in w) else 0) for w in pts)
    # (III-5) 展開
    fh = {T: E(lambda x: g[x] * chi(T, x), n) for T in subs}
    c10 = all(sum(fh[T] * chi(T, x) for T in subs) == g[x] for x in pts)
    # (IV-4) (2.3)
    c = F(random.randint(-7, 7), 3)
    lhs = E(lambda x: (g[x] - c) ** 2, n)
    rhs = Var(lambda x: g[x], n) + (E(lambda x: g[x], n) - c) ** 2
    c11 = lhs == rhs and lhs >= Var(lambda x: g[x], n)
    # (IV-5) (2.4)
    c12 = True
    for j in range(1, n + 1):
        Sj = frozenset([j])
        Inf = E(lambda x: ((g[x] - g[flip(x, Sj)]) / 2) ** 2, n)
        L = E(lambda x: abs(g[x] - g[flip(x, Sj)]), n)
        c12 &= L ** 2 <= 4 * Inf
    # 次数：線形性と積
    h = {x: F(random.randint(-9, 9), random.randint(1, 5)) for x in pts}
    hh = {T: E(lambda x: h[x] * chi(T, x), n) for T in subs}
    a, b = F(3, 2), F(-5, 7)
    c13 = all(E(lambda x: (a * g[x] + b * h[x]) * chi(T, x), n) == a * fh[T] + b * hh[T] for T in subs)
    c14 = all(
        E(lambda x: g[x] * h[x] * chi(W, x), n) == sum(fh[T] * hh[U] for T in subs for U in subs if T ^ U == W)
        for W in subs
    )
    c15 = all(len(T ^ U) <= len(T) + len(U) for T in subs for U in subs)
    # Part V：X_i=(1-x_i)/2, f=2p-1
    p = {tuple((1 - v) // 2 for v in x): F(random.randint(0, 9), 9) for x in pts}
    Xs = list(itertools.product([0, 1], repeat=n))
    toX = lambda x: tuple((1 - v) // 2 for v in x)
    f = {x: 2 * p[toX(x)] - 1 for x in pts}
    c16 = sorted(toX(x) for x in pts) == sorted(Xs)
    flipX = lambda X, i: tuple(1 - v if k + 1 == i else v for k, v in enumerate(X))
    c17 = all(toX(flip(x, frozenset([i]))) == flipX(toX(x), i) for x in pts for i in range(1, n + 1))
    EX = lambda q: sum(F(q(X)) for X in Xs) / len(Xs)
    c18 = all(
        E(lambda x: ((f[x] - f[flip(x, frozenset([i]))]) / 2) ** 2, n) == EX(lambda X: (p[X] - p[flipX(X, i)]) ** 2)
        for i in range(1, n + 1)
    )
    mp = EX(lambda X: p[X])
    c19 = Var(lambda x: f[x], n) == 4 * EX(lambda X: (p[X] - mp) ** 2)
    c20 = all(-1 <= f[x] <= 1 for x in pts)
    # f(x)=x_j の影響力は 1（Part IV §1 の例）
    c21 = all(
        E(lambda x: (F(x[j - 1] - flip(x, frozenset([j]))[j - 1]) / 2) ** 2, n) == 1 for j in range(1, n + 1)
    )
    # 点 y でだけ 1 の関数の一次結合に、どの関数も書ける（係数は f(y)。Part III §4 の次元の説明）
    c22 = all(sum(g[y] * (1 if x == y else 0) for y in pts) == g[x] for x in pts)
    for k, v in enumerate([c1, c2, c3, c3b, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22], 1):
        check(f"n={n} 一般の式 c{k}", v)

# ---------- 数値例 ----------
# Part I：p = X1 X2
Xs = list(itertools.product([0, 1], repeat=2))
p = lambda X: X[0] * X[1]
EX = lambda q: sum(F(q(X)) for X in Xs) / 4
flipX = lambda X, i: tuple(1 - v if k + 1 == i else v for k, v in enumerate(X))
check("I: E[p]=1/4", EX(p) == F(1, 4))
check("I: Var[p]=3/16", EX(lambda X: (p(X) - F(1, 4)) ** 2) == F(3, 16))
check("I: (p-E p)^2 の値 1/16,1/16,1/16,9/16", [(p(X) - F(1, 4)) ** 2 for X in Xs] == [F(1, 16)] * 3 + [F(9, 16)])
check("I: p(X)-p(X^1) = 0,-1,0,1 (X=(0,0),(0,1),(1,0),(1,1))", [p(X) - p(flipX(X, 1)) for X in Xs] == [0, -1, 0, 1])
check("I: p(X)-p(X^2) = 0,0,-1,1", [p(X) - p(flipX(X, 2)) for X in Xs] == [0, 0, -1, 1])
check("I: Inf_1[p]=Inf_2[p]=1/2", all(EX(lambda X: (p(X) - p(flipX(X, i))) ** 2) == F(1, 2) for i in (1, 2)))
check("I: (3/32)^7 < 1/2", F(3, 32) ** 7 < F(1, 2))
print("   (3/32)^7 =", float(F(3, 32) ** 7))

# Part II の例（n=3）
x = (1, -1, 1)
S, T = frozenset({1, 3}), frozenset({1, 2})
check("II: x^S=(-1,-1,-1)", flip(x, S) == (-1, -1, -1))
check("II: x^2=(1,1,1)", flip(x, {2}) == (1, 1, 1))
check("II: xbar=(-1,1,-1)", flip(x, {1, 2, 3}) == (-1, 1, -1))
check("II: (x^S)^T=(1,1,-1)", flip(flip(x, S), T) == (1, 1, -1))
check("II: S△T={2,3}, x^{2,3}=(1,1,-1)", S ^ T == {2, 3} and flip(x, {2, 3}) == (1, 1, -1))
z = (-1, -1, 1)
check("II: Δ(x,z)={1}, ag={2,3}", [i + 1 for i in range(3) if x[i] != z[i]] == [1])
check("II: x^{1}=z, xbar^{2,3}=z", flip(x, {1}) == z and flip((-1, 1, -1), {2, 3}) == z)
check("II: ag(xbar,x^S)={1,3}", [i + 1 for i in range(3) if (-1, 1, -1)[i] == (-1, -1, -1)[i]] == [1, 3])
a = (1, 0, 2)
check("II: a(S)=3, ||a||_1=3", a[0] + a[2] == 3 and sum(abs(v) for v in a) == 3)
check("II: a=(1,-2): ||a||_1=3, a([2])=-1", abs(1) + abs(-2) == 3 and 1 - 2 == -1)

# 例の関数 f（n=2）
pts = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
fv = {(1, 1): -1, (1, -1): -1, (-1, 1): -1, (-1, -1): 1}
f = lambda x: fv[x]
check("II: E f=-1/2", E(f, 2) == F(-1, 2))
check("II: (f+1/2)^2 = 1/4,1/4,1/4,9/4", [(F(f(x)) + F(1, 2)) ** 2 for x in pts] == [F(1, 4)] * 3 + [F(9, 4)])
check("II: Var f=3/4", Var(f, 2) == F(3, 4))
check("II: f(x^1) の値 -1,1,-1,-1 と平均 -1/2", [f(flip(x, {1})) for x in pts] == [-1, 1, -1, -1] and E(lambda x: f(flip(x, {1})), 2) == F(-1, 2))
check("II: Pr[f=1]=1/4", F(sum(1 for x in pts if f(x) == 1), 4) == F(1, 4))
check("II: E[3f+2]=1/2", E(lambda x: 3 * f(x) + 2, 2) == F(1, 2))

# Part III
tab = {x: [chi(T, x) for T in [frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})]] for x in pts}
check("III: χ の表", tab == {(1, 1): [1, 1, 1, 1], (1, -1): [1, 1, -1, -1], (-1, 1): [1, -1, 1, -1], (-1, -1): [1, -1, -1, 1]})
check("III: 例 χ_{1}χ_{1,2}=χ_{2} at (-1,1): (-1)(-1)=1", chi({1}, (-1, 1)) * chi({1, 2}, (-1, 1)) == 1 == chi({2}, (-1, 1)))
coef = {T: E(lambda x: f(x) * chi(T, x), 2) for T in [frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})]}
check("III: 係数 -1/2,-1/2,-1/2,1/2", list(coef.values()) == [F(-1, 2), F(-1, 2), F(-1, 2), F(1, 2)])
check("III: f·χ_{1} = -1,-1,1,-1", [f(x) * chi({1}, x) for x in pts] == [-1, -1, 1, -1])
check("III: f·χ_{2} = -1,1,-1,-1", [f(x) * chi({2}, x) for x in pts] == [-1, 1, -1, -1])
check("III: f·χ_{1,2} = -1,1,1,1", [f(x) * chi({1, 2}, x) for x in pts] == [-1, 1, 1, 1])
check("III: 再構成", all(sum(coef[T] * chi(T, x) for T in coef) == f(x) for x in pts))
check("III: Σ_T χ_T(w): w=(1,-1) で 0, w=(1,1) で 4", sum(tab[(1, -1)]) == 0 and sum(tab[(1, 1)]) == 4)
# 次数の例：f=x1, h=x1+x2, fh=1+x1x2
check("III: x1(x1+x2)=1+x1x2", all(x[0] * (x[0] + x[1]) == 1 + x[0] * x[1] for x in pts))
# 本文の例：u=x1, v=x1+x2（係数の並びは ∅, {1}, {2}, {1,2}）
Ts = list(coef)
uh = [E(lambda x: x[0] * chi(T, x), 2) for T in Ts]
vh = [E(lambda x: (x[0] + x[1]) * chi(T, x), 2) for T in Ts]
uvh = [E(lambda x: x[0] * (x[0] + x[1]) * chi(T, x), 2) for T in Ts]
check("III: u の係数 (0,1,0,0)、v の係数 (0,1,1,0)", uh == [0, 1, 0, 0] and vh == [0, 1, 1, 0])
check("III: uv の係数 (1,0,0,1)", uvh == [1, 0, 0, 1])
conv = [sum(uh[a] * vh[b] for a in range(4) for b in range(4) if Ts[a] ^ Ts[b] == W) for W in Ts]
check("III: (III-9) で求めた uv の係数が、直接求めた係数と同じ", conv == uvh)
nz = [(sorted(Ts[a]), sorted(Ts[b])) for a in range(4) for b in range(4) if uh[a] * vh[b] != 0]
check("III: 係数が 0 でない組は ({1},{1}) と ({1},{2})", nz == [([1], [1]), ([1], [2])])
check("III: 2u-3v の係数 (0,-1,-3,0)", [E(lambda x: (2 * x[0] - 3 * (x[0] + x[1])) * chi(T, x), 2) for T in Ts] == [0, -1, -3, 0])
check("III: g=3χ_∅ は全点で 3、ほかの係数 0", [E(lambda x: 3 * chi(T, x), 2) for T in Ts] == [3, 0, 0, 0])
# (U2) の組の例：w=(1,-1), i=2
w = (1, -1)
check("III: 組 (∅,{2}) と ({1},{1,2}) の値がどちらも 1 と -1", (chi(set(), w), chi({2}, w)) == (1, -1) and (chi({1}, w), chi({1, 2}, w)) == (1, -1))
# Part I の追加の例
check("I: X1 と X1^3 は 0,1 で同じ値", all(t == t ** 3 for t in (0, 1)))
check("I: 3X1^2X2-X2+5 の単項式の次数 3,1,0", [2 + 1, 0 + 1, 0] == [3, 1, 0])
# (II-6) の例
check("II: (x^S)^S=x の例", flip(flip((1, -1, 1), {1, 3}), {1, 3}) == (1, -1, 1))
# 負の成分があると ||a||_1 > a([n])
check("II: 負の成分があれば ||a||_1 > a([n])", all(sum(abs(v) for v in a) > sum(a) for a in itertools.product([-2, -1, 0, 1, 2], repeat=3) if min(a) < 0))

# Part IV
check("IV: f(x)-f(x^1) = 0,-2,0,2", [f(x) - f(flip(x, {1})) for x in pts] == [0, -2, 0, 2])
check("IV: f(x)-f(x^2) = 0,0,-2,2", [f(x) - f(flip(x, {2})) for x in pts] == [0, 0, -2, 2])
Inf = lambda j: E(lambda x: (F(f(x) - f(flip(x, {j}))) / 2) ** 2, 2)
L = lambda j: E(lambda x: abs(f(x) - f(flip(x, {j}))), 2)
check("IV: Inf_1=Inf_2=1/2, L_1=L_2=1, L=2", Inf(1) == Inf(2) == F(1, 2) and L(1) == L(2) == 1 and L(1) + L(2) == 2)
check("IV: (2.3) c=1: (f-1)^2=4,4,4,0, 平均3 = 3/4+9/4", [(f(x) - 1) ** 2 for x in pts] == [4, 4, 4, 0] and E(lambda x: (f(x) - 1) ** 2, 2) == 3 == F(3, 4) + (F(-1, 2) - 1) ** 2)
check("IV: (2.4) 1 <= 2", L(1) ** 2 == 1 and 4 * Inf(1) == 2)
# h=|f(x)-f(x^1)| の値と分散
hv = [abs(f(x) - f(flip(x, {1}))) for x in pts]
check("IV: h=0,2,0,2, E h=1, E h^2=2, Var h=1", hv == [0, 2, 0, 2] and F(sum(hv), 4) == 1 and F(sum(v * v for v in hv), 4) == 2 and F(sum((v - 1) ** 2 for v in hv), 4) == 1)

# Part V
toX = lambda x: tuple((1 - v) // 2 for v in x)
check("V: 対応 x→X", [toX(x) for x in pts] == [(0, 0), (0, 1), (1, 0), (1, 1)])
check("V: f=2p-1 が例の f", all(2 * p(toX(x)) - 1 == f(x) for x in pts))
check("V: Var f = 4 Var p", Var(f, 2) == 4 * F(3, 16))
check("V: x=(1,-1), i=1: x^1=(-1,-1)→X=(1,1)=X^1 of (0,1)", toX(flip((1, -1), {1})) == (1, 1) == flipX((0, 1), 1))

bad = [n for n, v in ok if not v]
print(f"\n合計 {len(ok)} 件、不一致 {len(bad)} 件")
for n in bad:
    print("  不一致:", n)
sys.exit(1 if bad else 0)
