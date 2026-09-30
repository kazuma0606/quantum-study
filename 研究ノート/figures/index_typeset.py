"""添字を「見える化」するための簡易組版（matplotlib）。

数式の各添字を 1 つずつ別の部品として配置し、座標（アンカー）を持たせる。
これにより、添字ごとの色分け・ダミー添字の囲み・添字同士の結線・引き出し注釈が描ける。

使い方の概略:
    cv = Canvas(1500, 900)
    A = cv.formula(80, 700, [Sym(r"\\Gamma", up=[F("k")], down=[D("i", "t"), F("j")]),
                             Sym("V", up=[D("i", "t")])])
    cv.link(A, "t")          # タグ "t" の 2 つのダミー添字を帯で結ぶ
    cv.save("figX.png")

座標は「ピクセル（dpi=100）」で、y は上向き。保存時は dpi=150 に拡大される。
"""

from dataclasses import dataclass, field

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.transforms import Bbox

from make_christoffel_figures import OUT  # noqa: F401  (rcParams: 日本語フォント等を設定)

DPI = 100
PX = DPI / 72.0  # 1pt = PX px

# 添字の文字ごとの固定色（同じ文字は、どの式でも同じ色）
LETTER = {"i": "#1f77b4", "j": "#2ca02c", "k": "#d62728", "l": "#9467bd",
          "m": "#e67e00", "n": "#8c564b", "a": "#c2185b", "p": "#0f9aa8", "q": "#8a8a00"}


def tint(c, f=0.80):
    r, g, b = to_rgb(c)
    return (r + (1 - r) * f, g + (1 - g) * f, b + (1 - b) * f)


@dataclass
class Ix:
    """1 つの添字。kind: free（自由）/ dummy（和を取る）/ clash（衝突：警告表示）"""
    tex: str
    kind: str = "free"
    color: str | None = None
    tag: str | None = None

    def col(self):
        return self.color or LETTER.get(self.tex, "#555555")


def F(tex, **kw):
    return Ix(tex, "free", **kw)


def D(tex, tag=None, **kw):
    return Ix(tex, "dummy", tag=tag, **kw)


def C(tex, tag=None, **kw):
    return Ix(tex, "clash", tag=tag, **kw)


@dataclass
class Sym:
    """記号 1 つ（基底文字＋上付き添字の並び＋下付き添字の並び）"""
    base: str
    up: list = field(default_factory=list)
    down: list = field(default_factory=list)
    color: str = "black"
    size: float | None = None
    mark: str | None = None  # 記号全体の背景マーカー色（δ の強調など）


@dataclass
class Txt:
    """添字のない記号・演算子（mathtext）。math=False なら通常の文字列（日本語可）"""
    s: str
    color: str = "black"
    pad: float = 12
    math: bool = True
    size: float | None = None


