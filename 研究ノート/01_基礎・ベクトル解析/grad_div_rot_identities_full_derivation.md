# $\operatorname{grad}(\mathbf u\cdot\mathbf v)$、$\operatorname{div}(\mathbf u\times\mathbf v)$、$\operatorname{rot}(\mathbf u\times\mathbf v)$ ―途中式を省略しない完全証明―

3つの公式に共通して使われている「省かれた途中式」の正体は、**存在しない項を、同じ値をゼロになるように足して引く（ゼロを足す）というテクニック**です。この操作が明示されずに使われているため、天下り的に見えてしまいます。ここでは、その「ゼロを足す」箇所も含めて、すべての項を書き出します。

記法：$\mathbf u=(u_1,u_2,u_3)$、$\mathbf v=(v_1,v_2,v_3)$（すべて$x,y,z$の関数）、$\partial_x,\partial_y,\partial_z$は各座標での偏微分。

---

# 1. $\operatorname{grad}(\mathbf u\cdot\mathbf v)$ の第1成分

## ステップ1：積の微分で、愚直に6項に展開する

$$
\partial_x(\mathbf u\cdot\mathbf v) = \partial_x(u_1v_1+u_2v_2+u_3v_3)
$$

積の微分公式 $\partial_x(fg)=(\partial_xf)g+f(\partial_xg)$ を3つの項それぞれに適用します（これは元のノートにもある通りです）：

$$
= (\partial_xu_1)v_1+u_1(\partial_xv_1) + (\partial_xu_2)v_2+u_2(\partial_xv_2) + (\partial_xu_3)v_3+u_3(\partial_xv_3)\tag{A}
$$

**この式Aには、$\partial_x$しか出てきません。$\partial_y,\partial_z$は一切含まれていません。** ここが重要な出発点です。

## ステップ2：目標の形を確認する

最終的に到達したいのは、次の4つのグループです：

$$
\underbrace{(\partial_xu_1)v_1+(\partial_yu_1)v_2+(\partial_zu_1)v_3}_{=(\operatorname{grad}u_1)\cdot\mathbf v} + \underbrace{(\partial_xv_1)u_1+(\partial_yv_1)u_2+(\partial_zv_1)u_3}_{=(\operatorname{grad}v_1)\cdot\mathbf u} + (\text{残り}) \tag{目標}
$$

**しかし式Aには $(\partial_yu_1)v_2$ や $(\partial_zu_1)v_3$ のような、$\partial_y,\partial_z$を含む項は1つも存在しません。** この2項をどこからか持ってこなければ、$(\operatorname{grad}u_1)\cdot\mathbf v$ という形を完成させられません。

## ステップ3：「ゼロを足す」―ここが省略されていた核心

そこで、次の4つの項を**足して、同時に同じものを引きます**（合計はゼロなので、式の値は変わりません）：

$$
\Big[(\partial_yu_1)v_2+(\partial_zu_1)v_3+(\partial_yv_1)u_2+(\partial_zv_1)u_3\Big] - \Big[(\partial_yu_1)v_2+(\partial_zu_1)v_3+(\partial_yv_1)u_2+(\partial_zv_1)u_3\Big] = 0
$$

これを式Aに加えます：

$$
\partial_x(\mathbf u\cdot\mathbf v) = \underbrace{(\partial_xu_1)v_1+u_1(\partial_xv_1)+(\partial_xu_2)v_2+u_2(\partial_xv_2)+(\partial_xu_3)v_3+u_3(\partial_xv_3)}_{\text{式A（元の6項）}}
$$
$$
\underbrace{+(\partial_yu_1)v_2+(\partial_zu_1)v_3+(\partial_yv_1)u_2+(\partial_zv_1)u_3}_{\text{足した4項}}\ \underbrace{-(\partial_yu_1)v_2-(\partial_zu_1)v_3-(\partial_yv_1)u_2-(\partial_zv_1)u_3}_{\text{引いた4項}}
$$

**全部で14項**（元の6項＋足した4項＋引いた4項）になりました。多く見えますが、ここから**足した4項**を使って$(\operatorname{grad}u_1)\cdot\mathbf v$と$(\operatorname{grad}v_1)\cdot\mathbf u$を作り、残りをまとめます。

## ステップ4：14項を並べ替えてグループ分けする

**グループ1**（式Aの$(\partial_xu_1)v_1$ ＋ 足した2項）：

$$
(\partial_xu_1)v_1+(\partial_yu_1)v_2+(\partial_zu_1)v_3 = (\operatorname{grad}u_1)\cdot\mathbf v
$$

**グループ2**（式Aの$u_1(\partial_xv_1)$ ＋ 足した2項）：

$$
u_1(\partial_xv_1)+(\partial_yv_1)u_2+(\partial_zv_1)u_3 = (\partial_xv_1)u_1+(\partial_yv_1)u_2+(\partial_zv_1)u_3=(\operatorname{grad}v_1)\cdot\mathbf u
$$

**グループ3**（式Aの残り2項 ＋ 引いた2項）：

$$
(\partial_xu_2)v_2+u_2(\partial_xv_2)-(\partial_yv_1)u_2-(\partial_zu_1)v_3\ \ (\text{一部})\dots
$$

ここで丁寧に、残った項をすべて書き出します。式Aから使ったのは$(\partial_xu_1)v_1$と$u_1\partial_xv_1$の2項だけなので、**式Aの残り4項**：

$$
(\partial_xu_2)v_2,\quad u_2(\partial_xv_2),\quad(\partial_xu_3)v_3,\quad u_3(\partial_xv_3)
$$

と、**引いた4項**：

