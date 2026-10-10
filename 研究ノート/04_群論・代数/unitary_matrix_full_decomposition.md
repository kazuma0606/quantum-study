# ユニタリ行列の絶対値・位相分離 ―完全導出ノート―

> **作成** 2026-09-17　**更新** 2026-10-05
> 2×2 のユニタリ行列を、U† = U^{-1} という定義だけから、「位相 × 純粋な回転 × 位相」の積にまで分解する完全導出ノート。
> Part IX でグローバル位相を分離した ZYZ 分解（量子ゲートの基本形）に至る。

$U=\begin{pmatrix}a&b\\c&d\end{pmatrix}$ から出発し、$U^\dagger=U^{-1}$ という定義だけを使って、最終的に「位相（対角行列）× 純粋な回転 × 位相（対角行列）」という3つの単純な行列の積にまで分解する、一連の導出をまとめます。

---

# Part 0：出発点（$U^\dagger=U^{-1}$ から $a,b,c,d$ の関係を導く）

$U=\begin{pmatrix}a&b\\c&d\end{pmatrix}$、$U^\dagger=\begin{pmatrix}a^*&c^*\\b^*&d^*\end{pmatrix}$、$U^{-1}=\dfrac1{\det U}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$。

$\Delta:=\det U$ と置き、$U^\dagger=U^{-1}$ を成分ごとに比較すると：

$$
a^*=\frac d\Delta,\qquad c^*=-\frac b\Delta,\qquad b^*=-\frac c\Delta,\qquad d^*=\frac a\Delta
$$

これを整理すると：

$$
\boxed{d=a^*\Delta,\qquad b=-c^*\Delta}
$$

$(2,2)$式に$(1,1)$式を代入すると $a=d^*\Delta=(a^*\Delta)^*\Delta=a|\Delta|^2$ となり、$|\Delta|^2=1$、すなわち

$$
\boxed{|\Delta|=1}
$$

が要求されます。また $\Delta=ad-bc$ に $d=a^*\Delta,\ b=-c^*\Delta$ を代入すると $\Delta=\Delta(|a|^2+|c|^2)$ となり：

$$
\boxed{|a|^2+|c|^2=1}
$$

$|\Delta|=1$ なので、実数 $\phi$ を使って $\Delta=e^{i\phi}$ と書けます（絶対値1の複素数は必ず単位円上の点として偏角で表せる、という複素数の極形式の一般論）。

---

# Part I：絶対値と位相を分離する必要性

$a,c$ をそれぞれ単独で絶対値1の複素数（$a=e^{i\alpha}$、$c=e^{i\beta}$）と置くと、$|a|^2+|c|^2=1+1=2\ne1$ となり矛盾します。**$a$ と $c$ の絶対値は独立ではなく、互いに拘束し合っている**ため、絶対値の部分と位相の部分を明確に分けて扱う必要があります。

---

# Part II：$a,c$ を絶対値・位相に分解する

## 1. 極形式で書く

$$
a=r_a e^{i\alpha},\qquad c=r_c e^{i\beta}\qquad(r_a,r_c\ge0,\ \alpha,\beta\in\mathbb R)
$$

## 2. 拘束条件を絶対値に適用する

$$
r_a^2+r_c^2=1
$$

## 3. 単位円の弧として $\theta$ でまとめる

$r_a,r_c\ge0$ かつ $r_a^2+r_c^2=1$ は、$(r_a,r_c)$ が単位円の第1象限の弧上にあることを意味し、ただ1つの角度 $\theta\in[0,\pi/2]$ を用いて

$$
\boxed{r_a=\cos\theta,\qquad r_c=\sin\theta}
$$

と表せます（$\cos^2\theta+\sin^2\theta=1$ が自動的に満たされる）。

## 4. まとめ

$$
\boxed{a=\cos\theta\,e^{i\alpha},\qquad c=\sin\theta\,e^{i\beta}}
$$

---

# Part III：$b,d$ を求める（Part 0の関係式に代入）

$$
a^*=\cos\theta\,e^{-i\alpha},\qquad c^*=\sin\theta\,e^{-i\beta}
$$

