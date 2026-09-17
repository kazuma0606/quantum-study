# クリストッフェル記号とリーマン曲率テンソル ―高階テンソル入門―

これまでの議論（計量テンソル $g_{ij}$、共変・反変、ラプラス・ベルトラミ作用素）の続きとして、「計量から先」の世界であるクリストッフェル記号とリーマン曲率テンソルを、**一般相対論までは踏み込まず**、具体的に計算できる2つの例（平坦な極座標／曲がった球面）で確かめながら整理します。

添字の約束は今までと同じです：$g_{ij}$（共変計量）、$g^{ij}$（反変計量、逆行列）、$i,j,k,l,m$ は座標 $q^i$ の添字。

---

# Part I：なぜクリストッフェル記号が必要になるのか

## 1. 「ベクトルを微分する」ことの落とし穴

デカルト座標では、ベクトル場 $V=V^a\mathbf e_a$ を微分するのは簡単です。基底 $\mathbf e_a$ が場所によらず一定なので、

$$
\frac{\partial V}{\partial x^b} = \frac{\partial V^a}{\partial x^b}\mathbf e_a
$$

つまり「成分を微分するだけ」で済みます。

ところが曲線座標 $q^i$ では、基底ベクトル

$$
\mathbf e_i(q) = \frac{\partial\mathbf x}{\partial q^i}
$$

自体が**場所によって向きも長さも変わります**（前回の極座標の例で $\mathbf e_\theta=(-r\sin\theta,\,r\cos\theta)$ が $r,\theta$ によって変わっていたことを思い出してください）。したがって、ベクトル場 $V=V^i\mathbf e_i$ を微分すると、積の微分から**基底ベクトル自身の微分**という新しい項が出てきます：

$$
\frac{\partial V}{\partial q^j} = \frac{\partial V^i}{\partial q^j}\mathbf e_i + V^i\frac{\partial\mathbf e_i}{\partial q^j}
$$

この「基底ベクトルがどう変化するか」を定量化する量が**クリストッフェル記号**です。

## 2. クリストッフェル記号の定義

基底ベクトルの微分 $\dfrac{\partial\mathbf e_i}{\partial q^j}$ は、それ自体1つのベクトルなので、基底 $\{\mathbf e_k\}$ で展開できます：

$$
\boxed{\frac{\partial\mathbf e_i}{\partial q^j} =: \Gamma^k{}_{ij}\,\mathbf e_k}
$$

この展開係数 $\Gamma^k{}_{ij}$ がクリストッフェル記号（接続係数）です。「$i$方向の基底ベクトルを、$j$方向に動きながら見たとき、$k$方向の成分がどれだけ出てくるか」を表す量、というのが直感的な意味です。

$\mathbf e_i=\partial\mathbf x/\partial q^i$ なので、

$$
\frac{\partial\mathbf e_i}{\partial q^j} = \frac{\partial^2\mathbf x}{\partial q^j\partial q^i} = \frac{\partial\mathbf e_j}{\partial q^i}
$$

（偏微分の交換、以前のラプラシアン導出でも使った混合偏微分の対称性そのものです）。したがって：

$$
\boxed{\Gamma^k{}_{ij} = \Gamma^k{}_{ji}}\qquad\text{（下2つの添字について対称）}
$$

---

# Part II：計量からクリストッフェル記号の公式を導く

## 3. 計量の微分とクリストッフェル記号

$g_{ij}=\mathbf e_i\cdot\mathbf e_j$ を $q^k$ で微分します。積の微分：

$$
\partial_kg_{ij} = \left(\frac{\partial\mathbf e_i}{\partial q^k}\right)\cdot\mathbf e_j + \mathbf e_i\cdot\left(\frac{\partial\mathbf e_j}{\partial q^k}\right)
$$

クリストッフェル記号の定義を代入すると：

$$
\boxed{\partial_kg_{ij} = \Gamma^l{}_{ki}g_{lj} + \Gamma^l{}_{kj}g_{il}}\tag{3-1}
$$

この式は $i,j,k$ を入れ替えれば、さらに2つの式が作れます：

