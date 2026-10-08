"""S2 の結果のまとめ：収束の診断、合成データでの正解の取り戻し、形どうしの比較（PSIS-LOO）。

壊れたチェーン（対数尤度の中央値が、最も良いチェーンより大きく低いもの）を見つけて報告し、比較からは除く。
1つの回が読めなくても、ほかの回のまとめは続ける。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s2_report.py
入力: results/s2/*_draws.npz・*_meta.json（s2_fit.py）、*_modes.json（s2_map.py）
出力: results/s2/s2_report.csv（回ごとの診断と推定値）、s2_report.md（表）、compare_<データ>.csv（形の比較）
"""

from __future__ import annotations

import csv
import json
import sys
import traceback
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import noise_model_jax as nm  # noqa: E402

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent / "results" / "s2"
PAIRS = ["22-23", "142-143"]
BROKEN_GAP = 50.0          # 対数尤度の中央値が、最も良いチェーンよりこれ以上低いチェーンを「壊れた」とみなす
SHOW = ("ZI", "IZ", "IX", "ZX", "ZZ")


def chain_health(ll: np.ndarray, n_chain: int) -> tuple[list[float], list[int]]:
    """チェーンごとの対数尤度（合計）の中央値と、健全なチェーンの番号。"""
    tot = ll.sum(axis=1).reshape(n_chain, -1)
    med = [float(np.median(tot[c])) for c in range(n_chain)]
    best = max(med)
    good = [c for c in range(n_chain) if np.isfinite(med[c]) and med[c] > best - BROKEN_GAP]
    return med, good


def rhat_max(x: np.ndarray) -> float:
    """分割 R-hat の最大値（x の形は (chain, draw, ...)。ばらつきのない成分は除く）。"""
    import arviz as az
    x = x.reshape(x.shape[0], x.shape[1], -1)
    x = x[..., np.std(x.reshape(-1, x.shape[-1]), axis=0) > 0]
    if x.shape[0] < 2 or x.shape[-1] == 0:
        return float("nan")
    return float(np.nanmax(np.asarray(az.rhat(x))))


