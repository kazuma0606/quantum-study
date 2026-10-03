# 行列値の微分形式・ゲージ理論・4次元時空への拡張

これまで扱ってきた微分形式（スカラー係数）を、①**行列を係数に持つ形式**（ゲージ理論・クリストッフェル記号との統合）と、②**4次元時空・複素数値の形式**（相対論・量子力学との接続）の2方向に拡張します。

---

# Part I：定義域と値域は独立という前提の確認

以前確認した通り、微分形式の「形式らしさ」（wedge積の反対称構造）は**定義域**（$\Omega\subset\mathbb R^n$、時空、多様体）の性質であり、**値域**（係数がどんな対象か：実数、複素数、行列）とは独立です。$\omega=\psi(x)\,dx$の$\psi$が実数・複素数・行列のどれであっても、外微分・wedge積の計算規則はそのまま機能します。この前提の上で、以下ではまず値域を「行列」にした場合を扱います。

---

# Part II：ゲージ場は「行列値の1-形式」

## 1. ゲージ場の定義

電磁ポテンシャル$A$（実数値の1-形式）を、$SU(2)$のような非可換ゲージ理論に一般化すると、$A$は**行列（リー代数の元）を係数に持つ1-形式**になります：

$$
A = A_\mu^a\,T^a\,dx^\mu\qquad(T^a\text{：生成子、}SU(2)\text{なら}T^a=\sigma^a/2)
$$

以前のパウリ行列のノートで扱った生成子$T^a=\sigma^a/2$が、ここで「1-形式の係数」として登場しています。

## 2. なぜ $A\wedge A\ne0$ になるのか

以前、スカラー係数の1-形式については $\alpha\wedge\alpha=0$（Part I §4の代数的性質）を確認しました。これは**係数同士が可換（スカラー）だから成り立つ**性質であり、行列係数では一般に崩れます。実際に確認します：

$$
A\wedge A = (A_\mu\,dx^\mu)\wedge(A_\nu\,dx^\nu) = A_\mu A_\nu\,dx^\mu\wedge dx^\nu
$$

（$A_\mu:=A_\mu^aT^a$、行列。）$dx^\mu\wedge dx^\nu$は$\mu,\nu$について反対称ですが、**この式全体を$\mu\leftrightarrow\nu$で入れ替えても、$A_\mu A_\nu$の部分は行列の積のままなので、単純にゼロにはなりません**。対称・反対称に分解すると：

$$
A_\mu A_\nu\,dx^\mu\wedge dx^\nu = \frac12(A_\mu A_\nu-A_\nu A_\mu)\,dx^\mu\wedge dx^\nu = \frac12[A_\mu,A_\nu]\,dx^\mu\wedge dx^\nu
$$

（これは、以前ポアンカレの補題のノートで確認した「対称×反対称の和はゼロになる」という補題の**逆**を使っています：$A_\mu A_\nu$を対称部分と反対称部分に分けると、対称部分は$dx^\mu\wedge dx^\nu$の反対称性と組み合わさってゼロになり、**反対称部分（交換子）だけが生き残る**、という構造です。)

$$
\boxed{A\wedge A = \frac12[A_\mu,A_\nu]\,dx^\mu\wedge dx^\nu}
$$

**スカラー係数なら$[A_\mu,A_\nu]=0$（数同士は可換）なので消えますが、行列係数では$[A_\mu,A_\nu]\ne0$（パウリ行列の交換関係$[\sigma_i,\sigma_j]=2i\varepsilon_{ijk}\sigma_k$がここで再び登場する場所）なので、一般に消えません。**

## 3. Yang-Mills場の強さ

$$
\boxed{F := dA+A\wedge A}
$$

電磁気学（$U(1)$、可換）では$A\wedge A=0$なので$F=dA$（以前確認した式）に戻りますが、$SU(2)$のような非可換ゲージ理論では$A\wedge A$という項が本質的に必要です。

---

# Part III：接続と曲率 ―クリストッフェル記号のノートとの統合

## 4. クリストッフェル記号を「行列値1-形式」として書く

以前のクリストッフェル記号$\Gamma^i{}_{jk}$を、行列の添字を$i,j$（行・列）、形式の添字を$k$として、1-形式にまとめます：

$$
\omega^i{}_j := \Gamma^i{}_{jk}\,dx^k
$$

## 5. 曲率 $\Omega=d\omega+\omega\wedge\omega$ を成分まで展開し、リーマン曲率テンソルと完全一致することを確認する

**$d\omega$の計算**：一般に、1-形式$\alpha=\alpha_kdx^k$の外微分は $d\alpha=\frac12(\partial_l\alpha_k-\partial_k\alpha_l)dx^l\wedge dx^k$ という、反対称化された形に書けます（これも以前の計算と同じ、対称・反対称の仕分けです）。$\alpha_k=\Gamma^i{}_{jk}$として：

$$
d\omega^i{}_j = \frac12\big(\partial_k\Gamma^i{}_{jl}-\partial_l\Gamma^i{}_{jk}\big)\,dx^k\wedge dx^l
$$

