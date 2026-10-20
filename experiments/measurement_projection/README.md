# 射影演算子による測定確率の検算

> **作成** 2026-10-17　**更新** 2026-10-20
> 研究ノート「射影演算子による測定確率の計算」（measurement_projection_born_rule.md）の、式と数値を確かめるスクリプトとテスト（49件）。Qiskit での確認を含む。

ノート [measurement_projection_born_rule.md](../../研究ノート/08_量子コンピュータ/measurement_projection_born_rule.md) の本編（テンソル積の作用、ボルン則、$P(x^\ast)=\frac1N$、4候補の例）と、付録A〜C（完全な射影測定とPOVM、結果レジスタの測定とエンタングルメント、クロネッカー積の性質とQiskit の並び順）と、別ノート「[部分トレースと縮約密度行列](../../研究ノート/08_量子コンピュータ/partial_trace_reduced_density_matrix.md)」を、NumPy・SciPy・Qiskit で確かめます。

```bash
uv run python experiments/measurement_projection/measurement_projection.py   # 値を表示する
uv run pytest experiments/measurement_projection -q                          # 検算（49 件）
```

| ファイル | 内容 |
|---|---|
| `measurement_projection.py` | 状態 $\lvert\Psi\rangle$、射影演算子 $M_x=P_x\otimes I$、確率、測定後の状態、係数行列とシュミット係数、測定演算子（Kraus）、Qiskit の回路、部分トレースと干渉の確率 |
| `tests/test_measurement_projection.py` | ノートの各主張に対応する検算（一覧はノートの付録D） |

ノートの付録D に、ノートの箇所とテストの対応表があります。図は [研究ノート/08_量子コンピュータ/figures/make_measurement_projection_figures.py](../../研究ノート/08_量子コンピュータ/figures/make_measurement_projection_figures.py) で作り、各図の値は `assert` でノートの式と照合しています。