$$
-(\partial_yu_1)v_2,\quad-(\partial_zu_1)v_3,\quad-(\partial_yv_1)u_2,\quad-(\partial_zv_1)u_3
$$

の、合計8項が残ります。これを整理すると：

$$
\big[(\partial_xu_2)v_2-(\partial_yv_1)u_2\big] + \big[u_2(\partial_xv_2)-(\partial_yu_1)v_2\big] + \big[(\partial_xu_3)v_3-(\partial_zv_1)u_3\big] + \big[u_3(\partial_xv_3)-(\partial_zu_1)v_3\big]
$$

これを $u_2,u_3$ でくくる組と $v_2,v_3$ でくくる組に分けます：

$$
\underbrace{u_2\big[(\partial_xv_2)-(\partial_yv_1)\big]-u_3\big[(\partial_zv_1)-(\partial_xv_3)\big]}_{=:G_3} + \underbrace{v_2\big[(\partial_xu_2)-(\partial_yu_1)\big]-v_3\big[(\partial_zu_1)-(\partial_xu_3)\big]}_{=:G_4}
$$

（符号に注意：$-(\partial_zu_1)v_3+u_3(\partial_xv_3)=u_3(\partial_xv_3-\partial_zv_1)$ となるよう、$-u_3$でくくっています。）これがまさに元のノートに出てきた $G_3,G_4$ の形です。

## ステップ5：$G_3,G_4$ を外積として認識する

$\operatorname{rot}$は、次の3成分で**定義**されます（導出するものではなく、これが定義です）：

$$
\operatorname{rot}\mathbf v := (\partial_yv_3-\partial_zv_2,\ \ \partial_zv_1-\partial_xv_3,\ \ \partial_xv_2-\partial_yv_1)
$$

外積 $\mathbf a\times\mathbf b$ の成分も定義であり、添字が$1\to2\to3\to1$と循環する規則を持ちます：

$$
(\mathbf a\times\mathbf b)_1=a_2b_3-a_3b_2,\qquad (\mathbf a\times\mathbf b)_2=a_3b_1-a_1b_3,\qquad(\mathbf a\times\mathbf b)_3=a_1b_2-a_2b_1
$$

$[\mathbf u\times\operatorname{rot}\mathbf v]_1$ を計算するには、$(\mathbf a\times\mathbf b)_1=a_2b_3-a_3b_2$ の公式に $\mathbf a=\mathbf u,\ \mathbf b=\operatorname{rot}\mathbf v$ を当てはめます：

$$
[\mathbf u\times\operatorname{rot}\mathbf v]_1 = u_2\cdot(\operatorname{rot}\mathbf v)_3-u_3\cdot(\operatorname{rot}\mathbf v)_2
$$

$\operatorname{rot}\mathbf v$の第3成分$(\partial_xv_2-\partial_yv_1)$と第2成分$(\partial_zv_1-\partial_xv_3)$を代入すると：

$$
[\mathbf u\times\operatorname{rot}\mathbf v]_1 = u_2(\partial_xv_2-\partial_yv_1)-u_3(\partial_zv_1-\partial_xv_3)
$$

これが$G_3$と完全に一致します。同様に、$(\mathbf a\times\mathbf b)_1$の公式に$\mathbf a=\mathbf v,\mathbf b=\operatorname{rot}\mathbf u$を当てはめると $G_4=[\mathbf v\times\operatorname{rot}\mathbf u]_1$ が確認できます。

## 第2成分（$\partial_y(\mathbf u\cdot\mathbf v)$）でも同じパターンが成立することの検証

「各成分の対称性から分かる」という一文は、天下り的な省略ではなく、**添字を$1\to2\to3\to1$と循環的にずらすだけで、まったく同じ論理が繰り返される**という意味です。ただし「最初から式の中に存在する項」が成分ごとに変わる点に注意して、実際に確認します。

$\partial_y(\mathbf u\cdot\mathbf v)$を積の微分で展開すると：

$$
(\partial_yu_1)v_1+u_1(\partial_yv_1)+(\partial_yu_2)v_2+u_2(\partial_yv_2)+(\partial_yu_3)v_3+u_3(\partial_yv_3)
$$

$x$成分のときは$(\partial_xu_1)v_1$が最初から存在していましたが、**$y$成分では代わりに$(\partial_yu_2)v_2$が最初から存在**しています（添字の役割が循環的にずれるため）。目標 $(\operatorname{grad}u_2)\cdot\mathbf v+(\operatorname{grad}v_2)\cdot\mathbf u+[\mathbf u\times\operatorname{rot}\mathbf v]_2+[\mathbf v\times\operatorname{rot}\mathbf u]_2$ を作るために、$(\partial_xu_2)v_1,(\partial_zu_2)v_3,(\partial_xv_2)u_1,(\partial_zv_2)u_3$の4項を足して引きます。

グループ1・2：

$$
(\partial_yu_2)v_2+(\partial_xu_2)v_1+(\partial_zu_2)v_3 = (\operatorname{grad}u_2)\cdot\mathbf v
$$
$$
u_2(\partial_yv_2)+(\partial_xv_2)u_1+(\partial_zv_2)u_3 = (\operatorname{grad}v_2)\cdot\mathbf u
$$

残った8項を整理すると：

$$
u_1\partial_yv_1+u_3\partial_yv_3-u_3\partial_zv_2-u_1\partial_xv_2 = u_3(\partial_yv_3-\partial_zv_2)-u_1(\partial_xv_2-\partial_yv_1)
$$

