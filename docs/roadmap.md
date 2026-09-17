# 量子コンピューティング ロードマップ

## 背景・目的

- 現職スキル: Python / AI・機械学習 / 数値計算 / データ分析 / Rust / Linux / OSS開発 / 医療AI研究（修士）
- 数学ベース: 行列・テンソル・固有値問題・変分法・Pauli行列・Hamiltonian まで自分で掘り進めている
- 目標: 量子ソフトウェアエンジニアとして転職できる実績を作る（量子だけでなく AI x HPC x 量子の境界領域を狙う）

---

## 主要ツール・プラットフォーム

### Qiskit (IBM)
- 量子プログラミングの教材として最適
- AerSimulator でローカル無料実行
- IBM Open Plan: 実機 10分 / 28日間 無料

### AWS Braket
- 量子計算のクラウド基盤として位置づけ
- 複数ベンダーの QPU にアクセス（IonQ / IQM / Rigetti / QuEra など）
- Hybrid Jobs: VQE/QAOA などの量子・古典ハイブリッドループを AWS で管理
- CUDA-Q との連携も可能
- 既存の AWS / Python / GPU スキルと相性が良い

### OpenQARP (富士通)
- 2026年9月15日オープンソース公開
- 「applications library, not a gate library」という位置づけ
- VQE / VQD / SSVQE / ADAPT-VQE / QAOA / QPE 等を実装済み
- 量子化学・Hamiltonian・Jordan-Wigner変換・ノイズシミュレーション等も扱う
- 富士通の40量子ビット大規模シミュレータへの接続も視野
- GitHub: https://openqarp.github.io/openqarp/source/getting_started.html

---

## 研究ノートの現状（理論カバレッジ）

`研究ノート/` に以下が整備済み。これらが Notebook 実装の理論バックボーンになる。

| ファイル | 内容 |
|---------|------|
| pauli_matrices_derivation_and_group.md | Pauli行列・SU(2)・Lie代数・Clifford代数・Pauli群 |
| angular_momentum_ladder_operators.md | ラダー演算子・係数導出・スピン1/2 |
| bra_ket_notation_path_integral.md | ブラケット記法・完全性関係・経路積分導出 |
| hydrogen_atom_legendre_laguerre.md | 水素原子・Legendre/Laguerre関数 |
| 水素原子_変数分離とルジャンドルラゲール陪関数.md | 同上（日本語版） |
| hydrogen_textbook_notation.md | 教科書記法の整理 |
| unitary_matrix_full_decomposition.md | ユニタリ行列の分解 |
| unitary_matrix_phase_separation_derivation.md | 位相分離の導出 |
| 計量テンソルと共変反変_まとめ.md | 計量テンソル・共変/反変 |
| 球座標の計量テンソル計算例.md | 球座標での具体計算 |
| christoffel_riemann_intro.md | Christoffel記号・Riemann曲率テンソル |
| nonlinear_laplacian_p_laplacian.md | p-ラプラシアン |

---

## ロードマップ

全体方針: 研究ノートの理論を Jupyter Notebook でコード化・可視化しながら、
段階的に量子アルゴリズム実装へ接続していく。

### Phase 1: 量子基礎の可視化・検証（進行中）

**目標**: 研究ノートの数式を動くコードと視覚で確認する

各 Notebook の構成イメージ（数式導出 → NumPy/SciPy 実装 → 可視化）:

```
NB-01: Pauli行列と量子状態
  Pauli行列の性質・交換関係を行列計算で検証
  Bloch球上の量子状態可視化

NB-02: SU(2)・ユニタリ変換
  exp(-iθσ/2) の実装・回転の可視化

NB-03: 角運動量とラダー演算子
  スピン1/2 の行列表現・固有値・係数の検証

NB-04: ブラケット記法と期待値
  完全性関係の数値的確認・演算子の期待値計算

NB-05: 水素原子の波動関数
  Legendre/Laguerre 関数のプロット・確率密度の可視化

NB-06: Hamiltonian と固有値問題
  簡単なスピン系の Hamiltonian → 固有値・固有状態
  → VQE への橋渡し
```

- ツール: Qiskit + AerSimulator（ローカル・無料）、NumPy/SciPy、matplotlib

### Phase 2: 量子回路・アルゴリズム実装

