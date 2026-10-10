# 微分形式とHodgeスター演算子 ―div, grad, rotの統一言語―

> **作成** 2026-10-01　**更新** 2026-10-03
> 微分形式とホッジスター演算子のノート。div・grad・rot、計量テンソル、ラプラス・ベルトラミ作用素が、
> 微分形式という1つの言語で統一され、ラプラシアンが ⋆d⋆d に集約されることを示す。

これまでの一連のノート（計量テンソル、ラプラス・ベルトラミ作用素、クリストッフェル記号、div/grad/rotの恒等式）が、実は**すべて1つの言語（微分形式）の中で統一的に記述できる**ことを示します。最後に、最初のノートで導出したラプラス・ベルトラミ作用素の公式が、$\star d\star d$というたった4文字の式に集約されることを確認します。

---

# Part I：微分形式とは何か

## 1. $k$-形式（$k$-form）

微分形式とは、**完全反対称なテンソル**を、基底 $dx^i$ の**外積**（wedge積）で表したものです。

- **0-形式**：ただの関数 $f$
- **1-形式**：$\omega = a\,dx+b\,dy+c\,dz$（$a,b,c$は関数）
- **2-形式**：$\omega = p\,dy\wedge dz+q\,dz\wedge dx+r\,dx\wedge dy$
- **3-形式**：$\omega = h\,dx\wedge dy\wedge dz$

3次元では4-形式以上は存在しません（4つ以上の$dx^i$を反対称に掛け合わせると、必ずどれか2つが重複して自動的にゼロになるからです）。

## 2. 外積（wedge積）の性質

$$
\boxed{dx^i\wedge dx^j = -dx^j\wedge dx^i}\qquad(\text{特に}\ dx^i\wedge dx^i=0)
$$

これは、以前扱った**レヴィ・チヴィタ記号 $\varepsilon_{ijk}$ の完全反対称性と、まったく同じ構造**です。実際、$k$-形式の成分は「反対称テンソル」そのものであり、$\varepsilon_{ijk}$（3階の完全反対称テンソル）は、まさに3-形式 $dx\wedge dy\wedge dz$ の成分表示に他なりません。

## 3. 完全反対称テンソルとは何か（補足）

$k$-形式の正体である「完全反対称テンソル」を、ここで簡単に整理しておきます。

**定義**：$k$階のテンソル $T_{i_1\cdots i_k}$ が完全反対称であるとは、どの2つの添字を入れ替えても符号が反転することを言います：

$$
\boxed{T_{\cdots i_a\cdots i_b\cdots} = -T_{\cdots i_b\cdots i_a\cdots}}
$$

**帰結**：同じ添字が2回出てくると、$T=-T$となり自動的にゼロになります。したがって、成分がゼロでないためには**すべての添字が互いに異なっている**必要があります。

**独立成分の個数**：$n$次元空間の完全反対称$k$階テンソルの独立成分は

$$
\boxed{\binom nk = \frac{n!}{k!(n-k)!}\ \text{個}}
$$

（添字の並び順の違いは符号だけの違いなので「同じ情報」とみなせ、独立な選び方の数だけ成分がある。）

**具体例**：

- $n=3,k=3$（$\varepsilon_{ijk}$）：$\binom33=1$ → 定数倍を除いて唯一の完全反対称3階テンソル
- $n=3,k=2$（$\operatorname{rot}\mathbf v$の元になる $\partial_iv_j-\partial_jv_i$）：$\binom32=3$ → たまたまベクトルの成分数（3）と一致する
- $n=4,k=2$（電磁場テンソル$F_{\mu\nu}$）：$\binom42=6$ → 電場3成分＋磁場3成分の正体

**この$\binom nk$という数え方こそ、「なぜ3次元でしか$\operatorname{rot}$を単純にベクトルとして扱えないのか」の答え**です。$n=3,k=2$のときだけ$\binom32=3=n$という偶然の一致が起き、2階の反対称テンソルとベクトル（1階テンソル）が同一視できています。$4$次元以上ではこの一致が崩れるため、$\operatorname{rot}$の一般化は2-形式（あるいは反対称テンソル）のまま扱う必要があり、単純な1本のベクトルには戻せなくなります。

## 4. wedge積の代数的性質（補足）

