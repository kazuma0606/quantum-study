# ユニタリ行列の位相分離パラメータ化 ―導出ノート―

前回導出した結果を土台に、$a,c$ を「絶対値×位相」に分解し、$b,d$ がどう書き換わるかを1行ずつ追います。最後に、前回の形（$b=-c^*\Delta$、$d=a^*\Delta$）と、今回の形を対比表にまとめます。

---

# 0. 前回までの復習（出発点）

$U=\begin{pmatrix}a&b\\c&d\end{pmatrix}$、$U^\dagger=U^{-1}$ から導いた関係：

$$
\boxed{d=a^*\Delta,\qquad b=-c^*\Delta,\qquad \Delta:=\det U,\qquad |\Delta|=1,\qquad |a|^2+|c|^2=1}
$$

ここから出発します。今回の目標は、この中の**独立な自由パラメータ**（$a,c$ の複素数2個 ＋ $\phi$）を、**制約なしに動かせる実数のパラメータ**（$\theta,\alpha,\beta,\phi$）に置き換えることです。

---

# Part I：なぜ絶対値と位相を分離する必要があるか

$a,c$ をそれぞれ単独で $a=e^{i\alpha}$、$c=e^{i\beta}$（絶対値を$1$と決め打ち）と置くと、

$$
|a|^2+|c|^2 = 1+1=2\ne1
$$

となり矛盾することが前回分かりました。**この失敗が教えてくれるのは、「$a$ と $c$ の絶対値は独立に $1$ にはできず、互いに関係し合っている」ということ**です。したがって、絶対値の部分と位相の部分を明確に分けて、絶対値の方だけ拘束条件 $|a|^2+|c|^2=1$ を満たすように処理する必要があります。

---

# Part II：$a,c$ を絶対値・位相に分解する

## 1. 極形式で書く

任意の複素数は、絶対値（$\ge0$の実数）と位相（実数、$2\pi$の周期）に分けて書けます：

$$
a = r_a\,e^{i\alpha},\qquad c = r_c\,e^{i\beta}\qquad(r_a,r_c\ge0,\ \alpha,\beta\in\mathbb R)
$$

これは常に可能な、複素数の一般的な書き方（極形式）であり、まだ何も仮定していません。

## 2. 拘束条件 $|a|^2+|c|^2=1$ を絶対値に適用する

$|a|=r_a$、$|c|=r_c$ なので：

$$
r_a^2+r_c^2=1
$$

## 3. $r_a,r_c$ を1つの角度 $\theta$ でまとめて表す

$r_a,r_c\ge0$ かつ $r_a^2+r_c^2=1$ という条件は、$(r_a,r_c)$ を平面上の点と見ると、**単位円の第1象限の弧（原点中心、半径1の円のうち $x,y\ge0$ の部分）上にある**ということを意味します。この弧上の点は、ただ1つの角度 $\theta\in[0,\pi/2]$ を使って

$$
\boxed{r_a=\cos\theta,\qquad r_c=\sin\theta}
$$

と表せます（$\cos^2\theta+\sin^2\theta=1$ が自動的に満たされるので、これは拘束条件を**恒等的に**満たす書き方です）。$\theta=0$ なら $a$ だけが生き残り（$r_a=1,r_c=0$）、$\theta=\pi/2$ なら $c$ だけが生き残ります（$r_a=0,r_c=1$）。

## 4. まとめ

$$
\boxed{a=\cos\theta\,e^{i\alpha},\qquad c=\sin\theta\,e^{i\beta}}\qquad(\theta\in[0,\tfrac\pi2],\ \alpha,\beta\in\mathbb R)
$$

これで、**$|a|^2+|c|^2=1$ という制約を毎回確認する必要がなくなり**、$\theta,\alpha,\beta$ を自由に（$\theta$ は範囲だけ気にして）選べば、必ず正しい $a,c$ が得られるようになりました。

---

# Part III：$b,d$ を求める（前回の関係式に代入するだけ）

## 5. $a^*,c^*$ を計算する

複素共役は、極形式では位相の符号を反転させるだけです（$r_a,r_c$ は実数なのでそのまま）：

$$
a^* = \cos\theta\,e^{-i\alpha},\qquad c^*=\sin\theta\,e^{-i\beta}
$$

## 6. $\Delta=e^{i\phi}$ を使って $d=a^*\Delta$ を計算する

$$
d = a^*\Delta = \big(\cos\theta\,e^{-i\alpha}\big)\big(e^{i\phi}\big)
$$

指数法則 $e^{X}e^{Y}=e^{X+Y}$（指数の肩同士を足すだけ）を使うと：

$$
\boxed{d = \cos\theta\,e^{i(\phi-\alpha)}}
$$

## 7. 同様に $b=-c^*\Delta$ を計算する

$$
b = -c^*\Delta = -\big(\sin\theta\,e^{-i\beta}\big)\big(e^{i\phi}\big) = -\sin\theta\,e^{i(\phi-\beta)}
$$

$$
\boxed{b = -\sin\theta\,e^{i(\phi-\beta)}}
$$

## 8. 全体をまとめる

$$
\boxed{
U = \begin{pmatrix}
\cos\theta\,e^{i\alpha} & -\sin\theta\,e^{i(\phi-\beta)}\\[4pt]
\sin\theta\,e^{i\beta} & \cos\theta\,e^{i(\phi-\alpha)}
\end{pmatrix}
}
$$

