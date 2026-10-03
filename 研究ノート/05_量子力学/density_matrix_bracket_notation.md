# 密度行列とブラケット記法 ―関係の整理と計算上の疑問の解消―

$\langle\Psi|\hat A|\Psi\rangle$ と $\operatorname{Tr}(\rho\hat A)$ の関係、そして密度行列が必要になる理由を整理し、最後に**未解決だった計算上の疑問**（外積を取ってから演算子を作用させたら縦ベクトルになってしまった件）を、具体例で最後まで解消します。

---

# Part I：純粋状態では2つの表現が完全に同値であることの証明

$\rho:=|\Psi\rangle\langle\Psi|$（密度演算子）と定義したとき、

$$
\boxed{\langle\Psi|\hat A|\Psi\rangle = \operatorname{Tr}(\rho\hat A)}
$$

を証明します。以前扱った完全性関係 $\sum_n|n\rangle\langle n|=1$（正規直交基底 $\{|n\rangle\}$）を使います。

トレースの定義（対角成分の和）を、基底 $\{|n\rangle\}$ で書き下します：

$$
\operatorname{Tr}(\rho\hat A) = \sum_n\langle n|\rho\hat A|n\rangle = \sum_n\langle n|\Psi\rangle\langle\Psi|\hat A|n\rangle
$$

$\langle n|\Psi\rangle$ はただの数（スカラー）なので、順番を入れ替えて後ろに回せます：

$$
= \sum_n\langle\Psi|\hat A|n\rangle\langle n|\Psi\rangle
$$

$\langle n|\Psi\rangle$ を右端に、$\langle\Psi|\hat A$ を左に出して、和の記号 $\sum_n$ を $|n\rangle\langle n|$ の部分にだけ残します：

$$
= \langle\Psi|\hat A\left(\sum_n|n\rangle\langle n|\right)|\Psi\rangle
$$

完全性関係 $\sum_n|n\rangle\langle n|=1$ を使うと：

$$
= \langle\Psi|\hat A\cdot1\cdot|\Psi\rangle = \langle\Psi|\hat A|\Psi\rangle
$$

$$
\boxed{\operatorname{Tr}(\rho\hat A) = \langle\Psi|\hat A|\Psi\rangle}
$$

**証明完了です。** 完全性関係というたった1つの道具（以前の経路積分の導出でも使った技法）だけで、この同値性が示せます。

---

# Part II：なぜ密度行列が必要になるのか（混合状態）

純粋状態だけなら、ケット $|\Psi\rangle$ だけで十分です。しかし、**「50%の確率で$|0\rangle$、50%の確率で$|1\rangle$」というような、古典的な確率混合を持つ状態**は、1つのケットでは表現できません。

これは「量子的な重ね合わせ」（$\frac1{\sqrt2}(|0\rangle+|1\rangle)$）とは**まったく別物**である点に注意が必要です。重ね合わせは干渉するので、測定基底を変えると確率分布が変わります。一方、「50%50%の確率混合」は、単に「どちらの状態にあるか自分たちが知らないだけ」という古典的な無知を表しており、干渉効果を持ちません。この違いを表現するために：

$$
\boxed{\rho = \sum_ip_i|\Psi_i\rangle\langle\Psi_i|}
$$

という一般形（各状態 $|\Psi_i\rangle$ に古典的な確率 $p_i$ を掛けて足し合わせたもの）が必要になります。純粋状態はこの特別な場合（ある1つの $i$ について $p_i=1$、他はすべて$0$）です。

期待値の計算は、混合状態でも同じ公式 $\langle A\rangle=\operatorname{Tr}(\rho\hat A)$ がそのまま使えます（Part Iの証明を、各 $|\Psi_i\rangle$ について行い、確率 $p_i$ で重み付けして足せば一般化できます）。「**1つのケットでは書けないものまで扱える**」という点が、密度行列の最大の利点です。

---

# Part III：計算上の疑問を解消する ―「外積を取ってから作用させたら縦ベクトルになった」

## 1. まず、正しい手順を具体的に確認する

$|\Psi\rangle=x_1|0\rangle+x_2|1\rangle$（$x_1,x_2\in\mathbb C$）とします。列ベクトルで書くと：

$$
|\Psi\rangle = \begin{pmatrix}x_1\\x_2\end{pmatrix},\qquad \langle\Psi| = \begin{pmatrix}x_1^*&x_2^*\end{pmatrix}
$$

**外積**（$|\Psi\rangle\langle\Psi|$、列ベクトル×行ベクトル）を計算します：

$$
\rho = |\Psi\rangle\langle\Psi| = \begin{pmatrix}x_1\\x_2\end{pmatrix}\begin{pmatrix}x_1^*&x_2^*\end{pmatrix} = \begin{pmatrix}x_1x_1^*&x_1x_2^*\\x_2x_1^*&x_2x_2^*\end{pmatrix} = \begin{pmatrix}|x_1|^2&x_1x_2^*\\x_2x_1^*&|x_2|^2\end{pmatrix}
$$

**これは$2\times2$の正方行列です。** 外積は「縦ベクトル×横ベクトル」なので、必ず正方行列（あるいは長方行列）になります。ここまでは問題ありません。

## 2. 演算子 $\hat A$ を作用させる（$\rho\hat A$）

$\hat A=\sigma_z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}$ を例に取ります。$\rho\hat A$ を計算します（**行列×行列**、正方行列同士の積）：

