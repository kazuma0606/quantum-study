"""添字の読み方を「見える化」する図（図10〜図13）を生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/02_微分幾何/figures/make_index_figures.py

出力（figures/）:
    fig10_free_dummy_rename.png   自由添字・ダミー添字・付け替えの衝突・一斉付け替え
    fig11_delta_cards.png         計量×逆計量＝δ、δ による添字のすり替え、添字の上げ下げ
    fig12_christoffel_indices.png クリストッフェル記号の添字の意味と、公式の添字の対応
    fig13_riemann_indices.png     リーマン曲率テンソルの添字の意味と、添字の帳簿チェック

色の約束：添字の文字ごとに固定色（i=青, j=緑, k=赤, l=紫, m=橙, n=茶）。
色付きの文字＝自由添字、色付きの囲み＝ダミー添字（上下でペアになって和を取る）。
組版の部品は index_typeset.py にある。式は christoffel_riemann_intro.md の本文と同じ形。
"""

from index_typeset import C, D, F, Ix, LETTER, Canvas, Sym, Txt

CI, CJ, CK, CL, CM, CN = (LETTER[c] for c in "ijklmn")
GRAY = "#444444"
RED = "#d62728"
GREEN = "#2a8a2a"


def m(s, col):
    """rich() 用: mathtext の断片"""
    return (s, col, "m")


def riemann(cv, x, y, mp, size=30, isize=21):
    """リーマン曲率テンソルの公式（Part VII §2）を描く。

    R^l_{kij} = ∂_i Γ^l_{jk} − ∂_j Γ^l_{ik} + Γ^l_{im} Γ^m_{jk} − Γ^l_{jm} Γ^m_{ik}
    mp: 役割 (l,k,i,j) → 実際に書く文字。色は文字ではなく役割についてくる。
    ダミー添字 m のペアには、タグ t3, t4 を付ける。
    """
    def I(role, kind="free", tag=None):
        return Ix(mp[role], kind, color=LETTER[role], tag=tag)

    return cv.formula(x, y, [
        Sym("R", up=[I("l")], down=[I("k"), I("i"), I("j")]), Txt("="),
        Sym(r"\partial", down=[I("i")]), Sym(r"\Gamma", up=[I("l")], down=[I("j"), I("k")]), Txt("-"),
        Sym(r"\partial", down=[I("j")]), Sym(r"\Gamma", up=[I("l")], down=[I("i"), I("k")]), Txt("+"),
        Sym(r"\Gamma", up=[I("l")], down=[I("i"), D("m", "t3")]),
        Sym(r"\Gamma", up=[D("m", "t3")], down=[I("j"), I("k")]), Txt("-"),
        Sym(r"\Gamma", up=[I("l")], down=[I("j"), D("m", "t4")]),
        Sym(r"\Gamma", up=[D("m", "t4")], down=[I("i"), I("k")]),
    ], size=size, isize=isize)