指数法則 $e^Xe^Y=e^{X+Y}$ を使って：

$$
d=a^*\Delta=\cos\theta\,e^{-i\alpha}\cdot e^{i\phi}=\boxed{\cos\theta\,e^{i(\phi-\alpha)}}
$$
$$
b=-c^*\Delta=-\sin\theta\,e^{-i\beta}\cdot e^{i\phi}=\boxed{-\sin\theta\,e^{i(\phi-\beta)}}
$$

## まとめ：位相分離された $U$

$$
\boxed{
U=\begin{pmatrix}
\cos\theta\,e^{i\alpha} & -\sin\theta\,e^{i(\phi-\beta)}\\[4pt]
\sin\theta\,e^{i\beta} & \cos\theta\,e^{i(\phi-\alpha)}
\end{pmatrix}
}
$$

自由パラメータは $\theta\in[0,\pi/2]$、$\alpha,\beta,\phi\in\mathbb R$ の実数4個で、$U(2)$ の次元（$n^2=4$）とぴったり一致します。

---

# Part IV：検算

## 1. $U^\dagger U=I$ を直接確認

$$
U^\dagger=\begin{pmatrix}\cos\theta\,e^{-i\alpha}&\sin\theta\,e^{-i\beta}\\-\sin\theta\,e^{-i(\phi-\beta)}&\cos\theta\,e^{-i(\phi-\alpha)}\end{pmatrix}
$$

**(1,1)**：$\cos^2\theta+\sin^2\theta=1$ ✓
**(1,2)**：$-\cos\theta\sin\theta\,e^{i(\phi-\alpha-\beta)}+\sin\theta\cos\theta\,e^{i(\phi-\alpha-\beta)}=0$ ✓
**(2,2)**：$\sin^2\theta+\cos^2\theta=1$ ✓（(2,1)も同様に0）

## 2. $\det U=e^{i\phi}$ の確認

$$
\det U=\cos^2\theta\,e^{i\phi}+\sin^2\theta\,e^{i\phi}=e^{i\phi}\ \checkmark
$$

---

# Part V：ゲージ固定（量子ゲート $U3$ との対応）

$\alpha=0$（全体位相の基準）、$\theta\to\theta/2$、$\beta=:\varphi$、$\phi-\beta=:\lambda$ と置き換えると：

$$
U=\begin{pmatrix}\cos(\theta/2)&-e^{i\lambda}\sin(\theta/2)\\e^{i\varphi}\sin(\theta/2)&e^{i(\varphi+\lambda)}\cos(\theta/2)\end{pmatrix}
$$

これは量子コンピュータの標準的な単一量子ビットゲート $U3(\theta,\varphi,\lambda)$ の定義と完全に一致します。

---

# Part VI：$\cos\theta,\sin\theta$ の部分（回転）と位相の部分を、行列の積として完全に分離する

ここがノートの本題です。Part IIIの結果を、対角行列 $\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)})$ で右から割ってみます（＝逆行列を掛ける）。

$$
U\cdot\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)})^{-1} =: A
$$

各成分を計算すると：

$$
A_{11}=\cos\theta\,e^{i\alpha}\cdot e^{-i\alpha}=\cos\theta
$$
$$
A_{12}=-\sin\theta\,e^{i(\phi-\beta)}\cdot e^{-i(\phi-\beta)}=-\sin\theta
$$
$$
A_{21}=\sin\theta\,e^{i\beta}\cdot e^{-i\alpha}=\sin\theta\,e^{i(\beta-\alpha)}
$$
$$
A_{22}=\cos\theta\,e^{i(\phi-\alpha)}\cdot e^{-i(\phi-\beta)}=\cos\theta\,e^{i(\beta-\alpha)}
$$

したがって：

$$
A=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta\,e^{i(\beta-\alpha)}&\cos\theta\,e^{i(\beta-\alpha)}\end{pmatrix}
$$

