# 部分トレースと縮約密度行列 ―入力レジスタだけを見る―

> **作成** 2026-10-17　**更新** 2026-10-17
> 2つのレジスタにまたがる状態から、片方のレジスタだけの状態（縮約密度行列）を作る部分トレースの定義と性質、係数行列との関係、結果レジスタとのエンタングルメントで干渉が消える仕組み、環境を使った見方（Kraus 表現）。
> 検算と図つき。

[射影演算子による測定確率のノート](measurement_projection_born_rule.md)（以下「本編」）では、関数を計算した後の状態 $|\Psi\rangle=\frac1{\sqrt N}\sum_i|x_i\rangle|f(x_i)\rangle$ について、入力レジスタを測る確率を求めました。このノートでは、同じ状況を**入力レジスタだけの状態**として表します。結果レジスタを「見ない」「無視する」ことを、数式で正確に書くのが部分トレースです。

- **Part I**：なぜ必要か。純粋状態の密度行列と、期待値 $\langle A\rangle=\operatorname{tr}(\rho A)$
- **Part II**：部分トレースの定義、成分の式、性質（基底によらない。期待値が縮約状態だけで決まる）
- **Part III**：本編の $|\Phi\rangle=\sum c_{x,y}|x\rangle|y\rangle$ の縮約密度行列 $\rho_A=CC^\dagger$。対角成分は確率、固有値はシュミット係数の2乗、混合状態としての見方
- **Part IV**：本編の例（4候補・正解1個）と、定数関数・1対1の関数の縮約密度行列
- **Part V**：結果レジスタが入力を「覚える」と、入力の干渉が消えること
- **Part VI**：環境を使った見方（Kraus 表現）

**関連ファイル**：図は [figures/make_measurement_projection_figures.py](figures/make_measurement_projection_figures.py)（mp07、mp08）で作っていて、各図の値はスクリプトの中で本文の式と照合しています。式と数値の検算は [experiments/measurement_projection/](../../experiments/measurement_projection/README.md)（部分トレースの8件を含む）。密度行列の基本は[密度行列のノート](../05_量子力学/density_matrix_bracket_notation.md)、ノイズと量子チャネルは[ノイズのノート](../05_量子力学/noise_modeling_through_mri.md)にあります。

**記号の約束**

- 入力レジスタを系 $A$（次元 $N$）、結果レジスタを系 $B$（次元 $M$）と書きます。基底は $|x\rangle$（$x=0,\dots,N-1$）、$|y\rangle$（$y=0,\dots,M-1$）です。
- $|\Phi\rangle=\sum_{x,y}c_{x,y}|x\rangle|y\rangle$、$C=(c_{x,y})$ は $N\times M$ の係数行列（本編の付録B）です。
- 演算子 $\rho$ の成分を $\rho_{(x,y),(x',y')}:=\langle x|\langle y|\,\rho\,|x'\rangle|y'\rangle$ と書きます。
- 式番号は `Part 番号-通し番号`（例：II-3）です。本編の式は「本編の (III-1)」のように書きます。

<a id="toc"></a>

## 目次

<!-- toc:start -->

