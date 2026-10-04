"""条件（量子ビット数、雑音の強さ、分割数、分解の次数）を変えて計算し、CSV に書き出す。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/sweep.py --qubits 2 3 4 --ps 0 0.002 0.005 0.01 0.02 --nmax 30
出力:
    results/sweep_<日時>.csv        1行 = 1つの条件（列は trotter_noise.Result のフィールド）
    results/sweep_<日時>.meta.json  実行の記録（引数、日時、ライブラリの版）
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from dataclasses import asdict, fields
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qubits", type=int, nargs="+", default=[2])
    ap.add_argument("--ps", type=float, nargs="+", default=[0.0, 0.002, 0.005, 0.01, 0.02])
    ap.add_argument("--orders", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--nmax", type=int, default=30)
    ap.add_argument("--t", type=float, default=2.0)
    ap.add_argument("--J", type=float, default=1.0)
    ap.add_argument("--g", type=float, default=1.0)
    ap.add_argument("--out", type=Path, default=None, help="出力する CSV（既定は results/sweep_<日時>.csv）")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.out or HERE / "results" / f"sweep_{stamp}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    names = [f.name for f in fields(tn.Result)]
    t0 = time.time()
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=names)
        w.writeheader()
        for nq in args.qubits:
            for order in args.orders:
                for p in args.ps:
                    for n in range(1, args.nmax + 1):
                        w.writerow(asdict(tn.run_point(nq, args.t, order, n, p, args.J, args.g)))
                print(f"N={nq} 完了（{time.time() - t0:.1f} 秒）", flush=True)
    meta = {
        "args": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()},
        "utc": stamp,
        "elapsed_sec": round(time.time() - t0, 2),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "model": "横磁場イジング模型（開いた鎖）、初期状態 |00…0>、ZZ の項1つにつき CNOT 2個、各 CNOT の後に2量子ビット脱分極（強さ p）",
    }
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
