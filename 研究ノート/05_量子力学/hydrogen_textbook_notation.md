# 水素原子のシュレディンガー方程式 ―教科書の記法に沿った導出ノート―

このノートは、お使いの教科書（第1章 ミクロの世界の謎、1.8 原子の構造）の記号と展開順序に合わせて、数理的な「途中式」を埋めたものです。教科書側の式番号は振られていないので、代わりに教科書のページと対応する形で節を進めます。記号は教科書に合わせて統一します：

- 電子の質量：$m_e$
- $a := \dfrac{Ze^2}{4\pi\varepsilon_0}$（$Z$：原子番号、水素なら $Z=1$）、これを使うと $V(r)=-\dfrac ar$
- ボーア半径：$r_0 := \dfrac{4\pi\varepsilon_0\hbar^2}{m_ee^2}$
- 球座標は教科書の図の通り（$z$ 軸から測った角度が $\theta$、$xy$ 平面内の角度が $\phi$）

---

# 1. 出発点（教科書 p.34–35 に対応）

3次元の時間に依存しないシュレディンガー方程式：

$$
-\frac{\hbar^2}{2m_e}\left(\frac{\partial^2}{\partial x^2}+\frac{\partial^2}{\partial y^2}+\frac{\partial^2}{\partial z^2}\right)\psi + V(r)\psi = E\psi,
\qquad V(r)=-\frac ar
$$

球座標でのラプラシアン（教科書の式）：

$$
\nabla^2 \equiv \frac1{r^2}\frac{\partial}{\partial r}\left(r^2\frac{\partial}{\partial r}\right) + \frac1{r^2\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta\frac{\partial}{\partial\theta}\right) + \frac1{r^2\sin^2\theta}\frac{\partial^2}{\partial\phi^2}
$$

（このラプラシアンが「なぜこの形になるか」は、前回のラプラス・ベルトラミ作用素のノートで詳しく導出済みです。ここでは教科書と同様に既知として使います。）

これを使うと、シュレディンガー方程式は

$$
-\frac{\hbar^2}{2m_e}\left[\frac1{r^2}\frac{\partial}{\partial r}\left(r^2\frac{\partial}{\partial r}\right)+\frac1{r^2\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta\frac{\partial}{\partial\theta}\right)+\frac1{r^2\sin^2\theta}\frac{\partial^2}{\partial\phi^2}\right]\psi + V(r)\psi = E\psi
$$

---

# 2. $\psi=R(r)Y(\theta,\phi)$ と置く（教科書 p.35–36）

代入して $-\dfrac{2m_er^2}{\hbar^2\psi}$ を掛けると：

$$
\frac1{R(r)}\frac{d}{dr}\left(r^2\frac{dR}{dr}\right) + \frac{2m_er^2}{\hbar^2}\big(E-V(r)\big)
= -\frac1{Y(\theta,\phi)}\left[\frac1{\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta\frac{\partial}{\partial\theta}\right)+\frac1{\sin^2\theta}\frac{\partial^2}{\partial\phi^2}\right]Y
$$

左辺は $r$ のみ、右辺は $\theta,\phi$ のみの関数なので、両辺は共通の定数（教科書の記号 $\alpha$）に等しくなければなりません：

$$
\boxed{\frac{d}{dr}\left(r^2\frac{dR}{dr}\right) + \frac{2m_er^2}{\hbar^2}\big(E-V(r)\big)R = \alpha R}\tag{動径方程式}
$$

$$
\boxed{\left[\frac1{\sin\theta}\frac{\partial}{\partial\theta}\left(\sin\theta\frac{\partial}{\partial\theta}\right)+\frac1{\sin^2\theta}\frac{\partial^2}{\partial\phi^2}\right]Y = -\alpha\,Y}\tag{角度方程式}
$$

