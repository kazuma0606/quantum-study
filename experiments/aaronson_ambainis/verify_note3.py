"""ノート3（予想から古典アルゴリズムへ）の式と数値例の検算。

対象のノート：研究ノート/09_論文読解/aaronson_ambainis/03_conjecture_to_classical_algorithm.md

一般の式は、N=1..4 のすべての点で、乱数の多項式（分数の係数）を作って、分数のまま確かめる。
- 次数の対応：{0,1}^N 上の次数 d 以下の多項式 p から f=2p-1 を作ると、|T|>d の係数が 0
- 影響力を係数で表す式、係数の2乗の和、総影響力 ≤ d（[AA14] の Lemma 3.1）
- 変数を固定した多項式の性質と、総影響力が平均で Inf_i だけ減る式
- 固定した座標によらない関数の平均、チェビシェフの不等式、マルコフの不等式
- アルゴリズム C を実際に走らせ、クエリの回数の平均、止まらない確率、誤差の確率を確かめる
数値例は、本文に書いた値と照らす。
検査ごとに「一致」「不一致」を表示し、不一致が1件でもあれば、終了コード 1 で終わる。

実行（リポジトリのルートから）:
    uv run python experiments/aaronson_ambainis/verify_note3.py
"""
from __future__ import annotations

import itertools
import random
import sys
from fractions import Fraction as F

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")  # Windows の既定の文字コードでは表示できない記号があるため
rnd = random.Random(20261112)

ok = []


def check(name, cond):
    ok.append((name, bool(cond)))
    print(("一致  " if cond else "不一致 ") + name)


# ---------- {0,1}^N 上の関数（点 → 値の辞書）と、多項式（指数の組 → 係数） ----------
def points(N):
    return list(itertools.product((0, 1), repeat=N))


def flip(X, i):  # X^i（i は 1 から）
    return tuple(1 - x if j == i - 1 else x for j, x in enumerate(X))


def setbit(X, i, b):  # X の i 番目を b にした点
    return tuple(b if j == i - 1 else x for j, x in enumerate(X))


def peval(poly, X):
    s = F(0)
    for m, c in poly.items():
        t = F(c)
        for x, e in zip(X, m):
            t *= F(x) ** e
        s += t
    return s


def table(poly, N):
    return {X: peval(poly, X) for X in points(N)}


def deg(poly):
    return max((sum(m) for m, c in poly.items() if c != 0), default=-1)


def restrict_poly(poly, i, b):  # 多項式の X_i に b を代入（指数 k の X_i は b^k）
    out = {}
    for m, c in poly.items():
        k = m[i - 1]
        c2 = F(c) * (F(b) ** k)
        m2 = tuple(0 if j == i - 1 else e for j, e in enumerate(m))
        out[m2] = out.get(m2, F(0)) + c2
    return {m: c for m, c in out.items() if c != 0}


def restrict(g, i, b):  # 関数の固定：g|_{i←b}(X) = g(X の i 番目を b にした点)
    return {X: g[setbit(X, i, b)] for X in g}


def mean(g):
    return sum(g.values(), F(0)) / len(g)


def var(g):
    m = mean(g)
    return sum(((v - m) ** 2 for v in g.values()), F(0)) / len(g)


def inf(g, i):  # Inf_i[g] = E[(g(X)-g(X^i))^2]
    return sum(((g[X] - g[flip(X, i)]) ** 2 for X in g), F(0)) / len(g)


def tinf(g, N):
    return sum((inf(g, i) for i in range(1, N + 1)), F(0))


def random_poly(N, d, maxexp=2):
    """次数 d 以下の多項式（指数は maxexp まで。多重線形でないものも含む）"""
    poly = {}
    for m in itertools.product(range(maxexp + 1), repeat=N):
        if sum(m) <= d and rnd.random() < 0.7:
            poly[m] = F(rnd.randint(-5, 5), rnd.randint(1, 4))
    return {m: c for m, c in poly.items() if c != 0}


def bounded(poly, N):
    """値を [0,1] に収める一次の変換 (p - min)/(max - min)。次数は上がらない"""
    t = table(poly, N)
    lo, hi = min(t.values()), max(t.values())
    if lo == hi:
        return {(0,) * N: F(1, 2)}
    out = {m: c / (hi - lo) for m, c in poly.items()}
    z = (0,) * N
    out[z] = out.get(z, F(0)) - lo / (hi - lo)
    return {m: c for m, c in out.items() if c != 0}


