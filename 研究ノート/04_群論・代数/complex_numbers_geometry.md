# 複素数の幾何学的構造 ―$\mathbb C\cong\mathbb R^2$から$U(1)$まで―

「複素数＝$a+bi$という数」という高校的な見方から一段上がり、複素数を「平面上の幾何学的対象」として捉え直します。これまでの $\sigma_y$、$SU(2)$ の議論と地続きの内容です。

---

# Part I：$\mathbb C\cong\mathbb R^2$ として見る

複素数 $z=a+bi$ を、平面上の点 $(a,b)$ そのものだと考えます。このとき、複素数の**足し算**は、ベクトルの足し算と完全に一致します：

$$
z_1+z_2 = (a_1+a_2)+(b_1+b_2)i \quad\longleftrightarrow\quad (a_1,b_1)+(a_2,b_2)=(a_1+a_2,b_1+b_2)
$$

問題は**掛け算**です。ベクトルには標準的な「掛け算」は定義されていませんが、複素数には定義されています。この掛け算が何を意味するのかを、以下で幾何学的に解き明かします。

---

# Part II：複素数の掛け算＝拡大縮小＋回転

$z=re^{i\theta}$（極形式、$r=|z|,\ \theta=\arg z$）と書くと、$z_1z_2=r_1r_2e^{i(\theta_1+\theta_2)}$ です。つまり掛け算は：

- **絶対値**：掛け算（$r_1\times r_2$）
- **偏角**：足し算（$\theta_1+\theta_2$）

に分解されます（以前ユニタリ行列の位相分離で使った「指数法則で肩同士を足す」という発想と同じです）。

特に $z\mapsto e^{i\theta}z$ という操作を考えると、絶対値は変わらず（$|e^{i\theta}|=1$）、偏角だけが $\theta$ だけ増えます。**これはまさに「原点を中心とした角度 $\theta$ の回転」**です。一方、$z\mapsto rz$（$r$：正の実数）は、向きを変えずに大きさだけを $r$ 倍にする**拡大縮小**です。したがって：

$$
\boxed{z \mapsto re^{i\theta}z \quad = \quad \text{拡大縮小（}r\text{倍）}+\text{回転（角度}\theta\text{）}}
$$

---

# Part III：複素数を「線形変換」として書く

$z\mapsto (a+bi)z$ という掛け算を、$z=x+yi$ を $(x,y)\in\mathbb R^2$ と見て、行列による線形変換として書き直します。

$$
(a+bi)(x+yi) = (ax-by)+(ay+bx)i
$$

これを $(x,y)\mapsto(ax-by,\ bx+ay)$ という変換と見ると：

$$
\boxed{a+bi \quad\longleftrightarrow\quad \begin{pmatrix}a&-b\\b&a\end{pmatrix}}
$$

という対応が得られます（実際に $\begin{pmatrix}a&-b\\b&a\end{pmatrix}\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}ax-by\\bx+ay\end{pmatrix}$ を計算すれば確認できます）。

## 1. 虚数単位 $i$ に対応する行列

$a=0,b=1$（つまり $z\mapsto iz$）を代入すると：

$$
i \longleftrightarrow J:=\begin{pmatrix}0&-1\\1&0\end{pmatrix}
$$

## 2. $J^2=-I$ の確認（$i^2=-1$ の行列版）

$$
J^2 = \begin{pmatrix}0&-1\\1&0\end{pmatrix}\begin{pmatrix}0&-1\\1&0\end{pmatrix} = \begin{pmatrix}-1&0\\0&-1\end{pmatrix} = -I
$$

**これは、以前パウリ行列のノートで扱った $\sigma_y$ の話と、構造的に同一です。** 実際、$-i\sigma_x=\begin{pmatrix}0&-1\\1&0\end{pmatrix}=J$ という対応があります（四元数の資料でも触れる通り）。「2乗すると $-I$ になる」という性質のおかげで、指数関数が $\cos,\sin$ に分解できる、という以前の議論がそのままここでも使えます。

---

# Part IV：$e^{\theta J}$ を計算する（複素数版のオイラーの公式）

$J^2=-I$ という性質を使い、パウリ行列のノートPart VIIIと**全く同じ手順**でテイラー展開を計算します。

$$
J^0=I,\quad J^1=J,\quad J^2=-I,\quad J^3=-J,\quad J^4=I,\ \dots
$$

（$J^2=-I$ が周期4のパターンを作ります。）テイラー展開 $e^{\theta J}=\sum_k\dfrac{(\theta J)^k}{k!}$ を偶数項・奇数項に分けます：

$$
e^{\theta J} = \underbrace{\left(1-\frac{\theta^2}{2!}+\frac{\theta^4}{4!}-\cdots\right)}_{=\cos\theta}I + \underbrace{\left(\theta-\frac{\theta^3}{3!}+\frac{\theta^5}{5!}-\cdots\right)}_{=\sin\theta}J
$$