wedge積が満たす基本性質を整理しておきます（$\alpha,\beta,\gamma$は形式、$a,b$はスカラー）：

$$
\boxed{
\begin{aligned}
&\alpha\wedge\alpha=0\\
&\alpha\wedge\beta=-\beta\wedge\alpha\qquad\text{（交代性）}\\
&(a\alpha+b\beta)\wedge\gamma=a(\alpha\wedge\gamma)+b(\beta\wedge\gamma)\qquad\text{（双線形性）}\\
&(\alpha\wedge\beta)\wedge\gamma=\alpha\wedge(\beta\wedge\gamma)\qquad\text{（結合則）}
\end{aligned}
}
$$

**ここで重要な注意点**：wedge積には結合則がありますが、**普通のベクトルの外積 $\mathbf a\times\mathbf b$ には結合則がありません**（$(\mathbf a\times\mathbf b)\times\mathbf c\ne\mathbf a\times(\mathbf b\times\mathbf c)$、これは前回のBAC-CAB則からも確認できます：両辺を計算すると一般に異なる式になります）。wedge積はベクトルの外積よりも**素性の良い、代数的に扱いやすい演算**であり、$\mathbf a\times\mathbf b$は「wedge積を取ってからHodgeスターで戻す」という、より複雑な操作の結果になっています（この点はPart V §3で実際に導出・検証します）。

## 5. 次数付き交換則（$p$-形式と$q$-形式のwedge積）

$p$-形式 $\lambda$ と $q$-形式 $\mu$ のwedge積には、一般化された交代性があります：

$$
\boxed{\lambda\wedge\mu = (-1)^{pq}\mu\wedge\lambda}
$$

$p=q=1$（1-形式同士）なら $(-1)^{1\cdot1}=-1$ となり、おなじみの $\alpha\wedge\beta=-\beta\wedge\alpha$ に一致します。$p=1,q=2$（1-形式と2-形式）なら$(-1)^{1\cdot2}=1$となり、**符号が変わらず交換できます**（$1\times2$個の基底を1つずつ隣と入れ替えていくと、偶数回の入れ替えで元に戻るため）。

## 6. wedge積とベクトルの外積・内積の対応（検算）

1-形式 $\lambda=Ax+By+Cz$、$\mu=Ex+Fy+Gz$（$x,y,z$は基底 $dx,dy,dz$ の略記）のwedge積を、性質1〜4だけを使って展開します：

$$
\lambda\wedge\mu = AE(x\wedge x)+AF(x\wedge y)+AG(x\wedge z)+BE(y\wedge x)+BF(y\wedge y)+BG(y\wedge z)+CE(z\wedge x)+CF(z\wedge y)+CG(z\wedge z)
$$

$x\wedge x=y\wedge y=z\wedge z=0$、$y\wedge x=-x\wedge y$等を使って整理すると：

$$
\boxed{\lambda\wedge\mu = (AF-BE)\,x\wedge y+(CE-AG)\,z\wedge x+(BG-CF)\,y\wedge z}
$$

係数 $(BG-CF,\ CE-AG,\ AF-BE)$ を見ると、これは**ベクトル $(A,B,C)\times(E,F,G)$ の成分そのもの**です（以前確認した外積の成分公式と完全に一致）。1-形式同士のwedge積が2-形式（＝Hodgeスターを通せばベクトルの外積）に対応する、というPart IIIの内容が、ここでも具体的な展開で裏付けられます。

さらに、1-形式と2-形式のwedge積は、**内積に対応**します：

$$
(Ax+By+Cz)\wedge(P\,y\wedge z+Q\,z\wedge x+R\,x\wedge y) = (AP+BQ+CR)\,x\wedge y\wedge z
$$

係数 $AP+BQ+CR$ は、ベクトル$(A,B,C)$と$(P,Q,R)$の**内積**そのものです。**「1-形式∧1-形式→外積」「1-形式∧2-形式→内積」という対応が、wedge積の代数だけから自然に出てくる**、というのがこの検算のポイントです。

---

# Part II：外微分 $d$ の定義

外微分 $d$ は、$k$-形式を $(k+1)$-形式に変換する演算子です。**関数の各偏微分に、対応する $dx^i$ を1本追加して外積を取る**、という操作です。