**目標**: Phase 1 の数学を量子回路・アルゴリズムに落とし込む

```
NB-07: 量子回路の基礎（Bell状態・量子テレポーテーション）
NB-08: VQE の実装（E(θ) = <ψ(θ)|H|ψ(θ)> の最小化）
NB-09: QAOA の実装
NB-10: ノイズモデルとエラー緩和
```

### Phase 3: クラウド・実機

**目標**: 実機で動かした経験を作る

```
Qiskit → IBM Open Plan（実機 10分/28日）
↓
AWS Braket → Local / Simulator / Hybrid Jobs
↓
実機 QPU（IonQ / IQM 等）で小規模回路を検証
```

- 成果物: 実機結果入り Notebook / コスト記録
- 参考: Braket ローカル state-vector simulator は ~25量子ビットまで

### Phase 4: OpenQARP + 量子化学

**目標**: 量子化学・科学計算側の応用に踏み込む

```
OpenQARP Getting Started
↓
VQE / QAOA / QPE の応用実装
↓
Hamiltonian → Jordan-Wigner変換
↓
分子エネルギー計算
↓
富士通大規模シミュレータ（接続可能であれば）
```

---

## リポジトリ構成案

```
quantum/
├── docs/                   # ロードマップ・設計メモ
├── 研究ノート/              # 理論マークダウン（既存）
├── notebooks/              # Jupyter Notebook 本体
│   ├── 01_pauli_bloch/
│   ├── 02_su2_rotation/
│   ├── 03_angular_momentum/
│   ├── 04_braket_expectation/
│   ├── 05_hydrogen_wavefunction/
│   ├── 06_hamiltonian_eigenvalue/
│   ├── 07_quantum_circuits/
│   ├── 08_vqe/
│   ├── 09_qaoa/
│   ├── 10_noise_mitigation/
│   ├── 11_ibm_hardware/
│   ├── 12_braket/
│   └── 13_openqarp/
└── src/                    # 共通ユーティリティ（可視化関数など）
```

---

## キャリア観点でのポイント

| 実績 | 採用側への訴求 |
|------|--------------|
| VQE を数学から実装 | 「量子アルゴリズムを理解している」の証明 |
| IBM / Braket 実機結果 | 「実機経験あり」と明示できる |
| Hybrid Jobs 実装 | 「クラウド量子計算ワークフローを組める」 |
| OpenQARP 利用 | 富士通系ポジションへのアピール |
| GitHub で公開 | 採用担当が確認できる形にする |

- 狙うポジション: 量子ソフトウェアエンジニア / 量子アルゴリズムエンジニア / HPC x 量子 / AI x 量子
- 富士通・IBM Japan が主な候補（いずれもソフトウェア側は数学・Python から参入余地あり）

---

## 関連プロジェクト・言語

### Favnir (`C:\Users\yoshi\favnir`)

個人開発中の関数型データ言語（Rust実装）。
詳細は `CLAUDE.md` 参照。

量子リポジトリとの接続タイミング:
- Phase 2 以降で実験データが実際に出てきたら検討
- VQE最適化軌跡 `(θ, E(θ))`、QPU測定結果などの収集・保存パイプラインが候補

### Lean4

形式証明言語。研究ノートの数学的命題をコードとして証明する用途。
詳細は `docs/content_strategy.md` 参照。
Phase 1 と並走して小さく始める（Pauli行列の交換関係あたりから）。

### Julia

数値計算・科学計算に強い言語。量子フレームワーク **Yao.jl** が存在する。

- PythonのNotebookと同様にIJuliaカーネルでJupyter上で動かせる
- 「同じVQEをPython(Qiskit)とJulia(Yao.jl)で実装して比較」はコンテンツとして有効
- Phase 2 以降で Python と並走して取り入れる想定
- かじった経験あり（ゼロスタートではない）

---

## メモ・懸念点（壁打ち用）

- IBM Open Plan の10分/28日制限は Phase 2 で実際にどう使うか要検討
- AWS Braket の実機 QPU コストは従量課金。予算上限設定が必要
- OpenQARP は公開直後なので情報が少ない。公式ドキュメントを逐次確認
- Qiskit と Braket SDK の違い（回路記法・バックエンド切り替え）は実際に触って確認
