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
| `QuantumStudy/Pauli.lean` | パウリ行列の定義、σx σy = iσz、[σx, σy] = 2iσz、σx² = I | [パウリ行列](../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md) |
| `QuantumStudy/DetExpTrace.lean` | det(e^A) = e^{tr A}（書き直し中のため、まだビルド対象に含めていない） | [det(e^A)=e^{tr A} の証明](../研究ノート/04_群論・代数/det_exp_trace_proof.md) |

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