外積の第2成分公式 $(\mathbf a\times\mathbf b)_2=a_3b_1-a_1b_3$ を使うと、これはちょうど $u_3(\operatorname{rot}\mathbf v)_1-u_1(\operatorname{rot}\mathbf v)_3=[\mathbf u\times\operatorname{rot}\mathbf v]_2$ です。$v$側の残り4項も同様に $[\mathbf v\times\operatorname{rot}\mathbf u]_2$ に一致します。

**これで、$y$成分でも確かに同じ構造（添字を1つずつ循環させるだけ）で証明が成立することが、実際の計算で確認できました。** $z$成分についても、まったく同じ手順（$1\to2\to3\to1$をもう一段ずらす）で成立します。

## 結論

$$
\boxed{\partial_x(\mathbf u\cdot\mathbf v) = (\operatorname{grad}u_1)\cdot\mathbf v + (\operatorname{grad}v_1)\cdot\mathbf u + (\mathbf u\times\operatorname{rot}\mathbf v)_1+(\mathbf v\times\operatorname{rot}\mathbf u)_1}
$$

**省略されていた核心は「$(\partial_yu_1)v_2$などの4項を、値を変えずに足して引く」という操作**でした。この4項は最初はどこにも存在しませんでしたが、$(\operatorname{grad}u_1)\cdot\mathbf v$という「完成させたい形」を作るために、意図的に挿入されたものです。

---

# 2. $\operatorname{div}(\mathbf u\times\mathbf v)$

こちらは「ゼロを足す」テクニックは不要で、**最初から必要な項がすべて揃っている**ため、純粋に「展開して並べ替える」だけで証明できます。

## ステップ1：$\mathbf u\times\mathbf v$ の各成分を確認する

$$
\mathbf u\times\mathbf v = (u_2v_3-u_3v_2,\ u_3v_1-u_1v_3,\ u_1v_2-u_2v_1)
$$

## ステップ2：divの定義通りに微分し、積の微分で展開する

$$
\operatorname{div}(\mathbf u\times\mathbf v) = \partial_x(u_2v_3-u_3v_2)+\partial_y(u_3v_1-u_1v_3)+\partial_z(u_1v_2-u_2v_1)
$$

各項を積の微分で展開します（3つの微分×2項＝6回の積の微分＝**合計12項**）：

$$
\partial_x(u_2v_3-u_3v_2) = (\partial_xu_2)v_3+u_2(\partial_xv_3) - (\partial_xu_3)v_2-u_3(\partial_xv_2)
$$
$$
\partial_y(u_3v_1-u_1v_3) = (\partial_yu_3)v_1+u_3(\partial_yv_1) - (\partial_yu_1)v_3-u_1(\partial_yv_3)
$$
$$
\partial_z(u_1v_2-u_2v_1) = (\partial_zu_1)v_2+u_1(\partial_zv_2) - (\partial_zu_2)v_1-u_2(\partial_zv_1)
$$

## ステップ3：12項を「$v_i$の係数になっている項」と「$u_i$の係数になっている項」に仕分ける

**$v_1$の係数を持つ項**（2つ）：$(\partial_yu_3)v_1,\ -(\partial_zu_2)v_1$

$$
(\partial_yu_3)v_1-(\partial_zu_2)v_1 = (\partial_yu_3-\partial_zu_2)v_1 = (\operatorname{rot}\mathbf u)_1\cdot v_1
$$

**$v_2$の係数を持つ項**（2つ）：$-(\partial_xu_3)v_2,\ (\partial_zu_1)v_2$

$$
-(\partial_xu_3)v_2+(\partial_zu_1)v_2 = (\partial_zu_1-\partial_xu_3)v_2 = (\operatorname{rot}\mathbf u)_2\cdot v_2
$$

**$v_3$の係数を持つ項**（2つ）：$(\partial_xu_2)v_3,\ -(\partial_yu_1)v_3$

$$
(\partial_xu_2)v_3-(\partial_yu_1)v_3 = (\partial_xu_2-\partial_yu_1)v_3 = (\operatorname{rot}\mathbf u)_3\cdot v_3
$$

この3つを足すと：

$$
(\operatorname{rot}\mathbf u)_1v_1+(\operatorname{rot}\mathbf u)_2v_2+(\operatorname{rot}\mathbf u)_3v_3 = (\operatorname{rot}\mathbf u)\cdot\mathbf v
$$

**残りの6項**（$u_1,u_2,u_3$が係数になっている項）も同様に仕分けます：

$u_1$の係数：$-u_1(\partial_yv_3),\ u_1(\partial_zv_2)$ → $-u_1(\partial_yv_3-\partial_zv_2)=-u_1(\operatorname{rot}\mathbf v)_1$

$u_2$の係数：$u_2(\partial_xv_3),\ -u_2(\partial_zv_1)$ → $-u_2(\partial_zv_1-\partial_xv_3)=-u_2(\operatorname{rot}\mathbf v)_2$

$u_3$の係数：$-u_3(\partial_xv_2),\ u_3(\partial_yv_1)$ → $-u_3(\partial_xv_2-\partial_yv_1)=-u_3(\operatorname{rot}\mathbf v)_3$

合計すると $-\mathbf u\cdot(\operatorname{rot}\mathbf v)$。

## 結論

$$
\boxed{\operatorname{div}(\mathbf u\times\mathbf v) = (\operatorname{rot}\mathbf u)\cdot\mathbf v - \mathbf u\cdot(\operatorname{rot}\mathbf v)}
$$

**この証明では「ゼロを足す」操作は不要**で、最初から出てきた12項を、$v_1,v_2,v_3$係数の3項ずつ、$u_1,u_2,u_3$係数の3項ずつに仕分けるだけで完成します。1番目のgradの証明との違いが、この点にあります。

---