**1回目の試み（$A$ を回転行列 $R(\theta)$ そのものと考えてしまう）が間違っていた理由**：$A$ の2行目には $e^{i(\beta-\alpha)}$ という位相が残っており、$A$ 自体はまだ「純粋な回転」ではありません。この位相を見落として $U=R(\theta)\cdot\operatorname{diag}(e^{i\alpha},e^{-i\beta})$ のような形にしてしまうと、$U^\dagger U=I$ を満たさず、矛盾が生じます。

## 1. $A$ の中の位相をさらに外に出す

$A$ の**2行目全体に共通して** $e^{i(\beta-\alpha)}$ がかかっていることに注目します。$\Delta:=\beta-\alpha$ と置くと、「2行目だけを位相倍する」操作は、左から対角行列 $\operatorname{diag}(1,e^{i\Delta})$ を掛けることに対応します：

$$
\operatorname{diag}(1,e^{i\Delta})\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}
=\begin{pmatrix}\cos\theta&-\sin\theta\\e^{i\Delta}\sin\theta&e^{i\Delta}\cos\theta\end{pmatrix}=A
$$

つまり：

$$
\boxed{A=\operatorname{diag}(1,\,e^{i(\beta-\alpha)})\cdot R(\theta)},\qquad R(\theta):=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}
$$

$R(\theta)$ は複素数を一切含まない、**純粋な（実数の）回転行列**です。

## 2. 全体をまとめる

$U=A\cdot\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)})$ だったので：

$$
\boxed{
U=\underbrace{\operatorname{diag}(1,\,e^{i(\beta-\alpha)})}_{\text{位相（左）}}\cdot\underbrace{R(\theta)}_{\text{純粋な回転（実数）}}\cdot\underbrace{\operatorname{diag}(e^{i\alpha},\,e^{i(\phi-\beta)})}_{\text{位相（右）}}
}
$$

## 3. 検算（元の $U$ に一致するか）

まず $R(\theta)\cdot\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)})$：

$$
\begin{pmatrix}\cos\theta\,e^{i\alpha}&-\sin\theta\,e^{i(\phi-\beta)}\\\sin\theta\,e^{i\alpha}&\cos\theta\,e^{i(\phi-\beta)}\end{pmatrix}
$$

これに左から $\operatorname{diag}(1,e^{i\Delta})$（$\Delta=\beta-\alpha$）を掛けます（1行目そのまま、2行目だけ $e^{i\Delta}$ 倍）：

$$
\begin{pmatrix}\cos\theta\,e^{i\alpha}&-\sin\theta\,e^{i(\phi-\beta)}\\\sin\theta\,e^{i(\Delta+\alpha)}&\cos\theta\,e^{i(\Delta+\phi-\beta)}\end{pmatrix}
$$

$\Delta+\alpha=\beta$、$\Delta+\phi-\beta=\phi-\alpha$ なので：

$$
\begin{pmatrix}\cos\theta\,e^{i\alpha}&-\sin\theta\,e^{i(\phi-\beta)}\\\sin\theta\,e^{i\beta}&\cos\theta\,e^{i(\phi-\alpha)}\end{pmatrix}
$$

Part IIIで導出した $U$ と完全に一致しました。

---

# Part VII：この分解が意味すること（量子計算との接続）

$$
\boxed{U(2)\text{の任意の行列}\ =\ \text{位相（対角）}\ \times\ \text{純粋な回転}\ \times\ \text{位相（対角）}}
$$

$\cos\theta,\sin\theta$（絶対値・回転成分）と、$\alpha,\beta,\phi$（位相成分）が、行列の積として完全に分離されました。真ん中の $R(\theta)$ には複素数が一切残っておらず、両側の対角行列だけが位相を担っています。

これは量子コンピュータで単一量子ビットの任意のゲートを実装する際によく使われる**$Z$-$Y$-$Z$分解**（対角な位相回転ゲート $R_Z$ で挟んで、実数の回転 $R_Y$ を真ん中に置く分解）と本質的に同じ構造です。対角行列 $\operatorname{diag}(1,e^{i\Delta})$ は、全体位相を1つ括り出せば $R_Z(\Delta)=\operatorname{diag}(e^{-i\Delta/2},e^{i\Delta/2})$ というゲートと同一視できます。

