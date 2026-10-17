# 射影演算子による測定確率の計算 ―$P(x^\ast)=\big\|(|x^\ast\rangle\langle x^\ast|\otimes I)|\Psi\rangle\big\|^2=\tfrac1N$の導出―

> **作成** 2026-10-17　**更新** 2026-10-17
> 入力レジスタを測ると正解の確率が $\frac1N$ になることを、射影演算子 $P_{x^\ast}\otimes I$ とボルン則から導出する。テンソル積の作用の証明、4候補の数値例、付録（完全な射影測定とPOVM、結果レジスタの測定とエンタングルメント、クロネッカー積の性質とQiskitの並び順、検算の一覧）。

関数を計算する量子回路に、すべての候補の均等な重ね合わせを入力したあと、入力レジスタを測定して正解$x^\ast$が得られる確率が$\tfrac1N$であることを、射影演算子を使って導出します。物理の仮定（ボルン則）を使う箇所と、線形代数だけで導ける箇所を区別しながら進めます。最後に4候補の数値例で確認します。

- **Part I**：何を計算するのか（$|\Psi\rangle$ と、求めたい確率）
- **Part II**：正解の成分だけを取り出す射影演算子 $|x^\ast\rangle\langle x^\ast|$
- **Part III**：なぜ $\otimes I$ が必要なのか。テンソル積の定義と、$(A\otimes B)(|u\rangle\otimes|v\rangle)=A|u\rangle\otimes B|v\rangle$ の証明、3つ以上のテンソル積、どこまで分けられるか、線形性
- **Part IV**：確率は、取り出した成分のノルムの2乗（ボルン則）
- **Part V**〜**VII**：$|\Psi\rangle$ に当てはめる、ノルムの2乗、一般の入力
- **Part VIII**：数値例（4候補・正解1個）
- **付録A**：完全な射影測定、測定後の状態、POVM
- **付録B**：結果レジスタを測る、係数行列とエンタングルメント
- **付録C**：クロネッカー積の性質と、Qiskit の並び順
- **付録D**：検算の一覧

**関連ファイル**：図は [figures/make_measurement_projection_figures.py](figures/make_measurement_projection_figures.py) で作っていて、各図の値はスクリプトの中で本文の式と照合しています。式と数値の検算は [experiments/measurement_projection/](../../experiments/measurement_projection/README.md)（スクリプトと44件のテスト、Qiskit での確認と、別ノートの部分トレースの検算を含む）。密度行列と完全性関係は[密度行列のノート](../05_量子力学/density_matrix_bracket_notation.md)、ブラケット記法とボルン則は[ブラケット記法のノート](../05_量子力学/bra_ket_notation_path_integral.md)、パウリ行列とブロッホ球は[パウリ行列のノート](../04_群論・代数/pauli_matrices_derivation_and_group.md)、指数関数とトロッター分解は[行列の指数関数のノート](../04_群論・代数/matrix_exponential_commutator_bch_trotter.md)、ノイズと量子チャネルは[ノイズのノート](../05_量子力学/noise_modeling_through_mri.md)にあります。

<a id="toc"></a>

## 目次

<!-- toc:start -->

