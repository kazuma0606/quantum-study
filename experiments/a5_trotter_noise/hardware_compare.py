"""実機の結果を、量子ビットの組・実行時の設定（なし・動的デカップリング・ゲートのツイリング）・分解の次数ごとに比べる図と表。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_compare.py
出力: figures/hardware_compare_N2.png と results/hardware_compare_N2.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hardware_analyze as ha  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"

PAIRS = [  # (量子ビットの組, [(ラベル, ファイル名の接頭辞, 色, 記号), ...])
    ("22–23", [
        ("1次：設定なし", "hardware_main_o1_", "#1f77b4", "o"),
        ("1次：動的デカップリング（XY4）", "hardware_dd_xy4_o1_", "#9467bd", "s"),
        ("1次：ゲートのツイリング", "hardware_twirl_o1_", "#2ca02c", "^"),
        ("2次：設定なし", "hardware_main_o2_", "#e67e00", "D"),
    ]),
    ("142–143", [
        ("1次：設定なし", "hardware_q142_o1_", "#1f77b4", "o"),
        ("1次：ゲートのツイリング", "hardware_q142_twirl_o1_", "#2ca02c", "^"),
        ("2次：設定なし", "hardware_q142_o2_", "#e67e00", "D"),
        ("2次：ゲートのツイリング", "hardware_q142_twirl_o2_", "#d62728", "v"),
    ]),
]


def main() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    table = []
    for row, (pair, runs) in enumerate(PAIRS):
        for label, prefix, color, marker in runs:
            path = sorted((HERE / "results").glob(prefix + "2*.csv"))[-1]
            rows, meta = ha.load(path)
            ns = np.array([r["n_steps"] for r in rows])
            err = np.array([r["local_err_hw"] for r in rows])
            noise = np.array([r["noise_part_hw"] for r in rows])
            sem = np.array([r["z_sem"] for r in rows])
            order = meta["args"]["order"]
            p_eff = ha.fit_p_eff(rows, 2, order, meta["args"]["t"])
            k = int(np.argmin(err))
            axes[row, 0].errorbar(ns, err, yerr=sem, fmt=marker + "-", color=color, ms=4.5, lw=1, capsize=2, label=label)
            axes[row, 1].errorbar(ns, noise, yerr=sem, fmt=marker + "-", color=color, ms=4.5, lw=1, capsize=2, label=label)
            table.append({"qubits": pair, "run": label, "file": path.name, "job_id": meta["job_id"],
                          "usage_quantum_seconds": meta["usage_quantum_seconds"], "shots": meta["args"]["shots"],
                          "order": order, "n_star_hw": int(ns[k]), "err_min_hw": float(err[k]), "err_min_sem": float(sem[k]),
                          "noise_part_n14": float(noise[ns == 14][0]), "p_eff_fit": p_eff})
        axes[row, 0].set_yscale("log")
        axes[row, 0].set_ylabel("局所的な量の誤差 $|\\langle Z_0\\rangle-\\langle Z_0\\rangle_{\\mathrm{exact}}|$")
        axes[row, 0].set_title(f"({'ac'[row]}) 量子ビット {pair}：設定ごとの誤差", fontsize=11)
        axes[row, 1].axhline(0, color="#999", lw=0.8)
        axes[row, 1].set_ylabel("雑音による変化（実機 − 雑音なしのトロッター積）")
        axes[row, 1].set_title(f"({'bd'[row]}) 量子ビット {pair}：雑音による変化", fontsize=11)
        for ax in axes[row]:
            ax.set_xlabel("分割数 $n$")
            ax.legend(fontsize=8.5)
    fig.suptitle("実機（ibm_fez、N=2、t=2）：ツイリングで、どちらの組でもコヒーレントな誤差の大部分が消える", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "hardware_compare_N2.png", dpi=150)
    out = HERE / "results" / "hardware_compare_N2.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    for r in table:
        print(f"{r['qubits']:8s} {r['run']:28s} n*={r['n_star_hw']:2d}  最小誤差 {r['err_min_hw']:.4f}±{r['err_min_sem']:.4f}  "
              f"n=14 の雑音による変化 {r['noise_part_n14']:+.4f}  実効的な p {r['p_eff_fit']:.4f}  利用 {r['usage_quantum_seconds']} 秒")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
