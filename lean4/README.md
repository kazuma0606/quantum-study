# lean4 ― 研究ノートの命題の形式証明（Lean 4 + Mathlib）

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