def fig10():
    cv = Canvas(1500, 1960)

    # ------------------------------------------------ ① 自由添字とダミー添字
    cv.card(30, 1920, 1440, 610, "① 自由添字とダミー添字")
    cv.rich(700, 1897, [("色つき文字", CK), ("＝自由添字　", GRAY), ("囲み", CI), ("＝ダミー添字（和を取る）", GRAY)],
            size=14, va="top")
    A = cv.formula(100, 1740, [
        Sym(r"\nabla", down=[F("j")]), Sym("V", up=[F("k")]), Txt("="),
        Sym(r"\partial", down=[F("j")]), Sym("V", up=[F("k")]), Txt("+"),
        Sym(r"\Gamma", up=[F("k")], down=[D("i", "G"), F("j")]), Sym("V", up=[D("i", "G")]),
    ], size=42, isize=28)
    js = [a for a in A["_all"] if a["letter"] == "j"]
    ks = [a for a in A["_all"] if a["letter"] == "k"]
    cv.guide(js[0], js[1], "bot", 0.5)
    cv.guide(js[1], js[2], "bot", 0.35)
    cv.guide(ks[0], ks[1], "top", 0.5)
    cv.guide(ks[1], ks[2], "top", 0.32)
    cv.link(A, "G", rad=0.5)
    y = 1600
    cv.rich(60, y, [("自由添字 ", GRAY), m("j", CJ), (" ", GRAY), m("k", CK),
                    ("：どの項にも、同じ位置（", GRAY), m("j", CJ), ("は下、", GRAY), m("k", CK),
                    ("は上）に1個ずつ現れる。外から値を指定する添字。", GRAY)], size=15)
    cv.rich(60, y - 40, [("ダミー添字 ", GRAY), m("i", CI),
                         ("：同じ項の中に、上（", GRAY), m(r"V^i", CI), ("の ", GRAY), m("i", CI), ("）と下（", GRAY),
                         m(r"\Gamma", GRAY), ("の下1番目の ", GRAY), m("i", CI),
                         ("）で1個ずつ → 1,2,3 について和（縮約）。", GRAY)], size=15)
    cv.rich(60, y - 100, [("付け替えても同じ式（ダミー添字は、どの文字で書いてもよい）：", GRAY)], size=15)
    B = cv.formula(100, y - 190, [
        Sym(r"\nabla", down=[F("j")]), Sym("V", up=[F("k")]), Txt("="),
        Sym(r"\partial", down=[F("j")]), Sym("V", up=[F("k")]), Txt("+"),
        Sym(r"\Gamma", up=[F("k")], down=[D("m", "G"), F("j")]), Sym("V", up=[D("m", "G")]),
    ], size=42, isize=28)
    cv.link(B, "G", rad=0.5)
    cv.rich(B["_end"] + 40, y - 190, [m("i", CI), (" → ", GRAY), m("m", CM), ("  に付け替え", GRAY)], size=17)

    # ------------------------------------------------ ② 付け替えで衝突させない
    cv.card(30, 1280, 1440, 500, "② 付け替えで衝突させない（付録B の例）")
    cv.rich(60, 1200, [m(r"T^m{}_j", GRAY), (" を、", GRAY), m(r"T^m{}_j:=\nabla_jV^m", GRAY),
                       (" として書き下したい。外側の ", GRAY), m("m", CM), (" は自由添字。", GRAY)], size=15, va="top")
    cv.badge(80, 1075, "×", RED)
    N = cv.formula(130, 1060, [
        Sym("T", up=[F("m")], down=[F("j")]), Txt("="),
        Sym(r"\partial", down=[F("j")]), Sym("V", up=[F("m")]), Txt("+"),
        Sym(r"\Gamma", up=[F("m")], down=[C("m", "x"), F("j")]), Sym("V", up=[C("m", "x")]),
    ], size=40, isize=27)
    ms = [a for a in N["_all"] if a["kind"] == "clash"]
    cv.callout(ms[0], "外側の m と同じ文字になり、\nどの m がどれか区別できない（m が5回）",
               (ms[0]["cx"] + 330, 1085), color=RED, size=14.5, ha="left")
    cv.badge(80, 915, "○", GREEN)
    O = cv.formula(130, 900, [
        Sym("T", up=[F("m")], down=[F("j")]), Txt("="),
        Sym(r"\partial", down=[F("j")]), Sym("V", up=[F("m")]), Txt("+"),
        Sym(r"\Gamma", up=[F("m")], down=[D("n", "n"), F("j")]), Sym("V", up=[D("n", "n")]),
    ], size=40, isize=27)
    cv.link(O, "n", rad=0.5)
    ns = O["n"][0]
    cv.callout(ns, "内側のダミー添字だけを、まだ使っていない文字 n に付け替える",
               (ns["cx"] + 330, 925), color=CN, size=14.5, ha="left")

    # ------------------------------------------------ ③ 一斉に付け替える
    cv.card(30, 750, 1440, 655, "③ 添字を一斉に付け替える（リーマン曲率テンソルの公式、Part VII §2）")

    ident = dict(l="l", k="k", i="i", j="j")
    swap = dict(l="q", k="p", i="j", j="i")
    cv.rich(60, 660, [("元の式", GRAY)], size=15)
    R0 = riemann(cv, 60, 610, ident)
    cv.link(R0, "t3", 0.5)
    cv.link(R0, "t4", 0.5)
    cv.rich(60, 535, [("付け替え：", GRAY), m("l", CL), ("→", GRAY), m("q", CL), ("　", GRAY),
                      m("k", CK), ("→", GRAY), m("p", CK), ("　", GRAY),
                      m("i", CI), ("→", GRAY), m("j", CI), ("　", GRAY),
                      m("j", CJ), ("→", GRAY), m("i", CJ), ("　（", GRAY), m("i", CI), ("と", GRAY), m("j", CJ),
                      ("は入れ替わり）", GRAY)], size=16)
    R1 = riemann(cv, 60, 470, swap)
    cv.link(R1, "t3", 0.5)
    cv.link(R1, "t4", 0.5)
    cv.rich(60, 405, [("色は「役割」についてくる：", GRAY), ("i", CI, "m"), ("だった位置（青）に文字 ", GRAY), m("j", CI),
                      (" が入り、", GRAY), ("j", CJ, "m"), ("だった位置（緑）に文字 ", GRAY), m("i", CJ), (" が入る。", GRAY)], size=15)

    cv.badge(80, 320, "×", RED)
    cv.rich(120, 310, [("順番に置き換えると失敗する（", RED), ("i", CI, "m"), ("→", RED), ("j", CJ, "m"), ("、次に ", RED),
                       ("j", CJ, "m"), ("→", RED), ("i", CI, "m"), ("）", RED)], size=15)
    yy = 230
    st = 32
    S0 = cv.formula(120, yy, [Sym(r"\partial", down=[F("i")]), Sym(r"\Gamma", up=[F("l")], down=[F("j"), F("k")])],
                    size=st, isize=22)
    cv.arrow((S0["_end"] + 10, yy + 12), (S0["_end"] + 120, yy + 12), GRAY)
    cv.rich(S0["_end"] + 22, yy + 40, [m(r"i\to j", GRAY)], size=15)
    S1 = cv.formula(S0["_end"] + 140, yy, [Sym(r"\partial", down=[F("j")]), Sym(r"\Gamma", up=[F("l")], down=[F("j"), F("k")])],
                    size=st, isize=22)
    cv.arrow((S1["_end"] + 10, yy + 12), (S1["_end"] + 120, yy + 12), GRAY)
    cv.rich(S1["_end"] + 22, yy + 40, [m(r"j\to i", GRAY)], size=15)
    S2 = cv.formula(S1["_end"] + 140, yy, [Sym(r"\partial", down=[F("i")]), Sym(r"\Gamma", up=[F("l")], down=[F("i"), F("k")])],
                    size=st, isize=22)
    cv.rich(S2["_end"] + 20, yy, [("← 微分の添字と ", RED), m(r"\Gamma", RED), (" の添字が同じ i になってしまう", RED)], size=15)
    cv.rich(120, 150, [("正しくは一斉に付け替えて ", GRAY), m(r"\partial_j\Gamma^l{}_{ik}", GRAY),
                       ("。または一時的な文字を経由する：", GRAY), m(r"i\to t,\ j\to i,\ t\to j", GRAY)], size=15)

    cv.save("fig10_free_dummy_rename.png")


