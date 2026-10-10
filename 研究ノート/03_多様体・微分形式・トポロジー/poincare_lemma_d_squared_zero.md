# ポアンカレの補題 $d^2=0$ ―丁寧な解説―

> **作成** 2026-10-01　**更新** 2026-10-03
> ポアンカレの補題 d²=0 が、普通の「2階微分がゼロ」とは違う主張であることを、具体的な計算で1ステップずつ確かめるノート。

「$d^2=0$」が、普通の意味での「2階微分がゼロ」とはまったく違う主張であることを、最初から具体的な計算で確認しながら理解します。急がず、1ステップずつ進みます。

---

# Part 0：この話の核心を先に一言で

$$
\boxed{
\begin{aligned}
&\text{普通の2階微分}\ f''(x)\ \text{：0-形式（関数）を、また0-形式（関数）に変換する操作。値は一般に0でない}\\
&\text{外微分を2回}\ d(df)\ \text{：0-形式を1-形式に、さらに1-形式を2-形式に変換する、}\textbf{別種の操作}\text{。こちらは必ず0になる}
\end{aligned}
}
$$

「2回微分する」という言葉は同じでも、**やっている操作の種類がまったく違います**。$f''(x)$は「同じ種類の対象（関数）から同じ種類の対象（関数）」への変換なので、何回繰り返しても一般にはゼロになりません。一方$d$は「0-形式→1-形式→2-形式」と、**適用するたびに対象の種類が変わっていく**操作です。この「種類が変わる」という性質が、$d^2=0$の正体に直結しています。以下、具体的に見ていきます。

---

# Part I：$df$ の意味を確認する（復習）

関数 $f(x,y,z)$（＝0-形式）に対して：

$$
df := \partial_xf\,dx+\partial_yf\,dy+\partial_zf\,dz
$$

これは以前扱った**全微分**と同じものです。$dx,dy,dz$を「小さい数」ではなく、「**ある方向ベクトル$\mathbf v=(v_x,v_y,v_z)$を受け取って、$df(\mathbf v)=(\partial_xf)v_x+(\partial_yf)v_y+(\partial_zf)v_z$という数を返す道具**」だと思うと、この先の計算がイメージしやすくなります。

**具体例**：$f(x,y,z)=x^2y+yz$ とします。

$$
\partial_xf = 2xy,\qquad \partial_yf=x^2+z,\qquad \partial_zf=y
$$

$$
df = 2xy\,dx+(x^2+z)\,dy+y\,dz
$$

この具体例を、この先ずっと使い続けます。

---

# Part II：wedge積 $dx\wedge dy$ とは何か

## 1. なぜ新しい「積」が必要なのか

$df$は1-形式でした。この$df$に、もう一度$d$を作用させたい（$d(df)$を計算したい）のですが、$df$の中には$dx,dy,dz$という「方向を受け取る道具」がすでに含まれています。これをもう一段微分すると、「**2つの方向を同時に受け取る道具**」が必要になります。これが2-形式であり、その基本部品が $dx\wedge dy$ のようなwedge積です。

## 2. wedge積の定義（反対称性）

$$
\boxed{dx\wedge dy = -dy\wedge dx}\qquad\text{（順番を入れ替えると符号が反転する）}
$$

$$
\boxed{dx\wedge dx = 0}\qquad\text{（同じものを2つ掛けると自動的にゼロ）}
$$

**この2つの規則だけ**を武器に、この先の計算をすべて進めます。難しい理論は今は不要で、「$dx\wedge dy$は$-dy\wedge dx$と書き換えられる」「同じ文字が2つ並んだらゼロ」という、単なる**書き換えのルール**として扱えば十分です。

---

# Part III：1-形式に $d$ を作用させる（$d\omega$の計算方法）

$\omega = P\,dx+Q\,dy+R\,dz$（$P,Q,R$は関数）という1-形式があったとき、$d\omega$の計算方法を確認します。**各項ごとに、係数の関数を$d$で1-形式にしてから、元の$dx$（や$dy,dz$）とwedge積を取る**、というのがルールです：

$$
d\omega = dP\wedge dx + dQ\wedge dy + dR\wedge dz
$$

（このルールは「積の微分公式」の外微分版で、$d(f\,dx)=df\wedge dx$という規則から来ています。）

具体的に、$dP=\partial_xP\,dx+\partial_yP\,dy+\partial_zP\,dz$ なので：

$$
dP\wedge dx = \partial_xP(dx\wedge dx)+\partial_yP(dy\wedge dx)+\partial_zP(dz\wedge dx) = \partial_yP(dy\wedge dx)+\partial_zP(dz\wedge dx)
$$

（$dx\wedge dx=0$の項は自動的に消えます。）$Q,R$についても同様に計算し、最終的に $dx\wedge dy,\ dy\wedge dz,\ dz\wedge dx$ の係数ごとにまとめると：

$$
d\omega = (\partial_xQ-\partial_yP)\,dx\wedge dy+(\partial_yR-\partial_zQ)\,dy\wedge dz+(\partial_zP-\partial_xR)\,dz\wedge dx
$$

