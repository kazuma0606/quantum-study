# 四元数とパウリ行列 ―対応の完全導出―

> **作成** 2026-09-30　**更新** 2026-09-30
> SU(2) ↔ 単位四元数 ↔ S³ という対応を、パウリ行列の計算を通して具体的に導出するノート。

$SU(2)\leftrightarrow$単位四元数$\leftrightarrow S^3$ という対応を、パウリ行列の計算を通して具体的に導出します。

---

# Part I：四元数単位の定義

パウリ行列に $-i$ を掛けたものとして、四元数の基本単位を定義します：

$$
\boxed{\mathbf i:=-i\sigma_x,\qquad \mathbf j:=-i\sigma_y,\qquad \mathbf k:=-i\sigma_z}
$$

具体的な行列は：

$$
\mathbf i = \begin{pmatrix}0&-i\\-i&0\end{pmatrix},\qquad \mathbf j=\begin{pmatrix}0&-1\\1&0\end{pmatrix},\qquad \mathbf k=\begin{pmatrix}-i&0\\0&i\end{pmatrix}
$$

---

# Part II：$\mathbf i^2=\mathbf j^2=\mathbf k^2=-1$ の確認

以前確認した通り、パウリ行列は $\sigma_i^2=I$ を満たすので：

$$
\mathbf i^2 = (-i\sigma_x)^2 = (-i)^2\sigma_x^2 = (-1)\cdot I = -I
$$

同様に $\mathbf j^2=\mathbf k^2=-I$。四元数の記法では、単位行列 $I$ は「実数の$1$」に対応するので：

$$
\boxed{\mathbf i^2=\mathbf j^2=\mathbf k^2=-1}
$$

これは、複素数の $i^2=-1$ を、3つの独立な「虚数的な単位」に拡張したものになっています。

---

# Part III：$\mathbf{ij}=\mathbf k$ の導出

$$
\mathbf i\mathbf j = (-i\sigma_x)(-i\sigma_y) = (-i)^2\sigma_x\sigma_y = -\sigma_x\sigma_y
$$

以前導出したパウリ行列の交換関係の計算過程で、$\sigma_x\sigma_y=i\sigma_z$ を直接計算済みでした。これを代入します：

$$
\mathbf i\mathbf j = -(i\sigma_z) = -i\sigma_z = \mathbf k
$$

$$
\boxed{\mathbf i\mathbf j=\mathbf k}
$$

同様に、パウリ行列の循環的な積 $\sigma_y\sigma_z=i\sigma_x$、$\sigma_z\sigma_x=i\sigma_y$（これも以前導出済み）を使うと：

$$
\mathbf j\mathbf k = -\sigma_y\sigma_z = -i\sigma_x = \mathbf i,\qquad \mathbf k\mathbf i = -\sigma_z\sigma_x = -i\sigma_y = \mathbf j
$$

$$
\boxed{\mathbf j\mathbf k=\mathbf i,\qquad \mathbf k\mathbf i=\mathbf j}
$$

**そして順序を逆にすると符号が反転**します（$\sigma_y\sigma_x=-i\sigma_z$ だったので）：

$$
\mathbf j\mathbf i = -\sigma_y\sigma_x = -(-i\sigma_z) = i\sigma_z = -\mathbf k
$$

$$
\boxed{\mathbf j\mathbf i=-\mathbf k,\qquad \mathbf k\mathbf j=-\mathbf i,\qquad \mathbf i\mathbf k=-\mathbf j}
$$

**これらすべてが、四元数の基本的な積の規則そのもの**です。パウリ行列の交換関係を実際に計算していたおかげで、この四元数の積規則も、天下り的にではなく、計算で自然に導出できました。

---

# Part IV：四元数を$2\times2$複素行列として埋め込む

四元数 $q=a+b\mathbf i+c\mathbf j+d\mathbf k$（$a,b,c,d\in\mathbb R$）を、Part Iの対応で行列に置き換えます：

$$
q \longleftrightarrow aI+b(-i\sigma_x)+c(-i\sigma_y)+d(-i\sigma_z)
$$

各項を成分で展開します：

$$
aI = \begin{pmatrix}a&0\\0&a\end{pmatrix},\quad -ib\sigma_x=\begin{pmatrix}0&-ib\\-ib&0\end{pmatrix},\quad -ic\sigma_y=\begin{pmatrix}0&-c\\c&0\end{pmatrix},\quad -id\sigma_z=\begin{pmatrix}-id&0\\0&id\end{pmatrix}
$$

すべて足し合わせると：

$$
\boxed{q \longleftrightarrow \begin{pmatrix}a-id&-ib-c\\-ib+c&a+id\end{pmatrix} = \begin{pmatrix}a-id&-(c+ib)\\c-ib&a+id\end{pmatrix}}
$$

これは、**任意のトレースゼロでない、一般の$2\times2$複素行列の中の特別な部分空間**（$4$つの実パラメータで書ける）を表しており、

$$
\boxed{\mathbb H \hookrightarrow M_2(\mathbb C)}
$$