**結論**：$U(2)$ の任意の行列は、「位相を回す操作（$Z$軸まわりの回転）2つ」と「実数の回転（$Y$軸まわりの回転）1つ」、合計3つの単純な操作の積に分解できます。$U3$ ゲートのパラメータ $\theta,\varphi,\lambda$ は、まさにこの3つの回転の回転角に対応しています。

---

# Part VIII：パウリ行列と「行列を指数に入れる」ことの意味

Part IXで使う $R_z,R_y$ の定義には、$\exp(-i\frac\theta2\sigma)$ という「行列を指数の肩に乗せた」表記が出てきます。ここで一度立ち止まって、パウリ行列とは何か、そしてこの指数表記が何を意味しているのかを確認します。

## 1. パウリ行列とは

パウリ行列は、次の3つの $2\times2$ 行列です：

$$
\sigma_x=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
\sigma_y=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\qquad
\sigma_z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}
$$

これらは、量子力学におけるスピン$\frac12$（あるいは量子ビット）の、$x,y,z$ 各方向の「測定値」を表す演算子です。共通する重要な性質：

$$
\boxed{\sigma_x^\dagger=\sigma_x,\quad\sigma_y^\dagger=\sigma_y,\quad\sigma_z^\dagger=\sigma_z}\qquad\text{（すべてエルミート）}
$$

$$
\boxed{\sigma_x^2=\sigma_y^2=\sigma_z^2=I}\qquad\text{（2乗すると単位行列に戻る）}
$$

**2番目の性質（2乗すると $I$）が、今回の指数計算の鍵**になります。実際に確認します：

$$
\sigma_z^2=\begin{pmatrix}1&0\\0&-1\end{pmatrix}\begin{pmatrix}1&0\\0&-1\end{pmatrix}=\begin{pmatrix}1&0\\0&1\end{pmatrix}=I
$$

$$
\sigma_y^2=\begin{pmatrix}0&-i\\i&0\end{pmatrix}\begin{pmatrix}0&-i\\i&0\end{pmatrix}=\begin{pmatrix}(-i)(i)&0\\0&(i)(-i)\end{pmatrix}=\begin{pmatrix}1&0\\0&1\end{pmatrix}=I
$$

（$(-i)(i)=-i^2=1$、$(i)(-i)=-i^2=1$ を使用。）

## 2. 「行列を指数に入れる」とは何か（行列指数関数の定義）

以前、時間発展演算子 $e^{-i\hat Ht/\hbar}$ を扱ったときと**まったく同じ定義**を使います。指数関数 $e^x$ のテイラー展開

$$
e^x=\sum_{n=0}^\infty\frac{x^n}{n!}=1+x+\frac{x^2}{2!}+\frac{x^3}{3!}+\cdots
$$

の $x$ に、そのまま行列を代入したものを**行列指数関数**と呼びます：

$$
e^A:=\sum_{n=0}^\infty\frac{A^n}{n!}=I+A+\frac{A^2}{2!}+\frac{A^3}{3!}+\cdots
$$

（$A^0=I$、$A^n$ は行列の積を$n$回繰り返すこと。）これは天下り的な発明ではなく、**「指数関数とは何か」という定義そのもの（テイラー展開）を、数の代わりに行列に適用しただけ**です。