class Canvas:
    def __init__(self, w, h, bg="#e9eff8"):
        self.w, self.h, self.bg = w, h, bg
        self.cx0, self.cy0, self.cx1, self.cy1 = w, h, 0, 0  # カードの範囲（card() で更新）
        self.fig = plt.figure(figsize=(w / DPI, h / DPI), dpi=DPI, facecolor=bg)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(0, h)
        self.ax.axis("off")
        self.r = self.fig.canvas.get_renderer()

    # ---------------------------------------------------------- 基本部品
    def width(self, s, size, **kw):
        t = self.ax.text(0, 0, s, fontsize=size, **kw)
        wd = t.get_window_extent(self.r).width
        t.remove()
        return wd

    def card(self, x, ytop, w, h, title=None, ec="#5b7db1", lw=3.0, fc="white"):
        self.cx0, self.cx1 = min(self.cx0, x), max(self.cx1, x + w)
        self.cy0, self.cy1 = min(self.cy0, ytop - h), max(self.cy1, ytop)
        self.ax.add_patch(FancyBboxPatch((x, ytop - h), w, h,
                                         boxstyle="round,pad=0,rounding_size=18",
                                         fc=fc, ec=ec, lw=lw, zorder=0.2))
        if title:
            self.ax.text(x + 26, ytop - 22, title, fontsize=17, fontweight="bold",
                         color="#20304a", va="top", ha="left", zorder=5)

    def rich(self, x, y, segs, size=14.5, va="baseline"):
        """(文字列, 色, 種別) を左から順に並べる。種別: 't'=通常文字, 'm'=mathtext。終端 x を返す"""
        for seg in segs:
            s, col, kind = (seg + ("t",))[:3] if len(seg) == 2 else seg
            render = f"${s}$" if kind == "m" else s
            self.ax.text(x, y, render, fontsize=size, color=col, va=va, ha="left", zorder=5)
            x += self.width(render, size)
        return x

    # ---------------------------------------------------------- 添字・記号の組版
    def _index(self, ix, x, yb, isize, out, place):
        em = isize * PX
        col = ix.col()
        render = f"${ix.tex}$"
        wd = self.width(render, isize)
        pad = 0 if ix.kind == "free" else 4.5
        if ix.kind in ("dummy", "clash"):
            fc = tint(col, 0.78) if ix.kind == "dummy" else "#ffd6d6"
            ec = col if ix.kind == "dummy" else "#d62728"
            self.ax.add_patch(FancyBboxPatch((x, yb - 0.30 * em), wd + 2 * pad, 1.18 * em,
                                             boxstyle="round,pad=0,rounding_size=7",
                                             fc=fc, ec=ec, lw=1.8 if ix.kind == "dummy" else 2.4, zorder=2))
        self.ax.text(x + pad, yb, render, fontsize=isize, color=col, va="baseline", ha="left", zorder=3)
        a = dict(tag=ix.tag, letter=ix.tex, kind=ix.kind, place=place, color=col,
                 cx=x + (wd + 2 * pad) / 2, cy=yb + 0.30 * em,
                 top=yb + 0.88 * em, bot=yb - 0.30 * em, left=x, right=x + wd + 2 * pad)
        out.append(a)
        return wd + 2 * pad

    def _sym(self, x, yb, s, size, isize, out):
        bsz = s.size or size
        render = f"${s.base}$"
        bw = self.width(render, bsz)
        bpx = bsz * PX
        x0 = x
        self.ax.text(x, yb, render, fontsize=bsz, color=s.color, va="baseline", ha="left", zorder=3)
        xi = x + bw + 2
        up_y, dn_y = yb + 0.42 * bpx, yb - 0.24 * bpx

        def group(idxs, y_g, place):
            xx = xi
            for ix in idxs:
                xx += self._index(ix, xx, y_g, isize, out, place) + 2
            return xx

        x_up = group(s.up, up_y, "up")
        x_dn = group(s.down, dn_y, "down")
        x_end = max(x_up, x_dn, xi) + 4
        if s.mark:
            self.ax.add_patch(FancyBboxPatch((x0 - 6, yb - 0.55 * bpx), x_end - x0 + 8, 1.75 * bpx,
                                             boxstyle="round,pad=0,rounding_size=10",
                                             fc=s.mark, ec="none", zorder=0.6))
        return x_end

    def formula(self, x, yb, items, size=32, isize=21):
        """items を左から順に配置。戻り値は {タグ: [アンカー, ...]} と、終端 x（キー "_end"）"""
        out = []
        for it in items:
            if isinstance(it, Sym):
                x = self._sym(x, yb, it, size, isize, out)
            else:
                sz = it.size or size
                render = f"${it.s}$" if it.math else it.s
                self.ax.text(x + it.pad / 2, yb, render, fontsize=sz, color=it.color,
                             va="baseline", ha="left", zorder=3)
                x += self.width(render, sz) + it.pad
        res = {"_end": x, "_all": out}
        for a in out:
            if a["tag"]:
                res.setdefault(a["tag"], []).append(a)
        return res

    # ---------------------------------------------------------- 結線・注釈
    def link(self, A, tag, rad=0.25, lw=6, alpha=0.32):
        """タグの付いた 2 つのダミー添字を、太い半透明の帯で結ぶ（ペアであることを示す）"""
        a, b = A[tag][:2]
        self.ax.add_patch(FancyArrowPatch((a["cx"], a["cy"]), (b["cx"], b["cy"]),
                                          connectionstyle=f"arc3,rad={rad}", arrowstyle="-",
                                          lw=lw, color=a["color"], alpha=alpha, zorder=1,
                                          capstyle="round", shrinkA=0, shrinkB=0))

    def bridge(self, a, b, rad=0.25, lw=6, alpha=0.32):
        """アンカー a, b を直接指定して帯で結ぶ（1 つの添字と複数の添字をペアにしたいとき）"""
        self.ax.add_patch(FancyArrowPatch((a["cx"], a["cy"]), (b["cx"], b["cy"]),
                                          connectionstyle=f"arc3,rad={rad}", arrowstyle="-",
                                          lw=lw, color=a["color"], alpha=alpha, zorder=1,
                                          capstyle="round", shrinkA=0, shrinkB=0))

    def guide(self, a, b, side="top", rad=0.3, color=None, lw=2.0):
        """自由添字どうし（同じ文字）を点線でつなぐ。side: top / bot"""
        ya, yb = (a["top"], b["top"]) if side == "top" else (a["bot"], b["bot"])
        sgn = -1 if side == "top" else 1  # arc3: 左→右のとき rad>0 で下向きに曲がる
        self.ax.add_patch(FancyArrowPatch((a["cx"], ya), (b["cx"], yb),
                                          connectionstyle=f"arc3,rad={sgn * abs(rad)}", arrowstyle="-",
                                          lw=lw, color=color or a["color"], zorder=1.5,
                                          linestyle=(0, (1.5, 2.2)), shrinkA=0, shrinkB=0))

    def arrow(self, p, q, color="#444", lw=2.0, rad=0.0, style="-|>", ls="-", ms=14, z=4):
        self.ax.add_patch(FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}", arrowstyle=style,
                                          lw=lw, color=color, zorder=z, linestyle=ls,
                                          mutation_scale=ms, shrinkA=0, shrinkB=0))

    def callout(self, a, text, xy, color=None, anchor="bot", size=14, ha="center", weight="normal"):
        col = color or a["color"]
        y_from = a["bot"] if anchor == "bot" else a["top"]
        self.ax.annotate(text, xy=(a["cx"], y_from), xytext=xy, ha=ha, va="top" if anchor == "bot" else "bottom",
                         fontsize=size, color=col, fontweight=weight,
                         arrowprops=dict(arrowstyle="-", color=col, lw=1.6, shrinkA=3, shrinkB=1,
                                         relpos=(0.5, 1.0) if anchor == "bot" else (0.5, 0.0)),
                         zorder=6)

    def badge(self, x, y, s, color, size=22):
        """✓ / ✗ などの丸バッジ"""
        self.ax.text(x, y, s, fontsize=size, color="white", fontweight="bold", ha="center", va="center",
                     zorder=6, bbox=dict(boxstyle="circle,pad=0.28", fc=color, ec="none"))

    def save(self, name):
        # カード全体の範囲＋余白だけを残して切り出す（軸全体を余白として数えないため、範囲は自前で計算）
        pad = 34
        box = Bbox.from_extents((self.cx0 - pad) / DPI, (self.cy0 - pad) / DPI,
                                (self.cx1 + pad) / DPI, (self.cy1 + pad) / DPI)
        self.fig.savefig(OUT / name, dpi=150, facecolor=self.bg, bbox_inches=box)
        plt.close(self.fig)
        print("saved", OUT / name)