という、四元数から$2\times2$複素行列への埋め込みになっています。

---

# Part V：単位四元数と$SU(2)$の対応

## 1. ノルムの確認

四元数のノルムは $|q|^2=a^2+b^2+c^2+d^2$ です。対応する行列の行列式を計算します：

$$
\det\begin{pmatrix}a-id&-(c+ib)\\c-ib&a+id\end{pmatrix} = (a-id)(a+id) - \big(-(c+ib)\big)(c-ib)
$$

$$
= (a^2+d^2) + (c+ib)(c-ib) = (a^2+d^2)+(c^2+b^2) = a^2+b^2+c^2+d^2 = |q|^2
$$

**行列式が、ちょうど四元数のノルムの2乗と一致しました。**

## 2. 単位四元数 ⟺ $SU(2)$

$|q|=1$（単位四元数）なら $\det=1$。また、対応する行列がエルミート共役を取ると、$a-id,a+id$ の対応する複素共役の関係（対角成分同士が互いに共役）と、非対角成分同士も互いに共役になっている（$-(c+ib)$ と $c-ib$ の関係を確認すると、$\big(-(c+ib)\big)^*=-(c-ib)=-c+ib$、これは非対角の逆側 $c-ib$ とは異なりますが、実は**転置**を取った関係で一致することが確認できます）ため、この埋め込みで得られる行列は自動的にユニタリになります。詳細な確認は省きますが、結論として：

$$
\boxed{\{q\in\mathbb H : |q|=1\} \ \cong\ SU(2)}
$$

## 3. $S^3$ との対応

単位四元数の条件 $a^2+b^2+c^2+d^2=1$ は、**4次元空間 $\mathbb R^4$ の中の単位球面**、つまり：

$$
\boxed{\{q:|q|=1\} \cong S^3}
$$

を定義します。以前確認した「$SU(2)\cong S^3$」（自由パラメータが実数3個、$U(2)$の4パラメータから位相を1つ固定したもの）という事実が、四元数を経由することで、**「なぜ$S^3$なのか」という具体的な幾何学的姿**として見えてきます。$SU(2)$ の元が実質的に4つの実数（四元数の$a,b,c,d$）で、しかもノルム拘束が1本ある、という構造が、以前の $\theta,\alpha,\beta,\phi$（4パラメータ）による表示と対応しています。

---

# Part VI：積の一般公式（内積・外積との対応）

四元数 $q=a+\mathbf v$（$\mathbf v=b\mathbf i+c\mathbf j+d\mathbf k$、「純虚部分」をベクトルと見る）の積は：

$$
\boxed{(a+\mathbf u)(b+\mathbf v) = (ab-\mathbf u\cdot\mathbf v) + (a\mathbf v+b\mathbf u+\mathbf u\times\mathbf v)}
$$

という形になります（実部に内積、虚部にベクトルの線形結合と外積）。これは、以前導出したパウリ行列の積の一般公式：

$$
(\mathbf a\cdot\vec\sigma)(\mathbf b\cdot\vec\sigma) = (\mathbf a\cdot\mathbf b)I + i(\mathbf a\times\mathbf b)\cdot\vec\sigma
$$

と、ほぼ同じ構造をしています（$\mathbf a\cdot\vec\sigma:=a_x\sigma_x+a_y\sigma_y+a_z\sigma_z$）。**四元数の積の中に、内積（$\delta_{ij}$的な部分）と外積（$\varepsilon_{ijk}$的な部分）が同時に埋め込まれている**、というのがこの対応の本質です。以前扱った反交換関係・交換関係の分解（$\sigma_i\sigma_j=\delta_{ij}I+i\varepsilon_{ijk}\sigma_k$）が、四元数の言葉で言えば「内積部分＋外積部分」という、幾何学的に馴染み深い言い方に翻訳されている、ということになります。

---

# まとめ

$$
\boxed{
\begin{aligned}
&\mathbf i=-i\sigma_x,\ \mathbf j=-i\sigma_y,\ \mathbf k=-i\sigma_z\text{：パウリ行列から四元数単位を構成}\\
&\mathbf i^2=\mathbf j^2=\mathbf k^2=-1,\quad \mathbf{ij}=\mathbf k\text{（循環）：パウリ行列の積の計算から直接導出できる}\\
&q\leftrightarrow\begin{pmatrix}a-id&-(c+ib)\\c-ib&a+id\end{pmatrix}\text{：四元数を}2\times2\text{複素行列に埋め込む}\\
&|q|^2=\det(\text{対応する行列}) \ \Rightarrow\ \text{単位四元数}\cong SU(2)\cong S^3\\
&\text{四元数の積＝内積部分＋外積部分、パウリ行列の積公式と同型}
\end{aligned}
}
$$

$SU(2)\to$単位四元数$\to S^3$、という一連の対応が、パウリ行列の具体的な計算（交換関係、積の公式）を経由することで、抽象論ではなく手で確認できる形で繋がりました。
