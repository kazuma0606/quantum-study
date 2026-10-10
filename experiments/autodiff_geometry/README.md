# 自動微分が返すものを、座標を変えて確かめる

> **作成** 2026-10-10　**更新** 2026-10-10
> JAX・PyTorch・TensorFlow の自動微分と勾配降下法が、計量・座標・複素数についてどう振る舞うかを、極座標と再パラメータ化の例で確かめる実験。

「自動微分は連鎖律を機械的に適用するだけで、微分の幾何学的な構造（どこに住む量を何と比べるか）までは扱わない」という主張を、ライブラリのソースの読み取りと数値実験で確かめます。理論の側は研究ノート（微分の整理のノート）に書き、ここは検算の置き場です。

```bash
uv sync --group tf                                                # TensorFlow を入れる（初回だけ）
uv run python experiments/autodiff_geometry/autodiff_geometry.py  # 値を表示する
uv run pytest experiments/autodiff_geometry -q                    # 検算（22 件）
```

| ファイル | 内容 |
|---|---|
| `autodiff_geometry.py` | 実験の本体。JAX・PyTorch・TensorFlow で同じ量を計算する関数（`LIBS = jax, torch, tf`） |
| `tests/test_autodiff_geometry.py` | 下の表の各行に対応する検算（手計算の値、3つのライブラリの一致、反例） |

## 確かめたこと

例の関数は $f(r,\theta)=r^2\sin\theta$、点は $r=2,\ \theta=0.7$ です（(c) だけ別）。

| | 主張 | 結果 | テスト |
|---|---|---|---|
| (a) | `grad` が返すのは $df$（余接ベクトル）の成分 $(2r\sin\theta,\ r^2\cos\theta)=(2.577,\ 3.059)$。計量を使った勾配ベクトル（座標基底 $(2.577,\ 0.765)$、正規直交基底 $(2.577,\ 1.530)$）とは別の量 | 3つのライブラリで一致 | `test_grad_is_dL_components` ほか |
| (b) | ヘッセ行列は座標の2階偏微分で、その和（$-1.288$）は真のラプラシアン $3\sin\theta=1.933$ にならない。$\Gamma$ で補正した共変ヘッセ $\partial_i\partial_jf-\Gamma^k{}_{ij}\partial_kf$ のトレースは一致する | 3つのライブラリのヘッセ行列が一致。$\Gamma$ は計量の自動微分から作った（$\Gamma^r{}_{\theta\theta}=-r$、$\Gamma^\theta{}_{r\theta}=1/r$） | `test_naive_sum_of_second_derivatives_is_not_the_laplacian` ほか |
| (b') | 計量 $g$ だけからラプラス・ベルトラミ作用素 $\frac1{\sqrt g}\partial_j(\sqrt g\,g^{jk}\partial_kf)$ を自動微分で組める | 極座標の3点で $3\sin\theta$ に一致。単位球面上の $\cos\theta$ で $\Delta=-2\cos\theta$ | `test_laplace_beltrami_built_from_metric_only` ほか |
| (c) | $L(w)=\frac12(w-3)^2$ を $w=\varphi^3$ と再パラメータ化すると、同じ学習率・同じステップ数の勾配降下法が別の軌跡になる。計量 $g_{\varphi\varphi}=9\varphi^4$ で補正すると $w$ 座標の結果に一致する | $T=1$ の $w$：$w$ 座標 $2.0808$、$\varphi$ 座標 $3.0000$、$\varphi$ 座標の自然勾配 $2.0812$（厳密解 $2.0803$）。誤差は学習率にほぼ比例して減る | `test_gradient_descent_depends_on_parametrization` ほか |
| (d) | 複素数の勾配の規約は、ライブラリで共役の向きが違う | $f=\lvert z\rvert^2$、$z=1+2i$ で、PyTorch と TensorFlow は $2z=2+4i$、JAX は $2\bar z=2-4i$ | `test_complex_gradient_conventions` |

(c) の計量 $9\varphi^4$ は、$w$ 座標のユークリッド計量を $\varphi$ 座標に引き戻したもので、フィッシャー計量ではありません。要点は、計量がテンソルとして変換すれば、補正した勾配は座標の取り方によらないことです。

## ライブラリのソースで確かめたこと

| | PyTorch | TensorFlow（Keras） | JAX |
|---|---|---|---|
| 勾配降下法の更新式 | `torch/optim/sgd.py` の 378・380 行目 `param.add_(grad, alpha=-lr)` | `keras/src/optimizers/sgd.py` の 123 行目 `assign_sub(variable, gradient*learning_rate)`（docstring は $w=w-\text{lr}\cdot g$） | 本体には最適化器がない（optax は別。この環境には入っていない） |
| 勾配の型 | 引数と同じ形のテンソル（`p.grad`） | 引数と同じ形（`tape.gradient`） | `jax.grad` の docstring（`api.py` 450〜456 行目）：「引数と同じ形と型」 |
| 計量を掛ける処理 | どの更新式にもない | どの更新式にもない | なし |
| ヘッセ行列 | `torch/autograd/functional.py` の 982〜986 行目：`jacobian` を2回取る | `GradientTape` を入れ子にして `jacobian`（このスクリプトの実装） | `jax.hessian`（実装は未読） |
| 複素数 | 数値で確認（上の (d)） | `tensorflow/python/ops/math_grad.py` の 324 行目のコメント「複素数の入力では、勾配は共役の向き」、各演算の勾配で `conj` を使う | 数値で確認（上の (d)） |

つまり、どのライブラリでも、勾配は「$df$ の成分を、引数と同じ形の配列として返したもの」で、更新式は成分ごとの引き算です。暗黙のうちに、パラメータ空間にユークリッド計量が入っています。

**読んでいないもの**：PyTorch の C++ 側の微分公式（`derivatives.yaml` は wheel に入っていない）、TensorFlow の C++ カーネル、JAX の `ad.py` の内部（定義の所在は確認）、`jax.hessian` の実装。

## 関連

- 理論の側：[ヤコビ行列から見るラプラス・ベルトラミ作用素](../../研究ノート/02_微分幾何/laplace_beltrami_from_jacobian_matrix.md)（(b) の補正項 $C_k=-g^{ij}\Gamma^k{}_{ij}$）、[クリストッフェル記号のノート](../../研究ノート/02_微分幾何/christoffel_riemann_intro.md)
- 微分の本の構想：[book_plan_differentiation.md](../../docs/book_plan_differentiation.md)（コラム「ディープラーニングの数理」）
