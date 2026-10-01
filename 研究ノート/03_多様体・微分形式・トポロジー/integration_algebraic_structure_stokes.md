# 積分の代数的構造 ―Stokesの定理から de Rhamコホモロジーまで―

これまで「微分」側（$\operatorname{grad},\operatorname{div},\operatorname{rot}\to d$、$d^2=0$）を徹底的に抽象化してきました。ここでは「積分」側にも、まったく同じくらい強い代数的構造があることを示します。特に、$d$と境界作用素$\partial$が**互いに随伴（共役）である**という事実は、以前のブラケット記法のノートで扱った「エルミート共役」の概念と、驚くほど同じ形をしています。

---

# Part I：出発点 ―微積分の基本定理を思い出す

$$
\int_a^bf'(x)\,dx = f(b)-f(a)
$$

これを「領域とその境界」という言葉で言い換えます。積分区間 $[a,b]$ の**境界**は、2つの点 $\{a,b\}$ です（向き付きで、$b$は$+$、$a$は$-$として数える）。すると、右辺 $f(b)-f(a)$ は、「$f$を境界上で評価して、符号付きで足し合わせたもの」と見なせます：

$$
\int_{[a,b]}df = \int_{\partial[a,b]}f
$$

（$df=f'(x)dx$、$\partial[a,b]=\{b\}-\{a\}$という「符号付きの点の集まり」への$0$次元の積分は、単にその点での関数の値。）**これが、この先の一般化ストークスの定理の、最も単純な特殊ケースです。**

---

# Part II：一般化ストークスの定理

$$
\boxed{\int_Md\omega = \int_{\partial M}\omega}
$$

（$M$：$k$次元の向き付き領域、$\partial M$：その境界（$(k-1)$次元）、$\omega$：$(k-1)$-形式。）

## 具体化1：$\omega$が0-形式（$k=1$）→ 微積分の基本定理

Part Iそのものです。

## 具体化2：$\omega$が1-形式（$k=2$）→ グリーンの定理・ストークスの定理

$\omega=P\,dx+Q\,dy$（平面領域$M$）とすると、以前確認した通り $d\omega=(\partial_xQ-\partial_yP)\,dx\wedge dy$ なので：

$$
\iint_M(\partial_xQ-\partial_yP)\,dx\,dy = \oint_{\partial M}(P\,dx+Q\,dy)
$$

**これがグリーンの定理そのものです。** 3次元で$\omega$を$\operatorname{rot}$に対応する1-形式とみなせば、おなじみのストークスの定理（曲面積分＝境界の線積分）になります。

## 具体化3：$\omega$が2-形式（$k=3$）→ ガウスの発散定理

$\omega$を$\operatorname{div}$に対応する2-形式とすると、$d\omega$は3-形式（＝$\operatorname{div}\mathbf V$を体積要素倍したもの）なので：

$$
\iiint_M\operatorname{div}\mathbf V\,dV = \oiint_{\partial M}\mathbf V\cdot d\mathbf A
$$

**これがガウスの発散定理です。**

## まとめ

$$
\boxed{\text{微積分の基本定理、グリーンの定理、ストークスの定理、ガウスの発散定理は、すべて}\int_Md\omega=\int_{\partial M}\omega\text{という1本の式の、次数違いの特殊ケース}}
$$

前回のノートで「$\operatorname{grad},\operatorname{div},\operatorname{rot}$は$d$という1つの演算子に統一される」と確認しましたが、**それぞれに対応する積分定理たちも、まったく同じように1本の式に統一されていた**ということです。

---

# Part III：積分を「ペアリング」として捉え直す

$\omega$（形式）と$C$（積分する領域、「チェイン」と呼ばれます）の組から、実数を作る操作として積分を捉えます：

$$
\langle\omega,C\rangle := \int_C\omega
$$

これは、以前のブラケット記法のノートで扱った**内積 $\langle\phi|\psi\rangle$ と同じ役割**（2つの対象から1つの数を作る、双線形なペアリング）を果たします。Stokesの定理を、このペアリングの記法で書き直すと：

$$
\langle d\omega,C\rangle = \int_Cd\omega = \int_{\partial C}\omega = \langle\omega,\partial C\rangle
$$

$$
\boxed{\langle d\omega,C\rangle = \langle\omega,\partial C\rangle}
$$

## エルミート共役との対応

以前、エルミート演算子について

$$
\langle\hat A\phi|\psi\rangle = \langle\phi|\hat A^\dagger\psi\rangle
$$

（$\hat A$を左のブラ側にかけたものは、右のケット側に$\hat A^\dagger$をかけたものと同じ）という関係を扱いました。今回の

$$
\langle d\omega,C\rangle = \langle\omega,\partial C\rangle
$$

