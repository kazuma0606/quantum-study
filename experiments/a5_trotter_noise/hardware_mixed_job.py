"""来月の実機のジョブ（組ごとに1本、回路を混ぜる）を組み立て、実機用に変換して、QPU の時間を見積もる（ドライランだけ）。

a5_data.synthetic_mixed_job（合成データの予行演習）と同じ回路を、組ごとに1本のジョブに混ぜる：
  トロッター回路：1次・2次、n = 1〜14（hardware.py と同じ回路）。--twirl をつけると、同じ回路をツイリングありでもう一度数える
  監視用の回路  ：制御の Z 回転（|+> にして X・Y・Z で測る）と、標的の X 回転（|0> のまま Z・Y・X で測る）、k = 12（hardware_zprobe.py）。
                  3 つ目の基底は 2026-11-07 から（11/03 の 1 回目は 2 つの基底だけ）
  c1 Z の測定   ：制御 |1>、反転を戻す、標的の Z 回転（X・Y で測る）。22–23 は k = 1〜4、142–143 は k = 2, 4, 8, 12
  T1 専用の回路 ：制御 |0>・|1>、CX の組を k 回、両方を Z で同時に測る（hardware_t1probe.py）。k ごとにショットを配れる
  読み出しの較正：全 0・全 1（hardware.py と同じ）
QPU の時間の見積もり（hardware_t1probe.py と同じ 2 通り）：
  (a) 2 秒 ＋ 0.3 ms × ショットの合計（回路の長さを考えない。これまでのジョブの実績）
  (b) 2 秒 ＋ Σ ショット × (0.3 ms ＋ その回路の実行時間)。実行時間は qiskit の estimate_duration で見積もる
--submit をつけない限り、実機にジョブを出さない（既定はドライラン。出す前に、見積もりと承認が要る）。
--submit では、組ごとに1本のジョブを出し（回路ごとにショット数を指定する）、投入の直後にジョブ ID を
results/hardware_mixed_<タグ>_<組>_<時刻>.json に書き、結果が届いたら回路ごとのカウントと利用時間を同じファイルに足す。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/hardware_mixed_job.py --t1-ks 0 48 --t1-k-shots 5000 10000
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import qiskit
import qiskit_ibm_runtime
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler import generate_preset_pass_manager

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hardware as hw  # noqa: E402
import hardware_t1probe as ht  # noqa: E402
import hardware_zprobe as hz  # noqa: E402

N, T = 2, 2.0
SEC_PER_JOB, SEC_PER_SHOT = 2.0, 3e-4
PAIRS = {"22-23": [22, 23], "142-143": [142, 143]}
C1_KS = {"22-23": (1, 2, 3, 4), "142-143": (2, 4, 8, 12)}
HERE = Path(__file__).resolve().parent
JST = timezone(timedelta(hours=9))


def job_circuits(pair: str, args) -> list[tuple[str, dict, object, int]]:
    """(種類, 回路の目印, 回路, ショット数) の並び。目印は、結果を解析するときに回路を見分けるためのもの。"""
    rows = []
    for order in (1, 2):
        for n in args.trotter_ns:
            rows.append(("トロッター", {"order": order, "n": n},
                         hw.measured_trotter_circuit(N, T, order, n), args.trotter_shots))
    # 監視用の回路は、3 つの基底で測る（2026-11-07 から）。2 つの基底（Z 回転なら X・Y、X 回転なら Z・Y）だけでは、
    # 測らない向きへ倒れる回転（11/03 の 142–143 の標的の Y 軸まわりの回転など）が、位相ではなく「長さが縮む」としか見えない
    for axis, target, bases in (("Z", 0, ("X", "Y", "Z")), ("X", 1, ("Z", "Y", "X"))):
        for b in bases:
            rows.append(("監視用", {"target": target, "axis": axis, "k": args.monitor_k, "basis": b},
                         hz.probe_circuit(target, args.monitor_k, b, axis), args.probe_shots))
    for k in C1_KS[pair]:
        for b in ("X", "Y"):
            rows.append(("c1 Z", {"target": 1, "axis": "Z", "k": k, "basis": b, "control_one": True},
                         hz.probe_circuit(1, k, b, "Z", control_one=True), args.probe_shots))
    k_shots = args.t1_k_shots or [args.t1_shots] * len(args.t1_ks)
    for c1 in (False, True):
        for k, sh in zip(args.t1_ks, k_shots):
            rows.append(("T1 専用", {"k": k, "control_one": c1}, ht.t1probe_circuit(k, c1), sh))
    for i, qc in enumerate(hw.calibration_circuits(N)):
        rows.append(("読み出しの較正", {"prepared": "1" * N if i else "0" * N}, qc, args.cal_shots))
    return rows


def calibration(backend, qubits: list[int]) -> dict:
    """投入の時点の較正の値（hardware.py と同じ項目）。"""
    t = backend.target
    gate = "cz" if "cz" in t.operation_names else "ecr"
    a, b = qubits
    return {"pair_error": (t[gate].get((a, b)) or t[gate].get((b, a))).error,
            "readout_errors": {q: t["measure"][(q,)].error for q in qubits},
            "t1_us": {q: backend.qubit_properties(q).t1 * 1e6 for q in qubits},
            "t2_us": {q: backend.qubit_properties(q).t2 * 1e6 for q in qubits}}


def submit(backend, pair: str, rows, isa, args):
    """組ごとに1本のジョブを出し、投入の直後にジョブ ID を書く。(ジョブ, 記録, 書き出し先) を返す。"""
    sampler = SamplerV2(mode=backend)
    submitted = datetime.now(timezone.utc)
    job = sampler.run([(tq, None, sh) for (_, _, _, sh), tq in zip(rows, isa)])
    out = HERE / "results" / f"hardware_mixed_{args.tag}_{pair}_{submitted:%Y%m%dT%H%M%SZ}.json"
    record = {
        "args": vars(args), "backend": backend.name, "pair": pair, "qubits": PAIRS[pair], "job_id": job.job_id(),
        "submitted_utc": submitted.isoformat(), "calibration": calibration(backend, PAIRS[pair]),
        "circuits": [{"kind": kind, **label, "shots": sh, "name": tq.name, "depth": tq.depth(),
                      "two_qubit_gates": tq.count_ops().get("cz", 0) + tq.count_ops().get("ecr", 0)}
                     for (kind, label, _, sh), tq in zip(rows, isa)],
        "qiskit": qiskit.__version__, "qiskit_ibm_runtime": qiskit_ibm_runtime.__version__,
    }
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"投入：{pair} のジョブ {job.job_id()}（{submitted.astimezone(JST):%Y-%m-%d %H:%M:%S} JST）。記録 {out}", flush=True)
    return job, record, out


def collect(job, record: dict, out: Path) -> None:
    """結果を待ち、回路ごとのカウントと利用時間を記録に足す。"""
    pair = record["pair"]
    result = job.result()
    for c, r in zip(record["circuits"], result):
        c["counts"] = r.join_data().get_counts()
        assert sum(c["counts"].values()) == c["shots"], f"{c['name']}：カウントの合計が {c['shots']} でない"
    record["usage_quantum_seconds"] = job.usage()
    record["finished_utc"] = datetime.now(timezone.utc).isoformat()
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"結果：{pair} のジョブ {job.job_id()}、利用時間 {record['usage_quantum_seconds']} 秒。{out}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--pairs", nargs="+", default=list(PAIRS), choices=list(PAIRS))
    ap.add_argument("--trotter-ns", type=int, nargs="+", default=list(range(1, 15)))
    ap.add_argument("--trotter-shots", type=int, default=8000)
    ap.add_argument("--twirl", action="store_true", help="トロッター回路をツイリングありでもう一度数える")
    ap.add_argument("--monitor-k", type=int, default=12)
    ap.add_argument("--probe-shots", type=int, default=3000, help="監視用の回路と c1 Z の測定のショット数")
    ap.add_argument("--t1-ks", type=int, nargs="+", default=[0, 48])
    ap.add_argument("--t1-shots", type=int, default=7500)
    ap.add_argument("--t1-k-shots", type=int, nargs="+", help="T1 専用の回路のショットを k ごとに配る（--t1-ks と同じ長さ）")
    ap.add_argument("--cal-shots", type=int, default=3000)
    ap.add_argument("--tag", default="m1")
    ap.add_argument("--submit", action="store_true", help="実機にジョブを出す（出す前に、時間の見積もりと承認が要る）")
    ap.add_argument("--no-wait", action="store_true", help="--submit で、投入だけして結果を待たない")
    args = ap.parse_args()
    if args.t1_k_shots and len(args.t1_k_shots) != len(args.t1_ks):
        ap.error("--t1-k-shots は --t1-ks と同じ長さにする")
    if args.t1_k_shots and min(args.t1_k_shots) <= 0:
        ap.error("--t1-k-shots は正の整数にする")
    if args.submit and args.twirl:
        ap.error("--twirl つきの投入はまだ用意していない（ツイリングはジョブ全体にかかるので、別のジョブに分ける必要がある）")

    backend = QiskitRuntimeService(instance="open-instance").backend(args.backend)
    grand_a = grand_b = 0.0
    jobs = []
    for pair in args.pairs:
        rows = job_circuits(pair, args)
        if args.twirl:
            rows += [("トロッター（ツイリング）", lab, qc, sh) for kind, lab, qc, sh in rows if kind == "トロッター"]
        pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=PAIRS[pair])
        isa = pm.run([qc for _, _, qc, _ in rows])
        jobs.append((pair, rows, isa))
        by_kind: dict[str, list[float]] = {}
        for (kind, _, qc, sh), tq in zip(rows, isa):
            dur = tq.estimate_duration(backend.target, unit="s")
            v = by_kind.setdefault(kind, [0, 0, 0.0, 0.0])
            v[0] += 1
            v[1] += sh
            v[2] = max(v[2], dur)
            v[3] += sh * (SEC_PER_SHOT + dur)
        tot_a = SEC_PER_JOB + SEC_PER_SHOT * sum(v[1] for v in by_kind.values())
        tot_b = SEC_PER_JOB + sum(v[3] for v in by_kind.values())
        grand_a, grand_b = grand_a + tot_a, grand_b + tot_b
        print(f"\n## {pair}（量子ビット {PAIRS[pair]}、{args.backend}）")
        print("| 種類 | 回路 | ショットの合計 | 1回の実行の最長（μs） | (b) の秒 |")
        print("|---|---|---|---|---|")
        for kind, (nc, ns, dmax, sec) in by_kind.items():
            print(f"| {kind} | {nc} | {ns} | {dmax * 1e6:.1f} | {sec:.1f} |")
        print(f"回路 {len(isa)} 本。QPU の時間の見積もり：(a) {tot_a:.1f} 秒、(b) {tot_b:.1f} 秒")
    print(f"\n合計（{len(args.pairs)} 本のジョブ）：(a) {grand_a:.1f} 秒、(b) {grand_b:.1f} 秒")
    if not args.submit:
        print("ドライラン：実機にはジョブを出していない")
        return
    # 先に全部の組を投入してから待つ（組の間で時刻がずれないように）
    submitted = [submit(backend, pair, rows, isa, args) for pair, rows, isa in jobs]
    if not args.no_wait:
        for s in submitted:
            collect(*s)


if __name__ == "__main__":
    main()