YELLOW = "#fff0a0"


def by_pos(A, letter, place):
    """式の中の、指定した文字・位置（"up"/"down"）の添字を、左から順に返す"""
    return [a for a in A["_all"] if a["letter"] == letter and a["place"] == place]


def fig11():
    """δ のカード：計量×逆計量、添字のすり替え、上げ下げ、AJ=I"""
    cv = Canvas(1500, 1820)
    EC = "#3b6fb6"

    # ------------------------------------------------ ① 計量 × 逆計量 = δ
    cv.card(30, 1780, 1440, 440, "① 計量 × 逆計量 ＝ δ　（和で消えた k のかわりに、残った i と j が δ の添字になる）", ec=EC, lw=3.4)
    A = cv.formula(190, 1560, [
        Sym("g", up=[F("i"), D("k", "a")]), Sym("g", down=[D("k", "a"), F("j")]), Txt("=", pad=30),
        Sym(r"\delta", up=[F("i")], down=[F("j")], mark=YELLOW),
    ], size=62, isize=42)
    cv.link(A, "a", rad=0.55)
    gi, di = by_pos(A, "i", "up")
    gj, dj = by_pos(A, "j", "down")
    cv.arrow((gi["cx"], gi["top"] + 6), (di["cx"], di["top"] + 6), CI, lw=2.6, rad=-0.22)
    cv.arrow((gj["cx"], gj["bot"] - 6), (dj["cx"], dj["bot"] - 6), CJ, lw=2.6, rad=0.22)
    cv.rich(700, 1580, [("g", GRAY, "m"), (" の各成分を並べた行列と、その逆行列の積が単位行列", GRAY)], size=15)
    cv.rich(60, 1415, [("k", CK, "m"), ("：上（", GRAY), ("g^{ik}", GRAY, "m"), ("）と下（", GRAY), ("g_{kj}", GRAY, "m"),
                       ("）でペア → 1,2,3 について和を取って消える。", GRAY)], size=15)
    cv.rich(60, 1375, [("i, j", CI, "m"), ("：そのまま引き継がれ、", GRAY), (r"\delta^i{}_j", GRAY, "m"),
                       ("の上・下の添字になる。値は ", GRAY), (r"\delta^i{}_j=1\ (i=j),\ 0\ (i\neq j)", GRAY, "m"), ("。", GRAY)], size=15)

    # ------------------------------------------------ ② δ は添字のすり替え
    cv.card(30, 1310, 1440, 430, "② δ は「添字のすり替え」：j = i の項だけが生き残る", ec=EC, lw=3.4)
    a = cv.formula(90, 1120, [
        Sym(r"\delta", up=[F("i")], down=[D("j", "p")], mark=YELLOW), Sym("V", up=[D("j", "p")]), Txt("=", pad=24),
        Sym("V", up=[F("i")]),
    ], size=50, isize=34)
    cv.link(a, "p", rad=0.5)
    i1, i2 = by_pos(a, "i", "up")
    cv.arrow((i1["cx"], i1["top"] + 6), (i2["cx"], i2["top"] + 6), CI, lw=2.6, rad=-0.25)
    cv.rich(90, 1010, [("上付きの ", GRAY), m("j", CJ), (" が ", GRAY), m("i", CI), (" にすり替わる", GRAY)], size=15)
    b = cv.formula(820, 1120, [
        Sym(r"\delta", up=[D("i", "s")], down=[F("j")], mark=YELLOW), Sym("V", down=[D("i", "s")]),
        Txt("=", pad=24), Sym("V", down=[F("j")]),
    ], size=50, isize=34)
    cv.link(b, "s", rad=0.5)
    j1, j2 = by_pos(b, "j", "down")
    cv.arrow((j1["cx"], j1["bot"] - 6), (j2["cx"], j2["bot"] - 6), CJ, lw=2.6, rad=0.25)
    cv.rich(820, 1010, [("下付きの ", GRAY), m("i", CI), (" が ", GRAY), m("j", CJ), (" にすり替わる", GRAY)], size=15)
    cv.rich(60, 940, [(r"\sum_j\delta^i{}_jV^j=\delta^i{}_1V^1+\delta^i{}_2V^2+\delta^i{}_3V^3=V^i", GRAY, "m"),
                      ("　（", GRAY), (r"\delta^i{}_j", GRAY, "m"), ("は ", GRAY), m("j=i", GRAY),
                      (" の項だけ 1、他は 0 なので、その項だけが残る）", GRAY)], size=15)

    # ------------------------------------------------ ③ 添字の上げ下げ
    cv.card(30, 850, 1440, 300, "③ 添字の上げ下げも同じ仕組み（計量が δ を作り、添字を付け替える）", ec=EC, lw=3.4)
    c = cv.formula(70, 720, [
        Sym("g", up=[F("i"), D("j", "a")]), Sym("V", down=[D("j", "a")]), Txt("=", pad=16),
        Sym("g", up=[F("i"), D("j", "b")]), Sym("g", down=[D("j", "b"), D("k", "c")]), Sym("V", up=[D("k", "c")]),
        Txt("=", pad=16),
        Sym(r"\delta", up=[F("i")], down=[D("k", "d")], mark=YELLOW), Sym("V", up=[D("k", "d")]), Txt("=", pad=16),
        Sym("V", up=[F("i")]),
    ], size=40, isize=27)
    for tg in ("a", "b", "c", "d"):
        cv.link(c, tg, rad=0.5)
    cv.rich(60, 640, [(r"V_j=g_{jk}V^k", GRAY, "m"), ("（下げた形）を代入 → ", GRAY),
                      (r"g^{ij}g_{jk}=\delta^i{}_k", GRAY, "m"), (" で ", GRAY), m("j", CJ),
                      (" が消え → ", GRAY), (r"\delta^i{}_kV^k=V^i", GRAY, "m"), (" で ", GRAY), m("k", CK),
                      (" が ", GRAY), m("i", CI), (" にすり替わる。", GRAY)], size=15)
    cv.rich(60, 600, [("同様に ", GRAY), (r"g_{ij}V^j=V_i", GRAY, "m"), ("（下げる）。上げ下げは、計量が δ を作って添字を付け替える操作です。", GRAY)],
            size=15)

    # ------------------------------------------------ ④ AJ = I（Part III §1）
    cv.card(30, 520, 1440, 470, "④ 行列の積 AJ = I も同じ仕組み（Part III §1 で Γ の添字 k を k′ にすり替えた操作）", ec=EC, lw=3.4)
    KP = "#e0607e"
    d = cv.formula(90, 385, [
        Sym("A", up=[F("k")], down=[D("a", "u")]), Sym("J", up=[D("a", "u")], down=[F("i")]), Txt("=", pad=24),
        Sym(r"\delta", up=[F("k")], down=[F("i")], mark=YELLOW),
    ], size=46, isize=31)
    cv.link(d, "u", rad=0.5)
    cv.rich(560, 385, [("行列の積 ", GRAY), (r"(AJ)^k{}_i=\sum_aA^k{}_aJ^a{}_i", GRAY, "m"),
                       (" の ", GRAY), m("a", "#c2185b"), (" が和で消え、行 ", GRAY), m("k", CK), (" と列 ", GRAY), m("i", CI),
                       (" が残る", GRAY)], size=15)
    e = cv.formula(90, 250, [
        Sym("A", up=[F("k'", color=KP)], down=[D("a", "x")]), Sym("J", up=[D("a", "x")], down=[D("k", "y")]),
        Sym(r"\Gamma", up=[D("k", "y")], down=[F("i"), F("j")]), Txt("=", pad=20),
        Sym(r"\delta", up=[F("k'", color=KP)], down=[D("k", "z")], mark=YELLOW),
        Sym(r"\Gamma", up=[D("k", "z")], down=[F("i"), F("j")]), Txt("=", pad=20),
        Sym(r"\Gamma", up=[F("k'", color=KP)], down=[F("i"), F("j")]),
    ], size=46, isize=31)
    for tg in ("x", "y", "z"):
        cv.link(e, tg, rad=0.5)
    kps = by_pos(e, "k'", "up")
    cv.arrow((kps[1]["cx"], kps[1]["top"] + 6), (kps[2]["cx"], kps[2]["top"] + 6), KP, lw=2.6, rad=-0.3)
    cv.rich(60, 120, [("δ が ", GRAY), m("k", CK), (" を ", GRAY), m("k'", KP),
                      (" にすり替える：Γ の上付き添字が、A の行番号 k′ に置き換わる。", GRAY)], size=15)

    cv.save("fig11_delta_cards.png")


