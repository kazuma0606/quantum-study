"""S4（SBI）の本番を、順番にまとめて回す（長時間。留守中に回す用）。

  1. 逐次版（SNPE）：6 回のくり返し、1 回あたり 10 万回のシミュレーション（実データの事後分布を NUTS と比べる）
  2. 事前分布全体の版（amortized）：100 万回のシミュレーション、SBC 300 組（区間の正直さを確かめる）
--plan first が上の 2 つ（10/10 に実行済み）。--plan local（既定）は、事前分布を NUTS の事後分布のまわりの箱
（中央値 ± k×標準偏差、k = 6 と 10）に絞った局所版を、それぞれ 30 万回のシミュレーションと SBC 300 組で回す。
進み具合は results/s4/batch.log（各回の開始・終了）と、回ごとのログ（*.log）に出る。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s4_batch.py --plan local
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "s4"
PLANS = {}
RUNS = [  # (名前, 引数)
    ("sequential_6x100k", ["--mode", "sequential", "--rounds", "6", "--sims", "100000", "--max-epochs", "300",
                           "--tag", "sequential_6x100k"]),
    ("amortized_1M", ["--mode", "amortized", "--sims", "1000000", "--max-epochs", "300", "--sbc", "300",
                      "--sbc-draws", "500", "--tag", "amortized_1M"]),
]
PLANS["first"] = RUNS
# 10/11：事前分布を NUTS の事後分布のまわりの箱に絞った局所版（箱の広さ ±6σ と ±10σ）。学習のバッチを大きくして GPU を使い切る
PLANS["local"] = [
    ("local_k6_300k", ["--mode", "amortized", "--box-k", "6", "--sims", "300000", "--max-epochs", "300", "--train-batch", "4096",
                       "--sbc", "300", "--sbc-draws", "500", "--tag", "local_k6_300k"]),
    ("local_k10_300k", ["--mode", "amortized", "--box-k", "10", "--sims", "300000", "--max-epochs", "300", "--train-batch", "4096",
                        "--sbc", "300", "--sbc-draws", "500", "--tag", "local_k10_300k"]),
]


def log(msg: str) -> None:
    with (OUT / "batch.log").open("a", encoding="utf-8") as fh:
        fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", choices=["first", "local"], default="local")
    RUNS = PLANS[ap.parse_args().plan]
    OUT.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    log(f"開始：{len(RUNS)} 回")
    for i, (name, args) in enumerate(RUNS, 1):
        log(f"{i}/{len(RUNS)} {name}：開始")
        with (OUT / f"{name}.log").open("w", encoding="utf-8") as fh:
            rc = subprocess.run([sys.executable, str(HERE / "s4_sbi.py"), *args], stdout=fh, stderr=subprocess.STDOUT,
                                cwd=HERE.parents[1], env=env).returncode
        log(f"{i}/{len(RUNS)} {name}：終了（終了コード {rc}）")
    log("すべて完了")


if __name__ == "__main__":
    main()
