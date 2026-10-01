# 開発要件

## ディレクトリ構成の原則

```
quantum/
├── CLAUDE.md
├── REQUIREMENTS.md          # このファイル
├── pyproject.toml
├── docs/                    # ロードマップ・戦略メモ
├── 研究ノート/               # 理論マークダウン（Claudeとの壁打ちで作成）。ジャンル別に
│   │                         #   01_基礎・ベクトル解析 / 02_微分幾何 / 03_多様体・微分形式・トポロジー
│   │                         #   / 04_群論・代数 / 05_量子力学 のフォルダへ分類
│   └── tools/                # ノート用の補助スクリプト（目次の生成など）
└── notebooks/
    ├── foundations/         # 数学・物理の基礎（微分幾何〜量子力学）
    │   └── 01_metric_tensor/
    │       ├── metric_tensor.py       # 実装
    │       ├── test_metric_tensor.py  # テスト
    │       └── 01_metric_tensor.ipynb # 可視化・説明
    └── 01_pauli_bloch/      # 量子計算（同じ構成）
        ├── pauli_bloch.py
        ├── test_pauli_bloch.py
        └── 01_pauli_bloch.ipynb
```

## 各ディレクトリの構成ルール

各 Notebook ディレクトリは必ず以下の3ファイルセットで構成する：

| ファイル | 役割 |
|---------|------|
| `<name>.py` | 実装（純粋な関数・数値計算） |
| `test_<name>.py` | pytest テスト（数学的な正しさを保証） |
| `<name>.ipynb` | 可視化・説明（.py から import して使う） |

**方針**: Notebook は「動くことが保証された関数を使って見せる場所」。
数学的な正しさは `.py` + `pytest` で担保する。

## 開発フロー

```
1. 研究ノート（Markdown）で理論を整理
        ↓
2. .py に実装（純粋関数として）
        ↓
3. test_*.py で pytest テスト
        ↓
4. .ipynb で import → 可視化・説明
```

## コマンド

```bash
# テスト実行（全体）
uv run pytest

# テスト実行（特定ディレクトリ）
uv run pytest notebooks/foundations/01_metric_tensor/

# テスト実行（詳細表示）
uv run pytest -v

# Jupyter 起動
uv run jupyter lab
```

## Python 環境

- パッケージ管理: **uv**
- Python: 3.12.12

### 本体依存

| パッケージ | 用途 |
|-----------|------|
| qiskit | 量子回路 |
| qiskit-aer | ローカルシミュレータ |
| jupyter / jupyterlab | Notebook |
| numpy | 数値計算 |
| scipy | 科学計算 |
| matplotlib | 可視化 |

### 開発依存

| パッケージ | 用途 |
|-----------|------|
| pytest | テスト |

| sympy | 記号計算（ユニタリ行列の導出・交換関係の検証・Christoffel記号の自動計算など） |

SymPy の主な用途：
- Pauli 行列の交換関係を記号的に検証
- `exp(-iθ/2 * σ)` などの行列指数を展開
- `sympy.diffgeom` モジュールで計量テンソル → Christoffel記号・Riemann曲率テンソルを自動計算
- Euler-Lagrange 方程式の記号的な導出

## 研究ノート一覧

壁打ちで作成した理論ノート。各 Notebook の理論バックボーンになる。

### 微分幾何・ベクトル解析

| ファイル | 内容 |
|---------|------|
| 計量テンソルと共変反変_まとめ.md | 計量テンソルの定義・共変/反変・grad/div/ラプラシアンの一般化 |
| 球座標の計量テンソル計算例.md | 球座標での g_ij・√\|g\|・逆計量の具体計算 |
| christoffel_riemann_intro.md | Christoffel記号の定義・計算例（平坦/球面）・Riemann曲率テンソル |
| nonlinear_laplacian_p_laplacian.md | p-ラプラシアンの定義・変分原理からの導出・1次元完全解 |

### 群論・代数

