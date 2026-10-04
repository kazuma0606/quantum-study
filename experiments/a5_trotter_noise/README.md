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
| `analyze.py` | CSV から実際の $n^*$ とモデルの予測を求め、`*_optimum.csv` に出力（指標：`infidelity`・`trace_dist`・`local_err`） |
| `exponents.py` | `analyze` の結果から、$n^*\propto p^s$ の指数 $s$ を指標・次数ごとに当てはめ、`*_exponents.csv` に出力 |
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
| `test_local_error_decomposition_identity` | 局所的な量の誤差 = \|トロッター部分 + 雑音部分\|（符号つき） | 成立 |
| `test_noise_does_not_always_shrink_toward_zero` | **反例の固定**：「雑音は ⟨Z_0⟩ を必ず 0 に近づける」は成り立たない | 反例あり（N=5、2次、p=0.02、n=3） |
| `test_lie_local_optimum_is_a_cancellation_point` | 1次・局所的な量の最適点は、2つの部分が逆符号で3割未満まで打ち消し合う点 | 成立（N=3、p=0.001〜0.02） |
| `test_first_order_coefficient_formula` | 導出した1次の係数 $c_1$ の式が、数値（誤差 × $n/t$）と一致 | 成立（ランダムな積状態・観測量） |
| `test_layden_condition_gives_zero_first_order` | $O$ が ZZ の項と交換し、初期状態が計算基底なら $c_1=0$ | 反例なし |
| `test_time_reversal_hypothesis_is_false` | **反例の固定**：「すべて実数なら $c_1=0$」は成り立たない | 反例あり（実数の積状態で $c_1\approx0.014$） |
| `test_small_c1_of_real_states_is_specific_to_N3_t2` | 実数の状態で $c_1$ が小さかったのは $N=3$・$t=2$ の偶然（共通の零点が $t=1.9$〜$2.2$ にある、他の時刻では5倍以上） | 成立 |

## ここまでの結果（2026年10月4日、`results/sweep_N2-6_optimum.csv`）

1. **状態全体の不忠実度は、モデルどおり**：$q\approx2$（1次）・$4$（2次）で、予測 $n^*$ は実際とほぼ一致。不忠実度は誤差の2乗なので、$n^*\propto p^{-1/3}$（1次）・$p^{-1/5}$（2次）になる。
2. **$n^*$ は系の大きさ $N$ にほとんどよらず、最小誤差だけが $N$ とともに悪くなる**（不忠実度、$N\ge4$）。例：$p=0.001$ の1次で $n^*=11$〜$12$（N=4〜8）、最小誤差は 0.074（N=4）→ 0.172（N=8）。2次では $n^*=7$（N=4〜8）。N=3 だけは例外的（1次で $n^*=7$）。N=7・8 は `results/sweep_N7-8.csv`（密度行列で約4分）。
3. **局所的な量 $\langle Z_0\rangle$ では、1次でも誤差が $1/n^2$ で減る**。A と B の順を入れ替えても $\langle Z_0\rangle$ が変わらない対称性があり（テストで確認）、1次の誤差が打ち消し合うため。
4. **局所的な量では、素朴なモデルに反例がある**：
   - ストラング分解で、$p\ge0.01$ のとき $n^*=2$（予測は約 7.5、N=3〜6）。小さい $n$ ではトロッター誤差そのものが $n$ について単調でなく、$n=2$ でたまたま小さくなる（N=3 で $n=2$ のとき −0.017、$n=3$ のとき −0.051）。
   - 「ストラング分解の $n^*$ はトロッター分解以下」も、N=3・$p=0.005$ で破れる（9 対 10）。
   - 1次の最小誤差がとても小さく出る（0.0002 など）のは、トロッター誤差と雑音の効果が符号つきで打ち消し合うため。CSV の `z_trotter_part`（雑音なしのトロッター積の誤差）と `z_noise_part`（雑音による変化）に分けて記録したところ、1次の最適点（N=3 で $n=17,9,5$ など）は、2つが逆符号で互いの大きさの3割未満まで打ち消し合う点だった。つまり、この量の「最適な $n$」は綱引きの釣り合いではなく、偶然の打ち消し合いで決まっている。実機でこの量だけを見ると、最適な $n$ を誤って選ぶおそれがある。
   - 「雑音は $\langle Z_0\rangle$ を必ず 0 に近づける」も成り立たない（720 条件中 18 件の反例。雑音なしの値が 0 に近いとき）。