# 3. $\operatorname{rot}(\mathbf u\times\mathbf v)$ の第1成分

## ステップ1：$\operatorname{rot}$の第1成分の定義に代入する

$\mathbf w:=\mathbf u\times\mathbf v=(w_1,w_2,w_3)$、$w_2=u_3v_1-u_1v_3$、$w_3=u_1v_2-u_2v_1$ として：

$$
(\operatorname{rot}\mathbf w)_1 = \partial_yw_3-\partial_zw_2 = \partial_y(u_1v_2-u_2v_1)-\partial_z(u_3v_1-u_1v_3)
$$

## ステップ2：積の微分で8項に展開する

$$
\partial_y(u_1v_2-u_2v_1) = (\partial_yu_1)v_2+u_1(\partial_yv_2)-(\partial_yu_2)v_1-u_2(\partial_yv_1)
$$
$$
\partial_z(u_3v_1-u_1v_3) = (\partial_zu_3)v_1+u_3(\partial_zv_1)-(\partial_zu_1)v_3-u_1(\partial_zv_3)
$$

2番目の式全体にマイナスがかかることに注意して引き算すると（**合計8項**）：

$$
(\operatorname{rot}\mathbf w)_1 = (\partial_yu_1)v_2+u_1(\partial_yv_2)-(\partial_yu_2)v_1-u_2(\partial_yv_1) -(\partial_zu_3)v_1-u_3(\partial_zv_1)+(\partial_zu_1)v_3+u_1(\partial_zv_3)\tag{B}
$$

**式Bには$\partial_x$を含む項が1つもありません。** $\partial_y,\partial_z$の8項だけです。

## ステップ3：目標の形を確認する

到達したいのは：

$$
(\operatorname{grad}u_1)\cdot\mathbf v - (\operatorname{grad}v_1)\cdot\mathbf u + u_1(\operatorname{div}\mathbf v)-v_1(\operatorname{div}\mathbf u)
$$

これを全展開すると：

$$
\underbrace{(\partial_xu_1)v_1+(\partial_yu_1)v_2+(\partial_zu_1)v_3}_{(\operatorname{grad}u_1)\cdot\mathbf v} - \underbrace{\big[(\partial_xv_1)u_1+(\partial_yv_1)u_2+(\partial_zv_1)u_3\big]}_{(\operatorname{grad}v_1)\cdot\mathbf u}
$$
$$
+\underbrace{u_1(\partial_xv_1+\partial_yv_2+\partial_zv_3)}_{u_1\operatorname{div}\mathbf v} - \underbrace{v_1(\partial_xu_1+\partial_yu_2+\partial_zu_3)}_{v_1\operatorname{div}\mathbf u}
$$

これは**16項**（4項×4グループ）ありますが、**$\partial_x$を含む項が4つ**混ざっています：$(\partial_xu_1)v_1$、$-(\partial_xv_1)u_1$、$u_1\partial_xv_1$、$-v_1\partial_xu_1$。式Bには$\partial_x$の項が存在しなかったので、これらは**互いに打ち消し合ってゼロにならなければ、そもそも一致しない**はずです。実際に確認します：

$$
(\partial_xu_1)v_1\ -\ (\partial_xv_1)u_1\ +\ u_1(\partial_xv_1)\ -\ v_1(\partial_xu_1)
$$

$(\partial_xu_1)v_1$ と $-v_1(\partial_xu_1)$ は同じ量の符号違いなので**打ち消し合ってゼロ**。$-(\partial_xv_1)u_1$ と $u_1(\partial_xv_1)$ も同様に**打ち消し合ってゼロ**。

**4つの$\partial_x$項は、目標の式の中で自動的に相殺してゼロになる**、というのがこの証明の核心です（1番目のgradの証明とは逆に、ここでは「余計な項を足す」のではなく、「もともと式の中にある$\partial_x$項同士が勝手に消える」というのがポイントです）。

## ステップ4：残った12項（$\partial_y,\partial_z$の項）を確認する

$\partial_x$の4項を除いた、残り12項は：

$$
(\partial_yu_1)v_2+(\partial_zu_1)v_3 -(\partial_yv_1)u_2-(\partial_zv_1)u_3 + u_1\partial_yv_2+u_1\partial_zv_3 - v_1\partial_yu_2-v_1\partial_zu_3
$$

（これは8項ですが、式が長いので念のため：$(\operatorname{grad}u_1)\cdot\mathbf v$から2項、$-(\operatorname{grad}v_1)\cdot\mathbf u$から2項、$u_1\operatorname{div}\mathbf v$から2項、$-v_1\operatorname{div}\mathbf u$から2項の、合計8項です。）

これが、式Bの8項と**1つずつ完全に一致する**ことを確認します：

| 式Bの項 | 目標側の対応する項 |
|---|---|
| $(\partial_yu_1)v_2$ | $(\partial_yu_1)v_2$ |
| $u_1(\partial_yv_2)$ | $u_1\partial_yv_2$ |
| $-(\partial_yu_2)v_1$ | $-v_1\partial_yu_2$（同じもの） |
| $-u_2(\partial_yv_1)$ | $-(\partial_yv_1)u_2$（同じもの） |
| $-(\partial_zu_3)v_1$ | $-v_1\partial_zu_3$（同じもの） |
| $-u_3(\partial_zv_1)$ | $-(\partial_zv_1)u_3$（同じもの） |
| $(\partial_zu_1)v_3$ | $(\partial_zu_1)v_3$ |
| $u_1(\partial_zv_3)$ | $u_1\partial_zv_3$ |

**8項すべて一致しました。**

## 結論