$$
d(f) := \partial_if\,dx^i,\qquad d(\omega_idx^i) := \partial_j\omega_i\,dx^j\wedge dx^i,\qquad\dots
$$

これから、$d$を3次元で具体的に計算すると、**div, grad, rotの正体そのものが姿を現します。**

---

# Part III：3次元での具体的対応 ―計算で確認する

## 1. $d(0\text{-形式}) \leftrightarrow \operatorname{grad}$

$$
df = \partial_xf\,dx+\partial_yf\,dy+\partial_zf\,dz
$$

係数を並べたベクトル $(\partial_xf,\partial_yf,\partial_zf)$ は、まさに $\operatorname{grad}f$ です。

$$
\boxed{df \ \longleftrightarrow\ \operatorname{grad}f}
$$

（**注**：ここでは$df$（1-形式）と$\operatorname{grad}f$（ベクトル）を、平坦な直交座標での成分の一致に基づいて同一視しています。厳密には$\operatorname{grad}f=(df)^\sharp$という、$\sharp$（音楽同型）を経由した関係ですが、$\sharp$はPart VIでまとめて導入するので、それまでは「係数を並べればそのままgrad」という、この節の対応で進めます。）

## 2. $d(1\text{-形式}) \leftrightarrow \operatorname{rot}$

$\omega=a\,dx+b\,dy+c\,dz$（対応するベクトルを $\mathbf V=(a,b,c)$ とする）に $d$ を適用します：

$$
d\omega = da\wedge dx+db\wedge dy+dc\wedge dz
$$

$da=\partial_xa\,dx+\partial_ya\,dy+\partial_za\,dz$ なので、$da\wedge dx=\partial_ya\,dy\wedge dx+\partial_za\,dz\wedge dx=-\partial_ya\,dx\wedge dy+\partial_za\,dz\wedge dx$。同様に $db\wedge dy,\ dc\wedge dz$ を計算し、$dx\wedge dy$、$dy\wedge dz$、$dz\wedge dx$ の係数ごとに集めます：

$$
d\omega = (\partial_yc-\partial_zb)\,dy\wedge dz + (\partial_za-\partial_xc)\,dz\wedge dx + (\partial_xb-\partial_ya)\,dx\wedge dy
$$

係数を並べると $(\partial_yc-\partial_zb,\ \partial_za-\partial_xc,\ \partial_xb-\partial_ya)$、これは**$\operatorname{rot}\mathbf V$の定義そのもの**です。

$$
\boxed{d\omega \ \longleftrightarrow\ \operatorname{rot}\mathbf V}
$$

## 3. $d(2\text{-形式}) \leftrightarrow \operatorname{div}$

$\omega=p\,dy\wedge dz+q\,dz\wedge dx+r\,dx\wedge dy$（対応するベクトル $\mathbf W=(p,q,r)$）に $d$ を適用します：

$$
d\omega = dp\wedge dy\wedge dz+dq\wedge dz\wedge dx+dr\wedge dx\wedge dy
$$

$dp\wedge dy\wedge dz$では、$dp$の中の$dy,dz$成分は$dy\wedge dy=0$等で消え、$\partial_xp\,dx\wedge dy\wedge dz$だけが残ります。同様に他の2項も整理すると：

$$
d\omega = (\partial_xp+\partial_yq+\partial_zr)\,dx\wedge dy\wedge dz
$$

係数 $\partial_xp+\partial_yq+\partial_zr$ は、**$\operatorname{div}\mathbf W$の定義そのもの**です。

$$
\boxed{d\omega \ \longleftrightarrow\ \operatorname{div}\mathbf W}
$$

## まとめ表

| 形式の次数 | $d$を適用すると | ベクトル解析での意味 |
|---|---|---|
| 0-形式（関数） | 1-形式 | $\operatorname{grad}$ |
| 1-形式 | 2-形式 | $\operatorname{rot}$ |
| 2-形式 | 3-形式 | $\operatorname{div}$ |

$$
\boxed{\operatorname{grad},\ \operatorname{rot},\ \operatorname{div}\ \text{はすべて、同じ演算子}d\text{の、次数の違う適用先にすぎない}}
$$

---

# Part IV：ポアンカレの補題 $d^2=0$ ―2つの有名な恒等式の正体

外微分には、次数を問わず常に成り立つ、非常に重要な性質があります：