def summarize_run(tag: str) -> dict:
    meta = json.loads((OUT / f"{tag}_meta.json").read_text(encoding="utf-8"))
    d = np.load(OUT / f"{tag}_draws.npz")
    n_chain = meta["args"]["chains"]
    ll = d["log_lik"]
    med, good = chain_health(ll, n_chain)
    theta, p = d["theta"], d["p"]                                      # (chain, draw, 2, 15)、(chain, draw, 2)
    params = np.concatenate([theta.reshape(*theta.shape[:2], -1), p], axis=-1)
    row = {"run": tag, "data": meta["args"]["data"], "form": meta["args"]["form"], "drift": meta["args"]["drift"],
           "elapsed_min": round(meta["elapsed_s"] / 60, 1), "divergences": meta["divergences"],
           "tree_cap_frac": round(meta.get("tree_cap_fraction", float("nan")), 2),
           "chains": n_chain, "good_chains": len(good),
           "loglik_median_by_chain": " / ".join(f"{m:.1f}" if abs(m) < 1e6 else f"{m:.1e}" for m in med),
           "rhat_max_all": round(rhat_max(params), 3),
           "rhat_max_good": round(rhat_max(params[good]), 3) if len(good) >= 2 else float("nan")}
    modes_path = OUT / f"{tag}_modes.json"
    if modes_path.exists():
        modes = json.loads(modes_path.read_text(encoding="utf-8"))
        row["map_modes"] = len(modes)
        row["map_best_count"] = modes[0]["count"]
        row["map_second_gap"] = round(modes[1]["delta_from_best"], 2) if len(modes) > 1 else float("nan")
    flat_th = theta[good].reshape(-1, 2, 15)
    flat_p = p[good].reshape(-1, 2)
    for g, pair in enumerate(PAIRS):
        for lab in SHOW:
            k = nm.LABELS15.index(lab)
            if np.std(flat_th[:, g, k]) == 0 and np.all(flat_th[:, g, k] == 0):
                continue
            row[f"{pair}_{lab}"] = round(float(np.median(flat_th[:, g, k])), 4)
            row[f"{pair}_{lab}_sd"] = round(float(np.std(flat_th[:, g, k])), 4)
        row[f"{pair}_p"] = round(float(np.median(flat_p[:, g])), 4)
    # 制御の状態ごとの、標的の回転（ノートの式 (III-1)(III-2)）：制御 |0> は IX+ZX など、|1> は IX−ZX など
    for g, pair in enumerate(PAIRS):
        for ax, (li, lz) in (("X", ("IX", "ZX")), ("Y", ("IY", "ZY")), ("Z", ("IZ", "ZZ"))):
            a, b = flat_th[:, g, nm.LABELS15.index(li)], flat_th[:, g, nm.LABELS15.index(lz)]
            for name, v in (("c0", a + b), ("c1", a - b)):
                row[f"{pair}_{ax}_{name}"] = round(float(np.median(v)), 4)
                row[f"{pair}_{ax}_{name}_sd"] = round(float(np.std(v)), 4)
    if "sigma_drift" in d:
        row["sigma_drift"] = round(float(np.median(d["sigma_drift"][good])), 4)
    if meta.get("truth"):
        hits, total, missed = 0, 0, []
        for g, pair in enumerate(PAIRS):
            tr = meta["truth"][pair]
            checks = [(lab, v, flat_th[:, g, nm.LABELS15.index(lab)]) for lab, v in tr["theta"].items() if v != 0.0]
            checks.append(("p", tr["p"], flat_p[:, g]))
            for lab, v, s in checks:
                lo, hi = np.percentile(s, [5, 95])
                total += 1
                if lo <= v <= hi:
                    hits += 1
                else:
                    missed.append(f"{pair}:{lab}")
        row["truth_in_90pct"] = f"{hits}/{total}"
        row["truth_missed"] = ", ".join(missed)
        if "delta_job" in d:
            dj = d["delta_job"][good].reshape(-1, d["delta_job"].shape[-1])
            offs = meta["truth"]["22-23"]["job_offsets"]
            jobs = [jb[1] for jb in meta["jobs"]]
            jump = max(offs, key=lambda j: abs(offs[j]))
            order = list(np.argsort(-np.abs(dj.mean(axis=0))))
            row["jump_job_rank"] = order.index(jobs.index(jump)) + 1
            row["jump_delta"] = f"{dj[:, jobs.index(jump)].mean():+.4f}（正解 {offs[jump]:+.4f}）"
    return row, ll, good, n_chain


def compare(group: dict) -> list[dict]:
    """同じデータの回どうしを PSIS-LOO で比べる（健全なチェーンだけを使う）。"""
    import arviz as az
    idatas, skipped = {}, []
    for tag, (ll, good, n_chain) in group.items():
        lls = ll.reshape(n_chain, -1, ll.shape[-1])[good]
        idata = az.from_dict({"posterior": {"dummy": np.zeros(lls.shape[:2])}, "log_likelihood": {"y": lls}})
        try:
            az.loo(idata)                          # PSIS が計算できない回（点ごとの値がほぼ一定など）は比較から除く
            idatas[tag] = idata
        except Exception as e:
            skipped.append((tag, f"{type(e).__name__}: {e}", float(np.median(lls.sum(axis=-1)))))
    if len(idatas) < 2:
        return [], skipped
    # ArviZ 1.x の compare の表は有効数字で丸めるので、点ごとの elpd から自分で計算する
    loos = {tag: az.loo(idata, pointwise=True) for tag, idata in idatas.items()}
    elpd_i = {tag: np.asarray(l.elpd_i).ravel() for tag, l in loos.items()}
    best = max(loos, key=lambda t: float(loos[t].elpd))
    rows = []
    for rank, tag in enumerate(sorted(loos, key=lambda t: -float(loos[t].elpd))):
        diff_i = elpd_i[tag] - elpd_i[best]
        k = np.asarray(loos[tag].pareto_k).ravel()
        rows.append({"run": tag, "rank": rank, "elpd": round(float(loos[tag].elpd), 1), "se": round(float(loos[tag].se), 1),
                     "elpd_diff": round(float(diff_i.sum()), 1), "dse": round(float(np.sqrt(len(diff_i) * np.var(diff_i))), 1),
                     "points_k_gt_0.7": int(np.sum(k > 0.7)), "points": len(k)})
    return rows, skipped


