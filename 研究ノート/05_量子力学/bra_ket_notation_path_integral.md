# ブラケット記法 ―注意点・活用法・経路積分への道―

これまでの一連の会話（エルミート演算子の直交性、時間発展演算子、$|x\rangle,|p\rangle,|n\rangle$ の違い）を整理し、最後に**完全性関係を繰り返し挿入する**という一つの技法だけで、経路積分の式を実際に導出するところまでまとめます。

---

# Part 0：通常の関数形式との対応表

まず全体の見取り図です。左が「波動関数の言葉」、右が「ブラケットの言葉」で、同じものを指しています。

| 波動関数形式 | ブラケット形式 | 意味 |
|---|---|---|
| $\Psi(x)$ | $\langle x\vert\Psi\rangle$ | 抽象的な状態 $\vert\Psi\rangle$ の位置基底での成分 |
| $\tilde\Psi(p)$ | $\langle p\vert\Psi\rangle$ | 同じ状態の運動量基底での成分 |
| $\int\Phi^*(x)\Psi(x)dx$ | $\langle\Phi\vert\Psi\rangle$ | 内積 |
| $\int\Psi^*(x)\hat A\Psi(x)dx$ | $\langle\Psi\vert\hat A\vert\Psi\rangle$ | 期待値 |
| $\hat p=-i\hbar\partial/\partial x$ | $\hat p$（基底に依らない抽象的な演算子） | 運動量演算子（表示によって形が変わる） |
| $\delta(x-x')$ | $\langle x\vert x'\rangle$ | 位置基底の「直交関係」（連続版） |
| $\int\phi_n^*(x)\psi(x)dx=c_n$、$\psi(x)=\sum_nc_n\phi_n(x)$ | $c_n=\langle n\vert\Psi\rangle$、$\vert\Psi\rangle=\sum_nc_n\vert n\rangle$ | 固有関数展開 |

**一番大事な変換規則**：抽象ベクトル $|\Psi\rangle$ を、ある基底 $\{|e_i\rangle\}$ に「射影」した数値の集まりが、通常の関数形式・成分表示です。

$$
\boxed{\Psi(x)=\langle x|\Psi\rangle,\qquad \tilde\Psi(p)=\langle p|\Psi\rangle,\qquad c_n=\langle n|\Psi\rangle}
$$

これは、以前扱った「抽象ベクトル $\mathbf v$ と、基底 $\mathbf e_i$ で展開した成分 $v^i=\mathbf e_i\cdot\mathbf v$」の関係と完全に同じ構造です。

---

# Part I：基本ルール

## 1. 内積とエルミート共役

$$
\langle\phi|\psi\rangle^* = \langle\psi|\phi\rangle,\qquad \langle\psi|=\big(|\psi\rangle\big)^\dagger
$$

## 2. 完全性関係（resolution of identity）

正規直交基底なら、恒等演算子はその基底で「分解」できます：

$$
\text{離散：}\ \sum_n |n\rangle\langle n|=1,\qquad\quad \text{連続：}\ \int |x\rangle\langle x|\,dx=1
$$

**これが今回一番重要な道具です。** 任意の状態やその積の間に、これを「$1$（何も変えない演算子）」として挿入できます。

## 3. 演算子の行列要素・期待値

$$
A_{mn}:=\langle m|\hat A|n\rangle,\qquad \langle\hat A\rangle_\psi := \langle\psi|\hat A|\psi\rangle
$$

---

# Part II：誤解しやすい注意点（今回の会話で出てきたもの）

## 1. $|x\rangle$ は「$\hat x$ を作用させた結果」ではない

$|x\rangle$ は $\hat x$ の固有状態というラベルであって、演算子の作用の結果ではありません。演算子が実際に働くのは、演算子が式の中に明示的に書かれているときだけです：

$$
\hat x|x\rangle = x|x\rangle\quad(\text{定義そのもの})\qquad\ne\qquad |x\rangle\ (\text{これ自体は演算ではない})
$$

## 2. $\langle x|$ は「共役転置してから $\hat x$ を作用させる」ことではない

$\langle x|=(|x\rangle)^\dagger$ というだけで、$\hat x$ の作用は含まれません。$\hat x$ が関わるのは $\langle x|\hat A\cdots$ のように演算子がブラの隣に明示的にあるときだけです。

## 3. 離散スペクトルと連続スペクトルで、直交関係も完全性関係も形が変わる

| | 離散（$\vert n\rangle$、例：調和振動子の $\hat N$、水素原子の $\hat H$） | 連続（$\vert x\rangle,\vert p\rangle$） |
|---|---|---|
| 直交関係 | $\langle n\vert m\rangle=\delta_{nm}$（クロネッカー） | $\langle x\vert x'\rangle=\delta(x-x')$（ディラック） |
| 完全性関係 | $\sum_n\vert n\rangle\langle n\vert=1$（和） | $\int\vert x\rangle\langle x\vert\,dx=1$（積分） |
| 規格化 | $\vert n\rangle$ は物理的な状態（規格化可能） | $\vert x\rangle$ は正規化不可能な理想化（デルタ関数で「規格化」） |

