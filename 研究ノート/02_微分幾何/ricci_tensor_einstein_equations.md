# リッチテンソル・スカラー曲率・アインシュタイン方程式

クリストッフェル記号のノートPart IXで「紹介のみ」としていたリッチテンソル $R_{ij}$ とスカラー曲率 $R$ を、実際に手を動かして掘り下げます。特に「なぜこの縮約を取るのか」「計量の共変微分がなぜゼロになるのか」「球面で実際に$R_{ij}$を計算するとどうなるか」を、天下り的な提示を避けて導出します。

---

# Part I：リッチテンソルの定義 ―なぜこの縮約なのか

## 1. リーマン曲率テンソルの反対称性を、既存の公式から直接確認する

クリストッフェル記号のノートで導出した公式：

$$
R^l{}_{kij} = \partial_i\Gamma^l{}_{jk} - \partial_j\Gamma^l{}_{ik} + \Gamma^l{}_{im}\Gamma^m{}_{jk} - \Gamma^l{}_{jm}\Gamma^m{}_{ik}
$$

**この式で$i,j$を入れ替えてみます**：

$$
R^l{}_{kji} = \partial_j\Gamma^l{}_{ik} - \partial_i\Gamma^l{}_{jk} + \Gamma^l{}_{jm}\Gamma^m{}_{ik} - \Gamma^l{}_{im}\Gamma^m{}_{jk}
$$

これは、元の式のすべての項の符号を反転させたものと完全に一致します：

$$
\boxed{R^l{}_{kij} = -R^l{}_{kji}}\qquad\text{（最後の2つの添字について反対称）}
$$

**これは天下り的な性質ではなく、既に手元にある公式を眺めるだけで直接確認できます。**

## 2. ある縮約が、自動的にゼロになることの確認

逆計量$g^{ij}$（対称：$g^{ij}=g^{ji}$）を、この反対称な添字$i,j$に対して縮約してみます：

$$
g^{ij}R^l{}_{kij}
$$

**これは、以前ポアンカレの補題のノートで証明した「対称×反対称の和は必ずゼロになる」という一般補題そのものです**（$g^{ij}$が対称、$R^l{}_{kij}$が$i,j$について反対称なので）：

$$
\boxed{g^{ij}R^l{}_{kij} = 0}
$$

**つまり、最後の2つの添字（反対称なペア）を計量で縮約しても、何も情報が得られません。** 意味のある縮約は、**上付きの$l$と、下付き3つ（$k,i,j$）のうち、反対称なペア以外の添字**（つまり$k$）を組み合わせたものだけになります。

## 3. リッチテンソルの定義

$$
\boxed{R_{ij} := R^k{}_{ikj}}
$$

（上付き添字$l$を、下付き添字の1番目の場所（元の記法では$k$の位置）と縮約したもの。残った2つの添字を$i,j$と名付けています。）

## 4. なぜ「この」縮約が、本質的に唯一なのか（正直な限界）

上付き添字$l$を、下付き3つの添字（$k,i,j$）のどれと組み合わせるかで、原理的には3通りの縮約が考えられます。**2.で確認した通り、$i,j$（反対称なペア）との縮約は自動的にゼロ**なので、残るのは「$k$と縮約する」（今回採用した定義）か「$l$を残したまま、$i$または$j$と縮約する」かの、実質2択です。

**これらが（符号を除いて）同じものになる**ことは、リーマン曲率テンソルが持つ、もう一段深い対称性（**第一ビアンキ恒等式**：$R^l{}_{[kij]}=0$、3つの下付き添字を巡回的に足すとゼロになる、という性質）から従います。この恒等式は、$\Gamma$の対称性だけからさらに一段の計算が必要になるため、**今回は導出を割愛し、事実として受け入れます**（今回の球面の例では、後述する通り2次元なので独立成分が1つしかなく、この区別自体が問題にならないため、実害はありません）。

---

# Part II：計量の共変微分はゼロである（$\nabla g=0$）

## 5. 準備：以前導出済みの公式を思い出す

クリストッフェル記号のノートPart II・Part Vのキリングベクトルの計算で、次の関係式を導出済みでした：

