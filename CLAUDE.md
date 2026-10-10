# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

個人の量子コンピューティング学習・実装リポジトリ。式を天下りに受け取らず、導出し、コードで検算し、実機やシミュレータで確かめることが目的。

ロードマップ詳細: `docs/roadmap.md`

## 構成予定

```
quantum/
├── docs/                  # ロードマップ・設計メモ
├── 01_fundamentals/       # Qiskit + 数学基礎（Pauli行列・Hamiltonian・VQE）
├── 02_hardware/           # IBM Open Plan / AWS Braket 実機実験
└── 03_openqarp/           # OpenQARP（富士通）応用アルゴリズム
```

## 主要技術スタック（予定）

- **Qiskit** + AerSimulator: ローカル量子シミュレーション
- **AWS Braket SDK**: クラウド量子計算・Hybrid Jobs
- **OpenQARP**: 富士通製量子アルゴリズムフレームワーク（2026年9月OSS公開）
- Python / NumPy / SciPy / Jupyter Notebook

## Python 環境管理

**uv** を使用。

```bash
# プロジェクト初期化
uv init

# パッケージ追加
uv add qiskit

# 実行
uv run python script.py
uv run jupyter notebook
```

## Julia 環境

Julia 1.12.0 インストール済み。

グローバルに入っているパッケージ: `LinearAlgebra`, `PyCall`, `PackageCompiler`

量子関連パッケージ（Phase 2 以降で追加予定）:
```julia
using Pkg
Pkg.add("Yao")  # 量子回路フレームワーク
```

`PyCall` が入っているため Julia から Python を呼ぶことも可能。

## Lean 4 環境

研究ノートの命題の形式証明は `lean4/`（Lake プロジェクト、ライブラリ名 `QuantumStudy`）に置く。詳細は `lean4/README.md`。

- 版: Lean v4.28.0 / Mathlib v4.28.0（elan の既定も v4.28.0）
- ビルド: `cd lean4 && lake build`（`QuantumStudy.lean` で import したモジュールが対象）
- 1ファイルの検査: `cd lean4 && lake env lean QuantumStudy/Pauli.lean`
- `lean4/.lake/`（Mathlib を含み約 6.5GB）はコミットしない。新しい環境では `lake exe cache get` で取得する

## 作業の手順（Skill・サブエージェント・tools）

くり返す作業の約束事は `.claude/skills/` の Skill にまとめてある。該当する作業では必ず使う。

| Skill | 使う場面 |
|---|---|
| `research-note` | 研究ノートを書く・追記する・直す |
| `note-figures` | ノート用の図（matplotlib）を作る |
| `notebook-gen` | ノートブックを生成スクリプトから作る・直す |
| `quantum-experiment` | シミュレータ・実機（IBM、AWS Braket）で実験する |

サブエージェント（`.claude/agents/`）：`note-reviewer`（ノートの点検、編集しない）、`literature-scout`（先行研究の調査）、`lean-prover`（Lean の証明の試行錯誤）。

補助スクリプトは `tools/`（リンク検査、縦棒の検査、スライダーのチェック、図の書き出しとスクリーンショット、ノートブックの生成スクリプト）。詳細は `tools/README.md`。

## 関連プロジェクト

### Favnir (`C:\Users\yoshi\favnir`)

個人開発中の関数型データ言語（Rust実装）。型付きパイプラインとeffectシステムを中核にしたデータエンジニアリング向け言語。

- コア概念: `type / bind / trf / flw / rune / effect`
- 副作用を型で明示（`!Db`, `!Io`, `!Network` など）
- データ処理向けruneが多数整備済み（csv, parquet, duckdb, s3, aws...）

**quantumリポジトリとの関係**: 直接の統合は現時点では行わない。将来的に量子実験の測定結果・最適化軌跡などのデータ処理パイプラインをFavnirで構築する可能性がある。

```
Qiskit/Braket（量子回路・実行）
    ↓ 測定結果・期待値データ
Favnir（型安全なデータパイプライン）
```

コンテンツ観点では「量子計算の古典側データ処理をFavnirで型安全に扱う」という切り口を将来的に検討。

## 注意事項

- AWS Braket 実機 QPU は従量課金。コスト上限を必ず設定してから実行すること
- IBM Open Plan は 10分 / 28日間 の QPU 利用制限あり。実機ジョブは慎重に
- OpenQARP はリリース直後のため公式ドキュメントを都度確認すること