- [Part I：なぜ必要か](#p1)
  - [1. 本編の結果と、残った疑問](#p1-1)
  - [2. 純粋状態の密度行列と、期待値](#p1-2)
- [Part II：部分トレース](#p2)
  - [1. 定義と成分の式](#p2-1)
  - [2. 基本的な性質](#p2-2)
  - [3. 縮約状態だけで、系 A についての予言が決まる](#p2-3)
- [Part III：|Phi⟩ の縮約密度行列](#p3)
  - [1. ρ\_A=CC^dagger](#p3-1)
  - [2. 対角成分は、入力が x になる確率](#p3-2)
  - [3. 固有値は、シュミット係数の2乗](#p3-3)
  - [4. 混合状態としての見方](#p3-4)
- [Part IV：例](#p4)
  - [1. 本編の例（4候補・正解1個）](#p4-1)
  - [2. 3つの関数の比較](#p4-2)
- [Part V：結果レジスタが入力を覚えると、干渉が消える](#p5)
  - [1. 入力に H^⊗ n をかけて測る](#p5-1)
  - [2. 3つの関数](#p5-2)
  - [3. 2量子ビットの模型：覚える度合いを連続的に変える](#p5-3)
- [Part VI：環境を使った見方](#p6)
- [まとめ](#summary)
- [付録A：検算の一覧](#appA)

<!-- toc:end -->

---

<a id="p1"></a>

# Part I：なぜ必要か

<!-- part-toc:start -->

**この Part の内容**

- [1. 本編の結果と、残った疑問](#p1-1)
- [2. 純粋状態の密度行列と、期待値](#p1-2)

<!-- part-toc:end -->

<a id="p1-1"></a>

## 1. 本編の結果と、残った疑問

本編の付録Bで、結果レジスタを測ると入力レジスタの状態が変わること、$|\Psi\rangle$ が一般にエンタングルしていることを見ました。しかし、次の問いには、まだ答えていません。

> 結果レジスタを**測らずに**、ただ見ない（無視する）とき、入力レジスタは、どんな状態にあるのか。入力レジスタに行うあらゆる測定の結果は、何で決まるのか。

エンタングルした状態では、入力レジスタ単独の状態ベクトル $|u\rangle$ は存在しません（積状態でないので）。それでも、入力レジスタだけについての予言は、1つの行列（縮約密度行列）で、まとめて書けます。

<a id="p1-2"></a>

## 2. 純粋状態の密度行列と、期待値

状態 $|\Phi\rangle$ に対して、演算子

$$
\rho:=|\Phi\rangle\langle\Phi|\tag{I-1}
$$

を、**密度行列**と呼びます。演算子 $A$ の期待値は、

$$
\langle\Phi|A|\Phi\rangle=\operatorname{tr}(\rho A)\tag{I-2}
$$

と書けます。

**証明**：基底 $|j\rangle$ で $\operatorname{tr}(\rho A)=\sum_j\langle j|\Phi\rangle\langle\Phi|A|j\rangle$ です。数 $\langle j|\Phi\rangle$ と $\langle\Phi|A|j\rangle$ の順序を入れ替え、$\sum_j|j\rangle\langle j|=I$（完全性関係）を使うと、$\sum_j\langle\Phi|A|j\rangle\langle j|\Phi\rangle=\langle\Phi|A\big(\sum_j|j\rangle\langle j|\big)|\Phi\rangle=\langle\Phi|A|\Phi\rangle$ です。$\square$

本編の確率 $P(x)=\langle\Phi|M_x|\Phi\rangle$（本編の Part IV §7）は、(I-2) で $A=M_x=P_x\otimes I$ とした

$$
P(x)=\operatorname{tr}\big(\rho\,(P_x\otimes I)\big)
$$

です。ボルン則（確率が $\langle\Phi|M|\Phi\rangle$）が、密度行列では $\operatorname{tr}(\rho M)$ という形になります。

---

<a id="p2"></a>

# Part II：部分トレース

<!-- part-toc:start -->

**この Part の内容**

- [1. 定義と成分の式](#p2-1)
- [2. 基本的な性質](#p2-2)
- [3. 縮約状態だけで、系 A についての予言が決まる](#p2-3)

<!-- part-toc:end -->

<a id="p2-1"></a>

## 1. 定義と成分の式

**定義**：$A$ と $B$ の合成系の演算子の全体から、$A$ の演算子の全体への線形写像 $\operatorname{Tr}_B$ で、積の形の演算子について

$$
\operatorname{Tr}_B(X\otimes Y)=X\,\operatorname{tr}(Y)\tag{II-1}
$$

を満たすものを、$B$ についての**部分トレース**（$B$ をトレースアウトする）と呼びます（$X$ は $A$ 上、$Y$ は $B$ 上の演算子）。

**存在と一意性**：積の形の演算子 $|x\rangle\langle x'|\otimes|y\rangle\langle y'|$（$x,x',y,y'$ のすべての組）は、合成系の演算子全体の基底です。そこで、一般の $\rho=\sum\rho_{(x,y),(x',y')}\,|x\rangle\langle x'|\otimes|y\rangle\langle y'|$ に、線形性で (II-1) を適用して定めます。$\operatorname{tr}\big(|y\rangle\langle y'|\big)=\langle y'|y\rangle=\delta_{yy'}$ なので、

$$
\operatorname{Tr}_B\rho=\sum_{x,x'}\Big(\sum_y\rho_{(x,y),(x',y)}\Big)|x\rangle\langle x'|,\qquad(\operatorname{Tr}_B\rho)_{x,x'}=\sum_y\rho_{(x,y),(x',y)}\tag{II-2}
$$

です。**第2・第4の添字（$B$ の添字）を同じ値にして、足す**、というのが部分トレースの計算です。$A$ をトレースアウトする $\operatorname{Tr}_A$ も同様で、$(\operatorname{Tr}_A\rho)_{y,y'}=\sum_x\rho_{(x,y),(x,y')}$ です。

<a id="p2-2"></a>

## 2. 基本的な性質

- **全体のトレースを保つ**：$\operatorname{tr}(\operatorname{Tr}_B\rho)=\sum_{x,y}\rho_{(x,y),(x,y)}=\operatorname{tr}\rho$。密度行列のトレース 1（確率の和が 1）が、縮約でも保たれます。
- **基底によらない**：$B$ の別の正規直交基底 $|y'_k\rangle=\sum_yV_{yk}|y\rangle$（$V$ はユニタリ行列）を使っても、(II-2) の右辺は変わりません。$\sum_k\langle y'_k|\,Z\,|y'_k\rangle=\sum_k\sum_{y,y''}\overline{V_{yk}}V_{y''k}\langle y|Z|y''\rangle=\sum_{y,y''}(VV^\dagger)_{y''y}\langle y|Z|y''\rangle=\sum_y\langle y|Z|y\rangle$（$VV^\dagger=I$）です。
- **エルミートで、固有値が $0$ 以上**：これは Part III で、$|\Phi\rangle$ の場合に $\rho_A=CC^\dagger$ と書けることから分かります。

<a id="p2-3"></a>

## 3. 縮約状態だけで、系 A についての予言が決まる

**主張**：$A$ の演算子 $X_A$ について

$$
\operatorname{tr}\big[(X_A\otimes I)\rho\big]=\operatorname{tr}\big[X_A\,\operatorname{Tr}_B\rho\big]\tag{II-3}
$$

が成り立ちます。

**証明**：両辺は $\rho$ について線形なので、積の形の $\rho=X\otimes Y$ について確かめれば十分です。左辺は、本編の付録C-1（混合積）から $(X_A\otimes I)(X\otimes Y)=X_AX\otimes Y$ で、付録C-2（$\operatorname{tr}(P\otimes Q)=\operatorname{tr}P\operatorname{tr}Q$）から

$$
\operatorname{tr}\big[X_AX\otimes Y\big]=\operatorname{tr}(X_AX)\operatorname{tr}(Y)
$$

です。右辺は、(II-1) から $\operatorname{tr}\big[X_A\,X\operatorname{tr}(Y)\big]=\operatorname{tr}(X_AX)\operatorname{tr}(Y)$ で、一致します。$\square$

**意味**：系 $A$ だけに作用する観測量 $X_A\otimes I$ の期待値は、**縮約密度行列 $\rho_A:=\operatorname{Tr}_B\rho$ だけで決まります**。系 $B$ を測るかどうか（測って結果を忘れても、測らなくても）は、$A$ についての予言を変えません。ボルン則の確率（射影演算子 $P=\sum$ の期待値）も同じです。

---

<a id="p3"></a>

# Part III：$|\Phi\rangle$ の縮約密度行列

<!-- part-toc:start -->

**この Part の内容**

- [1. ρ\_A=CC^dagger](#p3-1)
- [2. 対角成分は、入力が x になる確率](#p3-2)
- [3. 固有値は、シュミット係数の2乗](#p3-3)
- [4. 混合状態としての見方](#p3-4)

<!-- part-toc:end -->

<a id="p3-1"></a>

## 1. $\rho_A=CC^\dagger$

$\rho=|\Phi\rangle\langle\Phi|$ の成分は、$|\Phi\rangle=\sum c_{x,y}|x\rangle|y\rangle$ から $\rho_{(x,y),(x',y')}=c_{x,y}\,\overline{c_{x',y'}}$ です。(II-2) に代入して、

$$
(\rho_A)_{x,x'}=\sum_yc_{x,y}\,\overline{c_{x',y}}=(CC^\dagger)_{x,x'},\qquad\boxed{\rho_A=CC^\dagger}\tag{III-1}
$$

です（$CC^\dagger$ の $(x,x')$ 成分は、$C$ の第 $x$ 行と第 $x'$ 行の内積）。$B$ の側も同様に

$$
(\rho_B)_{y,y'}=\sum_xc_{x,y}\,\overline{c_{x,y'}},\qquad\rho_B=C^TC^\ast=(C^\dagger C)^T\tag{III-2}
$$

です（$C^\ast$ は成分の複素共役）。

$\rho_A=CC^\dagger$ は、エルミート（$(CC^\dagger)^\dagger=CC^\dagger$）で、任意のベクトル $v$ について $\langle v|CC^\dagger|v\rangle=\|C^\dagger v\|^2\ge0$ です。トレースは $\sum_{x,y}|c_{x,y}|^2=1$ です。

<a id="p3-2"></a>

## 2. 対角成分は、入力が $x$ になる確率

(III-1) の対角成分は、

$$
(\rho_A)_{x,x}=\sum_y|c_{x,y}|^2=P(x)
$$

で、本編の Part IV §3 の (IV-1) です。Part I §2 の式と (II-3) からも、$P(x)=\operatorname{tr}\big[\rho(P_x\otimes I)\big]=\operatorname{tr}\big[P_x\rho_A\big]=\langle x|\rho_A|x\rangle$ と出ます。**縮約密度行列の対角成分が、入力の測定確率**で、**非対角成分**（Part V で扱うコヒーレンス）は、入力に別の基底の測定（たとえばアダマール基底）を行ったときの確率に効きます。

<a id="p3-3"></a>

## 3. 固有値は、シュミット係数の2乗

本編の付録B-3 の特異値分解 $C=USV^\dagger$（$U,V$ はユニタリ、特異値 $s_k$）を使うと、

$$
\rho_A=CC^\dagger=US\,S^TU^\dagger,\qquad\rho_B=(C^\dagger C)^T=(VS^TS\,V^\dagger)^T\tag{III-3}
$$

で、$\rho_A$ の固有値は $s_k^2$（と、余った次元の $0$）、$\rho_B$ の固有値も同じ $s_k^2$ です（転置は固有値を変えない）。**$\rho_A$ と $\rho_B$ は、ゼロでない固有値が同じ**で、その固有値 $p_k=s_k^2$ が本編の付録B-3 の確率です。

- **純度**：$\operatorname{tr}\rho_A^2=\sum_kp_k^2$。$\sum_kp_k=1$ なので、$1$ になるのは $p$ が1つだけ $1$ のとき、つまり $C$ の階数が $1$（積状態）のときだけです。それ以外では $1$ より小さくなり、$N$ 個が等確率のとき最小値 $1/N$ です。
- **エントロピー**：$S=-\sum_kp_k\log_2p_k$ は、$\rho_A$ の固有値のエントロピーです（本編の付録B-3）。積状態で $0$。

<a id="p3-4"></a>

## 4. 混合状態としての見方

$CC^\dagger$ を、$C$ の列 $\mathbf c_y:=(c_{x,y})_x$ で書くと、$CC^\dagger=\sum_y\mathbf c_y\mathbf c_y^\dagger$ なので、

$$
\rho_A=\sum_yP(y)\,|\phi_y\rangle\langle\phi_y|,\qquad|\phi_y\rangle=\frac{1}{\sqrt{P(y)}}\sum_xc_{x,y}|x\rangle\tag{III-4}
$$

です（$P(y)=\sum_x|c_{x,y}|^2$）。$|\phi_y\rangle$ は、本編の付録B-2 の (B-2) の、**結果レジスタを測って $y$ が出たときの入力レジスタの状態**です。したがって、

> 結果レジスタを測って結果を**忘れた**ときの入力レジスタは、確率 $P(y)$ で状態 $|\phi_y\rangle$ にある混合状態 $\sum_yP(y)|\phi_y\rangle\langle\phi_y|$ で、これは $\rho_A$ と**一致**します。

(II-3) から、$A$ を測る確率は、$B$ を測っても測らなくても同じです。ただし、(III-4) の分解は一意ではありません。$B$ を別の基底で測ると、別の状態の混合として $\rho_A$ が書けます（同じ $\rho_A$ になる）。**$\rho_A$ という行列は同じでも、どう分解するか（何を測ったか）は決まらない**のが、混合状態の特徴です。

---

<a id="p4"></a>

# Part IV：例

<!-- part-toc:start -->

**この Part の内容**

- [1. 本編の例（4候補・正解1個）](#p4-1)
- [2. 3つの関数の比較](#p4-2)

<!-- part-toc:end -->

<a id="p4-1"></a>

## 1. 本編の例（4候補・正解1個）

本編の Part VIII の $|\Psi\rangle=\frac12\big(|00\rangle|0\rangle+|01\rangle|0\rangle+|10\rangle|0\rangle+|11\rangle|1\rangle\big)$ の係数行列は、本編の付録B-1 の

$$
C=\frac12\begin{pmatrix}1&0\\1&0\\1&0\\0&1\end{pmatrix}
$$

です。(III-1) から、

$$
\rho_A=CC^\dagger=\frac14\begin{pmatrix}1&1&1&0\\1&1&1&0\\1&1&1&0\\0&0&0&1\end{pmatrix}
$$

です（例：$(\rho_A)_{00,01}$ は、第 $00$ 行 $\frac12(1,0)$ と第 $01$ 行 $\frac12(1,0)$ の内積 $\frac14$）。**対角成分はすべて $\frac14$** で、入力の確率 $P(x)=\frac14$ と一致します（本編の Part VIII §6）。

**固有値と固有ベクトル**：$00,01,10$ の3行3列のブロック $\frac14J_3$（$J_3$ は全成分が $1$ の行列）は、固有ベクトル $(1,1,1)/\sqrt3$ の固有値が $\frac14\cdot3=\frac34$、これと直交する2つのベクトルの固有値が $0$ です。$|11\rangle$ の固有値は $\frac14$ です。

$$
\rho_A=\frac34\,|s\rangle\langle s|+\frac14\,|11\rangle\langle11|,\qquad|s\rangle=\frac{|00\rangle+|01\rangle+|10\rangle}{\sqrt3}
$$

これは (III-4) そのもので、$|s\rangle$ と $|11\rangle$ は、本編の付録B-2 の、結果レジスタを測ったときの入力の状態、$\frac34$ と $\frac14$ はその確率です。また、$\rho_B=(C^\dagger C)^T=\operatorname{diag}\big(\tfrac34,\tfrac14\big)$ で、固有値は $\rho_A$ と同じです（Part III §3）。

<a id="p4-2"></a>

## 2. 3つの関数の比較

| 関数 | $\rho_A$ | 固有値 | 純度 $\operatorname{tr}\rho_A^2$ | エントロピー |
|---|---|---|---|---|
| 定数 $f(x)=0$ | 全成分 $\frac14$（階数 $1$） | $1$ | $1$（純粋状態） | $0$ bit |
| 例（$f(x)=1\Leftrightarrow x=11$） | 上の行列 | $\frac34,\ \frac14$ | $\frac{9}{16}+\frac1{16}=\frac58$ | $0.811$ bit |
| 1対1（$f(x)=x$） | $\frac14I_4$ | $\frac14$ が4つ | $\frac14$（最小） | $2$ bit |

- **定数関数**：結果レジスタが入力の情報を持たないので、入力レジスタは、純粋状態 $|s\rangle=\frac12\sum|x\rangle$ のままです。$\rho_A=|s\rangle\langle s|$。
- **1対1**：結果レジスタが、入力を完全に覚えているので、入力レジスタは**最大混合状態** $\frac1NI$（どの基底で測っても等確率）で、非対角成分がすべて $0$ です。

![縮約密度行列](figures/mp07_reduced_states.png)

*図。入力レジスタの縮約密度行列 $\rho_A=CC^\dagger$（実部）。左：定数関数（全成分が $0.25$、固有値 $1$。純粋状態）。中：本編の例（$00,01,10$ の間に非対角成分が残り、$|11\rangle$ とは独立。固有値 $0.75,0.25$）。右：1対1（対角のみ、固有値 $0.25$ が4つ。最大混合状態）。図を描くときに、$\rho_A=CC^\dagger$ と、例の行列、固有値を式で確かめています。*

---

<a id="p5"></a>

# Part V：結果レジスタが入力を覚えると、干渉が消える

<!-- part-toc:start -->

**この Part の内容**

- [1. 入力に H^⊗ n をかけて測る](#p5-1)
- [2. 3つの関数](#p5-2)
- [3. 2量子ビットの模型：覚える度合いを連続的に変える](#p5-3)

<!-- part-toc:end -->

<a id="p5-1"></a>

## 1. 入力に $H^{\otimes n}$ をかけて測る

入力レジスタ（$n$ 量子ビット、$N=2^n$）に、アダマールゲートを各量子ビットにかけてから、すべて $0$ か測る操作を考えます。$H|0\rangle=|+\rangle=\frac1{\sqrt2}(|0\rangle+|1\rangle)$ と $H^\dagger=H$ から、

$$
H^{\otimes n}|0\cdots0\rangle=\frac1{\sqrt N}\sum_x|x\rangle=:|s\rangle
$$

です。$00\cdots0$ が出る確率は、$H^{\otimes n}$ をかけてから $P_{0\cdots0}$ を測るので、

$$
p_0=\langle\Phi|\big(H^{\otimes n}P_{0\cdots0}H^{\otimes n}\otimes I\big)|\Phi\rangle=\langle\Phi|\big(|s\rangle\langle s|\otimes I\big)|\Phi\rangle\tag{V-1}
$$

です（$H^{\otimes n}|0\cdots0\rangle\langle0\cdots0|H^{\otimes n}=|s\rangle\langle s|$）。(II-3) で $X_A=|s\rangle\langle s|$ とすると、

$$
p_0=\operatorname{tr}\big[|s\rangle\langle s|\,\rho_A\big]=\langle s|\rho_A|s\rangle=\frac1N\sum_{x,x'}(\rho_A)_{x,x'}\tag{V-2}
$$

です。**入力レジスタに行う、この「干渉の測定」の結果は、$\rho_A$ の全成分の和（非対角成分を含む）で決まります。**

<a id="p5-2"></a>

## 2. 3つの関数

| 関数 | $\rho_A$ の全成分の和 | $p_0=\frac1N\times$ 和 |
|---|---|---|
| 定数 | $16\times\frac14=4$ | $\frac14\cdot4=1$ |
| 例 | $(9+1)\times\frac14=\frac{10}4$ | $\frac14\cdot\frac{10}{4}=\frac58$ |
| 1対1 | $\operatorname{tr}\rho_A=1$（対角のみ） | $\frac14\cdot1=\frac14$ |

- 定数関数：入力は純粋状態 $|s\rangle$ のままなので、$H^{\otimes2}$ で $|00\rangle$ に戻り、$p_0=1$（干渉が完全に見える）。
- 1対1：入力は最大混合状態で、$p_0=\frac14$、つまり**単に等確率に測っているのと同じ**（干渉が見えない）。
- 本編の例：その中間の $\frac58=0.625$。

全体の状態 $|\Psi\rangle$ に $H^{\otimes2}\otimes I$ をかけて、入力が $00$ になる確率を直接計算しても、3つとも一致します（検算済み）。

<a id="p5-3"></a>

## 3. 2量子ビットの模型：覚える度合いを連続的に変える

入力 1 量子ビット、結果 1 量子ビット（$e_0,e_1$ は結果レジスタの規格化された2つの状態）で、

$$
|\Phi_\theta\rangle=\frac1{\sqrt2}\big(|0\rangle|e_0\rangle+|1\rangle|e_1\rangle\big),\qquad|e_0\rangle=\begin{pmatrix}1\\0\end{pmatrix},\ |e_1\rangle=\begin{pmatrix}\cos\theta\\\sin\theta\end{pmatrix}
$$

とします（$\langle e_0|e_1\rangle=\cos\theta$）。「入力が $0$ なら結果は $e_0$、$1$ なら $e_1$」と、結果レジスタが入力を（不完全に）覚えています。係数は $c_{0,y}=\frac{(e_0)_y}{\sqrt2}$、$c_{1,y}=\frac{(e_1)_y}{\sqrt2}$ なので、(III-1) から

$$
\rho_A=\frac12\begin{pmatrix}1&\langle e_1|e_0\rangle\\\langle e_0|e_1\rangle&1\end{pmatrix}=\frac12\begin{pmatrix}1&\cos\theta\\\cos\theta&1\end{pmatrix}\tag{V-3}
$$

です（$(\rho_A)_{0,1}=\sum_yc_{0,y}\overline{c_{1,y}}=\frac12\langle e_1|e_0\rangle$）。

- **コヒーレンス**（非対角成分の2倍の大きさ）は $|\cos\theta|=|\langle e_0|e_1\rangle|$：結果レジスタの2つの状態が**似ているほど**（重なりが大きいほど）、入力のコヒーレンスが残ります。
- $H$ をかけて $0$ が出る確率は、(V-2) と同様に $\langle+|\rho_A|+\rangle=\frac12(1+\cos\theta)$（図の青）。
- 固有値は $\frac12(1\pm|\cos\theta|)$。$\theta=0$（$e_0=e_1$）は積状態（エントロピー $0$、干渉は完全）、$\theta=\frac\pi2$（$e_0\perp e_1$）はベル状態 $\frac1{\sqrt2}(|0\rangle|0\rangle+|1\rangle|1\rangle)$ で、$\rho_A=\frac12I$、エントロピー 1 bit、干渉なし。$\theta=\pi$ は $e_1=-e_0$ で、再び積状態（$|{-}\rangle\otimes|e_0\rangle$）です。

![干渉の見えやすさ](figures/mp08_interference_visibility.png)

*左：$|\Phi_\theta\rangle$ について、$H$ の後で $0$ が出る確率（青）、コヒーレンス（橙）、エンタングルメントエントロピー（赤の破線）。結果レジスタの2つの状態が直交する $\theta=\frac\pi2$ で、コヒーレンスが $0$、エントロピーが最大になる。右：入力に $H^{\otimes2}$ をかけて $00$ が出る確率（Part V §2）。図を描くときに、(V-3) と $p_0=\frac12(1+\cos\theta)$、$0.625$ などを式で確かめています。*

**まとめると**：結果レジスタが、入力の値の違いを（直交する状態として）記録するほど、**どの値だったかが原理的に分かる**ので、入力の重ね合わせの干渉が消えます。これは、環境に位相の情報が漏れて、系のコヒーレンスが失われる**デコヒーレンス**（脱位相）と同じ仕組みで、結果レジスタが環境の役を果たしています。関数を計算した結果を残したままでは、入力レジスタの干渉を使うアルゴリズムが働かない理由で、**計算した結果を逆計算（アンコンピュート）で戻す**と、結果レジスタが $|0\cdots0\rangle$ に戻って、入力は再び積状態になり、干渉が使えます（$U_f^\dagger U_f=I$ なので、$U_f^\dagger|\Psi\rangle=\frac1{\sqrt N}\sum_i|x_i\rangle|0\cdots0\rangle$）。

---

<a id="p6"></a>

# Part VI：環境を使った見方

系 $S$ に環境 $E$（初期状態 $|0_E\rangle$）を足し、全体をユニタリ演算子 $U$ で発展させて、環境をトレースアウトします。

$$
\rho_S'=\operatorname{Tr}_E\big[U\big(\rho_S\otimes|0_E\rangle\langle0_E|\big)U^\dagger\big]
$$

$E$ の基底 $|m_E\rangle$ で (II-2) を書くと、$\operatorname{Tr}_E Z=\sum_m\langle m_E|Z|m_E\rangle$（$\langle m_E|$ は $E$ の因子にだけ作用する）です。$Z=U(\rho_S\otimes|0_E\rangle\langle0_E|)U^\dagger$ について、

$$
\rho_S'=\sum_m\langle m_E|U|0_E\rangle\,\rho_S\,\langle0_E|U^\dagger|m_E\rangle=\sum_mK_m\,\rho_S\,K_m^\dagger,\qquad K_m:=\langle m_E|U|0_E\rangle\tag{VI-1}
$$

です（$\langle m_E|U|0_E\rangle$ は、系の演算子）。**系だけを見ると、ユニタリな全体の発展が、$\sum_mK_m\rho K_m^\dagger$ という、一般の（ユニタリでない）変化に見えます**。トレースが保たれること $\operatorname{tr}\rho_S'=1$ は、$\sum_mK_m^\dagger K_m=I$（本編の付録A-4）と同じ条件です。

$K_m$ の組を、**クラウス表現**と呼びます。本編の付録A-4 の、誤差のある測定演算子 $K_m$ と同じ形です。ノイズのノート（[noise_modeling_through_mri.md](../05_量子力学/noise_modeling_through_mri.md)）の脱分極、T1、脱位相の量子チャネルも、この形の $K_m$ の組で書けます。Part V §3 の模型で、入力 1 量子ビットを系、結果レジスタを環境と見ると、$\rho_A$ の非対角成分が $\langle e_1|e_0\rangle$ 倍になった (V-3) は、**環境が位相の情報をどれだけ持ち出したか**を表す、脱位相です。

---

<a id="summary"></a>

# まとめ

| Part | 要点 |
|---|---|
| I | 純粋状態の密度行列 $\rho=|\Phi\rangle\langle\Phi|$、期待値 $\langle A\rangle=\operatorname{tr}(\rho A)$ |
| II | 部分トレース $\operatorname{Tr}_B(X\otimes Y)=X\operatorname{tr}Y$。成分は $B$ の添字を揃えて足す。$\operatorname{tr}[(X_A\otimes I)\rho]=\operatorname{tr}[X_A\rho_A]$：$A$ についての予言は $\rho_A$ だけで決まる |
| III | $\rho_A=CC^\dagger$。対角成分が $P(x)$、固有値がシュミット係数の2乗、$\rho_A=\sum_yP(y)|\phi_y\rangle\langle\phi_y|$（結果を忘れた混合状態） |
| IV | 本編の例：$\rho_A=\frac34|s\rangle\langle s|+\frac14|11\rangle\langle11|$。定数関数は純粋、1対1は最大混合 |
| V | $p_0=\frac1N\sum\rho_{xx'}$：定数 $1$、例 $\frac58$、1対1 $\frac14$。結果レジスタが入力を覚えるほど干渉が消える（デコヒーレンスと同じ仕組み） |
| VI | $\operatorname{Tr}_E[U(\rho\otimes|0_E\rangle\langle0_E|)U^\dagger]=\sum_mK_m\rho K_m^\dagger$。系だけを見ると、ユニタリな発展が一般の変化（量子チャネル）に見える |

---

<a id="appA"></a>

# 付録A：検算の一覧

このノートの式と数値は、[experiments/measurement_projection/](../../experiments/measurement_projection/README.md) のテストと、図のスクリプトの `assert` で確かめています。

| ノートの箇所 | 確かめたこと | テスト |
|---|---|---|
| Part II §1 | $\operatorname{Tr}_B(X\otimes Y)=X\operatorname{tr}Y$、$\operatorname{Tr}_A(X\otimes Y)=\operatorname{tr}X\,Y$ | `test_partial_trace_definition_on_product_operators` |
| Part II §3 | $\operatorname{tr}[(X_A\otimes I)\rho]=\operatorname{tr}[X_A\rho_A]$ | `test_expectation_value_needs_only_the_reduced_state` |
| Part III §1、§3 | $\rho_A=CC^\dagger$、$\rho_B=C^TC^\ast$、固有値がシュミット係数の2乗、トレース 1 | `test_reduced_state_is_C_Cdagger_and_CTCbar` |
| Part III §2 | $(\rho_A)_{x,x}=P(x)$ | `test_reduced_state_diagonal_is_input_probability` |
| Part IV §1 | 例の $\rho_A$、固有値 $\frac34,\frac14$、固有ベクトル、$\rho_B=\operatorname{diag}(\frac34,\frac14)$、(III-4) の分解 | `test_reduced_state_of_the_example` |
| Part IV §2 | 定数関数：純粋、1対1：$\frac14I_4$（純度 $\frac14$） | `test_constant_and_injective_functions` |
| Part V §1、§2 | $p_0=\frac1N\sum\rho_{xx'}$：$1$、$\frac58$、$\frac14$（全体に $H^{\otimes2}\otimes I$ をかけた直接計算とも一致） | `test_interference_after_hadamard_depends_on_the_result_register` |
| Part V §3 | コヒーレンス $=\frac12|\cos\theta|$（$\theta$ を6通り）、$p_0=\frac12(1+\cos\theta)$、$\theta=\frac\pi2$ で $\rho_A=\frac12I$ | `test_visibility_and_environment_overlap` |
| Part VI | $\operatorname{Tr}_E[U(\rho\otimes|0\rangle\langle0|)U^\dagger]=\sum K_m\rho K_m^\dagger$ | `test_environment_picture_gives_kraus_sum` |
| 図 | mp07、mp08 の各値を本文の式と `assert` で照合 | `figures/make_measurement_projection_figures.py` |

```bash
uv run pytest experiments/measurement_projection -q
uv run python 研究ノート/08_量子コンピュータ/figures/make_measurement_projection_figures.py mp07 mp08
```
