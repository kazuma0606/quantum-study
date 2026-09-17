# $\det(e^A) = e^{\operatorname{tr}A}$ の証明

この公式は、パウリ行列のノート Part I で「$SU(2)$ の条件 $\det U=1$ には $\operatorname{tr}A=0$ が必要」として使った根拠そのものである。証明に使う道具は、これまでの議論の中で既に手に入れたものだけで足りる。

---

## 方針：2つの経路

| 経路 | 対象 | 使う道具 |
|------|------|---------|
| 対角化を使う | $A$ が対角化可能な場合 | 相似変換を指数の中に通す公式・トレースの巡回性 |
| Jacobiの公式を使う | 一般の場合（対角化不要） | Jacobiの公式・トレースの巡回性 |

---

## 証明1：対角化できる場合

### 前提

$A$ が対角化可能とする。つまりある正則行列 $P$ と対角行列 $\Lambda=\operatorname{diag}(\lambda_1,\dots,\lambda_n)$（$\lambda_i$：$A$ の固有値）を使って

$$
A = P\Lambda P^{-1}\tag{式1}
$$

と書けるとする。目標は $\det(e^A)=e^{\operatorname{tr}A}$ を示すことである。

---

### ステップ1：$e^A$ を対角行列の指数に置き換える

以前証明した「相似変換は指数の中に丸ごと通せる」公式

$$
Pe^{X}P^{-1} = e^{PXP^{-1}}\tag{式2}
$$

（証明：$P^{-1}P=I$ を挟み込んで $P\Lambda^nP^{-1}=(P\Lambda P^{-1})^n$ を示し、テイラー展開の各項に適用する）に $X=\Lambda$ を代入する：

$$
Pe^\Lambda P^{-1} = e^{P\Lambda P^{-1}}\tag{式3}
$$

右辺の $P\Lambda P^{-1}$ は式1よりちょうど $A$ なので：

$$
Pe^\Lambda P^{-1} = e^A\tag{式4}
$$

これで「$e^A$ という計算しにくいもの」が「対角行列 $\Lambda$ の指数だけを含む形」に置き換わった。

---

### ステップ2：両辺の行列式を取り、$P, P^{-1}$ を消す

式4の両辺に $\det(\cdot)$ を適用する：

$$
\det\big(Pe^\Lambda P^{-1}\big) = \det\big(e^A\big)\tag{式5}
$$

左辺に行列式の乗法性 $\det(XYZ)=\det X\cdot\det Y\cdot\det Z$ を使う：

$$
\det\big(Pe^\Lambda P^{-1}\big) = \det(P)\cdot\det(e^\Lambda)\cdot\det(P^{-1})\tag{式6}
$$

$\det(P^{-1})=\dfrac{1}{\det P}$ なので：

$$
\det(P)\cdot\det(P^{-1}) = \det(P)\cdot\frac{1}{\det P} = 1\tag{式7}
$$

式7を式6に代入し、さらに式5と合わせると：

$$
\det\big(e^A\big) = \det(e^\Lambda)\tag{式8}
$$

「$e^A$ の行列式」の計算が「$e^\Lambda$ の行列式」の計算に帰着した。$\Lambda$ は対角行列なのでこちらの方がずっと簡単である。

---

### ステップ3：$e^\Lambda$ を具体的に計算する

$\Lambda = \operatorname{diag}(\lambda_1,\dots,\lambda_n)$ のべき乗は対角成分ごとにべき乗するだけ：

$$
\Lambda^k = \operatorname{diag}\big(\lambda_1^k,\dots,\lambda_n^k\big)\tag{式9}
$$

これをテイラー展開の定義 $e^\Lambda=\sum_{k=0}^\infty\dfrac{\Lambda^k}{k!}$ に代入する：

$$
e^\Lambda = \sum_{k=0}^\infty\frac{1}{k!}\operatorname{diag}\big(\lambda_1^k,\dots,\lambda_n^k\big) = \operatorname{diag}\!\left(\sum_{k=0}^\infty\frac{\lambda_1^k}{k!},\ \dots,\ \sum_{k=0}^\infty\frac{\lambda_n^k}{k!}\right)\tag{式10}
$$