$$
\boxed{(\operatorname{rot}(\mathbf u\times\mathbf v))_1 = (\operatorname{grad}u_1)\cdot\mathbf v - (\operatorname{grad}v_1)\cdot\mathbf u + u_1(\operatorname{div}\mathbf v)-v_1(\operatorname{div}\mathbf u)}
$$

**この証明で省略されていたのは、「目標の式に含まれる4つの$\partial_x$項が、実は互いに打ち消し合ってゼロになる」という確認**でした。式Bには最初から$\partial_x$が登場しないので、目標の式の$\partial_x$部分が自動的にゼロになることを示さなければ、両辺が食い違って見えてしまいます。

---

# まとめ：3つの証明に共通する「省略されていたロジック」

$$
\boxed{
\begin{aligned}
&\operatorname{grad}(\mathbf u\cdot\mathbf v)\text{の証明：存在しない項を「足して引く」（ゼロを足す）ことで、}\operatorname{grad}\text{の形を人為的に作り出す}\\
&\operatorname{div}(\mathbf u\times\mathbf v)\text{の証明：ゼロを足す必要はなく、最初からある項を}v_i,u_i\text{の係数で仕分けるだけ}\\
&\operatorname{rot}(\mathbf u\times\mathbf v)\text{の証明：目標の式の中に紛れ込む}\partial_x\text{の4項が、実は自動的に打ち消し合ってゼロになる、という逆方向の確認が必要}
\end{aligned}
}
$$

いずれも、**「積の微分で愚直に展開した項」と「目標の式を展開した項」が、実は同じ項の集まりである**ということを、1つずつ照合することで証明が完結します。教科書やノートでこの過程が省略されるのは、照合の作業自体は機械的（かつ長い）ので、結果の対応関係だけを見せて「詳細は自分で確認してください」というスタンスを取っているからだと思われます。今回のように全項を書き出して照合すれば、天下り的に見える部分は一切なくなります。

---

# 補足：$\varepsilon$-$\delta$恒等式による導出型の証明

上の3つの証明は、いずれも**答えの形をあらかじめ知っていないと組み立てられない「検証型」の証明**でした。ここでは、答えを一切仮定せず、恒等式だけから機械的に計算を進めて、自動的に答えに辿り着く「**導出型**」**の証明**を行います。

## 0. 記法の準備

添字 $i,j,k,l,m$ はすべて $1,2,3$（$x,y,z$に対応）を走り、**同じ添字が1つの項の中に2回現れたら、その添字について和を取る**（アインシュタインの縮約記法）というルールを使います。$\partial_i:=\partial/\partial x_i$。

外積とrotは、$\varepsilon_{ijk}$を使って

$$
(\mathbf a\times\mathbf b)_i = \varepsilon_{ijk}a_jb_k,\qquad (\operatorname{rot}\mathbf a)_i = \varepsilon_{ijk}\partial_ja_k
$$

と書けます。

## 1. 鍵となる恒等式：$\varepsilon_{ijk}\varepsilon_{klm}=\delta_{il}\delta_{jm}-\delta_{im}\delta_{jl}$

この恒等式（証明済みの代数的事実として使います）を、簡単に検算しておきます。$i=1,j=2$とすると、$\varepsilon_{12k}$は$k=3$のときだけ非ゼロ（$\varepsilon_{123}=1$）なので：

$$
\varepsilon_{12k}\varepsilon_{klm} = \varepsilon_{123}\varepsilon_{3lm} = \varepsilon_{3lm}
$$

$(l,m)=(1,2)$なら$\varepsilon_{312}=1$（$(3,1,2)$は$(1,2,3)$の偶置換）。右辺は$\delta_{1\cdot1}\delta_{2\cdot2}-\delta_{1\cdot2}\delta_{2\cdot1}=1\cdot1-0\cdot0=1$、一致。$(l,m)=(2,1)$なら$\varepsilon_{321}=-1$。右辺は$\delta_{12}\delta_{21}-\delta_{11}\delta_{22}=0-1=-1$、これも一致します。

また、$\varepsilon_{ijk}$の添字を2つ入れ替えると符号が反転する（完全反対称）という性質も使います：$\varepsilon_{ijk}=-\varepsilon_{jik}$、また$\varepsilon_{ijk}=\varepsilon_{jki}=\varepsilon_{kij}$（3つとも循環置換なので符号は変わらない）。

## 2. $\operatorname{div}(\mathbf u\times\mathbf v)$ の導出（一番簡単）

$$
\operatorname{div}(\mathbf u\times\mathbf v) = \partial_i(\mathbf u\times\mathbf v)_i = \partial_i(\varepsilon_{ijk}u_jv_k) = \varepsilon_{ijk}\big[(\partial_iu_j)v_k+u_j(\partial_iv_k)\big]
$$

（$\varepsilon_{ijk}$は定数なので、積の微分の外に出せます。）2つの項に分けます。

**第1項**：$\varepsilon_{ijk}(\partial_iu_j)v_k$。ここで$\varepsilon_{ijk}=\varepsilon_{kij}$（循環置換）を使うと：

$$
\varepsilon_{ijk}(\partial_iu_j)v_k = \varepsilon_{kij}(\partial_iu_j)v_k = \big[\varepsilon_{kij}\partial_iu_j\big]v_k = (\operatorname{rot}\mathbf u)_k\,v_k = (\operatorname{rot}\mathbf u)\cdot\mathbf v
$$

**第2項**：$\varepsilon_{ijk}u_j(\partial_iv_k)$。ここで$\varepsilon_{ijk}=-\varepsilon_{jik}$（$i,j$を入れ替えると符号反転）を使うと：