（この係数が、以前確認した$\operatorname{rot}(P,Q,R)$の成分と一致することは、前回のノートで確認済みです。）

---

# Part IV：$d(df)$ を最初から最後まで、具体的な数値関数で計算する

いよいよ本題です。Part Iの具体例 $f=x^2y+yz$（$df=2xy\,dx+(x^2+z)\,dy+y\,dz$）を使って、$d(df)$を**一切省略せず**計算します。$P=2xy,\ Q=x^2+z,\ R=y$として、Part IIIのルールをそのまま適用します。

## 1. $dP\wedge dx$ の計算

$$
dP = \partial_x(2xy)\,dx+\partial_y(2xy)\,dy+\partial_z(2xy)\,dz = 2y\,dx+2x\,dy+0\,dz
$$

$$
dP\wedge dx = 2y(dx\wedge dx)+2x(dy\wedge dx)+0 = 0+2x(-dx\wedge dy)+0 = -2x\,dx\wedge dy
$$

## 2. $dQ\wedge dy$ の計算

$$
dQ = \partial_x(x^2+z)\,dx+\partial_y(x^2+z)\,dy+\partial_z(x^2+z)\,dz = 2x\,dx+0\,dy+1\,dz
$$

$$
dQ\wedge dy = 2x(dx\wedge dy)+0+1(dz\wedge dy) = 2x\,dx\wedge dy - dy\wedge dz
$$

（$dz\wedge dy=-dy\wedge dz$を使用。）

## 3. $dR\wedge dz$ の計算

$$
dR = \partial_x(y)\,dx+\partial_y(y)\,dy+\partial_z(y)\,dz = 0\,dx+1\,dy+0\,dz
$$

$$
dR\wedge dz = 0+1(dy\wedge dz)+0 = dy\wedge dz
$$

## 4. 3つを全部足す

$$
d(df) = \underbrace{-2x\,dx\wedge dy}_{\text{①}} + \underbrace{\big(2x\,dx\wedge dy-dy\wedge dz\big)}_{\text{②}} + \underbrace{dy\wedge dz}_{\text{③}}
$$

**$dx\wedge dy$の係数**：①の$-2x$ と ②の$+2x$ → **$-2x+2x=0$**

**$dy\wedge dz$の係数**：②の$-1$ と ③の$+1$ → **$-1+1=0$**

$$
\boxed{d(df) = 0}
$$

**実際に、$f_{xy}$のような記号のまま計算しなくても、具体的な数値混じりの関数で、項が1つずつぴったり打ち消し合うのが見えたと思います。** これが偶然ではないことを、次のPartで確認します。

---

# Part V：なぜ「どんな関数$f$でも」必ずゼロになるのか（一般証明）

Part IVは1つの具体例でしたが、**任意の$f$で必ずゼロになる**ことを、一般的に証明します。ここが今回の核心です。

## 1. $d(df)$の一般形

$f$を一般の関数として、Part I〜IIIと同じ手順を記号のまま実行すると（Part IVでやったことを、具体的な数値の代わりに一般の$f$で繰り返すだけです）：

$$
d(df) = (\partial_x\partial_yf-\partial_y\partial_xf)\,dx\wedge dy+(\partial_y\partial_zf-\partial_z\partial_yf)\,dy\wedge dz+(\partial_z\partial_xf-\partial_x\partial_zf)\,dz\wedge dx
$$

## 2. 混合偏微分の対称性を使う

$f$が十分滑らかな関数であれば（シュワルツの定理）：

$$
\boxed{\partial_x\partial_yf = \partial_y\partial_xf}
$$

（以前のラプラシアン導出でも使った、微分の順序を入れ替えられるという性質です。）これを代入すると、$dx\wedge dy$の係数は $\partial_x\partial_yf-\partial_y\partial_xf=0$。他の2つの係数も同様にゼロになります。

$$
\boxed{d(df)=0}
$$

## 3. もっと一般的に：「対称×反対称＝0」という代数の構造

実は、上の議論は**もっと一般的な代数の事実の、特別な場合**です。この一般論を知っておくと、$d^2=0$が「たまたま偏微分の性質でゼロになった」のではなく、**構造的に必ずゼロになる**ことが分かります。

**一般的な補題**：$S_{ij}$が対称（$S_{ij}=S_{ji}$）、$A_{ij}$が反対称（$A_{ij}=-A_{ji}$）なら、これらを全部の添字について掛けて足したもの $\sum_{i,j}S_{ij}A_{ij}$ は、**$S,A$の中身が何であっても必ずゼロ**になります。

**証明**（3行で終わります）：和を取る添字$i,j$の名前を入れ替えても、和の値は変わりません（以前確認した「ダミー添字の付け替え」と同じ理屈）：

$$
\sum_{i,j}S_{ij}A_{ij} = \sum_{i,j}S_{ji}A_{ji}
$$

右辺に$S_{ji}=S_{ij}$（対称）と$A_{ji}=-A_{ij}$（反対称）を代入すると：

