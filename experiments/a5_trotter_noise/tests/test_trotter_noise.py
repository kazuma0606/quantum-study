"""テーマ A-5 の反例探し。

乱数で多数の場合を試し、主張（誤差の上限、望遠鏡和、雑音の通路の性質、Qiskit の回路との一致、
最適な分割数の振る舞い）が破れる場合がないかを調べる。破れたら、その場合（種・次元・パラメータ）を表示して失敗する。

実行（リポジトリのルートから）: uv run pytest experiments/a5_trotter_noise -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import trotter_noise as tn  # noqa: E402

N_TRIALS = 400
RTOL = 1e-9


def random_hermitian(rng: np.random.Generator, dim: int, scale: float) -> np.ndarray:
    M = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
    return scale * (M + M.conj().T) / 2


def random_case(seed: int):
    rng = np.random.default_rng(seed)
    dim = int(rng.integers(2, 9))
    A = random_hermitian(rng, dim, rng.uniform(0.1, 3))
    B = random_hermitian(rng, dim, rng.uniform(0.1, 3))
    t = float(rng.uniform(0.05, 3))
    n = int(rng.integers(1, 40))
    return dim, A, B, t, n


# ------------------------------------------------------------------ 誤差の上限
@pytest.mark.parametrize("order", [1, 2])
def test_trotter_bound_random_hermitian(order: int) -> None:
    """ランダムなエルミート行列の組で、n ステップの誤差が上限を超えないか（反例探し）。"""
    worst = 0.0
    for seed in range(N_TRIALS):
        dim, A, B, t, n = random_case(seed)
        U = tn.step_unitary(A, B, t / n, order)
        err = tn.opnorm(np.linalg.matrix_power(U, n) - expm(-1j * (A + B) * t))
        bound = tn.trotter_bound(A, B, t, n, order)
        worst = max(worst, err / bound if bound > 0 else 0.0)
        assert err <= bound * (1 + RTOL) + 1e-12, (
            f"反例：order={order}, seed={seed}, dim={dim}, t={t:.3f}, n={n}, 誤差={err:.3e} > 上限={bound:.3e}")
    print(f"order={order}：誤差/上限 の最大 = {worst:.3f}")


@pytest.mark.parametrize("order", [1, 2])
def test_trotter_bound_single_step_is_tight_order(order: int) -> None:
    """1ステップの誤差が、小さな δ で δ^{order+1} に比例する（上限の次数が正しい）。"""
    rng = np.random.default_rng(1)
    A, B = random_hermitian(rng, 4, 1.0), random_hermitian(rng, 4, 1.0)
    ds = np.array([1e-2, 5e-3, 2.5e-3])
    errs = [tn.opnorm(tn.step_unitary(A, B, d, order) - expm(-1j * (A + B) * d)) for d in ds]
    slope = np.polyfit(np.log(ds), np.log(errs), 1)[0]
    assert abs(slope - (order + 1)) < 0.05, f"1ステップの誤差の次数 {slope:.3f} が {order + 1} でない"


def test_telescoping_inequality() -> None:
    """‖U^n - V^n‖ ≤ n‖U - V‖（‖U‖, ‖V‖ ≤ 1）。ユニタリと、ノルム 1 以下の縮小写像で反例を探す。"""
    rng = np.random.default_rng(7)
    for seed in range(N_TRIALS):
        dim = int(rng.integers(2, 7))
        n = int(rng.integers(1, 30))
        if seed % 2 == 0:
            U = expm(-1j * random_hermitian(rng, dim, 1.0))
            V = expm(-1j * random_hermitian(rng, dim, 1.0))
        else:
            M1, M2 = rng.normal(size=(dim, dim)), rng.normal(size=(dim, dim))
            U, V = M1 / tn.opnorm(M1), M2 / tn.opnorm(M2) * rng.uniform(0.5, 1)
        lhs = tn.opnorm(np.linalg.matrix_power(U, n) - np.linalg.matrix_power(V, n))
        rhs = n * tn.opnorm(U - V)
        assert lhs <= rhs * (1 + RTOL) + 1e-12, f"反例：seed={seed}, dim={dim}, n={n}, {lhs:.3e} > {rhs:.3e}"


# ------------------------------------------------------------------ 雑音の通路
def test_depolarizing_is_cptp_like() -> None:
    """脱分極の通路が、トレース・エルミート性・正定値性を保つか。p=1 で i,j の部分が I/4 になるか。"""
    rng = np.random.default_rng(3)
    for seed in range(200):
        n_q = int(rng.integers(2, 5))
        dim = 2**n_q
        M = rng.normal(size=(dim, dim)) + 1j * rng.normal(size=(dim, dim))
        rho = M @ M.conj().T
        rho /= np.trace(rho)
        i, j = sorted(rng.choice(n_q, 2, replace=False))
        p = float(rng.uniform(0, 1))
        out = tn.depolarize_pair(rho, int(i), int(j), p, n_q)
        assert np.isclose(np.trace(out), 1), f"トレースが保たれない：seed={seed}"
        assert np.allclose(out, out.conj().T), f"エルミートでない：seed={seed}"
        assert np.linalg.eigvalsh(out).min() > -1e-12, f"負の固有値：seed={seed}"


# ------------------------------------------------------------------ Qiskit との一致
def _qiskit_matrix(n_qubits: int, t: float, n: int, order: int) -> np.ndarray:
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import PauliEvolutionGate
    from qiskit.quantum_info import Operator, SparsePauliOp
    from qiskit.synthesis import LieTrotter, SuzukiTrotter

    # Qiskit のパウリ文字列は右端が量子ビット 0。こちらの op_on は左端が 0 なので、文字列を反転して合わせる
    def label(ops: dict[int, str]) -> str:
        return "".join(ops.get(k, "I") for k in range(n_qubits))[::-1]

    zz = [label({i: "Z", i + 1: "Z"}) for i in range(n_qubits - 1)]
    xs = [label({i: "X"}) for i in range(n_qubits)]
    if order == 1:
        terms, synth = zz + xs, LieTrotter(reps=n)               # 先に並べた ZZ が先に作用する
    else:
        terms, synth = xs + zz, SuzukiTrotter(order=2, reps=n)   # 先に並べた X が外側
    op = SparsePauliOp(terms, [1.0] * len(terms))
    qc = QuantumCircuit(n_qubits)
    qc.append(PauliEvolutionGate(op, time=t, synthesis=synth), range(n_qubits))
    # Operator は量子ビット 0 を右端（クロネッカー積の最後）に置く。こちらの並び（左端が 0）に合わせて反転する
    return Operator(qc.decompose().decompose()).reverse_qargs().data


@pytest.mark.parametrize("n_qubits", [2, 3])
@pytest.mark.parametrize("order", [1, 2])
def test_matches_qiskit_synthesis(n_qubits: int, order: int) -> None:
    """自前のトロッター積が、Qiskit の LieTrotter・SuzukiTrotter の回路と（大域位相を除いて）一致するか。"""
    t, n = 1.3, 5
    A, B = tn.tfim_parts(n_qubits)
    mine = np.linalg.matrix_power(tn.step_unitary(A, B, t / n, order), n)
    theirs = _qiskit_matrix(n_qubits, t, n, order)
    overlap = abs(np.trace(mine.conj().T @ theirs)) / mine.shape[0]
    assert np.isclose(overlap, 1, atol=1e-9), f"Qiskit と一致しない：重なり {overlap:.6f}"


# ------------------------------------------------------------------ 最適な分割数
def _best_n(n_qubits: int, order: int, p: float, metric: str, t: float = 2.0, nmax: int = 30) -> int:
    errs = [getattr(tn.run_point(n_qubits, t, order, n, p), metric) for n in range(1, nmax + 1)]
    return int(np.argmin(errs)) + 1


@pytest.mark.parametrize("metric", ["infidelity", "local_err"])
def test_optimal_n_decreases_with_noise(metric: str) -> None:
    """雑音 p を強くすると、最適な分割数 n* は増えない（N=2、t=2）。"""
    ps = [0.002, 0.005, 0.01, 0.02, 0.04]
    for order in (1, 2):
        best = [_best_n(2, order, p, metric) for p in ps]
        assert all(b2 <= b1 for b1, b2 in zip(best, best[1:])), f"反例：order={order}, {metric}, n*={best}"


@pytest.mark.parametrize("metric", ["infidelity", "local_err"])
def test_strang_needs_fewer_steps(metric: str) -> None:
    """同じ雑音なら、ストラング分解の n* はトロッター分解以下で、到達できる最小誤差も小さい（N=2、t=2）。"""
    for p in (0.005, 0.01, 0.02):
        n1, n2 = _best_n(2, 1, p, metric), _best_n(2, 2, p, metric)
        e1 = getattr(tn.run_point(2, 2.0, 1, n1, p), metric)
        e2 = getattr(tn.run_point(2, 2.0, 2, n2, p), metric)
        assert n2 <= n1 and e2 <= e1, f"反例：p={p}, {metric}, n*: Lie {n1} / Strang {n2}, 誤差 {e1:.4f} / {e2:.4f}"


# ------------------------------------------------------------------ 予測の精度と、見つかった反例
def _optimum_table(qubits: list[int], ps: list[float], nmax: int = 30) -> list[dict]:
    from dataclasses import asdict

    import analyze

    rows = [asdict(tn.run_point(nq, 2.0, order, n, p))
            for nq in qubits for order in (1, 2) for p in [0.0] + ps for n in range(1, nmax + 1)]
    return analyze.analyze(rows)


def test_global_infidelity_follows_model() -> None:
    """状態全体の不忠実度では、モデル a/n^q + b p n の予測 n* が、実際の n* と 2 以内で合う（N=2〜5）。
    当てはめた q は 2×次数（1次で約2、2次で約4）に近い。ただし N=3 の1次だけは q≈2.4〜2.5 とずれる
    （n≤30〜40 ではまだ漸近的な振る舞いに達していない）ので、許容幅を 0.5 にしている。"""
    table = [r for r in _optimum_table([2, 3, 4, 5], [0.001, 0.002, 0.005, 0.01, 0.02]) if r["metric"] == "infidelity"]
    for r in table:
        assert abs(r["n_star"] - r["n_star_pred"]) <= 2, f"予測が外れた：{r}"
        assert abs(r["q_fit"] - 2 * r["order"]) < 0.5, f"q が 2×次数 から外れた：{r}"


def test_local_observable_order_symmetry() -> None:
    """⟨Z_0⟩ は、A と B の順番を入れ替えたトロッター積でも同じ値になる（乱数で t, n, N を変えて反例を探す）。
    この対称性のため、1次のトロッター分解でも局所的な量の誤差は 1/n^2 で減る。"""
    rng = np.random.default_rng(11)
    for _ in range(60):
        N = int(rng.integers(2, 6))
        t, n = float(rng.uniform(0.3, 3)), int(rng.integers(1, 20))
        A, B = tn.tfim_parts(N, J=float(rng.uniform(0.3, 2)), g=float(rng.uniform(0.3, 2)))
        Z0 = tn.op_on(tn.Z, 0, N)
        psi0 = np.zeros(2**N, dtype=complex)
        psi0[0] = 1
        d = t / n
        vals = []
        for first, second in ((A, B), (B, A)):
            psi = np.linalg.matrix_power(expm(-1j * second * d) @ expm(-1j * first * d), n) @ psi0
            vals.append(np.real(psi.conj() @ Z0 @ psi))
        assert np.isclose(vals[0], vals[1], atol=1e-10), f"反例：N={N}, t={t:.3f}, n={n}, {vals}"


def test_known_counterexamples_local_observable() -> None:
    """局所的な量 |⟨Z_0⟩ の誤差| では、素朴な主張に反例がある（見つかった反例を固定しておく）。
    (a) 「ストラング分解の n* はトロッター分解以下」：N=3, p=0.005 で Lie 9 < Strang 10。
    (b) 「モデルの予測どおり」：N=3〜5、2次、p≥0.01 で n*=2（予測は約7.5）。小さい n ではトロッター誤差
        そのものが n について単調でなく、n=2 でたまたま小さくなるため。"""
    table = [r for r in _optimum_table([3, 4, 5], [0.005, 0.01, 0.02]) if r["metric"] == "local_err"]
    get = {(r["n_qubits"], r["order"], r["p"]): r for r in table}
    assert get[(3, 1, 0.005)]["n_star"] < get[(3, 2, 0.005)]["n_star"]
    for N in (3, 4, 5):
        for p in (0.01, 0.02):
            r = get[(N, 2, p)]
            assert r["n_star"] == 2 and r["n_star_pred"] > 5, r


# ------------------------------------------------------------------ 局所的な量の、符号つきの分解
def test_local_error_decomposition_identity() -> None:
    """local_err = |トロッター部分 + 雑音部分|（どちらも符号つき）が、すべての条件で成り立つ。"""
    for N in (2, 3, 4):
        for order in (1, 2):
            for p in (0.0, 0.005, 0.02):
                for n in (1, 3, 7, 15):
                    r = tn.run_point(N, 2.0, order, n, p)
                    assert np.isclose(abs(r.z_trotter_part + r.z_noise_part), r.local_err, atol=1e-12), r


def test_noise_does_not_always_shrink_toward_zero() -> None:
    """反例の固定：「雑音は <Z_0> を必ず 0 に近づける（雑音部分の符号は、雑音なしの値と逆）」は成り立たない。
    雑音なしの値が 0 に近いと、雑音が同じ向きに押すことがある（例：N=5、2次、p=0.02、n=3）。"""
    r = tn.run_point(5, 2.0, 2, 3, 0.02)
    z_clean = r.z_exact + r.z_trotter_part
    assert z_clean < 0 and r.z_noise_part < 0, r


def test_lie_local_optimum_is_a_cancellation_point() -> None:
    """1次の分解で局所的な量を測ったときの最適な n* は、トロッター部分と雑音部分の符号が逆で、
    互いの大きさの3割未満まで打ち消し合う点になっている（N=3、p = 0.001, 0.005, 0.02）。
    つまり、この量の「最小誤差」は綱引きの釣り合いではなく、偶然の打ち消し合いで決まっている。"""
    for p in (0.001, 0.005, 0.02):
        rs = [tn.run_point(3, 2.0, 1, n, p) for n in range(1, 31)]
        best = min(rs, key=lambda r: r.local_err)
        tp, npart = best.z_trotter_part, best.z_noise_part
        assert tp * npart < 0, best
        assert best.local_err < 0.3 * min(abs(tp), abs(npart)), best


# ------------------------------------------------------------------ 1次の誤差の係数（導出した式の検証）
def _product_state(thetas, phases) -> np.ndarray:
    from functools import reduce
    return reduce(np.kron, [np.array([np.cos(a / 2), np.exp(1j * b) * np.sin(a / 2)]) for a, b in zip(thetas, phases)])


def test_first_order_coefficient_formula() -> None:
    """導出した c_1 の式が、数値の (誤差) × n / t と一致する（ランダムな積状態と観測量、N=2〜4、n=2000）。"""
    rng = np.random.default_rng(21)
    for _ in range(12):
        N = int(rng.integers(2, 5))
        A, B = tn.tfim_parts(N, J=float(rng.uniform(0.5, 1.5)), g=float(rng.uniform(0.5, 1.5)))
        psi0 = _product_state(rng.uniform(0.2, 2.9, N), rng.uniform(0, 2 * np.pi, N))
        O = tn.op_on([tn.Z, tn.X][int(rng.integers(2))], int(rng.integers(N)), N)
        t, n = float(rng.uniform(0.5, 2.5)), 2000
        exact = expm(-1j * (A + B) * t) @ psi0
        psi = np.linalg.matrix_power(tn.step_unitary(A, B, t / n, 1), n) @ psi0
        err = np.real(psi.conj() @ O @ psi) - np.real(exact.conj() @ O @ exact)
        c1 = tn.first_order_coefficient(A, B, psi0, O, t)
        assert abs(err * n / t - c1) < 0.02 + 0.02 * abs(c1), f"式と合わない：N={N}, t={t:.3f}, 数値 {err * n / t:.4f}, 式 {c1:.4f}"


def test_layden_condition_gives_zero_first_order() -> None:
    """O が A（ZZ の項）と交換し、初期状態が A の固有状態（計算基底の状態）なら c_1 = 0（乱数で反例を探す）。"""
    rng = np.random.default_rng(23)
    for _ in range(40):
        N = int(rng.integers(2, 5))
        A, B = tn.tfim_parts(N, J=float(rng.uniform(0.3, 2)), g=float(rng.uniform(0.3, 2)))
        psi0 = np.zeros(2**N, dtype=complex)
        psi0[int(rng.integers(2**N))] = 1
        O = tn.op_on(tn.Z, int(rng.integers(N)), N)
        assert abs(tn.first_order_coefficient(A, B, psi0, O, float(rng.uniform(0.3, 3)))) < 1e-12


def test_time_reversal_hypothesis_is_false() -> None:
    """反例の固定：「ハミルトニアン・初期状態・観測量がすべて実数なら c_1 = 0」は成り立たない。
    実数の積状態から <Z_0> を測ると、c_1 は小さいが 0 ではない（N=3、t=2、角度は乱数の種 5）。
    以前この仮説が成り立つように見えたのは、c_1 が小さく、n ≤ 160 では δ² の項がまだ勝っていたため。"""
    A, B = tn.tfim_parts(3)
    rng = np.random.default_rng(5)
    psi0 = _product_state(rng.uniform(0.3, 2.8, 3), np.zeros(3))
    c1 = tn.first_order_coefficient(A, B, psi0, tn.op_on(tn.Z, 0, 3), 2.0)
    assert abs(c1) > 5e-3, c1


def test_small_c1_of_real_states_is_specific_to_N3_t2() -> None:
    """実数の積状態で c_1 が小さかったのは、N=3・t=2 がたまたま共通の零点の近くだったため（一般の性質ではない）。
    (a) 同じ実数の状態でも、時刻を変えると |c_1| の最大は t=2 での値の5倍を超える（t=2 だけが特別に小さい）。
    (b) N=3 の実数の積状態では、c_1(t) が t = 1.9〜2.2 の間で符号を変える（状態によらない共通の零点）。"""
    A, B = tn.tfim_parts(3)
    Z0 = tn.op_on(tn.Z, 0, 3)
    rng = np.random.default_rng(5)
    ts = np.linspace(0.05, 6, 120)
    for _ in range(5):
        psi0 = _product_state(rng.uniform(0.3, 2.8, 3), np.zeros(3))
        c = [tn.first_order_coefficient(A, B, psi0, Z0, t) for t in ts]
        assert max(map(abs, c)) > 5 * abs(tn.first_order_coefficient(A, B, psi0, Z0, 2.0))
        c_lo = tn.first_order_coefficient(A, B, psi0, Z0, 1.9)
        c_hi = tn.first_order_coefficient(A, B, psi0, Z0, 2.2)
        assert c_lo * c_hi < 0, (c_lo, c_hi)


# ------------------------------------------------------------------ 指標ごとの指数 n* ∝ p^s
def test_exponent_depends_on_metric() -> None:
    """モデルの n*（連続的な予測）の p に対する指数が、指標と次数で予想どおりに変わる（N=2）：
    トレース距離 -1/(k+1)、不忠実度 -1/(2k+1)、局所的な量（Layden の条件で q=2）-1/3。許容幅 0.04。"""
    from dataclasses import asdict

    import analyze
    import exponents

    ps = [0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
    rows = [asdict(tn.run_point(2, 2.0, order, n, p)) for order in (1, 2) for p in [0.0] + ps for n in range(1, 61)]
    res = exponents.exponents(analyze.analyze(rows))
    got = {(r["metric"], r["order"]): r["s_model"] for r in res}
    for key in [("trace_dist", 1), ("trace_dist", 2), ("infidelity", 1), ("infidelity", 2), ("local_err", 1)]:
        assert abs(got[key] - exponents.EXPECTED[key]) < 0.04, f"{key}: {got[key]} と予想 {exponents.EXPECTED[key]:.3f}"