## 指標ごとの指数 $n^*\propto p^s$（`exponents.py`、`results/sweep_exponents_exponents.csv`）

誤差を $\frac a{n^q}+bpn$ とすると $n^*\propto p^{-1/(q+1)}$。$q$ は「何で測るか」で変わる。$N=2,4,5$、$p=0.0002$〜$0.05$、$n\le80$ で当てはめた結果：

| 指標 | 予想（1次） | モデルの $s$（1次） | 予想（2次） | モデルの $s$（2次） |
|---|---|---|---|---|
| トレース距離（距離） | $-1/2$ | −0.48〜−0.49 | $-1/3$ | −0.33 |
| 不忠実度（距離の2乗） | $-1/3$ | −0.32 | $-1/5$ | −0.20 |
| 局所的な量 $\langle Z_0\rangle$ | $-1/3$（Layden の条件で $q=2$） | −0.33 | $-1/3$ | −0.33（実際の $n^*$ は −0.14〜−0.56 とばらつく） |

- **Knee–Munro (2015) の「距離で測れば1次で $p^{-1/2}$」と、ここでの「不忠実度で $p^{-1/3}$」は、同じ模型の中で指標の違いとしてつながる。**
- 局所的な量の1次は、トロッター分解なのに $-1/2$ ではなく $-1/3$（$c_1=0$ のため誤差が $1/n^2$）。
- 局所的な量の2次は、モデルでは $-1/3$ だが、実際の $n^*$ は打ち消し合いと $n^*=2$ の反例で指数が定まらない。
- 整数の $n^*$ から直接当てはめた指数（`s_actual`）は、予想より絶対値がやや小さい（$n^*$ が小さいと整数に丸める影響が大きい）。モデルの指数（`s_model`）は `test_exponent_depends_on_metric` で予想と 0.04 以内であることを確認。

## 先行研究との関係（2026年10月4日の調査、`literature-scout`）

