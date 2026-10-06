"""IBM の実機の較正データの履歴（1日ごと）を集め、CSV と図にする。実機の利用時間は使わない（API で過去の較正値を読むだけ）。

対象：実験で使った量子ビット（既定は ibm_fez の 22, 23, 142, 143）と、その組の CZ。
各日について、その日の正午（日本時間）より前で最も新しい較正値を取る（較正は毎日 20:30 ごろ更新される）。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/calibration_history.py --days 120
出力: results/calibration_history_<実機>.csv と figures/calibration_history_<実機>.png
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit_ibm_runtime import QiskitRuntimeService

HERE = Path(__file__).resolve().parent
JST = timezone(timedelta(hours=9))
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--qubits", type=int, nargs="+", default=[22, 23, 142, 143])
    ap.add_argument("--pairs", nargs="+", default=["22-23", "142-143"])
    ap.add_argument("--days", type=int, default=120)
    args = ap.parse_args()
    pairs = [tuple(int(x) for x in s.split("-")) for s in args.pairs]

    backend = QiskitRuntimeService(instance="open-instance").backend(args.backend)
    out = HERE / "results" / f"calibration_history_{args.backend}.csv"
    rows, seen = [], set()
    today = datetime.now(JST).replace(hour=12, minute=0, second=0, microsecond=0)
    for d in range(args.days, -1, -1):
        when = today - timedelta(days=d)
        try:
            p = backend.properties(datetime=when)
        except Exception as e:  # 取れない日は飛ばして記録だけ残す
            print(f"{when:%Y-%m-%d}：取得できず（{type(e).__name__}）")
            continue
        if p is None or p.last_update_date in seen:
            continue
        seen.add(p.last_update_date)
        row = {"calibrated_jst": p.last_update_date.astimezone(JST).isoformat()}
        for q in args.qubits:
            row[f"T1_us_q{q}"] = p.t1(q) * 1e6
            row[f"T2_us_q{q}"] = p.t2(q) * 1e6
            row[f"readout_err_q{q}"] = p.readout_error(q)
        for a, b in pairs:
            try:
                row[f"cz_err_{a}_{b}"] = p.gate_error("cz", [a, b])
            except Exception:
                row[f"cz_err_{a}_{b}"] = p.gate_error("cz", [b, a])
        rows.append(row)
        print(f"{row['calibrated_jst'][:16]}  T2 q22 {row.get('T2_us_q22', float('nan')):6.1f} us  CZ 22-23 {row.get('cz_err_22_23', float('nan')):.4f}", flush=True)
    keys = list(rows[0])
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} 日分を書き出し: {out}")

    t = [datetime.fromisoformat(r["calibrated_jst"]) for r in rows]
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.5), sharex=True)
    for ax, key, label in ((axes[0, 0], "T1_us", "T1（μs）"), (axes[0, 1], "T2_us", "T2（μs）"),
                           (axes[1, 0], "readout_err", "読み出しの誤り率")):
        for q in args.qubits:
            ax.plot(t, [r[f"{key}_q{q}"] for r in rows], ".-", ms=3, lw=0.8, label=f"量子ビット {q}")
        ax.set_ylabel(label)
        ax.legend(fontsize=8)
    ax = axes[1, 1]
    for a, b in pairs:
        ax.plot(t, [r[f"cz_err_{a}_{b}"] for r in rows], ".-", ms=3, lw=0.8, label=f"CZ {a}–{b}")
    ax.set_ylabel("CZ の誤差（較正値）")
    ax.legend(fontsize=8)
    for ax in axes[1]:
        ax.tick_params(axis="x", rotation=30)
    fig.suptitle(f"{args.backend} の較正データの履歴（1日ごと、実験で使った量子ビット）", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / f"calibration_history_{args.backend}.png", dpi=150)
    print("図を書き出し")


if __name__ == "__main__":
    main()