は、**$d$を「$\omega$側にかける」ことと、$\partial$を「$C$側にかける」ことが、ペアリングを通じて等価である**という、まったく同じ構造をしています。つまり：

$$
\boxed{d\ \text{と}\ \partial\ \text{は、積分というペアリングに関して、互いに随伴（共役）の関係にある}}
$$

エルミート共役が「内積を保つように、演算子を片方からもう片方に移し替える」操作だったのと同様に、Stokesの定理は「$d$（代数的な微分操作）を、$\partial$（幾何学的な境界を取る操作）に移し替える」規則になっています。

---

# Part IV：$\partial^2=0$ ―境界の境界は存在しない

以前、$d^2=0$を「対称×反対称＝0」という一般的な代数の構造から導出しました。境界作用素$\partial$にも、対応する性質があります：

$$
\boxed{\partial(\partial C) = \varnothing}
$$

**直感的な確認**：円盤の境界は円周です。では円周の境界は？ 円周は「縁のない」閉じた曲線なので、境界は存在しません（空集合）。同様に、球の境界は球面で、球面自体には境界がありません。**「境界を取る」という操作を2回繰り返すと、必ず何もない状態になる**、というのが$\partial^2=0$の意味です。

## $d^2=0$との双対性

Part IIIの随伴関係を2回使うと：

$$
\langle d^2\omega,C\rangle = \langle d\omega,\partial C\rangle = \langle\omega,\partial^2C\rangle
$$

もし$d^2=0$が成り立つなら、左辺は任意の$C$について$0$。**任意の$C$についてペアリングが$0$になるためには、右辺の$\partial^2C$が（実質的に）空でなければなりません。** つまり、$d^2=0$と$\partial^2=0$は、**片方が成り立てば、ペアリングを通じてもう片方も要請される、双対の関係**にあります。前回のノートで「$d^2=0$は対称×反対称の構造から必然的に成り立つ」と確認しましたが、**その必然性が、幾何学側では「境界に境界はない」という、これまた直感的に明らかな事実として現れている**、というのが今回の対応関係の美しいところです。

---

# Part V：de Rhamコホモロジー ―積分が「位相」を検出する

## 1. 閉形式と完全形式

$d\omega=0$を満たす$\omega$を**閉形式**、$\omega=d\eta$と書ける$\omega$を**完全形式**と呼びます。$d^2=0$から、**完全形式は必ず閉形式**です（$\omega=d\eta\Rightarrow d\omega=d(d\eta)=0$）。しかし**逆は一般に成り立ちません**。この「閉形式だが完全形式でない」という食い違いが、空間の位相的な性質（穴の有無など）を検出します。

## 2. 具体例：原点を除いた平面上の1-形式

$$
\omega := \frac{-y\,dx+x\,dy}{x^2+y^2}\qquad(\text{原点}(0,0)\text{を除いた平面上で定義})
$$

**閉形式であることの確認**：$P=\dfrac{-y}{x^2+y^2}$、$Q=\dfrac{x}{x^2+y^2}$ として、$\partial_xQ-\partial_yP$を計算します（商の微分）：

$$
\partial_xQ = \frac{(x^2+y^2)-x(2x)}{(x^2+y^2)^2} = \frac{y^2-x^2}{(x^2+y^2)^2},\qquad \partial_yP = \frac{-(x^2+y^2)+y(2y)}{(x^2+y^2)^2} = \frac{y^2-x^2}{(x^2+y^2)^2}
$$

$$
\partial_xQ-\partial_yP = 0 \quad\Longrightarrow\quad d\omega=0
$$

**確かに閉形式です。**

**完全形式でないことの確認**：単位円 $x=\cos\theta,\ y=\sin\theta$（$dx=-\sin\theta\,d\theta,\ dy=\cos\theta\,d\theta$）に沿って$\omega$を積分します：

$$
\omega = \frac{-\sin\theta(-\sin\theta\,d\theta)+\cos\theta(\cos\theta\,d\theta)}{1} = (\sin^2\theta+\cos^2\theta)\,d\theta = d\theta
$$

$$
\oint_{|z|=1}\omega = \int_0^{2\pi}d\theta = 2\pi
$$

**もし$\omega$が完全形式（$\omega=df$、ある関数$f$の全微分）なら、閉じたループに沿った積分は必ず$0$になるはずです**（$\oint_Cdf=f(\text{終点})-f(\text{始点})=0$、始点と終点が同じ点だから）。実際には$2\pi\ne0$なので、**$\omega$は閉形式だが完全形式ではない**ことが確認できました。

## 3. これは何を検出しているのか