$$
\boxed{d(d\omega) = 0}\qquad\text{（ポアンカレの補題）}
$$

**なぜ成り立つのか**：$d^2f=\partial_j\partial_if\,dx^j\wedge dx^i$ を考えると、$\partial_j\partial_if$（偏微分の順序を入れ替えても同じ、対称）と $dx^j\wedge dx^i=-dx^i\wedge dx^j$（反対称）という、**対称なものと反対称なものを掛け合わせて和を取ると、必ずゼロになる**という一般的な代数の事実から従います（以前のラプラシアン導出で使った混合偏微分の対称性 $\partial_i\partial_j=\partial_j\partial_i$ が、ここでも本質的な役割を果たしています）。

この$d^2=0$を、Part IIIの対応表に当てはめると：

$$
d(df)=0 \ \longleftrightarrow\ \boxed{\operatorname{rot}(\operatorname{grad}f)=\mathbf 0}
$$

$$
d(d\omega)=0\ (\omega\text{が1-形式}) \ \longleftrightarrow\ \boxed{\operatorname{div}(\operatorname{rot}\mathbf V)=0}
$$

**この2つは、ベクトル解析の教科書でおなじみの「勾配の回転はゼロ」「回転の発散はゼロ」という公式そのものです。** これらが別々の偶然の一致ではなく、$d^2=0$というたった1つの一般的な事実の、次数違いの表れにすぎなかった、ということが分かります。

---

# Part V：Hodgeスター演算子 $\star$

外微分$d$だけでは、Part IIIの表の**片道**（0→1→2→3次元へと上げる方向）しか作れません。$\operatorname{div}$を$\operatorname{grad}$や$\operatorname{rot}$と同じ土俵で扱う（あるいは、逆に次数を下げる）には、もう1つの演算子**Hodgeスター**$\star$が必要です。

## 0. Hodgeスターの正式な定義（なぜ表の対応になるのか）

以下の表（$\star dx=dy\wedge dz$等）は、天下り的な対応ではなく、**次の式を満たす唯一の写像**として定義されます：

$$
\boxed{\beta\wedge\star\alpha = \langle\beta,\alpha\rangle\,\operatorname{vol}}\qquad(\text{任意の}k\text{-形式}\beta\text{について、}\alpha\text{も}k\text{-形式})
$$

（$\langle\cdot,\cdot\rangle$は計量から誘導される$k$-形式同士の内積、正規直交基底なら$\langle dx,dx\rangle=1,\langle dx,dy\rangle=0$等、$\operatorname{vol}:=dx\wedge dy\wedge dz$は体積要素。）

**実際に$\star dx$を導出してみます。** $\alpha=dx$として、任意の1-形式$\beta=\beta_1dx+\beta_2dy+\beta_3dz$に対して定義式の右辺を計算すると：

$$
\beta\wedge\star dx = \langle\beta,dx\rangle\,\operatorname{vol} = \beta_1\,dx\wedge dy\wedge dz
$$

（$\langle\beta,dx\rangle$は$\beta$の$dx$成分$\beta_1$を取り出す内積。）$\star dx=dy\wedge dz$を試しに代入して、この式が成り立つか確認します：

$$
\beta\wedge(dy\wedge dz) = (\beta_1dx+\beta_2dy+\beta_3dz)\wedge dy\wedge dz = \beta_1(dx\wedge dy\wedge dz)
$$

（$\beta_2dy\wedge dy\wedge dz=0$、$\beta_3dz\wedge dy\wedge dz=0$、$dy\wedge dy=dz\wedge dz=0$のため。）**一致しました。** つまり$\star dx=dy\wedge dz$は、定義式$\beta\wedge\star\alpha=\langle\beta,\alpha\rangle\operatorname{vol}$を満たす唯一の答えとして、計算で決まるものであり、語呂合わせや対称性からの当てはめではありません。$\star dy,\star dz,\star1$なども同じ手順で導出できます。

## 1. 3次元・平坦な計量での定義（上の定義から導かれる結果）

$\star$は$k$-形式を$(n-k)$-形式に変換します（$n$=空間の次元）。3次元では、基底同士を次のように対応させます：

