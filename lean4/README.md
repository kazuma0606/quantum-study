# lean4 ― 研究ノートの命題の形式証明（Lean 4 + Mathlib）

> **作成** 2026-10-03　**更新** 2026-10-04
> 研究ノートの命題を Lean 4 + Mathlib で形式証明する場所の説明。版、ビルドの方法、証明したもの（パウリ行列、det(e^A) = e^{tr A}、シューア分解、望遠鏡和の不等式）。

研究ノートで手計算・SymPy で確かめた命題を、Lean で形式的に証明する場所です（[docs/content_strategy.md](../docs/content_strategy.md) の三層構造の第3層）。

## バージョン

| 項目 | 版 |
|---|---|
| Lean | v4.28.0（`lean-toolchain`） |
| Mathlib | v4.28.0（`lakefile.toml`、`lake-manifest.json`） |

## 構成

| ファイル | 内容 | 対応ノート |
|---|---|---|
| `QuantumStudy/Pauli.lean` | パウリ行列の定義と、積の表（σi² = I、σxσy = iσz など9通り）、交換関係 [σi, σj] = 2iε_ijk σk（3つ）、反交換関係（3つ）、トレース | [パウリ行列](../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md) |
| `QuantumStudy/DetExpTrace.lean` | det(e^A) = e^{tr A} を、**一般の複素正方行列**について証明（`det_exp`。ノートの証明2：行列式の微分可能性、単位行列での微分 = トレース、微分方程式 f′ = (tr A) f）。対角化できる行列・エルミート行列の場合（ノートの証明1）と、「1つの U からは tr = 0 は出ない」反例も含む。Mathlib v4.28.0 では TODO になっている定理 | [det(e^A)=e^{tr A} の証明](../研究ノート/04_群論・代数/det_exp_trace_proof.md) |
| `QuantumStudy/Schur.lean` | **シューア分解**（どの複素正方行列も A = U T U*、U ユニタリ・T 上三角。行列の大きさについての帰納法）と、それを使った**三角化の道**による det(e^A) = e^{tr A}（`det_exp_via_schur`）。シューア分解は Mathlib v4.28.0 にない | [det(e^A)=e^{tr A} の証明](../研究ノート/04_群論・代数/det_exp_trace_proof.md) |
| `QuantumStudy/Telescoping.lean` | **望遠鏡和の不等式**：ノルム環で ‖U‖ ≤ 1、‖V‖ ≤ 1 なら ‖Uⁿ − Vⁿ‖ ≤ n‖U − V‖（`norm_pow_sub_pow_le_mul`。`NormOneClass` も完備性も使わない）。トロッター誤差 ‖(e^{A/n}e^{B/n})ⁿ − e^{A+B}‖ ≤ n‖e^{A/n}e^{B/n} − e^{(A+B)/n}‖ の要。系として、複素行列に ℓ∞ 作用素ノルム・ℓ² 作用素ノルム（スペクトルノルム）を入れた版も含む。Mathlib v4.28.0 に同じ補題はない | [行列の指数関数・交換子・BCH・トロッター](../研究ノート/04_群論・代数/matrix_exponential_commutator_bch_trotter.md) の Part VI §2、実験 [a5_trotter_noise](../experiments/a5_trotter_noise/) |

`QuantumStudy.lean` で import したモジュールが、`lake build` のビルド対象になります。

## 使い方

```bash
cd lean4
lake build                                   # QuantumStudy 全体をビルド（証明の検査）
lake env lean QuantumStudy/Pauli.lean        # 1ファイルだけ検査
```

## 初回の準備

`.lake/`（Mathlib を含み数 GB）はコミットしません（`.gitignore`）。新しい環境では、次のコマンドで Mathlib を取得します。

```bash
cd lean4
lake exe cache get   # Mathlib のビルド済みファイルをダウンロード
lake build
```

この PC では、同じ版を使う既存プロジェクト（`~/don_theory/verify/lean4`）の `.lake/packages` をコピーして用意しました。
