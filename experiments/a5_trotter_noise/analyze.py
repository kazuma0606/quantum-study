"""sweep.py の CSV から、条件ごとの最適な分割数 n* を求め、モデルによる予測と比べて CSV に書き出す。

モデル：誤差 ≈ a / n^q ＋ b p n
  第1項（トロッター誤差）：雑音なし（p = 0）の行から、両対数の傾きで q と a を当てはめる。
          （状態全体の不忠実度は誤差の2乗に比例するので q ≈ 2×次数、局所的な量の誤差は q ≈ 次数 になるはず）
  第2項（雑音）：一番弱い雑音 p_min の行と p = 0 の行の差から、(差) ≈ b p n の b を当てはめる。
  予測：d/dn = 0 から n* = (q a / (b p))^{1/(q+1)}。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/analyze.py results/sweep_….csv
出力: 同じ名前の _optimum.csv
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

METRICS = ("infidelity", "trace_dist", "local_err")


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in r:
            r[k] = float(r[k]) if k not in ("n_qubits", "order", "n_steps", "cnots") else int(r[k])
    return rows


def analyze(rows: list[dict], fit_from: int = 5) -> list[dict]:
    groups: dict[tuple, dict[float, dict[int, dict]]] = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        groups[(r["n_qubits"], r["order"])][r["p"]][r["n_steps"]] = r
    out = []
    for (nq, order), by_p in sorted(groups.items()):
        ps = sorted(by_p)
        if 0.0 not in by_p or len(ps) < 2:
            continue
        clean = by_p[0.0]
        ns = np.array(sorted(clean))
        p_min = ps[1]
        for metric in METRICS:
            e0 = np.array([clean[n][metric] for n in ns])
            sel = (ns >= fit_from) & (e0 > 1e-14)
            q, loga = np.polyfit(np.log(ns[sel]), np.log(e0[sel]), 1)
            q, a = -q, float(np.exp(loga))
            diff = np.array([by_p[p_min][n][metric] for n in ns]) - e0
            b = float(np.polyfit(ns, diff, 1)[0] / p_min)
            for p in ps[1:]:
                errs = np.array([by_p[p][n][metric] for n in ns])
                k = int(np.argmin(errs))
                pred = (q * a / (b * p)) ** (1 / (q + 1)) if b > 0 else float("nan")
                out.append({"n_qubits": nq, "order": order, "metric": metric, "p": p,
                            "n_star": int(ns[k]), "err_min": float(errs[k]),
                            "n_star_pred": round(pred, 2), "q_fit": round(q, 3), "a_fit": a, "b_fit": b,
                            "hit_nmax": bool(ns[k] == ns.max())})
    return out


def main() -> None:
    src = Path(sys.argv[1])
    res = analyze(load(src))
    dst = src.with_name(src.stem + "_optimum.csv")
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0]))
        w.writeheader()
        w.writerows(res)
    for r in res:
        flag = "（上限に到達）" if r["hit_nmax"] else ""
        print(f"N={r['n_qubits']} 次数{r['order']} {r['metric']:10s} p={r['p']:<6} n*={r['n_star']:3d}{flag} "
              f"予測 {r['n_star_pred']:6.2f}  最小誤差 {r['err_min']:.4f}  q={r['q_fit']}")
    print(f"書き出し: {dst}")


if __name__ == "__main__":
    main()