## 4. 演算子の「形」は基底の選び方に依存する

$\hat p$ という抽象的な演算子は1つですが、それを**どの基底で見るか**によって具体的な表式が変わります：

$$
\langle x|\hat p|\Psi\rangle = -i\hbar\frac{\partial}{\partial x}\Psi(x)\qquad(\text{位置表示})
$$
$$
\langle p|\hat p|\Psi\rangle = p\,\tilde\Psi(p)\qquad(\text{運動量表示})
$$

「$\hat p=-i\hbar\partial/\partial x$」という式そのものが、実は**位置基底というレンズを通して見たときだけの表現**であって、$\hat p$ の本体（抽象的な演算子）はどの表示にも依存しません。

## 5. $|n\rangle$ は文脈依存の記号

$|x\rangle,|p\rangle$ は特定の演算子（$\hat x,\hat p$）の固有状態を指す固定的な記号ですが、$|n\rangle$ は「今考えている系の、離散スペクトルを持つ何らかのエルミート演算子」の固有状態という**その都度中身が変わる略記**です。前後の文脈（調和振動子の $\hat N$ か、水素原子の $\hat H$ か）を確認する必要があります。

---

# Part III：活用法 ―完全性関係を挟み込む技法

ブラケット記法の最大の実用的価値は、**完全性関係 $\int |x\rangle\langle x|\,dx=1$ を、式の好きな場所に挿入できる**という一点に集約されます。これにより、抽象的な演算子の計算を、具体的な関数の積分に変換できます。

## 例：$\langle\phi|\hat A|\psi\rangle$ を位置表示の積分に変換する

$$
\langle\phi|\hat A|\psi\rangle = \langle\phi|\Big(\int |x\rangle\langle x|\,dx\Big)\hat A|\psi\rangle = \int\langle\phi|x\rangle\langle x|\hat A|\psi\rangle\,dx = \int\phi^*(x)\big(\hat A\psi\big)(x)\,dx
$$

**完全性関係を1回挿入しただけで、抽象的な内積が、見慣れた積分の形に自動的に変換されました。** これがブラケット記法の実用上の核心です。次のPartで、この技法を「時間発展演算子」に繰り返し適用することで、経路積分の式そのものを導出します。

---

# Part IV：経路積分への道 ―完全性関係を繰り返し挿入する

## 1. 出発点

以前扱った遷移確率振幅（プロパゲーター）：

$$
K(x_f,t;x_i,0) := \langle x_f| e^{-i\hat Ht/\hbar}|x_i\rangle
$$

を導出します。ハミルトニアンは

$$
\hat H = \frac{\hat p^2}{2m}+V(\hat x)
$$

とします。

## 2. 時間を細かく分割する

時間 $t$ を $N$ 個の微小区間 $\varepsilon:=t/N$ に分割します：

$$
e^{-i\hat Ht/\hbar} = \Big(e^{-i\hat H\varepsilon/\hbar}\Big)^N
$$

（指数法則。演算子でも、同じ演算子同士の積なら普通の数と同じように振る舞います。）

## 3. 完全性関係を $N-1$ 回挿入する

各時間刻みの間に、位置基底の完全性関係 $\int |x_k\rangle\langle x_k|\,dx_k=1$ を挿入します：

$$
K = \int dx_1\cdots dx_{N-1}\ \langle x_f|e^{-i\hat H\varepsilon/\hbar}|x_{N-1}\rangle\langle x_{N-1}|e^{-i\hat H\varepsilon/\hbar}|x_{N-2}\rangle\cdots\langle x_1|e^{-i\hat H\varepsilon/\hbar}|x_i\rangle
$$

**この時点ですでに、「$x_i$ から $x_f$ へ、途中の点 $x_1,\dots,x_{N-1}$ をどう経由するか」というすべての可能性を積分で足し上げる形になっています。** これが「経路の和」の正体の第一歩です。

