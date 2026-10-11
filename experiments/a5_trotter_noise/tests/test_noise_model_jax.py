"""noise_model_jax（JAX の前向き計算）が、これまでの NumPy の計算（coherent_fits.py、trotter_noise.py）と一致することを確かめる。"""

import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import coherent_fits as cf  # noqa: E402
import noise_model_jax as nm  # noqa: E402
import trotter_noise as tn  # noqa: E402

NS = list(range(1, 15))


def _numpy_err(theta15, p, twirled):
    return cf.error_sup(nm.LABELS15, np.asarray(theta15), p, twirled)


def test_noiseless_matches_exact_trotter():
    for order in (1, 2):
        z = np.asarray(nm.trotter_z0(order, NS, nm.error_sup(jnp.zeros(15), 0.0, False)))
        ref = np.array([tn.run_point(2, 2.0, order, n, 0.0).z_exact + tn.run_point(2, 2.0, order, n, 0.0).z_trotter_part for n in NS])
        assert np.max(np.abs(z - ref)) < 1e-12


@pytest.mark.parametrize("twirled", [False, True])
@pytest.mark.parametrize("order", [1, 2])
def test_random_coherent_errors_match_numpy(order, twirled):
    rng = np.random.default_rng(10 * order + twirled)
    for _ in range(5):
        th = rng.normal(0, 0.03, 15)
        p = rng.uniform(0, 0.01)
        z_jax = np.asarray(nm.trotter_z0(order, NS, nm.error_sup(jnp.array(th), p, twirled)))
        z_np = cf.z0_curve(order, NS, _numpy_err(th, p, twirled))
        assert np.max(np.abs(z_jax - z_np)) < 1e-10


def test_rx_layer_error_matches_numpy():
    rng = np.random.default_rng(3)
    th = rng.normal(0, 0.03, 15)
    xe_th = rng.normal(0, 0.02, 15)
    x_err_np = cf.sup(cf.expm(-1j * sum(t * cf.PAULI2[l] for l, t in zip(nm.LABELS15, xe_th))))
    for order in (1, 2):
        z_np = cf.z0_curve(order, NS, _numpy_err(th, 0.002, False), x_err_np)
        z_jax = np.asarray(nm.trotter_z0(order, NS, nm.error_sup(jnp.array(th), 0.002, False), nm.sup(nm.coherent_unitary(jnp.array(xe_th)))))
        assert np.max(np.abs(z_jax - z_np)) < 1e-10


def test_probe_phase_slopes_match_numpy():
    ks = (0, 2, 4, 8, 12)
    th = nm.theta_from({"ZI": -0.017, "IX": 0.018, "ZX": -0.011, "IZ": 0.004})
    labels = nm.LABELS15
    err = nm.error_sup(jnp.array(th), 0.003, False)
    ref = cf.zprobe_slopes(labels, th, 0.003, ks)
    for target in (0, 1):
        e_ref, e_y = nm.probe_expectations(err, "Z", target, ks)
        slope = np.polyfit(ks, np.unwrap(np.arctan2(np.asarray(e_y), np.asarray(e_ref))), 1)[0]
        assert abs(slope - ref[target]) < 1e-10
    e_ref, e_y = nm.probe_expectations(err, "X", 1, ks)
    slope = np.polyfit(ks, np.unwrap(np.arctan2(np.asarray(e_y), np.asarray(e_ref))), 1)[0]
    assert abs(slope - cf.xprobe_slope(labels, th, 0.003, ks)) < 1e-10


def test_twirled_channel_is_trace_preserving_pauli_channel():
    th = jnp.array(np.random.default_rng(5).normal(0, 0.05, 15))
    S = nm.error_sup(th, 0.0, True)
    assert np.allclose(np.asarray(nm.VEC_I @ S), np.asarray(nm.VEC_I))      # トレースを保つ
    # パウリ通路なので、パウリ行列の vec は固有ベクトル（向きを混ぜない）
    for P in np.asarray(nm.PAULI16):
        v = P.reshape(-1)
        w = np.asarray(S) @ v
        lam = (v.conj() @ w) / (v.conj() @ v)
        assert np.allclose(w, lam * v)


def test_gradient_is_finite():
    def f(th):
        return jnp.sum(nm.trotter_z0(1, NS, nm.error_sup(th, 0.003, False)))
    g = jax.grad(f)(jnp.full(15, 0.01))
    assert np.all(np.isfinite(np.asarray(g))) and np.max(np.abs(np.asarray(g))) > 0


def test_synthetic_job_statistics():
    truth = nm.default_truth()["142-143"]
    rng = np.random.default_rng(0)
    job = nm.simulate_trotter_job(truth, "a", 1, False, NS, 200000, rng)
    assert np.max(np.abs(job["z"] - job["z_true"])) < 5 * np.max(job["sem"])
    truth.job_offsets["b"] = 0.05
    shifted = nm.simulate_trotter_job(truth, "b", 1, False, NS, 200000, rng)
    assert np.max(np.abs(shifted["z_true"] - job["z_true"])) > 0.01                # 揺らぎが値を動かす


def test_real_data_loader_and_synthetic_copy():
    import a5_data
    trotter, probes = a5_data.load_all()
    assert len(trotter) == 21 and sum(len(j["n"]) for j in trotter) == 152
    assert len(probes) == 42 and all(o["sigma"] > 0 for o in probes)
    # 実データの雑音なしのトロッター値は、JAX の計算と一致する
    for j in trotter:
        z = np.asarray(nm.trotter_z0(j["order"], j["n"], nm.error_sup(jnp.zeros(15), 0.0, False)))
        assert np.max(np.abs(z - j["z_trot"])) < 1e-9
    truths = nm.default_truth()
    syn_t, syn_p = a5_data.synthetic_like(trotter, probes, truths, np.random.default_rng(1))
    assert len(syn_t) == len(trotter) and len(syn_p) == len(probes)
    resid = np.concatenate([(j["z"] - j["z_true"]) / j["sem"] for j in syn_t])
    assert 0.5 < np.std(resid) < 1.5                                      # 合成データのばらつきが実データの統計誤差に合う


def test_amplitude_damping():
    """振幅減衰（T1）の超演算子：クラウス演算子からの直接の計算と一致し、トレースを保ち、|11> を |00> の側へ移す。
    ツイリングすると |0> への偏りが消える。gamma=0 は減衰なしと同じ。"""
    g = 0.1
    k0, k1 = np.diag([1, np.sqrt(1 - g)]), np.array([[0, np.sqrt(g)], [0, 0]])
    ref = sum(np.kron(np.kron(a, b), np.conj(np.kron(a, b))) for a in (k0, k1) for b in (k0, k1))
    D = np.asarray(nm.damp_sup(g))
    assert np.allclose(D, ref)
    assert np.allclose(np.asarray(nm.VEC_I) @ D, np.asarray(nm.VEC_I))
    rho11 = np.zeros((4, 4)); rho11[3, 3] = 1
    assert np.allclose(np.diag((D @ rho11.reshape(-1)).reshape(4, 4)).real, [0.01, 0.09, 0.09, 0.81])
    rho00 = np.zeros((4, 4)); rho00[0, 0] = 1
    T = np.asarray(nm.pauli_twirl(jnp.asarray(D)))
    assert not np.allclose(T @ rho00.reshape(-1), rho00.reshape(-1))          # ツイリング後は |00> も動く（偏りのない通路）
    th = jnp.full(15, 0.01)
    for tw in (False, True):
        assert np.allclose(np.asarray(nm.error_sup(th, 0.002, tw)), np.asarray(nm.error_sup(th, 0.002, tw, 0.0)))
