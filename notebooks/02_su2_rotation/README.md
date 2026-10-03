# NB-02 SU(2) とブロッホ球の回転

[パウリ行列のノート](../../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md)の Part VII（指数関数・ブロッホ球の回転・二重被覆）と、[ユニタリ行列のノート](../../研究ノート/04_群論・代数/unitary_matrix_full_decomposition.md)の Part VIII〜IX（R_z, R_y と ZYZ 分解）を、NumPy の実装とスライダー付きの図で確かめ、Qiskit で答え合わせをします（量子回路は Phase 2 で扱います）。

| ノートブック | 内容 |
|---|---|
| [01_su2_exponential.ipynb](01_su2_exponential.ipynb) | e^{−iθ n·σ/2} の閉じた形を、級数の部分和（収束のグラフ）と scipy の `expm` で確かめる。SU(2) の元から回転軸と角度を取り出す。Qiskit の `RXGate`・`RYGate`・`RZGate`・`PhaseGate`・`UGate` との関係（大域位相の違い）。二重被覆（θ = 2π で −I） |
| [02_bloch_rotation.ipynb](02_bloch_rotation.ipynb) | U からブロッホ球の回転行列 R を作り、ロドリゲスの公式・回転の合成・R(−U) = R(U) を確かめる。軸・角度・初期状態のスライダーで回転を見る。回転の順序による違い（Rx と Ry。小さな角度では z 軸まわりの α² の回転）。ZYZ 分解を自前で計算し、Qiskit の `OneQubitEulerDecomposer` と比べ、3つの回転を順に進めて見る |

## 実行

```bash
uv run jupyter notebook notebooks/02_su2_rotation
```

VS Code のノートブック表示でも動きます。上から順に実行してください。各セルの `assert` が、ノートの式と計算結果の一致を確かめます。スライダー（ipywidgets と plotly の `FigureWidget`）は、カーネルが動いている状態で操作できます。