$$
\boxed{2\Gamma^m{}_{ab}g_{mc} = \partial_ag_{bc}+\partial_bg_{ac}-\partial_cg_{ab}}
$$

## 6. $\nabla_ig_{jk}=0$ を導出する

計量$g_{jk}$（下付き添字2個のテンソル）の共変微分は、**リーマン曲率テンソルのノートPart VII §11で導出した一般規則**（下付き添字ごとに$-\Gamma$の項を独立に足す）に従います：

$$
\nabla_ig_{jk} = \partial_ig_{jk} - \Gamma^l{}_{ji}g_{lk} - \Gamma^l{}_{ki}g_{jl}
$$

**5.の公式を、2つの項それぞれに適用します**：

$$
\Gamma^l{}_{ji}g_{lk} = \frac12\big(\partial_jg_{ik}+\partial_ig_{jk}-\partial_kg_{ij}\big)\qquad(a=j,b=i,c=k\text{を代入})
$$

$$
\Gamma^l{}_{ki}g_{jl} = \frac12\big(\partial_kg_{ij}+\partial_ig_{kj}-\partial_jg_{ki}\big)\qquad(a=k,b=i,c=j\text{を代入})
$$

**2つを足します**（$g_{kj}=g_{jk}$、$g_{ki}=g_{ik}$を使用）：

$$
\Gamma^l{}_{ji}g_{lk}+\Gamma^l{}_{ki}g_{jl} = \frac12\Big[(\partial_jg_{ik}+\partial_ig_{jk}-\partial_kg_{ij})+(\partial_kg_{ij}+\partial_ig_{jk}-\partial_jg_{ik})\Big]
$$

**$\partial_jg_{ik}$と$-\partial_jg_{ik}$、$-\partial_kg_{ij}$と$+\partial_kg_{ij}$が、それぞれ打ち消し合います**：

$$
= \frac12\big[2\partial_ig_{jk}\big] = \partial_ig_{jk}
$$

## 7. 結論

$$
\nabla_ig_{jk} = \partial_ig_{jk} - \partial_ig_{jk} = \boxed{0}
$$

**計量は、共変微分してもゼロになります。** これは「計量と両立する接続」（メトリック接続、レヴィ・チヴィタ接続）と呼ばれる性質で、クリストッフェル記号を計量から導出した時点で、実は自動的に埋め込まれていた性質でした。今回、その埋め込まれていた性質を、明示的に確認したことになります。

---

# Part III：球面の具体例で、実際に計算する

クリストッフェル記号のノートPart VIIIで、球面（半径$a$、$q^1=\theta,q^2=\phi$）について、既に

$$
R^\theta{}_{\phi\theta\phi} = \sin^2\theta,\qquad \Gamma^\theta{}_{\phi\phi}=-\sin\theta\cos\theta,\qquad\Gamma^\phi{}_{\theta\phi}=\cot\theta
$$

を導出済みです。ここから、$R_{ij}$、$R$まで、実際に手を動かして計算します。

## 8. $R^\phi{}_{\theta\phi\theta}$ を計算する

$R_{\theta\theta}$を求めるには、$R^\theta{}_{\theta\theta\theta}$（後で見る通り自動的にゼロ）と$R^\phi{}_{\theta\phi\theta}$が必要です。定義式に$l=\phi,k=\theta,i=\phi,j=\theta$を代入します：

$$
R^\phi{}_{\theta\phi\theta} = \partial_\phi\Gamma^\phi{}_{\theta\theta} - \partial_\theta\Gamma^\phi{}_{\phi\theta} + \Gamma^\phi{}_{\phi m}\Gamma^m{}_{\theta\theta} - \Gamma^\phi{}_{\theta m}\Gamma^m{}_{\phi\theta}
$$

各項を計算します：

