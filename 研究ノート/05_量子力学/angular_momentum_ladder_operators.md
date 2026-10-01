# 角運動量のラダー演算子 ―構成と係数の導出―

前回のパウリ行列のノートPart IIIで、天下り的に使った

$$
S_+|\!\downarrow\rangle=\hbar|\!\uparrow\rangle,\qquad S_+|\!\uparrow\rangle=0,\qquad S_-|\!\uparrow\rangle=\hbar|\!\downarrow\rangle,\qquad S_-|\!\downarrow\rangle=0
$$

について、「ラダー演算子とは何か」「なぜ $j=\frac12$ だとこの係数が $\hbar$ になるのか」を、交換関係 $[J_i,J_j]=i\hbar\varepsilon_{ijk}J_k$ だけから最後まで導出します。

---

# Part I：出発点 ― 角運動量演算子の交換関係

角運動量演算子 $J_x,J_y,J_z$（水素原子の軌道角運動量、電子のスピン、どちらも同じ代数に従います）は

$$
\boxed{[J_x,J_y]=i\hbar J_z,\qquad [J_y,J_z]=i\hbar J_x,\qquad [J_z,J_x]=i\hbar J_y}
$$

を満たします（前回のパウリ行列の交換関係 $[\sigma_i,\sigma_j]=2i\varepsilon_{ijk}\sigma_k$ と見比べると、$J_i=\frac\hbar2\sigma_i$ とすれば $[J_i,J_j]=\frac{\hbar^2}4[\sigma_i,\sigma_j]=\frac{\hbar^2}4\cdot2i\varepsilon_{ijk}\sigma_k=i\hbar\varepsilon_{ijk}\left(\frac\hbar2\sigma_k\right)=i\hbar\varepsilon_{ijk}J_k$ となり、確かに一致します）。

また、全角運動量の2乗

$$
J^2 := J_x^2+J_y^2+J_z^2
$$

は、各 $J_i$ とすべて交換します（$[J^2,J_z]=0$ など）。これは「回転の大きさ（$J^2$）と、特定の1軸への射影（$J_z$）は、同時に確定した値を持てる」ということを意味し、$J^2,J_z$ の同時固有状態 $|j,m\rangle$ を考えることができます：

$$
J^2|j,m\rangle=\hbar^2j(j+1)|j,m\rangle,\qquad J_z|j,m\rangle=\hbar m|j,m\rangle
$$

（$j(j+1)$ という書き方の理由は、Part VIで自然に分かります。ひとまず「$J^2$の固有値を表すための記号」として受け入れてください。）

---

# Part II：ラダー演算子の定義

$$
\boxed{J_+ := J_x+iJ_y,\qquad J_- := J_x-iJ_y}
$$

**なぜこの組み合わせを考えるのか**：$J_x,J_y$ 単体では、$J_z$ と交換しない（$[J_z,J_x]=i\hbar J_y\ne0$）ため、$J_z$ の固有状態に作用させると、固有状態のままではいられません。ところが、$J_x$ と $J_y$ を虚数単位 $i$ で組み合わせると、$J_z$ との交換関係が驚くほど単純になります（Part IIIで確認）。これは、以前 $A_{ij}A_{ik}$ のような添字の組み合わせを整理したときと同じ発想で、**「バラバラだと複雑な量も、適切な線形結合を取ると構造が見える」**という一般的なテクニックです。

$J_-=J_+^\dagger$ であることも確認しておきます（$J_x,J_y$ はどちらもエルミートなので、$J_+^\dagger=(J_x+iJ_y)^\dagger=J_x^\dagger-iJ_y^\dagger=J_x-iJ_y=J_-$）。

---

# Part III：$[J_z,J_\pm]=\pm\hbar J_\pm$ の証明

$$
[J_z,J_+] = [J_z,J_x+iJ_y] = [J_z,J_x]+i[J_z,J_y]
$$

Part Iの交換関係を使います。$[J_z,J_x]=i\hbar J_y$（$[J_x,J_y]=i\hbar J_z$ を巡回置換したもの）、$[J_z,J_y]=-i\hbar J_x$（$[J_y,J_z]=i\hbar J_x$ の順序を入れ替えたもの、交換子の反対称性 $[A,B]=-[B,A]$ を使用）：

$$
[J_z,J_+] = i\hbar J_y + i(-i\hbar J_x) = i\hbar J_y+\hbar J_x = \hbar(J_x+iJ_y) = \hbar J_+
$$

$$
\boxed{[J_z,J_+]=\hbar J_+}
$$

同様に：

$$
[J_z,J_-] = [J_z,J_x]-i[J_z,J_y] = i\hbar J_y-i(-i\hbar J_x) = i\hbar J_y-\hbar J_x = -\hbar(J_x-iJ_y) = -\hbar J_-
$$

