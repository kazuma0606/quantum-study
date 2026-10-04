"""実機の結果（hardware.py の CSV）を、シミュレーションと比べる。

  - 実機の局所的な量の誤差 |<Z_0>_実機 - <Z_0>_正確| と、その最小点
  - 雑音による変化（実機の値 - 雑音なしのトロッター積の値）
  - 実効的な雑音の強さ p_eff：脱分極の密度行列の計算（trotter_noise）が実機の <Z_0> に一番合う p を、
    n ≥ 3 の点の重みつき最小二乗で探す（較正データの CZ の誤差との比較用）

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_analyze.py results/hardware_main_o1_….csv results/hardware_main_o2_….csv
出力: figures/hardware_N2.png と results/hardware_summary_N2.csv
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"


def load(path: Path) -> tuple[list[dict], dict]:
    rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(path.open(encoding="utf-8"))]
    meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    return rows, meta


def fit_p_eff(rows: list[dict], N: int, order: int, t: float) -> float:
    ps = np.concatenate([np.linspace(0.0005, 0.01, 39), np.linspace(0.011, 0.06, 50)])
    sel = [r for r in rows if r["n_steps"] >= 3]
    def cost(p: float) -> float:
        return sum(((tn.run_point(N, t, order, int(r["n_steps"]), p).z_exact
                     + tn.run_point(N, t, order, int(r["n_steps"]), p).z_trotter_part
                     + tn.run_point(N, t, order, int(r["n_steps"]), p).z_noise_part) - r["z_readout_corrected"]) ** 2
                   / r["z_sem"] ** 2 for r in sel)
    costs = [cost(p) for p in ps]
    return float(ps[int(np.argmin(costs))])


def main() -> None:
    paths = [Path(a) for a in sys.argv[1:]]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    summary = []
    colors = {1: "#1f77b4", 2: "#e67e00"}
    for path in paths:
        rows, meta = load(path)
        N, order, t = meta["args"]["N"], meta["args"]["order"], meta["args"]["t"]
        ns = np.array([r["n_steps"] for r in rows])
        err = np.array([r["local_err_hw"] for r in rows])
        sem = np.array([r["z_sem"] for r in rows])
        noise = np.array([r["noise_part_hw"] for r in rows])
        p_cal = float(list(meta["calibration"]["pair_errors"].values())[0])
        p_eff = fit_p_eff(rows, N, order, t)
        sim_cal = [tn.run_point(N, t, order, int(n), p_cal) for n in ns]
        sim_eff = [tn.run_point(N, t, order, int(n), p_eff) for n in ns]
        k = int(np.argmin(err))
        label = "1次（トロッター）" if order == 1 else "2次（ストラング）"
        c = colors[order]
        ax = axes[0]
        ax.errorbar(ns, err, yerr=sem, fmt="o", color=c, ms=5, capsize=2, label=f"{label}：実機")
        ax.plot(ns, [r.local_err for r in sim_cal], ":", color=c, lw=1.2, label=f"{label}：脱分極 p={p_cal:.4f}（較正の CZ 誤差）")
        ax.plot(ns, [r.local_err for r in sim_eff], "-", color=c, lw=1.5, alpha=0.8, label=f"{label}：脱分極 p={p_eff:.4f}（実機に当てはめ）")
        ax2 = axes[1]
        ax2.errorbar(ns, noise, yerr=sem, fmt="o", color=c, ms=5, capsize=2, label=f"{label}：実機")
        ax2.plot(ns, [r.z_noise_part for r in sim_eff], "-", color=c, lw=1.5, alpha=0.8, label=f"{label}：脱分極 p={p_eff:.4f}")
        summary.append({"N": N, "order": order, "backend": meta["backend"], "job_id": meta["job_id"],
                        "usage_quantum_seconds": meta["usage_quantum_seconds"], "p_calibration_cz": p_cal,
                        "p_eff_fit": p_eff, "p_eff_over_p_cal": round(p_eff / p_cal, 2),
                        "n_star_hw": int(ns[k]), "err_min_hw": float(err[k]), "err_min_sem": float(sem[k]),
                        "n_star_sim_cal": int(ns[int(np.argmin([r.local_err for r in sim_cal]))]),
                        "n_star_sim_eff": int(ns[int(np.argmin([r.local_err for r in sim_eff]))])})
    axes[0].set_yscale("log")
    axes[0].set_xlabel("分割数 $n$")
    axes[0].set_ylabel("局所的な量の誤差 $|\\langle Z_0\\rangle-\\langle Z_0\\rangle_{\\mathrm{exact}}|$")
    axes[0].set_title("(a) 実機（ibm_fez、N=2、t=2）とシミュレーション", fontsize=11)
    axes[0].legend(fontsize=7.5, loc="lower left")
    axes[1].axhline(0, color="#999", lw=0.8)
    axes[1].set_xlabel("分割数 $n$")
    axes[1].set_ylabel("雑音による変化（実機 − 雑音なしのトロッター積）")
    axes[1].set_title("(b) 雑音による変化：実機は較正からの予測よりずっと大きい", fontsize=11)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    out_png = HERE / "figures" / "hardware_N2.png"
    fig.savefig(out_png, dpi=150)
    out_csv = HERE / "results" / "hardware_summary_N2.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    for s in summary:
        print(s)
    print(f"書き出し: {out_png}\n書き出し: {out_csv}")


if __name__ == "__main__":
    main()