# ---------- Q_n 側：x_i = 1 - 2X_i、f = 2p - 1 ----------
def chi(T, x):
    r = 1
    for i in T:
        r *= x[i - 1]
    return r


def subsets(N):
    return [T for k in range(N + 1) for T in itertools.combinations(range(1, N + 1), k)]


def fourier(p_tab, N):
    """f(x) = 2p(X) - 1 の係数 f^(T) = E[f χ_T]"""
    out = {}
    for T in subsets(N):
        s = F(0)
        for X in points(N):
            x = tuple(1 - 2 * a for a in X)
            s += (2 * p_tab[X] - 1) * chi(T, x)
        out[T] = s / 2**N
    return out


# ================= Part II：変数を固定した多項式 =================
good_deg = good_val = good_dep = good_self = True
for N in range(1, 5):
    for _ in range(15):
        d = rnd.randint(0, 3)
        poly = bounded(random_poly(N, d), N)
        tab = table(poly, N)
        for i in range(1, N + 1):
            for b in (0, 1):
                rp = restrict_poly(poly, i, b)
                rt = restrict(tab, i, b)
                good_deg &= deg(rp) <= max(deg(poly), -1) and (deg(poly) < 0 or deg(rp) <= deg(poly))
                good_val &= table(rp, N) == rt and all(0 <= v <= 1 for v in rt.values())
                good_dep &= all(rt[X] == rt[flip(X, i)] for X in rt)
            # p(X) = p|_{i←X_i}(X)
            good_self &= all(tab[X] == restrict(tab, i, X[i - 1])[X] for X in tab)
check("II: 固定した多項式の次数は元の次数以下", good_deg)
check("II: 固定した多項式の値は、元の値（[0,1] に入る）", good_val)
check("II: 固定した多項式は X_i によらない（g(X)=g(X^i)）", good_dep)
check("II: p(X) = p|_{i←X_i}(X)", good_self)

# 影響力の分解：l≠i で Inf_l[p] = (Inf_l[p|0] + Inf_l[p|1])/2、Inf_i[p|b] = 0、総影響力の式
good_split = good_zero = good_total = good_mean = good_var = True
for N in range(1, 5):
    for _ in range(15):
        tab = table(bounded(random_poly(N, rnd.randint(0, 3)), N), N)
        for i in range(1, N + 1):
            g0, g1 = restrict(tab, i, 0), restrict(tab, i, 1)
            for l in range(1, N + 1):
                if l != i:
                    good_split &= inf(tab, l) == (inf(g0, l) + inf(g1, l)) / 2
            good_zero &= inf(g0, i) == 0 and inf(g1, i) == 0
            good_total &= (tinf(g0, N) + tinf(g1, N)) / 2 == tinf(tab, N) - inf(tab, i)
            good_mean &= (mean(g0) + mean(g1)) / 2 == mean(tab)
            # 分散は平均で減る（使わないが、確かめておく）
            good_var &= (var(g0) + var(g1)) / 2 <= var(tab)
check("II: l≠i で Inf_l[p] = (Inf_l[p|_{i←0}] + Inf_l[p|_{i←1}])/2", good_split)
check("II: Inf_i[p|_{i←b}] = 0", good_zero)
check("II: (Inf[p|_{i←0}] + Inf[p|_{i←1}])/2 = Inf[p] - Inf_i[p]", good_total)
check("II: (E[p|_{i←0}] + E[p|_{i←1}])/2 = E[p]", good_mean)
check("II: (Var[p|0] + Var[p|1])/2 ≤ Var[p]（参考）", good_var)

# 固定した座標によらない関数：A 上の平均 = 全体の平均
good_A = True
for N in range(1, 5):
    for _ in range(10):
        S = [i for i in range(1, N + 1) if rnd.random() < 0.5]
        bvals = {i: rnd.randint(0, 1) for i in S}
        tab = table(random_poly(N, 3), N)
        g = tab
        for i in S:
            g = restrict(g, i, bvals[i])  # S の座標によらない関数
        A = [X for X in points(N) if all(X[i - 1] == bvals[i] for i in S)]
        good_A &= len(A) == 2 ** (N - len(S))
        good_A &= sum((g[X] for X in A), F(0)) / len(A) == mean(g)
        # 2^{|S|} 対 1 の対応
        cnt = {}
        for X in points(N):
            Y = X
            for i in S:
                Y = setbit(Y, i, bvals[i])
            cnt[Y] = cnt.get(Y, 0) + 1
        good_A &= set(cnt) == set(A) and all(c == 2 ** len(S) for c in cnt.values())