（教科書は動径方程式の両辺に $r^2$ を掛けたままの形で書いているので、ここでも $\dfrac1{r^2}$ で割らずにこの形を保ちます。前回のノートでは割った形を使いましたが、本質的には同じ方程式です。）

---

# 3. $Y=\Theta(\theta)\Phi(\phi)$ と分離する（教科書 p.36–37）

角度方程式に代入し、$\sin^2\theta/(\Theta\Phi)$ を掛けると：

$$
\frac{\sin\theta}{\Theta}\frac{d}{d\theta}\left(\sin\theta\frac{d\Theta}{d\theta}\right) + \alpha\sin^2\theta = -\frac1\Phi\frac{d^2\Phi}{d\phi^2}
$$

左辺は $\theta$ のみ、右辺は $\phi$ のみなので、共通の定数（教科書の記号 $\beta$）に等しい：

$$
\frac{d^2\Phi}{d\phi^2} = -\beta\,\Phi(\phi)\tag{$\Phi$方程式}
$$

$$
\left[\sin\theta\frac{d}{d\theta}\left(\sin\theta\frac{d}{d\theta}\right)+\alpha\sin^2\theta\right]\Theta(\theta) = \beta\,\Theta(\theta)\tag{$\Theta$方程式}
$$

## 3-1. $\Phi$ 方程式を解く

一般解は

$$
\Phi(\phi) = Ce^{i\sqrt\beta\phi} + De^{-i\sqrt\beta\phi}
$$

角度 $\phi$ は物理的に $\phi$ と $\phi+2\pi$ が同じ点を指すので、一価性 $\Phi(\phi+2\pi)=\Phi(\phi)$ を要求すると $e^{i2\pi\sqrt\beta}=1$、つまり $\sqrt\beta=m$（整数）でなければなりません。したがって $\beta=m^2$ で、

$$
\boxed{\Phi_m(\phi) = Ae^{im\phi}+Be^{-im\phi}}\qquad(m=0,\pm1,\pm2,\dots)
$$

（正の $m$ と負の $m$ をそれぞれ別の解として扱えば、$Ae^{im\phi}$ の形だけで $m$ の全範囲をカバーできます。規格化条件 $\int_0^{2\pi}|\Phi_m|^2d\phi=1$ から係数を決めれば $\Phi_m(\phi)=\dfrac1{\sqrt{2\pi}}e^{im\phi}$ です。）

$\beta=m^2$ を $\Theta$ 方程式に戻すと：

$$
\boxed{\left[\sin\theta\frac{d}{d\theta}\left(\sin\theta\frac{d}{d\theta}\right)+\alpha\sin^2\theta\right]\Theta(\theta) = m^2\,\Theta(\theta)}
$$

---

# 4. $x=\cos\theta$ への変換とLegendre方程式への帰着

両辺を $\sin^2\theta$ で割って整理すると：

$$
\frac1{\sin\theta}\frac{d}{d\theta}\left(\sin\theta\frac{d\Theta}{d\theta}\right) + \left[\alpha-\frac{m^2}{\sin^2\theta}\right]\Theta = 0
$$

$x=\cos\theta$（$\sin^2\theta=1-x^2$、$\frac{d}{d\theta}=-\sin\theta\frac{d}{dx}$）と置換すると（計算は積の微分を機械的に展開するだけです）：

$$
\boxed{\frac{d}{dx}\left[(1-x^2)\frac{d\Theta}{dx}\right] + \left[\alpha-\frac{m^2}{1-x^2}\right]\Theta = 0}\tag{associated Legendre方程式}
$$

**なぜ $\alpha=l(l+1)$ でなければならないか**：$x=0$ のまわりでべき級数 $\Theta=\sum_ka_kx^k$ として解くと、漸化式の分子に $k(k+1)-\alpha$ が現れます。$\alpha$ がこの形（$l(l+1)$、$l$：非負整数）でない限り、級数は $x\to\pm1$（$\theta\to0,\pi$、球の極）で発散し、物理的に許される（有限な）波動関数になりません。したがって