$$
\varepsilon_{ijk}u_j(\partial_iv_k) = -\varepsilon_{jik}u_j(\partial_iv_k) = -u_j\big[\varepsilon_{jik}\partial_iv_k\big] = -u_j(\operatorname{rot}\mathbf v)_j = -\mathbf u\cdot(\operatorname{rot}\mathbf v)
$$

## 結論

$$
\boxed{\operatorname{div}(\mathbf u\times\mathbf v) = (\operatorname{rot}\mathbf u)\cdot\mathbf v - \mathbf u\cdot(\operatorname{rot}\mathbf v)}
$$

**恒等式$\varepsilon_{ijk}\varepsilon_{klm}$すら使わず、$\varepsilon$の添字を入れ替えるだけで証明が終わりました。** ゼロを足す操作は一切登場していません。

## 3. $\operatorname{grad}(\mathbf u\cdot\mathbf v)$ の導出

$$
\partial_i(\mathbf u\cdot\mathbf v) = \partial_i(u_kv_k) = (\partial_iu_k)v_k+u_k(\partial_iv_k)
$$

目標に近づけるため、まず$[\mathbf u\times\operatorname{rot}\mathbf v]_i$を計算してみます（天下り的に「これを目標に使おう」と決めているわけではなく、$\mathbf u\times\operatorname{rot}\mathbf v$という自然な量を計算したら何が出てくるか確認しているだけです）：

$$
[\mathbf u\times\operatorname{rot}\mathbf v]_i = \varepsilon_{ijk}u_j(\operatorname{rot}\mathbf v)_k = \varepsilon_{ijk}u_j\big(\varepsilon_{klm}\partial_lv_m\big) = \varepsilon_{ijk}\varepsilon_{klm}\,u_j\partial_lv_m
$$

恒等式$\varepsilon_{ijk}\varepsilon_{klm}=\delta_{il}\delta_{jm}-\delta_{im}\delta_{jl}$を代入します：

$$
= (\delta_{il}\delta_{jm}-\delta_{im}\delta_{jl})\,u_j\partial_lv_m
$$

$\delta$は「添字をすり替える」働きをします（$\delta_{il}$は$l$を$i$に、$\delta_{jm}$は$m$を$j$に、というように）：

$$
= u_j\partial_iv_j - u_j\partial_jv_i
$$

第2項$u_j\partial_jv_i$はまさに方向微分$(\mathbf u\cdot\nabla)v_i$なので：

$$
[\mathbf u\times\operatorname{rot}\mathbf v]_i = u_j\partial_iv_j - (\mathbf u\cdot\nabla)v_i
$$

移項すると：

$$
u_j\partial_iv_j = [\mathbf u\times\operatorname{rot}\mathbf v]_i + (\mathbf u\cdot\nabla)v_i = [\mathbf u\times\operatorname{rot}\mathbf v]_i + (\operatorname{grad}v_i)\cdot\mathbf u
$$

（$(\mathbf u\cdot\nabla)v_i=u_j\partial_jv_i=(\operatorname{grad}v_i)\cdot\mathbf u$、grad$v_i$の各成分$\partial_jv_i$を$u_j$と内積を取っているだけです。）

**ここで、左辺の添字を$j$から$k$に付け替えます**：$u_j\partial_iv_j$は$j$について和を取っている（$j=1,2,3$を全部代入して足し合わせる）ダミー添字なので、名前を変えても値は変わりません（$\sum_jx_j=\sum_kx_k$と同じ理屈、積分の$\int f(x)dx=\int f(y)dy$とも同じです）。この先$\mathbf u,\mathbf v$を入れ替えた式と表記をそろえるため、$k$と呼び直しておきます：

$$
u_k\partial_iv_k = [\mathbf u\times\operatorname{rot}\mathbf v]_i + (\operatorname{grad}v_i)\cdot\mathbf u
$$

（外側に残る$i$は1回しか出てこない「自由添字」なので、こちらは名前を変えると別の式になってしまい、変更できません。変えてよいのは「2回出てきて和を取られている添字」だけ、という点に注意してください。）

$\mathbf u,\mathbf v$を入れ替えた式も同様に成り立ちます：

$$
v_k\partial_iu_k = [\mathbf v\times\operatorname{rot}\mathbf u]_i + (\operatorname{grad}u_i)\cdot\mathbf v
$$

**この2つを足すと**：

$$
u_k\partial_iv_k+v_k\partial_iu_k = [\mathbf u\times\operatorname{rot}\mathbf v]_i+[\mathbf v\times\operatorname{rot}\mathbf u]_i+(\operatorname{grad}v_i)\cdot\mathbf u+(\operatorname{grad}u_i)\cdot\mathbf v
$$

左辺は、最初に展開した$\partial_i(\mathbf u\cdot\mathbf v)=(\partial_iu_k)v_k+u_k(\partial_iv_k)$と完全に一致します（$(\partial_iu_k)v_k=v_k\partial_iu_k$なので）。

## 結論

$$
\boxed{\partial_i(\mathbf u\cdot\mathbf v) = (\operatorname{grad}u_i)\cdot\mathbf v+(\operatorname{grad}v_i)\cdot\mathbf u+[\mathbf u\times\operatorname{rot}\mathbf v]_i+[\mathbf v\times\operatorname{rot}\mathbf u]_i}
$$

**「$\mathbf u\times\operatorname{rot}\mathbf v$を計算してみたら、たまたま欲しかった形の一部が出てきた」という、必然的な発見の流れになっています。** どの項を足すかを事前に決めておく必要は、どこにもありませんでした。

## 4. $\operatorname{rot}(\mathbf u\times\mathbf v)$ の導出

