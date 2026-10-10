# 微分の地図の検算

> **作成** 2026-10-10　**更新** 2026-10-10
> 研究ノート「微分の地図」（derivative_map.md）の、反例と数値の主張を確かめるスクリプトとテスト（12件）。

ノート [derivative_map.md](../../研究ノート/01_基礎・ベクトル解析/derivative_map.md) に書いた、ガトー微分とフレシェ微分の反例、汎関数微分と離散化、弱微分、ヤコビアン、リー括弧、確率微分、分数階微分、ウィルティンガー微分、差分と自動微分、パラメータシフト則を、数値と記号計算で確かめます。

```bash
uv run python experiments/derivative_map/derivative_map.py   # 値を表示する
uv run pytest experiments/derivative_map -q                  # 検算（12 件）
```

| ノートの節 | 確かめたこと | テスト |
|---|---|---|
| Part II §3 | $f=x^3/(x^2+y^2)$：原点で全方向の方向微分があるが、方向について加法的でない（$1+0\ne\tfrac12$）。斉次性は成り立つ | `test_directional_derivative_exists_but_is_not_additive` |
| Part II §4 | $f=xy/(x^2+y^2)$：偏微分は 0 だが、方向 $(1,1)$ の差商は $1/(2t)$ で発散 | `test_partial_derivatives_exist_but_other_directions_do_not` |
| Part II §5 | $f=x^3y/(x^6+y^2)$：全方向の方向微分が 0（線形）だが、曲線 $y=x^3$ に沿って $f=\tfrac12$ | `test_linear_gateaux_derivative_but_not_differentiable` |
| Part III §1 | 離散化した $J[u]=\int\tfrac12u'^2$ を自動微分した成分は、$-u''$ の $\Delta x$ 倍（400 点で、$\Delta x$ で割ると最大誤差 $5\times10^{-5}$、点を2倍にすると誤差は $1/3$ 以下） | `test_autodiff_of_discretized_functional_is_dx_times_functional_derivative` |
| Part III §2 | $\lvert x\rvert$ の弱微分は $\mathrm{sign}$、$\mathrm{sign}$ の超関数微分は $2\delta$（試験関数との積分） | `test_weak_derivative_pairings` |
| Part III §2 | 極座標のガウス積分 $=\pi$（ヤコビアン $r$）。放物面の面積要素 $\sqrt{\det(J^TJ)}=\sqrt{1+4u^2+4v^2}$ | `test_jacobian_is_density_of_pulled_back_measure` |
| Part III §4 | $[fX,Y]=f[X,Y]-Y(f)X$（SymPy、一般の関数） | `test_lie_derivative_is_not_function_linear_in_X` |
| Part III §5 | ウィルティンガー微分：$\bar z$、$z^2$、$\lvert z\rvert^2$ | `test_wirtinger_derivatives` |
| Part III §6 | $\int W\,dW$：中点の和は $W_T^2/2$ に、左端点の和は $(W_T^2-\sum(\Delta W)^2)/2$ にちょうど一致。差の平均 $\approx T/2$ | `test_ito_vs_stratonovich` |
| Part III §8 | 分数階微分（$\alpha=\tfrac12$）：リーマン・リウヴィルは定数で $1/\sqrt{\pi x}$、カプートは 0 | `test_fractional_derivatives_differ_in_initial_values` |
| Part IV §1 | 前進差分 $O(h)$（$f''/2$）、中心差分 $O(h^2)$（$f'''/6$）、丸め誤差で頭打ち。自動微分は丸め誤差程度 | `test_finite_difference_orders_and_autodiff` |
| Part IV §4 | パラメータシフト則が厳密（$\langle Z\rangle=\cos\theta$ の微分） | `test_parameter_shift_rule_is_exact` |

関連：[experiments/autodiff_geometry/](../autodiff_geometry/README.md)（自動微分と計量の検算）。