check("II: S の座標によらない g で、A 上の平均 = E[g]、|A| = 2^{N-|S|}、各点に 2^{|S|} 個が移る", good_A)

# チェビシェフ：Pr[|g - Eg| > ε] ≤ Var/ε^2
good_cheb = True
for N in range(1, 5):
    for _ in range(10):
        tab = table(bounded(random_poly(N, 3), N), N)
        m, v = mean(tab), var(tab)
        for eps in (F(1, 10), F(1, 4), F(1, 2)):
            frac = F(sum(1 for x in tab.values() if abs(x - m) > eps), 2**N)
            good_cheb &= frac <= v / eps**2
check("II: チェビシェフの不等式 Pr[|g-Eg|>ε] ≤ Var[g]/ε^2", good_cheb)

# ================= Part III：次数の対応と、総影響力 ≤ d =================
good_degf = good_infT = good_pars = good_sum = good_le = True
for N in range(1, 5):
    for _ in range(20):
        d = rnd.randint(1, 3)
        poly = bounded(random_poly(N, d), N)
        tab = table(poly, N)
        fh = fourier(tab, N)
        good_degf &= all(fh[T] == 0 for T in fh if len(T) > d)
        for j in range(1, N + 1):
            good_infT &= inf(tab, j) == sum((fh[T] ** 2 for T in fh if j in T), F(0))
        Ef2 = sum(((2 * tab[X] - 1) ** 2 for X in tab), F(0)) / 2**N
        good_pars &= Ef2 == sum((c**2 for c in fh.values()), F(0))
        good_sum &= tinf(tab, N) == sum((len(T) * fh[T] ** 2 for T in fh), F(0))
        good_le &= tinf(tab, N) <= d * Ef2 <= d and Ef2 <= 1
check("III: p の次数 ≤ d なら、f=2p-1 の |T|>d の係数は 0", good_degf)
check("III: Inf_j[p] = Σ_{T∋j} f^(T)^2", good_infT)
check("III: E[f^2] = Σ_T f^(T)^2", good_pars)
check("III: Σ_j Inf_j = Σ_T |T| f^(T)^2", good_sum)
check("III: Inf[p] ≤ d E[f^2] ≤ d（値が [0,1]）", good_le)
# 次数が d 以下の一次の関数：X_i = (χ_∅ - χ_{i})/2
x_sym = sp.symbols("x1:5")
good_u = True
for N in range(1, 5):
    for i in range(1, N + 1):
        for T in subsets(N):
            # u_i(x) = (1 - x_i)/2 の係数 E[u_i χ_T]（x は Q_N の全点）
            c = sum((F(1 - x[i - 1], 2) * chi(T, x) for x in itertools.product((1, -1), repeat=N)), F(0)) / 2**N
            want = F(1, 2) if T == () else (F(-1, 2) if T == (i,) else F(0))
            good_u &= c == want
check("III: X_i = (1 - x_i)/2 の係数は χ_∅ に 1/2、χ_{i} に -1/2、ほかは 0（N=1〜4）", good_u)
# 次数の対応で、単項式 X_1^2 X_2（次数 3）→ (1-x1)^2(1-x2)/8 を x_i^2=1 で直すと次数 ≤ 3
e = sp.expand(((1 - x_sym[0]) / 2) ** 2 * ((1 - x_sym[1]) / 2))
e_ml = sp.expand(e.subs(x_sym[0] ** 2, 1))
check("III: X_1^2 X_2 → (1-x_1)(1-x_2)/4（x_1^2=1 で）", sp.expand(e_ml - (1 - x_sym[0]) * (1 - x_sym[1]) / 4) == 0)


