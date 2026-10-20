# 概念の一覧 ―どのノートで導出済みか―

> **作成** 2026-10-20　**更新** 2026-10-20
> 研究ノートで使う概念が、どのノートのどの節で詳しく導出されているかの一覧。新しい概念を使うときの「初出か既出か」の判定に使う。

使い方は `docs/note_style.md` の §1 にあります。

- 使いたい概念が表にある → 導出し直さず、「○○ノートで導出済み」とリンクして使う。
- 表にない → このリポジトリで初めて出る概念として詳解し、**同じコミットで表に追加する**。
- 表の「場所」は、詳しい手順つきの導出がある節です。節が分かるものは節まで、まだ確認していないものはノート名だけを書きます（節を確認したら書き足す）。

パスは `研究ノート/` からの相対パスです。

## 量子コンピュータ（08_量子コンピュータ/）

| 概念 | 場所 |
|---|---|
| テンソル積（ベクトル、行列、$(A\otimes B)(u\otimes v)=Au\otimes Bv$） | `08_量子コンピュータ/measurement_projection_born_rule.md` Part III §2-c〜2-e |
| 3つ以上のテンソル積、テンソル積の分解の判定 | 同上 Part III §2-f、§2-g |
| 射影演算子 $P_x=\lvert x\rangle\langle x\rvert$ | 同上 Part II |
| ボルン則、入力レジスタだけを測る確率 | 同上 Part IV |
| テンソル積の性質（混合積、転置、ユニタリ性、トレース、固有値、行列式） | 同上 付録A-1 |
| 射影測定の完全性、測定後の状態、再現性 | 同上 付録A-2〜A-4 |
| 測定演算子、クラウス演算子、トレースが確率になる理由、トレースの巡回性 | 同上 付録A-5-1 |
| POVM | 同上 付録A-5-2 |
| 誤差のある測定、環境を使った見方 | 同上 付録A-5-3 |
| 係数行列、積状態の判定、シュミット分解、エンタングルメントエントロピー | 同上 付録B |
| 教科書と Qiskit の並び順 | 同上 付録C |
| 純粋状態の密度行列、期待値 $\operatorname{tr}(\rho A)$ | `08_量子コンピュータ/partial_trace_reduced_density_matrix.md` Part I §2 |
| 部分トレース、縮約密度行列 | 同上 Part II、Part III |
| 結果レジスタが入力を覚えると干渉が消える | 同上 Part V |
| 環境を使った見方（クラウス表現の導出） | 同上 Part VI |

## 基礎・ベクトル解析（01_）

| 概念 | 場所 |
|---|---|
| 関数、線形写像、微分、積分の統一的な見方 | `01_基礎・ベクトル解析/functions_linear_maps_derivatives_integrals.md` |
| 微分の定義の強さ、対象と構造（微分の地図） | `01_基礎・ベクトル解析/derivative_map.md` |
| 自動微分、余接ベクトル | `01_基礎・ベクトル解析/autodiff_and_coordinates.md` |
| grad、div、rot の恒等式 | `01_基礎・ベクトル解析/grad_div_rot_identities_full_derivation.md` |
| ラグランジュの未定乗数法 | `01_基礎・ベクトル解析/lagrange_multipliers.md` |
| $p$-ラプラシアン | `01_基礎・ベクトル解析/nonlinear_laplacian_p_laplacian.md` |
| べき級数、収束半径 | `01_基礎・ベクトル解析/power_series_radius_of_convergence.md` |

## 微分幾何・多様体（02_、03_）