ただし、この代入が許される理由（収束）と、この定義を選ぶ理由（時間発展の方程式から決まる）は、本節では述べていません。[行列の指数関数と交換子のノート](matrix_exponential_commutator_bch_trotter.md#p0)の Part 0 にまとめています（収束、$\cos A,\sin A$ とオイラーの公式、エルミート行列 $H$ の $e^{-iHt}$ がユニタリになる理由）。

## 3. パウリ行列の指数関数を具体的に計算する（$\sigma^2=I$ を使う）

$A=-i\dfrac\theta2\sigma$（$\sigma$ はパウリ行列のどれか1つ）としてテイラー展開します。$\sigma^2=I$ を使うと、$A$ のべき乗は驚くほど単純になります：

$$
A^0=I,\quad A^1=-i\frac\theta2\sigma,\quad A^2=\left(-i\frac\theta2\right)^2\sigma^2=-\frac{\theta^2}4I,\quad A^3=A^2\cdot A=-\frac{\theta^2}4I\cdot\left(-i\frac\theta2\sigma\right)=i\frac{\theta^3}8\sigma,\ \dots
$$

**偶数乗は $I$ の実数倍、奇数乗は $\sigma$ の（虚数を含む）倍数**という、きれいな交互パターンになっていることが分かります。これを一般化すると：

$$
A^{2k}=(-1)^k\left(\frac\theta2\right)^{2k}I,\qquad A^{2k+1}=-i(-1)^k\left(\frac\theta2\right)^{2k+1}\sigma
$$

これをテイラー展開に戻し、偶数項と奇数項に分けて集めます：

$$
e^A=\underbrace{\sum_{k=0}^\infty\frac{A^{2k}}{(2k)!}}_{\text{偶数項}}+\underbrace{\sum_{k=0}^\infty\frac{A^{2k+1}}{(2k+1)!}}_{\text{奇数項}}
$$

**偶数項**：

$$
\sum_{k=0}^\infty\frac{(-1)^k(\theta/2)^{2k}}{(2k)!}I = \left[\sum_{k=0}^\infty\frac{(-1)^k(\theta/2)^{2k}}{(2k)!}\right]I = \cos(\theta/2)\,I
$$

（角括弧の中身は、まさに $\cos x$ のテイラー展開 $\cos x=\sum_k\frac{(-1)^kx^{2k}}{(2k)!}$ そのもの、$x=\theta/2$ の場合です。）

**奇数項**：

$$
\sum_{k=0}^\infty\frac{-i(-1)^k(\theta/2)^{2k+1}}{(2k+1)!}\sigma = -i\left[\sum_{k=0}^\infty\frac{(-1)^k(\theta/2)^{2k+1}}{(2k+1)!}\right]\sigma = -i\sin(\theta/2)\,\sigma
$$

（角括弧の中身は $\sin x=\sum_k\frac{(-1)^kx^{2k+1}}{(2k+1)!}$ のテイラー展開、$x=\theta/2$ の場合です。）

## 4. まとめの公式

$$
\boxed{\exp\!\left(-i\frac\theta2\sigma\right) = \cos(\theta/2)\,I - i\sin(\theta/2)\,\sigma}
$$

**これが「行列を指数に入れる」ことの正体**です。$e^{i\theta}=\cos\theta+i\sin\theta$（オイラーの公式）の行列版、と考えると分かりやすいです。オイラーの公式は「$i$」という**2乗すると$-1$になる特別な数**を使うことで、テイラー展開が $\cos,\sin$ に分解できたのでした。パウリ行列は「2乗すると$I$になる特別な行列」なので、まったく同じロジックで $\cos,\sin$ に分解できる、という共通の仕組みです。

## 5. $\sigma_z,\sigma_y$ に代入して、$R_z,R_y$ の定義を導く

**$\sigma=\sigma_z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}$ の場合**：

$$
\exp\!\left(-i\frac\theta2\sigma_z\right) = \cos(\theta/2)\begin{pmatrix}1&0\\0&1\end{pmatrix} - i\sin(\theta/2)\begin{pmatrix}1&0\\0&-1\end{pmatrix} = \begin{pmatrix}\cos(\theta/2)-i\sin(\theta/2)&0\\0&\cos(\theta/2)+i\sin(\theta/2)\end{pmatrix}
$$

オイラーの公式を使うと $\cos(\theta/2)\mp i\sin(\theta/2)=e^{\mp i\theta/2}$ なので：

$$
\boxed{R_z(\theta):=\exp\!\left(-i\frac\theta2\sigma_z\right) = \begin{pmatrix}e^{-i\theta/2}&0\\0&e^{i\theta/2}\end{pmatrix}}
$$

