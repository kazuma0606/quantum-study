# 開発要件

## ディレクトリ構成の原則

```
quantum/
├── CLAUDE.md
├── REQUIREMENTS.md          # このファイル
├── pyproject.toml
├── docs/                    # ロードマップ・戦略メモ
├── 研究ノート/               # 理論マークダウン（Claudeとの壁打ちで作成）
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

### 本体依存（追加）

| パッケージ | 用途 |
|-----------|------|
| sympy | 記号計算（ユニタリ行列の導出・交換関係の検証・Christoffel記号の自動計算など） |

SymPy の主な用途：
- Pauli 行列の交換関係を記号的に検証
- `exp(-iθ/2 * σ)` などの行列指数を展開
- `sympy.diffgeom` モジュールで計量テンソル → Christoffel記号・Riemann曲率テンソルを自動計算
- Euler-Lagrange 方程式の記号的な導出

## foundations/ の構成

微分幾何から量子計算まで「ベクトル・行列で考える」という視点で一貫させる。
詳細は `docs/foundations_strategy.md` 参照。

| ディレクトリ | テーマ | 研究ノート |
|------------|------|-----------|
| 01_metric_tensor | 計量テンソル・共変反変 | 計量テンソルと共変反変_まとめ.md |
| 02_spherical_coords | 球座標の具体計算 | 球座標の計量テンソル計算例.md |
| 03_christoffel_riemann | Christoffel記号・Riemann曲率 | christoffel_riemann_intro.md |
| 04_laplacian_general | ラプラス・ベルトラミ作用素 | 〃（5節） |
| 05_p_laplacian | p-ラプラシアン・変分原理 | nonlinear_laplacian_p_laplacian.md |
| 06_lagrangian | Lagrange力学・Euler-Lagrange方程式 | （壁打ちで作成予定） |
| 07_hamiltonian | Hamilton力学・Legendre変換 | （壁打ちで作成予定） |
| 08_poisson_bracket | Poisson括弧 → 交換子への橋渡し | （壁打ちで作成予定） |
| 09_matrix_mechanics | Heisenbergの行列力学 | （壁打ちで作成予定） |
| 10_hydrogen_atom | 水素原子（球座標ラプラシアンの応用） | hydrogen_atom_legendre_laguerre.md 等 |
| 11_bra_ket | ブラケット記法・完全性関係 | bra_ket_notation_path_integral.md |
| 12_path_integral | 経路積分の導出 | 〃（Part IV） |