$$
\partial_ig_{jk} = \Gamma^l{}_{ij}g_{lk} + \Gamma^l{}_{ik}g_{jl}\tag{3-2}
$$
$$
\partial_jg_{ki} = \Gamma^l{}_{jk}g_{li} + \Gamma^l{}_{ji}g_{kl}\tag{3-3}
$$

## 4. 3つの式を組み合わせて $\Gamma$ だけを取り出す

$(3\text{-}2)+(3\text{-}3)-(3\text{-}1)$ を計算します。右辺の項を対称性 $\Gamma^l{}_{ij}=\Gamma^l{}_{ji}$、$g_{ij}=g_{ji}$ を使って整理すると：

- $\Gamma^l{}_{ij}g_{lk}$（(3-2)より）と $\Gamma^l{}_{ji}g_{kl}$（(3-3)より）は同じものなので、足すと $2\Gamma^l{}_{ij}g_{lk}$
- $\Gamma^l{}_{ik}g_{jl}$（(3-2)より）と $-\Gamma^l{}_{ki}g_{lj}$（$-(3\text{-}1)$より）は符号違いで同じものなので、**打ち消し合ってゼロ**
- $\Gamma^l{}_{jk}g_{li}$（(3-3)より）と $-\Gamma^l{}_{kj}g_{il}$（$-(3\text{-}1)$より）も同様に**打ち消し合ってゼロ**

したがって：

$$
\partial_ig_{jk} + \partial_jg_{ki} - \partial_kg_{ij} = 2\Gamma^l{}_{ij}g_{lk}
$$

両辺に逆計量 $g^{km}$ を掛けて $k$ について和を取ると（$g^{km}g_{lk}=\delta^m_l$）：

$$
\boxed{\Gamma^k{}_{ij} = \frac12g^{kl}\left(\partial_ig_{jl} + \partial_jg_{il} - \partial_lg_{ij}\right)}
$$

これがクリストッフェル記号の標準公式です。**計量さえ分かっていれば、あとは微分するだけで完全に決まる**という点が重要です（新しい幾何学的データを追加で与える必要はありません）。

---

# Part III：別の定義（ヤコビアンの2階微分から）― 以前の議論との接続

実はクリストッフェル記号には、計量を経由しない、もっと直接的な定義もあります。これは以前ヤコビアン $J,A$ を使って計算していた内容と直結します。

$\mathbf e_i=\partial\mathbf x/\partial q^i$（デカルト座標成分で書けば $J^a{}_i=\partial x^a/\partial q^i$）なので：

$$
\frac{\partial\mathbf e_i}{\partial q^j} = \frac{\partial^2\mathbf x}{\partial q^j\partial q^i}\qquad(\text{成分で書けば }\ \partial_jJ^a{}_i)
$$

これを基底 $\mathbf e_k$ で展開するとき、$\mathbf e_k$ の「係数を取り出す」操作は、$A^k{}_a=\partial q^k/\partial x^a$（前回のノートの $A$、ヤコビアンの逆行列）を掛けることに対応します：

$$
\boxed{\Gamma^k{}_{ij} = A^k{}_a\,\partial_jJ^a{}_i = A^k{}_a\,\frac{\partial^2x^a}{\partial q^j\partial q^i}}
$$

これは前回の「ラプラシアンの一般化」のノートで扱った $\partial_jA_{ik}=-A_{il}(\partial_jJ_{lm})A_{mk}$ という式に出てきた $\partial_jJ$ の項と、**まったく同じ量**です。つまり、あのとき第2項の整理に使った $A(\partial J)$ という組み合わせは、実はクリストッフェル記号そのものだったことになります。以前扱った「体積要素の発散」の話は、クリストッフェル記号を使うと

$$
\frac1{\sqrt{|g|}}\partial_i\left(\sqrt{|g|}V^i\right) = \partial_iV^i + \Gamma^i{}_{ij}V^j
$$

という、より一般的な形（**共変発散**）の特別な場合だったことも分かります（$\Gamma^i{}_{ij}=\partial_j\ln\sqrt{|g|}$ という関係が成り立ちます。これは前回導出した「$\operatorname{div}$ の一般公式」の中身そのものです）。

---

# Part IV：共変微分

## 5. ベクトル成分の「正しい微分」