これがPart IXで使う $R_z(\theta)$ の定義そのものです。

**$\sigma=\sigma_y=\begin{pmatrix}0&-i\\i&0\end{pmatrix}$ の場合**：

$$
\exp\!\left(-i\frac\theta2\sigma_y\right) = \cos(\theta/2)\begin{pmatrix}1&0\\0&1\end{pmatrix} - i\sin(\theta/2)\begin{pmatrix}0&-i\\i&0\end{pmatrix}
$$

非対角成分を計算します：$(1,2)$成分は $-i\sin(\theta/2)\times(-i)=i^2\sin(\theta/2)\times(-1)\cdots$ 丁寧に：$-i\times(-i)=i^2=-1$ なので $(1,2)$成分は $-\sin(\theta/2)$。$(2,1)$成分は $-i\times i=-i^2=1$ なので $\sin(\theta/2)$。

$$
\boxed{R_y(\theta):=\exp\!\left(-i\frac\theta2\sigma_y\right) = \begin{pmatrix}\cos(\theta/2)&-\sin(\theta/2)\\\sin(\theta/2)&\cos(\theta/2)\end{pmatrix}}
$$

これがPart IXで使う、**成分がすべて実数の回転行列**です。ここまでの $A$ の計算で出てきた $R(\theta)$ が $\sigma_y$ 由来だったのは偶然ではなく、「非対角成分の符号が反対で、対角成分が等しい、実数の回転行列」という形が、パウリ行列のうち $\sigma_y$ を指数に入れたときにちょうど出てくる形だから、ということがここで分かります。

## 6. 物理的な意味（簡単に）

$\exp(-i\frac\theta2\sigma)$ という演算子は、Blochの球（量子ビットの状態を球面上の点として表す図）上で、**$\sigma$ が指す軸のまわりに、状態を角度 $\theta$ だけ回転させる**という操作に対応します。$\sigma_z,\sigma_y,\sigma_x$ はそれぞれ $z$軸、$y$軸、$x$軸に対応する「回転の生成子（generator）」と呼ばれ、指数関数に入れることで初めて「実際の回転」という操作になります。これは、古典力学で角運動量 $L_z$ が $z$軸まわりの回転を生成する、という話の量子版でもあります。

---

# Part IX：グローバル位相を分離する（ZYZ分解）

量子計算の教科書でよく見る形は、Part VIの分解からさらに一歩進んで、**2つの対角行列からスカラーの全体位相（グローバル位相）を1つに集約**したものです。ここまでの結果

$$
U=\operatorname{diag}(1,e^{i\Delta})\cdot R(\theta)\cdot\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)}),\qquad \Delta=\beta-\alpha
$$

を出発点に、この最後の変形を行います。

## 1. 対角行列からスカラー位相を括り出す方法

一般に、対角行列 $\operatorname{diag}(e^{i\gamma_1},e^{i\gamma_2})$ は、2つの指数の**平均**をスカラーとして括り出せます：

$$
\operatorname{diag}(e^{i\gamma_1},e^{i\gamma_2}) = e^{i\frac{\gamma_1+\gamma_2}2}\cdot\operatorname{diag}\!\left(e^{-i\frac{\gamma_2-\gamma_1}2},\,e^{i\frac{\gamma_2-\gamma_1}2}\right) = e^{i\frac{\gamma_1+\gamma_2}2}\cdot R_z(\gamma_2-\gamma_1)
$$

ここで $R_z(\theta):=\operatorname{diag}(e^{-i\theta/2},e^{i\theta/2})$（$Z$軸まわりの回転ゲート、パウリ行列 $\sigma_z$ を使うと $R_z(\theta)=\exp(-i\frac\theta2\sigma_z)$）です。

## 2. 左右の対角行列にそれぞれ適用する

**左側** $\operatorname{diag}(1,e^{i\Delta})$（$\gamma_1=0,\ \gamma_2=\Delta$）：

$$
\operatorname{diag}(1,e^{i\Delta}) = e^{i\Delta/2}\cdot R_z(\Delta)
$$

