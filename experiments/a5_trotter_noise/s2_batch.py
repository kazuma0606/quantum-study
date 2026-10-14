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
    # 10/10：S4 のあとに自動で回す。F5 の「制御 |1> の Z 回転 −0.11」が事前分布の幅によらないか（データ由来か）、
    # F5 でも揺らぎが要るか、制御 |1> の測定つき合成データでの失敗（seed1）が種によるものか
    "followup": [("real", "F5", "D1", 40, ["--prior-width", "0.02", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
                 ("real", "F5", "D1", 40, ["--prior-width", "0.1", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
                 ("real", "F5", "D0", 30, ["--label", "long"], ["--warmup", "600", "--samples", "600"]),
                 ("synthetic", "F5", "D1", 30, ["--extra-c1", "--seed", "2", "--label", "seed2"]),
                 ("synthetic", "F5", "D1", 30, ["--extra-c1", "--seed", "1", "--label", "seed1long"],
                  ["--warmup", "600", "--samples", "600"])],
    # 10/11：事後予測チェックで、ずれが統計誤差の約 1.3 倍（T1 の形のずれは 1σ）。F5+D1 に T1（CX ごとの振幅減衰）と、
    # 誤差棒を広げる係数を、それぞれ・両方入れて、予測の良さ（LOO）と、制御 |1> の Z 回転などが動くかを見る
    "t1": [("real", "F5", "D1", 12, ["--t1", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
           ("real", "F5", "D1", 12, ["--obs-scale", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
           ("real", "F5", "D1", 12, ["--t1", "--obs-scale", "--label", "long"], ["--warmup", "600", "--samples", "600"])],
    # 10/11 午後：① 本番の予行演習。正解を実データの当てはめ（誤差棒つき）から作り、22–23 の制御 |1> の Z 回転だけを
    # −0.11 と +0.105 にした2つの世界で、S6 の推奨の測定（c1 Z、22–23 は k=1〜4）を加え、実データの約 1.4 倍のばらつきを入れて、
    # 誤差棒つき・T1＋誤差棒つきのモデルで当てはめる。② T1＋誤差棒の MAP 探索を出発点 30 個でやり直す。③ 外れの1点を抜く
    # 10/12：実機の制御 |1> の Z の測定（傾き約 0、−0.11 と +0.105 のどちらでもない）を加えた当てはめ（D）、
    # 外れ値に強い尤度（A）、誤差棒の倍率を組ごとに分ける（B）、予行演習の乱数の種を変える（C）
    "today": [
        ("real", "F5", "D1", 30, ["--obs-scale", "--with-c1-hw", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
        ("real", "F5", "D1", 30, ["--t1", "--obs-scale", "--with-c1-hw", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
        ("real", "F5", "D1", 30, ["--obs-scale", "--robust", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
        ("real", "F5", "D1", 30, ["--obs-scale-pair", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
        *[("synthetic", "F5", "D1", 20,
           ["--obs-scale", "--extra-c1", "--c1-design", "rec", "--truth-from", "real_F5_D1_os_long",
            "--truth-c1z", v, "--syn-noise", "1.42", "1.35", "--seed", sd, "--label", f"{lab}s{sd}"],
           ["--warmup", "600", "--samples", "600"])
          for sd in ("1", "2") for v, lab in (("-0.11", "rehm011"), ("0.105", "rehp0105"))],
    ],
    # 10/12 夕方：1 時期で分けるモデル（10/12 のジョブだけ制御 |1> の Z 回転が別）、2 T1＋誤差棒＋t 分布の尤度、3 それに実機を加える
    "evening": [
        ("real", "F5", "D1", 30, ["--obs-scale", "--with-c1-hw", "--split-hw", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
        ("real", "F5", "D1", 30, ["--t1", "--obs-scale", "--robust", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
        ("real", "F5", "D1", 30, ["--t1", "--obs-scale", "--robust", "--with-c1-hw", "--label", "long"], ["--warmup", "600", "--samples", "600"]),
    ],
    # 10/13：来月の測り方で「T1 が欠けていた」と「時期で回転が変わった」を区別できるかの予行演習。
    # 世界 A：T1 あり・回転は変わらない（T1＋誤差棒＋実機の当てはめが正解）。世界 B：T1 なし・来月のジョブだけ制御 |1> の Z 回転が
    # −0.11 → −0.006（誤差棒の当てはめが正解）。どちらにも来月の混ぜたジョブ（--mixed-job）を加え、2つのモデルで当てはめる
    "distinguish": [
        *[("synthetic", "F5", "D1", 20,
           [*model, "--mixed-job", "--syn-noise", "1.42", "1.35", *world, "--label", f"w{wname}"],
           ["--warmup", "600", "--samples", "600"])
          for wname, world in (("A", ["--truth-from", "real_F5_D1_t1_os_hw1_long"]),
                               ("B", ["--truth-from", "real_F5_D1_os_long", "--truth-c1z", "-0.11", "--truth-new-c1z", "-0.006"]))
          for model in (["--t1", "--obs-scale"], ["--obs-scale", "--split-hw"])],
    ],
    # 10/14：T1 なしの世界の回し直し（不具合を直したもの）と、読み出しの偏りを入れた T1 専用の回路の予行演習
    "readout": [
        *[("synthetic", "F5", "D1", 20,
           ["--t1", "--obs-scale", "--mixed-job", "--t1-probe", "--syn-noise", "1.42", "1.35",
            "--truth-from", "real_F5_D1_t1_os_hw1_long", *world, *ro, *model, "--label", lab],
           ["--warmup", "600", "--samples", "600"])
          for lab, world, ro, model in (
              ("wA0fix", ["--truth-no-t1"], [], []),
              ("wA1r", [], ["--syn-ro", "0.01", "0.03"], ["--ro-model"]),
              ("wA0r", ["--truth-no-t1"], ["--syn-ro", "0.01", "0.03"], ["--ro-model"]),
              ("wA1rs1", ["--seed", "1"], ["--syn-ro", "0.01", "0.03"], ["--ro-model"]),
              ("wA0rs1", ["--truth-no-t1", "--seed", "1"], ["--syn-ro", "0.01", "0.03"], ["--ro-model"]),
              ("wA0rnoro", ["--truth-no-t1"], ["--syn-ro", "0.01", "0.03"], []))],
    ],
    "rehearsal": [
        *[("synthetic", "F5", "D1", 20,
           [*t1, "--obs-scale", "--extra-c1", "--c1-design", "rec", "--truth-from", "real_F5_D1_os_long",
            "--truth-c1z", v, "--syn-noise", "1.42", "1.35", "--label", lab],
           ["--warmup", "600", "--samples", "600"])
          for t1 in ([], ["--t1"]) for v, lab in (("-0.11", "rehm011"), ("0.105", "rehp0105"))],
        ("real", "F5", "D1", 30, ["--t1", "--obs-scale", "--label", "long30"], ["--warmup", "600", "--samples", "600"]),
        ("real", "F5", "D1", 20, ["--obs-scale", "--drop-trotter", "db13un9b694s73drokvg:2:2", "--label", "drop1"],
         ["--warmup", "600", "--samples", "600"]),
    ],
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
