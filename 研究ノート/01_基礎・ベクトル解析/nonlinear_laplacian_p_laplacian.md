# 非線形ラプラシアン入門 ―$p$-ラプラシアンの導出と具体例―

「計量テンソルがあるからといって、方程式が線形であるとは限らない」という話の続きとして、**非線形ラプラシアン**の代表格である $p$-ラプラシアンを、変分原理から実際に導出し、1次元で完全に解ける具体例まで作ります。教科書にあまり載っていない内容とのことなので、「なぜあの形になるのか」を省略せずに追います。

---

# Part 0：線形作用素とは何か（復習）

作用素 $L$ が**線形**であるとは、任意の関数 $u,v$ と定数 $a,b$ に対して

$$
\boxed{L(au+bv) = aL(u)+bL(v)}
$$

（重ね合わせの原理）が成り立つことです。標準的なラプラシアン $\Delta u=\sum_i\partial_i^2u$ はこれを満たします：

$$
\Delta(au+bv) = \sum_i\partial_i^2(au+bv) = a\sum_i\partial_i^2u+b\sum_i\partial_i^2v = a\Delta u+b\Delta v
$$

微分という操作自体が線形（$\partial_i(au+bv)=a\partial_iu+b\partial_iv$）なので、それを繰り返すだけのラプラシアンも自動的に線形になります。**この性質は、計量が複雑かどうか（$\Delta_g$ かどうか）とは無関係**です。$\Delta_gu=\frac1{\sqrt{|g|}}\partial_i(\sqrt{|g|}g^{ij}\partial_ju)$ も、$u$ に対しては係数 $g^{ij},\sqrt{|g|}$ を固定して見れば、やはり線形です。

問題は、**この後に何を掛けるか**です。

---

# Part I：$p$-ラプラシアンの定義

$$
\boxed{\Delta_pu := \operatorname{div}\big(|\nabla u|^{p-2}\nabla u\big)}
$$

（$|\nabla u|=\sqrt{\sum_i(\partial_iu)^2}$、$p>1$ の実数）。$p=2$ なら $|\nabla u|^0=1$ なので $\Delta_2u=\operatorname{div}(\nabla u)=\Delta u$、通常のラプラシアンに戻ります。

$p\ne2$ のとき非線形になる理由を先に一言で言うと、**係数 $|\nabla u|^{p-2}$ 自体が $u$ に依存している**からです。$u$ を2倍にすれば、係数も変わってしまい、単純な比例関係が崩れます。

---

# Part II：変分原理からの導出（なぜこの形になるのか）

通常のラプラシアン $\Delta u=0$ は、**Dirichletエネルギー**

$$
E[u] = \frac12\int_\Omega|\nabla u|^2\,dx
$$

を最小化する関数が満たす方程式（Euler–Lagrange方程式）として自然に出てきます。$p$-ラプラシアンも、これを一般化した**$p$-エネルギー**

$$
\boxed{E_p[u] = \frac1p\int_\Omega|\nabla u|^p\,dx}
$$

の最小化から出てきます。これを実際に導出します。

## 1. 第一変分を計算する

$u$ を最小化する関数、$\varphi$ を境界でゼロになる任意のテスト関数（$\varphi|_{\partial\Omega}=0$）とし、$u+\varepsilon\varphi$（$\varepsilon$：小さなパラメータ）でエネルギーを評価します：

$$
F(\varepsilon) := E_p[u+\varepsilon\varphi] = \frac1p\int_\Omega|\nabla u+\varepsilon\nabla\varphi|^p\,dx
$$

$u$ が最小値を与えるなら、$\varepsilon=0$ で $F$ は極小値を取るはずなので $F'(0)=0$ です。

被積分関数を $\varepsilon$ で微分します。$|\mathbf v|^p=(\mathbf v\cdot\mathbf v)^{p/2}$ の形の連鎖律：

$$
\frac{d}{d\varepsilon}|\nabla u+\varepsilon\nabla\varphi|^p
= \frac{d}{d\varepsilon}\big[(\nabla u+\varepsilon\nabla\varphi)\cdot(\nabla u+\varepsilon\nabla\varphi)\big]^{p/2}
$$

$$
= \frac p2\big[(\nabla u+\varepsilon\nabla\varphi)\cdot(\nabla u+\varepsilon\nabla\varphi)\big]^{p/2-1}\cdot2(\nabla u+\varepsilon\nabla\varphi)\cdot\nabla\varphi
$$