$$
\boxed{[J_z,J_-]=-\hbar J_-}
$$

---

# Part IV：$J_\pm$ が固有値を $\pm\hbar$ だけ動かすことの証明

これがラダー演算子（梯子演算子）と呼ばれる理由です。$J_z|j,m\rangle=\hbar m|j,m\rangle$ に対して、$J_z\big(J_+|j,m\rangle\big)$ を計算します。

$[J_z,J_+]=\hbar J_+$ を書き換えると $J_zJ_+=J_+J_z+\hbar J_+$ なので：

$$
J_z\big(J_+|j,m\rangle\big) = \big(J_+J_z+\hbar J_+\big)|j,m\rangle = J_+\big(J_z|j,m\rangle\big)+\hbar J_+|j,m\rangle
$$

$$
= J_+\big(\hbar m|j,m\rangle\big)+\hbar J_+|j,m\rangle = \hbar(m+1)\big(J_+|j,m\rangle\big)
$$

つまり、**$J_+|j,m\rangle$ は、$J_z$ の固有値が $\hbar(m+1)$ である固有状態**です。したがって：

$$
\boxed{J_+|j,m\rangle \propto |j,m+1\rangle}
$$

（$m$ の値を1つ上げる、つまり「梯子を1段登る」。）同様に $J_-|j,m\rangle\propto|j,m-1\rangle$（1段下る）も示せます。**比例定数（係数）がまだ分かっていない**ので、次のPartで決定します。

---

# Part V：$J_+J_-,\ J_-J_+$ を $J^2,J_z$ で書き換える

係数を求めるために、$J_\pm$ 同士の積を計算します。

$$
J_+J_- = (J_x+iJ_y)(J_x-iJ_y) = J_x^2-iJ_xJ_y+iJ_yJ_x+J_y^2 = J_x^2+J_y^2-i[J_x,J_y]
$$

$[J_x,J_y]=i\hbar J_z$ を代入すると：

$$
J_+J_- = J_x^2+J_y^2-i(i\hbar J_z) = J_x^2+J_y^2+\hbar J_z
$$

$J^2=J_x^2+J_y^2+J_z^2$ より $J_x^2+J_y^2=J^2-J_z^2$ なので：

$$
\boxed{J_+J_- = J^2-J_z^2+\hbar J_z}
$$

同様に：

$$
J_-J_+ = J_x^2+J_y^2+i[J_x,J_y] = J^2-J_z^2-\hbar J_z
$$

$$
\boxed{J_-J_+ = J^2-J_z^2-\hbar J_z}
$$

---

# Part VI：係数を決定する（ノルムを計算する）

## 1. $J_+|j,m\rangle$ の「長さ」を計算する

$J_+|j,m\rangle$ 自身の内積（ノルムの2乗）を計算します。$J_-=J_+^\dagger$（Part II）だったので：

$$
\big\|J_+|j,m\rangle\big\|^2 = \langle j,m|J_+^\dagger J_+|j,m\rangle = \langle j,m|J_-J_+|j,m\rangle
$$

Part Vで求めた $J_-J_+=J^2-J_z^2-\hbar J_z$ を代入します：

$$
= \langle j,m|\big(J^2-J_z^2-\hbar J_z\big)|j,m\rangle
$$

$|j,m\rangle$ は $J^2,J_z$ の固有状態なので、それぞれの固有値をそのまま代入できます（$J^2\to\hbar^2j(j+1)$、$J_z\to\hbar m$、$J_z^2\to\hbar^2m^2$）：

$$
= \hbar^2j(j+1)-\hbar^2m^2-\hbar\cdot\hbar m = \hbar^2\big[j(j+1)-m^2-m\big] = \hbar^2\big[j(j+1)-m(m+1)\big]
$$

## 2. ノルムの2乗から、係数を復元する

$\big\|J_+|j,m\rangle\big\|^2=\hbar^2\big[j(j+1)-m(m+1)\big]$ であり、Part IVより $J_+|j,m\rangle$ は規格化された $|j,m+1\rangle$ の定数倍だったので、その定数（＝ノルムそのもの、慣習的に正の実数に取る）は、この式の平方根です：

$$
\boxed{J_+|j,m\rangle = \hbar\sqrt{j(j+1)-m(m+1)}\ |j,m+1\rangle}
$$

同様の計算（$J_+J_-=J^2-J_z^2+\hbar J_z$ を使う）から：

$$
\boxed{J_-|j,m\rangle = \hbar\sqrt{j(j+1)-m(m-1)}\ |j,m-1\rangle}
$$

**これが、水素原子の $l,m$ や、スピンの $j,m$ を問わず、角運動量理論全般で成り立つ一般公式です。**

---

# Part VII：$j=\frac12$ を代入する（スピン$\frac12$の場合）

## 1. $S_+|\!\downarrow\rangle$（$m=-\frac12$ から $m=+\frac12$ へ）