$$
\star1 = dx\wedge dy\wedge dz,\qquad \star dx=dy\wedge dz,\quad\star dy=dz\wedge dx,\quad\star dz=dx\wedge dy
$$
$$
\star(dy\wedge dz)=dx,\quad\star(dz\wedge dx)=dy,\quad\star(dx\wedge dy)=dz,\qquad \star(dx\wedge dy\wedge dz)=1
$$

（規則：ある$k$個の基底を、残りの$(n-k)$個の基底に、全体として $dx\wedge dy\wedge dz$ になるよう「補完する」という操作です。）

## 2. 一般の計量が入った場合（以前のノートとの接続）

計量が $\delta_{ij}$（平坦・直交座標）でない一般の場合、Hodgeスターの定義には**$\sqrt{|g|}$と逆計量$g^{ij}$**が入り込みます：

$$
\boxed{(\star\alpha)_{j_1\cdots j_{n-k}} = \frac{\sqrt{|g|}}{k!}\,\varepsilon_{i_1\cdots i_kj_1\cdots j_{n-k}}\,g^{i_1l_1}\cdots g^{i_kl_k}\,\alpha_{l_1\cdots l_k}}
$$

**この$\sqrt{|g|}$こそ、以前のラプラス・ベルトラミ作用素のノートで「体積要素の伸縮を補正する量」として導出したものと、まったく同一の対象です。** つまり、Hodgeスター演算子は、「計量によって内積・体積要素を測る」という、これまでずっと扱ってきた話の**自然な延長**にすぎません。

**注**：$\flat,\sharp$（$g_{ij},g^{ij}$を使う、ベクトル⇔1-形式の変換）と、この$\star$（$k$-形式⇔$(n-k)$-形式の変換）は別の演算で、$\flat,\sharp$には$\sqrt{|g|}$は不要ですが、$\star$には必ず$\sqrt{|g|}$が入り込みます。実際に$\star dx$等を一般計量で導出する計算は、Part VII §2で行います。

## 3. $\mathbf a\times\mathbf b$ が「wedge積$+\star$」の結果であることの検証

以前の補足で「$\mathbf a\times\mathbf b$はwedge積を取ってからHodgeスターで戻した結果」と述べましたが、ここで実際に確認します。$\mathbf a=(a_1,a_2,a_3)$、$\mathbf b=(b_1,b_2,b_3)$ を1-形式に変換します（$\flat$操作、平坦な計量なので成分はそのまま）：

$$
\mathbf a^\flat = a_1dx+a_2dy+a_3dz,\qquad \mathbf b^\flat=b_1dx+b_2dy+b_3dz
$$

**ステップ1：wedge積を計算する**（Part I §6と同じ手順、反対称性 $dy\wedge dx=-dx\wedge dy$ 等を使って整理）：

$$
\mathbf a^\flat\wedge\mathbf b^\flat = (a_1b_2-a_2b_1)\,dx\wedge dy+(a_3b_1-a_1b_3)\,dz\wedge dx+(a_2b_3-a_3b_2)\,dy\wedge dz
$$

係数を見ると、$(\mathbf a\times\mathbf b)=(a_2b_3-a_3b_2,\ a_3b_1-a_1b_3,\ a_1b_2-a_2b_1)$ という外積の成分が、係数として現れています：

$$
\mathbf a^\flat\wedge\mathbf b^\flat = (\mathbf a\times\mathbf b)_1\,dy\wedge dz+(\mathbf a\times\mathbf b)_2\,dz\wedge dx+(\mathbf a\times\mathbf b)_3\,dx\wedge dy
$$

**この時点ではまだ「2-形式」であって「ベクトル」ではありません。**

**ステップ2：Hodgeスターを適用する**（本節1.の対応をそのまま使う）：

$$
\star\big(\mathbf a^\flat\wedge\mathbf b^\flat\big) = (\mathbf a\times\mathbf b)_1\,\star(dy\wedge dz)+(\mathbf a\times\mathbf b)_2\,\star(dz\wedge dx)+(\mathbf a\times\mathbf b)_3\,\star(dx\wedge dy)
$$

$$
= (\mathbf a\times\mathbf b)_1dx+(\mathbf a\times\mathbf b)_2dy+(\mathbf a\times\mathbf b)_3dz = (\mathbf a\times\mathbf b)^\flat
$$