$$
= p\,|\nabla u+\varepsilon\nabla\varphi|^{p-2}(\nabla u+\varepsilon\nabla\varphi)\cdot\nabla\varphi
$$

$\varepsilon=0$ を代入すると：

$$
\left.\frac{d}{d\varepsilon}\right|_{\varepsilon=0}|\nabla u+\varepsilon\nabla\varphi|^p = p\,|\nabla u|^{p-2}\nabla u\cdot\nabla\varphi
$$

したがって：

$$
F'(0) = \frac1p\int_\Omega p\,|\nabla u|^{p-2}\nabla u\cdot\nabla\varphi\,dx = \int_\Omega|\nabla u|^{p-2}\nabla u\cdot\nabla\varphi\,dx
$$

## 2. 部分積分で $\varphi$ を外に出す

ベクトル場 $\mathbf A:=|\nabla u|^{p-2}\nabla u$ と置きます。発散定理（部分積分の多次元版）：

$$
\int_\Omega\mathbf A\cdot\nabla\varphi\,dx = \int_{\partial\Omega}(\mathbf A\cdot\mathbf n)\varphi\,dS - \int_\Omega(\operatorname{div}\mathbf A)\varphi\,dx
$$

$\varphi|_{\partial\Omega}=0$ なので境界項は消えます：

$$
F'(0) = -\int_\Omega\operatorname{div}\big(|\nabla u|^{p-2}\nabla u\big)\varphi\,dx
$$

## 3. 変分法の基本補題

$F'(0)=0$ が**任意の**テスト関数 $\varphi$ について成り立たなければならないので（もし被積分関数がある点で正なら、その近くだけで正になる $\varphi$ を選べば積分も正になってしまい矛盾する、という論法）、被積分関数自体がゼロでなければなりません：

$$
\boxed{-\operatorname{div}\big(|\nabla u|^{p-2}\nabla u\big) = 0 \quad\Longleftrightarrow\quad \Delta_pu=0}
$$

これが**$p$-調和方程式**です。エネルギーに外力の仕事 $-\int_\Omega fu\,dx$ を足した汎関数 $E_p[u]-\int_\Omega fu\,dx$ を最小化すれば、同様の計算で

$$
\boxed{-\Delta_pu = f}
$$

が導かれます（$Δ_2u=-f$、つまり $-\Delta u=f$ のポアソン方程式の直接の一般化です）。

**まとめると**：$p$-ラプラシアンは「天下り的に定義された謎の演算子」ではなく、**「エネルギー汎関数の中の $|\nabla u|^2$ を $|\nabla u|^p$ に置き換えただけ」**という、非常に自然な一般化です。$p=2$ のときだけ、たまたまEuler-Lagrange方程式が線形になる、という言い方もできます。

---

# Part III：1次元で完全に解く

抽象論だけでは実感が湧きにくいので、区間 $(0,L)$ 上で $-\Delta_pu=c$（$c$：正の定数、両端固定 $u(0)=u(L)=0$）を実際に解きます。1次元では $\operatorname{div}$ も勾配も単なる $d/dx$ なので：

$$
-\frac{d}{dx}\left(|u'|^{p-2}u'\right) = c
$$

## 1. 1回積分する

$$
|u'|^{p-2}u' = -cx + C_1
$$

対称性（定数 $c$、対称な境界条件なので解は $x=L/2$ について対称になるはず）から、最大値を取る $x=L/2$ で $u'=0$ になります。$x=L/2$ を代入すると $0=-cL/2+C_1$、つまり $C_1=cL/2$：

$$
|u'|^{p-2}u' = c\left(\frac L2-x\right)
$$

## 2. $u'$ について解く

$c>0$ で $u$ が原点付近で増加すると仮定すると、$0\le x\le L/2$ の範囲で $u'>0$ なので $|u'|^{p-2}u'=(u')^{p-1}$：