# ================= Part IV：アルゴリズム C =================
def run_C(tab, N, v, theta, Mfloor=None):
    """入力ごとに C を走らせ、(クエリの回数 K, 出力, 履歴, 選んだ影響力の列, 最後の多項式) を返す"""
    res = {}
    for X in tab:
        g = tab
        K = 0
        hist = []
        infs = []
        while var(g) > v:
            if Mfloor is not None and K >= Mfloor:
                break
            cand = [i for i in range(1, N + 1) if inf(g, i) > theta]
            if not cand:
                return None  # 仮定が成り立たない（本文の仮定のもとでは起こらない）
            i = cand[0]
            infs.append(inf(g, i))
            hist.append((i, X[i - 1]))
            g = restrict(g, i, X[i - 1])
            K += 1
        res[X] = (K, mean(g), tuple(hist), infs, g)
    return res


good_assume = good_tele = good_EK = good_markov = good_fail = good_leaf = good_new = True
n_runs = 0
for N in range(1, 5):
    for _ in range(25):
        T = rnd.randint(1, 2)
        poly = bounded(random_poly(N, 2 * T), N)
        tab = table(poly, N)
        eps = F(rnd.choice([1, 2, 3]), 10)
        delta = F(rnd.choice([1, 2, 4]), 10)
        v = eps**2 * delta / 2
        theta = (eps**2 * delta / (4 * T)) ** 7
        # 仮定（論文の Corollary 1.2 の形）が、この小さい例で成り立つか（参考の確かめ）
        if var(tab) > 0:
            good_assume &= max(inf(tab, i) for i in range(1, N + 1)) >= (var(tab) / (2 * T)) ** 7
        res = run_C(tab, N, v, theta)
        if res is None:
            good_assume = False
            continue
        n_runs += 1
        Ks = {X: r[0] for X, r in res.items()}
        EK = F(sum(Ks.values()), 2**N)
        # 望遠鏡の式：E[Inf[p_K]] = Inf[p] - E[Σ_j Inf_{i_j}[p_j]]
        E_last = sum((tinf(r[4], N) for r in res.values()), F(0)) / 2**N
        E_used = sum((sum(r[3], F(0)) for r in res.values()), F(0)) / 2**N
        good_tele &= E_last == tinf(tab, N) - E_used
        good_EK &= theta * EK <= E_used <= tinf(tab, N) <= 2 * T
        # 選ばれた番号は、まだ聞いていない番号
        good_new &= all(len({i for i, _ in r[2]}) == len(r[2]) for r in res.values())
        M = (4 * T) ** 8 * eps ** (-14) * delta ** (-8)
        good_markov &= F(sum(1 for k in Ks.values() if k >= M), 2**N) <= delta / 2
        good_markov &= M == 4 * T / (delta * theta)
        # 葉ごと：同じ履歴の入力の集合 = 履歴と合う入力の集合
        leaves = {}
        for X, r in res.items():
            leaves.setdefault(r[2], []).append(X)
        for h, Xs in leaves.items():
            A = [X for X in points(N) if all(X[i - 1] == b for i, b in h)]
            good_leaf &= sorted(A) == sorted(Xs)
        # 誤差：|出力 - p(X)| > ε の割合 ≤ δ
        Mf = int(M) if M < 10**6 else 10**6
        resM = run_C(tab, N, v, theta, Mf)
        fail = F(sum(1 for X, r in resM.items() if abs(r[1] - tab[X]) > eps), 2**N)
        good_fail &= fail <= delta
        # 止まったときは、葉の上で Var ≤ v
        good_fail &= all(var(r[4]) <= v for r in res.values())
check("IV: 小さい例で、仮定 Inf_i ≥ (Var/2T)^7 を満たす i がある（参考。論文の主張の検査ではない）", good_assume)
check("IV: E[Inf[p_K]] = Inf[p] - E[Σ_j Inf_{i_j}[p_j]]", good_tele)
check("IV: θ E[K] ≤ E[Σ Inf_{i_j}[p_j]] ≤ Inf[p] ≤ 2T", good_EK)
check("IV: 選ぶ番号は、まだ聞いていない番号", good_new)
check("IV: M = 4T/(δθ) = (4T)^8 ε^-14 δ^-8、Pr[K ≥ M] ≤ δ/2", good_markov)
check("IV: 同じ履歴で止まる入力の集合 = 履歴と合う入力の集合", good_leaf)
check("IV: 誤差が ε を超える割合 ≤ δ、止まったとき Var ≤ ε^2δ/2", good_fail)
check(f"IV: アルゴリズムを走らせた例の数 = {n_runs}（0 でない）", n_runs > 0)