**ちょうど、ベクトル$\mathbf a\times\mathbf b$を1-形式に変換したものと一致しました。** $\sharp$（$\flat$の逆操作）を両辺に適用すれば：

$$
\boxed{\mathbf a\times\mathbf b = \Big[\star\big(\mathbf a^\flat\wedge\mathbf b^\flat\big)\Big]^\sharp}
$$

$$
\boxed{
\begin{aligned}
&\text{①}\ \mathbf a,\mathbf b\ \xrightarrow{\ \flat\ }\ \mathbf a^\flat,\mathbf b^\flat\quad\text{（ベクトルを1-形式に変換）}\\
&\text{②}\ \xrightarrow{\ \wedge\ }\ \mathbf a^\flat\wedge\mathbf b^\flat\quad\text{（wedge積、係数に外積成分が現れるが、まだ2-形式）}\\
&\text{③}\ \xrightarrow{\ \star\ }\ (\mathbf a\times\mathbf b)^\flat\ \xrightarrow{\ \sharp\ }\ \mathbf a\times\mathbf b\quad\text{（Hodgeスターで1-形式に戻し、最後にベクトルに戻す）}
\end{aligned}
}
$$

---

# Part VI：grad, rot, div を $d,\star$ で統一的に書く

$1$-形式とベクトルを行き来する操作（**音楽同型**、"musical isomorphism"と呼ばれます）を導入します：ベクトル$\mathbf V=(V^1,V^2,V^3)$に対応する1-形式を $V^\flat:=g_{ij}V^idx^j$（添字を下げる）、1-形式$\omega=\omega_idx^i$に対応するベクトルを $\omega^\sharp:=g^{ij}\omega_j\,\partial_i$（添字を上げる）と定義します。これは以前の「計量による添字の上げ下げ」の議論そのものです。

## $\sharp$は何をしているのか（$\flat$の逆操作、平坦な座標では見えにくい理由）

$\flat$（ベクトル→1-形式）と$\sharp$（1-形式→ベクトル）は、それぞれ以前の資料の $v_i=g_{ij}v^j$（下げる）、$v^i=g^{ij}v_j$（上げる）と完全に同じ操作です。平坦な直交座標（$g_{ij}=\delta_{ij}$）では $V_i=\delta_{ij}V^j=V^i$ となり、**添字を上げても下げても数値が変わらない**ため、$\flat,\sharp$は「見た目上、何もしていない変換」に見えてしまいます。

**極座標のような非直交座標で確認すると、$\flat,\sharp$が実際に数値を変えていることが見えます。** 以前の計量 $g_{rr}=1,\ g_{\theta\theta}=r^2$ を使うと、ベクトル$V=(V^r,V^\theta)$を1-形式に変換した際：

$$
V^\flat = g_{rr}V^r\,dr+g_{\theta\theta}V^\theta\,d\theta = V^r\,dr+r^2V^\theta\,d\theta
$$

$\theta$成分に$r^2$が掛かり、数値が変わります。これを$\sharp$（逆計量$g^{rr}=1,\ g^{\theta\theta}=1/r^2$を使用）で戻すと：

$$
(V^\flat)^\sharp = g^{rr}(V^r)\,\partial_r+g^{\theta\theta}(r^2V^\theta)\,\partial_\theta = V^r\partial_r+\frac1{r^2}(r^2V^\theta)\partial_\theta = V^r\partial_r+V^\theta\partial_\theta = V
$$

**ちゃんと元のベクトルに戻ります。** $\sharp$は「$\flat$で下げた添字を、逆計量で元通りに上げ戻す」という、$\flat$の完全な逆操作であり、平坦な座標でだけ「何もしていないように見える」だけで、一般の座標では実際に仕事をしています。

これを使うと：

$$
\boxed{\operatorname{grad}f = (df)^\sharp}
$$

$$
\boxed{\operatorname{rot}\mathbf V = \big(\star\,d(V^\flat)\big)^\sharp}
$$

$$
\boxed{\operatorname{div}\mathbf V = \star\,d\,\star(V^\flat)}
$$

$\operatorname{grad},\operatorname{rot},\operatorname{div}$という一見バラバラな3つの演算子が、**「外微分$d$」と「Hodgeスター$\star$」という、たった2つの演算子の組み合わせだけ**で、過不足なく再現されます。