$$
(\operatorname{rot}(\mathbf u\times\mathbf v))_i = \varepsilon_{ijk}\partial_j(\mathbf u\times\mathbf v)_k = \varepsilon_{ijk}\partial_j(\varepsilon_{klm}u_lv_m) = \varepsilon_{ijk}\varepsilon_{klm}\big[(\partial_ju_l)v_m+u_l(\partial_jv_m)\big]
$$

恒等式を代入します：

$$
= (\delta_{il}\delta_{jm}-\delta_{im}\delta_{jl})\big[(\partial_ju_l)v_m+u_l(\partial_jv_m)\big]
$$

角括弧の中の2つの項それぞれに、$\delta_{il}\delta_{jm}$の部分と$-\delta_{im}\delta_{jl}$の部分を掛けて、合計4つの項に展開します。

**項1**（$\delta_{il}\delta_{jm}\times(\partial_ju_l)v_m$、$l=i,m=j$と置換）：

$$
(\partial_ju_i)v_j = v_j\partial_ju_i = (\mathbf v\cdot\nabla)u_i
$$

**項2**（$\delta_{il}\delta_{jm}\times u_l(\partial_jv_m)$、$l=i,m=j$と置換）：

$$
u_i(\partial_jv_j) = u_i(\operatorname{div}\mathbf v)
$$

**項3**（$-\delta_{im}\delta_{jl}\times(\partial_ju_l)v_m$、$m=i,l=j$と置換）：

$$
-(\partial_ju_j)v_i = -v_i(\operatorname{div}\mathbf u)
$$

**項4**（$-\delta_{im}\delta_{jl}\times u_l(\partial_jv_m)$、$m=i,l=j$と置換）：

$$
-u_j(\partial_jv_i) = -(\mathbf u\cdot\nabla)v_i
$$

4項をすべて足し合わせます：

$$
(\operatorname{rot}(\mathbf u\times\mathbf v))_i = (\mathbf v\cdot\nabla)u_i+u_i(\operatorname{div}\mathbf v)-v_i(\operatorname{div}\mathbf u)-(\mathbf u\cdot\nabla)v_i
$$

$(\mathbf v\cdot\nabla)u_i=(\operatorname{grad}u_i)\cdot\mathbf v$、$(\mathbf u\cdot\nabla)v_i=(\operatorname{grad}v_i)\cdot\mathbf u$ と書き直すと：

## 結論

$$
\boxed{(\operatorname{rot}(\mathbf u\times\mathbf v))_i = (\operatorname{grad}u_i)\cdot\mathbf v-(\operatorname{grad}v_i)\cdot\mathbf u+u_i(\operatorname{div}\mathbf v)-v_i(\operatorname{div}\mathbf u)}
$$

**ここでも$\partial_x$の項が勝手に消えるかどうかを気にする必要は一切ありません。** 恒等式を機械的に適用して4項に分解しただけで、答えがそのまま出てきました。

## まとめ：2つの証明方式の違い

$$
\boxed{
\begin{aligned}
&\text{「ゼロを足す」方式：答えを知っていることが前提。検証・確認には向くが、「なぜ」には答えない}\\
&\varepsilon\text{-}\delta\text{方式：}\varepsilon_{ijk}\varepsilon_{klm}=\delta_{il}\delta_{jm}-\delta_{im}\delta_{jl}\text{という1本の恒等式から、3つとも機械的に、答えを仮定せず導出できる}
\end{aligned}
}
$$

3つの公式すべてで、**$\mathbf u\times(\mathbf v$または$\operatorname{rot}\mathbf v)$のような「外積を含む式」を計算すると、$\varepsilon_{ijk}\varepsilon_{klm}$という2つの$\varepsilon$の積が必然的に現れ、それが恒等式によって「内積の差」に自動分解される**、というのが3つの公式に共通する、本当の仕組みでした。「なぜ外積っぽい項が生えてくるのか」という最初の疑問の答えは、まさにこの恒等式そのものにあった、ということになります。

---

# 補足2：これらの公式は、どこで使うのか

3つの公式は、途中式が長いわりに「いつ使うのか」が見えにくいものです。代表的な使い道を、1つずつ見ます。記号 $(\mathbf a\cdot\nabla)\mathbf b$ は、成分が $(\mathbf a\cdot\nabla)b_i=a_j\partial_jb_i=(\operatorname{grad}b_i)\cdot\mathbf a$ のベクトルです。これを使うと、上で証明した公式は

$$
\operatorname{grad}(\mathbf u\cdot\mathbf v)=(\mathbf v\cdot\nabla)\mathbf u+(\mathbf u\cdot\nabla)\mathbf v+\mathbf u\times\operatorname{rot}\mathbf v+\mathbf v\times\operatorname{rot}\mathbf u
$$

$$
\operatorname{div}(\mathbf u\times\mathbf v)=(\operatorname{rot}\mathbf u)\cdot\mathbf v-\mathbf u\cdot(\operatorname{rot}\mathbf v)
$$

$$
\operatorname{rot}(\mathbf u\times\mathbf v)=(\mathbf v\cdot\nabla)\mathbf u-(\mathbf u\cdot\nabla)\mathbf v+\mathbf u\,(\operatorname{div}\mathbf v)-\mathbf v\,(\operatorname{div}\mathbf u)
$$

と書けます（SymPy で3つとも確認済み）。

## 1. $\operatorname{grad}(\mathbf u\cdot\mathbf v)$：流体の移流項とベルヌーイの定理

$\mathbf v=\mathbf u$（流体の速度場）とすると、$\operatorname{grad}|\mathbf u|^2=2(\mathbf u\cdot\nabla)\mathbf u+2\,\mathbf u\times\operatorname{rot}\mathbf u$ なので、