$$
\boxed{\alpha=l(l+1),\qquad l=0,1,2,\dots}
$$

これが方位量子数 $l$ の由来です。以後 $\alpha=l(l+1)$ として進めます。

---

# 5. Legendre多項式の構成（$m=0$ の場合）

級数を最後まで追う代わりに、Legendre方程式

$$
(1-x^2)y''-2xy'+l(l+1)y=0
$$

を満たす多項式を直接構成します。$w(x):=(x^2-1)^l$ とおくと

$$
w'=2lx(x^2-1)^{l-1}=\frac{2lx}{x^2-1}w \quad\Longrightarrow\quad (x^2-1)w'=2lx\,w\tag{5-1}
$$

この恒等式の両辺を $(l+1)$ 回微分します。ライプニッツの公式 $\dfrac{d^n}{dx^n}(uv)=\sum_{k=0}^n\binom nk u^{(k)}v^{(n-k)}$ を使うと（左辺は $u=x^2-1$、$u'=2x$、$u''=2$；右辺は $u=2lx$、$u'=2l$）：

$$
(x^2-1)w^{(l+2)}+2(l+1)xw^{(l+1)}+l(l+1)w^{(l)} = 2lxw^{(l+1)}+2l(l+1)w^{(l)}
$$

整理すると（$y:=w^{(l)}$、$w^{(l+1)}=y'$、$w^{(l+2)}=y''$）：

$$
(x^2-1)y''+2xy'-l(l+1)y=0 \quad\Longleftrightarrow\quad (1-x^2)y''-2xy'+l(l+1)y=0
$$

つまり $y=\dfrac{d^l}{dx^l}(x^2-1)^l$ は自動的にLegendre方程式を満たします。規格化して（$x=1$ で値 $1$ になるよう定数を選ぶ）：

$$
\boxed{P_l(x) \equiv \frac1{2^ll!}\frac{d^l}{dx^l}(x^2-1)^l}\qquad\text{（教科書の定義と一致：ルジャンドル多項式）}
$$

$(x^2-1)^l$ は $2l$ 次多項式なので、$l$ 回微分すると $l$ 次の多項式になり、$\theta=0,\pi$ での発散も自動的に回避されます。

---

# 6. Legendre陪多項式の構成（$m\ne0$ の場合）

Legendre方程式 $(1-x^2)P_l''-2xP_l'+l(l+1)P_l=0$ の両辺を $x$ で $|m|$ 回微分します（以後 $|m|$ をそのまま使い、教科書と同じく符号は付けません）。ライプニッツの公式を各項に適用し（第1項は $u=1-x^2$、第2項は $u=-2x$）、$v:=P_l^{(|m|)}$ と置いて整理すると：