# θ を大きくした（人工の）しきい値でも、E[K] ≤ Inf[p]/θ' の議論が成り立つこと
good_big = True
cnt_big = 0
for N in range(2, 5):
    for _ in range(25):
        tab = table(bounded(random_poly(N, 3), N), N)
        th = F(rnd.choice([1, 2, 5]), 100)
        v = F(1, 100)
        res = {}
        okrun = True
        for X in tab:
            g, K, used = tab, 0, F(0)
            while var(g) > v:
                cand = [i for i in range(1, N + 1) if inf(g, i) > th]
                if not cand:
                    break
                i = cand[0]
                used += inf(g, i)
                g = restrict(g, i, X[i - 1])
                K += 1
            res[X] = (K, used, g)
        EK = F(sum(r[0] for r in res.values()), 2**N)
        Eused = sum((r[1] for r in res.values()), F(0)) / 2**N
        Elast = sum((tinf(r[2], N) for r in res.values()), F(0)) / 2**N
        good_big &= Elast == tinf(tab, N) - Eused and th * EK <= Eused <= tinf(tab, N)
        cnt_big += EK > 0
check(f"IV: 大きいしきい値 θ' でも θ' E[K] ≤ Inf[p]（K>0 の例 {cnt_big} 件）", good_big and cnt_big > 0)

# 式の変形（記号で）
e_, d_, T_ = sp.symbols("epsilon delta T", positive=True)
v_ = e_**2 * d_ / 2
th_ = (e_**2 * d_ / (4 * T_)) ** 7
check("IV: (v/(2T))^7 = (ε^2δ/(4T))^7（v=ε^2δ/2）", sp.simplify((v_ / (2 * T_)) ** 7 - th_) == 0)
check("IV: (2T/θ)/(δ/2) = 4T/(δθ)", sp.simplify((2 * T_ / th_) / (d_ / 2) - 4 * T_ / (d_ * th_)) == 0)
check("IV: 4T/(δθ) = (4T)^8 ε^-14 δ^-8", sp.simplify(4 * T_ / (d_ * th_) - (4 * T_) ** 8 * e_ ** (-14) * d_ ** (-8)) == 0)
check("IV: v/ε^2 = δ/2", sp.simplify(v_ / e_**2 - d_ / 2) == 0)

# ================= 数値例 =================
X1, X2 = sp.symbols("X1 X2")
# 例1：P = (X1 + X2)/2（1回のクエリ）。回路で確かめる
r2 = sp.sqrt(2)
psi0 = {(1, 0): 1 / r2, (1, 1): 0, (2, 0): 1 / r2, (2, 1): 0}  # U0|s> = (H⊗I)|1,0>
good_circ = True
for X in points(2):
    after = {}
    for (i, b), a in psi0.items():
        k = (i, b ^ X[i - 1])
        after[k] = after.get(k, 0) + a
    pacc = sp.simplify(abs(after[(1, 1)]) ** 2 + abs(after[(2, 1)]) ** 2)
    good_circ &= pacc == sp.Rational(X[0] + X[1], 2)
check("例1: |s>=|1,0>、U0=H⊗I、U1=I、B={(1,1),(2,1)} の受理確率 = (X1+X2)/2", good_circ)
H = sp.Matrix([[1, 1], [1, -1]]) / r2
U0 = sp.kronecker_product(H, sp.eye(2))
check("例1: U0|1,0> = (|1,0>+|2,0>)/√2", list(U0[:, 0]) == [1 / r2, 0, 1 / r2, 0])
pA = {(1, 0): F(1, 2), (0, 1): F(1, 2)}  # (X1+X2)/2
tA = table(pA, 2)
check("例1: 値 0, 1/2, 1/2, 1", [tA[X] for X in points(2)] == [0, F(1, 2), F(1, 2), 1])
check("例1: E = 1/2、Var = 1/8", mean(tA) == F(1, 2) and var(tA) == F(1, 8))
check("例1: Inf_1 = Inf_2 = 1/4、Inf = 1/2", inf(tA, 1) == F(1, 4) and inf(tA, 2) == F(1, 4) and tinf(tA, 2) == F(1, 2))
fhA = fourier(tA, 2)
check("例1: f = 2p-1 = -(x1+x2)/2 の係数（∅:0, {1}:-1/2, {2}:-1/2, {1,2}:0）",
      fhA[()] == 0 and fhA[(1,)] == F(-1, 2) and fhA[(2,)] == F(-1, 2) and fhA[(1, 2)] == 0)