- [Part I：何を計算するのか](#p1)
- [Part II：正解の成分だけを取り出す演算子|x^\*⟩⟨ x^\*|](#p2)
- [Part III：なぜ⊗ Iが必要なのか](#p3)
  - [1. 全体の状態は2つのレジスタのテンソル積](#p3-1)
  - [2. テンソル積の演算子は、それぞれのレジスタに別々に作用する](#p3-2)
  - [3. M\_x^\*を各項に作用させる](#p3-3)
  - [4. 線形性：和の各項に別々に作用させてよい](#p3-4)
- [Part IV：確率は、取り出した成分のノルムの2乗（ボルン則）](#p4)
  - [1. 一般の状態の展開](#p4-1)
  - [2. 仮定：ボルン則](#p4-2)
  - [3. 入力レジスタだけを測定する場合](#p4-3)
  - [4. 成分を取り出す](#p4-4)
  - [5. テンソル積の内積](#p4-5)
  - [6. ノルムの2乗を計算する](#p4-6)
  - [7. 結論](#p4-7)
- [Part V：|Psi⟩に当てはめる](#p5)
- [Part VI：ノルムの2乗を取る](#p6)
- [Part VII：一般の入力の場合](#p7)
- [Part VIII：数値例：4候補・正解1個](#p8)
  - [1. 設定](#p8-1)
  - [2. 列ベクトルで書く](#p8-2)
  - [3. 射影演算子を行列で書く](#p8-3)
  - [4. 状態に作用させる（Part Vの確認）](#p8-4)
  - [5. ノルムの2乗（Part VIの確認）](#p8-5)
  - [6. 他の候補](#p8-6)
- [まとめ](#summary)
- [付録A：完全な射影測定、測定後の状態、POVM](#appA)
  - [A-1. 完全性：確率の和が1になる](#A-1)
  - [A-2. 測定後の状態（射影仮説）](#A-2)
  - [A-3. 同じ測定をもう一度すると](#A-3)
  - [A-4. 一般の測定と POVM](#A-4)
- [付録B：結果レジスタを測る、係数行列とエンタングルメント](#appB)
  - [B-1. 係数行列](#B-1)
  - [B-2. 結果レジスタを測る](#B-2)
  - [B-3. 積状態の判定：係数行列の階数](#B-3)
- [付録C：クロネッカー積の性質と、Qiskit の並び順](#appC)
  - [C-1. テンソル積同士の積はテンソル積](#C-1)
  - [C-2. そのほかの性質](#C-2)
  - [C-3. Qiskit の並び順](#C-3)
- [付録D：検算の一覧](#appD)

<!-- toc:end -->

---

## 記法と約束

このノートでは、**記号の宣言**（この節）、**演算の定義**（初めて使う箇所で定義）、**性質の証明**（必要な箇所で証明）を区別します。この節で宣言した記号は、以降は説明なしで使います。

### 共通の記法

| 記法 | 意味 |
|---|---|
| $\mathbb N,\ \mathbb R,\ \mathbb C$ | 自然数、実数、複素数の集合 |
| $\mathcal H$ | 有限次元の複素ヒルベルト空間（内積を持つ複素ベクトル空間） |
| $\dim\mathcal H=m$ | $\mathcal H$の次元が$m$ |
| $\lvert\psi\rangle\in\mathcal H$ | $\mathcal H$に属するケットベクトル |
| $\langle\psi\rvert$ | $\lvert\psi\rangle$に対応するブラ（成分を複素共役にして横に並べたもの） |
| $\langle\phi\vert\psi\rangle$ | 内積。成分で$\sum_k\phi_k^\ast\psi_k$ |
| $\lVert\psi\rVert$ | ノルム（長さ）。$\lVert\psi\rVert^2:=\langle\psi\vert\psi\rangle$ |
| $\mathcal L(\mathcal H)$ | $\mathcal H$上の線形演算子（$\mathcal H\to\mathcal H$の線形写像）全体 |
| $A^\dagger$ | $A$の随伴演算子（行列では、転置して複素共役を取ったもの） |
| $I_{\mathcal H}$、$I_m$ | $\mathcal H$上の恒等演算子、$m\times m$の単位行列 |
| $\otimes$ | テンソル積（Part III §2で定義） |
| $\cong$ | 同型（基底を対応させることで同一視できる） |
| $\delta_{ij}$ | クロネッカーのデルタ（$i=j$なら$1$、それ以外は$0$） |

**基底を固定した表示**：有限次元のヒルベルト空間$\mathcal H$で正規直交基底（量子計算では計算基底）を1つ固定すると、ベクトルは成分を並べた列ベクトルで、演算子は行列で表せます。このノートでは、この意味で$\mathcal H=\mathbb C^m$、$\mathcal L(\mathcal H)=\mathbb C^{m\times m}$（$m\times m$の複素行列全体）と書きます。有限次元なので、すべての線形演算子は行列で表せます（無限次元の空間では、$\mathcal L(\mathcal H)$を有界な線形演算子に限る、などの条件が文献によって付きます）。

**書体の使い分け**：$\mathbb C$のような黒板太字は数の集合、$\mathcal H$のような筆記体は空間、$|\psi\rangle$のようなケットはベクトル、$A$のような斜体の大文字は演算子（行列）、$\mathrm{CNOT}$のような立体の文字は名前の付いたゲートや群（例：$\mathrm{SU}(2)$）、$\mathfrak{su}(2)$のようなフラクトゥール体はリー代数を表します。

### 量子計算の約束

$q$量子ビットのレジスタの状態空間は

$$
\mathcal H_q:=(\mathbb C^2)^{\otimes q}\cong\mathbb C^{2^q}
$$

で、量子状態は規格化されたベクトル$|\psi\rangle\in\mathcal H_q$、$\langle\psi|\psi\rangle=1$です。計算基底$|j\rangle$（$j=0,\dots,2^q-1$）は、$j$を2進数で書いたビット列の順に並べます（例：2量子ビットでは$|00\rangle,|01\rangle,|10\rangle,|11\rangle$）。$|ab\rangle$は$|a\rangle\otimes|b\rangle$の略記で、$|u\rangle|v\rangle$も$|u\rangle\otimes|v\rangle$の略記です。量子ビットの個数$q$と状態空間の次元$2^q$は別のものです（Part III §2-f-5）。

### このノートで使う記号

- $x_1,\dots,x_N$：入力の候補となるビット列。すべて異なるとします。$|x_i\rangle$はその計算基底ベクトルで、正規直交：$\langle x_i|x_j\rangle=\delta_{ij}$。
- $x^\ast$：正解。候補$x_1,\dots,x_N$の中にちょうど1つ含まれるとします。$\delta_{x^\ast,x_i}$は$x_i=x^\ast$なら$1$、それ以外は$0$です。
- $f(x)$：候補$x$に対して計算する関数の値（ビット列）。$|f(x)\rangle$はその計算基底ベクトルです。
- **入力レジスタ**：$x$を入れる量子ビットの組。**結果レジスタ**：$f(x)$を書き込む量子ビットの組。
- $I$：結果レジスタ上の恒等演算子。

---

<a id="p1"></a>

# Part I：何を計算するのか

関数を計算する回路$U_f$は、結果レジスタを$|0\cdots0\rangle$に初期化しておくと

$$
U_f\,|x\rangle|0\cdots0\rangle=|x\rangle|f(x)\rangle
$$

と働く回路です（入力$x$を残したまま、結果レジスタに$f(x)$を書き込みます）。入力レジスタをすべての候補の均等な重ね合わせ$\frac1{\sqrt N}\sum_i|x_i\rangle$にして$U_f$をかけると、$U_f$は線形なので和の各項に別々に作用し：

$$
|\Psi\rangle:=\frac1{\sqrt N}\sum_{i=1}^N|x_i\rangle|f(x_i)\rangle
$$

となります。これは入力レジスタと結果レジスタを合わせた量子状態です。

**求めたいもの**：この状態で入力レジスタを測定したとき、正解$x^\ast$が得られる確率$P(x^\ast)$。

**方針**：正解に対応する状態の成分だけを取り出し（Part II・Part III）、その大きさから確率を求めます（Part IV〜Part VI）。

![回路の流れ](figures/mp01_flow.png)

*回路の流れ。$U_f$ で $|\Psi\rangle$ を作り、結果レジスタには何もしない恒等演算子 $I$ を組み合わせた $M_{x^\ast}=P_{x^\ast}\otimes I$ で正解の成分を取り出し、ノルムの2乗を取ると確率 $P(x^\ast)$ が得られる。図を描くときに、$N=4$ の例で $P=\frac14$、$M_{x^\ast}|\Psi\rangle=\frac12|111\rangle$ を確かめています。*

---

<a id="p2"></a>

# Part II：正解の成分だけを取り出す演算子$|x^\ast\rangle\langle x^\ast|$

**記法**：正解$x^\ast$についての演算子を

$$
P_{x^\ast}:=|x^\ast\rangle\langle x^\ast|
$$

と定義します。これは、正解$x^\ast$の方向（1次元の部分空間）への**射影演算子**です。

**作用**：候補の基底ベクトル$|x_i\rangle$に作用させると、ブラとケットの積$\langle x^\ast|x_i\rangle$が数になるので：

$$
P_{x^\ast}|x_i\rangle=|x^\ast\rangle\langle x^\ast|x_i\rangle=\delta_{x^\ast,x_i}\,|x^\ast\rangle
$$

（最後は正規直交性$\langle x^\ast|x_i\rangle=\delta_{x^\ast,x_i}$です。）したがって：

$$
P_{x^\ast}|x_i\rangle=\begin{cases}|x^\ast\rangle&(x_i=x^\ast)\\0&(x_i\ne x^\ast)\end{cases}
$$

**$P_{x^\ast}$は、正解の基底成分だけを残し、それ以外をゼロにする演算子です。** これは新しい仮定ではなく、計算基底の正規直交性から直接導かれる性質です。

**射影演算子の性質**：

- $P_{x^\ast}^2=P_{x^\ast}$：$P_{x^\ast}^2=|x^\ast\rangle\langle x^\ast|x^\ast\rangle\langle x^\ast|=|x^\ast\rangle\cdot1\cdot\langle x^\ast|=P_{x^\ast}$（一度取り出したものをもう一度取り出しても変わらない）。
- $P_{x^\ast}^\dagger=P_{x^\ast}$：$(|a\rangle\langle b|)^\dagger=|b\rangle\langle a|$なので、$a=b=x^\ast$では自分自身です。

---

<a id="p3"></a>

# Part III：なぜ$\otimes I$が必要なのか

<!-- part-toc:start -->

**この Part の内容**

- [1. 全体の状態は2つのレジスタのテンソル積](#p3-1)
- [2. テンソル積の演算子は、それぞれのレジスタに別々に作用する](#p3-2)
  - [2-a. 設定：2つのレジスタ](#p3-2a)
  - [2-b. 複合系の状態空間](#p3-2b)
  - [2-c. ベクトルのテンソル積の定義](#p3-2c)
  - [2-d. 行列のテンソル積の定義](#p3-2d)
  - [2-e. (III-1)の証明](#p3-2e)
  - [2-f. 3つ以上のテンソル積](#p3-2f)
  - [2-g. どこまで分けられるか：分解の判定基準](#p3-2g)
- [3. M\_x^\*を各項に作用させる](#p3-3)
- [4. 線形性：和の各項に別々に作用させてよい](#p3-4)

<!-- part-toc:end -->

<a id="p3-1"></a>

## 1. 全体の状態は2つのレジスタのテンソル積

$|\Psi\rangle$の各項は$|x_i\rangle\otimes|f(x_i)\rangle$という、入力レジスタと結果レジスタのテンソル積です。$P_{x^\ast}$は入力レジスタの上の演算子なので、そのままでは全体の状態に作用させられません（例えば入力が2量子ビット、結果が1量子ビットなら、$P_{x^\ast}$は$4\times4$、全体の状態は8次元です）。

測定したいのは入力レジスタだけで、結果レジスタには何もしたくありません。そこで、結果レジスタには恒等演算子$I$を組み合わせて：

$$
M_{x^\ast}:=P_{x^\ast}\otimes I=|x^\ast\rangle\langle x^\ast|\otimes I
$$

と定義します。

<a id="p3-2"></a>

## 2. テンソル積の演算子は、それぞれのレジスタに別々に作用する

この節の目標は、次の式(III-1)を証明することです：

$$
(A\otimes B)\big(|u\rangle\otimes|v\rangle\big)=A|u\rangle\otimes B|v\rangle\tag{III-1}
$$

Part III §2-a〜Part III §2-dで記号とテンソル積を定義し、Part III §2-eで(III-1)を証明します。Part III §2-fでは3つ以上のテンソル積に広げ、Part III §2-gでは、どこまで分けて計算できるかを扱います。

<a id="p3-2a"></a>

### 2-a. 設定：2つのレジスタ

2つのレジスタの状態空間と、そこに属するベクトル、そこに作用する演算子を次のように宣言します：

$$
\mathcal H_A=\mathbb C^m,\qquad\mathcal H_B=\mathbb C^n,\qquad|u\rangle\in\mathcal H_A,\qquad|v\rangle\in\mathcal H_B,\qquad A\in\mathcal L(\mathcal H_A),\qquad B\in\mathcal L(\mathcal H_B)
$$

基底を固定すると$A\in\mathbb C^{m\times m}$、$B\in\mathbb C^{n\times n}$です。$A,B$は一般の線形演算子で、ユニタリである必要はありません（量子ゲートも射影演算子も、この議論に含まれます）。

**記法**：$\mathcal H_A$の計算基底を$|k\rangle_A$（$k=0,\dots,m-1$）、$\mathcal H_B$の計算基底を$|l\rangle_B$（$l=0,\dots,n-1$）と書き、それぞれ正規直交です：${}_A\langle k|k'\rangle_A=\delta_{kk'}$、${}_B\langle l|l'\rangle_B=\delta_{ll'}$。ベクトルを基底で展開して、その係数（成分）を$u_k,v_l\in\mathbb C$と書きます：

$$
|u\rangle=\sum_{k=0}^{m-1}u_k|k\rangle_A,\qquad|v\rangle=\sum_{l=0}^{n-1}v_l|l\rangle_B
$$

演算子の行列成分は$A_{kk'}$、$B_{ll'}$と書きます。

<a id="p3-2b"></a>

### 2-b. 複合系の状態空間

2つのレジスタを合わせた系の状態空間は、テンソル積で

$$
\mathcal H_{AB}:=\mathcal H_A\otimes\mathcal H_B\cong\mathbb C^{mn}
$$

と表されます（Part III §2-cで定義します）。$m$次元と$n$次元の空間から、$mn$次元の空間ができます。対応関係をまとめると：

| 対象 | 属する空間・写像 | 次元・大きさ |
|---|---|---|
| $\lvert u\rangle$ | $\mathcal H_A$ | $m$ |
| $\lvert v\rangle$ | $\mathcal H_B$ | $n$ |
| $\lvert u\rangle\otimes\lvert v\rangle$ | $\mathcal H_{AB}$ | $mn$ |
| $A$ | $\mathcal H_A\to\mathcal H_A$ | $m\times m$ |
| $B$ | $\mathcal H_B\to\mathcal H_B$ | $n\times n$ |
| $A\otimes B$ | $\mathcal H_{AB}\to\mathcal H_{AB}$ | $mn\times mn$ |

<a id="p3-2c"></a>

### 2-c. ベクトルのテンソル積の定義

**記法**：複合系の計算基底を$|k,l\rangle:=|k\rangle_A\otimes|l\rangle_B$と書きます。

テンソル積は、各因子について線形（**双線形**）であるように定義されます：

$$
(a|u_1\rangle+b|u_2\rangle)\otimes|v\rangle=a\,|u_1\rangle\otimes|v\rangle+b\,|u_2\rangle\otimes|v\rangle,\qquad|u\rangle\otimes(a|v_1\rangle+b|v_2\rangle)=a\,|u\rangle\otimes|v_1\rangle+b\,|u\rangle\otimes|v_2\rangle
$$

（これはテンソル積の定義の一部で、(III-1)のために新しく仮定したものではありません。）双線形性を左の因子、右の因子の順に使うと：

$$
|u\rangle\otimes|v\rangle=\Big(\sum_ku_k|k\rangle_A\Big)\otimes\Big(\sum_lv_l|l\rangle_B\Big)=\sum_ku_k\Big(|k\rangle_A\otimes\sum_lv_l|l\rangle_B\Big)=\sum_k\sum_lu_kv_l\,|k,l\rangle
$$

したがって、基底$|k,l\rangle$に対応する成分は：

$$
\boxed{\big(|u\rangle\otimes|v\rangle\big)_{(k,l)}=u_k\,v_l}\qquad(0\le k<m,\ 0\le l<n)
$$

これが「左の各成分に、右のベクトル全体を掛けて並べる（総当たりで成分同士の積を作る）」ことの式での表現です。

**成分の並べ方**：成分の番号を組$(k,l)$で表し、$(0,0),(0,1),\dots,(0,n-1),(1,0),\dots,(m-1,n-1)$の順（左の番号$k$を固定して、右の番号$l$を先に進める順）に並べます。普通の列ベクトルの番号$\alpha$（0から数える）との対応は：

$$
\alpha=kn+l
$$

です。$m=n=2$なら、$(0,0),(0,1),(1,0),(1,1)$がそれぞれ$\alpha=0,1,2,3$です。

**例**：$|0\rangle=(1,0)^T$、$|1\rangle=(0,1)^T$として、$|u\rangle=|1\rangle$（$u_0=0,u_1=1$）、$|v\rangle=|0\rangle$（$v_0=1,v_1=0$）とすると、成分は順に$u_0v_0=0$、$u_0v_1=0$、$u_1v_0=1$、$u_1v_1=0$なので：

$$
|1\rangle\otimes|0\rangle=(0,0,1,0)^T=|10\rangle
$$

**注意**：$|uv\rangle:=|u\rangle\otimes|v\rangle$という略記は、2つのレジスタの状態を並べたものです。複合系の一般の状態が、必ずこのような1つのテンソル積の形に書けるという意味ではありません（Part III §2-f-5）。

<a id="p3-2d"></a>

### 2-d. 行列のテンソル積の定義

$A\otimes B$は$mn\times mn$の行列で、行の番号を組$(k,l)$、列の番号を組$(k',l')$で表して、成分を

$$
\boxed{\big(A\otimes B\big)_{(k,l),(k',l')}:=A_{kk'}\,B_{ll'}}
$$

と定義します。これは、$A$の各成分に行列$B$全体を掛けて、ブロック状に並べることにあたります。$A,B$がともに$2\times2$なら：

$$
A\otimes B=\begin{pmatrix}A_{00}B&A_{01}B\\A_{10}B&A_{11}B\end{pmatrix}=\begin{pmatrix}A_{00}B_{00}&A_{00}B_{01}&A_{01}B_{00}&A_{01}B_{01}\\A_{00}B_{10}&A_{00}B_{11}&A_{01}B_{10}&A_{01}B_{11}\\A_{10}B_{00}&A_{10}B_{01}&A_{11}B_{00}&A_{11}B_{01}\\A_{10}B_{10}&A_{10}B_{11}&A_{11}B_{10}&A_{11}B_{11}\end{pmatrix}
$$

例えば、行$(0,1)$・列$(1,0)$の成分は$A_{01}B_{10}$で、成分を1から数える普通の行列表示では第2行・第3列（$a_{12}b_{21}$）にあたります。

<a id="p3-2e"></a>

### 2-e. (III-1)の証明

**証明したい式**：Part III §2の冒頭で掲げた

$$
(A\otimes B)\big(|u\rangle\otimes|v\rangle\big)=A|u\rangle\otimes B|v\rangle
$$

を、Part III §2-cとPart III §2-dの定義だけを使って証明します。

**方針**：2つのベクトルが等しいとは、次元が同じで、すべての成分が等しいことです。左辺は$mn\times mn$の行列$A\otimes B$と$mn$次元のベクトル$|u\rangle\otimes|v\rangle$の積なので$mn$次元、右辺は$m$次元のベクトル$A|u\rangle$と$n$次元のベクトル$B|v\rangle$のテンソル積なので$mn$次元で、次元は同じです。そこで、**右辺の第$(k,l)$成分と左辺の第$(k,l)$成分を別々に計算し、すべての$(k,l)$で一致することを示します。**

**右辺の第$(k,l)$成分**：Part III §2-cのベクトルのテンソル積の定義を、$A|u\rangle$と$B|v\rangle$という2つのベクトルに当てはめると、第$(k,l)$成分は「$A|u\rangle$の第$k$成分」と「$B|v\rangle$の第$l$成分」の積です。それぞれを行列とベクトルの積の定義（第$k$行と、ベクトルの成分を掛けて、すべての列について足す）で書くと：

$$
\Big[A|u\rangle\otimes B|v\rangle\Big]_{(k,l)}=(A|u\rangle)_k\,(B|v\rangle)_l=\Big(\sum_{k'=0}^{m-1}A_{kk'}u_{k'}\Big)\Big(\sum_{l'=0}^{n-1}B_{ll'}v_{l'}\Big)\tag{R}
$$

**左辺の第$(k,l)$成分**：

*ステップ1（行列とベクトルの積の定義）*：行列$M$と列ベクトル$\mathbf z$の積の第$\alpha$成分は$(M\mathbf z)_\alpha=\sum_\beta M_{\alpha\beta}z_\beta$です。今は$M=A\otimes B$、$\mathbf z=|u\rangle\otimes|v\rangle$で、行の番号$\alpha$は組$(k,l)$、列の番号$\beta$は組$(k',l')$なので、「すべての列について足す」は「すべての$k'$とすべての$l'$について足す」ことです：

$$
\Big[(A\otimes B)\big(|u\rangle\otimes|v\rangle\big)\Big]_{(k,l)}=\sum_{k'=0}^{m-1}\sum_{l'=0}^{n-1}\big(A\otimes B\big)_{(k,l),(k',l')}\,\big(|u\rangle\otimes|v\rangle\big)_{(k',l')}
$$

*ステップ2（定義を代入）*：Part III §2-dの$(A\otimes B)_{(k,l),(k',l')}=A_{kk'}B_{ll'}$と、Part III §2-cの$(|u\rangle\otimes|v\rangle)_{(k',l')}=u_{k'}v_{l'}$を代入します：

$$
=\sum_{k'=0}^{m-1}\sum_{l'=0}^{n-1}A_{kk'}B_{ll'}\,u_{k'}v_{l'}
$$

*ステップ3（2つの和に分ける）*：各成分は複素数なので、掛け算の順序を入れ替えて$\big(A_{kk'}u_{k'}\big)\big(B_{ll'}v_{l'}\big)$とします。前の括弧は$k'$にだけ依存し$l'$には依存せず、後の括弧は$l'$にだけ依存し$k'$には依存しません。そのため、分配法則を逆向きに使って：

$$
\Big[(A\otimes B)\big(|u\rangle\otimes|v\rangle\big)\Big]_{(k,l)}=\Big(\sum_{k'=0}^{m-1}A_{kk'}u_{k'}\Big)\Big(\sum_{l'=0}^{n-1}B_{ll'}v_{l'}\Big)\tag{L}
$$

（分配法則の向きは、例えば$(a_0+a_1)(b_0+b_1)=a_0b_0+a_0b_1+a_1b_0+a_1b_1$です。右辺の「すべての組の積の和」は、左辺の「和と和の積」に戻せます。）

**比較**：(L)と(R)の右辺は同じ式です。したがって、すべての$(k,l)$（$0\le k<m$、$0\le l<n$）について、左辺の第$(k,l)$成分と右辺の第$(k,l)$成分が等しくなります。

**結論**：次元が同じで、すべての成分が等しいので、

$$
\boxed{(A\otimes B)\big(|u\rangle\otimes|v\rangle\big)=A|u\rangle\otimes B|v\rangle}
$$

が成り立ちます。これで(III-1)が証明されました。

**補足**：ステップ1〜3（左辺の計算）だけを見ると、「テンソル積の行列とベクトルの積を、成分で書き直した」計算に見えます。それが右辺の成分(R)と一致することを確かめるところまでが、(III-1)の証明です。この証明は線形代数だけで、ボルン則のような量子力学の公理は使っていません。具体的な数値を入れて確かめると成り立つのは、ステップ3の「独立な2つの和が積に分かれる」ことを、各成分で見ていることにあたります。

<a id="p3-2f"></a>

### 2-f. 3つ以上のテンソル積

#### 2-f-1. 設定

3つのレジスタの状態空間を$\mathbb C^m$、$\mathbb C^n$、$\mathbb C^s$とし：

$$
|u\rangle\in\mathbb C^m,\quad|v\rangle\in\mathbb C^n,\quad|w\rangle\in\mathbb C^s,\qquad A\in\mathbb C^{m\times m},\quad B\in\mathbb C^{n\times n},\quad C\in\mathbb C^{s\times s}
$$

とします。合わせた系の状態空間は$\mathbb C^m\otimes\mathbb C^n\otimes\mathbb C^s\cong\mathbb C^{mns}$で、$A\otimes B\otimes C$は$mns\times mns$の行列です。成分の添字は$u_k$、$v_l$、$w_r$（$0\le k<m$、$0\le l<n$、$0\le r<s$）と書きます。

#### 2-f-2. 成分による定義

Part III §2-c、Part III §2-dと同じく、番号の3つの組で：

$$
\big(|u\rangle\otimes|v\rangle\otimes|w\rangle\big)_{(k,l,r)}:=u_kv_lw_r,\qquad\big(A\otimes B\otimes C\big)_{(k,l,r),(k',l',r')}:=A_{kk'}B_{ll'}C_{rr'}
$$

#### 2-f-3. 作用の式と証明

$$
\boxed{(A\otimes B\otimes C)\big(|u\rangle\otimes|v\rangle\otimes|w\rangle\big)=A|u\rangle\otimes B|v\rangle\otimes C|w\rangle}
$$

Part III §2-eと同じ方針で、左辺と右辺の第$(k,l,r)$成分を比べます。まず左辺の成分を計算します。ステップ1・2から：

$$
\sum_{k'}\sum_{l'}\sum_{r'}A_{kk'}B_{ll'}C_{rr'}\,u_{k'}v_{l'}w_{r'}
$$

掛け算を$\big(A_{kk'}u_{k'}\big)\big(B_{ll'}v_{l'}\big)\big(C_{rr'}w_{r'}\big)$と並べ替えると、3つの括弧はそれぞれ別の添字にだけ依存するので、3つの和の積に分かれます：

$$
=\Big(\sum_{k'}A_{kk'}u_{k'}\Big)\Big(\sum_{l'}B_{ll'}v_{l'}\Big)\Big(\sum_{r'}C_{rr'}w_{r'}\Big)=(A|u\rangle)_k\,(B|v\rangle)_l\,(C|w\rangle)_r
$$

一方、右辺の第$(k,l,r)$成分は、Part III §2-f-2のベクトルのテンソル積の定義を$A|u\rangle$、$B|v\rangle$、$C|w\rangle$に当てはめて$(A|u\rangle)_k\,(B|v\rangle)_l\,(C|w\rangle)_r$です。左辺と右辺の成分がすべての$(k,l,r)$で一致し、次元（$mns$）も同じなので、式が証明されました。4つ以上の場合も、和が個数分に分かれるだけで、同じ証明が成り立ちます。

#### 2-f-4. いくつかの量子ビットを1つのレジスタとしてまとめる

**括弧の位置**：成分で見ると$(u_kv_l)w_r=u_k(v_lw_r)$なので、$\big(|u\rangle\otimes|v\rangle\big)\otimes|w\rangle$と$|u\rangle\otimes\big(|v\rangle\otimes|w\rangle\big)$は同じ成分を持ちます。厳密には2つは自然な同型で対応する空間の元ですが、量子計算では同一視し、括弧を省略します。

**まとめて見る**：3つの1量子ビット$|u\rangle,|v\rangle,|w\rangle\in\mathbb C^2$について、**記法**：$|z\rangle:=|v\rangle\otimes|w\rangle\in\mathbb C^4$とおくと：

$$
|u\rangle\otimes|v\rangle\otimes|w\rangle=|u\rangle\otimes|z\rangle
$$

で、3量子ビットを「1量子ビットのレジスタ」と「2量子ビットのレジスタ」の2つのまとまりとして扱えます。演算子を$A\in\mathbb C^{2\times2}$、$B\in\mathbb C^{4\times4}$とすると$A\otimes B\in\mathbb C^{8\times8}$で、(III-1)から：

$$
(A\otimes B)\big(|u\rangle\otimes|v\rangle\otimes|w\rangle\big)=(A\otimes B)\big(|u\rangle\otimes|z\rangle\big)=A|u\rangle\otimes B|z\rangle=A|u\rangle\otimes B\big(|v\rangle\otimes|w\rangle\big)
$$

**前提**：行列の大きさと、作用させるベクトルの次元が一致している必要があります。$A$は2次元の$|u\rangle$に、$B$は4次元の$|v\rangle\otimes|w\rangle$に作用します。この先の計算は$B$の形で決まります（Part III §2-g）。

#### 2-f-5. 量子ビット数と状態空間の次元、積の形でない状態

1量子ビットの状態空間は$\mathbb C^2$、2量子ビットは$\mathbb C^2\otimes\mathbb C^2\cong\mathbb C^4$、3量子ビットは$\mathbb C^8$で、一般に$q$量子ビットでは$(\mathbb C^2)^{\otimes q}\cong\mathbb C^{2^q}$です：

| 量子ビット数 | 状態空間 | 次元 |
|---|---|---|
| 1 | $\mathbb C^2$ | 2 |
| 2 | $\mathbb C^4$ | 4 |
| 3 | $\mathbb C^8$ | 8 |
| $q$ | $\mathbb C^{2^q}$ | $2^q$ |

量子ビットが1つ増えるごとに、次元は2倍になります。量子ビットの個数と状態ベクトルの次元は別のもので、例えば2量子ビットの状態は4次元ベクトルです。

**積の形でない状態**：$q$量子ビットの一般の状態$|\psi\rangle=\sum_{j=0}^{2^q-1}\alpha_j|j\rangle$（$\sum_j|\alpha_j|^2=1$）は、各量子ビットの状態の1つのテンソル積に書けるとは限りません。例えば

$$
|\Phi^+\rangle:=\tfrac1{\sqrt2}\big(|00\rangle+|11\rangle\big)
$$

は、どんな1量子ビットの状態$|u\rangle,|v\rangle$を選んでも$|u\rangle\otimes|v\rangle$には等しくなりません。実際、$|u\rangle\otimes|v\rangle$の成分はPart III §2-cから$(u_0v_0,u_0v_1,u_1v_0,u_1v_1)$で、$|\Phi^+\rangle$の成分$(\tfrac1{\sqrt2},0,0,\tfrac1{\sqrt2})$と比べると、$u_0v_0\ne0$、$u_1v_1\ne0$から$u_0,v_1\ne0$なので$u_0v_1\ne0$となり、第2成分が$0$であることと矛盾します。このような状態を**エンタングルした状態**と呼びます。

**それでも$A\otimes B$は作用できる**：(III-1)は積の形の状態についての式ですが、一般の状態は積の形の状態（例えば基底$|j\rangle$）の和なので、線形性（Part III §4）で各項に(III-1)を使えます：

$$
(A\otimes B)|\Phi^+\rangle=\tfrac1{\sqrt2}\big((A\otimes B)|00\rangle+(A\otimes B)|11\rangle\big)=\tfrac1{\sqrt2}\big(A|0\rangle\otimes B|0\rangle+A|1\rangle\otimes B|1\rangle\big)
$$

#### 2-f-6. $n$個への一般化

**記号**：$n$個のテンソル積を、総積$\prod$にならって次のように書きます：

$$
\bigotimes_{i=1}^nA_i:=A_1\otimes A_2\otimes\cdots\otimes A_n,\qquad\bigotimes_{i=1}^n|u_i\rangle:=|u_1\rangle\otimes|u_2\rangle\otimes\cdots\otimes|u_n\rangle
$$

同じものを$n$個並べる場合は$V^{\otimes n}$と書きます（$V$はベクトル空間や行列などの、並べる対象です。記法と約束の$(\mathbb C^2)^{\otimes q}$がその例です）。行列のテンソル積は**クロネッカー積**とも呼ばれます。

**設定**：$|u_i\rangle\in\mathbb C^{d_i}$、$A_i\in\mathbb C^{d_i\times d_i}$（$i=1,\dots,n$）とします。**記法**：成分の番号の組を$\mathbf k:=(k_1,\dots,k_n)$（$0\le k_i<d_i$）と書き、$\mathbf k'=(k_1',\dots,k_n')$も同様とします。

**成分による定義**：Part III §2-c、Part III §2-d、Part III §2-f-2を$n$個に広げて：

$$
\Big(\bigotimes_{i=1}^n|u_i\rangle\Big)_{\mathbf k}:=\prod_{i=1}^n(u_i)_{k_i},\qquad\Big(\bigotimes_{i=1}^nA_i\Big)_{\mathbf k,\mathbf k'}:=\prod_{i=1}^n(A_i)_{k_ik_i'}
$$

**テンソル積の成分は、各因子の成分の普通の数の総積**です。「総当たりで成分同士を掛ける」ことが、$\prod$でそのまま書けます。成分の番号の組は$\mathbf k$の取り方の数だけあるので、次元は$\prod_{i=1}^nd_i$です（$q$量子ビットなら$2^q$）。

**補題（積の和は和の積）**：$a_1,\dots,a_n$を、それぞれ1つの添字の関数とします（$a_i$は添字$k_i'$の関数）。このとき：

$$
\sum_{k_1'}\sum_{k_2'}\cdots\sum_{k_n'}\ \prod_{i=1}^na_i(k_i')=\prod_{i=1}^n\Big(\sum_{k_i'}a_i(k_i')\Big)\tag{L$_n$}
$$

右辺の$\sum_{k_i'}a_i(k_i')$は、$a_i$の値をすべての添字について足した**1つの数**です。和の添字は「すべての値について足す」ための目印なので、どの文字で書いても同じ数を表しますが、ここでは文字を付け替えずに済むよう、左辺と同じ$k_i'$のまま書いています。

*証明*（$n$についての数学的帰納法）：次の2つを示します。

**(i) $n=1$のとき**：(L$_1$)の左辺は$\sum_{k_1'}a_1(k_1')$、右辺も$\sum_{k_1'}a_1(k_1')$で、一致します。

**(ii) $n-1$で成り立つなら、$n$でも成り立つ**：$n-1$のときの式（帰納法の仮定）は：

$$
\sum_{k_1'}\cdots\sum_{k_{n-1}'}\ \prod_{i=1}^{n-1}a_i(k_i')=\prod_{i=1}^{n-1}\Big(\sum_{k_i'}a_i(k_i')\Big)\tag{L$_{n-1}$}
$$

これを使って(L$_n$)を示します。

*ステップa（最後の因子を総積から外に出す）*：総積の定義から、$n$個の積は「$n-1$個の積」と「$n$個目の因子」の積です：

$$
\prod_{i=1}^na_i(k_i')=\Big[\prod_{i=1}^{n-1}a_i(k_i')\Big]\,a_n(k_n')
$$

*ステップb（一番内側の和の外に出す）*：(L$_n$)の左辺で、一番内側の和は$\sum_{k_n'}$です。ステップaの角括弧は$k_n'$を含まないので、$k_n'$について足すときは定数として扱えて、和の外に出せます（例えば$\sum_kc\,b(k)=c\sum_kb(k)$と同じです）：

$$
\sum_{k_1'}\cdots\sum_{k_{n-1}'}\sum_{k_n'}\Big[\prod_{i=1}^{n-1}a_i(k_i')\Big]a_n(k_n')=\sum_{k_1'}\cdots\sum_{k_{n-1}'}\Big[\prod_{i=1}^{n-1}a_i(k_i')\Big]\Big(\sum_{k_n'}a_n(k_n')\Big)
$$

*ステップc（残りの和の外に出す）*：$\sum_{k_n'}a_n(k_n')$は、$k_n'$についての和を取り終えた1つの数で、$k_1',\dots,k_{n-1}'$を含みません。したがって、残りの和$\sum_{k_1'}\cdots\sum_{k_{n-1}'}$にとっても定数で、すべての和の外に出せます：

$$
=\Big(\sum_{k_n'}a_n(k_n')\Big)\cdot\sum_{k_1'}\cdots\sum_{k_{n-1}'}\ \prod_{i=1}^{n-1}a_i(k_i')
$$

*ステップd（帰納法の仮定を使う）*：後ろの部分は(L$_{n-1}$)の左辺そのものなので、(L$_{n-1}$)の右辺に置き換えます：

$$
=\Big(\sum_{k_n'}a_n(k_n')\Big)\cdot\prod_{i=1}^{n-1}\Big(\sum_{k_i'}a_i(k_i')\Big)
$$

*ステップe（総積にまとめ直す）*：前の因子$\sum_{k_n'}a_n(k_n')$は、右辺の総積で$i=n$とした因子です。ステップaと逆向きに総積の定義を使うと：

$$
=\prod_{i=1}^n\Big(\sum_{k_i'}a_i(k_i')\Big)
$$

これは(L$_n$)の右辺です。したがって、(L$_{n-1}$)が成り立てば(L$_n$)も成り立ちます。

**結論**：(i)から$n=1$で成り立ち、(ii)から$n=1$で成り立てば$n=2$で、$n=2$で成り立てば$n=3$で、…と順に成り立つので、数学的帰納法により、すべての$n\ge1$で(L$_n$)が成り立ちます。$n=2$の場合が、Part III §2-eのステップ3です。

**(III-1)の一般化**：

$$
\boxed{\Big(\bigotimes_{i=1}^nA_i\Big)\Big(\bigotimes_{i=1}^n|u_i\rangle\Big)=\bigotimes_{i=1}^nA_i|u_i\rangle}
$$

*証明*：Part III §2-eと同じく、両辺の第$\mathbf k$成分を比べます。次元はどちらも$\prod_id_i$です。

左辺の第$\mathbf k$成分は、行列とベクトルの積の定義（すべての列$\mathbf k'$について足す）と、上の成分による定義から：

$$
\sum_{k_1'}\cdots\sum_{k_n'}\Big(\prod_{i=1}^n(A_i)_{k_ik_i'}\Big)\Big(\prod_{i=1}^n(u_i)_{k_i'}\Big)=\sum_{k_1'}\cdots\sum_{k_n'}\ \prod_{i=1}^n\Big[(A_i)_{k_ik_i'}(u_i)_{k_i'}\Big]
$$

（数の積は順序を入れ替えてよいので、同じ$i$の因子どうしをまとめました。）いま求めているのは第$\mathbf k$成分なので、$k_1,\dots,k_n$は固定された番号です。したがって角括弧は、添字$k_i'$だけの関数とみなせます。補題で$a_i(k_i'):=(A_i)_{k_ik_i'}(u_i)_{k_i'}$とおくと：

$$
=\prod_{i=1}^n\Big(\sum_{k_i'}(A_i)_{k_ik_i'}(u_i)_{k_i'}\Big)
$$

各因子の括弧は、行列とベクトルの積の定義（第$k_i$行とベクトルの成分を掛けて、すべての列$k_i'$について足す）から$A_i|u_i\rangle$の第$k_i$成分です：

$$
=\prod_{i=1}^n\big(A_i|u_i\rangle\big)_{k_i}
$$

右辺の第$\mathbf k$成分は、ベクトルのテンソル積の定義を$A_i|u_i\rangle$に当てはめて$\prod_{i=1}^n(A_i|u_i\rangle)_{k_i}$です。すべての$\mathbf k$で一致するので、式が証明されました。

#### 2-f-7. 順序について：$A\otimes B\ne B\otimes A$

**テンソル積は、一般に順序を入れ替えられません。** $\bigotimes_{i=1}^n$は「$i=1$から順に左から並べる」という意味です。

**例**：$X=\begin{pmatrix}0&1\\1&0\end{pmatrix}$（反転）として、$X\otimes I_2$と$I_2\otimes X$を$|00\rangle$に作用させると、(III-1)から：

$$
(X\otimes I_2)|00\rangle=X|0\rangle\otimes|0\rangle=|10\rangle,\qquad(I_2\otimes X)|00\rangle=|0\rangle\otimes X|0\rangle=|01\rangle
$$

結果が違うので$X\otimes I_2\ne I_2\otimes X$です。左に置いた因子は1つ目のレジスタに、右に置いた因子は2つ目のレジスタに作用するので、入れ替えると作用するレジスタが変わります。

**交換子との区別**：**記法**：行列の交換子を$[A,B]:=AB-BA$と書きます。交換子は**行列の積**の順序を入れ替えたときの差で、テンソル積の順序とは別のものです。上の例では$[X,I_2]=XI_2-I_2X=0$（行列の積としては可換）ですが、$X\otimes I_2\ne I_2\otimes X$です。

**恒等演算子の添字と作用する空間**：Part III §2-aで宣言した$A\in\mathbb C^{m\times m}$、$B\in\mathbb C^{n\times n}$に対して、$I_m$は$m\times m$、$I_n$は$n\times n$の単位行列です。添字は隣に書かれた行列の名前ではなく、**その因子が作用するレジスタの次元**を示します。したがって、$A\otimes I_n$は第1レジスタに$A$、第2レジスタに$I_n$を作用させ、$I_m\otimes B$は第1レジスタに$I_m$、第2レジスタに$B$を作用させます。どちらも$mn\times mn$の行列です。$A\otimes I_m$とすると一般には$m^2\times m^2$となり、ここで考える複合系とは次元が一致しません。$X$が$2\times2$行列の上の例では、両レジスタが2次元なので$I_2$を使いました。

**交換子で書ける事実**：別々のレジスタに作用する演算子は、行列の積として可換です。$A\in\mathbb C^{m\times m}$、$B\in\mathbb C^{n\times n}$について：

$$
\boxed{(A\otimes I_n)(I_m\otimes B)=A\otimes B=(I_m\otimes B)(A\otimes I_n)}
$$

これを(III-1)だけから導きます。

*準備（基底ベクトルに作用させると列が出てくる）*：複合系の基底ベクトル$|k\rangle\otimes|l\rangle$の成分は、Part III §2-cの定義から$(|k\rangle\otimes|l\rangle)_{(k',l')}=\delta_{kk'}\delta_{ll'}$で、第$(k,l)$成分だけが$1$、他は$0$です。行列$M$にこのベクトルを掛けると、行列とベクトルの積の定義から$M$の第$(k,l)$列だけが取り出されます。したがって、2つの$mn\times mn$行列が、すべての基底ベクトル$|k\rangle\otimes|l\rangle$に対して同じ結果を返せば、すべての列が一致するので、行列として等しくなります。

*左の式*：$(A\otimes I_n)(I_m\otimes B)$を$|k\rangle\otimes|l\rangle$に作用させます。行列の積は右から順に作用するので、まず$I_m\otimes B$を作用させ、(III-1)と$I_m|k\rangle=|k\rangle$を使うと：

$$
(I_m\otimes B)\big(|k\rangle\otimes|l\rangle\big)=|k\rangle\otimes B|l\rangle
$$

次に$A\otimes I_n$を作用させ、(III-1)と$I_n\big(B|l\rangle\big)=B|l\rangle$を使うと：

$$
(A\otimes I_n)\big(|k\rangle\otimes B|l\rangle\big)=A|k\rangle\otimes B|l\rangle
$$

*右の式*：$(I_m\otimes B)(A\otimes I_n)$も同様に、まず$A\otimes I_n$で$A|k\rangle\otimes|l\rangle$、次に$I_m\otimes B$で$A|k\rangle\otimes B|l\rangle$です。

*$A\otimes B$*：(III-1)から、$(A\otimes B)\big(|k\rangle\otimes|l\rangle\big)=A|k\rangle\otimes B|l\rangle$です。

3つの行列は、すべての基底ベクトル$|k\rangle\otimes|l\rangle$に対して同じ$A|k\rangle\otimes B|l\rangle$を返すので、準備から行列として等しく、上の式が成り立ちます。両端を引き算すると：

$$
\big[A\otimes I_n,\ I_m\otimes B\big]=(A\otimes I_n)(I_m\otimes B)-(I_m\otimes B)(A\otimes I_n)=0
$$

$A$と$B$自身が可換かどうか（そもそも大きさが違えば$AB$も定義されません）に関係なく成り立ちます。「1つ目のレジスタに$A$、2つ目に$B$を同時にかけること」は「片方ずつ、どちらの順番でかけても同じ」ということで、量子回路で別々の量子ビットに作用するゲートを順番に並べて描いてよいのは、このためです。

**括弧の位置は変えてよい**：一方、Part III §2-f-4で見た通り、成分で$(u_kv_l)w_r=u_k(v_lw_r)$なので、括弧の位置は変えてよく（結合法則にあたる）、$\bigotimes$は括弧なしで書けます。テンソル積は「順序は変えられないが、括弧は自由」という点で、行列の積と同じ性質を持っています。

**テンソル積どうしの積** $(U_1\otimes U_2)(V_1\otimes V_2)=U_1V_1\otimes U_2V_2$ は、同じ方法で示せます（付録C-1）。

<a id="p3-2g"></a>

### 2-g. どこまで分けられるか：分解の判定基準

#### 2-g-1. 判定基準

Part III §2-f-4の$B\big(|v\rangle\otimes|w\rangle\big)$を、さらに$|v\rangle$側と$|w\rangle$側に分けられるかどうかは、**行列$B$が$B=B_1\otimes B_2$（$B_1,B_2\in\mathbb C^{2\times2}$）の形に書けるかどうか**で決まります。書き方ではなく、行列そのものの性質です。

- **書ける場合**：(III-1)をもう一度使って$B\big(|v\rangle\otimes|w\rangle\big)=B_1|v\rangle\otimes B_2|w\rangle$なので、全体は

$$
(A\otimes B)\big(|u\rangle\otimes|v\rangle\otimes|w\rangle\big)=A|u\rangle\otimes B_1|v\rangle\otimes B_2|w\rangle
$$

- **書けない場合**：$B\big(|v\rangle\otimes|w\rangle\big)$を4次元のベクトルとしてそのまま計算します。計算はできますが、(III-1)を使って$B_1|v\rangle\otimes B_2|w\rangle$と演算子ごとに分けることはできません。ただし、特定の入力に対する出力が積状態になる可能性まで否定するものではありません。例えば$(I_2\otimes\mathrm{CNOT})\big(|u\rangle\otimes|v\rangle\otimes|w\rangle\big)=|u\rangle\otimes\mathrm{CNOT}\big(|v\rangle\otimes|w\rangle\big)$です。

#### 2-g-2. CNOTは$B_1\otimes B_2$の形に書けない

CNOTは$2\times2$のブロックで$\begin{pmatrix}I_2&0\\0&X\end{pmatrix}$（$X=\begin{pmatrix}0&1\\1&0\end{pmatrix}$）です。仮に$\mathrm{CNOT}=B_1\otimes B_2$と書けたとすると、Part III §2-dのブロック表示から

$$
\begin{pmatrix}(B_1)_{00}B_2&(B_1)_{01}B_2\\(B_1)_{10}B_2&(B_1)_{11}B_2\end{pmatrix}=\begin{pmatrix}I_2&0\\0&X\end{pmatrix}
$$

です。左上のブロックから$(B_1)_{00}B_2=I_2$なので$(B_1)_{00}\ne0$で、$B_2=\frac1{(B_1)_{00}}I_2$です。右下のブロックから$(B_1)_{11}B_2=X$で、これに$B_2$を代入すると$X=\frac{(B_1)_{11}}{(B_1)_{00}}I_2$となります。しかし$X$は対角成分が$0$で非対角成分が$1$なので、単位行列の定数倍にはなりません。これは矛盾なので、CNOTは$B_1\otimes B_2$の形に書けません。

#### 2-g-3. 恒等演算子を付けても、$B$自体は分けられない

$B\in\mathbb C^{4\times4}$に恒等演算子を付けた$B\otimes I_2$は$8\times8$の行列で、3量子ビットに作用する**別の演算子**です（「2量子ビットに$B$をかけ、もう1つの量子ビットには何もしない」という意味）。$B$自身とは大きさが違うので等しくなく、$B$の中身（$|v\rangle$と$|w\rangle$をどう混ぜるか）も変わらないため、$|v\rangle$側と$|w\rangle$側に分けることにはなりません。

一方、**全体の演算子$A\otimes B$は、恒等演算子を使って行列の積に分解できます**。Part III §2-f-7で$m=2$、$n=4$として導いた通り、

$$
(A\otimes I_4)(I_2\otimes B)=A\otimes B=(I_2\otimes B)(A\otimes I_4)
$$

です。ただし、この分解でも$B$は$I_2\otimes B$の中にまとまったままで、$|v\rangle$と$|w\rangle$には分かれません。

#### 2-g-4. このノートの$M_{x^\ast}$との対応

入力レジスタが2量子ビット、結果レジスタが1量子ビットなら、$\mathcal H_A=\mathbb C^4$、$\mathcal H_B=\mathbb C^2$で、$|x_i\rangle\in\mathbb C^4$、$|f(x_i)\rangle\in\mathbb C^2$、$|x_i\rangle\otimes|f(x_i)\rangle\in\mathbb C^8$です。射影演算子は$P_{x^\ast}\in\mathbb C^{4\times4}$、結果レジスタには$I_2\in\mathbb C^{2\times2}$を組み合わせて：

$$
M_{x^\ast}=P_{x^\ast}\otimes I_2\in\mathbb C^{8\times8}
$$

これはPart III §2-f-4の「まとめて見る」形で、$P_{x^\ast}$は入力レジスタの2量子ビットにまとめて作用し、$I_2$は結果レジスタに作用します。$P_{x^\ast}$を1量子ビットずつに分けるかどうか（Part III §2-g-1）は、この計算には必要ありません。各項への作用はPart III §3で、和で書かれた$|\Psi\rangle$全体への作用はPart III §4の線形性で扱います。

<a id="p3-3"></a>

## 3. $M_{x^\ast}$を各項に作用させる

(III-1)で$A=P_{x^\ast}$、$B=I$、$|u\rangle=|x_i\rangle$、$|v\rangle=|f(x_i)\rangle$とし、Part IIの結果と$I|f(x_i)\rangle=|f(x_i)\rangle$を使います：

$$
M_{x^\ast}\big(|x_i\rangle|f(x_i)\rangle\big)=\big(P_{x^\ast}|x_i\rangle\big)\otimes\big(I|f(x_i)\rangle\big)=\delta_{x^\ast,x_i}\,|x^\ast\rangle|f(x_i)\rangle\tag{III-2}
$$

**入力が正解の項だけを残し、結果レジスタはそのまま保ちます。**

<a id="p3-4"></a>

## 4. 線形性：和の各項に別々に作用させてよい

$M_{x^\ast}$は行列なので、行列の積の分配法則から、ベクトル$|u\rangle,|v\rangle$と数$a,b$について

$$
M_{x^\ast}\big(a|u\rangle+b|v\rangle\big)=a\,M_{x^\ast}|u\rangle+b\,M_{x^\ast}|v\rangle
$$

が成り立ちます（線形性）。これを繰り返し使うと、和についても

$$
M_{x^\ast}\Big(\sum_ic_i|v_i\rangle\Big)=\sum_ic_i\,M_{x^\ast}|v_i\rangle
$$

です。これは$M_{x^\ast}$が射影演算子であることとは関係なく、行列で表されるすべての演算子（量子ゲートを含む）について成り立つ性質です。

---

---

<a id="p4"></a>

# Part IV：確率は、取り出した成分のノルムの2乗（ボルン則）

<!-- part-toc:start -->

**この Part の内容**

- [1. 一般の状態の展開](#p4-1)
- [2. 仮定：ボルン則](#p4-2)
- [3. 入力レジスタだけを測定する場合](#p4-3)
- [4. 成分を取り出す](#p4-4)
- [5. テンソル積の内積](#p4-5)
- [6. ノルムの2乗を計算する](#p4-6)
- [7. 結論](#p4-7)

<!-- part-toc:end -->

ここで、なぜ「成分を取り出してノルムの2乗を取る」と確率になるのかを導きます。

<a id="p4-1"></a>

## 1. 一般の状態の展開

入力レジスタと結果レジスタを合わせた一般の状態を、計算基底で

$$
|\Phi\rangle=\sum_{x,y}c_{x,y}\,|x\rangle|y\rangle
$$

と展開します（$x$は入力、$y$は結果の基底ラベル、$c_{x,y}$は複素数の係数）。

<a id="p4-2"></a>

## 2. 仮定：ボルン則

**全体を計算基底で測定したとき、$(x,y)$が得られる確率は$|c_{x,y}|^2$である。** これは量子力学の公理（ボルン則）で、このノートで物理の仮定を使うのはここだけです。

<a id="p4-3"></a>

## 3. 入力レジスタだけを測定する場合

入力が$x$になるのは、結果レジスタの値$y$が何であっても$(x,y)$が出た場合です。これらは互いに重ならない（同時には起こらない）ので、確率を足し合わせて：

$$
P(x)=\sum_y|c_{x,y}|^2\tag{IV-1}
$$

<a id="p4-4"></a>

## 4. 成分を取り出す

Part III §3の計算は、候補$x_i$に限らず一般の基底$|x'\rangle|y\rangle$でも同じなので、$P_x:=|x\rangle\langle x|$について

$$
(P_x\otimes I)\,|x'\rangle|y\rangle=\delta_{x,x'}\,|x\rangle|y\rangle
$$

です。Part III §4の線形性で$|\Phi\rangle$の和の各項に作用させます：

$$
(P_x\otimes I)|\Phi\rangle=\sum_{x',y}c_{x',y}\,\delta_{x,x'}\,|x\rangle|y\rangle
$$

$\delta_{x,x'}$は$x'=x$のときだけ$1$なので、$x'$についての和は$x'=x$の項だけが残ります：

$$
(P_x\otimes I)|\Phi\rangle=\sum_yc_{x,y}\,|x\rangle|y\rangle
$$

<a id="p4-5"></a>

## 5. テンソル積の内積

ノルムを計算する準備として、テンソル積同士の内積を求めます：

$$
\big(\langle a|\langle b|\big)\big(|c\rangle|d\rangle\big)=\langle a|c\rangle\,\langle b|d\rangle\tag{IV-2}
$$

**導出**：ブラは、ケットの成分を複素共役にして横に並べたものです。$|a\rangle|b\rangle$の成分は$a_kb_l$なので、そのブラの成分は$a_k^\ast b_l^\ast$です。内積は対応する成分の積の和なので：

$$
\sum_{k,l}a_k^\ast b_l^\ast\,c_kd_l=\Big(\sum_ka_k^\ast c_k\Big)\Big(\sum_lb_l^\ast d_l\Big)=\langle a|c\rangle\langle b|d\rangle
$$

（ここでも$k$と$l$の和が独立に分かれます。）

<a id="p4-6"></a>

## 6. ノルムの2乗を計算する

Part IV §4のベクトルを$|w\rangle:=\sum_yc_{x,y}|x\rangle|y\rangle$とおき、ノルムの2乗$\|w\|^2:=\langle w|w\rangle$を計算します。ブラは係数を複素共役にして$\langle w|=\sum_{y}c_{x,y}^\ast\,\langle x|\langle y|$です。2つの和は別々の文字$y,y'$で書きます：

$$
\langle w|w\rangle=\sum_y\sum_{y'}c_{x,y}^\ast\,c_{x,y'}\,\big(\langle x|\langle y|\big)\big(|x\rangle|y'\rangle\big)
$$

(IV-2)と正規直交性から$\big(\langle x|\langle y|\big)\big(|x\rangle|y'\rangle\big)=\langle x|x\rangle\langle y|y'\rangle=1\cdot\delta_{y,y'}$なので、$y'=y$の項だけが残り：

$$
\big\|(P_x\otimes I)|\Phi\rangle\big\|^2=\sum_yc_{x,y}^\ast c_{x,y}=\sum_y|c_{x,y}|^2
$$

<a id="p4-7"></a>

## 7. 結論

(IV-1)と見比べると：

$$
\boxed{P(x)=\big\|(P_x\otimes I)|\Phi\rangle\big\|^2}
$$

**取り出した成分のノルムの2乗が、入力レジスタの測定確率です。** 物理の仮定はボルン則（Part IV §2）だけで、それ以外は線形代数から導かれています。

（なお、Part IIの$P_x^\dagger=P_x$、$P_x^2=P_x$と、$I^\dagger=I$、$I^2=I$から$(P_x\otimes I)^\dagger(P_x\otimes I)=P_x\otimes I$となるので、$\|(P_x\otimes I)|\Phi\rangle\|^2=\langle\Phi|(P_x\otimes I)|\Phi\rangle$とも書けます。）この形から、全部の$x$について確率を足すと$1$になること、測定した後の状態がどうなるかは、付録A（A-1、A-2）で扱います。

---

<a id="p5"></a>

# Part V：$|\Psi\rangle$に当てはめる

Part III §4の線形性で、$M_{x^\ast}$をPart Iの$|\Psi\rangle$の和の各項に作用させます：

$$
M_{x^\ast}|\Psi\rangle=M_{x^\ast}\Big(\frac1{\sqrt N}\sum_{i=1}^N|x_i\rangle|f(x_i)\rangle\Big)=\frac1{\sqrt N}\sum_{i=1}^NM_{x^\ast}\big(|x_i\rangle|f(x_i)\rangle\big)
$$

各項に(III-2)を代入します：

$$
M_{x^\ast}|\Psi\rangle=\frac1{\sqrt N}\sum_{i=1}^N\delta_{x^\ast,x_i}\,|x^\ast\rangle|f(x_i)\rangle
$$

和を書き出すと、

$$
\frac1{\sqrt N}\Big(\delta_{x^\ast,x_1}|x^\ast\rangle|f(x_1)\rangle+\delta_{x^\ast,x_2}|x^\ast\rangle|f(x_2)\rangle+\cdots+\delta_{x^\ast,x_N}|x^\ast\rangle|f(x_N)\rangle\Big)
$$

です。$x_1,\dots,x_N$はすべて異なり、正解$x^\ast$はその中にちょうど1つあるので、$\delta_{x^\ast,x_i}=1$となる$i$はただ1つで、他の項はすべてゼロです。残る項では$x_i=x^\ast$なので$f(x_i)=f(x^\ast)$です：

$$
\boxed{M_{x^\ast}|\Psi\rangle=\frac1{\sqrt N}\,|x^\ast\rangle|f(x^\ast)\rangle}
$$

---

<a id="p6"></a>

# Part VI：ノルムの2乗を取る

Part IV §7から、$P(x^\ast)=\|M_{x^\ast}|\Psi\rangle\|^2$です。Part Vのベクトルのブラは、係数$\frac1{\sqrt N}$を複素共役にしたもの（実数なのでそのまま）を使って$\frac1{\sqrt N}\langle x^\ast|\langle f(x^\ast)|$です：

$$
P(x^\ast)=\frac1{\sqrt N}\cdot\frac1{\sqrt N}\,\big(\langle x^\ast|\langle f(x^\ast)|\big)\big(|x^\ast\rangle|f(x^\ast)\rangle\big)
$$

(IV-2)から、括弧の部分は$\langle x^\ast|x^\ast\rangle\,\langle f(x^\ast)|f(x^\ast)\rangle$で、どちらも規格化された基底ベクトルなので$1\cdot1=1$です。したがって：

$$
\boxed{P(x^\ast)=\frac1N}
$$

---

<a id="p7"></a>

# Part VII：一般の入力の場合

入力が均等な重ね合わせでなく

$$
\sum_{i=1}^N\alpha_i|x_i\rangle,\qquad\sum_{i=1}^N|\alpha_i|^2=1
$$

の場合、$U_f$をかけた後の状態は（線形性から）$\sum_i\alpha_i|x_i\rangle|f(x_i)\rangle$です。Part Vの$\frac1{\sqrt N}$が$\alpha_i$に置き換わるだけなので、Part Vと同じ計算で$M_{x^\ast}$を作用させると$\alpha_{x^\ast}|x^\ast\rangle|f(x^\ast)\rangle$が残り（$\alpha_{x^\ast}$は$x_i=x^\ast$となる$i$の$\alpha_i$）、Part VIと同じ計算でノルムの2乗は（$\alpha_{x^\ast}$は一般に複素数なので$\alpha_{x^\ast}^\ast\alpha_{x^\ast}$として）：

$$
\boxed{P(x^\ast)=|\alpha_{x^\ast}|^2}
$$

これは、$U_f$をかける前に入力レジスタを測定した場合の確率と同じです。**$U_f$は各候補に$|f(x_i)\rangle$というラベルを付けるだけで、入力の振幅$\alpha_i$を変えない**ので、関数を計算しても正解の確率は増えません。均等な重ね合わせでは$\alpha_{x^\ast}=\frac1{\sqrt N}$なので$\frac1N$です。正解の確率を大きくするには、振幅$\alpha_i$そのものを動かす別の操作（グローバー探索の位相オラクルと拡散演算子）が必要です。

なお、入力レジスタを**単独で**測る確率は変わりませんが、結果レジスタとの間には相関が生まれます（均等な重ね合わせでは、$f$ が定数でなければ、$U_f$ は入力と結果をエンタングルさせる。一般の振幅では、振幅がゼロでない入力の上で $f$ が**複数の値を取る場合に限って**相関が生まれます。たとえば入力が $|0\rangle$ だけなら、非定数の $f$ でも出力は $|0\rangle|f(0)\rangle$ の積状態です。付録B-3）。結果レジスタを測ると入力レジスタの状態が変わることは、付録B（B-2、B-3）で扱います。

---

<a id="p8"></a>

# Part VIII：数値例：4候補・正解1個

<!-- part-toc:start -->

**この Part の内容**

- [1. 設定](#p8-1)
- [2. 列ベクトルで書く](#p8-2)
- [3. 射影演算子を行列で書く](#p8-3)
- [4. 状態に作用させる（Part Vの確認）](#p8-4)
- [5. ノルムの2乗（Part VIの確認）](#p8-5)
- [6. 他の候補](#p8-6)

<!-- part-toc:end -->

<a id="p8-1"></a>

## 1. 設定

候補は$x\in\{00,01,10,11\}$（$N=4$、入力レジスタは2量子ビット）、正解は$x^\ast=11$、関数は正解に印を付ける

$$
f(x)=\begin{cases}1&(x=11)\\0&(x\ne11)\end{cases}
$$

とします（結果レジスタは1量子ビット）。Part Iの状態は：

$$
|\Psi\rangle=\tfrac12\big(|00\rangle|0\rangle+|01\rangle|0\rangle+|10\rangle|0\rangle+|11\rangle|1\rangle\big)=\tfrac12\big(|000\rangle+|010\rangle+|100\rangle+|111\rangle\big)
$$

（最初の2文字が入力、最後の1文字が結果です。）

<a id="p8-2"></a>

## 2. 列ベクトルで書く

2量子ビットの基底を$|00\rangle,|01\rangle,|10\rangle,|11\rangle$の順に並べると$|11\rangle=(0,0,0,1)^T$です。3量子ビットの基底を$|000\rangle,|001\rangle,|010\rangle,|011\rangle,|100\rangle,|101\rangle,|110\rangle,|111\rangle$の順に並べると、$|\Psi\rangle$に現れるのは1番目、3番目、5番目、8番目なので：

$$
|\Psi\rangle=\tfrac12\begin{pmatrix}1&0&1&0&1&0&0&1\end{pmatrix}^T
$$

<a id="p8-3"></a>

## 3. 射影演算子を行列で書く

Part IIの定義から、$P_{11}$はケット（縦ベクトル）とブラ（横ベクトル）の積です：

$$
P_{11}=|11\rangle\langle11|=\begin{pmatrix}0\\0\\0\\1\end{pmatrix}\begin{pmatrix}0&0&0&1\end{pmatrix}=\begin{pmatrix}0&0&0&0\\0&0&0&0\\0&0&0&0\\0&0&0&1\end{pmatrix}
$$

（第$(k,l)$成分は、縦ベクトルの第$k$成分と横ベクトルの第$l$成分の積で、$k=l=4$のときだけ$1$です。）

Part IIIの$M_{11}=P_{11}\otimes I_2$（$I_2$は$2\times2$の単位行列）は、Part III §2の行列のテンソル積の定義から、$P_{11}$の各成分に$I_2$を掛けて並べた$8\times8$行列です。$P_{11}$でゼロでない成分は$(4,4)$成分の$1$だけなので、右下の$2\times2$のブロックだけが$1\cdot I_2$になります：

$$
M_{11}=\begin{pmatrix}0&0&0&0&0&0&0&0\\0&0&0&0&0&0&0&0\\0&0&0&0&0&0&0&0\\0&0&0&0&0&0&0&0\\0&0&0&0&0&0&0&0\\0&0&0&0&0&0&0&0\\0&0&0&0&0&0&1&0\\0&0&0&0&0&0&0&1\end{pmatrix}
$$

第7行7列と第8行8列が$1$なのは、入力レジスタが$11$である基底が、7番目の$|110\rangle$と8番目の$|111\rangle$の2つだからです。

![P11 ⊗ I2 の行列](figures/mp02_block_matrix.png)

*$P_{11}$（$4\times4$）の各成分に $I_2$ を掛けて並べると $M_{11}$（$8\times8$）になる。$P_{11}$ の $(4,4)$ 成分だけが $1$ なので、右下の $2\times2$ のブロックだけが $I_2$ で、ほかはすべてゼロ。図を描くときに、$M_{11}=P_{11}\otimes I_2$ の対角が $(0,0,0,0,0,0,1,1)$ であることを確かめています。*

<a id="p8-4"></a>

## 4. 状態に作用させる（Part Vの確認）

**行列の積で**：$M_{11}$は第7成分と第8成分だけを残し、他をゼロにします。$|\Psi\rangle$の第7成分は$0$、第8成分は$\frac12$なので：

$$
M_{11}|\Psi\rangle=\tfrac12\begin{pmatrix}0&0&0&0&0&0&0&1\end{pmatrix}^T=\tfrac12|111\rangle
$$

**各項ごとに**（Part III §4の線形性と(III-2)で）：

$$
M_{11}|\Psi\rangle=\tfrac12\big(M_{11}|00\rangle|0\rangle+M_{11}|01\rangle|0\rangle+M_{11}|10\rangle|0\rangle+M_{11}|11\rangle|1\rangle\big)
$$

$\delta_{11,00}=\delta_{11,01}=\delta_{11,10}=0$、$\delta_{11,11}=1$なので、最初の3項はゼロ、最後の項は$|11\rangle|1\rangle=|111\rangle$で：

$$
M_{11}|\Psi\rangle=\tfrac12|111\rangle
$$

2つの計算は一致し、Part Vの式$\frac1{\sqrt N}|x^\ast\rangle|f(x^\ast)\rangle$で$N=4$、$x^\ast=11$、$f(x^\ast)=1$としたものにもなっています。

<a id="p8-5"></a>

## 5. ノルムの2乗（Part VIの確認）

$$
P(11)=\big\|\tfrac12|111\rangle\big\|^2=\tfrac12\cdot\tfrac12\,\langle111|111\rangle=\tfrac14\cdot1=\tfrac14
$$

Part VIの$\frac1N$で$N=4$としたものと一致します。

<a id="p8-6"></a>

## 6. 他の候補

Part IV §3の(IV-1)で、入力が各値になる基底の係数を数えると：

| 入力$x$ | 該当する基底 | 係数 | 確率 |
|---|---|---|---|
| $00$ | $\lvert000\rangle$、$\lvert001\rangle$ | $\tfrac12$、$0$ | $\tfrac14$ |
| $01$ | $\lvert010\rangle$、$\lvert011\rangle$ | $\tfrac12$、$0$ | $\tfrac14$ |
| $10$ | $\lvert100\rangle$、$\lvert101\rangle$ | $\tfrac12$、$0$ | $\tfrac14$ |
| $11$ | $\lvert110\rangle$、$\lvert111\rangle$ | $0$、$\tfrac12$ | $\tfrac14$ |

4つの候補の確率はすべて$\frac14$で、合計は$1$です。関数の値をすべての候補について計算したにもかかわらず、正解の確率はランダムに1つ選ぶのと同じ$\frac14$のままです。

![状態の成分と確率](figures/mp03_amplitudes.png)

*左：$|\Psi\rangle$ の8成分（橙は入力が $11$ の基底）。中：$M_{11}|\Psi\rangle=\frac12|111\rangle$（入力が $11$ の成分だけが残る）。右：入力 $x$ の確率はどれも $\frac14=\frac1N$。図を描くときに、成分と確率を本文の式で確かめています。*

**この先**：入力レジスタを測った**後**の状態は付録A（A-2）、結果レジスタを測るとどうなるか、$|\Psi\rangle$ がどれだけエンタングルしているかは付録B、教科書の式と Qiskit の並び順の違いは付録Cで扱います。

---

<a id="summary"></a>

# まとめ

1. Part II：$P_{x^\ast}=|x^\ast\rangle\langle x^\ast|$は、正解の基底成分だけを残す（正規直交性から）。
2. Part III：$M_{x^\ast}=P_{x^\ast}\otimes I$は、入力が正解の項だけを残し、結果レジスタはそのまま保つ（$(A\otimes B)(|u\rangle\otimes|v\rangle)=A|u\rangle\otimes B|v\rangle$から）。和には線形性で各項に作用させる。
3. Part IV：取り出した成分のノルムの2乗が確率（ボルン則と、テンソル積の内積$\big(\langle a|\langle b|\big)\big(|c\rangle|d\rangle\big)=\langle a|c\rangle\langle b|d\rangle$から）。物理の仮定はボルン則だけ。
4. Part V：$|\Psi\rangle$の和の各項に作用させると、$\delta_{x^\ast,x_i}$で正解の1項だけが残り$\frac1{\sqrt N}|x^\ast\rangle|f(x^\ast)\rangle$。
5. Part VI：そのノルムの2乗が$P(x^\ast)=\frac1N$。
6. Part VII：一般の入力では$P(x^\ast)=|\alpha_{x^\ast}|^2$で、$U_f$は入力の振幅を変えない。
7. Part VIII：4候補の例で、行列$P_{11}\otimes I_2$（第7・第8対角成分だけが1）を使って$\frac14$になることを確認。

---

<a id="appA"></a>

# 付録A：完全な射影測定、測定後の状態、POVM

<!-- part-toc:start -->

**この付録の内容**

- [A-1. 完全性：確率の和が1になる](#A-1)
- [A-2. 測定後の状態（射影仮説）](#A-2)
- [A-3. 同じ測定をもう一度すると](#A-3)
- [A-4. 一般の測定と POVM](#A-4)

<!-- part-toc:end -->

本編は、「入力が $x^\ast$ になる確率」だけを求めました。ここでは、(1) 入力レジスタのすべての値についての測定をまとめて見ると確率の和が $1$ になること、(2) 測定した**後**の状態、(3) 射影測定をさらに一般にした測定（POVM）を扱います。

**前提**：この付録では、入力レジスタの全基底 $|0\rangle,\dots,|N-1\rangle$（$N=2^q$）について考えます（本編の候補 $x_1,\dots,x_N$ が全基底にあたる場合です）。$P_x:=|x\rangle\langle x|$、$M_x:=P_x\otimes I$（$I$ は結果レジスタ上の恒等演算子）です。

<a id="A-1"></a>

## A-1. 完全性：確率の和が1になる

**(a) $M_x$ どうしは直交する**：

$$
M_xM_{x'}=\delta_{xx'}\,M_x\tag{A-1}
$$

**証明**：付録C-1の式 $(U_1\otimes U_2)(V_1\otimes V_2)=U_1V_1\otimes U_2V_2$ で $U_1=P_x$、$V_1=P_{x'}$、$U_2=V_2=I$ とすると $M_xM_{x'}=P_xP_{x'}\otimes I$ です。$P_xP_{x'}=|x\rangle\langle x|x'\rangle\langle x'|=\delta_{xx'}|x\rangle\langle x|$（正規直交性 $\langle x|x'\rangle=\delta_{xx'}$）なので、$M_xM_{x'}=\delta_{xx'}P_x\otimes I=\delta_{xx'}M_x$ です。

**(b) 足すと恒等演算子になる**：テンソル積は各因子について線形（Part III §2-c の双線形性）なので、

$$
\sum_xM_x=\Big(\sum_xP_x\Big)\otimes I=I_N\otimes I=I\tag{A-2}
$$

です。ここで $\sum_x|x\rangle\langle x|=I_N$（正規直交基底の**完全性関係**。$|\psi\rangle=\sum_x|x\rangle\langle x|\psi\rangle$ と書けることの言い換え）を使いました。

**(c) 確率の和**：Part IV §7 の括弧書きの式 $P(x)=\langle\Phi|M_x|\Phi\rangle$ を $x$ について足し、(A-2) を使うと

$$
\sum_xP(x)=\Big\langle\Phi\Big|\Big(\sum_xM_x\Big)\Big|\Phi\Big\rangle=\langle\Phi|\Phi\rangle=1\tag{A-3}
$$

です。本編の $P(x)=\sum_y|c_{x,y}|^2$ を $x$ で足して $\sum_{x,y}|c_{x,y}|^2=\langle\Phi|\Phi\rangle=1$ としても、同じことです（Part IV §3）。**射影演算子の完全系（直交し、足すと $I$）が、「起こりうる結果の確率を足すとちょうど $1$」を保証しています。**

<a id="A-2"></a>

## A-2. 測定後の状態（射影仮説）

本編で使った物理の仮定は、ボルン則（Part IV §2）だけでした。測定した**後**の状態を決めるには、もう1つ仮定が要ります。

**仮定（射影仮説）**：入力レジスタの測定で $x$ が得られたとき、測定直後の状態は

$$
|\Phi_x\rangle:=\frac{M_x|\Phi\rangle}{\sqrt{P(x)}}\tag{A-4}
$$

になる（$P(x)>0$ のとき）。

**規格化の確認**：$P(x)=\|M_x\Phi\|^2$ なので、$\|\Phi_x\|^2=\dfrac{\|M_x\Phi\|^2}{P(x)}=1$ です。$\sqrt{P(x)}$ で割るのは、射影した状態の長さが $\sqrt{P(x)}<1$ に縮んでいるのを、$1$ に戻すためです。

**例（Part VIII の $|\Psi\rangle$）**：Part V の結果から $M_{11}|\Psi\rangle=\tfrac12|111\rangle$、$P(11)=\tfrac14$ なので

$$
|\Psi_{11}\rangle=\frac{\tfrac12|111\rangle}{\sqrt{1/4}}=|11\rangle|1\rangle
$$

です。ほかの入力も同様に、$|\Psi_{00}\rangle=|00\rangle|0\rangle$、$|\Psi_{01}\rangle=|01\rangle|0\rangle$、$|\Psi_{10}\rangle=|10\rangle|0\rangle$ で、測定後は**積状態**になります（結果レジスタは、入力に対応する $|f(x)\rangle$ に決まる）。一般の振幅 $\alpha_x$ の場合は $\alpha_x/|\alpha_x|$ が全体の位相として残りますが、全体の位相は状態を変えません（図 A-1 の左上と右上：$|\alpha_i|^2=0.1,0.2,0.3,0.4$ の例で、$10$ を測ると確率 $0.3$ で $|10\rangle|0\rangle$ になる）。

![測定後の状態と、誤差のある測定](figures/mp04_post_measurement.png)

*図 A-1。左上：測定前の $|c|^2$（$|\alpha_i|^2=0.1,0.2,0.3,0.4$、$f$ は Part VIII と同じ）。右上：入力を測って $10$ が出たとき（確率 $0.3$）、状態は $|10\rangle|0\rangle$ になる。左下：結果レジスタを測って $0$ が出たとき（確率 $0.6$、付録B-2）、入力は $|00\rangle,|01\rangle,|10\rangle$ の重ね合わせ（$|c|^2$ は $0.1:0.2:0.3$ の比）に残る。右下：誤差 $\epsilon$ のある $Z$ 測定（A-4）で、結果 $0$ の確率が $\epsilon>0$ では $1$ にも $0$ にも届かない。図を描くときに、これらの確率と状態を本文の式で確かめています。*

<a id="A-3"></a>

## A-3. 同じ測定をもう一度すると

(A-4) の状態に、同じ測定をもう一度行います。$M_x^2=M_x$ ((A-1) で $x=x'$) なので、

$$
M_x|\Phi_x\rangle=\frac{M_x^2|\Phi\rangle}{\sqrt{P(x)}}=|\Phi_x\rangle,\qquad\|M_x\Phi_x\|^2=1
$$

で、2回目も同じ $x$ が**確率 $1$** で出ます。別の $x'\ne x$ については $M_{x'}M_x=0$ ((A-1)) なので、確率は $0$ です。**測定は再現できる**、というのが射影測定の性質です。

<a id="A-4"></a>

## A-4. 一般の測定と POVM

射影測定は、測定の演算子 $M_x$ が $M_x^2=M_x=M_x^\dagger$（射影演算子）という強い条件を満たす場合です。条件をゆるめて、

$$
\sum_mK_m^\dagger K_m=I\tag{A-5}
$$

を満たす演算子の組 $\{K_m\}$ を、**測定演算子**として一般に扱えます。結果 $m$ の確率と測定後の状態は

$$
P(m)=\|K_m\Phi\|^2=\langle\Phi|K_m^\dagger K_m|\Phi\rangle,\qquad|\Phi_m\rangle=\frac{K_m|\Phi\rangle}{\sqrt{P(m)}}\tag{A-6}
$$

です。(A-5) は、$\sum_mP(m)=\langle\Phi|\sum_mK_m^\dagger K_m|\Phi\rangle=1$ にするための条件です。$E_m:=K_m^\dagger K_m$ は、固有値が $0$ 以上のエルミート演算子で、$\sum_mE_m=I$ を満たします。この $\{E_m\}$ を **POVM**（正作用素値測度）と呼びます。確率 $P(m)=\langle\Phi|E_m|\Phi\rangle$ は $E_m$ だけで決まり、測定後の状態まで決めるには $K_m$ が要ります（$K_m$ には、$E_m$ を変えない任意のユニタリ変換 $K_m\to V_mK_m$ の不定性があります）。射影測定は、$K_m=M_x$ のとき（$E_m=M_x$）です。

**例：誤差のある $Z$ 測定**。1量子ビットで

$$
K_0=\begin{pmatrix}\sqrt{1-\epsilon}&0\\0&\sqrt\epsilon\end{pmatrix},\qquad K_1=\begin{pmatrix}\sqrt\epsilon&0\\0&\sqrt{1-\epsilon}\end{pmatrix}
$$

とします。(A-5) を確かめると、$K_0^\dagger K_0+K_1^\dagger K_1=\mathrm{diag}\big((1-\epsilon)+\epsilon,\ \epsilon+(1-\epsilon)\big)=I$ です。$E_0=\mathrm{diag}(1-\epsilon,\ \epsilon)$ なので、状態 $\cos\frac\theta2|0\rangle+\sin\frac\theta2|1\rangle$ で結果 $0$ が出る確率は

$$
P(0)=(1-\epsilon)\cos^2\frac\theta2+\epsilon\sin^2\frac\theta2
$$

です。$\epsilon=0$ なら通常の $Z$ 測定（$K_0=|0\rangle\langle0|$）、$\epsilon>0$ では、$|0\rangle$（$\theta=0$）でも結果 $0$ の確率が $1-\epsilon$ にとどまり、$|1\rangle$ でも $\epsilon$ の確率で $0$ が出ます（図 A-1 の右下）。**注意（読み出し誤差との違い）**：結果の確率だけを見れば、「射影測定をして、結果ラベルを確率 $\epsilon$ で取り違える」読み出し誤差と同じです。しかし**測定後の状態は違います**。状態 $|+\rangle$、$\epsilon=0.1$ で結果 $0$ が出たとき（確率はどちらも $\frac12$）、ラベルの取り違えの模型では測定後の状態は $(1-\epsilon)|0\rangle\langle0|+\epsilon|1\rangle\langle1|$ で非対角成分が $0$ ですが、$K_0$ による測定後の状態は $\propto(\sqrt{1-\epsilon},\ \sqrt\epsilon)^T$ の純粋状態で、非対角成分が $\sqrt{\epsilon(1-\epsilon)}=0.3$ 残ります（数値で確認）。ただし、この「ラベル取り違え」の模型は、結果 $0$ に**複数の演算子**が対応するので、(A-6) のような1結果1演算子の形では書けません（結果 $0$ の後の状態 $\mathrm{diag}(0.9,\,0.1)$ は階数 $2$ の混合状態で、単一の $K_0|+\rangle$ では表せない）。一般の測定は、結果 $m$ に演算子の組 $\{K_{m\alpha}\}_\alpha$ を割り当てて、$\sum_{m,\alpha}K_{m\alpha}^\dagger K_{m\alpha}=I$ を満たすものです（(A-6) は各 $m$ に $\alpha$ が1つの場合）。このとき、結果 $m$ の確率と、測定後の状態（密度行列）は

$$
P(m)=\operatorname{tr}\Big(\sum_\alpha K_{m\alpha}\rho K_{m\alpha}^\dagger\Big),\qquad\rho_m=\frac{\sum_\alpha K_{m\alpha}\rho K_{m\alpha}^\dagger}{P(m)},\qquad E_m=\sum_\alpha K_{m\alpha}^\dagger K_{m\alpha}\tag{A-7}
$$

です。ラベル取り違えの模型は、$K_{0,1}=\sqrt{1-\epsilon}\,P_0$、$K_{0,2}=\sqrt\epsilon\,P_1$（結果 $0$ の2つの経路）、$K_{1,1}=\sqrt{1-\epsilon}\,P_1$、$K_{1,2}=\sqrt\epsilon\,P_0$ で、$\rho_0\propto(1-\epsilon)P_0\rho P_0+\epsilon P_1\rho P_1$、$E_0=(1-\epsilon)P_0+\epsilon P_1$ になります。以下では、1結果1演算子の場合 (A-6) を扱います。また $K_0^2=\mathrm{diag}(1-\epsilon,\ \epsilon)\ne K_0$ なので、$\epsilon>0$ の $K_0$ は射影演算子ではありません。結果 $0$ の後の状態 $\propto(\sqrt{1-\epsilon}\cos\frac\theta2,\ \sqrt\epsilon\sin\frac\theta2)^T$ は $|0\rangle$ に完全には崩れません（弱い測定）。

**注意：足す順序**：(A-5) は、各 $K_m^\dagger K_m$ を作ってから足す条件で、$\big(\sum_mK_m^\dagger\big)\big(\sum_mK_m\big)=\sum_{m,m'}K_m^\dagger K_{m'}$ ではありません。後者には、$m\ne m'$ の**交差項** $K_m^\dagger K_{m'}$ が入ります。例：ビット反転の測定演算子 $K_0=\sqrt{1-p}\,I$、$K_1=\sqrt p\,X$ では、$K_0^\dagger K_0+K_1^\dagger K_1=(1-p)I+pI=I$ ですが、

$$
\Big(\sum_mK_m^\dagger\Big)\Big(\sum_mK_m\Big)=\big(\sqrt{1-p}\,I+\sqrt p\,X\big)^2=I+2\sqrt{p(1-p)}\,X\ne I\qquad(0<p<1)
$$

です（$X^2=I$ を使いました）。

**環境を使った見方**：系と環境 $E$ をまとめた状態にユニタリ演算子 $U$ を作用させ、環境の初期状態を $|0_E\rangle$、環境を基底 $|m_E\rangle$ で測ったとき、系に作用する演算子は $K_m=\langle m_E|U|0_E\rangle$ です。$U^\dagger U=I$ と環境の完全性関係 $\sum_m|m_E\rangle\langle m_E|=I_E$ から

$$
\sum_mK_m^\dagger K_m=\langle0_E|U^\dagger\Big(\sum_m|m_E\rangle\langle m_E|\Big)U|0_E\rangle=\langle0_E|U^\dagger U|0_E\rangle=I
$$

となり、(A-5) が自動的に成り立ちます。逆に、任意の POVM は、系を拡張した空間の射影測定として実現できることが知られています（ナイマルクの拡張定理。ここでは証明せず、事実として引用します）。系の側から見ると、環境との相互作用で、射影測定が一般の測定に見える、ということです（[ノイズのノート](../05_量子力学/noise_modeling_through_mri.md)の T1 の緩和などの量子チャネルも、同じ形の $K_m$ の組で書けます）。

---

<a id="appB"></a>

# 付録B：結果レジスタを測る、係数行列とエンタングルメント

<!-- part-toc:start -->

**この付録の内容**

- [B-1. 係数行列](#B-1)
- [B-2. 結果レジスタを測る](#B-2)
- [B-3. 積状態の判定：係数行列の階数](#B-3)

<!-- part-toc:end -->

本編では入力レジスタだけを測りました。ここでは、**結果レジスタ**を測ったとき入力レジスタに何が残るか、そして $|\Psi\rangle$ がどれだけエンタングルしているかを、係数行列で調べます。

<a id="B-1"></a>

## B-1. 係数行列

状態 $|\Phi\rangle=\sum_{x,y}c_{x,y}|x\rangle|y\rangle$（Part IV §1）の係数を、入力 $x$ を行、結果 $y$ を列とする $N\times M$ の行列 $C=(c_{x,y})$ に並べます。$|\Psi\rangle$（振幅 $\alpha_x$）では

$$
c_{x,y}=\alpha_x\,\delta_{y,f(x)}
$$

で、各行にゼロでない成分がちょうど1つあります。Part VIII の例（$N=4$、$M=2$、$\alpha_x=\tfrac12$、$f(x)=1\Leftrightarrow x=11$）では

$$
C=\frac12\begin{pmatrix}1&0\\1&0\\1&0\\0&1\end{pmatrix}
$$

です（行が $00,01,10,11$、列が $y=0,1$）。

- 規格化：$\sum_{x,y}|c_{x,y}|^2=1$。
- 入力の確率（Part IV §3 の (IV-1)）：$P(x)=\sum_y|c_{x,y}|^2$、つまり**第 $x$ 行の成分の絶対値の2乗の和**。
- 結果の確率：$P(y)=\sum_x|c_{x,y}|^2$、つまり**第 $y$ 列の成分の絶対値の2乗の和**（B-2）。

<a id="B-2"></a>

## B-2. 結果レジスタを測る

結果レジスタが $y$ になる測定の演算子を $M'_y:=I_N\otimes|y\rangle\langle y|$ とします。Part III §3 と同じ計算（(III-1) と線形性）で、基底 $|x\rangle|y'\rangle$ に作用させると

$$
M'_y\big(|x\rangle|y'\rangle\big)=|x\rangle\otimes|y\rangle\langle y|y'\rangle=\delta_{y,y'}\,|x\rangle|y\rangle
$$

なので、

$$
M'_y|\Phi\rangle=\sum_{x}c_{x,y}\,|x\rangle|y\rangle=\Big(\sum_xc_{x,y}|x\rangle\Big)\otimes|y\rangle\tag{B-1}
$$

です。確率は $P(y)=\|M'_y\Phi\|^2=\sum_x|c_{x,y}|^2$（Part IV §6 と同じ計算）で、測定後の状態は

$$
|\Phi_y\rangle=\frac{1}{\sqrt{P(y)}}\Big(\sum_xc_{x,y}|x\rangle\Big)\otimes|y\rangle\tag{B-2}
$$

と、**積状態**になります。$|\Psi\rangle$ では $c_{x,y}=\alpha_x\delta_{y,f(x)}$ なので、

$$
P(y)=\sum_{x:\,f(x)=y}|\alpha_x|^2,\qquad|\Psi_y\rangle=\frac{1}{\sqrt{P(y)}}\Big(\sum_{x:\,f(x)=y}\alpha_x|x\rangle\Big)\otimes|y\rangle\tag{B-3}
$$

です。**結果 $y$ を測ると、入力レジスタは、$f(x)=y$ を満たす $x$（$y$ の逆像）だけの重ね合わせに絞り込まれます。**

**例（Part VIII）**：$\alpha_x=\tfrac12$ で、逆像は $f^{-1}(0)=\{00,01,10\}$、$f^{-1}(1)=\{11\}$ なので

$$
P(0)=3\cdot\tfrac14=\tfrac34,\quad|\Psi_0\rangle=\frac{|00\rangle+|01\rangle+|10\rangle}{\sqrt3}\otimes|0\rangle;\qquad P(1)=\tfrac14,\quad|\Psi_1\rangle=|11\rangle|1\rangle
$$

です（$\frac12(|00\rangle+|01\rangle+|10\rangle)\big/\sqrt{3/4}=(|00\rangle+|01\rangle+|10\rangle)/\sqrt3$）。確率の和は $\tfrac34+\tfrac14=1$ です。

**入力と結果の両方を測る**：付録C-1の式から $M_xM'_y=(P_x\otimes I)(I\otimes P_y)=P_x\otimes P_y=M'_yM_x$ で、順序を入れ替えても同じです。同時確率は $P(x,y)=\|M_xM'_y\Phi\|^2=|c_{x,y}|^2$ で、ボルン則（Part IV §2）そのものです。

<a id="B-3"></a>

## B-3. 積状態の判定：係数行列の階数

**主張**：$|\Phi\rangle$ が入力レジスタの状態と結果レジスタの状態のテンソル積 $|u\rangle\otimes|v\rangle$ の形に書けることと、係数行列 $C$ の階数が $1$ であることは同値です。

**証明**：$|u\rangle=\sum_xu_x|x\rangle$、$|v\rangle=\sum_yv_y|y\rangle$ なら、$|u\rangle\otimes|v\rangle=\sum_{x,y}u_xv_y|x\rangle|y\rangle$（Part III §2-c）なので、$c_{x,y}=u_xv_y$、つまり $C=uv^T$（列ベクトル $u$ と行ベクトル $v^T$ の積）で、階数は $1$ です。逆に、階数 $1$ の行列は $C=uv^T$ の形に書けるので、$|\Phi\rangle=\sum_{x,y}u_xv_y|x\rangle|y\rangle=|u\rangle\otimes|v\rangle$ です（零行列は規格化に反するので除く）。$\square$

Part III §2-f-5 の積状態の判定（$2\times2$ では $w_{00}w_{11}=w_{01}w_{10}$、つまり $\det C=0$）は、この主張の $N=M=2$ の場合です。

**$|\Psi\rangle$ の場合**（振幅 $\alpha_x$ がすべて $0$ でないとき。下の例は均等な重ね合わせ）：

| 関数 | 係数行列 | 階数 | 状態 |
|---|---|---|---|
| 定数 $f(x)=0$ | 第0列だけがゼロでない | $1$ | 積状態：$\big(\sum_x\alpha_x|x\rangle\big)\otimes|0\rangle$ |
| Part VIII の例 | 列が2つとも使われる | $2$ | エンタングルしている |
| 1対1（$f(x)=x$） | 各行・各列に1つずつ | $N$ | エンタングルしている（均等なら、エントロピーが最大 $\log_2N$） |

階数が積状態かどうかの判定であって、エンタングルメントの**量**を表すわけではない点に注意してください。1対1の関数では、階数は**振幅がゼロでない入力の個数**で決まり、振幅の偏りだけではエントロピーが下がります。たとえば $\alpha=(\sqrt{0.9},\sqrt{0.1},0,0)$ なら、振幅がゼロでない入力が $00$ と $01$ の2つなので階数は $2$、$p_k=(0.9,0.1)$ でエントロピーは約 $0.469$ bit です。一方、$\alpha=(\sqrt{0.4},\sqrt{0.3},\sqrt{0.2},\sqrt{0.1})$ のように、すべて $0$ でなければ階数は $4$ のままで、偏りの分だけエントロピーが $\log_24=2$ bit より小さくなります。また、階数が大きくても、シュミット確率が偏っていればエントロピーは小さくなります（$p=(0.999,0.0005,0.0005)$ は階数 $3$ ですが、$p=(0.5,0.5)$ の階数 $2$ よりエントロピーが小さい）。量の比較には、次のエンタングルメントエントロピーを使います。

**シュミット分解**：$C$ の特異値分解 $C=USV^\dagger$（$U,V$ はユニタリ、$S$ は特異値 $s_1\ge s_2\ge\cdots\ge0$ を対角に持つ）を使うと、$c_{x,y}=\sum_kU_{xk}\,s_k\,\overline{V_{yk}}$ なので

$$
|\Phi\rangle=\sum_ks_k\Big(\sum_xU_{xk}|x\rangle\Big)\otimes\Big(\sum_y\overline{V_{yk}}|y\rangle\Big)=\sum_ks_k\,|u_k\rangle\otimes|v_k\rangle\tag{B-4}
$$

です。$U,V$ の列は正規直交なので、$\{|u_k\rangle\}$、$\{|v_k\rangle\}$ も正規直交で、$\sum_ks_k^2=\sum|c_{x,y}|^2=1$ です（係数行列のフロベニウスノルム）。ゼロでない特異値の個数が $C$ の階数で、**階数 $1$ のときだけ積状態**です。

**エンタングルメントエントロピー**：$p_k:=s_k^2$ を確率と見て、$S:=-\sum_kp_k\log_2p_k$ を、エンタングルメントの大きさの指標とします（積状態で $0$）。

| 関数 | $p_k$ | $S$ |
|---|---|---|
| 定数 | $(1)$ | $0$ bit |
| Part VIII の例 | $(\tfrac34,\tfrac14)$ | $-\tfrac34\log_2\tfrac34-\tfrac14\log_2\tfrac14\approx0.811$ bit |
| 1対1（$N=4$、均等） | $(\tfrac14,\tfrac14,\tfrac14,\tfrac14)$ | $\log_24=2$ bit |

Part VIII の例の $p_k=(\tfrac34,\tfrac14)$ は、$C^TC=\tfrac14\begin{pmatrix}3&0\\0&1\end{pmatrix}$ の固有値です。この例では $C^TC$ が対角なので、その対角成分が、結果レジスタの確率 $P(y)=(\tfrac34,\tfrac14)$（B-2）と一致しています（図 B-1）。

![係数行列と階数](figures/mp05_coefficient_matrices.png)

*図 B-1。係数行列 $C=(c_{x,y})$（行が入力、列が結果）。定数関数（階数 $1$、エントロピー $0$）、Part VIII の例（階数 $2$、$0.811$ bit）、1対1（階数 $4$、$2$ bit）。図を描くときに、階数とエントロピーを式で確かめています。*

**関数を計算することは、入力と結果をエンタングルさせる**：$U_f$ を均等な重ね合わせに作用させると、$f$ が定数でない限り、入力レジスタと結果レジスタは積状態でなくなります。本編 Part VII の「$U_f$ は振幅を変えない」ことと矛盾しません。入力レジスタを**単独で**測る確率は $|\alpha_x|^2$ のままですが、結果レジスタの情報が入力レジスタと相関を持つので、結果レジスタを測ると、入力レジスタの状態が (B-3) のように変わります。入力レジスタだけを見るための記述（部分トレースと、密度行列 $CC^\dagger$）は、別のノート（[部分トレースと縮約密度行列](partial_trace_reduced_density_matrix.md)）で扱います。

---

<a id="appC"></a>

# 付録C：クロネッカー積の性質と、Qiskit の並び順

<!-- part-toc:start -->

**この付録の内容**

- [C-1. テンソル積同士の積はテンソル積](#C-1)
- [C-2. そのほかの性質](#C-2)
- [C-3. Qiskit の並び順](#C-3)

<!-- part-toc:end -->

<a id="C-1"></a>

## C-1. テンソル積同士の積はテンソル積

$$
\boxed{(U_1\otimes U_2)(V_1\otimes V_2)=U_1V_1\otimes U_2V_2}\tag{C-1}
$$

**証明**：両辺を、任意の基底ベクトル $|k\rangle\otimes|l\rangle$ に作用させて比べます。左辺は、右の行列から順に作用させ、(III-1) を2回使うと：

$$
(U_1\otimes U_2)(V_1\otimes V_2)\big(|k\rangle\otimes|l\rangle\big)=(U_1\otimes U_2)\big(V_1|k\rangle\otimes V_2|l\rangle\big)=U_1V_1|k\rangle\otimes U_2V_2|l\rangle
$$

右辺も (III-1) から $U_1V_1|k\rangle\otimes U_2V_2|l\rangle$ です。行列を基底ベクトルに作用させた結果はその行列の列なので（2つの行列のすべての列が一致すれば、行列として等しい。Part III §2-f-7 の準備を参照）、両辺は等しくなります。$\square$

**帰結**：

- $U,V$ がどちらもテンソル積なら、$UV$ もテンソル積です。例えば $(X\otimes I_2)(I_2\otimes Z)=X\otimes Z$。
- $U,V$ がテンソル積でなくても、積がテンソル積になることがあります。例えば $\mathrm{CNOT}\cdot\mathrm{CNOT}=I_4=I_2\otimes I_2$（CNOT は自分自身の逆行列）。
- したがって、「行列の積で書かれているから分けられない」のではなく、Part III §2-g-1 の通り、**結果の行列が $B_1\otimes B_2$ の形に書けるか**で判断します。
- $U_1=A$、$U_2=I_4$、$V_1=I_2$、$V_2=B$ とすると $AI_2\otimes I_4B=A\otimes B$ で、Part III §2-f-7 の $(A\otimes I_n)(I_m\otimes B)=A\otimes B$ になります。

<a id="C-2"></a>

## C-2. そのほかの性質

行列 $A\in\mathbb C^{m\times m}$、$B\in\mathbb C^{n\times n}$ について、成分は $(A\otimes B)_{(k,l),(k',l')}=A_{kk'}B_{ll'}$ です（Part III §2-d）。

- **転置・共役転置**：$(A\otimes B)^T=A^T\otimes B^T$、$(A\otimes B)^\dagger=A^\dagger\otimes B^\dagger$。成分 $(k,l),(k',l')$ の入れ替えと複素共役が、$A_{kk'}$ と $B_{ll'}$ にそれぞれ独立に働くからです。
- **ユニタリ性**：$U_1,U_2$ がユニタリなら、(C-1) と上の式から $(U_1\otimes U_2)^\dagger(U_1\otimes U_2)=U_1^\dagger U_1\otimes U_2^\dagger U_2=I\otimes I=I$ で、$U_1\otimes U_2$ もユニタリです。別々のレジスタに作用するゲートを並べたものは、ユニタリです。
- **トレース**：$\operatorname{tr}(A\otimes B)=\sum_{k,l}A_{kk}B_{ll}=\operatorname{tr}A\cdot\operatorname{tr}B$（対角成分は $(k,l)=(k',l')$ のとき）。
- **固有値**：$Au=\lambda u$、$Bv=\mu v$ なら、(III-1) から $(A\otimes B)(u\otimes v)=\lambda\mu\,(u\otimes v)$ なので、固有値の積 $\lambda\mu$ が $A\otimes B$ の固有値です（$A,B$ が対角化できるなら、これですべての固有値が出ます）。
- **行列式**：$\det(A\otimes B)=(\det A)^n(\det B)^m$。$(A\otimes B)=(A\otimes I_n)(I_m\otimes B)$（Part III §2-f-7）で、$I_m\otimes B$ は $B$ を $m$ 個並べたブロック対角行列なので $\det=(\det B)^m$、$A\otimes I_n$ は行と列の並べ替えで $A$ を $n$ 個並べたブロック対角行列になるので $\det=(\det A)^n$ です（後者は、並べ替えが行と列に同じ置換を施す相似変換で、行列式を変えないことを使います。ここでは事実として引用します）。

トレース、転置、共役転置、混合積、固有値、行列式の式は、ランダムな複素行列（$2\times2$ と $3\times3$）でも数値で確かめました。

<a id="C-3"></a>

## C-3. Qiskit の並び順

本編の教科書流の記法では、$|x_1x_2y\rangle$ の**左が第1の因子**で、$|u\rangle\otimes|v\rangle\otimes|w\rangle$ の成分は $u$ が最上位の添字です。Qiskit は、**ラベルの右端が量子ビット $q_0$** で、$|q_{n-1}\cdots q_1q_0\rangle$ と書きます（添字 $=\sum_jq_j2^j$）。

| | 教科書（本編） | Qiskit |
|---|---|---|
| ラベル | $\lvert\text{第1}\ \text{第2}\ \text{第3}\rangle$ | $\lvert q_2\,q_1\,q_0\rangle$ |
| 添字（3量子ビット） | $4\cdot\text{第1}+2\cdot\text{第2}+\text{第3}$ | $4q_2+2q_1+q_0$ |
| 対応 | 第1 $\leftrightarrow q_2$、第2 $\leftrightarrow q_1$、第3 $\leftrightarrow q_0$ | 番号の大きい方から順に |

![教科書とQiskitの並び順](figures/mp06_qiskit_order.png)

*図 C-1。教科書の「第 $k$」は、Qiskit では番号の大きい方から順に対応させる。下の2つの行列は、教科書の CNOT（制御が左＝第1）が Qiskit の cx(1, 0) と同じ行列で、cx(0, 1) は別の行列であることを示す。図を描くときに、Qiskit の `Operator` と比べています。*

**確かめた例**：

1. 2量子ビットの回路で量子ビット $q_0$ に $X$ をかけると、状態ベクトルは $(0,1,0,0)^T$、ラベルは `'01'`（$q_1=0$、$q_0=1$）です。教科書の「第1量子ビットに $X$」は $X\otimes I_2$ なので $|00\rangle\to|10\rangle=(0,0,1,0)^T$ で、Qiskit では $q_1$ に $X$ をかけたもの（`x(1)`）にあたります。
2. 教科書の CNOT（制御が左＝第1）の行列 $\begin{pmatrix}1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&1&0\end{pmatrix}$ は、Qiskit の `cx(1, 0)`（制御 $q_1$、標的 $q_0$）の行列と一致しました。`cx(0, 1)` の行列は別物です。
3. **Part VIII の回路**を、入力レジスタを $q_2,q_1$、結果レジスタを $q_0$ として作ります：

```python
qc = QuantumCircuit(3)
qc.h(2); qc.h(1)      # 入力レジスタを均等な重ね合わせに
qc.ccx(2, 1, 0)       # f(x)=1 ⇔ x=11：入力がどちらも 1 のとき、結果レジスタを反転
```

この回路の状態ベクトルは $\tfrac12(1,0,1,0,1,0,0,1)^T$ で、Part VIII の $|\Psi\rangle$ と**完全に一致**します（教科書の第1を番号の大きい量子ビットに対応させたため）。入力レジスタ $(q_2,q_1)$ の確率は、`Statevector.probabilities([2, 1])` で $(\tfrac14,\tfrac14,\tfrac14,\tfrac14)$ です。$M_{11}=P_{11}\otimes I_2$ を、この状態ベクトルに行列として作用させても、$\tfrac12|111\rangle$ になります。

Qiskit のコードと教科書の式を突き合わせるときは、最初に、**量子ビットの番号とラベルの並び順の対応**を決めてください。

---

<a id="appD"></a>

# 付録D：検算の一覧

このノートの式と数値は、[experiments/measurement_projection/](../../experiments/measurement_projection/README.md) のスクリプトとテスト（44件）、図のスクリプトの `assert` で確かめています。

| ノートの箇所 | 確かめたこと | テスト |
|---|---|---|
| Part III §2-e | $(A\otimes B)(u\otimes v)=Au\otimes Bv$（(III-1)）。$(a,b)\otimes(c,d)=(ac,ad,bc,bd)$、$\lvert0\rangle\otimes\lvert0\rangle=(1,0,0,0)^T$ | `test_mixed_product_rule_3_1`、`test_kron_components_and_labels` |
| Part II | $P^2=P$、$P^\dagger=P$、正解以外をゼロにする | `test_projector_properties` |
| Part III §2-f | $(A\otimes I_n)(I_m\otimes B)=A\otimes B=(I_m\otimes B)(A\otimes I_n)$、$X\otimes I\ne I\otimes X$、$A\otimes I_m$ の次元 | `test_identity_commutes_with_other_register_operator` |
| Part III §2-f-5 | $\lvert\Phi^+\rangle$ は積状態でない。積状態の条件 $w_{00}w_{11}=w_{01}w_{10}$ | `test_entangled_state_is_not_product` |
| Part III §2-g-2 | CNOT は $B_1\otimes B_2$ に書けない（再配置行列の階数 $2$） | `test_cnot_is_not_a_tensor_product` |
| 付録C-1 | $(U_1\otimes U_2)(V_1\otimes V_2)=U_1V_1\otimes U_2V_2$、$\mathrm{CNOT}^2=I$ | `test_mixed_product_of_tensor_products_and_cnot_squared` |
| Part IV | $P(x)=\sum_y\lvert c_{x,y}\rvert^2=\lVert(P_x\otimes I)\Phi\rVert^2=\langle\Phi\vert P_x\otimes I\vert\Phi\rangle$、$(P\otimes I)^\dagger(P\otimes I)=P\otimes I$ | `test_born_rule_and_projector_agree_for_random_states` |
| Part IV §5 | $(\langle a\lvert\langle b\rvert)(\lvert c\rangle\lvert d\rangle)=\langle a\vert c\rangle\langle b\vert d\rangle$ | `test_inner_product_of_tensor_products_4_2` |
| Part V、VI | $M_{x}\lvert\Psi\rangle=\frac1{\sqrt N}\lvert x\rangle\lvert f(x)\rangle$、$P(x)=\frac1N$（3つの $(n_{\mathrm{in}},n_{\mathrm{out}})$） | `test_uniform_superposition_gives_one_over_N` |
| Part VII | $P(x^\ast)=\lvert\alpha_{x^\ast}\rvert^2$ | `test_general_amplitudes_give_alpha_squared` |
| Part VIII | $\lvert\Psi\rangle$ の成分、$M_{11}$ の対角、$M_{11}\lvert\Psi\rangle=\frac12\lvert111\rangle$、確率 $\frac14$ | `test_example_8` |
| 付録A-1 | $M_xM_{x'}=\delta M_x$、$\sum M_x=I$、$\sum P(x)=1$ | `test_projective_measurement_is_complete` |
| 付録A-2、A-3 | 測定後の状態の規格化、再現性、Part VIII の測定後の状態 | `test_post_measurement_state_and_repeatability`、`test_post_measurement_of_example_is_a_product_state` |
| 付録A-4 | $\sum K^\dagger K=I$、$P(0)=(1-\epsilon)\cos^2+\epsilon\sin^2$、$\epsilon=0$ で射影測定、$K_0$ は射影でない | `test_general_measurement_kraus_completeness` |
| 付録A-4 | $\sum K^\dagger K=I$ だが $(\sum K^\dagger)(\sum K)=I+2\sqrt{p(1-p)}X$。振幅減衰の $K_1^\dagger K_1=\gamma\lvert1\rangle\langle1\rvert$ | `test_sum_of_kraus_then_product_is_not_identity` |
| 付録A-4 | 弱い測定 $K_0$ と、ラベル取り違えの読み出し誤差は、確率が同じで測定後の状態が違う（非対角成分 $\sqrt{\epsilon(1-\epsilon)}$ と $0$） | `test_unsharp_measurement_differs_from_readout_error_after_the_measurement` |
| 付録B-3 | 階数はエンタングルメントの量でない（偏った振幅の1対1は階数2・約 $0.469$ bit。階数3でも $p=(0.999,\ldots)$ は階数2の $p=(0.5,0.5)$ よりエントロピーが小さい） | `test_rank_is_not_a_measure_of_entanglement` |
| 付録A-4 | ラベル取り違えの読み出し誤差は、結果 $0$ に2つの演算子が要る（条件付き状態 $\mathrm{diag}(1-\epsilon,\epsilon)$ は階数 $2$、$E_0=(1-\epsilon)P_0+\epsilon P_1$） | `test_readout_error_needs_several_operators_per_outcome` |
| 付録B-3 | 1対1では階数 $=$ 振幅がゼロでない入力の個数（$\alpha=(\sqrt{0.4},\ldots)$ は階数 $4$ でエントロピーは $2$ bit 未満）。入力が $\lvert0\rangle$ だけなら、非定数の $f$ でも積状態 | `test_injective_function_rank_counts_nonzero_amplitudes` |
| 付録A-4 | $K_m=\langle m_E\vert U\vert0_E\rangle$ から $\sum K^\dagger K=I$ | `test_stinespring_form_of_kraus` |
| 付録B-2 | 結果レジスタを測ったときの確率と状態、逆像の重ね合わせ | `test_result_register_collapse_for_example`、`test_result_register_collapse_is_uniform_on_preimage` |
| 付録B-3 | 係数行列の階数（定数 $1$、例 $2$、1対1 $4$）、階数 $1$ ⇔ 積状態、シュミット係数とエントロピー | `test_rank_of_coefficient_matrix_decides_product_form`、`test_schmidt_numbers_of_example_and_entropy` |
| 付録B | $CC^\dagger$ の対角成分が $P(x)$ | `test_reduced_state_diagonal_is_input_probability` |
| 付録C-2 | トレース、転置、共役転置、固有値、行列式、ユニタリ性 | `test_tensor_product_invariants` |
| 付録C-3 | Qiskit の並び順、cx(1, 0) の行列、Part VIII の回路の状態ベクトルと確率。$q_0$ に $X$ は $I\otimes X$、$q_1$ に $X$ は $X\otimes I$ | `test_qiskit_ordering_matches_the_note`、`test_qiskit_single_qubit_gate_positions` |
| 図 | 各図の値を本文の式と `assert` で照合 | `figures/make_measurement_projection_figures.py` |

```bash
uv run pytest experiments/measurement_projection -q
uv run python 研究ノート/08_量子コンピュータ/figures/make_measurement_projection_figures.py
```