Part Iの計算に戻ります。$V=V^i\mathbf e_i$ を微分すると：

$$
\frac{\partial V}{\partial q^j} = \frac{\partial V^k}{\partial q^j}\mathbf e_k + V^i\Gamma^k{}_{ij}\mathbf e_k = \left(\frac{\partial V^k}{\partial q^j}+\Gamma^k{}_{ij}V^i\right)\mathbf e_k
$$

括弧の中身が、微分してもきちんと「反変ベクトルとして変換する」量になります。これを**共変微分**と呼びます：

$$
\boxed{\nabla_jV^k := \partial_jV^k + \Gamma^k{}_{ij}V^i}
$$

**なぜ普通の偏微分 $\partial_jV^k$ ではダメなのか**：$\partial_jV^k$ は基底ベクトルが変化する効果を無視しているので、座標変換に対して正しく振る舞いません（テンソルになりません）。$\Gamma^k{}_{ij}V^i$ の項が、その「基底が変化する分」をちょうど補正しています。

共変ベクトル（下付き）の共変微分は符号が反転します：

$$
\boxed{\nabla_jV_k := \partial_jV_k - \Gamma^i{}_{kj}V_i}
$$

（この符号の違いは、$V^iV_i$ のようなスカラー量を微分したとき、$\Gamma$ の項がきれいに打ち消し合ってスカラーとして正しく振る舞うように、という要請から決まります。）

---

# Part V：測地線方程式（応用として）

## 6. 「まっすぐな線」を任意の座標で書く

デカルト座標では、まっすぐな線（等速直線運動の軌跡）は $\dfrac{d^2x^a}{dt^2}=0$ と書けます。これを曲線座標 $q^i(t)$ に変換します。$x^a=x^a(q(t))$ なので：

$$
\frac{dx^a}{dt} = J^a{}_i\dot q^i,\qquad
\frac{d^2x^a}{dt^2} = J^a{}_i\ddot q^i + \left(\partial_jJ^a{}_i\right)\dot q^i\dot q^j
$$

（$\dot q^i:=dq^i/dt$）。$\dfrac{d^2x^a}{dt^2}=0$ に $A^k{}_a$（$AJ=I$）を掛けて $a$ について和を取ると：

$$
\ddot q^k + A^k{}_a\left(\partial_jJ^a{}_i\right)\dot q^i\dot q^j = 0
$$

Part IIIの関係 $\Gamma^k{}_{ij}=A^k{}_a\partial_jJ^a{}_i$ を使うと：

$$
\boxed{\ddot q^k + \Gamma^k{}_{ij}\dot q^i\dot q^j = 0}\qquad\text{（測地線方程式）}
$$

これは「デカルト座標で見れば直進する軌道が、曲線座標 $q^i$ ではどう見えるか」を表す方程式です。平坦な空間でも、曲線座標（極座標など）で見ると $\Gamma\ne0$ なので軌道の式は複雑になりますが、それでも「まっすぐ」という性質自体は変わりません。曲がった空間（次のPartで扱う球面など）では、この方程式が定義する曲線（測地線）こそが「その空間内でのまっすぐな道」になります。

---

# Part VI：具体例1 ― 極座標（平坦な空間）でクリストッフェル記号を計算する

2次元極座標 $q^1=r,\ q^2=\theta$、$x=r\cos\theta,\ y=r\sin\theta$。基底ベクトルは前回と同様：

$$
\mathbf e_r=(\cos\theta,\sin\theta),\qquad \mathbf e_\theta=(-r\sin\theta,\ r\cos\theta)
$$

## 7. 基底ベクトルの微分から直接計算する

$$
\frac{\partial\mathbf e_r}{\partial r} = (0,0) = \mathbf 0 \quad\Longrightarrow\quad \Gamma^r{}_{rr}=\Gamma^\theta{}_{rr}=0
$$

$$
\frac{\partial\mathbf e_r}{\partial\theta} = (-\sin\theta,\cos\theta) = \frac1r\mathbf e_\theta \quad\Longrightarrow\quad \Gamma^\theta{}_{r\theta}=\frac1r,\quad \Gamma^r{}_{r\theta}=0
$$