$$
(\mathbf u\cdot\nabla)\mathbf u=\operatorname{grad}\frac{|\mathbf u|^2}2-\mathbf u\times\boldsymbol\omega,\qquad\boldsymbol\omega=\operatorname{rot}\mathbf u\ (\text{渦度})
$$

です。左辺は、流体の運動方程式に出てくる**移流項**（流れに乗って運ばれることによる速度の変化）です。

密度 $\rho$ が一定で粘性のない流体の運動方程式（オイラー方程式）$\frac{\partial\mathbf u}{\partial t}+(\mathbf u\cdot\nabla)\mathbf u=-\frac1\rho\operatorname{grad}p$ に入れると

$$
\frac{\partial\mathbf u}{\partial t}+\operatorname{grad}\Big(\frac{|\mathbf u|^2}2+\frac p\rho\Big)=\mathbf u\times\boldsymbol\omega
$$

です。

- **流れが時間によらず（$\partial_t\mathbf u=0$）、渦がない（$\boldsymbol\omega=0$）**なら、$\operatorname{grad}\big(\frac{|\mathbf u|^2}2+\frac p\rho\big)=0$ で、$\frac{|\mathbf u|^2}2+\frac p\rho$ はどこでも一定です。これが**ベルヌーイの定理**（速いところは圧力が低い）です。
- 渦があっても、流線（$\mathbf u$ の方向）に沿って内積を取ると、$(\mathbf u\times\boldsymbol\omega)\cdot\mathbf u=0$ なので、流線に沿っては一定です。

## 2. $\operatorname{div}(\mathbf u\times\mathbf v)$：電磁場のエネルギー保存（ポインティングの定理）

電場 $\mathbf E$ と磁場 $\mathbf H$ の外積 $\mathbf S=\mathbf E\times\mathbf H$（**ポインティング・ベクトル**、電磁場のエネルギーの流れ）の発散は、公式から

$$
\operatorname{div}(\mathbf E\times\mathbf H)=\mathbf H\cdot\operatorname{rot}\mathbf E-\mathbf E\cdot\operatorname{rot}\mathbf H
$$

です。マクスウェル方程式 $\operatorname{rot}\mathbf E=-\frac{\partial\mathbf B}{\partial t}$、$\operatorname{rot}\mathbf H=\mathbf J+\frac{\partial\mathbf D}{\partial t}$ を入れ、真空や線形な物質（$\mathbf D=\varepsilon\mathbf E$、$\mathbf B=\mu\mathbf H$）では $\mathbf E\cdot\frac{\partial\mathbf D}{\partial t}=\frac\partial{\partial t}\big(\frac12\mathbf E\cdot\mathbf D\big)$ などとまとめられるので

$$
\frac{\partial w}{\partial t}+\operatorname{div}\mathbf S=-\mathbf E\cdot\mathbf J,\qquad w=\frac12\big(\mathbf E\cdot\mathbf D+\mathbf H\cdot\mathbf B\big)
$$

となります。「電磁場のエネルギー密度 $w$ の増え方＋流れ出る量＝電流がする仕事の分だけ減る」という**エネルギー保存の式**で、[正規化フローのノート](../06_確率・統計/normalizing_flows_introduction.md)の Part VI の連続の式に、湧き出し（右辺）が付いた形です。

## 3. $\operatorname{rot}(\mathbf u\times\mathbf v)$：磁力線と渦線は流体に「凍りつく」

**磁気流体の誘導方程式**：電気抵抗のない導電性の流体（プラズマなど）では、磁場が $\frac{\partial\mathbf B}{\partial t}=\operatorname{rot}(\mathbf u\times\mathbf B)$ に従います。公式と $\operatorname{div}\mathbf B=0$ を使うと

$$
\frac{\partial\mathbf B}{\partial t}+(\mathbf u\cdot\nabla)\mathbf B=(\mathbf B\cdot\nabla)\mathbf u-\mathbf B\,(\operatorname{div}\mathbf u)
$$

です。左辺は「流れに乗って見たときの磁場の変化」、右辺の $(\mathbf B\cdot\nabla)\mathbf u$ は「流れが磁力線を引き伸ばす効果」です。磁力線は流体と一緒に動き、引き伸ばされると強くなります（**アルヴェーンの定理**。太陽の黒点や、地球の磁場を作るダイナモの基本）。

**渦度方程式**：§1 のオイラー方程式の rot を取ると、勾配の rot は $0$ なので

$$
\frac{\partial\boldsymbol\omega}{\partial t}=\operatorname{rot}(\mathbf u\times\boldsymbol\omega)
$$

で、誘導方程式とまったく同じ形です。したがって、粘性のない流体では、**渦線も流体と一緒に動く**（ケルビン・ヘルムホルツの渦定理）ことが、同じ公式から分かります。

## 4. まとめ

| 公式 | 使われる場所 | 物理的な意味 |
|---|---|---|
| $\operatorname{grad}(\mathbf u\cdot\mathbf v)$ | 流体の移流項 | ベルヌーイの定理（速いところは圧力が低い） |
| $\operatorname{div}(\mathbf u\times\mathbf v)$ | ポインティングの定理 | 電磁場のエネルギー保存 |
| $\operatorname{rot}(\mathbf u\times\mathbf v)$ | 誘導方程式、渦度方程式 | 磁力線・渦線が流体に凍りつく |

量子力学にも、ブラケットや演算子の積に微分が作用する場面（ノルムの保存、エーレンフェストの定理、ヘルマン・ファインマンの定理など）があり、[ブラケット記法のノート](../05_量子力学/bra_ket_notation_path_integral.md)の Part V にまとめました。