def stacking_weights(elpd_i: np.ndarray) -> np.ndarray:
    """スタッキングの重み（Yao ら 2018）：点ごとの LOO 予測密度 exp(elpd_i) を重み w で混ぜたときの、対数の和を最大にする。
    elpd_i の形は (モデル数, 点の数)。重みは単体（0 以上、和が 1）の上で、ソフトマックスで表して最適化する。"""
    from scipy.optimize import minimize
    from scipy.special import logsumexp, softmax

    def neg(z):
        w = softmax(np.r_[0.0, z])
        return -np.sum(logsumexp(elpd_i + np.log(w)[:, None], axis=0))

    res = minimize(neg, np.zeros(elpd_i.shape[0] - 1), method="BFGS")
    return softmax(np.r_[0.0, res.x])


def stacking_section(groups: dict) -> list[str]:
    """F3s の、22–23 の差の符号が正の回と負の回を、スタッキングで合わせる。"""
    import arviz as az
    out = []
    for data, group in groups.items():
        pos, neg = f"{data}_F3s_D1_pos", f"{data}_F3s_D1_neg"
        if pos not in group or neg not in group:
            continue
        elpd_i, theta = [], []
        for tag in (pos, neg):
            ll, good, n_chain = group[tag]
            lls = ll.reshape(n_chain, -1, ll.shape[-1])[good]
            loo = az.loo(az.from_dict({"posterior": {"dummy": np.zeros(lls.shape[:2])}, "log_likelihood": {"y": lls}}), pointwise=True)
            elpd_i.append(np.asarray(loo.elpd_i).ravel())
            theta.append(np.load(OUT / f"{tag}_draws.npz")["theta"][good].reshape(-1, 2, 15))
        w = stacking_weights(np.array(elpd_i))
        out += ["", f"**{data}：F3s の差の符号（22–23）の、スタッキングによる合わせ方**", "",
                f"重み：正 {w[0]:.3f}、負 {w[1]:.3f}（elpd：正 {elpd_i[0].sum():.1f}、負 {elpd_i[1].sum():.1f}）", "",
                "| 成分 | 正の回の中央値 | 負の回の中央値 | 合わせた分布の中央値（90% 区間） |", "|---|---|---|---|"]
        rng = np.random.default_rng(0)
        n = min(len(theta[0]), len(theta[1]))
        pick = rng.random(n) < w[0]
        mixed = np.where(pick[:, None, None], theta[0][:n], theta[1][:n])
        for g, pair in enumerate(PAIRS):
            for lab in ("ZI", "IX", "ZX", "IZ", "ZZ"):
                k = nm.LABELS15.index(lab)
                lo, md_, hi = np.percentile(mixed[:, g, k], [5, 50, 95])
                out.append(f"| {pair} {lab} | {np.median(theta[0][:, g, k]):+.4f} | {np.median(theta[1][:, g, k]):+.4f} | "
                           f"{md_:+.4f}（{lo:+.4f}〜{hi:+.4f}） |")
            k1, k2 = nm.LABELS15.index("IZ"), nm.LABELS15.index("ZZ")
            ssum = mixed[:, g, k1] + mixed[:, g, k2]
            out.append(f"| {pair} IZ＋ZZ（和） | | | {np.median(ssum):+.4f}（{np.percentile(ssum, 5):+.4f}〜{np.percentile(ssum, 95):+.4f}） |")
    return out