def fig12():
    """クリストッフェル記号の添字の意味と、公式の添字の対応"""
    cv = Canvas(1500, 1760)
    EC = "#3b6fb6"

    # ------------------------------------------------ ① Γ^k_ij の 3 つの席
    cv.card(30, 1720, 1440, 610, "① 添字の意味：Γ の3つの添字（k, i, j）の席", ec=EC)
    A = cv.formula(230, 1470, [
        Sym(r"\partial", down=[F("j")]), Sym(r"\mathbf{e}", down=[F("i")]), Txt("=", pad=26),
        Sym(r"\Gamma", up=[D("k", "a")], down=[F("i"), F("j")], mark=YELLOW),
        Sym(r"\mathbf{e}", down=[D("k", "a")]),
    ], size=56, isize=38)
    cv.link(A, "a", rad=0.5)
    gk = by_pos(A, "k", "up")[0]
    gi = by_pos(A, "i", "down")[1]
    gj = by_pos(A, "j", "down")[1]
    cv.callout(gk, r"$k$（上）：結果として出てくる基底 $\mathbf{e}_k$" + "\n" + "（新しい基底のうち、どの向きの成分か）",
               (gk["cx"] + 60, 1620), color=CK, anchor="top", size=15, ha="left")
    cv.callout(gi, r"$i$（下・1番目）：微分される基底 $\mathbf{e}_i$", (gi["cx"] - 30, 1350), color=CI, size=15, ha="right")
    cv.callout(gj, r"$j$（下・2番目）：動く方向 $q^j$" + "\n" + r"（$\partial_j=\partial/\partial q^j$）",
               (gj["cx"] + 60, 1350), color=CJ, size=15, ha="left")
    cv.rich(60, 1205, [(r"\partial_j\mathbf{e}_i", GRAY, "m"), (" は 1 本のベクトル → 基底 ", GRAY), (r"\mathbf{e}_k", GRAY, "m"),
                       (" で展開した係数が ", GRAY), (r"\Gamma^k{}_{ij}", GRAY, "m"), (" 。", GRAY)], size=15)
    cv.rich(60, 1165, [("下の2つは入れ替えても同じ：", GRAY), (r"\Gamma^k{}_{ij}=\Gamma^k{}_{ji}", GRAY, "m"),
                       ("（", GRAY), (r"\partial_j\mathbf{e}_i=\partial_i\mathbf{e}_j", GRAY, "m"), ("、混合偏微分の対称性）。", GRAY)], size=15)

    # ------------------------------------------------ ② 公式の添字の行き先
    cv.card(30, 1080, 1440, 400, "② 公式の添字の行き先：ダミー添字 l は3か所でペアになる（Part II）", ec=EC)
    B = cv.formula(70, 900, [
        Sym(r"\Gamma", up=[F("k")], down=[F("i"), F("j")]), Txt("=", pad=14), Txt(r"\frac{1}{2}", pad=10),
        Sym("g", up=[F("k"), D("l", "L")]), Txt("(", pad=4),
        Sym(r"\partial", down=[F("i")]), Sym("g", down=[F("j"), D("l", "L")]), Txt("+", pad=14),
        Sym(r"\partial", down=[F("j")]), Sym("g", down=[F("i"), D("l", "L")]), Txt("-", pad=14),
        Sym(r"\partial", down=[D("l", "L")]), Sym("g", down=[F("i"), F("j")]), Txt(")", pad=4),
    ], size=42, isize=29)
    ls = [a for a in B["_all"] if a["letter"] == "l"]
    for other in ls[1:]:
        cv.bridge(ls[0], other, rad=-0.28 if other is ls[-1] else 0.3, lw=5)
    cv.rich(60, 800, [("自由添字 ", GRAY), m("k", CK), ("（上）、", GRAY), m("i, j", CI),
                      ("（下）：どの項でも左辺と同じ位置に現れる（", GRAY), m(r"k", CK), (" は ", GRAY), m(r"g^{kl}", GRAY),
                      (" の上、", GRAY), m("i, j", CI), (" は ", GRAY), (r"\partial", GRAY, "m"), (" と ", GRAY), m("g", GRAY),
                      (" の下）。", GRAY)], size=15)
    cv.rich(60, 760, [("ダミー添字 ", GRAY), m("l", CL), ("：", GRAY), (r"g^{kl}", GRAY, "m"), (" の上の ", GRAY), m("l", CL),
                      (" が、括弧の中の3か所の下の ", GRAY), m("l", CL), (" とペアになり、和を取る。", GRAY)], size=15)
    cv.rich(60, 720, [("括弧の中は、3つの添字 ", GRAY), m("i, j, l", GRAY), (" を巡回させた形（", GRAY),
                      (r"\partial_ig_{jl}+\partial_jg_{il}-\partial_lg_{ij}", GRAY, "m"), ("）。", GRAY)], size=15)

    # ------------------------------------------------ ③ 反変と共変
    cv.card(30, 640, 1440, 525, "③ 反変と共変：Γ の中で i と k の入る場所が入れ替わる（Part IV §1）", ec=EC)
    R1 = cv.formula(90, 470, [
        Sym(r"\nabla", down=[F("j")]), Sym("V", up=[F("k")]), Txt("="),
        Sym(r"\partial", down=[F("j")]), Sym("V", up=[F("k")]), Txt("+"),
        Sym(r"\Gamma", up=[F("k")], down=[D("i", "r1"), F("j")]), Sym("V", up=[D("i", "r1")]),
    ], size=44, isize=30)
    cv.link(R1, "r1", rad=0.5)
    cv.rich(80, 385, [("反変（上付き）", CK), ("：結果の添字 ", GRAY), m("k", CK), (" は Γ の上、ダミーの ", GRAY), m("i", CI),
                      (" は Γ の下（", GRAY), m(r"V^i", CI), (" と縮約）。符号は ＋", GRAY)], size=15)
    R2 = cv.formula(90, 290, [
        Sym(r"\nabla", down=[F("j")]), Sym("V", down=[F("k")]), Txt("="),
        Sym(r"\partial", down=[F("j")]), Sym("V", down=[F("k")]), Txt("-"),
        Sym(r"\Gamma", up=[D("i", "r2")], down=[F("k"), F("j")]), Sym("V", down=[D("i", "r2")]),
    ], size=44, isize=30)
    cv.link(R2, "r2", rad=-0.5)
    cv.rich(80, 205, [("共変（下付き）", CK), ("：結果の添字 ", GRAY), m("k", CK), (" は Γ の下、ダミーの ", GRAY), m("i", CI),
                      (" は Γ の上（", GRAY), m(r"V_i", CI), (" と縮約）。符号は −", GRAY)], size=15)
    cv.rich(80, 150, [("どちらも「ダミー添字は Γ と V で上下がペア」「自由添字 ", GRAY), m("j, k", CK),
                      (" は全項で同じ位置」という規則を満たしている。", GRAY)], size=15)

    cv.save("fig12_christoffel_indices.png")


