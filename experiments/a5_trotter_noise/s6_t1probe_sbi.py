"""S6 の補助：T1 専用の回路だけを読むニューラル事後推定（SBI、NPE）で、ショット数ごとの「見分けられる割合」を出す。

NUTS（s2_fit.py）は1回の当てはめに約1時間かかるので、乱数の種を数百に増やして「T1 ありとなしを見分けられる割合」を
出すことはできない（10/14 の監査の指摘：1000 ショットの1回の試しでは必要なショット数は決まらない）。そこで、
T1 専用の回路のデータ → γ の事後分布、をニューラルネット（正規化フロー）に一度学ばせ、合成データ1組あたり一瞬で
事後分布を出せるようにする。

シミュレータ（22–23 の組、回転は real_F5_D1_t1_os_hw1_long の事後平均に固定）
  パラメータ（6個、事前分布はすべて一様）：γ ∈ [0, 0.004]（CNOT ごとの振幅減衰。0 を含む）、p ∈ [0.0005, 0.005]（脱分極）、
    読み出しの誤り e01・e10 を制御・標的の量子ビットごとに ∈ [0, 0.08]
  データ（20 個）：制御を |0>・|1> に準備し、CX の組を k = 2, 4, 8, 16, 24 回、2つの量子ビットの生の <Z>（読み出しの誤りを含む）。
    2つの量子ビットは同じショットで同時に測るので、4通りの同時の結果を多項分布で引いてから集計する（10/15 の監査で直した。
    それ以前の結果 t1probe_sbi_s0〜s2 は、2つを独立な二項分布で作っていた）。
    ショットの二項分布のばらつきに、実データ並みの余分なばらつき（統計誤差の 1.35 倍、s2_fit.py の --syn-noise と同じ）を足す
限界：回転は固定、ほかの回路（トロッター回路など）は読まない。混ぜたジョブ全体を当てはめる NUTS より単純なので、
  見分けられる割合はやや楽観的に出る可能性がある。NUTS の結果（第2段、種2つ）と並べて確かめる。

見分けの判定：事後分布の中央値が γ = 0.0009（22–23 の当てはめの値の約半分）を超えたら「T1 あり」と判定する。
  T1 ありの世界（γ = 0.00179、0.00086）で「T1 あり」と判定した割合（検出率）と、T1 なしの世界（γ = 0）で「T1 あり」と
  判定した割合（誤検出率）を、ショット数ごとに出す。あわせて γ の 90% 区間の幅と、区間に正解が入る割合も出す。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s6_t1probe_sbi.py --shots 500 1000 2000 3000 --sims 200000
出力: results/s6/t1probe_sbi.md と .json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import noise_model_jax as nm  # noqa: E402
import s2_fit  # noqa: E402

OUT = Path(__file__).resolve().parent / "results" / "s6"
NAMES = ["gamma", "p", "e01_c", "e10_c", "e01_t", "e10_t"]
LOW = np.array([0.0, 0.0005, 0.0, 0.0, 0.0, 0.0])
HIGH = np.array([0.004, 0.005, 0.08, 0.08, 0.08, 0.08])
KS = (2, 4, 8, 16, 24)
NOISE = 1.35
THRESH = 0.0009
# 2つ目の判定（10/15 に追加）：90% 区間の下の端（5% 点）が LO_THRESH を超えたら「T1 あり」。中央値の判定では、しきい値 0.0009 が
# 「小さい T1（0.00086）」の正解とほぼ同じで、その世界の検出率が意味を持たなかったため
LO_THRESH = 0.0003
WORLDS = {"T1 なし（γ=0）": 0.0, "T1 小（γ=0.00086）": 0.00086, "T1 あり（γ=0.00179）": 0.00179}
TRUE_REST = {"p": 0.00173, "e01": 0.01, "e10": 0.03}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def fixed_theta(pair: int = 0) -> jnp.ndarray:
    """組（0 = 22–23、1 = 142–143）の回転を、T1＋誤差棒＋実機の当てはめの事後平均に固定する。"""
    d = np.load(s2_fit.OUT / "real_F5_D1_t1_os_hw1_long_draws.npz")
    return jnp.asarray(d["theta"].reshape(-1, 2, 15).mean(0)[pair])


# 世界の正解の p（脱分極）：合成データの予行演習の正解（real_F5_D1_t1_os_hw1_long の事後平均）と同じ値
TRUE_P = {0: 0.00173, 1: 0.00207}


ROT_NAMES = [f"{b}_{a}" for b in ("c0", "c1") for a in "xyz"]
AXES = (("IX", "ZX"), ("IY", "ZY"), ("IZ", "ZZ"))


def rotation_prior(pair: int, k_sd: float = 4.0):
    """回転も推定する版（--free-rot）の事前分布：当てはめの事後分布の平均 ± k_sd × 標準偏差の箱（制御 |0>・|1> の X・Y・Z）。"""
    d = np.load(s2_fit.OUT / "real_F5_D1_t1_os_hw1_long_draws.npz")
    r = np.concatenate([d["rot_c0"].reshape(-1, 2, 3)[:, pair], d["rot_c1"].reshape(-1, 2, 3)[:, pair]], axis=1)
    m, sd = r.mean(0), r.std(0)
    return m, m - k_sd * sd, m + k_sd * sd


def theta_with_rotations(theta_fixed, rot):
    """固定の回転（ZI などはそのまま）の、制御 |0>・|1> の X・Y・Z の回転だけを rot（6 個）で置き換える（F5 の置き方）。"""
    th = theta_fixed
    for ax, (li, lz) in enumerate(AXES):
        th = th.at[nm.LABELS15.index(li)].set((rot[ax] + rot[3 + ax]) / 2)
        th = th.at[nm.LABELS15.index(lz)].set((rot[ax] - rot[3 + ax]) / 2)
    return th


def make_expect(theta, free_rot: bool = False):
    """パラメータ → 読み出しの結果の4通り（00, 01, 10, 11。左が制御）の確率。準備（|0>・|1>）× k（5通り）× 4 の 40 個。
    2つの量子ビットは同じショットで同時に測るので、本当の状態の同時確率に、量子ビットごとの読み出しの誤りの行列
    M = [[1−e01, e10], [e01, 1−e10]]（行が読んだ値、列が本当の値）のテンソル積をかける（10/15 の監査：制御と標的を
    別々の二項分布で作ると、2つの値の相関が消える）。"""
    def conf(e01, e10):
        return jnp.array([[1 - e01, e10], [e01, 1 - e10]])

    def one(par):
        g, p, e01c, e10c, e01t, e10t = par[:6]
        th = theta_with_rotations(theta, par[6:12]) if free_rot else theta
        err = nm.error_sup(th, p, False, g)
        M = jnp.kron(conf(e01c, e10c), conf(e01t, e10t))
        out = []
        for c1 in (False, True):
            P = nm.t1_probe_probs(err, c1, KS)              # (k, 4)
            out.append(P @ M.T)
        return jnp.concatenate(out).reshape(-1)
    return jax.jit(jax.vmap(one))


ZC = np.array([1, 1, -1, -1])       # 制御の Z の値（00, 01, 10, 11 の順、左が制御）
ZT = np.array([1, -1, 1, -1])       # 標的の Z の値


def simulate(expect, pars: np.ndarray, shots: int, rng: np.random.Generator, batch: int = 4096) -> np.ndarray:
    """4通りの同時の結果を多項分布で引き、制御・標的の <Z> を集計する（データは 20 個：準備 × k × 量子ビット）。
    実データ並みの余分なばらつき（統計誤差の 1.35 倍）も足す。"""
    xs = []
    for i in range(0, len(pars), batch):
        P = np.asarray(expect(jnp.asarray(pars[i:i + batch]))).reshape(-1, 2, len(KS), 4)
        P = np.clip(P, 0, None)
        P = P / P.sum(-1, keepdims=True)
        n = rng.multinomial(shots, P.reshape(-1, 4)).reshape(P.shape) / shots
        zc, zt = n @ ZC, n @ ZT                              # (batch, 準備, k)
        m = np.stack([zc, zt], axis=-1).reshape(len(P), -1)   # 準備 → k → 量子ビット の順
        sig = np.sqrt(np.maximum(1 - m**2, 1e-6) / shots)
        xs.append(m + rng.standard_normal(m.shape) * sig * np.sqrt(NOISE**2 - 1))
    return np.concatenate(xs)


def main() -> None:
    global KS, NAMES, LOW, HIGH
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, nargs="+", default=[500, 1000, 2000, 3000])
    ap.add_argument("--sims", type=int, default=200000)
    ap.add_argument("--max-epochs", type=int, default=300)
    ap.add_argument("--n-test", type=int, default=500, help="世界ごとの合成データの組数")
    ap.add_argument("--sbc", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="t1probe_sbi")
    ap.add_argument("--ks", type=int, nargs="+", default=list(KS), help="CX の組の回数の並び（既定 2 4 8 16 24）")
    ap.add_argument("--free-rot", action="store_true",
                    help="回転（制御 |0>・|1> の X・Y・Z の6個）も推定する。事前分布は当てはめの平均 ± 4 標準偏差の箱")
    ap.add_argument("--pair", type=int, choices=[0, 1], default=0,
                    help="回転と脱分極の条件をどちらの組にするか（0 = 22–23、1 = 142–143）")
    args = ap.parse_args()
    KS = tuple(args.ks)
    rot_mean = None
    if args.free_rot:
        rot_mean, rlo, rhi = rotation_prior(args.pair)
        NAMES = NAMES + ROT_NAMES
        LOW, HIGH = np.r_[LOW, rlo], np.r_[HIGH, rhi]
    import torch
    from sbi.inference import NPE
    from sbi.utils import BoxUniform
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    OUT.mkdir(parents=True, exist_ok=True)
    # 保存名に組を入れる（同じ --tag で組だけ変えると上書きされるため。10/17 の監査）。10/16 までの結果は、入れる前の名前のまま
    pair_name = ["22-23", "142-143"][args.pair]
    stem = f"{args.tag}_pair{pair_name}"
    expect = make_expect(fixed_theta(args.pair), args.free_rot)
    TRUE_REST["p"] = TRUE_P[args.pair]
    log(f"組の条件：{pair_name}（回転は{'推定する（6個）' if args.free_rot else '当てはめの事後平均に固定'}、"
        f"正解の p = {TRUE_REST['p']}）、k = {KS}")
    prior = BoxUniform(torch.tensor(LOW, dtype=torch.float32, device=dev), torch.tensor(HIGH, dtype=torch.float32, device=dev),
                       device=dev)
    rng = np.random.default_rng(args.seed)
    results = {"args": vars(args), "device": dev, "by_shots": {}}
    for shots in args.shots:
        t0 = time.time()
        log(f"{shots} ショット：シミュレーション {args.sims} 回")
        th = LOW + (HIGH - LOW) * rng.random((args.sims, len(NAMES)))
        xs = simulate(expect, th, shots, rng)
        log(f"{shots} ショット：シミュレーション完了（{time.time() - t0:.0f} 秒）。学習（{dev}）")
        inf = NPE(prior=prior, density_estimator="nsf", device=dev)
        inf.append_simulations(torch.tensor(th, dtype=torch.float32), torch.tensor(xs, dtype=torch.float32))
        est = inf.train(training_batch_size=2048, max_num_epochs=args.max_epochs, show_train_summary=False)
        post = inf.build_posterior(est)
        # 学習済みの推定器を保存する（判定の決まりを変えて計算し直すとき、学習し直さずに済むように）
        import pickle
        with (OUT / f"{stem}_{shots}_posterior.pkl").open("wb") as fh:
            pickle.dump(post, fh)
        log(f"{shots} ショット：学習完了（{time.time() - t0:.0f} 秒、エポック {inf._summary['epochs_trained'][-1]}）")

        def draws(x, n=1000):
            return post.sample((n,), x=torch.tensor(x, dtype=torch.float32, device=dev),
                               show_progress_bars=False).cpu().numpy()

        # SBC：事前分布から正解を引き、γ の 68%・90% 区間に正解が入る割合
        th_s = LOW + (HIGH - LOW) * rng.random((args.sbc, len(NAMES)))
        x_s = simulate(expect, th_s, shots, rng)
        cov = {68: [], 90: []}
        for i in range(args.sbc):
            s = draws(x_s[i], 500)
            for lv, (lo, hi) in ((68, (16, 84)), (90, (5, 95))):
                a, b = np.percentile(s, [lo, hi], axis=0)
                cov[lv].append((a <= th_s[i]) & (th_s[i] <= b))
        sbc = {lv: dict(zip(NAMES, np.mean(v, axis=0).round(3).tolist())) for lv, v in cov.items()}
        log(f"{shots} ショット：SBC γ の 68%・90% 区間の当たり率 {sbc[68]['gamma']:.3f}・{sbc[90]['gamma']:.3f}")

        # 3つの世界で、見分けられる割合
        worlds = {}
        for wname, g in WORLDS.items():
            row = [g, TRUE_REST["p"], TRUE_REST["e01"], TRUE_REST["e10"], TRUE_REST["e01"], TRUE_REST["e10"]]
            if args.free_rot:
                row += list(rot_mean)              # 世界の正解の回転は、固定の版と同じ当てはめの平均
            par = np.array([row] * args.n_test)
            x_w = simulate(expect, par, shots, rng)
            med, lo, hi, inside = [], [], [], []
            for i in range(args.n_test):
                s = draws(x_w[i])[:, 0]
                a, m, b = np.percentile(s, [5, 50, 95])
                med.append(m), lo.append(a), hi.append(b), inside.append(a <= g <= b)
            med, lo, hi = map(np.array, (med, lo, hi))
            worlds[wname] = {"gamma_true": g, "detect_rate": float(np.mean(med > THRESH)),
                             "detect_rate_lo": float(np.mean(lo > LO_THRESH)),
                             "lo5": lo.round(6).tolist(), "med": med.round(6).tolist(), "hi95": hi.round(6).tolist(),
                             "median_of_median": float(np.median(med)), "width90_median": float(np.median(hi - lo)),
                             "coverage90": float(np.mean(inside))}
            log(f"{shots} ショット・{wname}：「T1 あり」と判定 {worlds[wname]['detect_rate']:.3f}"
                f"（区間の下の端 > {LO_THRESH} の判定では {worlds[wname]['detect_rate_lo']:.3f}）、"
                f"γ の中央値 {worlds[wname]['median_of_median']:.5f}、90% 区間の幅 {worlds[wname]['width90_median']:.5f}、"
                f"正解が区間に入る割合 {worlds[wname]['coverage90']:.3f}")
        results["by_shots"][str(shots)] = {"sbc": sbc, "worlds": worlds, "seconds": time.time() - t0,
                                           "qpu_s_estimate": 2.0 + 3e-4 * 2 * len(KS) * shots}
        (OUT / f"{stem}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# T1 専用の回路：ショット数ごとの見分けられる割合（SBI）", "",
             f"{pair_name} の組、回転は固定。判定：事後分布の中央値が γ = {THRESH} を超えたら「T1 あり」。世界ごとに {args.n_test} 組。"
             "QPU 秒は T1 専用の回路だけの見積もり（2 秒 ＋ 0.3 ms × 回路 10 本 × ショット）。", "",
             f"判定率は「中央値 > {THRESH}」／「90% 区間の下の端 > {LO_THRESH}」の2通り。",  "",
             "| ショット | QPU 秒 | " + " | ".join(f"{w}：判定率" for w in WORLDS) + " | γ=0.00179 の 90% 区間の幅 | SBC γ（68%・90%） |",
             "|---|---|" + "---|" * len(WORLDS) + "---|---|"]
    for sh, r in results["by_shots"].items():
        w = r["worlds"]
        lines.append(f"| {sh} | {r['qpu_s_estimate']:.0f} | "
                     + " | ".join(f"{w[n]['detect_rate']:.3f}／{w[n]['detect_rate_lo']:.3f}" for n in WORLDS)
                     + f" | {w['T1 あり（γ=0.00179）']['width90_median']:.5f} | {r['sbc'][68]['gamma']:.2f}・{r['sbc'][90]['gamma']:.2f} |")
    (OUT / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log("\n".join(lines))


if __name__ == "__main__":
    main()
