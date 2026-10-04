# A-5 トロッター誤差と雑音の綱引き ―最適な分割数を予測して測る

`docs/research_ideas.md` のテーマ A-5 の計算一式です。ノートブックは作らず、**ライブラリ＋テスト（反例探し）＋CSV** で進めています。理論は[行列の指数関数と交換子のノート](../../研究ノート/04_群論・代数/matrix_exponential_commutator_bch_trotter.md)の Part VI。

## 問い

トロッター分解は分割数 $n$ を増やすほど誤差が減る（1次で $\propto1/n$、ストラング分解で $\propto1/n^2$）。しかし実機では $n$ に比例してゲートが増え、雑音が積み重なる。**最適な $n$ はどこにあり、何で決まるか。** 誤差を $\frac a{n^q}+b\,p\,n$（$p$ は CNOT 1個あたりの雑音）とモデル化すると、$n^*=\big(\frac{qa}{bp}\big)^{1/(q+1)}$ と予測できる。

## 模型

$N$ スピンの横磁場イジング模型（開いた鎖）$H=\sum_iZ_iZ_{i+1}+\sum_iX_i$、初期状態 $|00\cdots0\rangle$、時刻 $t=2$。1ステップに ZZ の項ごとに CNOT 2個、各 CNOT の後に2量子ビットの脱分極雑音（強さ $p$）。密度行列で正確に計算（雑音のサンプリングなし）。誤差は2通りで測る：

- `infidelity`：状態全体の不忠実度 $1-\langle\psi_{\text{exact}}|\rho|\psi_{\text{exact}}\rangle$
- `local_err`：局所的な量の誤差 $|\langle Z_0\rangle_\rho-\langle Z_0\rangle_{\text{exact}}|$（実機で測りやすい）

## ファイル

| ファイル | 中身 |
|---|---|
| `trotter_noise.py` | 模型、トロッター積、脱分極雑音、誤差の上限、1点の計算 `run_point` |
| `sweep.py` | 条件を変えて計算し、`results/*.csv` と `*.meta.json`（実行の記録）に出力 |
| `analyze.py` | CSV から実際の $n^*$ とモデルの予測を求め、`*_optimum.csv` に出力 |
| `tests/test_trotter_noise.py` | 反例探し（下の表） |
| `results/` | 計算結果の CSV |

```bash
uv run pytest experiments/a5_trotter_noise -q
uv run python experiments/a5_trotter_noise/sweep.py --qubits 2 3 4 5 6 --ps 0 0.001 0.002 0.005 0.01 0.02 --nmax 40 --out experiments/a5_trotter_noise/results/sweep_N2-6.csv
uv run python experiments/a5_trotter_noise/analyze.py experiments/a5_trotter_noise/results/sweep_N2-6.csv
```

## テスト（反例探し）

| テスト | 主張 | 結果 |
|---|---|---|
| `test_trotter_bound_random_hermitian` | ランダムなエルミート行列400組で、誤差 ≤ 上限（1次：$\frac{t^2}{2n}\lVert[A,B]\rVert$、2次：$\frac{t^3}{n^2}(\frac{\lVert[M,[M,O]]\rVert}{12}+\frac{\lVert[O,[O,M]]\rVert}{24})$） | 反例なし。誤差/上限の最大は 1次 0.997、2次 0.948（上限はほぼぎりぎりまで達する） |
| `test_trotter_bound_single_step_is_tight_order` | 1ステップの誤差の次数が 2（1次）・3（2次） | 成立 |
| `test_telescoping_inequality` | $\lVert U^n-V^n\rVert\le n\lVert U-V\rVert$（$\lVert U\rVert,\lVert V\rVert\le1$） | 反例なし |
| `test_depolarizing_is_cptp_like` | 雑音の通路がトレース・エルミート性・正定値性を保つ | 成立 |
| `test_matches_qiskit_synthesis` | 自前のトロッター積が Qiskit の `LieTrotter`・`SuzukiTrotter` と一致（N=2,3） | 成立 |
| `test_optimal_n_decreases_with_noise` | 雑音を強くすると $n^*$ は増えない（N=2） | 成立 |
| `test_strang_needs_fewer_steps` | ストラング分解の $n^*$ と最小誤差はトロッター分解以下（N=2） | 成立 |
| `test_global_infidelity_follows_model` | 不忠実度では、予測 $n^*$ が実際と2以内で合い、$q\approx2\times$次数（N=2〜5） | 成立（N=3 の1次だけ $q\approx2.4$〜$2.5$） |
| `test_local_observable_order_symmetry` | $\langle Z_0\rangle$ は A と B の順を入れ替えても同じ | 反例なし |
| `test_known_counterexamples_local_observable` | **見つかった反例を固定**（下の結果 3・4） | 反例が存在することを確認 |

## ここまでの結果（2026年10月4日、`results/sweep_N2-6_optimum.csv`）

1. **状態全体の不忠実度は、モデルどおり**：$q\approx2$（1次）・$4$（2次）で、予測 $n^*$ は実際とほぼ一致。不忠実度は誤差の2乗なので、$n^*\propto p^{-1/3}$（1次）・$p^{-1/5}$（2次）になる。
2. **$n^*$ は系の大きさ $N$ にほとんどよらず、最小誤差だけが $N$ とともに悪くなる**（不忠実度、$N\ge4$）。例：$p=0.001$ の1次で $n^*=11$（N=4〜6）、最小誤差は 0.074 → 0.126。N=3 だけは例外的（$n^*=7$）。
3. **局所的な量 $\langle Z_0\rangle$ では、1次でも誤差が $1/n^2$ で減る**。A と B の順を入れ替えても $\langle Z_0\rangle$ が変わらない対称性があり（テストで確認）、1次の誤差が打ち消し合うため。
4. **局所的な量では、素朴なモデルに反例がある**：
   - ストラング分解で、$p\ge0.01$ のとき $n^*=2$（予測は約 7.5、N=3〜6）。小さい $n$ ではトロッター誤差そのものが $n$ について単調でなく、$n=2$ でたまたま小さくなる（N=3 で $n=2$ のとき −0.017、$n=3$ のとき −0.051）。
   - 「ストラング分解の $n^*$ はトロッター分解以下」も、N=3・$p=0.005$ で破れる（9 対 10）。
   - 1次の最小誤差がとても小さく出る（0.0002 など）のは、トロッター誤差（正）と雑音による縮み（負）が符号つきで打ち消し合うため。実機でこの量だけを見ると、最適な $n$ を誤って選ぶおそれがある。

## 次の一歩

- 局所的な量の誤差を、符号つきでトロッター部分と雑音部分に分けて記録する（打ち消し合いを見えるようにする）。
- $N$ を増やす：密度行列で $N\le10$ 程度、それ以上は Qiskit Aer の軌跡法・MPS。
- 実機（IBM、$N=2$〜4）で測る前に、実機の較正データ（CNOT の誤差）から $n^*$ を予測しておく（`quantum-experiment` Skill の手順）。
- Lean：望遠鏡和の不等式 $\lVert U^n-V^n\rVert\le n\lVert U-V\rVert$ を、ノルム環で形式証明する候補（`lean-prover`）。