**右側** $\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)})$（$\gamma_1=\alpha,\ \gamma_2=\phi-\beta$）：

$$
\operatorname{diag}(e^{i\alpha},e^{i(\phi-\beta)}) = e^{i\frac{\alpha+\phi-\beta}2}\cdot R_z\big(\phi-\beta-\alpha\big)
$$

## 3. 組み立てて位相をまとめる

$$
U = e^{i\Delta/2}R_z(\Delta)\cdot R(\theta)\cdot e^{i\frac{\alpha+\phi-\beta}2}R_z(\phi-\beta-\alpha)
$$

2つのスカラー位相の指数を足すと：

$$
\frac\Delta2+\frac{\alpha+\phi-\beta}2 = \frac{(\beta-\alpha)+(\alpha+\phi-\beta)}2 = \frac\phi2
$$

**きれいに $\phi/2$ だけが残ります。** したがって：

$$
\boxed{U = e^{i\phi/2}\cdot R_z(\beta-\alpha)\cdot R(\theta)\cdot R_z(\phi-\beta-\alpha)}
$$

## 4. $R(\theta)$ が自然に $R_y$ になっていることの確認

$R(\theta)=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$ はすべて実数の成分を持ちます。これはパウリ行列 $\sigma_y=\begin{pmatrix}0&-i\\i&0\end{pmatrix}$ を使った

$$
R_y(\chi):=\exp\!\left(-i\frac\chi2\sigma_y\right)=\begin{pmatrix}\cos(\chi/2)&-\sin(\chi/2)\\\sin(\chi/2)&\cos(\chi/2)\end{pmatrix}
$$

と、$\chi=2\theta$ とすれば完全に一致します。つまりこの分解は自然に**$Z$-$Y$-$Z$分解**になっています：

$$
\boxed{U = e^{i\phi/2}\cdot R_z(\beta-\alpha)\cdot R_y(2\theta)\cdot R_z(\phi-\beta-\alpha)}
$$

ゲージ固定（$\alpha=0,\ \theta\to\theta/2,\ \beta=\varphi,\ \phi-\beta=\lambda$）を代入すると：

$$
U = e^{i(\varphi+\lambda)/2}\,R_z(\varphi)\,R_y(\theta)\,R_z(\lambda)
$$

これが、量子計算の教科書で標準的に書かれる「全体位相付きの$U3$ゲートのZYZ分解」の式です。

## 5. $Z$-$X$-$Z$分解との関係（共役変換による橋渡し）

文献によっては、真ん中の実数回転を $\sigma_x$ を使った $R_x(\chi)=\exp(-i\frac\chi2\sigma_x)=\begin{pmatrix}\cos(\chi/2)&-i\sin(\chi/2)\\-i\sin(\chi/2)&\cos(\chi/2)\end{pmatrix}$ で表す「$Z$-$X$-$Z$分解」

$$
U=e^{i\alpha}R_z(\beta)R_x(\gamma)R_z(\delta)
$$

が使われることもあります。$R_x$ は非対角成分に虚数 $-i\sin(\chi/2)$ を持つ点で、今回導出した実数の $R(\theta)$（$R_y$型）とは異なる行列です。

**「軸を変えただけ」というのは直感としては正しいのですが、これは数式としてきちんと橋渡しできます。** $R_z$ による共役変換（$R_z(\phi)(\cdot)R_z(-\phi)$）が、パウリ行列を $z$軸まわりに回転させる、という一般公式から出発します：

$$
\boxed{R_z(\phi)\,\sigma_x\,R_z(-\phi) = \sigma_x\cos\phi+\sigma_y\sin\phi}
$$

（$\sigma_x,\sigma_y$ を「$xy$平面上のベクトル」のように扱ったときの、角度 $\phi$ の回転公式です。）これを行列指数の中に代入します。一般に $R_z(\phi)e^{A}R_z(-\phi)=e^{R_z(\phi)AR_z(-\phi)}$（相似変換は指数関数の中に丸ごと通せる、というテイラー展開から従う性質：$R_z(\phi)A^nR_z(-\phi)=(R_z(\phi)AR_z(-\phi))^n$ を使えば、各項がそのまま対応することが分かります）が成り立つので：