$|\!\downarrow\rangle=|j,m\rangle=|\tfrac12,-\tfrac12\rangle$ として、Part VIの公式に $j=\frac12,\ m=-\frac12$ を代入します：

$$
j(j+1) = \frac12\cdot\frac32=\frac34,\qquad m(m+1)=\left(-\frac12\right)\left(\frac12\right)=-\frac14
$$

$$
\sqrt{j(j+1)-m(m+1)} = \sqrt{\frac34-\left(-\frac14\right)} = \sqrt{\frac34+\frac14} = \sqrt1 = 1
$$

$$
\boxed{S_+|\!\downarrow\rangle = \hbar\cdot1\cdot|\!\uparrow\rangle = \hbar|\!\uparrow\rangle}
$$

**係数がちょうど $\hbar$ になりました。** これが前回のノートで使った値の正体です。

## 2. $S_+|\!\uparrow\rangle$（$m=+\frac12$、一番上の段）

$j=\frac12,\ m=\frac12$（$m=j$、梯子の一番上）を代入すると：

$$
m(m+1) = \frac12\cdot\frac32=\frac34
$$

$$
\sqrt{j(j+1)-m(m+1)} = \sqrt{\frac34-\frac34}=\sqrt0=0
$$

$$
\boxed{S_+|\!\uparrow\rangle = 0}
$$

**これ以上上に登れない**ので、ゼロになるのは当然です（一番上の段から、さらに上に梯子を登ろうとしても行き場がない、という意味）。

## 3. $S_-|\!\uparrow\rangle,\ S_-|\!\downarrow\rangle$ も同様

$S_-$ の公式（$j(j+1)-m(m-1)$）に $j=\frac12,m=\frac12$ を代入すると $\frac34-\frac12\left(-\frac12\right)=\frac34+\frac14=1$ となり：

$$
\boxed{S_-|\!\uparrow\rangle = \hbar|\!\downarrow\rangle}
$$

$m=-\frac12$（一番下の段）を代入すると $\frac34-\left(-\frac12\right)\left(-\frac32\right)=\frac34-\frac34=0$ となり：

$$
\boxed{S_-|\!\downarrow\rangle = 0}
$$

**これで、前回のノートで使った4つの式がすべて、一般公式から具体的に導出できました。**

---

# Part VIII：$j=\frac12$ という値そのものは、どこから来るのか（補足）

$j=\frac12$ という値自体は、「電子のスピン角運動量が $\hbar/2$ の2つの状態（上向き・下向き）しか取らない」という、**実験事実（あるいはディラック方程式から導かれる、相対論的量子力学の要請）**として与えられるものです。今回の計算は、「$j=\frac12$ が与えられたときに、梯子の係数がどう決まるか」を導出したものであり、「なぜスピンが$\frac12$なのか」自体は、また別の（より深い）議論になります。

一般には $j$ は $0,\frac12,1,\frac32,2,\dots$（非負の整数または半整数）のみが許され、$m$ は $-j,-j+1,\dots,j-1,j$ の $2j+1$ 個の値を取ります。$j=\frac12$ なら $m=\pm\frac12$ の2状態だけ、というのはこの一般則の最小のケースです（水素原子の軌道角運動量 $l$ は整数のみでしたが、スピンは半整数も許される、という違いがあります）。

---

# まとめ：全体の流れ

```
[J_x,J_y]=iħJ_z 等（角運動量の基本交換関係）
        │  J_±:=J_x±iJ_y と定義
        ▼
[J_z,J_±]=±ħJ_±（証明：交換関係を直接展開するだけ）
        │  J_z(J_±|j,m⟩) を計算
        ▼
J_±|j,m⟩ は J_z の固有値を±1段動かす（比例定数は未定）
        │  J_+J_-, J_-J_+ を J²,J_z で書き換える
        ▼
J_∓J_± = J²-J_z²∓ħJ_z
        │  ‖J_±|j,m⟩‖² = ⟨j,m|J_∓J_±|j,m⟩ を計算
        ▼
J_±|j,m⟩ = ħ√(j(j+1)-m(m±1)) |j,m±1⟩
        │  j=1/2 を代入
        ▼
S_+|↓⟩=ħ|↑⟩,  S_+|↑⟩=0,  S_-|↑⟩=ħ|↓⟩,  S_-|↓⟩=0
```

「ラダー演算子」という名前は、$J_z$ の固有値（$m$）を梯子の段のように1段ずつ上げ下げする、という今回の性質（Part IV）に由来します。係数 $\hbar\sqrt{j(j+1)-m(m\pm1)}$ は、天下り的な公式ではなく、**$J_\pm$ 同士の積を $J^2,J_z$ で書き換え、その期待値（＝ノルムの2乗）を計算するだけ**で、交換関係から機械的に導き出せるものでした。