- $\Gamma^\phi{}_{\theta\theta}=0$（定数）なので $\partial_\phi\Gamma^\phi{}_{\theta\theta}=0$
- $\Gamma^\phi{}_{\phi\theta}=\Gamma^\phi{}_{\theta\phi}=\cot\theta$ なので $\partial_\theta\Gamma^\phi{}_{\phi\theta}=\partial_\theta(\cot\theta)=-\dfrac1{\sin^2\theta}$、したがって $-\partial_\theta\Gamma^\phi{}_{\phi\theta}=\dfrac1{\sin^2\theta}$
- $\Gamma^\phi{}_{\phi m}\Gamma^m{}_{\theta\theta}$：$\Gamma^m{}_{\theta\theta}=0$（$m=\theta,\phi$どちらも）なので、この項はゼロ
- $\Gamma^\phi{}_{\theta m}\Gamma^m{}_{\phi\theta}$：$m=\phi$の項だけ残る：$\Gamma^\phi{}_{\theta\phi}\Gamma^\phi{}_{\phi\theta}=\cot\theta\cdot\cot\theta=\cot^2\theta$、符号込みで$-\cot^2\theta$

まとめると：

$$
R^\phi{}_{\theta\phi\theta} = 0+\frac1{\sin^2\theta}+0-\cot^2\theta = \frac1{\sin^2\theta}-\frac{\cos^2\theta}{\sin^2\theta} = \frac{1-\cos^2\theta}{\sin^2\theta} = \frac{\sin^2\theta}{\sin^2\theta} = \boxed{1}
$$

## 9. $R_{\theta\theta}$、$R_{\phi\phi}$、$R_{\theta\phi}$ を計算する

$$
R_{\theta\theta} = R^\theta{}_{\theta\theta\theta}+R^\phi{}_{\theta\phi\theta}
$$

$R^\theta{}_{\theta\theta\theta}$は、Part I §1の反対称性（$i=j=\theta$の場合、$R^l{}_{kij}=-R^l{}_{kji}$で$i=j$とすると自動的にゼロ）から $R^\theta{}_{\theta\theta\theta}=0$。したがって：

$$
\boxed{R_{\theta\theta} = 0+1 = 1}
$$

$$
R_{\phi\phi} = R^\theta{}_{\phi\theta\phi}+R^\phi{}_{\phi\phi\phi} = \sin^2\theta+0
$$

$$
\boxed{R_{\phi\phi} = \sin^2\theta}
$$

$$
R_{\theta\phi} = R^\theta{}_{\theta\theta\phi}+R^\phi{}_{\theta\phi\phi}
$$

$R^\theta{}_{\theta\theta\phi}$は、$R^\theta{}_{\theta\phi\theta}$を計算すると（8.と同様の手順で、$\Gamma^\theta{}_{\theta\bullet}$がすべてゼロなためすべての項がゼロになることが確認できます）ゼロになり、反対称性からその符号反転もゼロ。$R^\phi{}_{\theta\phi\phi}$も、$i=j=\phi$なので反対称性から自動的にゼロです：

$$
\boxed{R_{\theta\phi} = 0}
$$

## 10. スカラー曲率 $R$ を計算する

$$
R = g^{ij}R_{ij} = g^{\theta\theta}R_{\theta\theta}+g^{\phi\phi}R_{\phi\phi}
$$

（非対角成分は$g^{\theta\phi}=0$なので寄与しません。）$g^{\theta\theta}=1/a^2$、$g^{\phi\phi}=1/(a^2\sin^2\theta)$を代入します：

$$
R = \frac1{a^2}\cdot1 + \frac1{a^2\sin^2\theta}\cdot\sin^2\theta = \frac1{a^2}+\frac1{a^2} = \boxed{\frac2{a^2}}
$$

## 11. ガウス曲率との一致を確認する

クリストッフェル記号のノートPart VIIIで、ガウス曲率$K=1/a^2$を導出済みでした。今回計算した$R=2/a^2$と見比べると：

$$
\boxed{R = 2K}
$$

**これが、Part IXで「単純な関係」として紹介だけしていた式の、実際の数値による確認です。** ただし、これはまだ**球面という1つの具体例**での確認にすぎません。次節で、球面に限らず、一般の2次元計量について証明します。

## 11-a. $R=2K$ を、一般の2次元計量で証明する（球面に限らない）

**直交座標系**（$g_{12}=0$、これまで扱った極座標・球座標はすべてこの形）で考えます。2次元では、以前多様体のノートPart II-bで確認した通り、リーマン曲率テンソルの独立成分は1つしかありません。この唯一の成分を$X:=R_{1212}$と置きます。

