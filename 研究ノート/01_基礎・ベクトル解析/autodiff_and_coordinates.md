# 自動微分は何を微分しているのか ―余接ベクトル・計量・座標―

自動微分（PyTorch の `autograd`、JAX の `grad`、TensorFlow の `GradientTape`）と勾配降下法は、「微分」を機械的に計算します。ところが、微分には、共変微分・外微分・リー微分のように、何を何と比べるかで定義が変わるものがあります。このノートでは、自動微分が返す量が数学的には何なのかを、極座標の具体例とライブラリの実装で確かめます。

- **Part I**：自動微分が計算するもの。微分は線形写像、`grad` は余接ベクトル $dL$ の成分
- **Part II**：$dL$ と勾配ベクトルの違い。極座標で、計量を使うと値が変わる
- **Part III**：2階微分とラプラシアン。座標の2階偏微分の和は、ラプラシアンにならない
- **Part IV**：勾配降下法と再パラメータ化。座標の取り方で軌跡が変わり、計量で補正すると変わらない
- **Part V**：複素数の勾配。ライブラリで共役の向きが違う
- **Part VI**：ライブラリの実装で確かめたことと、確かめていないこと

**関連ファイル**：検算は [experiments/autodiff_geometry/](../../experiments/autodiff_geometry/README.md)（スクリプトと22件のテスト。JAX・PyTorch・TensorFlow の3つで実行）。極座標の計量とクリストッフェル記号は [球座標の計量テンソル計算例](../02_微分幾何/球座標の計量テンソル計算例.md) と[クリストッフェル記号のノート](../02_微分幾何/christoffel_riemann_intro.md)、$df$ と $\mathrm{grad}$ の違いは[計量テンソルと共変反変_まとめ](../02_微分幾何/計量テンソルと共変反変_まとめ.md)の5節、ラプラス・ベルトラミ作用素の補正項は[ヤコビ行列から見るラプラス・ベルトラミ作用素](../02_微分幾何/laplace_beltrami_from_jacobian_matrix.md)にあります。

**記号の約束**

- $q=(q^1,\dots,q^n)$：座標（極座標なら $(r,\theta)$）。$\partial_j:=\partial/\partial q^j$。
- $g_{jk}$：計量、$g^{jk}$：その逆行列。繰り返される添字は和を取ります。
- ライブラリの出力は、$f$ の値を $q$ の関数として微分した成分の配列です。
- 式番号は `Part 番号-通し番号`（例：II-3）です。

<a id="toc"></a>

## 目次

<!-- toc:start -->

