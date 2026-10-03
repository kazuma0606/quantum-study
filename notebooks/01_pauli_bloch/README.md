# NB-01 パウリ行列とブロッホ球

[パウリ行列のノート](../../研究ノート/04_群論・代数/pauli_matrices_derivation_and_group.md)の内容を、NumPy の行列計算とスライダー付きの図で確かめ、Qiskit の `quantum_info` で答え合わせをします（量子回路とアルゴリズムは Phase 2 で扱います）。

| ノートブック | 内容 | 対応するノートの Part |
|---|---|---|
| [01_pauli_algebra.ipynb](01_pauli_algebra.ipynb) | パウリ行列の性質の表、積の表（ε_ijk）、交換関係・反交換関係、(a·σ)(b·σ) = (a·b)I + i(a×b)·σ（スライダーで b を動かす）、行列の展開。Qiskit の `Pauli`・`SparsePauliOp` との比較（`dot` と `compose` の順序の違い） | Part II・IV・V |
| [02_bloch_sphere.ipynb](02_bloch_sphere.ipynb) | ブロッホ球（θ・φ・大域位相のスライダー）、期待値と射影、重なり、測定のサンプリング（`Statevector.sample_counts`）、混合状態と純度（`DensityMatrix`）、Qiskit の Bloch 球の描画 | Part VI |

## 実行

```bash
uv run jupyter notebook notebooks/01_pauli_bloch
```

VS Code のノートブック表示でも動きます。上から順に実行してください。各セルの `assert` が、ノートの式と計算結果の一致を確かめます。スライダー（ipywidgets と plotly の `FigureWidget`）は、カーネルが動いている状態で操作できます。図の描画に数秒かかることがあります。