$\omega$は、実は**偏角$\theta=\arctan(y/x)$の全微分**です（$\theta$自体は原点の周りを1周すると$2\pi$だけ不連続に変化してしまう、多価関数なので、単一の関数$f=\theta$として**大域的**には定義できません）。この「局所的には$\theta$という関数の微分に見えるのに、大域的には1つの関数として存在できない」という食い違いこそが、**「原点という穴が1つ空いている」という、平面の位相的な性質**を検出しているのです。

$$
\boxed{
\begin{aligned}
&\text{原点を含む平面（穴なし）：この}\omega\text{に対応するものは大域的に}df\text{と書け、積分はゼロ}\\
&\text{原点を除いた平面（穴あり）：}\omega\text{は閉形式だが完全形式でなく、積分は}2\pi\ne0
\end{aligned}
}
$$

**これが「微分形式・微分方程式を調べていたら、いつの間にか空間の"穴の数"という位相的情報が出てきた」という現象の、一番具体的でシンプルな例です。** 以前扱った$U(1)\cong S^1$という円周の構造や、経路積分での位相の巻き付き方とも、この「$2\pi$の巻き付き数」という考え方は本質的に同じです。

## 4. de Rhamコホモロジー群

$$
\boxed{H^k_{\mathrm{dR}}(M) := \frac{\{\text{閉}k\text{-形式}\}}{\{\text{完全}k\text{-形式}\}}}
$$

（閉形式全体を、完全形式で「割った」商空間。）この群の次元（ベッチ数）が、空間$M$の「$k$次元の穴の数」を数えます。原点を除いた平面なら$H^1_{\mathrm{dR}}\cong\mathbb R$（1次元、$\omega$がその代表元）で、「穴が1つ」という情報とちょうど対応します。**解析（微分方程式）の言葉で定義された対象が、純粋に位相的な不変量と一致する**、というのがde Rham理論の核心です。

---

# Part VI：Cartanのマジック公式 ―積分・流れ・Lie群の再接続

$$
\boxed{\mathcal L_X\omega = d(i_X\omega)+i_X(d\omega)}
$$

- $i_X\omega$：**内部積**。ベクトル場$X$を$\omega$に「差し込んで」次数を1つ下げる操作（$k$-形式→$(k-1)$-形式）
- $\mathcal L_X\omega$：**Lie微分**。$X$が生成する流れに沿って$\omega$を運んだときの変化率

## $e^{tX}$との接続

以前、$SU(2)$や複素数のノートで、$e^{\theta J}$（行列の指数関数）が「$J$という生成子から、有限の回転という変換を作る」という構造を繰り返し見てきました。ベクトル場$X$についても同じ構造があり、$X$を「無限小の流れ」として指数化したもの $\phi_t:=e^{tX}$（$X$に沿って時間$t$だけ流れる、という変換）を考えると：

$$
\left.\frac{d}{dt}\right|_{t=0}\int_{\phi_t(M)}\omega = \int_M\mathcal L_X\omega
$$

**つまりCartanのマジック公式は、「ベクトル場が生成する流れに沿って積分領域を動かしたとき、積分の値がどう変化するか」を教えてくれる式**です。ここでも、以前散々扱った「生成子→指数写像→有限の変換」という構造（リー群論）と、今回の「$d,\partial,\int$」という積分の代数的構造が、$\mathcal L_X$を介して1つに合流しています。

---

# Part VII：超関数（デルタ関数）― ペアリング・随伴構造のもう一つの応用

Part IIIで確認した「$d$と$\partial$は、ペアリング$\langle\omega,C\rangle:=\int_C\omega$を介して互いに随伴である」という構造は、実は**デルタ関数のような、通常の意味では微分不可能な対象を「微分」するときにも、まったく同じ形で使われています。**

## 17. デルタ関数は「関数」ではなく「ペアリングそのもの」

$\delta(x)$は、$x=0$で無限大、他所ではゼロという、古典的な関数としては定義不可能な対象です。正確には、**「テスト関数$\varphi$（滑らかで、遠方でゼロになる関数）を1つ受け取ると、数$\varphi(0)$を返す」という、ペアリングとして定義**されます：

$$
\langle\delta,\varphi\rangle := \varphi(0)
$$

**これは、$\langle\omega,C\rangle=\int_C\omega$（形式$\omega$と領域$C$のペアリング）と、まったく同じ発想の道具**です。$\delta$を単体で扱わず、常に「何かとペアにして」初めて意味を持つ、という点が共通しています。

## 18. $\delta$の微分も、随伴関係を使って「押し付ける」

超関数の微分は、部分積分で微分をテスト関数側に移す、という規則で定義されます：

$$
\int_{-\infty}^\infty\delta'(x)\varphi(x)\,dx := -\int_{-\infty}^\infty\delta(x)\varphi'(x)\,dx = -\varphi'(0)
$$