| ここの結果 | 先行研究 |
|---|---|
| 誤差 $\frac a{n^q}+bpn$ から $n^*$ を求める枠組み | 既知。Knee–Munro (PRA 91, 052327, 2015; arXiv:1502.04536) は1次で距離（トレースノルムなど）を使い $n^*\propto p^{-1/2}$。Endo ら (arXiv:1808.03623)、Xu ら (arXiv:2504.10247) も同じ形 |
| 結果1：不忠実度では $q\approx2\times$次数、$n^*\propto p^{-1/3}$（1次）・$p^{-1/5}$（2次） | 距離で測る Knee–Munro の $p^{-1/2}$ と、指標（不忠実度＝距離の2乗）の違いで説明がつく。同じ模型で指標ごとの指数を並べた文献は見つからなかった |
| 1次と2次の雑音込みの比較 | Avtandilyan–Pogosov (Quantum Inf. Process. 24, 8, 2025; arXiv:2405.01131)：横磁場イジング模型などで次数1・2・4を比較。2次が有利になるゲート誤差のしきい値を議論 |
| 結果2：$n^*$ は $N$ によらない | 局所的な量では Trivedi–Cirac (arXiv:2509.17579) が厳密に示している（$n^*\propto\gamma^{-1/(k+d+1)}$、$k$ は次数、$d$ は格子の次元）。局所的なトロッター誤差が $N$ によらないことは Heyl–Hauke–Zoller (Sci. Adv. 5, eaau8342, 2019)、Granet–Dreyer (PRX Quantum 6, 010333, 2025) |
| 結果3：$\langle Z_0\rangle$ では1次でも $1/n^2$ | Layden (arXiv:2107.08032)：項が2つのとき、1次と2次の積は**回路の両端だけ**が違い（$U_1=e^{-iAδ/2}U_2e^{iAδ/2}$ の形）、初期状態が $A$ の固有状態で $A$ と交換する量を測るなら、両端の違いが効かず1次の項が消える。ここでは $\lvert00\cdots0\rangle$ が ZZ の項の固有状態で、$Z_0$ も ZZ の項と交換するので、この命題で説明できる（テストで見つけた「A と B の順を入れ替えても同じ」も、同じ構造の表れ） |
| 結果4：局所的な量での符号つきの打ち消し合い、小さい $n$ で単調でないための予測外れ | **見つからなかった**（新しさの中心になり得る）。小さい $n$ の振る舞いは、Heyl らの「ステップ幅のしきい値（それを越えるとカオス的になる）」と関係する可能性があるが未確認 |
| 誤差の上限の式 | Childs–Su–Tran–Wiebe–Zhu (PRX 11, 011020, 2021; arXiv:1912.08854)。2次の上限 $δ^3(\frac{\lVert[M,[M,O]]\rVert}{12}+\frac{\lVert[O,[O,M]]\rVert}{24})$（$M$ が真ん中）の形は、引用元の記述で確認。反エルミート（各因子がユニタリ）の条件で指数関数の因子が消える。命題番号（PRX 版で Proposition 10 か）は要確認 |

## 結果3の追加調査：Layden の説明だけでは足りない（2026年10月4日、数値のみ）

1次の分解の、局所的な量の誤差の傾き（$N=3$、$t=2$、$n=10$〜$160$ の両対数）：

| 初期状態 | 測る量 | 傾き | 解釈 |
|---|---|---|---|
| $\lvert000\rangle$（ZZ の項の固有状態） | $Z_0$ | −1.97 | Layden の条件どおり $1/n^2$ |
| $\lvert000\rangle$ | $X_0$ | −1.02 | $X_0$ は ZZ の項と交換しないので $1/n$（Layden どおり） |
| $\lvert+++\rangle$（横磁場の項の固有状態） | $X_0$ | −1.92 | 役割を入れ替えた Layden の条件どおり $1/n^2$ |
| $\lvert+++\rangle$ | $Z_0$ | ― | 全スピン反転 $\prod_iX_i$ の対称性で $\langle Z_0\rangle$ が常に 0（誤差は丸め誤差のみ） |
| ランダムな積状態（成分が**実数**） | $Z_0$ | −1.4〜−3.0 | **ZZ の固有状態でないのに $1/n$ より速い**。Layden の条件では説明できない |
| 同じ角度で、**複素数の位相**をつけた積状態 | $Z_0$ | −0.86〜−1.06 | $1/n$ に戻る |

いったん「ハミルトニアン・初期状態・測る量がすべて実数（時間反転の対称性）なら、1次の誤差の1次の部分が消える」という仮説を立てたが、**これは誤りだった**（次の節）。

## 1次の誤差の係数を導出する（仮説の否定）

1次の積はストラング分解の両端に因子を付けた形 $U_1^n=e^{-iBδ/2}\,U_2^n\,e^{iBδ/2}$ に書ける（$U_2$ の誤差は $O(δ^2)$）。両端の因子を $δ$ の1次まで展開し、$H=A+B$ が保存されることから $B(t)-B=-(A(t)-A)$ を使うと、

$$
\langle O\rangle_{U_1^n}-\langle O\rangle_{\text{exact}}=c_1\,δ+O(δ^2),\qquad c_1=-\frac i2\Big(\langle\psi(t)|[A,O]|\psi(t)\rangle-\langle\psi_0|[A,O(t)]|\psi_0\rangle\Big)
$$