| 概念 | 場所 |
|---|---|
| 計量テンソル、共変・反変 | `02_微分幾何/計量テンソルと共変反変_まとめ.md`、`02_微分幾何/球座標の計量テンソル計算例.md` |
| ヤコビ行列、ラプラス・ベルトラミ作用素 | `02_微分幾何/laplace_beltrami_from_jacobian_matrix.md` |
| リー微分 | `02_微分幾何/lie_derivative.md` |
| クリストッフェル記号、リーマン曲率 | `02_微分幾何/christoffel_riemann_intro.md` |
| リッチテンソル、アインシュタイン方程式 | `02_微分幾何/ricci_tensor_einstein_equations.md` |
| 接ベクトル、接続（抽象的な微分幾何） | `02_微分幾何/abstract_differential_geometry_bridge.md` |
| 多様体 | `03_多様体・微分形式・トポロジー/manifolds_introduction.md` |
| 微分形式、ホッジスター | `03_多様体・微分形式・トポロジー/differential_forms_hodge_star.md` |
| ポアンカレの補題、$d^2=0$ | `03_多様体・微分形式・トポロジー/poincare_lemma_d_squared_zero.md` |
| ストークスの定理、ド・ラームコホモロジー | `03_多様体・微分形式・トポロジー/integration_algebraic_structure_stokes.md` |
| トポロジー、ガウス・ボンネの定理 | `03_多様体・微分形式・トポロジー/topology_introduction.md` |
| 行列値の微分形式、ゲージ理論 | `03_多様体・微分形式・トポロジー/matrix_valued_forms_gauge_theory.md` |
| 複素多様体、ツイスター理論 | `03_多様体・微分形式・トポロジー/complex_manifolds_twistor_theory.md` |

## 群論・代数（04_）

| 概念 | 場所 |
|---|---|
| パウリ行列、交換関係、ブロッホ球 | `04_群論・代数/pauli_matrices_derivation_and_group.md` |
| 一般化パウリ行列、$SU(n)$ の生成子 | `04_群論・代数/generalized_pauli_and_sun_generators.md` |
| 行列の指数関数、交換子、BCH、トロッター分解 | `04_群論・代数/matrix_exponential_commutator_bch_trotter.md` |
| $\det(e^A)=e^{\operatorname{tr}A}$ | `04_群論・代数/det_exp_trace_proof.md` |
| ユニタリ行列の位相分離 | `04_群論・代数/unitary_matrix_full_decomposition.md`、`04_群論・代数/unitary_matrix_phase_separation_derivation.md` |
| 複素数の幾何 | `04_群論・代数/complex_numbers_geometry.md` |
| 四元数とパウリ行列 | `04_群論・代数/quaternions_pauli_matrices.md` |
| 古典群、例外型リー群 | `04_群論・代数/classical_and_exceptional_lie_groups.md` |

## 量子力学（05_）、確率・統計（06_）、数値計算（07_）

| 概念 | 場所 |
|---|---|
| ブラケット記法、経路積分への接続 | `05_量子力学/bra_ket_notation_path_integral.md` |
| 密度行列とブラケット記法 | `05_量子力学/density_matrix_bracket_notation.md` |
| ノイズのモデル化、T1・脱位相、量子チャネル | `05_量子力学/noise_modeling_through_mri.md` |
| トロッター実験の読み方、イジング模型 | `05_量子力学/trotter_experiment_translation.md` |
| 角運動量のラダー演算子 | `05_量子力学/angular_momentum_ladder_operators.md` |
| 水素原子（変数分離、ルジャンドル・ラゲール） | `05_量子力学/hydrogen_atom_legendre_laguerre.md`、`05_量子力学/hydrogen_textbook_notation.md` |
| 正規化フロー、確率密度の変数変換 | `06_確率・統計/normalizing_flows_introduction.md` |
| ヴァンデルモンド行列、スペクトル微分 | `07_数値計算/vandermonde_finite_difference_spectral.md` |

## 頻出する基本語（初めて使うときに1行で意味を述べれば足りる）

行列の積、転置、複素共役、共役転置、トレースの定義（対角成分の和）、行列式の定義、固有値・固有ベクトルの定義、ユニタリ行列・エルミート行列の定義、基底、正規直交、内積。

これらを使う証明の中で、**性質**（たとえばトレースの巡回性）が必要になったら、使う前に導出する（例：付録A-5-1）。