## 4. 微小時間の伝播（1ステップ分）を計算する

各因子 $\langle x_{k+1}|e^{-i\hat H\varepsilon/\hbar}|x_k\rangle$ を具体的に計算します。$\hat H=\hat p^2/2m+V(\hat x)$ は運動量部分と位置部分が交換しない（$[\hat x,\hat p]=i\hbar\ne0$）ので、厳密には $e^{-i\hat H\varepsilon/\hbar}\ne e^{-i\hat p^2\varepsilon/2m\hbar}e^{-iV(\hat x)\varepsilon/\hbar}$ ですが、$\varepsilon$ が微小なら誤差は $O(\varepsilon^2)$ で、$N\to\infty$（$\varepsilon\to0$）の極限では無視できます（Trotter近似）：

$$
e^{-i\hat H\varepsilon/\hbar} \approx e^{-i\hat p^2\varepsilon/2m\hbar}\,e^{-iV(\hat x)\varepsilon/\hbar}
$$

これを使うと：

$$
\langle x_{k+1}|e^{-i\hat H\varepsilon/\hbar}|x_k\rangle \approx e^{-iV(x_k)\varepsilon/\hbar}\langle x_{k+1}|e^{-i\hat p^2\varepsilon/2m\hbar}|x_k\rangle
$$

（$V(\hat x)$ は右のケット $|x_k\rangle$ に作用して固有値 $V(x_k)$ を返すので、数として外に出せます。）

## 5. 運動量の完全性関係を挿入する

残った $\langle x_{k+1}|e^{-i\hat p^2\varepsilon/2m\hbar}|x_k\rangle$ に、今度は運動量基底の完全性関係 $\int |p\rangle\langle p|\,dp=1$ を挿入します：

$$
\langle x_{k+1}|e^{-i\hat p^2\varepsilon/2m\hbar}|x_k\rangle = \int dp\,\langle x_{k+1}|p\rangle\,e^{-ip^2\varepsilon/2m\hbar}\,\langle p|x_k\rangle
$$

（$\hat p^2$ は $|p\rangle$ に対して固有値 $p^2$ を返すので指数の肩から演算子が消えます。）

位置・運動量の基底変換 $\langle x|p\rangle=\dfrac1{\sqrt{2\pi\hbar}}e^{ipx/\hbar}$（これも以前扱った関係です）を代入します：

$$
= \int\frac{dp}{2\pi\hbar}\,e^{ip(x_{k+1}-x_k)/\hbar}\,e^{-ip^2\varepsilon/2m\hbar}
$$

## 6. ガウス積分を実行する

指数の中身を $p$ について平方完成します：

$$
-\frac{i\varepsilon}{2m\hbar}p^2+\frac i\hbar(x_{k+1}-x_k)p = -\frac{i\varepsilon}{2m\hbar}\left[p-\frac{m(x_{k+1}-x_k)}\varepsilon\right]^2 + \frac{im(x_{k+1}-x_k)^2}{2\hbar\varepsilon}
$$

ガウス積分の公式 $\displaystyle\int dp\,e^{-\alpha p^2}=\sqrt{\pi/\alpha}$（$\alpha=i\varepsilon/2m\hbar$）を使うと：

$$
\int\frac{dp}{2\pi\hbar}e^{-\frac{i\varepsilon}{2m\hbar}[p-\cdots]^2} = \sqrt{\frac m{2\pi i\hbar\varepsilon}}
$$

したがって：

$$
\boxed{\langle x_{k+1}|e^{-i\hat H\varepsilon/\hbar}|x_k\rangle \approx \sqrt{\frac m{2\pi i\hbar\varepsilon}}\ \exp\left[\frac{i\varepsilon}\hbar\left(\frac m2\left(\frac{x_{k+1}-x_k}\varepsilon\right)^2-V(x_k)\right)\right]}
$$

括弧の中の $\dfrac m2\left(\dfrac{x_{k+1}-x_k}\varepsilon\right)^2-V(x_k)$ は、**運動エネルギーからポテンシャルエネルギーを引いたもの**、つまり**ラグランジアン** $L=\frac m2\dot x^2-V(x)$ の離散版そのものです。

## 7. すべてのステップを掛け合わせて連続極限を取る

Part 3の式に戻り、すべての $N$ ステップ分を掛け合わせます：