| ファイル | 内容 |
|---------|------|
| pauli_matrices_derivation_and_group.md | SU(2)の生成子としてのPauli行列・交換関係・Lie代数・Pauli群 |
| unitary_matrix_full_decomposition.md | ユニタリ行列の一般形の導出・分解 |
| unitary_matrix_phase_separation_derivation.md | 位相分離の導出 |
| det_exp_trace_proof.md | det(e^A)=e^(tr A) の証明（対角化/Jacobi公式の2経路） |
| generalized_pauli_and_sun_generators.md | SU(n)の生成子・Gell-Mann行列・一般化Pauli行列 |
| classical_and_exceptional_lie_groups.md | Lie群の分類全体像（古典群/例外型）・U(2)・SU(2)・SO(3)の位置づけ |
| quaternions_pauli_matrices.md | 四元数 ↔ Pauli行列の対応・SU(2)↔単位四元数↔S³ |
| complex_numbers_geometry.md | 複素数の幾何学的構造・ℂ≅ℝ²・U(1) |

### 量子力学

| ファイル | 内容 |
|---------|------|
| angular_momentum_ladder_operators.md | ラダー演算子の構成・係数導出・スピン1/2 |
| bra_ket_notation_path_integral.md | ブラケット記法・完全性関係・経路積分の導出 |
| hydrogen_atom_legendre_laguerre.md | 水素原子・Legendre/Laguerre関数 |
| 水素原子_変数分離とルジャンドルラゲール陪関数.md | 同上（日本語版） |
| hydrogen_textbook_notation.md | 教科書記法の整理 |
| density_matrix_bracket_notation.md | 密度行列・Tr(ρÂ)・混合状態・外積の扱い |

---

## foundations/ の構成

微分幾何から量子計算まで「ベクトル・行列で考える」という視点で一貫させる。
詳細は `docs/foundations_strategy.md` 参照。

### 微分幾何・ベクトル解析

| ディレクトリ | テーマ | 研究ノート |
|------------|------|-----------|
| 01_metric_tensor | 計量テンソル・共変反変 | 計量テンソルと共変反変_まとめ.md |
| 02_spherical_coords | 球座標の具体計算 | 球座標の計量テンソル計算例.md |
| 03_christoffel_riemann | Christoffel記号・Riemann曲率 | christoffel_riemann_intro.md |
| 04_laplacian_general | ラプラス・ベルトラミ作用素 | 計量テンソルと共変反変_まとめ.md（5節） |
| 05_p_laplacian | p-ラプラシアン・変分原理 | nonlinear_laplacian_p_laplacian.md |

### 解析力学

| ディレクトリ | テーマ | 研究ノート |
|------------|------|-----------|
| 06_lagrangian | Lagrange力学・Euler-Lagrange方程式 | （壁打ちで作成予定） |
| 07_hamiltonian | Hamilton力学・Legendre変換 | （壁打ちで作成予定） |
| 08_poisson_bracket | Poisson括弧 → 交換子への橋渡し | （壁打ちで作成予定） |

### 群論・代数

| ディレクトリ | テーマ | 研究ノート |
|------------|------|-----------|
| 09_matrix_mechanics | Heisenbergの行列力学・det(e^A)=e^(tr A) | det_exp_trace_proof.md |
| （追加予定）complex_geometry | 複素数の幾何・U(1) | complex_numbers_geometry.md |
| （追加予定）quaternions | 四元数 ↔ Pauli行列・SU(2) | quaternions_pauli_matrices.md |
| （追加予定）lie_groups | Lie群の分類・SU(n)生成子 | classical_and_exceptional_lie_groups.md / generalized_pauli_and_sun_generators.md |

### 量子力学

| ディレクトリ | テーマ | 研究ノート |
|------------|------|-----------|
| 10_hydrogen_atom | 水素原子（球座標ラプラシアンの応用） | hydrogen_atom_legendre_laguerre.md 等 |
| 11_bra_ket | ブラケット記法・完全性関係 | bra_ket_notation_path_integral.md |
| 12_path_integral | 経路積分の導出 | 〃（Part IV） |
| （追加予定）density_matrix | 密度行列・混合状態 | density_matrix_bracket_notation.md |