def fig13():
    """リーマン曲率テンソルの添字の意味と、添字の帳簿チェック"""
    cv = Canvas(1500, 1780)
    EC = "#3b6fb6"

    # ------------------------------------------------ ① R^l_kij の意味
    cv.card(30, 1740, 1440, 560, "① 添字の意味：曲率テンソルは、V の成分 k を、成分 l のずれに写す行列", ec=EC)
    A = cv.formula(90, 1520, [
        Txt("(", pad=4), Sym(r"\nabla", down=[F("i")]), Sym(r"\nabla", down=[F("j")]), Txt("-", pad=14),
        Sym(r"\nabla", down=[F("j")]), Sym(r"\nabla", down=[F("i")]), Txt(")", pad=8),
        Sym("V", up=[F("l")]), Txt("=", pad=24),
        Sym("R", up=[F("l")], down=[D("k", "a"), F("i"), F("j")], mark=YELLOW), Sym("V", up=[D("k", "a")]),
    ], size=50, isize=34)
    cv.link(A, "a", rad=0.5)
    ls = by_pos(A, "l", "up")
    cv.guide(ls[0], ls[1], "top", 0.25)
    i_lhs = by_pos(A, "i", "down")
    j_lhs = by_pos(A, "j", "down")
    rk = by_pos(A, "k", "down")[0]
    ri = i_lhs[-1]
    rj = j_lhs[-1]
    cv.callout(ls[1], r"$l$（上）：結果のベクトルの成分" + "\n" + r"（左辺の $V^l$ と同じ）", (ls[1]["cx"] + 30, 1618),
               color=CL, anchor="top", size=15, ha="left")
    cv.callout(rk, r"$k$：入力ベクトルの成分" + "\n" + r"（$V^k$ と縮約＝和）", (rk["cx"] - 60, 1400), color=CK, size=15,
               ha="right")
    cv.callout(ri, r"$i,\,j$：動く順序（$i,j$ と $j,i$ の差）" + "\n" + "入れ替えると符号が反転" + "\n"
               + r"$R^l{}_{kij}=-R^l{}_{kji}$", (ri["cx"] + 30, 1400), color=CI, size=15, ha="left")
    cv.rich(60, 1265, [("(i, j) を1組決めると、", GRAY), (r"R^l{}_{kij}", GRAY, "m"), (" は ", GRAY), m("l", CL),
                       (" を行、", GRAY), m("k", CK), (" を列とする行列になり、", GRAY), (r"V^k", GRAY, "m"),
                       (" に掛けると ", GRAY), (r"V^l", GRAY, "m"), (" 方向のずれが出る。", GRAY)], size=15)
    cv.rich(60, 1225, [("平坦な空間では ", GRAY), (r"R^l{}_{kij}=0", GRAY, "m"),
                       ("：一周して戻ってもベクトルはずれない（並行移動）。", GRAY)], size=15)

    # ------------------------------------------------ ② 公式
    cv.card(30, 1140, 1440, 330, "② 公式（Part VII §2）：全項で、l は上に1個、k, i, j は下に1個ずつ", ec=EC)
    R0 = riemann(cv, 60, 985, dict(l="l", k="k", i="i", j="j"), size=34, isize=23)
    cv.link(R0, "t3", 0.5)
    cv.link(R0, "t4", 0.5)
    cv.rich(60, 880, [("ダミー添字 ", GRAY), m("m", CM), ("：前の Γ の下と、後ろの Γ の上でペアになり、和を取って消える。", GRAY)], size=15)
    cv.rich(60, 842, [("残るのは ", GRAY), m("l", CL), (" が上、", GRAY), m("k", CK), (" ", GRAY), m("i", CI), (" ", GRAY),
                      m("j", CJ), (" が下 → 左辺 ", GRAY), (r"R^l{}_{kij}", GRAY, "m"), (" の添字と一致。", GRAY)], size=15)

    # ------------------------------------------------ ③ 添字の帳簿チェック
    cv.card(30, 800, 1440, 600, "③ 添字の帳簿チェック：各項のどこに、どの文字があるか", ec=EC)
    cols = [("項", None, 430), ("l", CL, 170), ("k", CK, 170), ("i", CI, 170), ("j", CJ, 170), ("m", CM, 290)]
    x0, ytop = 60, 720
    rh = 74
    heads_x = []
    x = x0
    for name, col, wd in cols:
        heads_x.append((x, wd))
        x += wd
    for (xx, wd), (name, col, _) in zip(heads_x, cols):
        cv.ax.add_patch(__import__("matplotlib").patches.Rectangle((xx, ytop - 56), wd, 56, fc="#e5ecf7", ec="#8aa0c8", lw=1.6, zorder=1))
        cv.ax.text(xx + wd / 2, ytop - 28, name if col is None else f"${name}$", ha="center", va="center",
                   fontsize=19, color=col or "#20304a", fontweight="bold", zorder=5)
    rows = [
        (r"\partial_i\Gamma^l{}_{jk}", ["Γ の上", "Γ の下", "∂ の下", "Γ の下", "―"]),
        (r"-\,\partial_j\Gamma^l{}_{ik}", ["Γ の上", "Γ の下", "Γ の下", "∂ の下", "―"]),
        (r"+\,\Gamma^l{}_{im}\Gamma^m{}_{jk}", ["前の Γ の上", "後の Γ の下", "前の Γ の下", "後の Γ の下",
                                                 "前の Γ の下 ＋ 後の Γ の上\n→ 和で消える"]),
        (r"-\,\Gamma^l{}_{jm}\Gamma^m{}_{ik}", ["前の Γ の上", "後の Γ の下", "後の Γ の下", "前の Γ の下",
                                                 "前の Γ の下 ＋ 後の Γ の上\n→ 和で消える"]),
    ]
    Rect = __import__("matplotlib").patches.Rectangle
    for r, (term, cells) in enumerate(rows):
        yt = ytop - 56 - r * rh
        for c, ((xx, wd), text) in enumerate(zip(heads_x, [term] + cells)):
            fc = "#ffffff" if c else "#f6f8fc"
            if c == 5 and text != "―":
                fc = "#fff4dc"
            cv.ax.add_patch(Rect((xx, yt - rh), wd, rh, fc=fc, ec="#8aa0c8", lw=1.2, zorder=1))
            if c == 0:
                cv.ax.text(xx + 18, yt - rh / 2, f"${text}$", ha="left", va="center", fontsize=20, zorder=5)
            else:
                colr = cols[c][1] if c < 5 else CM
                cv.ax.text(xx + wd / 2, yt - rh / 2, text, ha="center", va="center",
                           fontsize=14.5 if c < 5 else 13, color="#222", zorder=5)
    yb = ytop - 56 - 4 * rh - 40
    cv.badge(80, yb, "○", GREEN, size=20)
    cv.rich(120, yb - 8, [("どの項も：", GRAY), m("l", CL), ("が上に1回、", GRAY), m("k", CK), ("・", GRAY), m("i", CI), ("・", GRAY),
                          m("j", CJ), ("が下に1回ずつ（", GRAY), m("m", CM), ("は上下で消える）。項の並びは違っても、残る添字はそろっている。", GRAY)],
            size=15)
    cv.rich(120, yb - 48, [("公式を自分で組み立てるときは、この帳簿が合うかで、添字の付け間違いに気づける。", GRAY)], size=15)

    cv.save("fig13_riemann_indices.png")


if __name__ == "__main__":
    fig10()
    fig11()
    fig12()
    fig13()