$$
K = \lim_{N\to\infty}\left(\frac m{2\pi i\hbar\varepsilon}\right)^{N/2}\int dx_1\cdots dx_{N-1}\ \exp\left[\frac i\hbar\sum_{k=0}^{N-1}\varepsilon\left(\frac m2\left(\frac{x_{k+1}-x_k}\varepsilon\right)^2-V(x_k)\right)\right]
$$

$N\to\infty$（$\varepsilon\to0$）の極限で、和 $\sum_k\varepsilon(\cdots)$ はリーマン和として積分に収束します：

$$
\sum_{k=0}^{N-1}\varepsilon\left(\frac m2\dot x_k^2-V(x_k)\right) \longrightarrow \int_0^tdt'\left(\frac m2\dot x(t')^2-V(x(t'))\right) = S[x(t)]
$$

これはまさに**古典力学の作用**（ラグランジアンの時間積分）です。また、係数と積分測度 $\left(\frac m{2\pi i\hbar\varepsilon}\right)^{N/2}dx_1\cdots dx_{N-1}$ 全体を、形式的に $\mathcal Dx(t)$（「あらゆる経路にわたる積分測度」）とまとめて書くと：

$$
\boxed{K(x_f,t;x_i,0) = \int\mathcal Dx(t)\ e^{iS[x(t)]/\hbar}}
$$

これが経路積分の式です。**完全性関係を位置と運動量それぞれについて繰り返し挿入し、ガウス積分を実行して連続極限を取っただけ**で、演算子形式のプロパゲーター $\langle x_f|e^{-i\hat Ht/\hbar}|x_i\rangle$ から、経路積分の表式が完全に導出できました。

---

# Part V：ブラケットに微分が作用する場面 ―積の微分の公式の使い道―

「ブラとケットの積（内積）や、ケットとブラの積（外積）に微分が作用する場面は、量子力学にはないのでは」と思うかもしれませんが、実は基本的な定理の多くがそれです。どれも、ベクトル解析の $\operatorname{grad}(\mathbf u\cdot\mathbf v)$ などと同じ**積の微分**です（ベクトル解析での使い道は、[grad・div・rot の恒等式のノート](../01_基礎・ベクトル解析/grad_div_rot_identities_full_derivation.md)の補足2）。

## 1. 積の微分の形

パラメータ（時刻 $t$ など）$\lambda$ に依存する状態と演算子について、

$$
\frac{d}{d\lambda}\langle\phi|\psi\rangle=\langle\partial_\lambda\phi|\psi\rangle+\langle\phi|\partial_\lambda\psi\rangle,\qquad\frac{d}{d\lambda}\big(\hat A\hat B\big)=\frac{d\hat A}{d\lambda}\hat B+\hat A\frac{d\hat B}{d\lambda}\tag{V-1}
$$

です（内積も行列の積も、成分で書けば「掛けて足す」だけなので、数の積の微分がそのまま使える）。演算子の積では、**掛ける順番を保ったまま**微分します（$\hat A$ と $\hat B$ は交換するとは限らない）。外積 $|\psi\rangle\langle\psi|$ も同じで、$\frac{d}{dt}\big(|\psi\rangle\langle\psi|\big)=|\dot\psi\rangle\langle\psi|+|\psi\rangle\langle\dot\psi|$ です。

以下では、シュレーディンガー方程式 $i\hbar|\dot\psi\rangle=\hat H|\psi\rangle$ と、そのブラ版 $-i\hbar\langle\dot\psi|=\langle\psi|\hat H$（両辺のエルミート共役を取り、$\hat H^\dagger=\hat H$ を使う）を使います。

## 2. ノルムの保存（確率の合計は変わらない）

$$
\frac{d}{dt}\langle\psi|\psi\rangle=\langle\dot\psi|\psi\rangle+\langle\psi|\dot\psi\rangle=\frac i\hbar\langle\psi|\hat H|\psi\rangle-\frac i\hbar\langle\psi|\hat H|\psi\rangle=0\tag{V-2}
$$

（$\langle\dot\psi|=\frac i\hbar\langle\psi|\hat H$、$|\dot\psi\rangle=-\frac i\hbar\hat H|\psi\rangle$）。$\hat H$ がエルミートであることが、ちょうど打ち消し合いを生んでいます。時間発展演算子 $e^{-i\hat Ht/\hbar}$ がユニタリであること（[行列の指数関数と交換子のノート](../04_群論・代数/matrix_exponential_commutator_bch_trotter.md)の Part VI）の、微分版の証明です。

## 3. 期待値の時間変化（エーレンフェストの定理）

演算子 $\hat A$ の期待値 $\langle A\rangle=\langle\psi|\hat A|\psi\rangle$ を時間で微分すると、3つの積の微分で

$$
\frac{d}{dt}\langle\psi|\hat A|\psi\rangle=\langle\dot\psi|\hat A|\psi\rangle+\langle\psi|\hat A|\dot\psi\rangle+\Big\langle\psi\Big|\frac{\partial\hat A}{\partial t}\Big|\psi\Big\rangle=\frac i\hbar\big\langle[\hat H,\hat A]\big\rangle+\Big\langle\frac{\partial\hat A}{\partial t}\Big\rangle\tag{V-3}
$$

です。**例**：$\hat H=\frac{\hat p^2}{2m}+V(\hat x)$、$\hat A=\hat x$ なら、交換子の積の公式 $[\hat B\hat C,\hat x]=\hat B[\hat C,\hat x]+[\hat B,\hat x]\hat C$（ライプニッツ則。[行列の指数関数と交換子のノート](../04_群論・代数/matrix_exponential_commutator_bch_trotter.md)の Part III §1）と $[\hat p,\hat x]=-i\hbar$ から $[\hat p^2,\hat x]=-2i\hbar\hat p$ なので

$$
\frac{d\langle x\rangle}{dt}=\frac{\langle p\rangle}m,\qquad\frac{d\langle p\rangle}{dt}=-\big\langle V'(x)\big\rangle
$$

で、期待値はニュートンの運動方程式に（ほぼ）従います。

## 4. 外積の時間変化（フォン・ノイマン方程式）

密度行列 $\rho=|\psi\rangle\langle\psi|$（外積）を時間で微分すると

$$
i\hbar\frac{d\rho}{dt}=i\hbar|\dot\psi\rangle\langle\psi|+i\hbar|\psi\rangle\langle\dot\psi|=\hat H|\psi\rangle\langle\psi|-|\psi\rangle\langle\psi|\hat H=[\hat H,\rho]\tag{V-4}
$$

です（**フォン・ノイマン方程式**）。外積に微分が作用する、もっとも基本的な例で、混合状態（[密度行列のノート](density_matrix_bracket_notation.md)の Part II）の時間発展もこの式に従います。

## 5. エネルギーのパラメータ微分（ヘルマン・ファインマンの定理）

ハミルトニアンがパラメータ $\lambda$（原子核の位置、外場の強さなど）に依存し、$\hat H(\lambda)|\psi\rangle=E(\lambda)|\psi\rangle$、$\langle\psi|\psi\rangle=1$ とします。$E=\langle\psi|\hat H|\psi\rangle$ を $\lambda$ で微分すると

$$
\frac{dE}{d\lambda}=\langle\partial_\lambda\psi|\hat H|\psi\rangle+\Big\langle\psi\Big|\frac{\partial\hat H}{\partial\lambda}\Big|\psi\Big\rangle+\langle\psi|\hat H|\partial_\lambda\psi\rangle
$$

で、$\hat H|\psi\rangle=E|\psi\rangle$、$\langle\psi|\hat H=E\langle\psi|$ から第1項と第3項は $E\big(\langle\partial_\lambda\psi|\psi\rangle+\langle\psi|\partial_\lambda\psi\rangle\big)=E\,\frac{d}{d\lambda}\langle\psi|\psi\rangle=0$ になり

$$
\frac{dE}{d\lambda}=\Big\langle\psi\Big|\frac{\partial\hat H}{\partial\lambda}\Big|\psi\Big\rangle\tag{V-5}
$$

です。**状態の微分 $\partial_\lambda\psi$ を計算しなくても、エネルギーの微分が求まる**のがこの定理の価値で、分子の原子核にはたらく力（エネルギーを位置で微分したもの）の計算に使われます（数値でも確認済み）。

**VQE との関係**：量子コンピュータでパラメータ $\theta$ 付きの回路から作った状態 $|\psi(\theta)\rangle$ のエネルギー $E(\theta)=\langle\psi(\theta)|\hat H|\psi(\theta)\rangle$ を最小化するとき（VQE）、勾配はやはり積の微分で $\frac{dE}{d\theta}=2\operatorname{Re}\langle\partial_\theta\psi|\hat H|\psi\rangle$ です（$|\psi(\theta)\rangle$ は固有状態ではないので、式 (V-5) のようには簡単にならない）。回路のゲートが $e^{-i\theta\hat P/2}$（$\hat P$ はパウリ行列の積）の形なら、

$$
\frac{dE}{d\theta}=\frac12\Big[E\Big(\theta+\frac\pi2\Big)-E\Big(\theta-\frac\pi2\Big)\Big]\tag{V-6}
$$

と、**パラメータを $\pm\frac\pi2$ ずらした2回の測定から、勾配が正確に求まります**（パラメータシフト則。数値でも確認済み）。

## 6. 規格化された状態の微分は「純虚数」（ベリー位相）

$\langle\psi(\lambda)|\psi(\lambda)\rangle=1$ を $\lambda$ で微分すると、$\langle\partial_\lambda\psi|\psi\rangle+\langle\psi|\partial_\lambda\psi\rangle=2\operatorname{Re}\langle\psi|\partial_\lambda\psi\rangle=0$ なので、$\langle\psi|\partial_\lambda\psi\rangle$ は**純虚数**です。そこで $A(\lambda)=i\langle\psi|\partial_\lambda\psi\rangle$（実数）とおき、パラメータをゆっくり1周させたときに $\gamma=\oint A\,d\lambda$ を考えると、これが**ベリー位相**（幾何学的位相）になります。$A$ は、[行列値微分形式とゲージ理論のノート](../03_多様体・微分形式・トポロジー/matrix_valued_forms_gauge_theory.md)の「接続」の、量子状態の空間での例です。

## 7. まとめ

| 微分する対象 | 結果 | 名前 |
|---|---|---|
| 内積 $\langle\psi\vert\psi\rangle$ | $0$ | ノルム（確率）の保存 |
| 期待値 $\langle\psi\vert\hat A\vert\psi\rangle$ | $\frac i\hbar\langle[\hat H,\hat A]\rangle$ | エーレンフェストの定理 |
| 外積 $\vert\psi\rangle\langle\psi\vert$ | $\frac1{i\hbar}[\hat H,\rho]$ | フォン・ノイマン方程式 |
| エネルギー $\langle\psi\vert\hat H\vert\psi\rangle$ をパラメータで | $\langle\partial_\lambda\hat H\rangle$ | ヘルマン・ファインマンの定理（VQE ではパラメータシフト則） |
| 規格化 $\langle\psi\vert\psi\rangle=1$ をパラメータで | $\langle\psi\vert\partial_\lambda\psi\rangle$ は純虚数 | ベリー位相 |

---

# まとめ：全体の流れ

```
ブラケット記法の基本
   |x⟩,|p⟩,|n⟩：抽象ベクトル空間の基底（それぞれ演算子の固有状態）
   ⟨x|Ψ⟩=Ψ(x)：射影＝波動関数（成分表示）
        │
        ▼
完全性関係 ∫|x⟩⟨x|dx=1（または Σ|n⟩⟨n|=1）
        │  これを式の好きな場所に挿入できる、というのが実用上の核心
        ▼
K=⟨x_f|e^{-iĤt/ħ}|x_i⟩ に、時間刻みごとに位置の完全性関係を挿入
        │
        ▼
各微小時間の伝播に、運動量の完全性関係を挿入
        │  ⟨x|p⟩=e^{ipx/ħ}/√(2πħ) を使う
        ▼
ガウス積分を実行 → 各ステップがexp[iε(運動エネルギー−ポテンシャル)/ħ]
        │
        ▼
N→∞の連続極限 → 指数の肩が作用 S[x(t)] の積分に収束
        │
        ▼
K(x_f,t;x_i,0) = ∫Dx(t) e^{iS[x(t)]/ħ}　（経路積分）
```

ブラケット記法が最初とっつきにくいのは、$|x\rangle$ のような「基底ベクトルそのもの」を表す記号と、$\langle\Psi|\hat A|\Psi\rangle$ のような「演算子を実際に作用させて計算する」記号が、見た目は似ているのに中身の役割が違うからでした。しかし、その中で**完全性関係を挿入する**という一つのテクニックだけを押さえておけば、抽象的な演算子の式（$e^{-i\hat Ht/\hbar}$ など）を、具体的で計算可能な積分（経路積分）へと機械的に変換できる、というのが今回たどり着いた結論です。この技法は、以前の「基底ベクトルによる添字の上げ下げ」や「別の基底へ射影したときに違う顔を見せる」という話とも、根っこでは同じ「基底の分解」という発想でつながっています。