各対角成分はスカラーの指数関数のテイラー展開そのものなので：

$$
\sum_{k=0}^\infty\frac{\lambda_i^k}{k!} = e^{\lambda_i}\tag{式11}
$$

したがって：

$$
e^\Lambda = \operatorname{diag}\big(e^{\lambda_1},\dots,e^{\lambda_n}\big)\tag{式12}
$$

---

### ステップ4：対角行列の行列式を計算する

対角行列の行列式は対角成分の積である（後述の補足参照）：

$$
\det(e^\Lambda) = e^{\lambda_1}\cdot e^{\lambda_2}\cdots e^{\lambda_n} = \prod_{i=1}^ne^{\lambda_i}\tag{式13}
$$

指数法則 $e^{x_1}\cdots e^{x_n}=e^{x_1+\cdots+x_n}$ を使う：

$$
\det(e^\Lambda) = e^{\sum_i\lambda_i}\tag{式14}
$$

式14を式8に代入すると：

$$
\det\big(e^A\big) = e^{\sum_i\lambda_i}\tag{式15}
$$

---

### ステップ5：$\sum_i\lambda_i = \operatorname{tr}(A)$ を示す

$\Lambda$ のトレースは定義より：

$$
\operatorname{tr}(\Lambda) = \lambda_1+\cdots+\lambda_n = \sum_i\lambda_i\tag{式16}
$$

トレースの巡回性 $\operatorname{tr}(XY)=\operatorname{tr}(YX)$ を $\operatorname{tr}(A)=\operatorname{tr}(P\Lambda P^{-1})$ に適用する（$X=P\Lambda,\ Y=P^{-1}$）：

$$
\operatorname{tr}(A) = \operatorname{tr}(P\Lambda P^{-1}) = \operatorname{tr}(P^{-1}P\Lambda) = \operatorname{tr}(I\Lambda) = \operatorname{tr}(\Lambda)\tag{式17}
$$

式16・17より：

$$
\sum_i\lambda_i = \operatorname{tr}(A)\tag{式18}
$$

---

### 結論

式18を式15に代入すると：

$$
\boxed{\det(e^A) = e^{\operatorname{tr}(A)}}
$$

---

## 証明2：一般の場合（Jacobiの公式を使う）

対角化できない行列（ジョルダン標準形が必要な行列）も含む一般的な証明。ラプラス・ベルトラミ作用素の議論で使ったJacobiの公式を再利用する。

### Jacobiの公式（再掲）

任意の正則行列 $M$ について：

$$
\partial_l\ln|\det M| = \operatorname{tr}(M^{-1}\partial_lM)\tag{式19}
$$

（導出：$M+dM=M(I+M^{-1}dM)$ から $\det(I+\varepsilon X)\approx1+\varepsilon\operatorname{tr}X$ を使う。）

### 適用

$M(t):=e^{tA}$ とおくと、テイラー展開の項別微分より：

$$
\frac{d}{dt}e^{tA} = Ae^{tA}\tag{式20}
$$

式19に $M(t)=e^{tA}$、$\partial_l\to\dfrac{d}{dt}$ を代入する：

$$
\frac{d}{dt}\ln\det\big(e^{tA}\big) = \operatorname{tr}\!\left(\big(e^{tA}\big)^{-1}\cdot Ae^{tA}\right) = \operatorname{tr}\!\left(e^{-tA}Ae^{tA}\right)\tag{式21}
$$

トレースの巡回性 $\operatorname{tr}(XYZ)=\operatorname{tr}(YZX)$ を使う：

$$
\operatorname{tr}(e^{-tA}Ae^{tA}) = \operatorname{tr}(Ae^{tA}e^{-tA}) = \operatorname{tr}(A)\tag{式22}
$$

（$e^{tA}e^{-tA}=I$ なので。）したがって：

