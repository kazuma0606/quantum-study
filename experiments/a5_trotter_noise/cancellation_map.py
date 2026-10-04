"""局所的な量 <Z_0> の誤差で、トロッター部分と雑音部分が打ち消し合う領域を (n, p) の平面に描く。

打ち消し合いの度合い：R = |トロッター部分 + 雑音部分| / (|トロッター部分| + |雑音部分|)
  R = 1：同じ符号（足し合わさる）、R = 0：完全な打ち消し合い。
図には、局所的な量で選んだ最適な n*（打ち消し合いで決まる）と、状態全体の不忠実度で選んだ n*（綱引きで決まる）を重ねる。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/cancellation_map.py --qubits 3
出力:
    results/cancellation_map_N<N>.csv
    figures/cancellation_map_N<N>.png
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"


def cancellation_ratio(tp: float, npart: float) -> float:
    denom = abs(tp) + abs(npart)
    return abs(tp + npart) / denom if denom > 0 else 1.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qubits", type=int, default=3)
    ap.add_argument("--t", type=float, default=2.0)
    ap.add_argument("--nmax", type=int, default=40)
    ap.add_argument("--np", type=int, default=25, help="p の点の数（1e-4〜5e-2 の対数等間隔）")
    args = ap.parse_args()

    N = args.qubits
    ps = np.logspace(-4, np.log10(5e-2), args.np)
    ns = np.arange(1, args.nmax + 1)
    rows = []
    R = {1: np.zeros((len(ps), len(ns))), 2: np.zeros((len(ps), len(ns)))}
    best_local = {1: [], 2: []}
    best_fid = {1: [], 2: []}
    for order in (1, 2):
        for i, p in enumerate(ps):
            rs = [tn.run_point(N, args.t, order, int(n), float(p)) for n in ns]
            for j, r in enumerate(rs):
                R[order][i, j] = cancellation_ratio(r.z_trotter_part, r.z_noise_part)
                d = asdict(r)
                d["cancel_ratio"] = R[order][i, j]
                rows.append(d)
            best_local[order].append(int(ns[np.argmin([r.local_err for r in rs])]))
            best_fid[order].append(int(ns[np.argmin([r.infidelity for r in rs])]))

    # 照合：1次では、局所的な量の最適点は、弱い雑音（p ≤ 0.02）で打ち消し合いの強い点（R < 0.3）にある
    for i, p in enumerate(ps):
        if p <= 0.02:
            j = best_local[1][i] - 1
            assert R[1][i, j] < 0.3, f"1次、p={p:.2e}：局所的な量の最適点 n={best_local[1][i]} で R={R[1][i, j]:.2f}"

    out_csv = HERE / "results" / f"cancellation_map_N{N}.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, order in zip(axes, (1, 2)):
        im = ax.pcolormesh(ns, ps, R[order], cmap="RdYlBu", vmin=0, vmax=1, shading="nearest")
        ax.plot(best_local[order], ps, "o-", color="k", ms=3.5, lw=1.2, label="局所的な量 $\\langle Z_0\\rangle$ の最適な $n^*$")
        ax.plot(best_fid[order], ps, "s--", color="#7b2fbf", ms=3.5, lw=1.2, label="状態全体の不忠実度の最適な $n^*$")
        ax.set_yscale("log")
        ax.set_xlabel("分割数 $n$")
        ax.set_title(f"{'1次（トロッター）' if order == 1 else '2次（ストラング）'}、N={N}、t={args.t:g}", fontsize=11)
        ax.legend(fontsize=8.5, loc="upper right")
    axes[0].set_ylabel("CNOT 1個あたりの雑音 $p$")
    cb = fig.colorbar(im, ax=axes, shrink=0.9)
    cb.set_label("打ち消し合いの度合い $R$（0：完全に打ち消す、1：同じ符号）")
    fig.suptitle("局所的な量の誤差：トロッター部分と雑音部分の打ち消し合い", fontsize=12)
    out_png = HERE / "figures" / f"cancellation_map_N{N}.png"
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"書き出し: {out_csv}\n書き出し: {out_png}")


if __name__ == "__main__":
    main()