$$
\frac{\partial\mathbf e_\theta}{\partial\theta} = (-r\cos\theta,-r\sin\theta) = -r\,\mathbf e_r \quad\Longrightarrow\quad \Gamma^r{}_{\theta\theta}=-r,\quad \Gamma^\theta{}_{\theta\theta}=0
$$

（$\partial\mathbf e_\theta/\partial r=\frac1r\mathbf e_\theta$ も計算すると $\Gamma^\theta{}_{\theta r}=\frac1r$ となり、$\Gamma^\theta{}_{r\theta}=\Gamma^\theta{}_{\theta r}$ の対称性と一致します。）

## 8. 計量からの公式で検算する

$g_{rr}=1,\ g_{\theta\theta}=r^2,\ g_{r\theta}=0$（前回のノートの結果）、$g^{rr}=1,\ g^{\theta\theta}=1/r^2$ を使います：

$$
\Gamma^r{}_{\theta\theta} = \frac12g^{rr}\big(2\partial_\theta g_{\theta r}-\partial_rg_{\theta\theta}\big) = \frac12(1)(0-2r) = -r\ \checkmark
$$

$$
\Gamma^\theta{}_{r\theta} = \frac12g^{\theta\theta}\big(\partial_rg_{\theta\theta}+\partial_\theta g_{r\theta}-\partial_\theta g_{r\theta}\big) = \frac12\cdot\frac1{r^2}\cdot2r = \frac1r\ \checkmark
$$

一致しました。

## 9. 重要な観察：$\Gamma\ne0$ でも空間は平坦

この極座標の例では $\Gamma^r{}_{\theta\theta}=-r,\ \Gamma^\theta{}_{r\theta}=1/r$ とゼロでない値を持ちますが、これは**空間が曲がっているからではなく、単に座標が曲線的（基底ベクトルが場所ごとに向きを変える）だから**です。$xy$ 平面自体は真っ平らです。

つまり：

$$
\boxed{\Gamma^k{}_{ij}\ne0 \centernot\Longrightarrow \text{空間が曲がっている}}
$$

「空間が本当に曲がっているかどうか」を判定する量は、次に導入するリーマン曲率テンソルです。実際、$\Gamma$ という量は、以下で見るように**テンソルですらありません**（座標変換の仕方によって、値がゼロにもゼロでなくもなる）。

---

# Part VII：リーマン曲率テンソル

## 10. クリストッフェル記号はなぜテンソルでないのか

もしデカルト座標のように $\Gamma=0$ にできる座標が存在するなら（実際、平坦な空間では常に存在します）、テンソルの変換則（線形・同次）に従う量なら、1つの座標系でゼロならどの座標系でもゼロのはずです。しかし極座標では $\Gamma\ne0$ でした。これは、$\Gamma$ の座標変換則が**線形でない**（2階微分を含む余分な項が付く）ことを意味します。この「余分な項」こそが、Part IIIで見た $A^k{}_a\partial_jJ^a{}_i$ という構成の中に、Aとその微分の掛け算という非線形な要素として埋め込まれています。

## 11. 共変微分の非可換性として曲率を定義する

デカルト座標では、微分の順序は交換できます：$\partial_i\partial_j=\partial_j\partial_i$。しかし、共変微分については一般に

$$
\nabla_i\nabla_jV^k \ne \nabla_j\nabla_iV^k
$$

となり得ます。この**差**こそが曲率の本体です：

$$
\boxed{\big(\nabla_i\nabla_j-\nabla_j\nabla_i\big)V^l =: R^l{}_{kij}V^k}
$$

（この左辺は、$V^k$ の言葉で書けばテンソルの差なので、右辺の $R^l{}_{kij}$ は正真正銘のテンソルになります。$\Gamma$ の非線形性がここで打ち消し合い、テンソルとしての変換性が回復するのが、この定義の巧妙なところです。）

具体的に計算すると（$\nabla_jV^k=\partial_jV^k+\Gamma^k{}_{mj}V^m$ を2回適用し、差を取る）：