- [Part I：自動微分が計算するもの](#p1)
  - [1. 微分は線形写像、自動微分はその連鎖律](#p1-1)
  - [2. 前進モードと後退モード](#p1-2)
  - [3. `grad` が返すもの：dL の成分](#p1-3)
- [Part II：dL と勾配ベクトルの違い ―極座標の例―](#p2)
  - [1. 例](#p2-1)
  - [2. 同じ点で、3つの別の量](#p2-2)
  - [3. この差は誤差ではない](#p2-3)
- [Part III：2階微分とラプラシアン](#p3)
  - [1. ヘッセ行列は、一般の座標ではテンソルではない](#p3-1)
  - [2. 極座標での値](#p3-2)
  - [3. ラプラシアン](#p3-3)
  - [4. 計量だけから、自動微分でラプラシアンを作る](#p3-4)
- [Part IV：勾配降下法と再パラメータ化](#p4)
  - [1. 更新式に計量はない](#p4-1)
  - [2. 例：3乗による再パラメータ化](#p4-2)
  - [3. 計量で補正する（自然勾配）](#p4-3)
- [Part V：複素数の勾配](#p5)
- [Part VI：ライブラリの実装で確かめたこと](#p6)
- [まとめ](#summary)

<!-- toc:end -->

---

<a id="p1"></a>

# Part I：自動微分が計算するもの

<!-- part-toc:start -->

**この Part の内容**

- [1. 微分は線形写像、自動微分はその連鎖律](#p1-1)
- [2. 前進モードと後退モード](#p1-2)
- [3. `grad` が返すもの：dL の成分](#p1-3)

<!-- part-toc:end -->

<a id="p1-1"></a>

## 1. 微分は線形写像、自動微分はその連鎖律

関数 $F:\mathbb R^n\to\mathbb R^m$ の点 $x$ での微分は、線形写像 $DF_x:\mathbb R^n\to\mathbb R^m$ です（[関数・線形写像のノート](functions_linear_maps_derivatives_integrals.md)の Part III）。成分では $(DF_x)_{ij}=\partial F^i/\partial x^j$（ヤコビ行列）です。合成関数の微分は、微分の合成になります。

$$
D(G\circ F)_x=DG_{F(x)}\circ DF_x\tag{I-1}
$$

自動微分は、計算を小さな演算の合成に分け、各演算の微分（たとえば $\sin$ なら $\cos$ を掛ける）を知っておいて、(I-1) を機械的に当てはめます。

<a id="p1-2"></a>

## 2. 前進モードと後退モード

(I-1) を、どちら側から評価するかで2つのモードがあります。

| モード | 入力 | 出力 | 計算 | 向き |
|---|---|---|---|---|
| 前進（JVP） | 接ベクトル $v\in\mathbb R^n$ | $DF_x\,v\in\mathbb R^m$ | 入力から出力へ | 接ベクトルを押し出す |
| 後退（VJP、逆伝播） | 余接ベクトル $u\in(\mathbb R^m)^*$ | $u\,DF_x\in(\mathbb R^n)^*$ | 出力から入力へ | 余接ベクトルを引き戻す |

後退モードでは、出力側の線形関数 $u$（出力の微小な変化に対する重み）を、入力側の線形関数 $u\,DF_x$ に引き戻します。成分では $\sum_i u_i\,\partial F^i/\partial x^j$ で、ヤコビ行列の転置を $u$ に掛けたものです。

損失関数 $L:\mathbb R^n\to\mathbb R$ なら $m=1$ で、$u=1$ と置いた1回の後退計算で、$dL=(\partial_1L,\dots,\partial_nL)$ が全成分そろいます。機械学習でパラメータが何百万個あっても逆伝播が使われるのは、このためです。

<a id="p1-3"></a>

## 3. `grad` が返すもの：$dL$ の成分

したがって、`grad` が返すのは、$dL$ の成分 $\partial_jL$ です。$dL$ は、方向 $v$ を入れると方向微分 $dL(v)=v^j\partial_jL$ を返す線形関数、つまり余接ベクトルです。成分 $\partial_jL$ は、座標の取り方を変えると**共変に**変わります（座標が $q\to q'$ なら、$\partial'_kL=\dfrac{\partial q^j}{\partial q'^k}\partial_jL$）。

ところが、ライブラリは、この成分を「引数と同じ形の配列」として返します（JAX の `grad` の docstring：「引数と同じ形と型」）。配列には、添字が上付きか下付きかの区別がありません。ここで、余接ベクトル $dL$ を、接ベクトルの「勾配ベクトル」と同一視するには、計量が要ります。

$$
(\mathrm{grad}\,L)^j=g^{jk}\,\partial_kL\tag{I-2}
$$

ライブラリは、$g^{jk}=\delta^{jk}$（ユークリッド計量）を暗黙に使ったことになります。次の Part II で、これが値に影響する例を見ます。

---

<a id="p2"></a>

# Part II：$dL$ と勾配ベクトルの違い ―極座標の例―

<!-- part-toc:start -->

**この Part の内容**

- [1. 例](#p2-1)
- [2. 同じ点で、3つの別の量](#p2-2)
- [3. この差は誤差ではない](#p2-3)

<!-- part-toc:end -->

<a id="p2-1"></a>

## 1. 例

$f(r,\theta)=r^2\sin\theta$ を、極座標 $(r,\theta)$ の関数として自動微分します。点は $r=2$、$\theta=0.7$ です。極座標の計量は $g=\mathrm{diag}(1,r^2)$、逆計量は $g^{-1}=\mathrm{diag}(1,1/r^2)$ です。

自動微分の出力（$dL$ の成分）は、手計算の

$$
df=\Big(\frac{\partial f}{\partial r},\ \frac{\partial f}{\partial\theta}\Big)=\big(2r\sin\theta,\ r^2\cos\theta\big)=(2.577,\ 3.059)\tag{II-1}
$$

と一致します（JAX・PyTorch・TensorFlow のすべて）。

<a id="p2-2"></a>

## 2. 同じ点で、3つの別の量

(II-1) を、どう読むかで、値が変わります。

| 量 | 式 | 値（$r=2,\theta=0.7$） | 意味 |
|---|---|---|---|
| $df$ の成分（自動微分の出力） | $(\partial_rf,\ \partial_\theta f)$ | $(2.577,\ 3.059)$ | 余接ベクトル |
| 座標基底での勾配ベクトル | $g^{jk}\partial_kf=(\partial_rf,\ \tfrac1{r^2}\partial_\theta f)$ | $(2.577,\ 0.765)$ | $\mathrm{grad}f=2r\sin\theta\,\partial_r+\cos\theta\,\partial_\theta$ |
| 正規直交基底での成分 | $(\partial_rf,\ \tfrac1r\partial_\theta f)$ | $(2.577,\ 1.530)$ | 長さ1の基底ベクトル $\hat{\mathbf e}_r,\hat{\mathbf e}_\theta$ での成分 |

$\theta$ 成分だけを見ると、$3.059$、$0.765$、$1.530$ と、3通りの値になります。座標基底のベクトル $\partial_\theta$ は長さが $r$ なので、座標基底の成分 $0.765$ に $r=2$ を掛けると、正規直交基底の成分 $1.530$ になります。

**もう1つの確認**：$r=2,\ \theta=0$ では、$df=(0,\ 4)$、座標基底の勾配ベクトル $(0,\ 1)$、正規直交基底の成分 $(0,\ 2)$ です。勾配ベクトルは $1\cdot\partial_\theta$ で、$\partial_\theta$ の長さが $r=2$ なので、実際の長さは $2$ です（この3つの値は、テストで確かめています）。

<a id="p2-3"></a>

## 3. この差は誤差ではない

3つの値の差は、浮動小数点の丸め誤差ではなく、**別の量を同じ配列のように読んだ**ことによる差です。物理的な勾配ベクトル（たとえば速度場や力の向き）が欲しいときは、$g^{jk}$ を掛けるという処理が別に要ります。自動微分は、これを自動では行いません。

---

<a id="p3"></a>

# Part III：2階微分とラプラシアン

<!-- part-toc:start -->

**この Part の内容**

- [1. ヘッセ行列は、一般の座標ではテンソルではない](#p3-1)
- [2. 極座標での値](#p3-2)
- [3. ラプラシアン](#p3-3)
- [4. 計量だけから、自動微分でラプラシアンを作る](#p3-4)

<!-- part-toc:end -->

<a id="p3-1"></a>

## 1. ヘッセ行列は、一般の座標ではテンソルではない

`hessian` が返すのは、座標の2階偏微分の行列 $\partial_i\partial_jf$ です。PyTorch の `torch.autograd.functional.hessian` は、実装の中で `jacobian` を2回取っています。この行列は、座標を変えると、テンソルとしては変わりません。座標が $q\to q'$ のとき、

$$
\partial'_k\partial'_lf=\frac{\partial q^i}{\partial q'^k}\frac{\partial q^j}{\partial q'^l}\,\partial_i\partial_jf+\frac{\partial^2q^i}{\partial q'^k\partial q'^l}\,\partial_if
$$

で、右辺の第2項が余計に出ます。この項を打ち消すのが、**共変ヘッセ**です。

$$
(\nabla df)_{ij}=\partial_i\partial_jf-\Gamma^k{}_{ij}\,\partial_kf\tag{III-1}
$$

$\Gamma^k{}_{ij}$ はクリストッフェル記号です。(III-1) は $(0,2)$ テンソルになります。

<a id="p3-2"></a>

## 2. 極座標での値

極座標では、$\Gamma^r{}_{\theta\theta}=-r$、$\Gamma^\theta{}_{r\theta}=\Gamma^\theta{}_{\theta r}=1/r$、ほかの成分は 0 です（[クリストッフェル記号のノート](../02_微分幾何/christoffel_riemann_intro.md)）。$f=r^2\sin\theta$ の2階偏微分は、

$$
\partial_r^2f=2\sin\theta,\qquad\partial_r\partial_\theta f=2r\cos\theta,\qquad\partial_\theta^2f=-r^2\sin\theta
$$

です。(III-1) に代入すると、

$$
(\nabla df)_{rr}=2\sin\theta,\qquad
(\nabla df)_{r\theta}=2r\cos\theta-\frac1r\cdot r^2\cos\theta=r\cos\theta,\qquad
(\nabla df)_{\theta\theta}=-r^2\sin\theta-(-r)\cdot2r\sin\theta=r^2\sin\theta
$$

です。

<a id="p3-3"></a>

## 3. ラプラシアン

ラプラシアンは、共変ヘッセを逆計量で縮約したものです。

$$
\Delta f=g^{ij}(\nabla df)_{ij}=2\sin\theta+\frac1{r^2}\cdot r^2\sin\theta=3\sin\theta\tag{III-2}
$$

一方、各座標の2階偏微分を足しただけの値は、

$$
\partial_r^2f+\partial_\theta^2f=(2-r^2)\sin\theta=-1.288\qquad(r=2,\ \theta=0.7)
$$

で、(III-2) の $3\sin\theta=1.933$ とは符号まで違います。**自動微分で各座標の2階微分を足すだけでは、曲線座標ではラプラシアンになりません。** 係数 $g^{jk}$ も、補正項も足りないからです。

**独立な確認**：デカルト座標で $f=y\sqrt{x^2+y^2}$ を自動微分すると、$\partial_x^2f+\partial_y^2f=3y/r=3\sin\theta$ で、(III-2) と一致します。

$(\nabla df)$ の補正項は、[ラプラス・ベルトラミのノート](../02_微分幾何/laplace_beltrami_from_jacobian_matrix.md)で出てきた $C_k=-g^{ij}\Gamma^k{}_{ij}$ と同じものです。同ノートの (II-1) の通り、$\Delta f=g^{jk}\partial_j\partial_kf+C_k\partial_kf$ です。

<a id="p3-4"></a>

## 4. 計量だけから、自動微分でラプラシアンを作る

逆に、計量 $g_{jk}(q)$ を自動微分の関数として与えれば、ラプラス・ベルトラミ作用素

$$
\Delta f=\frac1{\sqrt g}\,\partial_j\big(\sqrt g\,g^{jk}\partial_kf\big)\tag{III-3}
$$

を自動微分で組めます。$V^j=\sqrt g\,g^{jk}\partial_kf$ を作り、そのヤコビ行列のトレース $\partial_jV^j$ を $\sqrt g$ で割る、という手順です。極座標の3点で $3\sin\theta$ に一致し、単位球面（計量 $\mathrm{diag}(1,\sin^2\theta)$）では $f=\cos\theta$ に対して $\Delta f=-2\cos\theta$ になります（$l=1$ の球面調和関数）。同じく、クリストッフェル記号も、計量の自動微分から作れます。

自動微分は、**計量という幾何学的な情報を人間が与えれば**、共変微分やラプラス・ベルトラミ作用素を計算する部品として使えます。どの計量・どの接続を使うかは、自動では決まりません。

---

<a id="p4"></a>

# Part IV：勾配降下法と再パラメータ化

<!-- part-toc:start -->

**この Part の内容**

- [1. 更新式に計量はない](#p4-1)
- [2. 例：3乗による再パラメータ化](#p4-2)
- [3. 計量で補正する（自然勾配）](#p4-3)

<!-- part-toc:end -->

<a id="p4-1"></a>

## 1. 更新式に計量はない

勾配降下法は、$\theta\leftarrow\theta-\eta\,\partial L/\partial\theta$ です。PyTorch の `torch/optim/sgd.py` は `param.add_(grad, alpha=-lr)`、Keras の `sgd.py` は `assign_sub(variable, gradient*learning_rate)` で、どちらも成分ごとの引き算だけです。(I-2) の $g^{jk}$ を掛ける処理はなく、パラメータ空間にユークリッド計量が暗黙に入っています。

<a id="p4-2"></a>

## 2. 例：3乗による再パラメータ化

損失 $L(w)=\tfrac12(w-3)^2$ を、パラメータ $w$ で書くか、$w=\varphi^3$ となる $\varphi$ で書くかを比べます。どちらも同じ損失で、同じ関数を別の座標で書いただけです。$w$ 座標の勾配降下法を、学習率 $\eta\to0$ の極限（勾配流）で書くと、

$$
\dot w=-\frac{dL}{dw}=-(w-3)\qquad\Longrightarrow\qquad w(t)=3-(3-w_0)\,e^{-t}\tag{IV-1}
$$

です。$\varphi$ 座標の勾配流は $\dot\varphi=-dL/d\varphi$ で、連鎖律 $dL/d\varphi=3\varphi^2\,dL/dw$ より、

$$
\dot w=3\varphi^2\dot\varphi=-9\varphi^4\,(w-3)\tag{IV-2}
$$

です。(IV-1) の速さが $1$ なのに対し、(IV-2) の速さは $9\varphi^4$ で、場所によって違います。たとえば $w=0.5$（$\varphi=0.794$）では約 $3.6$、$w=2$（$\varphi=1.26$）では約 $23$ です。同じ損失でも、座標の取り方で別の動きになります。

**数値**：$w_0=0.5$、学習率 $10^{-3}$、1000 ステップ（時刻 $T=1$）の $w$ の値は、次の通りです（JAX・PyTorch・TensorFlow で同じ）。

| 方法 | $T=1$ の $w$ |
|---|---|
| $w$ 座標の勾配降下法 | $2.0808$（厳密解 (IV-1) は $2.0803$） |
| $\varphi$ 座標の勾配降下法 | $3.0000$（ほぼ収束してしまう） |
| $\varphi$ 座標の自然勾配（下） | $2.0812$ |

<a id="p4-3"></a>

## 3. 計量で補正する（自然勾配）

勾配ベクトル (I-2) の考え方で、$dL$ に逆計量を掛けます。$\varphi$ 座標の計量として、$w$ 座標のユークリッド計量を引き戻したもの $g_{\varphi\varphi}=(dw/d\varphi)^2=9\varphi^4$ を使うと、

$$
\dot\varphi=-g^{\varphi\varphi}\frac{dL}{d\varphi}=-\frac{3\varphi^2\,(w-3)}{9\varphi^4}=-\frac{w-3}{3\varphi^2},
\qquad
\dot w=3\varphi^2\dot\varphi=-(w-3)\tag{IV-3}
$$

となり、(IV-1) と同じになります。計量が座標変換でテンソルとして変わるので、補正した勾配の流れは、座標の取り方によりません。表の $2.0812$ が (IV-1) の $2.0803$ にほぼ一致し、誤差は学習率にほぼ比例して小さくなります（学習率 $10^{-4}$ では $1/5$ 以下）。

**注意**：ここで使った計量は、私が $w$ 座標のユークリッド計量から選んだものです。機械学習で使われる自然勾配法は、確率モデルのフィッシャー情報行列を計量に使います。計量の選び方（どの空間で最急降下を考えるか）が、この方法の本質です。実用では、フィッシャー行列を近似することが多く、近似すると不変性が一部失われます。

---

<a id="p5"></a>

# Part V：複素数の勾配

実数値の関数 $f(z)$（$z=x+iy$）を、実部と虚部で見ると $f(x,y)$ です。

$$
df=f_x\,dx+f_y\,dy=\frac{\partial f}{\partial z}\,dz+\frac{\partial f}{\partial\bar z}\,d\bar z,\qquad
\frac{\partial}{\partial z}=\frac12(\partial_x-i\partial_y),\quad\frac{\partial}{\partial\bar z}=\frac12(\partial_x+i\partial_y)\tag{V-1}
$$

$\partial/\partial z$、$\partial/\partial\bar z$ は、ウィルティンガー微分です。$f=\lvert z\rvert^2=x^2+y^2$ なら $\partial f/\partial z=\bar z$、$\partial f/\partial\bar z=z$ です。

$z=1+2i$ での `grad` の出力は、次の通りです。

| ライブラリ | 出力 | 読み方 |
|---|---|---|
| PyTorch | $2+4i=2z$ | $f_x+if_y=2\,\partial f/\partial\bar z$（最急上昇の向き） |
| TensorFlow | $2+4i=2z$ | 同上 |
| JAX | $2-4i=2\bar z$ | $f_x-if_y=2\,\partial f/\partial z$（その共役） |

複素パラメータに勾配降下法を使うときは、この規約を知っておく必要があります。PyTorch と TensorFlow は、返された値を引けば（$z\leftarrow z-\eta\cdot\text{grad}$）、$(x,y)$ の最急降下になります。JAX は、共役を取ってから引く必要があります。ここで確かめたのは、実数値の $f$ の場合だけです。TensorFlow の `math_grad.py` には、「複素数の入力では、勾配は共役の向き」というコメントがあり、各演算の勾配で共役を使っています。

---

<a id="p6"></a>

# Part VI：ライブラリの実装で確かめたこと

| | PyTorch | TensorFlow（Keras） | JAX |
|---|---|---|---|
| 勾配降下法の更新式 | `sgd.py` の 378・380 行目 `param.add_(grad, alpha=-lr)` | `sgd.py` の 123 行目 `assign_sub(variable, gradient*learning_rate)` | 本体にはない（optax は別） |
| 勾配の型 | 引数と同じ形 | 引数と同じ形 | 引数と同じ形と型（`api.py` の docstring） |
| 計量を掛ける処理 | なし | なし | なし |
| ヘッセ行列 | `functional.py`：`jacobian` を2回 | `GradientTape` を入れ子にして `jacobian` | `jax.hessian` |
| 複素数の規約 | $2\,\partial f/\partial\bar z$ | 同左 | $2\,\partial f/\partial z$ |

**確かめていないもの**：PyTorch の C++ 側の微分公式、TensorFlow の C++ カーネル、JAX の `ad.py` の内部、`jax.hessian` の実装は、読んでいません。値の確認は、スクリプトの実行結果によります。

---

<a id="summary"></a>

# まとめ

| | 自動微分が計算するもの | 人間が与える必要があるもの |
|---|---|---|
| 1階微分 | $dL$ の成分（余接ベクトル）を、引数と同じ形の配列で | 勾配ベクトルが欲しいなら、計量 $g^{jk}$ |
| 2階微分 | 座標の2階偏微分 $\partial_i\partial_jf$ | 共変ヘッセには、接続（クリストッフェル記号） |
| ラプラシアン | 各座標の和は、曲線座標では不正解 | 計量だけから (III-3) を組む |
| 勾配降下法 | 成分ごとの引き算（暗黙のユークリッド計量） | 座標によらない降下には、計量（自然勾配） |
| 複素数 | ライブラリごとに共役の向きが違う | 規約の確認 |

自動微分は、**線形写像としての微分と連鎖律**を、巨大な関数に対しても機械的に計算します。しかし、計量、接続、どの空間で降下するか、といった幾何学的な構造は、自動微分の外にあります。これらが効くのは、曲線座標、PINN、曲面上の偏微分方程式、再パラメータ化に対する不変性が要る場面です。