**$\omega\wedge\omega$の計算**：

$$
(\omega\wedge\omega)^i{}_j = \omega^i{}_p\wedge\omega^p{}_j = \Gamma^i{}_{pk}\,dx^k\wedge\Gamma^p{}_{jl}\,dx^l = \Gamma^i{}_{pk}\Gamma^p{}_{jl}\,dx^k\wedge dx^l
$$

**ここでも「対称×反対称＝0」の構造を使います**：$dx^k\wedge dx^l$が反対称なので、係数$\Gamma^i{}_{pk}\Gamma^p{}_{jl}$のうち、$k,l$について対称な部分は自動的に消え、反対称化した部分だけが生き残ります：

$$
(\omega\wedge\omega)^i{}_j = \frac12\big(\Gamma^i{}_{pk}\Gamma^p{}_{jl}-\Gamma^i{}_{pl}\Gamma^p{}_{jk}\big)\,dx^k\wedge dx^l
$$

**両方を足します**：

$$
\Omega^i{}_j = d\omega^i{}_j+(\omega\wedge\omega)^i{}_j = \frac12\Big[\big(\partial_k\Gamma^i{}_{jl}-\partial_l\Gamma^i{}_{jk}\big) + \big(\Gamma^i{}_{pk}\Gamma^p{}_{jl}-\Gamma^i{}_{pl}\Gamma^p{}_{jk}\big)\Big]dx^k\wedge dx^l
$$

$\Omega^i{}_j=:\frac12R^i{}_{jkl}\,dx^k\wedge dx^l$（$R$は$k,l$について反対称、という慣習的な定義）と置くと：

$$
\boxed{R^i{}_{jkl} = \partial_k\Gamma^i{}_{jl}-\partial_l\Gamma^i{}_{jk}+\Gamma^i{}_{pk}\Gamma^p{}_{jl}-\Gamma^i{}_{pl}\Gamma^p{}_{jk}}
$$

**これは、以前のクリストッフェル記号のノートで独立に導出したリーマン曲率テンソルの公式**

$$
R^l{}_{kij} = \partial_i\Gamma^l{}_{jk}-\partial_j\Gamma^l{}_{ik}+\Gamma^l{}_{im}\Gamma^m{}_{jk}-\Gamma^l{}_{jm}\Gamma^m{}_{ik}
$$

**と、添字の名前の対応（$i\to l,\ j\to k,\ k\to i,\ l\to j,\ p\to m$）を付ければ、$\partial\Gamma-\partial\Gamma+\Gamma\Gamma-\Gamma\Gamma$という構造がまったく同一であることが、今回実際の展開で確認できました。**

$$
\boxed{\text{クリストッフェル記号}\ \Gamma\ =\ \text{接続}\ \omega\ (GL(n)\text{値の1-形式)}\qquad\text{リーマン曲率}\ =\ \text{曲率}\ \Omega=d\omega+\omega\wedge\omega}
$$

一般相対論の曲率とゲージ理論の場の強さは、「行列値の微分形式」という同じ言語で、文字通り同じ式でした。$\omega\wedge\omega$の非ゼロ性（Part IIの§2）が、クリストッフェル記号のノートで扱った$\Gamma\Gamma$の項（曲率の中の2次の項）の正体そのものです。

---

# Part IV：ホロノミー（平行移動の一般化）

以前扱った$e^{\theta J}$、$e^{-i\theta\sigma/2}$（生成子→指数写像→有限の変換）を、接続$A$（あるいは$\omega$）に沿って経路を"積分"した、**経路順序付き指数関数**として一般化します：

$$
\boxed{U(\gamma) = \mathcal P\exp\left(\int_\gamma A\right)}
$$

（$\mathcal P$：経路順序化。$A$が行列で非可換なので、単純な指数の肩の足し算では済まず、経路に沿った掛け算の順番を保つ必要があります。）これが**ホロノミー**（平行移動）で、クリストッフェル記号のノートで扱った測地線・平行移動の議論を、任意のゲージ群に一般化したものです。

---

# Part V：4次元時空でのHodgeスターの符号

## 6. $\star(dt\wedge dx)=-dy\wedge dz$ の導出

4次元時空（$t,x,y,z$）のミンコフスキー計量 $\eta=\operatorname{diag}(-1,+1,+1,+1)$（時間方向だけ符号が違う）を使います。定義式$\beta\wedge\star\alpha=\langle\beta,\alpha\rangle\operatorname{vol}$に$\alpha=\beta=dt\wedge dx$を代入します。

内積を計算します：

$$
\langle dt\wedge dx,\,dt\wedge dx\rangle = \eta^{tt}\eta^{xx}-\eta^{tx}\eta^{xt} = (-1)(1)-0 = -1
$$

$\operatorname{vol}=dt\wedge dx\wedge dy\wedge dz$なので：

