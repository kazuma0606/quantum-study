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
├── 研究ノート/             # 理論ノート（Markdown）。ジャンル別のフォルダに分けている
│   ├── 01_基礎・ベクトル解析/
│   ├── 02_微分幾何/        # クリストッフェル記号のノートと、その図・動画（figures/）
│   ├── 03_多様体・微分形式・トポロジー/
│   ├── 04_群論・代数/
│   ├── 05_量子力学/
│   └── tools/             # ノート用の補助スクリプト（目次の生成など）
└── notebooks/             # 実装・テスト・可視化
    └── foundations/       # 数学・物理の基礎（微分幾何〜量子力学）
```

各 notebooks ディレクトリは、「実装（`<name>.py`）」「テスト（`test_<name>.py`）」「可視化（`<name>.ipynb`）」の3点セットで構成します。数学的な正しさは pytest で担保し、Notebook は動くことが保証された関数を使って見せる場所、という方針です（詳細は [REQUIREMENTS.md](REQUIREMENTS.md)）。

## 研究ノート

理論ノートは [研究ノート/](研究ノート/) にあり、ジャンル別のフォルダに分けています（全31本）。各ノートが Notebook 実装とどう対応するかは、[REQUIREMENTS.md](REQUIREMENTS.md) の「研究ノート一覧」を参照してください。

### 01_基礎・ベクトル解析

| ノート | 内容 |
|---|---|
| [functions_linear_maps_derivatives_integrals](研究ノート/01_基礎・ベクトル解析/functions_linear_maps_derivatives_integrals.md) | 関数・線形写像・微分・積分を、統一的な視点でまとめ直す |
| [grad_div_rot_identities_full_derivation](研究ノート/01_基礎・ベクトル解析/grad_div_rot_identities_full_derivation.md) | grad・div・rot の恒等式の、途中式を省略しない証明 |
| [lagrange_multipliers](研究ノート/01_基礎・ベクトル解析/lagrange_multipliers.md) | ラグランジュの未定乗数法（なぜ勾配が平行になるのか） |
| [nonlinear_laplacian_p_laplacian](研究ノート/01_基礎・ベクトル解析/nonlinear_laplacian_p_laplacian.md) | $p$-ラプラシアンの導出と具体例 |

### 02_微分幾何

| ノート | 内容 |
|---|---|
| [計量テンソルと共変反変_まとめ](研究ノート/02_微分幾何/計量テンソルと共変反変_まとめ.md) | 計量テンソルによるベクトル解析の一般化 |
| [球座標の計量テンソル計算例](研究ノート/02_微分幾何/球座標の計量テンソル計算例.md) | 3次元極座標での計量テンソルの具体的計算 |
| [christoffel_riemann_intro](研究ノート/02_微分幾何/christoffel_riemann_intro.md) | クリストッフェル記号とリーマン曲率テンソル（付録A〜C、図・動画つき） |
| [ricci_tensor_einstein_equations](研究ノート/02_微分幾何/ricci_tensor_einstein_equations.md) | リッチテンソル・スカラー曲率・アインシュタイン方程式 |
| [lie_derivative](研究ノート/02_微分幾何/lie_derivative.md) | リー微分（流れに沿った、座標に依らない微分） |
| [abstract_differential_geometry_bridge](研究ノート/02_微分幾何/abstract_differential_geometry_bridge.md) | 抽象的な微分幾何との橋渡し（接ベクトル・接続の正式な定義） |

### 03_多様体・微分形式・トポロジー

| ノート | 内容 |
|---|---|
| [manifolds_introduction](研究ノート/03_多様体・微分形式・トポロジー/manifolds_introduction.md) | 多様体入門 |
| [topology_introduction](研究ノート/03_多様体・微分形式・トポロジー/topology_introduction.md) | トポロジー入門（ガウス・ボンネの定理を入り口に） |
| [differential_forms_hodge_star](研究ノート/03_多様体・微分形式・トポロジー/differential_forms_hodge_star.md) | 微分形式とホッジスター演算子 |
| [poincare_lemma_d_squared_zero](研究ノート/03_多様体・微分形式・トポロジー/poincare_lemma_d_squared_zero.md) | ポアンカレの補題 $d^2=0$ |
| [integration_algebraic_structure_stokes](研究ノート/03_多様体・微分形式・トポロジー/integration_algebraic_structure_stokes.md) | 積分の代数的構造（ストークスの定理からド・ラームコホモロジーまで） |
| [matrix_valued_forms_gauge_theory](研究ノート/03_多様体・微分形式・トポロジー/matrix_valued_forms_gauge_theory.md) | 行列値の微分形式・ゲージ理論 |
| [complex_manifolds_twistor_theory](研究ノート/03_多様体・微分形式・トポロジー/complex_manifolds_twistor_theory.md) | 複素多様体の分類とツイスター理論 |

### 04_群論・代数

| ノート | 内容 |
|---|---|
| [pauli_matrices_derivation_and_group](研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md) | パウリ行列の導出・交換関係・群構造 |
| [unitary_matrix_full_decomposition](研究ノート/04_群論・代数/unitary_matrix_full_decomposition.md) | ユニタリ行列の絶対値・位相分離 |
| [unitary_matrix_phase_separation_derivation](研究ノート/04_群論・代数/unitary_matrix_phase_separation_derivation.md) | ユニタリ行列の位相分離パラメータ化 |
| [det_exp_trace_proof](研究ノート/04_群論・代数/det_exp_trace_proof.md) | $\det(e^A)=e^{\operatorname{tr}A}$ の証明 |
| [generalized_pauli_and_sun_generators](研究ノート/04_群論・代数/generalized_pauli_and_sun_generators.md) | 一般化パウリ行列と $SU(n)$ の生成子 |
| [classical_and_exceptional_lie_groups](研究ノート/04_群論・代数/classical_and_exceptional_lie_groups.md) | 古典群と例外型リー群（分類の全体像） |
| [quaternions_pauli_matrices](研究ノート/04_群論・代数/quaternions_pauli_matrices.md) | 四元数とパウリ行列の対応 |
| [complex_numbers_geometry](研究ノート/04_群論・代数/complex_numbers_geometry.md) | 複素数の幾何学的構造（$\mathbb C\cong\mathbb R^2$ から $U(1)$ まで） |

### 05_量子力学

| ノート | 内容 |
|---|---|
| [angular_momentum_ladder_operators](研究ノート/05_量子力学/angular_momentum_ladder_operators.md) | 角運動量のラダー演算子 |
| [bra_ket_notation_path_integral](研究ノート/05_量子力学/bra_ket_notation_path_integral.md) | ブラケット記法と経路積分への道 |
| [density_matrix_bracket_notation](研究ノート/05_量子力学/density_matrix_bracket_notation.md) | 密度行列とブラケット記法 |
| [hydrogen_atom_legendre_laguerre](研究ノート/05_量子力学/hydrogen_atom_legendre_laguerre.md) | 水素原子（変数分離から、ルジャンドル・ラゲール陪関数まで） |
| [hydrogen_textbook_notation](研究ノート/05_量子力学/hydrogen_textbook_notation.md) | 水素原子（教科書の記法に沿った導出） |
| [水素原子_変数分離とルジャンドルラゲール陪関数](研究ノート/05_量子力学/水素原子_変数分離とルジャンドルラゲール陪関数.md) | 水素原子（`hydrogen_atom_legendre_laguerre` の日本語版） |

学習の候補と今後の計画は、[docs/learning_roadmap.md](docs/learning_roadmap.md) と [docs/roadmap.md](docs/roadmap.md) にあります。

### 図・動画・目次の入った長編ノート

[christoffel_riemann_intro.md](研究ノート/02_微分幾何/christoffel_riemann_intro.md)（クリストッフェル記号とリーマン曲率テンソル）には、本文のほかに、付録A〜C（ガウス・コダッツィ方程式、ボネの定理、ADM 拘束条件）と、次のものがあります。

- 図：[研究ノート/02_微分幾何/figures/](研究ノート/02_微分幾何/figures/) に22枚（基底ベクトルの変化、並行移動、主曲率、トーラスの曲率、時空図など）
- 動画（GIF）：同じ `figures/` に6本（並行移動、混合偏微分の交換、座標の四角形のずれ、極座標の基底、δ の添字のすり替え、ガウス正規座標）
- 添字の読み方の図：自由添字とダミー添字、δ による添字のすり替え、$\Gamma$ とリーマン曲率テンソルの添字の意味
- 目次、各 Part の小目次、表、Mermaid の図、重要な公式の白いカード

[lie_derivative.md](研究ノート/02_微分幾何/lie_derivative.md)（リー微分）にも、目次と、図7枚・動画（GIF）2本があります（流れの例、押し出しと引き戻し、流れで四角形を一周したずれ、面積と発散、キリングベクトル、クレローの関係など。ファイル名は `lie` で始まります）。

[functions_linear_maps_derivatives_integrals.md](研究ノート/01_基礎・ベクトル解析/functions_linear_maps_derivatives_integrals.md)（関数・線形写像・微分・積分）にも、目次と図9枚があります（単射・全射の矢印図、極座標の写像、核と像、逆関数定理の条件、変数変換、行列指数関数、ノルムと内積、フーリエ級数など。図は `研究ノート/01_基礎・ベクトル解析/figures/` にあります）。

図と動画は matplotlib で生成しています。図によっては、本文の公式（ガウスの公式、余因子行列の規則、双曲面の計量など）が成り立つことを、スクリプト内で数値確認してから描いています。

目次と小目次は、見出しから自動で生成します（見出しを直したあとに実行します）。

```bash
uv run python 研究ノート/tools/build_toc.py                                        # クリストッフェル記号のノート
uv run python 研究ノート/tools/build_toc.py 研究ノート/02_微分幾何/lie_derivative.md   # リー微分のノート
uv run python 研究ノート/tools/build_toc.py 研究ノート/01_基礎・ベクトル解析/functions_linear_maps_derivatives_integrals.md   # 関数・線形写像・微分・積分のノート
```

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
uv run python 研究ノート/02_微分幾何/figures/make_christoffel_figures.py   # 図1〜3（基底ベクトル・並行移動・主曲率）
uv run python 研究ノート/02_微分幾何/figures/make_extra_figures.py         # 図4〜8（Γ≠0でも平坦、球面、測地線、円柱、ADM）
uv run python 研究ノート/02_微分幾何/figures/make_cofactor_figure.py       # 図9（余因子行列）
uv run python 研究ノート/02_微分幾何/figures/make_index_figures.py         # 図10〜13（添字の読み方）
uv run python 研究ノート/02_微分幾何/figures/make_appendix_figures.py      # 図14〜22（付録A・B・C）
uv run python 研究ノート/02_微分幾何/figures/make_animations.py           # 動画（GIF）6本。--mp4 を付けると MP4 も出力（ffmpeg が必要）
uv run python 研究ノート/02_微分幾何/figures/make_lie_figures.py          # リー微分のノートの図7枚（lie01〜lie07）
uv run python 研究ノート/02_微分幾何/figures/make_lie_animations.py       # リー微分のノートの動画（GIF）2本
uv run python 研究ノート/01_基礎・ベクトル解析/figures/make_flm_figures.py # 関数・線形写像・微分・積分のノートの図9枚（flm01〜flm09）
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
