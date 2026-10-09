"""S2 の当てはめを、順番にまとめて回す（長時間。留守のあいだに回す用）。

各回：多くの出発点からの MAP 探索（s2_map.py）→ 一番高い山から NUTS（s2_fit.py --init map）。
最後に s2_report.py で、収束の診断・正解の取り戻し・PSIS-LOO による形の比較をまとめる。
進み具合は results/s2/batch.log（回ごとの開始・終了の時刻）と、回ごとのログ（*_map.log、*.log）に出る。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/s2_batch.py --plan sensitivity
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "s2"
PLANS = {  # 計画名 → [(データ, 形, 揺らぎ, MAP の出発点の数, 追加の引数)]
    # 10/8 朝：最初の一通り
    "first": [("synthetic", "F2", "D1", 30, []), ("real", "F2", "D1", 30, []), ("real", "F2", "D0", 20, []),
              ("real", "F1", "D1", 30, []), ("real", "F3", "D1", 30, []), ("real", "F4", "D1", 30, [])],
    # 10/8 夜：実データの収束の改善。F2 は出発点を増やし、F3 は和と差に置き直した F3s を、22–23 の差の符号ごとに
    "converge": [("real", "F2", "D1", 60, []),
                 ("real", "F3s", "D1", 40, ["--d-sign", "1"]),
                 ("real", "F3s", "D1", 40, ["--d-sign", "-1"])],
    # 10/9 の留守中：A 事前分布の感度分析（F3s 正、幅 0.01・0.02・0.1、較正の値つき）、B 制御の状態ごとの形 F5、
    # C 制御 |1> の直接の測定を加えた合成データ（来月の測定の設計の下調べ）
    "sensitivity": [("real", "F3s", "D1", 30, ["--d-sign", "1", "--prior-width", "0.01"]),
                    ("real", "F3s", "D1", 30, ["--d-sign", "1", "--prior-width", "0.02"]),
                    ("real", "F3s", "D1", 30, ["--d-sign", "1", "--prior-width", "0.1"]),
                    ("real", "F3s", "D1", 30, ["--d-sign", "1", "--calib"]),
                    ("real", "F5", "D1", 40, []),
                    ("synthetic", "F5", "D1", 30, []),
                    ("synthetic", "F5", "D1", 30, ["--extra-c1"]),
                    ("real", "F5", "D1", 40, ["--calib"]),
                    # 10/9 朝に追加：較正の値つきの負の符号（4 と合わせて符号のスタッキング）、F5 のサンプルを2倍、7 を別の種で
                    ("real", "F3s", "D1", 30, ["--d-sign", "-1", "--calib"]),
                    ("real", "F5", "D1", 40, ["--label", "long"], ["--warmup", "600", "--samples", "600"]),
                    ("synthetic", "F5", "D1", 30, ["--extra-c1", "--seed", "1", "--label", "seed1"])],
}
NUTS_ARGS = ["--warmup", "300", "--samples", "300", "--chains", "4", "--init", "map"]


def log(msg: str) -> None:
    with (OUT / "batch.log").open("a", encoding="utf-8") as fh:
        fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def run(cmd: list[str], logfile: Path) -> int:
    with logfile.open("w", encoding="utf-8") as fh:
        # 子のプロセスの出力を UTF-8 にする（Windows の既定の CP932 だと、日本語のログを検索で読み落とした。10/8）
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        return subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=HERE.parents[1], env=env).returncode


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", choices=list(PLANS), default="converge")
    RUNS = PLANS[ap.parse_args().plan]
    sys.path.insert(0, str(HERE))
    import s2_fit
    tag_parser = argparse.ArgumentParser()
    s2_fit.add_common_args(tag_parser)
    OUT.mkdir(parents=True, exist_ok=True)
    py = [sys.executable]
    log(f"開始：{len(RUNS)} 回")
    for i, run_spec in enumerate(RUNS, 1):
        data, form, drift, starts, extra = run_spec[:5]
        nuts_extra = run_spec[5] if len(run_spec) > 5 else []          # NUTS だけに渡す追加の引数（サンプル数など）
        base = ["--data", data, "--form", form, "--drift", drift, *extra]
        tag = s2_fit.make_tag(tag_parser.parse_args(base))
        log(f"{i}/{len(RUNS)} {tag}：MAP 探索（出発点 {starts}）")
        rc = run(py + [str(HERE / "s2_map.py"), *base, "--starts", str(starts)], OUT / f"{tag}_map.log")
        if rc != 0:
            log(f"{i}/{len(RUNS)} {tag}：MAP 探索が失敗（終了コード {rc}）。この回を飛ばす")
            continue
        log(f"{i}/{len(RUNS)} {tag}：NUTS")
        nuts = list(NUTS_ARGS)
        for j in range(0, len(nuts_extra), 2):                           # 同じ引数は後から渡したもので置き換える
            if nuts_extra[j] in nuts:
                nuts[nuts.index(nuts_extra[j]) + 1] = nuts_extra[j + 1]
            else:
                nuts += nuts_extra[j:j + 2]
        rc = run(py + [str(HERE / "s2_fit.py"), *base, *nuts], OUT / f"{tag}.log")
        log(f"{i}/{len(RUNS)} {tag}：終了（終了コード {rc}）")
    rc = run(py + [str(HERE / "s2_report.py")], OUT / "s2_report.log")
    log(f"まとめ（s2_report.py）終了（終了コード {rc}）。すべて完了")


if __name__ == "__main__":
    main()