$$
\boxed{e^{\theta J} = \cos\theta\,I+\sin\theta\,J = \begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}}
$$

これは、以前導出した2次元の回転行列 $R(\theta)$ そのものです。つまり：

$$
\boxed{e^{i\theta}\ (\text{複素数の世界})\quad\longleftrightarrow\quad e^{\theta J}\ (\text{行列の世界})}
$$

という対応が、オイラーの公式を経由してぴったり一致します。$e^{i\theta}=\cos\theta+i\sin\theta$ という式そのものが、実は「$2\times2$回転行列の指数表示」の複素数バージョンだった、というのがこの節の結論です。

---

# Part V：$\mathbb R^2$に「積」を入れたものが$\mathbb C$

$\mathbb R^2$ に、通常のベクトルの足し算に加えて、次のような特殊な積を定義します：

$$
(a,b)\cdot(c,d) := (ac-bd,\ ad+bc)
$$

これが $(a+bi)(c+di)=(ac-bd)+(ad+bc)i$ そのものです。**複素数とは、$\mathbb R^2$（2次元の実ベクトル空間）に、この特殊な掛け算を入れて「体」にしたもの**、という理解ができます（体：足し算・引き算・掛け算・割り算＝逆元が存在する代数構造）。

これは大きな主張です。**2次元の実ベクトル空間というだけなら、掛け算を持たないただのベクトル空間ですが、複素数はそこに「掛け算」まで自然に持ち込んだ、非常にリッチな構造**です。「複素数＝2次元ベクトルにすぎない」という理解では、この掛け算の構造（体であること）が見えなくなってしまいます。

---

# Part VI：$U(1)$という最小のLie群

絶対値1の複素数全体を考えます：

$$
U(1) := \{z\in\mathbb C : |z|=1\}
$$

これは $z=e^{i\theta}$（$\theta\in[0,2\pi)$）と書けるので、**複素平面の単位円**、つまり

$$
\boxed{U(1)\cong S^1}
$$

です。そして $U(1)$ は**群**です（$e^{i\theta_1}\cdot e^{i\theta_2}=e^{i(\theta_1+\theta_2)}\in U(1)$、単位元 $1=e^{i\cdot0}$、逆元 $e^{-i\theta}$ が存在）。しかも滑らかな多様体（円周）でもあるので、$U(1)$ はリー群です。以前扱った $U(2),SU(2)$ よりも、はるかに単純な**最小のリー群の例**が、実は最初から複素数の中に住んでいた、ということになります。

$U(1)$ の生成子（リー代数）は、$e^{i\theta}$ の $\theta$ に関する微分を $\theta=0$ で取ったもの、つまり単なる「$i$」（虚数単位）そのものです。以前の $\mathfrak{su}(2)$（パウリ行列が生成子）の議論と対応させると、$\mathfrak u(1)$ の生成子はたった1つ、$i$（あるいは行列表現なら $J$）だけです。

---

# Part VII：この先の学び方（Needhamの本について）

Tristan Needham著『Visual Complex Analysis』（Oxford University Press）という本が、今回の視点（複素数を幾何学的対象として捉える）を出発点に据えた、標準的な複素解析の教科書とはかなり異質な構成になっています。第1章のタイトルがまさに「Geometry and Complex Arithmetic」で、以降も

- Complex Functions as Transformations（複素関数を変換として捉える）
- Möbius Transformations and Inversion
- Differentiation: The Amplitwist Concept（微分を「拡大＋回転」として捉える）

という、計算よりも幾何学的直感を軸にした構成が続きます。

日本語で基礎を固めたい場合は、宮地秀樹『複素解析』（日本評論社）のような、複素数平面・極形式から始める入門書を並行して使うと、幾何学的な直感と厳密な理論の両方を補強できます。

---

# まとめ

$$
\boxed{
\begin{aligned}
&\mathbb C\cong\mathbb R^2\text{：複素数を平面上の点として見る}\\
&z_1z_2\text{：拡大縮小＋回転（絶対値は積、偏角は和）}\\
&a+bi\leftrightarrow\begin{pmatrix}a&-b\\b&a\end{pmatrix},\quad i\leftrightarrow J,\quad J^2=-I\\
&e^{\theta J}=\cos\theta\,I+\sin\theta\,J\quad\text{（オイラーの公式の行列版、パウリ行列の}\sigma_y\text{の議論と同型）}\\
&\mathbb C=(\mathbb R^2,\ +,\ \times)\text{：単なるベクトル空間を超えた「体」の構造}\\
&U(1)=\{|z|=1\}\cong S^1\text{：複素数の中に住む、最小のリー群}
\end{aligned}
}
$$

「複素数＝実部＋虚部の数」という見方から、「複素数＝回転と拡大縮小を同時に表現する幾何学的対象であり、かつ$\mathbb R^2$に積を入れた体である」という見方に移ることで、これまで扱ってきたユニタリ行列・パウリ行列・リー群の話が、すべて複素数という一番身近な対象の中に、最初から縮図として存在していたことが見えてきます。