$$
\boxed{R^l{}_{kij} = \partial_i\Gamma^l{}_{jk} - \partial_j\Gamma^l{}_{ik} + \Gamma^l{}_{im}\Gamma^m{}_{jk} - \Gamma^l{}_{jm}\Gamma^m{}_{ik}}
$$

これが**リーマン曲率テンソル**です。4本の添字を持つ4階テンソルであり、「クリストッフェル記号をもう一段微分し、かつ2次の項も加えたもの」という構造をしています。

## 12. 幾何学的な意味（並行移動）

もう一つの、より直感的な理解の仕方があります。ベクトルを、ある点から出発して小さな長方形の経路（$i$方向に少し動いて $j$方向に少し動く、と、$j$方向→$i$方向の順で動く、の2通り）に沿って「向きを変えずに」運ぶ（平行移動する）と、平坦な空間なら2通りの経路で同じ場所・同じ向きに戻ってきます。しかし曲がった空間では、**経路によって最終的なベクトルの向きがずれます**。このズレの量が、まさに $R^l{}_{kij}V^k$ です。球面上でベクトルを運ぶと向きがずれる、という現象（球面三角形の内角の和が180度を超えることとも関係します）が、この曲率テンソルの正体です。

---

# Part VIII：具体例2 ― 球面（曲がった空間）でリーマン曲率テンソルを計算する

## 13. 設定

半径 $a$（一定）の球面**そのもの**を、2次元の空間として考えます（3次元空間に埋め込まれた球の「表面」だけを、独立した2次元の曲がった世界として扱う、という点が重要です）。座標は $q^1=\theta,\ q^2=\phi$。

計量（前回導出した3次元球座標の計量で $r=a$ を固定したもの）：

$$
g_{\theta\theta}=a^2,\qquad g_{\phi\phi}=a^2\sin^2\theta,\qquad g_{\theta\phi}=0
$$

## 14. クリストッフェル記号

$g_{\theta\theta}=a^2$ は定数（微分すればゼロ）、$g_{\phi\phi}=a^2\sin^2\theta$ の $\theta$ 微分だけがゼロでない：

$$
\partial_\theta g_{\phi\phi} = 2a^2\sin\theta\cos\theta
$$

公式に代入します：

$$
\Gamma^\theta{}_{\phi\phi} = \frac12g^{\theta\theta}\big(-\partial_\theta g_{\phi\phi}\big) = \frac1{2a^2}\big(-2a^2\sin\theta\cos\theta\big) = -\sin\theta\cos\theta
$$

$$
\Gamma^\phi{}_{\theta\phi} = \frac12g^{\phi\phi}\big(\partial_\theta g_{\phi\phi}\big) = \frac1{2a^2\sin^2\theta}\big(2a^2\sin\theta\cos\theta\big) = \cot\theta
$$

（他の $\Gamma$ 成分はすべてゼロ。）

## 15. リーマン曲率テンソルを計算する

2次元なので、独立な成分は本質的に1つ（$R^\theta{}_{\phi\theta\phi}$）だけです。定義式に代入します：

$$
R^\theta{}_{\phi\theta\phi} = \partial_\theta\Gamma^\theta{}_{\phi\phi} - \partial_\phi\Gamma^\theta{}_{\theta\phi} + \Gamma^\theta{}_{\theta m}\Gamma^m{}_{\phi\phi} - \Gamma^\theta{}_{\phi m}\Gamma^m{}_{\theta\phi}
$$

各項を計算します：

- $\partial_\theta\Gamma^\theta{}_{\phi\phi} = \partial_\theta(-\sin\theta\cos\theta) = \sin^2\theta-\cos^2\theta$
- $\Gamma^\theta{}_{\theta\phi}=0$ なので $\partial_\phi\Gamma^\theta{}_{\theta\phi}=0$
- $\Gamma^\theta{}_{\theta m}\Gamma^m{}_{\phi\phi}$：$\Gamma^\theta{}_{\theta\theta}=0,\ \Gamma^\theta{}_{\theta\phi}=0$ なので、この項はゼロ
- $\Gamma^\theta{}_{\phi m}\Gamma^m{}_{\theta\phi}$：$m=\phi$ の項だけ残る：$\Gamma^\theta{}_{\phi\phi}\Gamma^\phi{}_{\theta\phi} = (-\sin\theta\cos\theta)(\cot\theta) = -\cos^2\theta$

