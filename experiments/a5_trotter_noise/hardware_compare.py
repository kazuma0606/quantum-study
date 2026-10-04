"""実機の結果を、実行時の設定（なし・動的デカップリング・ゲートのツイリング）と分解の次数ごとに比べる図と表。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_compare.py
出力: figures/hardware_compare_N2.png と results/hardware_compare_N2.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hardware_analyze as ha  # noqa: E402
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

RUNS = [  # (ラベル, ファイル名の接頭辞, 色, 記号)
    ("1次：設定なし", "hardware_main_o1_", "#1f77b4", "o"),
    ("1次：動的デカップリング（XY4）", "hardware_dd_xy4_o1_", "#9467bd", "s"),
    ("1次：ゲートのツイリング", "hardware_twirl_o1_", "#2ca02c", "^"),
    ("2次：設定なし", "hardware_main_o2_", "#e67e00", "D"),
]


def main() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    table = []
    for label, prefix, color, marker in RUNS:
        path = sorted((HERE / "results").glob(prefix + "*.csv"))[-1]
        rows, meta = ha.load(path)
        ns = np.array([r["n_steps"] for r in rows])
        err = np.array([r["local_err_hw"] for r in rows])
        noise = np.array([r["noise_part_hw"] for r in rows])
        sem = np.array([r["z_sem"] for r in rows])
        order = meta["args"]["order"]
        p_eff = ha.fit_p_eff(rows, 2, order, meta["args"]["t"])
        k = int(np.argmin(err))
        axes[0].errorbar(ns, err, yerr=sem, fmt=marker + "-", color=color, ms=4.5, lw=1, capsize=2, label=label)
        axes[1].errorbar(ns, noise, yerr=sem, fmt=marker + "-", color=color, ms=4.5, lw=1, capsize=2, label=label)
        table.append({"run": label, "file": path.name, "job_id": meta["job_id"], "usage_quantum_seconds": meta["usage_quantum_seconds"],
                      "order": order, "n_star_hw": int(ns[k]), "err_min_hw": float(err[k]), "err_min_sem": float(sem[k]),
                      "noise_part_n14": float(noise[ns == 14][0]), "p_eff_fit": p_eff})
    axes[0].set_yscale("log")
    axes[0].set_xlabel("分割数 $n$")
    axes[0].set_ylabel("局所的な量の誤差 $|\\langle Z_0\\rangle-\\langle Z_0\\rangle_{\\mathrm{exact}}|$")
    axes[0].set_title("(a) 実機（ibm_fez、N=2、t=2）：設定ごとの誤差", fontsize=11)
    axes[0].legend(fontsize=8.5)
    axes[1].axhline(0, color="#999", lw=0.8)
    axes[1].set_xlabel("分割数 $n$")
    axes[1].set_ylabel("雑音による変化（実機 − 雑音なしのトロッター積）")
    axes[1].set_title("(b) ツイリングで、1次の余分な雑音の大部分が消える", fontsize=11)
    axes[1].legend(fontsize=8.5)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "hardware_compare_N2.png", dpi=150)
    out = HERE / "results" / "hardware_compare_N2.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    for r in table:
        print(f"{r['run']:28s} n*={r['n_star_hw']:2d}  最小誤差 {r['err_min_hw']:.4f}±{r['err_min_sem']:.4f}  "
              f"n=14 の雑音による変化 {r['noise_part_n14']:+.4f}  実効的な p {r['p_eff_fit']:.4f}  利用 {r['usage_quantum_seconds']} 秒")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