$$
\frac{d}{dt}\ln\det\big(e^{tA}\big) = \operatorname{tr}(A)\tag{式23}
$$

右辺は $t$ に依存しない定数。両辺を $t$ で積分し、初期条件 $t=0$ で $\ln\det(e^0)=\ln\det I=0$ を使うと：

$$
\ln\det\big(e^{tA}\big) = t\cdot\operatorname{tr}(A)\tag{式24}
$$

$t=1$ を代入して：

$$
\boxed{\det(e^A) = e^{\operatorname{tr}(A)}}
$$

**この証明は $A$ が対角化できるかどうかに一切依存しない。**

---

## 補足：対角行列の行列式が対角成分の積になる理由

### $2\times2$ の確認

$$
\det\begin{pmatrix}\mu_1&0\\0&\mu_2\end{pmatrix} = \mu_1\mu_2 - 0\cdot0 = \mu_1\mu_2
$$

非対角成分が $0$ なので引き算の項が消える。

### $3\times3$ の確認（余因子展開）

1行目に沿って展開すると、非対角成分（0）が掛かる項はすべて消え：

$$
\det\begin{pmatrix}\mu_1&0&0\\0&\mu_2&0\\0&0&\mu_3\end{pmatrix} = \mu_1\cdot\det\begin{pmatrix}\mu_2&0\\0&\mu_3\end{pmatrix} = \mu_1\cdot\mu_2\mu_3 = \mu_1\mu_2\mu_3
$$

### 一般の $n\times n$（数学的帰納法）

$n\times n$ の対角行列を1行目に沿って余因子展開すると、生き残るのは $j=1$ の項だけ：

$$
\det D = \mu_1\cdot\det(D^{(1,1)})
$$

$D^{(1,1)}$ は $\operatorname{diag}(\mu_2,\dots,\mu_n)$ という1次小さい対角行列なので、帰納法の仮定より $\det(D^{(1,1)})=\mu_2\cdots\mu_n$。したがって：

$$
\det D = \mu_1\mu_2\cdots\mu_n = \prod_{i=1}^n\mu_i
$$

### 幾何学的な意味

計量テンソルのノートで扱った「行列式 = 体積の拡大率」という視点：対角行列は各座標軸を独立に $\mu_i$ 倍するだけなので、全体の体積拡大率は $\mu_1\mu_2\cdots\mu_n$ の単純な積になる。

---

## 全体の流れ（振り返り）

```
証明1（対角化できる場合）
    式1〜4 : A = PΛP⁻¹ と「相似変換を指数に通す公式」→ e^A = Pe^Λ P⁻¹
    式5〜8 : det を取り、det(P)det(P⁻¹)=1 で消去 → det(e^A) = det(e^Λ)
    式9〜14: e^Λ を対角成分ごとに計算 → det(e^Λ) = e^(Σλᵢ)
    式15〜18: トレースの巡回性 → Σλᵢ = tr(A)
    → det(e^A) = e^(tr A)

証明2（一般の場合）
    M(t) = e^(tA) にJacobiの公式を適用
    → d/dt ln det(e^(tA)) = tr(A)（定数）
    → 積分 + 初期条件 → ln det(e^A) = tr(A)
    → det(e^A) = e^(tr A)
```

## この公式の意味

パウリ行列のノート Part I で使った論理を再掲する：

$$
U = e^{iA} \text{ がユニタリ（}U^\dagger U=I\text{）かつ } \det U=1 \text{ であるには}
$$

$$
\det U = \det(e^{iA}) = e^{i\operatorname{tr}A} = 1 \iff \operatorname{tr}A = 0
$$

つまり「$SU(2)$ の生成子はトレースゼロでなければならない」という条件は、この公式から直接従う。パウリ行列がトレースゼロのエルミート行列の基底である理由の根拠がここにある。

また、Jacobiの公式は計量テンソルのノートで $\sqrt{|g|}$ の微分（発散の補正項）を導く際に使った公式と同一であり、これまでの議論が再び一つに繋がっている。
