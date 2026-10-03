# NB-03 角運動量とラダー演算子

[角運動量のラダー演算子のノート](../../研究ノート/05_量子力学/angular_momentum_ladder_operators.md)の公式 J±|j,m⟩ = ħ√(j(j+1) − m(m±1)) |j,m±1⟩ から、任意の j の行列を作り、ノートの各 Part の式を確かめます。単位は ħ = 1 です。

| ノートブック | 内容 |
|---|---|
| [01_ladder_operators.ipynb](01_ladder_operators.ipynb) | 任意の j の行列 Jx, Jy, Jz, J± を作る。j = 1/2 がパウリ行列の半分になること。交換関係・J² = j(j+1)・J∓J± = J² − Jz² ∓ Jz などを j = 0〜5 で確かめる。梯子の図（スライダーで j を変える）。「j は整数か半整数でなければならない」理由を、J− で下りるときのノルムの2乗（(j+m)(j−m+1)）が負になるかどうかで確かめる（j を 0.05 刻みで動かせる） |
| [02_spin_rotation_and_qubits.ipynb](02_spin_rotation_and_qubits.ipynb) | 回転したスピン j の測定確率（二項分布、スライダーで j と θ を変える）。2π 回転 = (−1)^{2j}（NB-02 の二重被覆の一般化）と、回転のトレースの式。n 個の量子ビットの全スピンを Qiskit の `SparsePauliOp` で作り、合成スピン j の組の数と、全員上向きから下りた梯子が spin_matrices(n/2) に一致することを確かめる |

## 実行

```bash
uv run jupyter notebook notebooks/03_angular_momentum
```

VS Code のノートブック表示でも動きます。上から順に実行してください。各セルの `assert` が、ノートの式と計算結果の一致を確かめます。スライダー（ipywidgets と plotly の `FigureWidget`）は、カーネルが動いている状態で操作できます。