（$O(t)=e^{iHt}Oe^{-iHt}$。第1項は終わりの端、第2項は始まりの端から来る）。`trotter_noise.first_order_coefficient` に実装し、`test_first_order_coefficient_formula` で数値（$n=2000$ の誤差 × $n/t$）と一致することを確かめた。

- **$c_1=0$ になる条件**：$O$ が $A$ と交換すれば第1項が、初期状態が $A$ の固有状態なら第2項が消える。両方を満たせば $c_1=0$（Layden の条件。`test_layden_condition_gives_zero_first_order`）。
- **時間反転の仮説は誤り**：実数の積状態から $\langle Z_0\rangle$ を測ると、$c_1$ は 0 ではない（例：0.0136、−0.0083、0.0103）。ただし、複素数の位相をつけた状態の $c_1$（0.10〜0.19）より 10〜20 倍小さい。前の表で実数の状態が「$1/n$ より速い」ように見えたのは、$c_1$ が小さいため、$n\le160$ では $δ^2$ の項がまだ勝っていた（漸近的な範囲に達していなかった）から。反例を `test_time_reversal_hypothesis_is_false` に固定した。
- **教訓**：傾きの当てはめだけで次数を判定すると、係数が小さい項を見落とす。導いた係数を直接計算して確かめる。
- **実数の状態で $c_1$ が小さかった理由も、偶然だった**：同じ実数の状態でも、時刻を変えると $|c_1|$ の最大は $t=2$ での値の5倍を超え（調べた状態で 0.14〜0.77）、複素数の状態と同じくらいの大きさになる。$N=3$ の実数の積状態では、$c_1(t)=0$ となる時刻が状態によらず $t\approx2.02$〜$2.09$ にあり、調べに使った $t=2$ がたまたまその近くだった（$N=2,4$ には $t\approx2$ の共通の零点はない）。`test_small_c1_of_real_states_is_specific_to_N3_t2` に固定。
- **教訓（2つ目）**：1つの条件（$N=3$・$t=2$）のデータだけから一般化しない。時刻や大きさを変えて確かめる。

## 次の一歩

- （任意）$N=3$ の実数の積状態に共通する $c_1$ の零点 $t\approx2.05$ の由来（スペクトルの特別な関係か）。
- ~~指標ごとの指数の表~~ → 完了（上の「指標ごとの指数」）。
- **打ち消し合いの領域の図**：$(n,p)$ の平面に、トロッター部分と雑音部分が打ち消し合う領域を描く（先行研究で見つからなかった点）。
- $N$ を増やす：密度行列で $N\le10$ 程度、それ以上は Qiskit Aer の軌跡法・MPS。
- 実機（IBM、$N=2$〜4）で測る前に、実機の較正データ（CNOT の誤差）から $n^*$ を予測しておく（`quantum-experiment` Skill の手順）。
- ~~Lean：望遠鏡和の不等式~~ → 証明済み（下の「形式証明」）。

## 形式証明

望遠鏡和の不等式 $\lVert U^n-V^n\rVert\le n\lVert U-V\rVert$（$\lVert U\rVert,\lVert V\rVert\le1$）を、一般のノルム環で Lean 4 + Mathlib により証明した（[lean4/QuantumStudy/Telescoping.lean](../../lean4/QuantumStudy/Telescoping.lean)、定理 `norm_pow_sub_pow_le_mul`。行列の ℓ∞ 作用素ノルム版・スペクトルノルム版の系も。`sorry` なし、標準の公理のみ）。トロッター分解の $n$ ステップの誤差を、1ステップの誤差の $n$ 倍で抑える部分（`test_telescoping_inequality` で数値的に確かめた主張）の形式証明にあたる。Mathlib v4.28.0 には、ノルム環でのこの補題はなかった（順序環の `abs_pow_sub_pow_le` のみ）。