def main() -> None:
    rows, groups = [], {}
    for meta_path in sorted(OUT.glob("*_meta.json")):
        tag = meta_path.name.removesuffix("_meta.json")
        if not (OUT / f"{tag}_draws.npz").exists():
            continue
        try:
            row, ll, good, n_chain = summarize_run(tag)
        except Exception:
            print(f"{tag}：まとめに失敗（飛ばす）")
            traceback.print_exc()
            continue
        rows.append(row)
        if len(good) >= 1:
            # 同じデータどうしだけを比べる（制御 |1> の直接の測定を加えた合成データは別のデータ）
            meta_args = json.loads((OUT / f"{tag}_meta.json").read_text(encoding="utf-8"))["args"]
            key = row["data"] + ("_c1" if meta_args.get("extra_c1") else "")
            groups.setdefault(key, {})[tag] = (ll, good, n_chain)

    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with (OUT / "s2_report.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    md = ["# S2 のまとめ（s2_report.py が自動で作成）", "",
          "| 回 | 健全なチェーン | R-hat 最大（全部／健全） | 発散 | 上限に達した割合 | MAP の山の数（一番高い山に着いた数、2番目との差） | 時間（分） |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['run']} | {r['good_chains']}/{r['chains']} | {r['rhat_max_all']} ／ {r['rhat_max_good']} | {r['divergences']} | "
                  f"{r['tree_cap_frac']} | {r.get('map_modes', '')}（{r.get('map_best_count', '')}、{r.get('map_second_gap', '')}） | {r['elapsed_min']} |")
    md += ["", "| 回 | 22–23 ZI | 22–23 IX | 22–23 ZX | 142–143 ZI | 142–143 IX | 142–143 ZX | p（22–23／142–143） | 揺らぎの大きさ | 正解の取り戻し |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        def v(key):
            return f"{r[key]:+.4f}±{r[key + '_sd']:.4f}" if key in r else "—"
        md.append(f"| {r['run']} | {v('22-23_ZI')} | {v('22-23_IX')} | {v('22-23_ZX')} | {v('142-143_ZI')} | {v('142-143_IX')} | "
                  f"{v('142-143_ZX')} | {r['22-23_p']:.4f}／{r['142-143_p']:.4f} | {r.get('sigma_drift', '—')} | "
                  f"{r.get('truth_in_90pct', '—')} {('跳びの検出 ' + str(r['jump_job_rank']) + ' 位') if 'jump_job_rank' in r else ''} |")
    md += ["", "**制御の状態ごとの、標的の回転（中央値±標準偏差、rad）：c0 は制御 |0>、c1 は制御 |1>**", "",
           "| 回 | 22–23 X c0 | 22–23 X c1 | 22–23 Z c0 | 22–23 Z c1 | 142–143 X c0 | 142–143 X c1 | 142–143 Z c0 | 142–143 Z c1 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        cells = [f"{r[k]:+.4f}±{r[k + '_sd']:.4f}" for k in (f"{p}_{a}_{c}" for p in PAIRS for a in ("X", "Z") for c in ("c0", "c1"))]
        md.append(f"| {r['run']} | " + " | ".join(cells) + " |")
    for data, group in groups.items():
        if len(group) < 2:
            continue
        try:
            cmp_rows, skipped = compare(group)
        except Exception:
            print(f"{data} の比較に失敗")
            traceback.print_exc()
            continue
        if not cmp_rows:
            continue
        with (OUT / f"compare_{data}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(cmp_rows[0]))
            w.writeheader()
            w.writerows(cmp_rows)
        md += ["", f"**{data} のデータでの形の比較（PSIS-LOO、健全なチェーンだけ。上ほど良い）**", "",
               "| 回 | 順位 | elpd | 一番良い回との差 | 差の標準誤差 | k̂ > 0.7 の点 |", "|---|---|---|---|---|---|"]
        for c in cmp_rows:
            md.append(f"| {c['run']} | {c['rank']} | {c['elpd']} | {c['elpd_diff']} | {c['dse']} | {c['points_k_gt_0.7']}/{c['points']} |")
        for tag, why, lp in skipped:
            md.append(f"| {tag} | 比較から除外 | （対数尤度の合計の中央値 {lp:.1f}） | PSIS-LOO が計算できない：{why[:60]} | | |")
    md += stacking_section(groups)
    (OUT / "s2_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
