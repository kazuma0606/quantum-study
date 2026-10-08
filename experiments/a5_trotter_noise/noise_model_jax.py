"""雑音のモデリング（docs/a5_modeling_plan.md の S1）：JAX による前向き計算と、正解の分かる合成データの生成。

coherent_fits.py（NumPy）と同じ回路・同じ規約を、自動微分できる形で書き直したもの。NUTS・SVI・SBI の共通の部品。
  - 量子ビットの順：行列は「左が量子ビット 0（制御）、右が量子ビット 1（標的）」（trotter_noise.op_on と同じ）
  - 超演算子は行優先の vec：ρ → UρU† は kron(U, conj(U))
  - 各 CX の直後に、コヒーレントな誤差 E = exp(-i Σ_k θ_k P_k)（P は 15 個の2量子ビットのパウリ）と脱分極 p を入れる
  - ツイリングありでは、E を確率 |c_P|^2 のパウリ通路に置き換える（E = Σ_P c_P P）
  - 2次の分解は、変換後の回路と同じく隣り合う RX(d) を RX(2d) にまとめた形：X(d)、[ZZ・X(2d)]×(n-1)、ZZ、X(d)
n ごとの段数の違いは、長さ NMAX の固定の繰り返しの中で「n を超えた段は何もしない」とマスクして表す（微分できるようにするため）。
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np
from jax.scipy.linalg import expm

jax.config.update("jax_enable_x64", True)

T = 2.0
NMAX = 14
_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_P1 = {"I": _I2, "X": _X, "Y": _Y, "Z": _Z}
LABELS15 = [a + b for a, b in itertools.product("IXYZ", repeat=2) if a + b != "II"]   # 1文字目が制御、2文字目が標的
LABELS16 = ["II"] + LABELS15
PAULI16 = jnp.array(np.stack([np.kron(_P1[l[0]], _P1[l[1]]) for l in LABELS16]))
CX = jnp.array(np.kron(np.diag([1, 0]), _I2) + np.kron(np.diag([0, 1]), _X), dtype=complex)
Z0 = jnp.array(np.kron(_Z, _I2))
VEC_I = jnp.eye(4, dtype=complex).reshape(-1)
RHO00 = jnp.zeros(16, dtype=complex).at[0].set(1.0)


def sup(U):
    """ρ → U ρ U† の超演算子（行優先の vec）。"""
    return jnp.kron(U, jnp.conj(U))


def depol_sup(p):
    return (1 - p) * jnp.eye(16, dtype=complex) + p * jnp.outer(VEC_I, VEC_I) / 4


def coherent_unitary(theta15):
    """E = exp(-i Σ_k θ_k P_k)。theta15 は LABELS15 の順の15個。"""
    H = jnp.einsum("k,kij->ij", theta15.astype(complex), PAULI16[1:])
    return expm(-1j * H)


def error_sup(theta15, p, twirled: bool):
    """CX の直後に入れる誤差の超演算子（コヒーレントな誤差のあとに脱分極）。"""
    E = coherent_unitary(theta15)
    if twirled:
        c = jnp.einsum("kij,ji->k", PAULI16, E) / 4                 # c_P = tr(P E) / 4
        S = jnp.einsum("k,kab->ab", jnp.abs(c) ** 2, jax.vmap(sup)(PAULI16))
    else:
        S = sup(E)
    return depol_sup(p) @ S


def _rx(theta):
    return jnp.cos(theta / 2) * _I2 - 1j * jnp.sin(theta / 2) * _X


def _rz_target(theta):
    return jnp.kron(_I2, jnp.diag(jnp.array([jnp.exp(-0.5j * theta), jnp.exp(0.5j * theta)])))


def trotter_z0(order: int, ns, err, x_err=None):
    """各 n の <Z_0>。err は CX の直後、x_err は RX の層の直後の誤差の超演算子（None なら誤差なし）。"""
    ns = jnp.asarray(ns)
    cx_e = err @ sup(CX)
    xe = jnp.eye(16, dtype=complex) if x_err is None else x_err

    def one(n):
        d = T / n
        zz = cx_e @ sup(_rz_target(2 * d)) @ cx_e
        x2 = xe @ sup(jnp.kron(_rx(2 * d), _rx(2 * d)))
        x1 = xe @ sup(jnp.kron(_rx(d), _rx(d)))
        rho = RHO00 if order == 1 else x1 @ RHO00

        def body(rho, k):
            if order == 1:
                new = x2 @ (zz @ rho)
            else:
                last = jnp.where(k == n - 1, 1.0, 0.0)
                new = (last * x1 + (1 - last) * x2) @ (zz @ rho)
            return jnp.where(k < n, new, rho), None

        rho, _ = jax.lax.scan(body, rho, jnp.arange(NMAX))
        return jnp.real(jnp.trace(Z0 @ rho.reshape(4, 4)))

    return jax.vmap(one)(ns)


def probe_expectations(err, axis: str, target: int, ks, control_one: bool = False, unflip: bool = False):
    """hardware_zprobe.py の回路（CX・CX を k 回）の期待値 (<基準の基底>, <Y>) を各 k について返す。
    axis="Z"：target を |+> にして X と Y で測る。axis="X"：|0> のまま Z と Y で測る。
    control_one=True：最初に制御（量子ビット 0）を X で |1> にしておく（制御が |1> のときの標的の回転を見る。
    target=1 で使う。CX のたびに標的が反転するが、CX の組では理想的には元に戻る）。
    unflip=True：各 CX のあとに標的へ X をかけて反転を戻す（制御が |1> のとき、標的の Z 回転の誤差は
    反転のたびにエコーのように打ち消されて見えないので、反転を戻して Z 回転をためる。10/9 に確認）。"""
    cx_e = err @ sup(CX)
    if unflip:
        cx_e = sup(jnp.array(np.kron(_I2, _X))) @ cx_e
    pair = cx_e @ cx_e
    H1 = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    Ht = np.kron(H1, _I2) if target == 0 else np.kron(_I2, H1)
    rho_start = sup(jnp.array(np.kron(_X, _I2))) @ RHO00 if control_one else RHO00
    rho0 = sup(jnp.array(Ht)) @ rho_start if axis == "Z" else rho_start
    ref_op = _X if axis == "Z" else _Z
    op_ref = jnp.array(np.kron(ref_op, _I2) if target == 0 else np.kron(_I2, ref_op))
    op_y = jnp.array(np.kron(_Y, _I2) if target == 0 else np.kron(_I2, _Y))
    kmax = int(max(ks))

    def body(rho, _):
        return pair @ rho, rho

    _, rhos = jax.lax.scan(body, rho0, jnp.arange(kmax + 1))     # rhos[k] = k 回くり返したあと
    sel = rhos[jnp.asarray(ks)]
    R = sel.reshape(-1, 4, 4)
    e_ref = jnp.real(jnp.einsum("ij,kji->k", op_ref, R))
    e_y = jnp.real(jnp.einsum("ij,kji->k", op_y, R))
    return e_ref, e_y


# ---------------------------------------------------------------- 合成データ

@dataclass
class PairTruth:
    """1組の量子ビットの「正解」のパラメータ（合成データ用）。"""
    theta15: np.ndarray                     # LABELS15 の順のコヒーレントな回転（rad）
    p: float                                # CNOT ごとの脱分極
    drift_label: str = "ZI"                 # ジョブごとの揺らぎを足す項
    job_offsets: dict = field(default_factory=dict)   # ジョブ名 → その項へのずれ（rad）


def theta_from(labels_values: dict) -> np.ndarray:
    th = np.zeros(15)
    for lab, v in labels_values.items():
        th[LABELS15.index(lab)] = v
    return th


def simulate_trotter_job(truth: PairTruth, job: str, order: int, twirled: bool, ns, shots: int, rng: np.random.Generator):
    """1本のジョブのトロッター回路の測定を、ショットの統計まで含めて作る（読み出しの誤りは補正済みと見なす）。"""
    th = truth.theta15.copy()
    th[LABELS15.index(truth.drift_label)] += truth.job_offsets.get(job, 0.0)
    z_true = np.asarray(trotter_z0(order, ns, error_sup(jnp.array(th), truth.p, twirled)))
    p0 = np.clip((1 + z_true) / 2, 0, 1)
    z_obs = 2 * rng.binomial(shots, p0) / shots - 1
    sem = np.sqrt(np.maximum(1 - z_obs**2, 1e-6) / shots)
    return {"job": job, "order": order, "twirled": twirled, "n": np.asarray(ns), "z": z_obs, "sem": sem, "z_true": z_true}


def default_truth() -> dict[str, PairTruth]:
    """これまでの当てはめ（coherent_fits.py の CZ 型）に近い値を、合成データの既定の正解にする。"""
    return {
        "22-23": PairTruth(theta_from({"ZI": -0.017, "IX": 0.018, "ZX": -0.011}), 0.0046),
        "142-143": PairTruth(theta_from({"ZI": -0.010, "IX": 0.033, "ZX": -0.003}), 0.0035),
    }
