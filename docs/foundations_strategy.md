# foundations/ 戦略メモ

## コンセプト

「ベクトル・行列で考える」という一本の視点で、微分幾何から量子計算まで貫く。

各 Notebook は三層構成で統一する：

```
Layer 1: 数式の導出（研究ノートの内容をベースに、天下りを使わず導く）
Layer 2: NumPy で行列として実装・数値検証
Layer 3: 可視化（固有値分布・位相空間図・波動関数・Bloch球など）
```

---

## 全体の接続図

```
計量テンソル g_ij = J^T J（行列）
    │
    ├─ 内積・長さ・角度の一般化
    ├─ 共変・反変（添字の上げ下げ）
    ├─ ラプラス・ベルトラミ作用素
    │       │
    │       └─ p-ラプラシアン（変分原理・非線形）
    │
    └─ 運動エネルギー T = ½ g_ij q̇^i q̇^j
            │
            ▼
        解析力学（Lagrange）
        L = T - V
        Euler-Lagrange 方程式
            │
            │ Legendre 変換
            ▼
        解析力学（Hamilton）
        H = T + V
        正準方程式
            │
            │ Poisson 括弧 {f, g}
            ▼
        対応原理：{f, g} → (1/iħ)[Â, B̂]
            │
            ▼
        行列力学（Heisenberg）
        物理量 = 行列（演算子）
        [x̂, p̂] = iħ を行列で確認
            │
            ├─ 固有値問題 → エネルギー準位・量子状態
            ├─ 水素原子（球座標ラプラシアンの応用）
            ├─ ブラケット記法・完全性関係
            └─ 経路積分
                    │
                    ▼
            量子計算（notebooks/ の本体）
            Pauli 行列・VQE・QAOA
```

**ポイント**: 計量テンソルがラグランジアンの運動エネルギーに直結しているため、
微分幾何の話がそのまま解析力学につながる。

---

## ディレクトリと研究ノートの対応

| ディレクトリ | 内容 | 研究ノート |
|------------|------|-----------|
| 01_metric_tensor | 計量テンソル・共変反変 | 計量テンソルと共変反変_まとめ.md |
| 02_spherical_coords | 球座標の具体計算 | 球座標の計量テンソル計算例.md |
| 03_christoffel_riemann | Christoffel記号・Riemann曲率 | christoffel_riemann_intro.md |
| 04_laplacian_general | ラプラス・ベルトラミ作用素 | 計量テンソルと共変反変_まとめ.md（5節） |
| 05_p_laplacian | p-ラプラシアン・変分原理 | nonlinear_laplacian_p_laplacian.md |
| 06_lagrangian | Lagrange力学・Euler-Lagrange方程式 | （未作成・壁打ちで作る） |
| 07_hamiltonian | Hamilton力学・Legendre変換 | （未作成・壁打ちで作る） |
| 08_poisson_bracket | Poisson括弧 → 交換子への橋渡し | （未作成・壁打ちで作る） |
| 09_matrix_mechanics | Heisenbergの行列力学 | （未作成・壁打ちで作る） |
| 10_hydrogen_atom | 水素原子（球座標ラプラシアンの応用） | hydrogen_atom_legendre_laguerre.md 等 |
| 11_bra_ket | ブラケット記法・完全性関係 | bra_ket_notation_path_integral.md |
| 12_path_integral | 経路積分の導出 | bra_ket_notation_path_integral.md（Part IV） |

「未作成」のノートは Claude との壁打ちで研究ノートを先に作り、
それを基に Notebook を実装する流れで進める。

---

## 可視化の方針

| テーマ | 可視化の内容 |
|--------|------------|
| 計量テンソル | 座標変換による基底ベクトルの変形・内積の変化 |
| 球座標 | 極座標グリッド・体積要素の可視化 |
| Christoffel | 平行移動の経路依存性（平坦 vs 曲面） |
| Lagrange | ポテンシャル面・最小作用の経路 |
| Hamilton | 位相空間の軌道（楕円・カオス） |
| 行列力学 | 調和振動子の行列表現・固有値 |
| 水素原子 | 波動関数・確率密度の3Dプロット |
| 経路積分 | 経路のアニメーション・作用の分布 |

---

## 進め方

1. まず研究ノートが既にある 01〜05 と 10〜12 から Notebook を作り始める
2. 06〜09（解析力学・行列力学）は壁打ちで研究ノートを先に書く
3. 各 Notebook が完成したら `docs/content_strategy.md` の Volume 構成に反映する