（部分積分 $\int\delta'\varphi\,dx=[\delta\varphi]-\int\delta\varphi'\,dx$ で、境界項$[\delta\varphi]$は$\varphi$が遠方でゼロなので消える、というのが形式的な動機です。）

$$
\boxed{\langle\delta',\varphi\rangle := -\langle\delta,\varphi'\rangle}
$$

**この定義は、$\delta$自体を一切微分していません。** 微分という操作を、常に滑らかな（$C^\infty$の）テスト関数$\varphi$の方に押し付けているだけです。$\varphi$は最初から滑らかだと仮定されているので、$\varphi'$は何の問題もなく存在します。

## 19. Part IIIの随伴関係と、寸分違わず同じ構造

$$
\boxed{\langle d\omega,C\rangle = \langle\omega,\partial C\rangle}\qquad(\text{Part III})
\qquad\Longleftrightarrow\qquad
\boxed{\langle\delta',\varphi\rangle = -\langle\delta,\varphi'\rangle}\qquad(\text{今回})
$$

「$d$を左側（$\omega$）にかけることと、$\partial$を右側（$C$）にかけることが等価」という関係と、「微分を左側（$\delta$）にかけることと、微分を右側（$\varphi$）にかけて符号を反転させることが等価」という関係は、**同じ"随伴"という仕組みの、別の場面での現れ**です。**「$\delta$を微分する」という本来定義できない操作を、「ペアリングの相方を、代わりに微分する」という常に実行可能な操作に置き換えている**、という点が共通しています。

## 20. フーリエ変換との接続：$x$空間の粗さと$k$空間の滑らかさ

$\delta$のフーリエ変換を計算すると：

$$
\mathcal F[\delta](k) = \int_{-\infty}^\infty\delta(x)e^{-ikx}dx = e^{-ik\cdot0} = 1
$$

**$\delta$（$x$空間では無限に鋭く尖った対象）のフーリエ変換は、定数関数$1$（$k$空間ではこの上なく滑らかな$C^\infty$関数）になります。** これは、以前のブラケット記法のノートで扱った$|x\rangle$（位置の固有状態、$x$空間ではデルタ関数）と、それを運動量基底に射影した$\langle p|x\rangle=e^{-ipx/\hbar}/\sqrt{2\pi\hbar}$（滑らかな平面波）の関係と、まったく同じ現象です。「$x$空間で粗い」ことと「$k$空間で滑らか」であることは、同じ対象の裏表です。

## まとめ

$$
\boxed{
\begin{aligned}
&\delta\text{は関数ではなく、テスト関数とのペアリングとして定義される超関数}\\
&\delta'\text{の定義}\langle\delta',\varphi\rangle=-\langle\delta,\varphi'\rangle\text{は、微分を常に滑らかなテスト関数側に移し替える操作}\\
&\text{これはPart IIIの}\langle d\omega,C\rangle=\langle\omega,\partial C\rangle\text{とまったく同じ「随伴」の構造}\\
&\delta\text{のフーリエ変換は定数（滑らか）：}x\text{空間で粗い⇔}k\text{空間で滑らか、という一般的な対応の一例}
\end{aligned}
}
$$

---

# まとめ：全体の図解

```
微積分の基本定理 ∫f'dx = f(b)-f(a)
        │  一般化（境界＝符号付きの点の集まり、という視点）
        ▼
一般化ストークスの定理 ∫_M dω = ∫_{∂M} ω
        │  0-形式→基本定理／1-形式→グリーン・ストークス／2-形式→ガウス
        ▼
ペアリング ⟨ω,C⟩:=∫_Cω を導入
        │
        ▼
⟨dω,C⟩=⟨ω,∂C⟩ ―― dと∂は互いに随伴（エルミート共役と同じ構造）
        │
        ▼
∂²=0（境界に境界はない）←→ d²=0（前回のノート）：随伴関係を通じた双対
        │
        ▼
閉形式（dω=0）と完全形式（ω=dη）の食い違い
        │  具体例：原点を除いた平面の (-ydx+xdy)/(x²+y²)、∮ω=2π≠0
        ▼
de Rhamコホモロジー H^k_dR(M) = 閉形式／完全形式
        （解析的に定義された量が、空間の「穴の数」という位相的情報を検出する）
        │
        ▼
Cartanのマジック公式 L_Xω = d(i_Xω)+i_X(dω)
        （積分領域を、ベクトル場が生成する流れ e^{tX} で動かしたときの変化率）
        → 以前のLie群・指数写像の話と再接続
```

「積分は微分ほど抽象化されていないのでは」という最初の疑問への答えは、**積分は微分の"逆操作"にとどまらず、$d$と互いに随伴な$\partial$という独立の代数的対象を持ち、そのペアリングを通じて空間の位相まで検出する、少なくとも微分と同じだけの深さを持つ構造**だった、ということになります。