$$
(dt\wedge dx)\wedge\star(dt\wedge dx) = -dt\wedge dx\wedge dy\wedge dz
$$

$\star(dt\wedge dx)=C\,dy\wedge dz$と置いて代入すると$C=-1$：

$$
\boxed{\star(dt\wedge dx) = -dy\wedge dz}
$$

**理由は$\eta^{tt}=-1$、時間方向の計量成分だけ符号が反対**だからです。これまでの3次元空間（計量がすべて$+1$）では一度も出てこなかった符号です。時間軸をまたぐHodgeスターには、必ずこの$-1$が1個ついてきます（$\star(dt\wedge dy)=-dz\wedge dx$、$\star(dt\wedge dz)=-dx\wedge dy$も同様。一方$\star(dx\wedge dy)=dt\wedge dz$のように、時間軸を含まない組から時間軸を含む組を作るときは符号が付きません）。

## 7. 電磁気学での意味

これが、電磁場テンソル$F$を扱ったとき、電場成分$\mathbf E$と磁場成分$\mathbf B$が$\star$を通すと入れ替わりつつ、**片方にだけマイナス符号がつく**（$\star F$を計算すると$\mathbf E\leftrightarrow\mathbf B$が非対称な符号関係で入れ替わる）という、電磁気学の教科書でよく見る現象の直接の原因です。

---

# Part VI：複素数値の微分形式と、ゲージ共変微分

## 8. 波動関数は「複素数値の0-形式」

$\psi(t,x,y,z)$は、時空という実数の多様体の上の複素数値関数、つまり**複素数値の0-形式**です。$d\psi=\partial_t\psi\,dt+\partial_x\psi\,dx+\partial_y\psi\,dy+\partial_z\psi\,dz$も、普通に計算できる複素数値の1-形式です。Part Iで確認した通り、**定義域（実数の時空）と値域（複素数）は独立**なので、これまでの微分形式の理論はそのまま使えます。

## 9. ゲージ共変微分：$U(1)$・電磁場・波動関数の合流

電磁場$F=dA$と波動関数$\psi$を組み合わせると、電磁場中の荷電粒子のシュレディンガー方程式（あるいはディラック方程式）に出てくる**共変微分**が、複素数値形式の言葉で書けます：

$$
\boxed{D\psi := d\psi-ieA\,\psi}
$$

（$A$：電磁ポテンシャルという実数値の1-形式、$e$：電荷。）これは$d$を、$A$という「ゲージ場」で補正した演算子です。以前扱った$U(1)$（複素数の位相、$e^{i\theta}$の群）が、ここで「電磁場のゲージ対称性」として、微分形式$A$と複素数値関数$\psi$を橋渡ししています。最初期の複素数の幾何学のノート（$U(1)\cong S^1$）が、ここで量子力学のゲージ理論という形で、もう一度合流します。

## 10. さらに先：複素幾何・Dolbeault複体（触りだけ）

複素数自体を「1つの複素座標$z=x+iy$」として扱う**複素幾何**では、$dz:=dx+i\,dy$という複素数値の1-形式を定義できます（複素数の幾何学のノートの$\mathbb C\cong\mathbb R^2$の直接の延長）。正則関数の理論とHodge理論を組み合わせた**Dolbeault複体**（$d=\partial+\bar\partial$という分解）という、さらに一段深い理論に繋がりますが、これはKähler多様体・代数幾何という、また別の広大な領域の入り口になります。

---

# まとめ：全体の構造

```
定義域（座標）と値域（係数）は独立
        │
        ├─ 値域を「行列」にする
        │     │
        │     ├─ A（ゲージ場）= 行列値1-形式、A∧A = (1/2)[A_μ,A_ν]dx^μ∧dx^ν ≠ 0
        │     ├─ F = dA + A∧A（Yang-Mills場の強さ）
        │     ├─ ω=Γ^i_jk dx^k（接続）、Ω=dω+ω∧ω = リーマン曲率テンソル（成分まで完全一致を確認）
        │     └─ U(γ)=P exp∫A（ホロノミー、平行移動の一般化）
        │
        └─ 値域を「複素数」、定義域を「4次元時空」にする
              │
              ├─ ⋆(dt∧dx)=-dy∧dz（ミンコフスキー計量の符号が生む非対称性、E,Bの入れ替わり）
              ├─ ψ（波動関数）= 複素数値0-形式
              ├─ Dψ = dψ-ieAψ（ゲージ共変微分、U(1)と電磁場と波動関数の合流）
              └─ dz=dx+idy → Dolbeault複体（複素幾何、さらに先の理論）
```

一般相対論（クリストッフェル記号・曲率）とゲージ理論（Yang-Mills・電磁気学）が、「行列値の微分形式」という1つの言葉の中で、**添字の付け替えを除いて文字通り同じ式**だったことが、今回の展開で具体的に確認できました。$SU(2)$・パウリ行列のノートから始まった一連の探索が、ここで一般相対論・場の理論という、物理学の2大柱の共通の骨格に到達したことになります。
