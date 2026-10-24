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

サブエージェント（`.claude/agents/`）：
- ノートの監査（どれも編集しない。ノート1本、または大きな改訂ごとに、プッシュの前に使う）：`granularity-reviewer`（初学者の目で、説明の粒度と論理の飛躍を見る）、`math-auditor`（式を再計算し、端点・次元・量化を見る）、`note-reviewer`（式番号・縦棒・リンク・日付などの形式を見る）。
- `literature-scout`（先行研究の調査）、`lean-prover`（Lean の証明の試行錯誤）。

ノートの説明の粒度の方針と、予備知識の線引き（「導出済み」の扱い）は `docs/note_style.md`、どの概念がどのノートで導出済みかは `docs/concepts.md`。

補助スクリプトは `tools/`（リンク検査、縦棒の検査、スライダーのチェック、図の書き出しとスクリーンショット、ノートブックの生成スクリプト、ノートの粒度の機械的な点検 `lint_notes.py`）。詳細は `tools/README.md`（`lint_notes.py` の使い方は、スクリプトの先頭の説明を参照）。

### Codex の push 前監査への応答

push が Codex の指摘で止まったら、`uv run --no-sync python tools/audit_workflow.py recent` と `findings <audit_id>` で指摘を確認する。各指摘を、具体的な根拠を確かめて `fix`（修正）、`dispute`（反論）、`human`（人の判断待ち）のいずれかで `respond <finding_id> ... --rationale ... --evidence ...` に記録する。反論では反例・式の導出・テスト結果などを示し、単なる同意や否定を根拠としない。修正をコミットして再度 push すると、Codex が前回の指摘の解消を一件ずつ判定する。二往復しても合意できなければ人に判断を委ねる。研究ノート本文の修正には `docs/note_style.md` の事前承認手順を守る。詳細は `tools/README.md`。

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