$$
R_z(\phi)R_x(\theta)R_z(-\phi) = R_z(\phi)\exp\!\left(-\frac{i\theta}2\sigma_x\right)R_z(-\phi) = \exp\!\left(-\frac{i\theta}2\big[R_z(\phi)\sigma_xR_z(-\phi)\big]\right)
$$

$$
= \exp\!\left(-\frac{i\theta}2(\sigma_x\cos\phi+\sigma_y\sin\phi)\right)
$$

ここで $\phi=\pi/2$（$\cos\phi=0,\ \sin\phi=1$）を代入すると：

$$
\boxed{R_z(\pi/2)\,R_x(\theta)\,R_z(-\pi/2) = \exp\!\left(-\frac{i\theta}2\sigma_y\right) = R_y(\theta)}
$$

**$R_x$ と $R_y$ は同じ行列ではありませんが、$z$軸まわりにもう一段回転をかけて挟む（共役を取る）ことで、完全に一致させられます。** つまり $Z$-$Y$-$Z$分解の真ん中の $R_y(\theta)$ を、この関係式で $R_x$ に置き換えると：

$$
R_y(\theta) = R_z(\pi/2)R_x(\theta)R_z(-\pi/2)
$$

を今回の $U=e^{i\phi/2}R_z(\beta-\alpha)R_y(2\theta)R_z(\phi-\beta-\alpha)$ に代入すれば、$R_z$ が4つ並ぶ式になり、隣り合う $R_z$ 同士をまとめ直す（$R_z$ は同じ軸まわりの回転なので、角度を足すだけで合成できる：$R_z(\phi_1)R_z(\phi_2)=R_z(\phi_1+\phi_2)$）ことで、$Z$-$X$-$Z$分解の形に書き換えられます。

**結論**：$Z$-$Y$-$Z$分解と$Z$-$X$-$Z$分解は「単に軸を変えただけ」ではなく、「**同じ$SU(2)$の元を、異なる生成子の組み合わせでパラメータ化しているが、その2つの表示は$R_z$による共役変換という具体的な数式で結ばれている**」というのが、より正確な理解です。

---

# 全体の流れの図解

```
U = (a  b; c  d),  U†=U⁻¹ から出発
        │
        ▼
d=a*Δ, b=-c*Δ, |Δ|=1 (Δ=e^{iφ}), |a|²+|c|²=1
        │  a,c を絶対値・位相に分解
        ▼
a=cosθ e^{iα}, c=sinθ e^{iβ}
        │  代入
        ▼
U = (cosθe^{iα}   -sinθe^{i(φ-β)} ;
     sinθe^{iβ}    cosθe^{i(φ-α)})
        │  ゲージ固定 α=0, θ→θ/2, β=φ, φ-β=λ
        ▼
量子ゲート U3(θ,φ,λ) と一致
        │
        │  右から diag(e^{iα}, e^{i(φ-β)})⁻¹ を掛ける
        ▼
A = (cosθ  -sinθ ; sinθe^{i(β-α)}  cosθe^{i(β-α)})
        │  2行目の共通位相 e^{i(β-α)} をさらに左から括り出す
        ▼
U = diag(1, e^{i(β-α)}) · R(θ) · diag(e^{iα}, e^{i(φ-β)})
        │  各対角行列から「平均位相」をスカラーとして括り出す
        │  diag(e^{iγ1},e^{iγ2}) = e^{i(γ1+γ2)/2}·R_z(γ2-γ1)
        ▼
2つのスカラー位相 Δ/2 と (α+φ-β)/2 を足すと、ちょうど φ/2 に集約
        ▼
U = e^{iφ/2} · R_z(β-α) · R_y(2θ) · R_z(φ-β-α)
        │
        ▼
量子計算の標準的な「全体位相付きZYZ分解」と一致
（Z-X-Z分解は、真ん中の回転軸をYからXに変えた、同等に正しい別表現）
```
