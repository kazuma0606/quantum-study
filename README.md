# quantum

個人の量子コンピューティング学習・実装リポジトリです。量子ソフトウェアエンジニアへの転職を見据えて、**理論の整理 → 実装 → テスト → 可視化**を一続きで積み上げています。

- 微分幾何から量子力学・群論までを、「ベクトル・行列で考える」視点で一貫して整理する
- 理論ノート（Markdown）の数式を、動くコードとテストで確認する
- 段階的に、Qiskit / AWS Braket / OpenQARP を使った量子アルゴリズム実装へ接続する

ロードマップの詳細は [docs/roadmap.md](docs/roadmap.md) を参照してください。

## リポジトリの構成

```
quantum/
├── README.md
├── CLAUDE.md              # Claude Code 向けの作業ガイド
├── REQUIREMENTS.md        # 開発要件・ディレクトリ規約・研究ノート一覧
├── pyproject.toml         # Python 依存関係（uv で管理）
├── docs/                  # ロードマップ・戦略メモ
├── 研究ノート/             # 理論ノート（Markdown）と、その図・生成スクリプト
│   └── figures/           # ノートの図（PNG）と、図を生成する Python スクリプト
└── notebooks/             # 実装・テスト・可視化
    └── foundations/       # 数学・物理の基礎（微分幾何〜量子力学）
```

各 notebooks ディレクトリは、「実装（`<name>.py`）」「テスト（`test_<name>.py`）」「可視化（`<name>.ipynb`）」の3点セットで構成します。数学的な正しさは pytest で担保し、Notebook は動くことが保証された関数を使って見せる場所、という方針です（詳細は [REQUIREMENTS.md](REQUIREMENTS.md)）。

## 研究ノート

理論ノートは [研究ノート/](研究ノート/) にあります。一覧と各ノートの位置づけは [REQUIREMENTS.md](REQUIREMENTS.md) の「研究ノート一覧」にまとめています。

| 分野 | ノート |
|---|---|
| 微分幾何・ベクトル解析 | [計量テンソルと共変反変_まとめ](研究ノート/計量テンソルと共変反変_まとめ.md)、[球座標の計量テンソル計算例](研究ノート/球座標の計量テンソル計算例.md)、[christoffel_riemann_intro](研究ノート/christoffel_riemann_intro.md)、[nonlinear_laplacian_p_laplacian](研究ノート/nonlinear_laplacian_p_laplacian.md) |
| 群論・代数 | [pauli_matrices_derivation_and_group](研究ノート/pauli_matrices_derivation_and_group.md)、[unitary_matrix_full_decomposition](研究ノート/unitary_matrix_full_decomposition.md)、[det_exp_trace_proof](研究ノート/det_exp_trace_proof.md)、[generalized_pauli_and_sun_generators](研究ノート/generalized_pauli_and_sun_generators.md)、[classical_and_exceptional_lie_groups](研究ノート/classical_and_exceptional_lie_groups.md)、[quaternions_pauli_matrices](研究ノート/quaternions_pauli_matrices.md)、[complex_numbers_geometry](研究ノート/complex_numbers_geometry.md) |
| 量子力学 | [angular_momentum_ladder_operators](研究ノート/angular_momentum_ladder_operators.md)、[bra_ket_notation_path_integral](研究ノート/bra_ket_notation_path_integral.md)、[hydrogen_atom_legendre_laguerre](研究ノート/hydrogen_atom_legendre_laguerre.md)、[density_matrix_bracket_notation](研究ノート/density_matrix_bracket_notation.md) |

### 図と表の入った長編ノート

[christoffel_riemann_intro.md](研究ノート/christoffel_riemann_intro.md)（クリストッフェル記号とリーマン曲率テンソル）には、本文のほかに、付録A〜C（ガウス・コダッツィ方程式、ボネの定理、ADM 拘束条件）と、次のものがあります。

- 図：[研究ノート/figures/](研究ノート/figures/) に22枚（基底ベクトルの変化、並行移動、主曲率、トーラスの曲率、時空図など）
- 添字の読み方の図：自由添字とダミー添字、δ による添字のすり替え、$\Gamma$ とリーマン曲率テンソルの添字の意味
- 表、Mermaid の図、重要な公式の白いカード

図は matplotlib で生成しています。図によっては、本文の公式（ガウスの公式、余因子行列の規則、双曲面の計量など）が成り立つことを、スクリプト内で数値確認してから描いています。

### ノートの表示について

ノートは、数式（`$...$`、`$$...$$`）と Mermaid を含む Markdown です。VS Code の Markdown プレビュー（数式は KaTeX）で確認しています。Mermaid の描画には、プレビュー用の拡張が必要です。

GitHub 上では、数式のエンジンが異なるため、一部の表現（`\colorbox`、`\fcolorbox` によるカードなど）の見え方が変わる可能性があります。

## セットアップ

Python 3.12 以上と、[uv](https://docs.astral.sh/uv/) を使います。

```bash
# 依存関係のインストール
uv sync

# テストの実行
uv run pytest

# Jupyter の起動
uv run jupyter lab
```

主な依存パッケージは、qiskit、qiskit-aer、numpy、scipy、sympy、matplotlib、jupyter です（開発用：pytest）。

### 図の再生成

図は、次のスクリプトで再生成できます（リポジトリのルートから実行）。

```bash
uv run python 研究ノート/figures/make_christoffel_figures.py   # 図1〜3（基底ベクトル・並行移動・主曲率）
uv run python 研究ノート/figures/make_extra_figures.py         # 図4〜8（Γ≠0でも平坦、球面、測地線、円柱、ADM）
uv run python 研究ノート/figures/make_cofactor_figure.py       # 図9（余因子行列）
uv run python 研究ノート/figures/make_index_figures.py         # 図10〜13（添字の読み方）
uv run python 研究ノート/figures/make_appendix_figures.py      # 図14〜22（付録A・B・C）
```

`index_typeset.py` は、添字を1つずつ色分け・結線して描くための組版部品で、`make_index_figures.py` から使われます。

## 使う技術（予定を含む）

- **Qiskit** + AerSimulator：ローカルでの量子シミュレーション
- **AWS Braket SDK**：クラウド量子計算、Hybrid Jobs
- **OpenQARP**（富士通）：応用アルゴリズムのフレームワーク（2026年9月にオープンソース公開）
- Python / NumPy / SciPy / SymPy / Jupyter Notebook

## 注意事項

- AWS Braket の実機 QPU は従量課金です。コストの上限を必ず設定してから実行してください。
- IBM Open Plan の実機利用は、28日間で10分の制限があります。実機ジョブは慎重に使ってください。
- OpenQARP はリリース直後のため、公式ドキュメントを都度確認してください。

## 関連ドキュメント

- [docs/roadmap.md](docs/roadmap.md)：ロードマップ
- [docs/foundations_strategy.md](docs/foundations_strategy.md)：foundations/ の構成と方針
- [docs/content_strategy.md](docs/content_strategy.md)：コンテンツ戦略
- [REQUIREMENTS.md](REQUIREMENTS.md)：開発要件・ディレクトリ規約・研究ノート一覧
- [CLAUDE.md](CLAUDE.md)：Claude Code 向けの作業ガイド