$$
\sum_{i,j}S_{ji}A_{ji} = \sum_{i,j}S_{ij}(-A_{ij}) = -\sum_{i,j}S_{ij}A_{ij}
$$

つまり、$\sum S_{ij}A_{ij}=-\sum S_{ij}A_{ij}$。両辺に同じもの（$\sum S_{ij}A_{ij}$）が入っているので、これを満たす値は$0$しかありません：

$$
\boxed{\sum_{i,j}S_{ij}A_{ij}=0}
$$

## 4. この一般補題を$d^2=0$に当てはめる

$d(df)$の計算に出てくる $\partial_i\partial_jf$（2階の混合偏微分）は、**どんな関数$f$についても**、シュワルツの定理から自動的に対称（$S_{ij}=\partial_i\partial_jf$）です。一方、$dx^i\wedge dx^j$（wedge積の基底）は、**定義から**必ず反対称（$A_{ij}=dx^i\wedge dx^j$、$A_{ij}=-A_{ji}$）です。

$$
d(df) = \sum_{i,j}(\partial_i\partial_jf)\,dx^i\wedge dx^j = \sum_{i,j}S_{ij}A_{ij} = 0
$$

**「対称なもの」と「反対称なもの」を掛けて全部足すと、必ずゼロになる**という、この一般補題1本だけから$d^2=0$が出てきます。$f$の具体的な中身（$x^2y+yz$だろうが何だろうが）は一切関係ありません。**これが「どんな関数でも必ずゼロになる」ことの、本当の理由**です。

---

# Part VI：$\operatorname{rot}(\operatorname{grad}f)=0$との対応

前回のノートでも触れましたが、ここでもう一度、直接確認します。$df\leftrightarrow\operatorname{grad}f=(\partial_xf,\partial_yf,\partial_zf)$、そして$d(df)\leftrightarrow\operatorname{rot}(\operatorname{grad}f)$という対応があるので：

$$
\operatorname{rot}(\operatorname{grad}f) = \big(\partial_y\partial_zf-\partial_z\partial_yf,\ \ \partial_z\partial_xf-\partial_x\partial_zf,\ \ \partial_x\partial_yf-\partial_y\partial_xf\big)
$$

各成分が、Part Vで確認した「対称な量の差」なので、シュワルツの定理からすべてゼロです：

$$
\boxed{\operatorname{rot}(\operatorname{grad}f) = \mathbf 0}
$$

これは、以前ベクトル解析の公式として個別に習うものですが、**その正体は$d^2=0$という、より一般的な構造の3次元での現れ**だった、ということになります。

---

# Part VII：改めて、「2階微分」という言葉のどこが紛らわしいか

$$
\begin{array}{c|c|c}
& \text{普通の2階微分}\ f'' & \text{外微分を2回}\ d(df) \\
\hline
\text{1回目の}d\text{で何が起きるか} & \text{関数}\to\text{関数}\text{（形は変わらない）} & \text{0-形式}\to\text{1-形式}\text{（形が変わる）} \\
\text{2回目の}d\text{で何が起きるか} & \text{関数}\to\text{関数} & \text{1-形式}\to\text{2-形式} \\
\text{結果に対称性・反対称性が関わるか} & \text{関わらない} & \partial_i\partial_jf\text{（対称）}\times dx^i\wedge dx^j\text{（反対称）が組み合わさる} \\
\text{一般にゼロになるか} & \text{ならない（}f=x^2\text{なら}f''=2\text{）} & \text{必ずゼロになる（構造的な必然）}
\end{array}
$$

**「2階微分」という同じ日本語が使われていても、$f''(x)$と$d(df)$はまったく別の演算**です。$f''$は「1変数の中で、同じ種類の操作を繰り返す」だけですが、$d$は「形式の次数を1つずつ押し上げていく」操作であり、**その過程で対称なもの（混合偏微分）と反対称なもの（wedge積）が自動的に出会うように、外微分という演算そのものが設計されている**、というのがこの話の本質でした。

---

# まとめ

$$
\boxed{
\begin{aligned}
&d^2=0\text{は「2階微分がゼロ」という意味ではなく、「0-形式}\to1\text{-形式}\to2\text{-形式という、次数を上げる操作を2回行うと必ずゼロになる」という意味}\\
&\text{原因は、}\partial_i\partial_jf\text{（混合偏微分、対称）と}dx^i\wedge dx^j\text{（wedge積、反対称）が自動的に出会うから}\\
&\text{一般補題「対称}\times\text{反対称の和}=0\text{」が、この現象の本当の理由（}f\text{の中身には一切依存しない）}\\
&\operatorname{rot}(\operatorname{grad}f)=\mathbf 0\text{という以前の公式は、この}d^2=0\text{の3次元での特別な現れにすぎない}
\end{aligned}
}
$$

具体的な関数$x^2y+yz$で実際に項が打ち消し合うのを1つずつ確認したこと（Part IV）と、それが「対称×反対称＝0」という、関数の中身に一切依存しない一般代数の帰結であること（Part V）の両方を押さえておけば、$d^2=0$は「なんとなく成り立つ不思議な公式」から「構造的に必然の性質」に見え方が変わると思います。