check("例1: Σ|T| f^2 = 1/2 ≤ d E[f^2] = 1·1/2（d=1）", sum(len(T) * c**2 for T, c in fhA.items()) == F(1, 2) and sum(c**2 for c in fhA.values()) == F(1, 2))
epsA, delA, TA = F(1, 2), F(1, 2), 1
vA = epsA**2 * delA / 2
thA = (epsA**2 * delA / (4 * TA)) ** 7
check("例1: v = ε^2δ/2 = 1/16、θ = (1/32)^7", vA == F(1, 16) and thA == F(1, 32) ** 7)
check("例1: θ = 2^-35 ≈ 2.91×10^-11", thA == F(1, 2**35) and abs(float(thA) - 2.91e-11) < 0.01e-11)
MA = (4 * TA) ** 8 * epsA ** (-14) * delA ** (-8)
check("例1: M = 2^38 = 274877906944 ≈ 2.7×10^11", MA == 2**38 == 274877906944)
for b in (0, 1):
    g = restrict(tA, 1, b)
    check(f"例1: p|_(1←{b}) の値（X2=0,1）= {b}/2, ({b}+1)/2、Var = 1/16、E = {b}/2+1/4",
          [g[(b, 0)], g[(b, 1)]] == [F(b, 2), F(b + 1, 2)] and var(g) == F(1, 16) and mean(g) == F(b, 2) + F(1, 4))
    check(f"例1: p|_(1←{b}) の Inf_2 = 1/4、総影響力 1/4 = 1/2 - 1/4", inf(g, 2) == F(1, 4) and tinf(g, 2) == F(1, 4))
resA = run_C(tA, 2, vA, thA)
check("例1: C は、どの入力でも X_1 を1回聞いて止まる（K=1）", all(r[0] == 1 and r[2][0][0] == 1 for r in resA.values()))
check("例1: 出力 = X1/2 + 1/4、誤差 |p(X) - 出力| = 1/4", all(r[1] == F(X[0], 2) + F(1, 4) and abs(tA[X] - r[1]) == F(1, 4) for X, r in resA.items()))
check("例1: チェビシェフの右辺 Var/ε^2 = (1/16)/(1/4) = 1/4 = δ/2", F(1, 16) / epsA**2 == F(1, 4) == delA / 2)
check("例1: E[K] = 1 ≤ 2T/θ", F(1) <= 2 * TA / thA)

# 例2：ノート2 の X1⊕X2（p = X1 + X2 - 2X1X2）
pB = {(1, 0): 1, (0, 1): 1, (1, 1): -2}
tB = table(pB, 2)
check("例2: Inf_1 = Inf_2 = 1、Inf = 2 = d = 2T", inf(tB, 1) == 1 and inf(tB, 2) == 1 and tinf(tB, 2) == 2)
fhB = fourier(tB, 2)
check("例2: f = 2p-1 = -x1x2（係数は {1,2} に -1 だけ）", fhB[(1, 2)] == -1 and all(fhB[T] == 0 for T in fhB if T != (1, 2)))
for b in (0, 1):
    g = restrict(tB, 1, b)
    want = {0: [F(0), F(1)], 1: [F(1), F(0)]}[b]
    check(f"例2: p|_(1←{b}) の値（X2=0,1）= {want}、Var = 1/4、総影響力 1 = 2 - 1",
          [g[(b, 0)], g[(b, 1)]] == want and var(g) == F(1, 4) and tinf(g, 2) == 1)
resB = run_C(tB, 2, F(1, 16), thA)
check("例2: C は X_1, X_2 を聞いて止まり（K=2）、出力は p(X) と等しい", all(r[0] == 2 and r[1] == tB[X] for X, r in resB.items()))

bad = [n for n, v in ok if not v]
print(f"\n合計 {len(ok)} 件、不一致 {len(bad)} 件")
for n in bad:
    print("  不一致:", n)
sys.exit(1 if bad else 0)
