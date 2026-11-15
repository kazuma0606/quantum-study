"""「はじめに」（00_はじめに.md）の図を作る。

実行: uv run --no-sync python 書籍/微分/figures/make_intro_figures.py [int01]

出力:
    int01_mercator.png   「この本で伝えたいこと」の地球の問い。
                         (a) 地球の上で同じ大きさの円（半径 10°）を、メルカトル図法の地図に写したもの。
                             高緯度ほど大きく描かれる（長さの倍率 1/cos φ、面積の倍率 1/cos² φ）。
                         (b) グリーンランド・カナダ・オーストラリアの実際の面積と、
                             メルカトル図法での見かけの面積の目安（代表の緯度での面積の倍率を掛けたもの）。
地図のデータは使わず、計算だけで描く。
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"

# 実際の面積（km²）。各国の総面積として広く使われている値。
AREAS = {"グリーンランド": 2_166_086, "カナダ": 9_984_670, "オーストラリア": 7_692_024}
# 見かけの面積の目安に使う代表の緯度（度）。国のおおよその中心の緯度。
REP_LAT = {"グリーンランド": 72, "カナダ": 60, "オーストラリア": 25}


def mercator_y(phi):
    """緯度 phi（ラジアン）を、メルカトル図法の縦の座標に写す。"""
    return np.log(np.tan(np.pi / 4 + phi / 2))


def circle_on_sphere(lat0, lon0, rho, n=400):
    """球面上で、中心 (lat0, lon0)、角度の半径 rho（すべてラジアン）の円の点の緯度・経度を返す。"""
    t = np.linspace(0, 2 * np.pi, n)
    lat = np.arcsin(np.sin(lat0) * np.cos(rho) + np.cos(lat0) * np.sin(rho) * np.cos(t))
    lon = lon0 + np.arctan2(
        np.sin(t) * np.sin(rho) * np.cos(lat0),
        np.cos(rho) - np.sin(lat0) * np.sin(lat),
    )
    return lat, lon


def int01():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.15, 1]})

    # (a) メルカトル図法の地図に、同じ大きさの円を写す
    rho = np.radians(10)
    lats = [0, 30, 60, 75]
    lons = [-120, -50, 20, 90]
    for lat_d in range(-60, 85, 15):
        ax1.axhline(mercator_y(np.radians(lat_d)), color=C_GRAY, lw=0.5, alpha=0.6)
    for lon_d in range(-180, 181, 30):
        ax1.axvline(np.radians(lon_d), color=C_GRAY, lw=0.5, alpha=0.6)
    for lat_d, lon_d in zip(lats, lons):
        lat, lon = circle_on_sphere(np.radians(lat_d), np.radians(lon_d), rho)
        xs, ys = lon, mercator_y(lat)
        ax1.fill(xs, ys, color=C_A, alpha=0.35)
        ax1.plot(xs, ys, color=C_A, lw=1.2)
        width = xs.max() - xs.min()
        # 横幅の倍率は、小さな円では 1/cos φ に近い（赤道の円との比）
        ratio = width / (2 * rho)
        if lat_d == 60:
            assert abs(ratio - 1 / np.cos(np.radians(60))) / 2 < 0.03, ratio
        f_area = 1 / np.cos(np.radians(lat_d)) ** 2
        label = f"緯度 {lat_d}°\n面積 約{f_area:.1f} 倍" if f_area < 10 else f"緯度 {lat_d}°\n面積 約{f_area:.0f} 倍"
        if lat_d < 70:
            ax1.text(xs.max() + np.radians(4), mercator_y(np.radians(lat_d)), label, ha="left", va="center", fontsize=9)
        else:
            ax1.text(xs.min() - np.radians(4), mercator_y(np.radians(lat_d)), label, ha="right", va="center", fontsize=9)
    ax1.set_xlim(np.radians(-180), np.radians(180))
    ax1.set_ylim(mercator_y(np.radians(-30)), mercator_y(np.radians(85)))
    yt = [0, 30, 60, 75]
    ax1.set_yticks([mercator_y(np.radians(d)) for d in yt], [f"{d}°" for d in yt])
    ax1.set_xticks([])
    ax1.set_ylabel("緯度")
    ax1.set_title("(a) 地球の上で同じ大きさの円を、メルカトル図法で描くと", fontsize=11)

    # (b) 実際の面積と、見かけの面積の目安
    names = list(AREAS)
    real = np.array([AREAS[k] for k in names]) / 1e6
    factor = np.array([1 / np.cos(np.radians(REP_LAT[k])) ** 2 for k in names])
    apparent = real * factor
    assert abs(1 / np.cos(np.radians(60)) ** 2 - 4) < 1e-12  # 緯度 60° で面積は 4 倍
    assert abs(AREAS["オーストラリア"] / AREAS["グリーンランド"] - 3.55) < 0.01  # 本文：約3.5倍
    assert abs(AREAS["カナダ"] / AREAS["オーストラリア"] - 1.30) < 0.01  # 本文：約1.3倍
    x = np.arange(len(names))
    w = 0.38
    b1 = ax2.bar(x - w / 2, real, w, color=C_A, label="実際の面積")
    b2 = ax2.bar(x + w / 2, apparent, w, color=C_B, alpha=0.8, label="メルカトル図法での見かけ（目安）")
    for rect, v in zip(b1, real):
        ax2.text(rect.get_x() + rect.get_width() / 2, v + 0.6, f"{v:.1f}", ha="center", fontsize=9)
    for rect, v in zip(b2, apparent):
        ax2.text(rect.get_x() + rect.get_width() / 2, v + 0.6, f"{v:.0f}", ha="center", fontsize=9)
    ax2.set_xticks(x, [f"{k}\n（緯度 約{REP_LAT[k]}°）" for k in names])
    ax2.set_ylabel("面積（百万 km²）")
    ax2.set_ylim(0, apparent.max() * 1.3)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.set_title("(b) 実際の面積と、地図での見かけ", fontsize=11)

    fig.text(0.5, 0.01,
             "(b) の見かけの面積は、国のおおよその中心の緯度での面積の倍率 1/cos²(緯度) を掛けた目安です。",
             ha="center", fontsize=9, color="#444444")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / "int01_mercator.png", dpi=150)
    plt.close(fig)
    print("int01_mercator.png：見かけの面積の目安", dict(zip(names, np.round(apparent, 1))))


FIGS = {"int01": int01}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(FIGS)
    for k in keys:
        FIGS[k]()