自由パラメータは $\theta\in[0,\pi/2]$、$\alpha,\beta,\phi\in\mathbb R$ の**実数4個**。これで $U(2)$ の次元（$n^2=2^2=4$）とぴったり一致する形になりました。

---

# Part IV：検算（$U^\dagger U=I$ を直接確認する）

念のため、Part IIIの結果が本当に $U^\dagger U=I$ を満たすか、$\Delta,a,c$ を経由せず**直接**確かめます。

$$
U^\dagger = \begin{pmatrix}\cos\theta\,e^{-i\alpha} & \sin\theta\,e^{-i\beta}\\ -\sin\theta\,e^{-i(\phi-\beta)} & \cos\theta\,e^{-i(\phi-\alpha)}\end{pmatrix}
$$

**(1,1)成分**：

$$
\cos\theta\,e^{-i\alpha}\cdot\cos\theta\,e^{i\alpha} + \sin\theta\,e^{-i\beta}\cdot\sin\theta\,e^{i\beta} = \cos^2\theta+\sin^2\theta = 1\ \checkmark
$$

**(1,2)成分**：

$$
\cos\theta\,e^{-i\alpha}\cdot\big(-\sin\theta\,e^{i(\phi-\beta)}\big) + \sin\theta\,e^{-i\beta}\cdot\cos\theta\,e^{i(\phi-\alpha)}
$$

$$
= -\sin\theta\cos\theta\,e^{i(\phi-\alpha-\beta)} + \sin\theta\cos\theta\,e^{i(\phi-\alpha-\beta)} = 0\ \checkmark
$$

（指数の肩が両方とも $\phi-\alpha-\beta$ にそろい、符号違いでちょうど打ち消し合いました。）

**(2,2)成分**：

$$
\big(-\sin\theta\,e^{-i(\phi-\beta)}\big)\big(-\sin\theta\,e^{i(\phi-\beta)}\big) + \cos\theta\,e^{-i(\phi-\alpha)}\cdot\cos\theta\,e^{i(\phi-\alpha)} = \sin^2\theta+\cos^2\theta=1\ \checkmark
$$

（(2,1)成分も同様に0になります。）すべて一致し、確かに $U^\dagger U=I$ です。

## 9. $\det U$ の検算

$$
\det U = \cos\theta\,e^{i\alpha}\cdot\cos\theta\,e^{i(\phi-\alpha)} - \big(-\sin\theta\,e^{i(\phi-\beta)}\big)\sin\theta\,e^{i\beta}
$$

$$
= \cos^2\theta\,e^{i\phi} + \sin^2\theta\,e^{i\phi} = e^{i\phi}\ \checkmark
$$

Part IIIの出発点で使った $\Delta=e^{i\phi}$ と矛盾なく一致しました。

---

# 対比ノート：前回の形 vs 今回の形

| | 前回（$a,c$を複素数のまま） | 今回（絶対値・位相を分離） |
|---|---|---|
| 自由パラメータ | $a,c\in\mathbb C$（拘束 $\lvert a\rvert^2+\lvert c\rvert^2=1$ あり）、$\phi\in\mathbb R$ | $\theta\in[0,\pi/2]$、$\alpha,\beta,\phi\in\mathbb R$（拘束なし） |
| $b$ | $b=-c^*\Delta$ | $b=-\sin\theta\,e^{i(\phi-\beta)}$ |
| $d$ | $d=a^*\Delta$ | $d=\cos\theta\,e^{i(\phi-\alpha)}$ |
| 拘束条件の扱い | 式の外側で別途 $\lvert a\rvert^2+\lvert c\rvert^2=1$ を満たす$a,c$を探す必要がある | $\cos^2\theta+\sin^2\theta=1$ が自動的に成立、探す必要なし |
| パラメータの数え方 | 分かりにくい（複素数2個引く拘束1個、で実質3個＋$\phi$） | 一目瞭然（実数4個、$U(2)$の次元と直接一致） |
| 見える構造 | $U^\dagger=U^{-1}$ という定義そのもの | $U(2)=U(1)\times SU(2)$、量子ゲート$U3$との対応 |

**変換の要点は、"$b,d$ の中身の関係式（$-c^*\Delta$、$a^*\Delta$）は一切変わらず、そこに代入する $a,c,\Delta$ の"表し方"だけを変えた**、という点です。導出のロジック自体は前回のPart III・IVをそのまま使い、Part IIで用意した $a,c$ の新しい書き方を機械的に代入しただけで、Part IIIの結果が出ています。

---

# 補足：ゲージを固定すると量子ゲートの標準形になる

$\alpha=0$（全体位相の基準を選ぶ）とし、$\theta\to\theta/2$（角度の定義を書き換える）、$\beta=:\varphi$、$\phi-\beta=:\lambda$（位相の呼び方を変えるだけ）とすると：

$$
U = \begin{pmatrix}\cos(\theta/2) & -e^{i\lambda}\sin(\theta/2)\\ e^{i\varphi}\sin(\theta/2) & e^{i(\varphi+\lambda)}\cos(\theta/2)\end{pmatrix}
$$

これは量子コンピュータの標準的な単一量子ビットゲート $U3(\theta,\varphi,\lambda)$ の定義そのものと一致します。Part II〜IVで導いた $\theta,\alpha,\beta,\phi$ というパラメータ化が、そのまま実際の量子計算ソフトウェアの記法に対応していたことになります。