---

# Part VII：ラプラス・ベルトラミ作用素 $=\star d\star d$ ―最初のノートとの完全な接続

$\Delta f=\operatorname{div}(\operatorname{grad}f)$ でした。Part VIの結果を代入します：

$$
\Delta f = \operatorname{div}\big((df)^\sharp\big) = \star\,d\,\star\big((df)^\sharp\big)^\flat = \star\,d\,\star(df)
$$

（$\flat$と$\sharp$は互いに逆操作なので、$\big((df)^\sharp\big)^\flat=df$ に戻ります。）

$$
\boxed{\Delta f = \star\,d\,\star\,d\,f}
$$

**これが、微分幾何で「Hodgeラプラシアン」と呼ばれる、驚くほど簡潔な表式です。**

## 1. 成分展開の準備：一般計量での$\star dx$を定義式から導出する

Part V §0の定義式 $\beta\wedge\star\alpha=\langle\beta,\alpha\rangle\operatorname{vol}$ に戻って、一般の（対角）計量での$\star dx$を求めます。**注意点**：ここから先で使う$\star$は、$\flat,\sharp$（$g_{ij},g^{ij}$を使う、ベクトル⇔1-形式の変換）とは別の演算です。$\flat,\sharp$には$\sqrt{|g|}$は不要ですが、$\star$には必ず$\sqrt{|g|}$が入り込みます。

一般の対角計量では、体積要素は $\operatorname{vol}=\sqrt{|g|}\,dx\wedge dy\wedge dz$、内積は逆計量を使って $\langle dx,dx\rangle=g^{xx}$ です。$\alpha=\beta=dx$を定義式に代入すると：

$$
dx\wedge\star dx = g^{xx}\sqrt{|g|}\,dx\wedge dy\wedge dz
$$

$\star dx=C\,dy\wedge dz$と置いて代入すると$C=g^{xx}\sqrt{|g|}$と決まります：

$$
\boxed{\star dx = g^{xx}\sqrt{|g|}\,dy\wedge dz,\qquad \star dy=g^{yy}\sqrt{|g|}\,dz\wedge dx,\qquad\star dz=g^{zz}\sqrt{|g|}\,dx\wedge dy}
$$

（平坦なら$g^{xx}=1,\sqrt{|g|}=1$で、Part V §1の表に戻ります。）同様に、$\star1=\sqrt{|g|}\,dx\wedge dy\wedge dz$の逆演算として（$\star\star=1$、3次元ユークリッド符号での一般性質を使う）：

$$
\boxed{\star(dx\wedge dy\wedge dz) = \frac1{\sqrt{|g|}}}
$$

**$\dfrac1{\sqrt{|g|}}$がここに現れる**、という点が抜けやすいポイントです。

## 2. $\star d\star df$ を実際に最後まで計算する

$$
\star df = g^{xx}\sqrt{|g|}\,\partial_xf\,dy\wedge dz+g^{yy}\sqrt{|g|}\,\partial_yf\,dz\wedge dx+g^{zz}\sqrt{|g|}\,\partial_zf\,dx\wedge dy
$$

各項に$d$をかけ（Part IIIと同じ手順で、生き残る成分だけを拾う）：

$$
d(\star df) = \Big[\partial_x\big(g^{xx}\sqrt{|g|}\partial_xf\big)+\partial_y\big(g^{yy}\sqrt{|g|}\partial_yf\big)+\partial_z\big(g^{zz}\sqrt{|g|}\partial_zf\big)\Big]dx\wedge dy\wedge dz
$$

最後に§1で導出した $\star(dx\wedge dy\wedge dz)=1/\sqrt{|g|}$ を掛けると：

$$
\star d\star df = \frac1{\sqrt{|g|}}\Big[\partial_x\big(g^{xx}\sqrt{|g|}\partial_xf\big)+\partial_y\big(g^{yy}\sqrt{|g|}\partial_yf\big)+\partial_z\big(g^{zz}\sqrt{|g|}\partial_zf\big)\Big]
$$

$$
\boxed{\star\,d\,\star\,d\,f = \frac1{\sqrt{|g|}}\partial_i\Big(\sqrt{|g|}\,g^{ij}\partial_jf\Big)}
$$

