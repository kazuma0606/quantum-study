"""S2 の結果のまとめ：収束の診断、合成データでの正解の取り戻し、形どうしの比較（PSIS-LOO）。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s2_report.py
入力: results/s2/*_draws.npz と *_meta.json（s2_fit.py の出力）
出力: results/s2/s2_report.csv（実行ごとの診断と取り戻しの結果）と、画面への要約
"""

from __future__ import annotations

import csv
import json
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import noise_model_jax as nm  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)
OUT = Path(__file__).resolve().parent / "results" / "s2"
PAIRS = ["22-23", "142-143"]


def rhat_max(x: np.ndarray) -> float:
    """分割 R-hat の最大値（x の形は (chain, draw, ...)）。"""
    import arviz as az
    return float(np.nanmax(np.asarray(az.rhat(x.reshape(x.shape[0], x.shape[1], -1)))))


def main() -> None:
    import arviz as az
    rows, loo_inputs = [], {}
    for meta_path in sorted(OUT.glob("*_meta.json")):
        tag = meta_path.name.removesuffix("_meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        d = np.load(OUT / f"{tag}_draws.npz")
        theta, p = d["theta"], d["p"]                       # (chain, draw, 2, 15), (chain, draw, 2)
        row = {"run": tag, "elapsed_s": round(meta["elapsed_s"]), "divergences": meta["divergences"],
               "rhat_max": rhat_max(np.concatenate([theta.reshape(*theta.shape[:2], -1), p], axis=-1))}
        flat_th = theta.reshape(-1, 2, 15)
        flat_p = p.reshape(-1, 2)
        if meta["truth"]:
            # 正解の取り戻し：各組の、正解の値が 0 でない成分と p について、90% 区間に正解が入るか
            hits, total, worst = 0, 0, ""
            for g, pair in enumerate(PAIRS):
                tr = meta["truth"][pair]
                for lab, v in tr["theta"].items():
                    if v == 0.0:
                        continue
                    k = nm.LABELS15.index(lab)
                    lo, hi = np.percentile(flat_th[:, g, k], [5, 95])
                    total += 1
                    hits += lo <= v <= hi
                    if not lo <= v <= hi:
                        worst += f"{pair}:{lab} 正解 {v:+.4f} 区間 [{lo:+.4f}, {hi:+.4f}]; "
                lo, hi = np.percentile(flat_p[:, g], [5, 95])
                total += 1
                hits += lo <= tr["p"] <= hi
                if not lo <= tr["p"] <= hi:
                    worst += f"{pair}:p 正解 {tr['p']:.4f} 区間 [{lo:.4f}, {hi:.4f}]; "
            row["truth_in_90pct"] = f"{hits}/{total}"
            row["missed"] = worst
            # 跳んだジョブを見抜けるか（ずれの事後平均の大きさの順位）
            if "delta_job" in d:
                dj = d["delta_job"].reshape(-1, d["delta_job"].shape[-1])
                offs = meta["truth"]["22-23"]["job_offsets"]
                jobs = [jb[1] for jb in meta["jobs"]]
                jump = max(offs, key=lambda j: abs(offs[j]))
                order = np.argsort(-np.abs(dj.mean(axis=0)))
                row["jump_job_rank"] = int(list(order).index(jobs.index(jump))) + 1
                row["jump_delta_mean"] = float(dj[:, jobs.index(jump)].mean())
                row["jump_delta_true"] = offs[jump]
        # 推定値（事後中央値）
        for g, pair in enumerate(PAIRS):
            for lab in ("ZI", "IZ", "IX", "ZX", "ZZ"):
                k = nm.LABELS15.index(lab)
                row[f"{pair}_{lab}"] = float(np.median(flat_th[:, g, k]))
            row[f"{pair}_p"] = float(np.median(flat_p[:, g]))
        if "sigma_drift" in d:
            row["sigma_drift"] = float(np.median(d["sigma_drift"]))
        rows.append(row)
        loo_inputs.setdefault(meta["args"]["data"], {})[tag] = d["log_lik"]

    # 形どうしの比較（同じデータに対する PSIS-LOO）
    for data, lls in loo_inputs.items():
        if len(lls) < 2:
            continue
        idatas = {}
        for tag, ll in lls.items():
            n_chain = json.loads((OUT / f"{tag}_meta.json").read_text(encoding="utf-8"))["args"]["chains"]
            idatas[tag] = az.from_dict({"posterior": {"dummy": np.zeros((n_chain, ll.shape[0] // n_chain))},
                                        "log_likelihood": {"y": ll.reshape(n_chain, -1, ll.shape[-1])}})
        cmp = az.compare(idatas)
        print(f"\n{data} のデータでの比較（PSIS-LOO、上ほど良い）")
        print(cmp)
        cmp.to_csv(OUT / f"compare_{data}.csv")

    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with (OUT / "s2_report.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
