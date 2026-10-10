# 00 テイラー展開 ―多項式近似から行列の指数関数・ヤコビ行列まで

> **作成** 2026-10-04　**更新** 2026-10-04
> テイラー展開を計算して確かめるノートブックの案内。多項式近似と収束半径から、行列の指数関数・ヤコビ行列（1次の近似）まで。

これまでのノート・ノートブックで何度も使ってきた「テイラー展開」と「1次の近似」を、計算して確かめるノートブックです。各節の「考えてみよう」で、スライダーを動かしながら考えます。

| ノートブック | 内容 |
|---|---|
| [01_taylor_euler.ipynb](01_taylor_euler.ipynb) | マクローリン展開の部分和（関数と次数のスライダー）、収束半径（1/(1+x²) は複素平面の ±i で壊れるので半径 1）、ラグランジュの剰余項、オイラーの公式 e^{iθ} = cos θ + i sin θ（部分和が渦を巻いて e^{iπ} = −1 に近づく）、テイラー展開できないなめらかな関数 e^{−1/x²}、丸め誤差（e^{−20} を級数でそのまま足すと桁落ちで崩れる） |
| [02_matrix_exponential.ipynb](02_matrix_exponential.ipynb) | 行列の指数関数の部分和、e^{θJ} = 回転行列（オイラーの公式の行列版）、P e^A P⁻¹ = e^{PAP⁻¹} と対角化・ジョルダン細胞、微分は1次の近似（行列式の展開の各次数、誤差 O(ε²) の傾き 2）、det(e^A) = e^{tr A}（Lean の `det_exp`・`det_exp_via_schur` へのリンク）、e^{A+B} ≠ e^A e^B（ずれ ≈ t²/2 [A,B]）、トロッター分解（誤差 1/n）とストラング分解（1/n²）。Qiskit の `LieTrotter`・`SuzukiTrotter` の回路とも比べる |
| [03_jacobian_linearization.ipynb](03_jacobian_linearization.ipynb) | ヤコビ行列は1次の近似（誤差 O(\|h\|²)）、逆写像のヤコビ行列 = J⁻¹（逆関数定理）、det J = 0 の3つの壊れ方（極座標の原点でつぶれる・折り返し (x², y)・一方向につぶす (x+y, 2x+2y)。写像と点 p をスライダーで選び、J・det J・逆行列を表示）、ニュートン法（誤差がおよそ2乗ずつ減る、det J ≈ 0 では大きく飛ぶ） |

## 実行

```bash
uv run jupyter notebook notebooks/foundations/00_taylor_series
```

上から順に実行してください。`assert` は、計算結果がノートの式（剰余項の上限、Jacobi の公式、det(e^A) = e^{tr A}、誤差の傾きなど）と合っていることを確かめます。2冊目の §4 は SymPy で 3×3 の行列式を展開し、§7 は Qiskit を使います。

## 関連

- [関数・線形写像・微分・積分のノート](../../../研究ノート/01_基礎・ベクトル解析/functions_linear_maps_derivatives_integrals.md)
- [べき級数と収束半径のノート](../../../研究ノート/01_基礎・ベクトル解析/power_series_radius_of_convergence.md)（1冊目の §2・§5 の背景。収束半径と複素平面の特異点、解析接続、e^{−1/x²}）
- [複素数の幾何学のノート](../../../研究ノート/04_群論・代数/complex_numbers_geometry.md)
- [行列の指数関数と交換子のノート](../../../研究ノート/04_群論・代数/matrix_exponential_commutator_bch_trotter.md)（2冊目の §3・§6・§7 の導出。ジョルダン標準形、BCH の公式、トロッター分解とストラング分解）
- [det(e^A) = e^{tr A} の証明](../../../研究ノート/04_群論・代数/det_exp_trace_proof.md)、Lean の証明は [DetExpTrace.lean](../../../lean4/QuantumStudy/DetExpTrace.lean)・[Schur.lean](../../../lean4/QuantumStudy/Schur.lean)
- [多様体入門のノート](../../../研究ノート/03_多様体・微分形式・トポロジー/manifolds_introduction.md)（座標特異点）