まとめると：

$$
R^\theta{}_{\phi\theta\phi} = (\sin^2\theta-\cos^2\theta) - 0 + 0 - (-\cos^2\theta) = \sin^2\theta
$$

添字を下げます（$R_{\theta\phi\theta\phi}=g_{\theta\theta}R^\theta{}_{\phi\theta\phi}$）：

$$
\boxed{R_{\theta\phi\theta\phi} = a^2\sin^2\theta}
$$

## 16. ガウス曲率との一致

2次元曲面のガウス曲率 $K$ は、$K=\dfrac{R_{\theta\phi\theta\phi}}{\det g}$（$\det g=g_{\theta\theta}g_{\phi\phi}=a^4\sin^2\theta$）で与えられます：

$$
K = \frac{a^2\sin^2\theta}{a^4\sin^2\theta} = \frac1{a^2}
$$

$$
\boxed{K=\frac1{a^2}}
$$

これは、半径 $a$ の球面のガウス曲率として教科書でよく知られている値と完全に一致します。**半径が大きいほど曲率が小さい**（大きな球ほど局所的には平らに見える）という直感とも整合します。極座標（Part VI）では $R=0$ になる（各自、上と同じ計算を極座標の $\Gamma$ に対して行うと、すべての項が打ち消し合ってゼロになることを確認できます）のに対し、球面では $R\ne0$ になる、という対比が「曲率とは何か」を最もクリアに示す最小例です。

---

# Part IX：リッチテンソル・スカラー曲率（簡単な紹介のみ）

リーマン曲率テンソルは添字が4本あって扱いにくいので、縮約して情報を圧縮したものがよく使われます：

$$
\boxed{R_{ij} := R^k{}_{ikj}}\qquad\text{（リッチテンソル、2階）}
$$

$$
\boxed{R := g^{ij}R_{ij}}\qquad\text{（スカラー曲率、1つの数）}
$$

2次元の場合、スカラー曲率とガウス曲率の間には $R=2K$ という単純な関係があります（今回の球面の例なら $R=2/a^2$）。一般相対論のアインシュタイン方程式はこの $R_{ij}$ と $R$ を使って書かれますが、今回はそこまでは踏み込みません。

---

# まとめ：全体の位置づけ

```
計量 g_ij（内積の表）
        │  微分（3つの式を組み合わせる）
        ▼
クリストッフェル記号 Γ^k_ij（基底ベクトルの変化率）
        │  ※ Γ自体はテンソルではない（極座標の例：Γ≠0でも空間は平坦）
        │
        ├─ 共変微分 ∇_jV^k = ∂_jV^k + Γ^k_ij V^i
        │      （基底の変化を補正した「正しい微分」）
        │
        ├─ 測地線方程式 q̈^k + Γ^k_ij q̇^i q̇^j = 0
        │      （曲線座標で見た「まっすぐな道」）
        │
        └─ リーマン曲率テンソル R^l_kij = ∂Γ-∂Γ+ΓΓ-ΓΓ
                （共変微分の非可換性、真の意味での「曲がり」）
                        │
                        ├─ 極座標（平坦）→ R=0
                        └─ 球面（曲がっている）→ R_θφθφ=a²sin²θ → ガウス曲率 K=1/a²
                                        │
                                        ▼
                        リッチテンソル R_ij、スカラー曲率 R=2K
                                        │
                                        ▼
                        （この先が一般相対論・アインシュタイン方程式）
```

今回の要点は、**「計量さえ与えられれば、クリストッフェル記号も曲率テンソルも、追加の仮定なしに完全に計算で決まる」**という点と、**「クリストッフェル記号がゼロでないことと、空間が曲がっていることはまったく別の話」**という点の2つでした。極座標という平坦な例と、球面という曲がった例を並べて実際に手を動かして計算することで、この違いが数字として体感できたと思います。一般相対論はこの続き（$R_{ij}$、$R$、そして物質のエネルギー・運動量テンソルを結びつけるアインシュタイン方程式）にありますが、そこは今回は扱わず、高階テンソルの入り口として、この位置で一区切りにします。