**リッチテンソルの対角成分を、$X$を使って計算します**。$R_{11}=R^k{}_{1k1}$の定義に戻り、$k=2$の項だけが生き残ること（反対称性から$k=1$の項は自動的にゼロ）を使うと：

$$
R_{11} = R^2{}_{121} = g^{22}R_{2121} = \frac1{g_{22}}R_{1212} = \frac{X}{g_{22}}
$$

（$R_{2121}=R_{1212}=X$は、以前確認した対のペア交換対称性から。）同様に：

$$
R_{22} = R^1{}_{212} = g^{11}R_{1212} = \frac{X}{g_{11}}
$$

**非対角成分$R_{12}$は、同様の計算をすると自動的にゼロになります**（反対称性から、生き残る項が存在しないため）。

**スカラー曲率を計算します**：

$$
R = g^{ij}R_{ij} = g^{11}R_{11}+g^{22}R_{22} = \frac1{g_{11}}\cdot\frac{X}{g_{22}}+\frac1{g_{22}}\cdot\frac{X}{g_{11}} = \frac{X}{g_{11}g_{22}}+\frac{X}{g_{11}g_{22}} = \frac{2X}{\det g}
$$

**一方、ガウス曲率は$K=X/\det g$**（$K=R_{\theta\phi\theta\phi}/\det g$の一般版、クリストッフェル記号のノート§16-eと同じ式）でした。したがって：

$$
\boxed{R = \frac{2X}{\det g} = 2K}
$$

**これで、球面という具体例に頼らず、任意の2次元計量について証明できました。**

**「2」の正体**：$g^{11}R_{11}$と$g^{22}R_{22}$を、それぞれ個別に計算すると：

$$
g^{11}R_{11} = \frac1{g_{11}}\cdot\frac{X}{g_{22}} = \frac{X}{\det g} = K,\qquad g^{22}R_{22} = \frac1{g_{22}}\cdot\frac{X}{g_{11}} = \frac{X}{\det g} = K
$$

**$g^{11}R_{11}$も$g^{22}R_{22}$も、それぞれ単独で$K$に等しくなっています。** つまり「2倍」は係数として掛かっているのではなく、**「$K$という同じ値を持つ項が、次元の数（2次元だから2個）だけ足し合わされている」**という構造でした。

## 11-b. 3次元以上では、どのような関係になるか

**高次元では、$K$という1つの数では曲率を表現しきれません。** 代わりに、**接空間内の2次元平面（断面）ごとに、異なる「断面曲率」**が定義されます：正規直交基底$\mathbf e_i,\mathbf e_j$が張る平面の断面曲率を$K_{ij}:=R_{ijij}$（$i\ne j$）とします。

**同じ手順（正規直交基底で対角成分を計算する）を$n$次元に一般化します。** $R_{ii}$（$i$番目の対角成分、和は取らない）は、$i$方向を含む、すべての2次元平面の断面曲率の和になります：

$$
R_{ii} = \sum_{k\ne i}K_{ik}
$$

これを$i$について全部足すと：

$$
R = \sum_iR_{ii} = \sum_i\sum_{k\ne i}K_{ik} = 2\sum_{i<j}K_{ij}
$$

（各ペア$(i,j)$が、和の中で$(i,k=j)$と$(k=i,j)$の2回数えられるため、$2$倍になります。）

$$
\boxed{R = 2\sum_{i<j}K_{ij}}
$$

**$n$次元では$\binom n2$個の断面曲率があり、$R$はその全部の和の2倍**です。$n=2$なら、ペアは$(1,2)$の1組だけなので$R=2K_{12}=2K$——**11-aで導出した式に、ちょうど戻ります。**

**空間が「等方的」（どの断面も同じ曲率$\kappa$を持つ、球面の高次元版）なら**：

$$
R = 2\times\binom n2\times\kappa = n(n-1)\kappa
$$

（$n$次元球面の標準的な公式。$n=2$なら$R=2\times1\times K=2K$、確かに一致します。）

