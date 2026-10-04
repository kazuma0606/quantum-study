"""最適な分割数 n* の、雑音の強さ p に対する指数 n* ∝ p^s を、指標ごと・次数ごとに当てはめる。

予想：誤差 ≈ a/n^q + b p n なら n* ∝ p^{-1/(q+1)}。
  トレース距離（トロッター誤差の大きさ）：q = 次数 k → s = -1/(k+1)（1次 -1/2、2次 -1/3。Knee–Munro 2015 の1次と同じ）
  不忠実度（誤差の2乗）：q = 2k → s = -1/(2k+1)（1次 -1/3、2次 -1/5）
  局所的な量 <Z_0>：この模型では 1次でも q = 2（Layden の条件）→ どちらも -1/3 が予想。ただし符号つきの打ち消し合いで崩れうる
n* は整数なので、実際の n* の当てはめ（s_actual）と、モデルの連続的な予測 n*_pred の当てはめ（s_model）の両方を出す。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/exponents.py results/sweep_….csv
出力: 同じ名前の _exponents.csv
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402

EXPECTED = {("trace_dist", 1): -1 / 2, ("trace_dist", 2): -1 / 3,
            ("infidelity", 1): -1 / 3, ("infidelity", 2): -1 / 5,
            ("local_err", 1): -1 / 3, ("local_err", 2): -1 / 3}


def exponents(table: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for r in table:
        if not r["hit_nmax"]:
            groups[(r["n_qubits"], r["order"], r["metric"])].append(r)
    out = []
    for (nq, order, metric), rs in sorted(groups.items()):
        if len(rs) < 3:
            continue
        lp = np.log([r["p"] for r in rs])
        s_act = float(np.polyfit(lp, np.log([r["n_star"] for r in rs]), 1)[0])
        s_mod = float(np.polyfit(lp, np.log([r["n_star_pred"] for r in rs]), 1)[0])
        out.append({"n_qubits": nq, "order": order, "metric": metric, "n_points": len(rs),
                    "s_actual": round(s_act, 3), "s_model": round(s_mod, 3),
                    "s_expected": round(EXPECTED[(metric, order)], 3),
                    "q_fit": rs[0]["q_fit"]})
    return out


def main() -> None:
    src = Path(sys.argv[1])
    res = exponents(analyze.analyze(analyze.load(src)))
    dst = src.with_name(src.stem + "_exponents.csv")
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0]))
        w.writeheader()
        w.writerows(res)
    print(f"{'N':>2} {'次数':>2} {'指標':12s} {'点数':>4} {'実際の s':>9} {'モデルの s':>10} {'予想':>7} {'q':>6}")
    for r in res:
        print(f"{r['n_qubits']:>2} {r['order']:>4} {r['metric']:12s} {r['n_points']:>4} {r['s_actual']:>9} "
              f"{r['s_model']:>10} {r['s_expected']:>7} {r['q_fit']:>6}")
    print(f"書き出し: {dst}")


if __name__ == "__main__":
    main()