**これは、最初のノートで、球座標の基底ベクトルから始めて何時間もかけて導出したラプラス・ベルトラミ作用素の公式と、寸分違わず一致します。** あのとき「なぜ$\sqrt{|g|}$が必要なのか」を、ヤコビ行列・体積要素の伸縮という言葉で一生懸命説明しましたが、微分形式の言語では、それは**Hodgeスター演算子の定義の中に、最初から織り込まれている**、ということになります。

---

# Part VIII：4次元・電磁気学・一般相対論への接続

## 1. 電磁場を2-形式として書く

電場 $\mathbf E$、磁場 $\mathbf B$ を、時空（4次元、座標 $t,x,y,z$）上の1つの2-形式 $F$ にまとめます：

$$
F = E_x\,dt\wedge dx+E_y\,dt\wedge dy+E_z\,dt\wedge dz + B_x\,dy\wedge dz+B_y\,dz\wedge dx+B_z\,dx\wedge dy
$$

## 2. マクスウェル方程式が2本の式にまとまる

$$
\boxed{dF=0}\qquad\text{（}\operatorname{div}\mathbf B=0\text{ と ファラデーの法則をまとめたもの）}
$$

$$
\boxed{d\star F = J}\qquad\text{（}\operatorname{div}\mathbf E=\rho\text{ と アンペール・マクスウェルの法則をまとめたもの）}
$$

（$J$は電流密度を表す3-形式。）**4本あったマクスウェル方程式が、$d$と$\star$を使うと、たった2本の式になります。** $dF=0$はPart IVのポアンカレの補題と同じ構造（$F=dA$と書けるポテンシャル$A$が存在すれば自動的に成立）、$d\star F=J$の方はPart VIIの$\operatorname{div}$の一般化そのものです。

## 3. 一般相対論への一般化

曲がった時空（クリストッフェル記号・リーマン曲率の話が関わる場）でも、$dF=0$、$d\star F=J$という**形はまったく変わりません**。変わるのは、$\star$の定義の中の計量 $g_{\mu\nu}$（時空の計量、以前扱った$g_{ij}$の4次元・ローレンツ符号版）だけです。これが、$\nabla_\mu F^{\mu\nu}=J^\nu$（共変微分を使った、教科書でよく見る形）という式の、微分形式での言い方になります。

---

# まとめ：全体の統一図

```
微分形式 d(0-形式)=1-形式 → grad
         d(1-形式)=2-形式 → rot
         d(2-形式)=3-形式 → div
                │
                ▼
         d² = 0 （ポアンカレの補題）
                │
         ├─ d(df)=0        ↔ rot(grad f)=0
         └─ d(dω)=0        ↔ div(rot V)=0
                │
Hodgeスター ⋆：計量 g、√|g| を使って次数を反転（以前のノートの√|g|と同一物）
                │
grad V = (df)^♯,  rot V = (⋆dV^♭)^♯,  div V = ⋆d⋆V^♭
                │
                ▼
      Δf = ⋆d⋆df = (1/√|g|)∂_i(√|g| g^{ij}∂_j f)
      （最初のラプラス・ベルトラミ作用素のノートと完全に一致）
                │
                ▼
4次元・電磁気学：F=2-形式、dF=0、d⋆F=J（マクスウェル方程式）
                │
                ▼
一般相対論：計量を曲がった時空のものに変えるだけで、同じ式がそのまま成り立つ
```

---

# 結び

今回の内容は、これまでのノート全部の**総集編**になっています。

- 計量テンソル $g_{ij}$、基底ベクトルの内積（最初のノート）
- $\sqrt{|g|}$、体積要素の伸縮（ラプラス・ベルトラミ作用素のノート）
- クリストッフェル記号、共変微分（曲率のノート）
- $\varepsilon_{ijk}$、完全反対称性（パウリ行列・div/grad/rotのノート）

これらすべてが、**「微分形式」というたった1つの枠組みの中に、部品として組み込まれていた**ことが、今回で見えてきました。div, grad, rotという、最初は別々の公式に見えていたものが、外微分$d$という同じ演算子の異なる次数への適用にすぎず、$\sqrt{|g|}$という以前散々扱った量が、Hodgeスター演算子$\star$の定義そのものだった、というのが、この一連の学習全体を貫く、一番大きな発見だったと思います。