$$
\rho\hat A = \begin{pmatrix}|x_1|^2&x_1x_2^*\\x_2x_1^*&|x_2|^2\end{pmatrix}\begin{pmatrix}1&0\\0&-1\end{pmatrix} = \begin{pmatrix}|x_1|^2&-x_1x_2^*\\x_2x_1^*&-|x_2|^2\end{pmatrix}
$$

**これも$2\times2$の正方行列のままです。** 正方行列にはトレース（対角成分の和）が定義できます：

$$
\operatorname{Tr}(\rho\hat A) = |x_1|^2-|x_2|^2
$$

## 3. 検算：$\langle\Psi|\hat A|\Psi\rangle$ と一致するか

$$
\langle\Psi|\hat A|\Psi\rangle = \begin{pmatrix}x_1^*&x_2^*\end{pmatrix}\begin{pmatrix}1&0\\0&-1\end{pmatrix}\begin{pmatrix}x_1\\x_2\end{pmatrix} = \begin{pmatrix}x_1^*&x_2^*\end{pmatrix}\begin{pmatrix}x_1\\-x_2\end{pmatrix} = x_1^*x_1-x_2^*x_2 = |x_1|^2-|x_2|^2
$$

**一致しました。** Part Iで証明した恒等式が、具体的な数値でも成立しています。

## 4. どこで「縦ベクトルになってしまった」のか（原因の特定）

おそらく、$\rho\hat A$（正方行列のまま）で止めるべきところを、さらに $|\Psi\rangle$ をもう一度右から掛けてしまった（$\rho\hat A|\Psi\rangle$ を計算してしまった）のだと思われます。実際に計算してみます：

$$
\rho\hat A|\Psi\rangle = \begin{pmatrix}|x_1|^2&-x_1x_2^*\\x_2x_1^*&-|x_2|^2\end{pmatrix}\begin{pmatrix}x_1\\x_2\end{pmatrix} = \begin{pmatrix}|x_1|^2x_1-x_1x_2^*x_2\\x_2x_1^*x_1-|x_2|^2x_2\end{pmatrix}
$$

**これは確かに縦ベクトル（$2\times1$）になります。** 正方行列（$2\times2$）に、さらに列ベクトル（$2\times1$）を右から掛けると、結果は再び列ベクトル（$2\times1$）になるからです（行列の積の一般規則：$(m\times n)$行列と$(n\times p)$行列の積は$(m\times p)$になる。ここでは $2\times2$ と $2\times1$ の積なので $2\times1$）。**列ベクトルにはトレースが定義できません**（トレースは正方行列の対角成分の和という定義なので、そもそも正方でないベクトルには適用できない概念です）。

## 5. 結論：$\operatorname{Tr}(\rho\hat A)$ は「$\rho\hat A$ という正方行列」のトレースであって、それをさらに $|\Psi\rangle$ に作用させるものではない

$$
\boxed{
\begin{aligned}
&\rho = |\Psi\rangle\langle\Psi|\quad\text{（}2\times2\text{、正方行列）}\\
&\rho\hat A\quad\text{（}2\times2\text{、正方行列のまま。ここでストップしてトレースを取る）}\\
&\operatorname{Tr}(\rho\hat A)\quad\text{（スカラー、これが期待値）}
\end{aligned}
}
$$

$\rho\hat A|\Psi\rangle$ のように、さらに $|\Psi\rangle$ を掛けてしまうと、正方行列でなくなり（列ベクトルになり）、トレースの定義域から外れてしまいます。これが「縦ベクトルになってトレースが計算できない」という現象の正体です。

---

# Part IV：規格化条件について（完全性関係との違い）

もう一つの疑問「$x_1,x_2$の絶対値の2乗が1になるはず」について。これは正しいですが、**完全性関係（completeness relation）とは別の条件**です。

- **完全性関係** $\sum_n|n\rangle\langle n|=1$：基底 $\{|n\rangle\}$ そのものが持つ性質。特定の状態が規格化されているかどうかとは無関係。
- **規格化条件** $\langle\Psi|\Psi\rangle=1$：状態 $|\Psi\rangle$ 自身が満たすべき条件。

$\rho=|\Psi\rangle\langle\Psi|$ のトレースを計算すると：

$$
\operatorname{Tr}(\rho) = |x_1|^2+|x_2|^2
$$

（Part III-1の $\rho$ の対角成分の和。）$\operatorname{Tr}(\rho)=1$ は密度行列の一般的な要請（確率の総和が1）なので、$|x_1|^2+|x_2|^2=1$ が要求されます。これは $\langle\Psi|\Psi\rangle=x_1^*x_1+x_2^*x_2=|x_1|^2+|x_2|^2=1$ という、**規格化条件**そのものです。完全性関係とは名前は似ていますが、指しているものが違う（片方は基底の性質、片方は個別の状態の性質）という点を区別しておくと、今後の混同を防げます。

---

# まとめ

$$
\boxed{
\begin{aligned}
&\langle\Psi|\hat A|\Psi\rangle=\operatorname{Tr}(\rho\hat A)\text{：完全性関係を使えば数行で証明できる恒等式}\\
&\rho=\sum_ip_i|\Psi_i\rangle\langle\Psi_i|\text{：古典的な確率混合を扱うために必要な一般化}\\
&\rho\hat A\text{は正方行列のまま：ここでトレースを取る。さらに}|\Psi\rangle\text{を掛けると列ベクトルになりトレース不可}\\
&|x_1|^2+|x_2|^2=1\text{は「規格化条件」であり、「完全性関係」とは別の概念}
\end{aligned}
}
$$