$$
\boxed{(1-x^2)v''-2(|m|+1)xv'+\big[l(l+1)-|m|(|m|+1)\big]v=0}\tag{6-1}
$$

つぎに $\Theta(x):=(1-x^2)^{|m|/2}v(x)$ と置いて、これが associated Legendre方程式そのものを満たすことを確認します。$s:=(1-x^2)^{|m|/2}$、$s'=-\dfrac{|m|xs}{1-x^2}$ を使って $\Theta',\Theta''$ を計算し（積の微分・商の微分を機械的に展開するだけ）、(6-1) を代入して整理すると：

$$
(1-x^2)\Theta''-2x\Theta'+\left[l(l+1)-\frac{m^2}{1-x^2}\right]\Theta=0
$$

が得られ、これはまさに4節の associated Legendre方程式です。したがって：

$$
\boxed{P_l^{|m|}(x) \equiv (1-x^2)^{|m|/2}\frac{d^{|m|}}{dx^{|m|}}P_l(x)}\qquad\text{（教科書の定義と一致：ルジャンドルの陪多項式）}
$$

$P_l$ は $l$ 次多項式なので、$|m|$ 回微分できるためには $|m|\le l$ が必要です。これが磁気量子数の範囲 $m=-l,\dots,l$ の由来です。

---

# 7. $\Theta_{l,m}(\theta)$ の組み立てと規格化

$\Theta$ を $x=\cos\theta$ に戻し、規格化定数と教科書の位相因子 $(-1)^{(m+|m|)/2}$（$m\ge0$ のとき $(-1)^m$、$m<0$ のとき $+1$ になる、教科書独自の符号の割り振り方）を付けると：

$$
\boxed{\Theta_{l,m}(\theta) = (-1)^{\frac{m+|m|}2}\sqrt{\frac{2l+1}2\frac{(l-|m|)!}{(l+|m|)!}}\,P_l^{|m|}(\cos\theta)}
$$

（規格化定数は $\displaystyle\int_0^\pi\Theta_{l,m}(\theta)^2\sin\theta\,d\theta=1$ という条件から、$P_l^{|m|}$ の直交関係 $\displaystyle\int_{-1}^1P_l^{|m|}(x)P_{l'}^{|m|}(x)dx=\dfrac2{2l+1}\dfrac{(l+|m|)!}{(l-|m|)!}\delta_{ll'}$ を使って決まります。）

**検算（教科書 p.38–39 の表と一致することの確認）**：

$$
\Theta_{0,0}=\sqrt{\tfrac12},\qquad
\Theta_{1,0}=\sqrt{\tfrac32}\cos\theta,\qquad
\Theta_{1,\pm1}=\pm\sqrt{\tfrac34}\sin\theta
$$
$$
\Theta_{2,0}=\sqrt{\tfrac58}(3\cos^2\theta-1),\qquad
\Theta_{2,\pm1}=\pm\sqrt{\tfrac{15}4}\sin\theta\cos\theta,\qquad
\Theta_{2,\pm2}=\sqrt{\tfrac{15}{16}}\sin^2\theta
$$

これらは実際に $P_0=1$、$P_1=x$、$P_2=\frac12(3x^2-1)$（5節の公式から）と、$P_1^1=(1-x^2)^{1/2}\cdot1=\sin\theta$、$P_2^1=(1-x^2)^{1/2}\cdot3x=3\sin\theta\cos\theta$、$P_2^2=(1-x^2)\cdot3=3\sin^2\theta$（6節の公式から）を代入し、規格化定数と符号を掛ければ再現できます。$m$ の偶奇で符号がどう付くか（$m=1$ には $-$、$m=2$ には $+$、$m=-1,-2$ には符号なし）も、$(-1)^{(m+|m|)/2}$ の定義通りです。

角度部分の全体は $Y(\theta,\phi)=\Theta_{l,m}(\theta)\Phi_m(\phi)$ です。

---

# 8. 動径方程式（教科書 p.36–37, 40–41）

2節の動径方程式に $\alpha=l(l+1)$ を代入します：

$$
\boxed{\left[\frac{d}{dr}\left(r^2\frac{d}{dr}\right)+\frac{2m_er^2}{\hbar^2}\big(E-V(r)\big)-l(l+1)\right]R(r)=0}\tag{動径方程式・確定版}
$$

これが教科書 p.41 に載っている最終形です。ここから $R_{nl}(r)$ を求めます。

## 8-1. $u(r)=rR(r)$ と置く

まず恒等式を確認します。$R=u/r$ なら

$$
r^2\frac{dR}{dr}=r^2\left(\frac{u'}r-\frac u{r^2}\right)=ru'-u,\qquad
\frac{d}{dr}(ru'-u)=ru''
$$

つまり $\dfrac{d}{dr}\left(r^2\dfrac{dR}{dr}\right)=ru''$。動径方程式（両辺を $r^2$ で割った上で $u=rR$ を使う形の方が以降の計算が見やすいので、ここだけ $\frac1{r^2}$ で割ります）：

$$
-\frac{\hbar^2}{2m_e}u''+\left[V(r)+\frac{\hbar^2l(l+1)}{2m_er^2}\right]u=Eu
$$

これは1次元シュレディンガー方程式と同じ形で、$\dfrac{\hbar^2l(l+1)}{2m_er^2}$ が遠心力ポテンシャルです。

## 8-2. 無次元化（ボーア半径 $r_0$ の導入）

束縛状態 $E<0$ に対して

$$
\kappa:=\frac{\sqrt{-2m_eE}}\hbar,\qquad \rho:=2\kappa r
$$

とおきます。$V(r)=-\dfrac ar$ を代入して整理すると：

$$
\frac{d^2u}{d\rho^2}=\left[\frac{l(l+1)}{\rho^2}-\frac\lambda\rho+\frac14\right]u,\qquad
\lambda:=\frac{m_ea}{\hbar^2\kappa}
$$

## 8-3. 漸近的な振る舞い

$\rho\to\infty$：方程式は $\dfrac{d^2u}{d\rho^2}\approx\dfrac14u$ に近づき、有限な解は $u\sim e^{-\rho/2}$。

$\rho\to0$：方程式は $\dfrac{d^2u}{d\rho^2}\approx\dfrac{l(l+1)}{\rho^2}u$ に近づき（オイラー型、$u=\rho^s$ を代入すると $s(s-1)=l(l+1)$）、原点で有限な解は $u\sim\rho^{l+1}$。

## 8-4. Laguerre方程式への帰着

$u(\rho)=\rho^{l+1}e^{-\rho/2}L(\rho)$ と置いて方程式に代入し（積の微分を2回展開）整理すると：

$$
\rho L''+\big[2(l+1)-\rho\big]L'+(\lambda-l-1)L=0
$$

$k:=2l+1$、$n':=\lambda-l-1$ と置き直せば：

$$
\boxed{\rho L''+(k+1-\rho)L'+n'L=0}\tag{associated Laguerre方程式}
$$

---

# 9. Laguerre多項式の構成（教科書 p.40 の定義と一致させる）

## 9-1. 素のLaguerre方程式 $\rho y''+(1-\rho)y'+ny=0$（$k=0$）

$w(\rho):=\rho^ne^{-\rho}$ とおくと

$$
w'=\left(\frac n\rho-1\right)w \quad\Longrightarrow\quad \rho w'=(n-\rho)w\tag{9-1}
$$

両辺を $(n+1)$ 回微分し（ライプニッツの公式、左辺は $u=\rho$、右辺は $u=n-\rho$）、$z:=w^{(n)}$ と置いて整理すると：

$$
\rho z''+(1+\rho)z'+(n+1)z=0
$$

（$w=\rho^ne^{-\rho}$ が $e^{-\rho}$ を含むため、$z$ 自体はまだ多項式になりません。）そこで $z(\rho)=e^{-\rho}L_n(\rho)$ と置いて代入し直すと（$z'=e^{-\rho}(L_n'-L_n)$、$z''=e^{-\rho}(L_n''-2L_n'+L_n)$ を使う）：

$$
\boxed{\rho L_n''+(1-\rho)L_n'+nL_n=0}
$$

$L_n(\rho)=e^\rho z(\rho)=e^\rho w^{(n)}(\rho)$ なので：

$$
\boxed{L_n(\rho) \equiv e^{\rho}\frac{d^n}{d\rho^n}\big(\rho^ne^{-\rho}\big)}\qquad\text{（教科書の定義と一致：ラゲール多項式）}
$$

## 9-2. Laguerre陪多項式

素のLaguerre方程式を $k$ 回微分すると（Part 6 の associated Legendre のときとまったく同じ論理で）、$(k+1-\rho)$ を係数に持つ associated Laguerre方程式の解が得られます：

$$
\boxed{L_n^k(\rho) \equiv \frac{d^k}{d\rho^k}L_n(\rho)}\qquad\text{（教科書の定義と一致：ラゲールの陪多項式）}
$$

は

$$
\rho(L_n^k)''+(k+1-\rho)(L_n^k)'+(n-k)L_n^k=0
$$

を満たします。8節の associated Laguerre方程式（$n'=n-k$、$k=2l+1$）と比較すると：

$$
n'=\lambda-l-1=n-k=n-(2l+1) \quad\Longrightarrow\quad n=\lambda+l
$$

$L(\rho)=L_n^{2l+1}(\rho)$（$n=\lambda+l$）が**多項式で終わる**（無限級数のまま発散しない）ためには、$n$ が非負整数である必要があります。$n-k=n'\ge0$（多項式の次数が非負）から $n\ge2l+1$、つまり

$$
\boxed{l\le n-1}
$$

---

# 10. 量子化とエネルギー準位（教科書 p.41–42 に対応）

$n=\lambda+l$ が非負整数でなければならないので、$\lambda$ も整数：

$$
\lambda=n\qquad(n=1,2,3,\dots,\ \text{主量子数})
$$

（8-2節の定義 $\lambda=\dfrac{m_ea}{\hbar^2\kappa}$ から $\kappa=\dfrac{m_ea}{\hbar^2n}$。）束縛エネルギー $E=-\dfrac{\hbar^2\kappa^2}{2m_e}$ に代入すると：

$$
E_n = -\frac{\hbar^2}{2m_e}\left(\frac{m_ea}{\hbar^2n}\right)^2 = -\frac{a^2m_e}{2\hbar^2}\cdot\frac1{n^2}
$$

$$
\boxed{E_n = -\frac{a^2m_e}{2\hbar^2}\frac1{n^2} = -\left(\frac{Ze^2}{4\pi\varepsilon_0}\right)^2\frac{m_e}{2\hbar^2}\frac1{n^2} = -\frac{Z^2e^4m_e}{32\varepsilon_0^2\pi^2\hbar^2}\frac1{n^2}}
$$

これは教科書 p.42 の式と完全に一致します。

ボーア半径 $r_0=\dfrac{4\pi\varepsilon_0\hbar^2}{m_ee^2}$ を使うと $\kappa=\dfrac Z{nr_0}$、したがって

$$
\boxed{\rho = 2\kappa r = \frac{2Zr}{nr_0}}
$$

（教科書の $R_{nl}(r)$ に出てくる無次元変数と一致します。）

---

# 11. 動径波動関数と全体の波動関数

$$
u(\rho)=\rho^{l+1}e^{-\rho/2}L_{n+l}^{2l+1}(\rho)
$$

（9-2節の $n_{\text{Laguerre添字}}=\lambda+l=n+l$ を使用）。$R(r)=u(r)/r$、$\rho=2Zr/(nr_0)$ を戻すと：

$$
\boxed{R_{nl}(r) = N_{nl}\left(\frac{2Zr}{nr_0}\right)^l e^{-Zr/(nr_0)}L_{n+l}^{2l+1}\!\left(\frac{2Zr}{nr_0}\right)}
$$

$N_{nl}$ は $\displaystyle\int_0^\infty R_{nl}(r)^2r^2dr=1$ から決まる規格化定数です。

## 11-1. 規格化定数の逆算（検算）

$\rho=\dfrac{2Zr}{nr_0}$（$dr=\dfrac{nr_0}{2Z}d\rho$）で変数変換すると：

$$
N_{nl}^2\left(\frac{nr_0}{2Z}\right)^3\int_0^\infty e^{-\rho}\rho^{2l+2}\big[L_{n+l}^{2l+1}(\rho)\big]^2d\rho = 1
$$

教科書の定義（$L_N^k=\dfrac{d^k}{dx^k}L_N$、$L_N=e^x\dfrac{d^N}{dx^N}(x^Ne^{-x})$）に対する標準的な直交性の積分公式：

$$
\int_0^\infty e^{-x}x^{k+1}\big[L_N^k(x)\big]^2dx = (2N-k+1)\frac{(N!)^3}{(N-k)!}
$$

に $N=n+l$、$k=2l+1$（$2N-k+1=2n$、$N-k=n-l-1$）を代入すると：

$$
\int_0^\infty e^{-\rho}\rho^{2l+2}\big[L_{n+l}^{2l+1}(\rho)\big]^2d\rho = 2n\,\frac{[(n+l)!]^3}{(n-l-1)!}
$$

規格化条件に戻して整理すると：

$$
\boxed{N_{nl}^2 = \left(\frac{2Z}{nr_0}\right)^3\frac{(n-l-1)!}{2n\,[(n+l)!]^3}}
$$

**教科書 p.40 の印字（$N_{nl}=-\left(\frac{2Z}{nr_0}\right)^{3/2}\sqrt{\dfrac{(n-l-1)!}{2n[(n+l)!]^3}}$）と完全に一致します。** 分子の $(n-l-1)!$ は $L_{n+l}^{2l+1}$ の多項式としての次数（$N-k=n-l-1$）から、分母の $[(n+l)!]^3$（3乗）は、$L_N$ をRodriguesの公式 $e^x\frac{d^N}{dx^N}(x^Ne^{-x})$ でそのまま（$1/N!$ を付けずに）定義するこの教科書の流儀に起因します。数学の教科書でよく使われる「$L_N$ に最初から $1/N!$ を付ける」規格化を採用すると、この3乗の因子は現れず、Griffithsなどの洋書でよく見る $(n+l)!$ の1乗だけのシンプルな形になります。**$L_N$ に $1/N!$ を付けるかどうかという規格化の流儀の違いが、そのまま規格化定数の階乗の指数の違いとして表れている**、というのがこの複雑さの正体です。

## 11-2. 注：一般的な（他の教科書でよく使われる）ラゲール陪多項式の流儀

物理・数学の文献でより一般的に使われるのは、パラメータ $\alpha$ を持つ一般ラゲール多項式です（Rodriguesの公式に最初から $\dfrac1{n!}$ を含む）：

$$
L_n^{(\alpha)}(x) := \frac{x^{-\alpha}e^x}{n!}\frac{d^n}{dx^n}\left(e^{-x}x^{n+\alpha}\right)
$$

これは $xy''+(\alpha+1-x)y'+ny=0$ を満たし、Part 8の associated Laguerre方程式（$\alpha=k$、$n\to n'$）と同一です。教科書の $L_N^k=\dfrac{d^k}{dx^k}L_N$（$L_N=e^x\frac{d^N}{dx^N}(x^Ne^{-x})$、$1/N!$ なし）とは、標準的な微分公式 $\dfrac{d^k}{dx^k}L_n^{(0)}(x)=(-1)^kL_{n-k}^{(k)}(x)$ を使うと

$$
L_N^k(x) = (-1)^kN!\,L_{N-k}^{(k)}(x)
$$

という関係で結ばれています。水素原子の場合（$N=n+l,\ k=2l+1$）：

$$
L_{n+l}^{2l+1}(x) = -(n+l)!\,L_{n-l-1}^{(2l+1)}(x)
$$

これを使って動径波動関数を書き直すと：

$$
R_{nl}(r) = N_{nl}'\left(\frac{2Zr}{nr_0}\right)^le^{-Zr/(nr_0)}L_{n-l-1}^{(2l+1)}\!\left(\frac{2Zr}{nr_0}\right)
$$

一般ラゲール多項式の標準的な直交性積分公式 $\displaystyle\int_0^\infty x^{\alpha+1}e^{-x}\big[L_n^{(\alpha)}(x)\big]^2dx=\dfrac{(n+\alpha)!}{n!}(2n+\alpha+1)$（$\alpha=2l+1,\ n\to n-l-1$）を使うと：

$$
\boxed{N_{nl}'^2 = \left(\frac{2Z}{nr_0}\right)^3\frac{(n-l-1)!}{2n\,(n+l)!}}
$$

$3$乗が消え、$(n+l)!$ の1乗だけのシンプルな形になります。多くの洋書（Griffiths, Sakurai など）はこちらの流儀（あるいはそれに近い流儀）を採用しています。**他の教科書・文献を読むときは、「$L$ に $1/n!$ が含まれているかどうか」を必ず定義式で確認する**のがポイントです。

全体の波動関数：

$$
\boxed{\psi_{nlm}(r,\theta,\phi) = R_{nl}(r)\,\Theta_{l,m}(\theta)\,\Phi_m(\phi)}
$$

量子数の範囲：

$$
n=1,2,3,\dots,\qquad l=0,1,\dots,n-1,\qquad m=-l,\dots,l
$$

教科書の表（K殻・L殻・M殻、$s,p,d,f$ 軌道）：

| $n$ | 殻 | $l$ | 軌道記号 | $m$ の範囲 |
|---|---|---|---|---|
| 1 | K殻 | 0 | 1s | $m=0$ |
| 2 | L殻 | 0 | 2s | $m=0$ |
| 2 | L殻 | 1 | 2p | $m=-1,0,1$ |
| 3 | M殻 | 0 | 3s | $m=0$ |
| 3 | M殻 | 1 | 3p | $m=-1,0,1$ |
| 3 | M殻 | 2 | 3d | $m=-2,-1,0,1,2$ |

（$l=0,1,2,3,\dots$ を $s,p,d,f,\dots$ と呼ぶのは分光学の歴史的な呼び名 sharp, principal, diffuse, fundamental の頭文字に由来する、と教科書に書かれている通りです。）

---

# まとめ：導出の全体フロー（教科書の記号で）

```
シュレディンガー方程式（球座標、V=-a/r）
        │  ψ=R(r)Y(θ,φ)
        ▼
動径方程式（定数α）      角度方程式（同じα）
        │                     │  Y=Θ(θ)Φ(φ)
        │                     ▼
        │              Φ''=-βΦ → 一価性 → β=m²、Φ_m=Ae^{imφ}
        │                     │
        │                     ▼
        │              Θ方程式 → x=cosθ → associated Legendre方程式
        │                     │  正則性 → α=l(l+1)
        │                     ▼
        │              P_l(x)=(1/2^l l!)d^l/dx^l(x²-1)^l（Rodrigues, l+1回微分で構成）
        │                     │  |m|回微分 + (1-x²)^{|m|/2}
        │                     ▼
        │              P_l^{|m|}(x) → Θ_{l,m}(θ)（規格化＋位相 (-1)^{(m+|m|)/2}）
        │
        ▼  α=l(l+1)代入、u=rR、ρ=2κr で無次元化、漸近形 ρ^{l+1}e^{-ρ/2}
associated Laguerre方程式
        │
        ▼
L_n(ρ)=e^ρ d^n/dρ^n(ρ^n e^{-ρ})（Rodrigues, n+1回微分で構成）
        │  k=2l+1回微分
        ▼
L_n^k(ρ) → 多項式で終わる条件 → n=λ+l ∈ ℤ → λ=n（主量子数）
        │
        ▼
E_n = -a²m_e/(2ħ²n²)、R_{nl}(r) = N_{nl}(2Zr/nr_0)^l e^{-Zr/(nr_0)} L_{n+l}^{2l+1}(2Zr/nr_0)
        │
        ▼
ψ_{nlm}(r,θ,φ) = R_{nl}(r) Θ_{l,m}(θ) Φ_m(φ)
```

LegendreもLaguerreも、**「ある関数 $w$ を作り、その満たす簡単な恒等式をライプニッツの公式で必要な回数だけ微分する」という同じ手法**で多項式解を構成できる、という点が教科書には書かれていない（結果だけが与えられている）「途中式」の核心部分でした。