$$
(u')^{p-1} = c\left(\frac L2-x\right) \quad\Longrightarrow\quad u' = c^{\frac1{p-1}}\left(\frac L2-x\right)^{\frac1{p-1}}
$$

## 3. もう1回積分する

$\beta:=\dfrac p{p-1}$（$p>1$ なら $\beta>1$）と置くと、$\dfrac1{p-1}=\beta-1$ なので：

$$
u'(x) = c^{\beta-1}\left(\frac L2-x\right)^{\beta-1}
$$

積分します：

$$
u(x) = -\frac{c^{\beta-1}}\beta\left(\frac L2-x\right)^\beta + C_2
$$

$u(0)=0$ から $C_2=\dfrac{c^{\beta-1}}\beta\left(\dfrac L2\right)^\beta$ が決まります：

$$
\boxed{u(x) = \frac{c^{\beta-1}}\beta\left[\left(\frac L2\right)^\beta-\left|\frac L2-x\right|^\beta\right],\qquad \beta=\frac p{p-1}}
$$

（$L/2\le x\le L$ は対称性 $u(x)=u(L-x)$ で決まります。絶対値を付けたのはこの対称性を1本の式にまとめるためです。）

## 4. 検算：$p=2$ で見慣れた形になるか

$p=2$ なら $\beta=2$：

$$
u(x) = \frac c2\left[\left(\frac L2\right)^2-\left(\frac L2-x\right)^2\right]
$$

$\left(\frac L2\right)^2-\left(\frac L2-x\right)^2$ は因数分解すると $\left(\frac L2-\left(\frac L2-x\right)\right)\left(\frac L2+\left(\frac L2-x\right)\right)=x(L-x)$ なので：

$$
u(x) = \frac c2\,x(L-x)
$$

これは $-u''=c$、$u(0)=u(L)=0$ の教科書通りの放物線解です。一致しました。

---

# Part IV：非線形性を実際の数値で確認する

Part IIIの解の形 $u_c(x)=\dfrac{c^{\beta-1}}\beta\left[\cdots\right]$ を見ると、$u_c$ は $c^{\beta-1}$ に比例しています。つまり、外力を $c\to\lambda c$ と $\lambda$ 倍にすると、解は $\lambda^{\beta-1}$ 倍になります。

**線形なら $\lambda$ 倍のはず**ですが、$\beta-1=\dfrac1{p-1}$ なので、これが $1$ に等しいのは $p=2$ のときだけです。具体的に $p=3$（$\beta=3/2$、$\beta-1=1/2$）で確認します：

- 外力 $c=1$ の解を $u_1$、外力 $c=1$ をもう一つ足した（つまり合計 $c=2$）解を $u_2$ とします。
- 線形なら $u_2 = u_1+u_1 = 2u_1$ となるはずです。
- しかし実際には $u_2 = 2^{\beta-1}u_1 = 2^{1/2}u_1 = \sqrt2\,u_1 \approx 1.414\,u_1$

$\sqrt2\ne2$ なので、**重ね合わせの原理が具体的な数値レベルで破れている**ことが確認できます。これが「非線形」の中身です（$p=2$ のときだけ $2^{\beta-1}=2^1=2$ となって、ちょうど線形の重ね合わせと一致します）。

---

# Part V：極限 $p\to1$、$p\to\infty$ で何が起こるか

## $p\to\infty$：$\infty$-ラプラシアン

$\Delta_pu=\operatorname{div}(|\nabla u|^{p-2}\nabla u)$ を積の微分で展開すると：

$$
\Delta_pu = |\nabla u|^{p-2}\Delta u + (p-2)|\nabla u|^{p-4}\big(\nabla^2u\,\nabla u\big)\cdot\nabla u
$$

（$\nabla^2u$ はヘシアン行列、$(\nabla^2u\,\nabla u)\cdot\nabla u=\sum_{i,j}\partial_i\partial_ju\,\partial_iu\,\partial_ju$）。方程式 $\Delta_pu=0$ の両辺を $(p-2)|\nabla u|^{p-4}$ で割ると：

$$
\frac{|\nabla u|^{2}}{p-2}\Delta u + \sum_{i,j}\partial_i\partial_ju\,\partial_iu\,\partial_ju = 0
$$

$p\to\infty$ の極限で第1項が消えるとみなすと、残るのは：

$$
\boxed{\Delta_\infty u := \sum_{i,j}\partial_i\partial_ju\,\partial_iu\,\partial_ju = 0}
$$

これが**$\infty$-ラプラシアン**です。$p$-ラプラシアンの族の「非線形性が極限まで強くなった」形で、最適Lipschitz拡張問題やゲーム理論（tug-of-war ゲーム）との関連で近年よく研究されています。

## $p\to1$：全変動（total variation）型

$$
\Delta_1u = \operatorname{div}\left(\frac{\nabla u}{|\nabla u|}\right)
$$

これは画像処理のノイズ除去（ROFモデル、全変動最小化）で使われる演算子で、レベルセット（$u=$一定の等高面）の平均曲率を測る量にもなっています。

---

# Part VI：一般の計量上の$p$-ラプラシアン（前回までとの接続）

前回までに導出した一般座標での発散公式

$$
\operatorname{div}_gV = \frac1{\sqrt{|g|}}\partial_i\big(\sqrt{|g|}V^i\big)
$$

に、ベクトル場として

$$
V^i := |\nabla u|_g^{p-2}g^{ij}\partial_ju,\qquad |\nabla u|_g^2 := g^{jk}\partial_ju\,\partial_ku
$$

（前回の「勾配の一般化」$(\operatorname{grad}u)^i=g^{ij}\partial_ju$ に、係数 $|\nabla u|_g^{p-2}$ を掛けただけ）を代入するだけで：

$$
\boxed{\Delta_gpu := \frac1{\sqrt{|g|}}\partial_i\left[\sqrt{|g|}\left(g^{jk}\partial_ju\,\partial_ku\right)^{\frac{p-2}2}g^{ij}\partial_ju\right]}
$$

前回導出した div の一般公式に、Part IIIで導いた「grad の $p$ 乗版」を代入しただけで、**曲がった空間上の $p$-ラプラシアンが自動的に得られる**、という点が重要です。計量が線形性を壊すわけではなく、非線形性は完全に $|\nabla u|_g^{p-2}$ という係数の側から来ている、ということがこの式からも見て取れます。

---

# Part VII：準線形・完全非線形という分類（用語整理）

PDEの非線形性には段階があります：

| 分類 | 特徴 | 例 |
|---|---|---|
| 線形 | 未知関数とその導関数について1次式 | $\Delta u=f$ |
| 準線形（quasilinear） | 最高階の導関数については1次だが、係数が低階の導関数（や $u$ 自身）に依存 | $\Delta_pu=f$（最高階の2階微分の係数 $\|\nabla u\|^{p-2}$ が1階微分 $\nabla u$ に依存） |
| 完全非線形（fully nonlinear） | 最高階の導関数についても非線形 | Monge–Ampère方程式 $\det(\nabla^2u)=f$ |

$p$-ラプラシアンは典型的な**準線形**方程式です。最高階の項（2階微分 $\partial_i\partial_ju$）は方程式の中に線形に現れますが、その「係数」の役割をしている $|\nabla u|^{p-2}$ が $u$ の1階微分に依存しているために、全体として非線形になります。

---

# Part VIII：応用分野（なぜこの演算子が重要視されるか）

- **非ニュートン流体**：power-law流体（応力とひずみ速度が非線形な関係を持つ流体）の定常流れは $p$-ラプラシアン型の方程式に従います。氷河の流動（Glenの流動則、$p\approx4/3$ 相当）もこの一種です。
- **非線形弾性・トーション問題**：円形でない断面を持つ棒のねじり問題は、$p\to\infty$ の極限で $\infty$-ラプラシアンと関係します。
- **画像処理**：全変動最小化（$p=1$ 付近）はエッジを保存したままノイズを除去する手法として広く使われています。
- **最適輸送・ゲーム理論**：$\infty$-ラプラシアンは、2人の交互選択によるランダムウォーク（tug-of-warゲーム）の期待値関数として現れることが知られています。

---

# まとめ：全体の位置づけ

```
標準ラプラシアン Δu（線形）
   Dirichletエネルギー E[u]=(1/2)∫|∇u|²dx の最小化
        │  |∇u|² → |∇u|^p に一般化
        ▼
p-エネルギー E_p[u]=(1/p)∫|∇u|^p dx
        │  第一変分（積の微分・部分積分・変分法の基本補題）
        ▼
p-ラプラシアン Δ_pu = div(|∇u|^{p-2}∇u)（準線形・非線形）
        │
        ├─ p=2 → 標準ラプラシアン（線形に戻る）
        ├─ p→∞ → ∞-ラプラシアン Δ_∞u=Σ∂_i∂_ju ∂_iu ∂_ju
        ├─ p→1 → 全変動型 div(∇u/|∇u|)
        │
        └─ 一般計量上：div_g の公式に |∇u|_g^{p-2}g^{ij}∂_ju を代入するだけ
                 → 計量が複雑でも非線形性の構造自体は変わらない
```

今回の一番のポイントは、**$p$-ラプラシアンは「係数が未知関数の微分に依存する」という一点だけで非線形になっている**ことと、**その非線形性は、変分原理（エネルギー最小化）というごく自然な発想から必然的に出てくる**ことでした。1次元の具体例で「重ね合わせが $\sqrt2$ 倍にしかならない」という数字を実際に見たことで、「非線形」が単なる言葉ではなく、具体的にどうずれるかまで確認できたと思います。