$$
\boxed{
\begin{aligned}
&\text{2次元：}R=2K\text{（唯一の断面曲率が、対角成分2つ分そのまま現れる）}\\
&n\text{次元：}R=2\sum_{i<j}K_{ij}\text{（}\binom n2\text{個の断面曲率の和の2倍、"2"はペアの数え方に由来）}\\
&\text{等方的な場合：}R=n(n-1)\kappa\text{（}n=2\text{で}2K\text{に帰着）}
\end{aligned}
}
$$

---

# Part IV：アインシュタイン方程式（紹介）

## 12. 方程式の形

一般相対論の中心的な方程式は、次の形をしています：

$$
\boxed{R_{ij}-\frac12Rg_{ij}+\Lambda g_{ij} = 8\pi GT_{ij}}
$$

- $R_{ij},R$：今回計算した、リッチテンソル・スカラー曲率（時空の曲がり方）
- $g_{ij}$：計量
- $\Lambda$：宇宙定数
- $T_{ij}$：エネルギー・運動量テンソル（物質・エネルギーの分布）
- $G$：ニュートンの万有引力定数

**左辺（$R_{ij}-\frac12Rg_{ij}+\Lambda g_{ij}$）は「時空の曲がり方」、右辺（$8\pi GT_{ij}$）は「そこにある物質・エネルギーの量」を表し、両者が比例する、というのがこの方程式が主張する内容です。** 「物質はどう時空を曲げるか」「曲がった時空の中で物質はどう動くか」（後者が、以前扱った測地線方程式）という、2つの問いに同時に答える方程式になっています。

**この方程式自体の導出（変分原理・アインシュタイン-ヒルベルト作用からの導出）は、今回は踏み込みません**。今回できたのは、左辺に出てくる$R_{ij},R$を、実際に手を動かして計算できるようになった、というところまでです。

## 13. 真空解：$R_{ij}=0$ の意味

物質がない領域（$T_{ij}=0$、$\Lambda=0$の場合）では、方程式は $R_{ij}-\frac12Rg_{ij}=0$ となります。両辺の跡（トレース、$g^{ij}$を掛けて縮約）を取ると、$n$次元時空で $R-\frac n2R=0$、つまり$n\ne2$なら$R=0$、これを元の式に戻すと：

$$
\boxed{R_{ij}=0}\qquad\text{（真空のアインシュタイン方程式）}
$$

**重要な注意**：$R_{ij}=0$（リッチテンソルがゼロ）であっても、**リーマン曲率テンソル$R^l{}_{kij}$自体はゼロとは限りません**（縮約で情報が落ちるため）。実際、ブラックホールの周りの真空領域（シュワルツシルト解）は、$R_{ij}=0$を満たしながら、$R^l{}_{kij}\ne0$（潮汐力を生む、本物の曲率）を持ちます。**「リッチ平坦」と「完全に平坦（$R^l{}_{kij}=0$）」は別の概念**、というのは、以前の複素多様体のノートで扱った「カラビ・ヤウ多様体」（リッチ平坦だが、一般には完全に平坦ではない）の定義とも、まさに整合する注意点です。

---

# まとめ

$$
\boxed{
\begin{aligned}
&\text{リッチテンソル}R_{ij}=R^k{}_{ikj}\text{：反対称なペアとの縮約は自動的にゼロ（対称×反対称=0）になるため、実質的に}\\
&\quad\text{残る縮約はこれだけ（高次元での厳密な一意性は第一ビアンキ恒等式が必要、今回は割愛）}\\
&\nabla_ig_{jk}=0\text{：計量と接続の両立性、既存の公式から直接導出できる}\\
&\text{球面の具体例：}R_{\theta\theta}=1,R_{\phi\phi}=\sin^2\theta,R=2/a^2=2K\text{（ガウス曲率との一致を数値で確認）}\\
&\text{アインシュタイン方程式：}R_{ij}-\frac12Rg_{ij}+\Lambda g_{ij}=8\pi GT_{ij}\text{、真空解}R_{ij}=0\text{はリーマン曲率がゼロとは限らない}
\end{aligned}
}
$$

「紹介のみ」で終わっていたリッチテンソルが、これまでのノートで積み上げてきた道具（対称×反対称の相殺、共変微分の一般規則、球面の具体的な$\Gamma$）だけを使って、実際に計算できる対象になりました。アインシュタイン方程式自体の導出（変分原理）は、また別の機会の課題として残しておきます。
