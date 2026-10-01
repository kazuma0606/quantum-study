"""研究ノート用のアニメーションを生成するスクリプト。

実行（リポジトリのルートから）:
    uv run python 研究ノート/figures/make_animations.py

必要なもの: ffmpeg（MP4 の書き出し。GIF は Pillow だけで書き出せる）

出力（このスクリプトと同じ figures/ ディレクトリ）:
    anim01_parallel_transport.mp4   球面上の並行移動（MP4, 1280x720, 30fps）
    anim01_parallel_transport.gif   同じ内容（GIF, 軽量版）

内容は christoffel_riemann_intro.md の Part VII §3 と fig2 の例（北極 → A → B → 北極 の 1/8 球面）。
ベクトルは、経路を細かく刻んで「各ステップで接平面に射影する」方法で、実際に数値で並行移動している。
一周して戻ったときの回転角が π/2（= K × 面積 = (1/a²)(4πa²/8)）になることを assert で確認してから描く。
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from matplotlib.patches import Rectangle

from make_christoffel_figures import OUT  # 日本語フォント等の rcParams も設定される

C_VEC, C_GHOST, C_TRAIL, C_ARC = "#e67e00", "#1f77b4", "#222222", "#d62728"
S_TOTAL = 1.5 * np.pi  # 経路の長さ（3 区間 × π/2、半径 1）


# ------------------------------------------------------------------ 経路と並行移動（数値計算）
def sphere(th, ph):
    th, ph = np.broadcast_arrays(th, ph)  # スカラーと配列を混ぜても形が揃うようにする
    return np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])


def path_point(s):
    """北極 → A（赤道, φ=0）→ B（赤道, φ=π/2）→ 北極。弧長 s での位置と進行方向の単位接ベクトル"""
    if s < np.pi / 2:                      # ① 子午線 φ=0 を南へ
        th, ph = s, 0.0
        t = np.array([np.cos(s), 0.0, -np.sin(s)])
    elif s < np.pi:                        # ② 赤道を東へ
        th, ph = np.pi / 2, s - np.pi / 2
        t = np.array([-np.sin(ph), np.cos(ph), 0.0])
    else:                                  # ③ 子午線 φ=π/2 を北へ
        th, ph = np.pi / 2 - (s - np.pi), np.pi / 2
        t = np.array([0.0, -np.cos(th), np.sin(th)])
    return sphere(th, ph), t


def transport(n_steps=6000):
    """各ステップで、ベクトルを新しい点の接平面に射影して正規化する（離散的な並行移動）"""
    ss = np.linspace(0, S_TOTAL, n_steps + 1)
    P = np.zeros((n_steps + 1, 3))
    T = np.zeros_like(P)
    for k, s in enumerate(ss):
        P[k], T[k] = path_point(min(s, S_TOTAL - 1e-12))
    V = np.zeros_like(P)
    V[0] = T[0]  # 出発時のベクトル = 最初の進行方向（北極から子午線 φ=0 の向き）
    for k in range(1, n_steps + 1):
        n = P[k]
        v = V[k - 1] - (V[k - 1] @ n) * n
        V[k] = v / np.linalg.norm(v)
    # 進行方向に対するベクトルの角度（法線 P まわりの符号付き角）。区間の境界ではジャンプするので unwrap する
    ang = np.arctan2(np.einsum("ij,ij->i", P, np.cross(T, V)), np.einsum("ij,ij->i", T, V))
    ang = np.unwrap(ang)
    return ss, P, T, V, -np.degrees(ang)  # 符号を反転して、0°, 90°, 180° と増える向きにする


def verify(P, V, rel_deg):
    """本文の結論（一周すると π/2 回転、Gauss-Bonnet）が数値で成り立つことを確認する"""
    rot = np.degrees(np.arccos(np.clip(V[0] @ V[-1], -1, 1)))
    assert abs(rot - 90.0) < 0.3, f"一周後の回転角が 90° でない: {rot:.3f}°"
    assert np.allclose(V[-1], [0, 1, 0], atol=5e-3), "終点でのベクトルが (0,1,0) でない"
    # 各区間で、進行方向に対する角度は一定（0°, 90°, 180°）
    n = len(rel_deg) - 1
    assert abs(rel_deg[n // 6]) < 0.3 and abs(rel_deg[n // 2] - 90) < 0.5 and abs(rel_deg[5 * n // 6] - 180) < 0.5
    # 曲がり角の合計 3×90° = 270°。平面なら 360° なので、不足 90° が回転角（= K × 面積 = π/2）
    area, K = 4 * np.pi / 8, 1.0
    assert abs(np.degrees(K * area) - 90.0) < 1e-9 and abs((360 - 3 * 90) - rot) < 0.3
    return rot


# ------------------------------------------------------------------ アニメーション
def build_figure(ss, P, V, rel):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="white")
    ax = fig.add_axes([0.0, 0.07, 0.60, 0.83], projection="3d")
    bx = fig.add_axes([0.675, 0.22, 0.30, 0.50])

    # 球面と、1/8 球面（経路で囲まれる領域）
    u, w = np.meshgrid(np.linspace(0, np.pi, 50), np.linspace(0, 2 * np.pi, 100))
    ax.plot_surface(np.sin(u) * np.cos(w), np.sin(u) * np.sin(w), np.cos(u), color="#dfe8f5", alpha=0.10, linewidth=0, shade=False)
    uo, wo = np.meshgrid(np.linspace(0, np.pi / 2, 30), np.linspace(0, np.pi / 2, 30))
    ax.plot_surface(np.sin(uo) * np.cos(wo), np.sin(uo) * np.sin(wo), np.cos(uo), color="#f5e6b8", alpha=0.45, linewidth=0, shade=False)
    for deg in range(0, 360, 30):  # 緯線・経線（薄く）
        q = np.linspace(0, np.pi, 80)
        ax.plot(*sphere(q, np.deg2rad(deg)), color="#c4cfdf", lw=0.5)
    for deg in (30, 60, 90, 120, 150):
        q = np.linspace(0, 2 * np.pi, 120)
        ax.plot(*sphere(np.deg2rad(deg), q), color="#c4cfdf", lw=0.5)
    ax.text(-0.17, -0.13, 1.12, "北極", ha="center", fontsize=13)  # 真上から見ても矢印と重ならない位置
    ax.text(1.14, 0, -0.06, "A", fontsize=15)
    ax.text(0, 1.14, -0.06, "B", fontsize=15)
    ax.set_box_aspect((1, 1, 1), zoom=1.25)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.view_init(elev=26, azim=42)
    ax.set_axis_off()

    # 出発時のベクトル（青）、軌跡、現在の点
    lift = 1.03
    ghost = ax.quiver(*(lift * P[0]), *(0.5 * V[0]), color=C_GHOST, lw=4.5, arrow_length_ratio=0.28)
    # 凡例は画面に固定して、矢印やラベルと重ならないようにする
    ax.text2D(0.02, 0.93, "■ 出発時のベクトル", color=C_GHOST, transform=ax.transAxes, fontsize=14)
    ax.text2D(0.02, 0.88, "■ 運ばれるベクトル", color=C_VEC, transform=ax.transAxes, fontsize=14)
    (trail,) = ax.plot([], [], [], color=C_TRAIL, lw=2.4)
    (dot,) = ax.plot([], [], [], "o", color=C_TRAIL, ms=7)

    # 右: 進行方向に対するベクトルの角度
    bounds = [0, np.pi / 2, np.pi, S_TOTAL]
    for i, (a, b) in enumerate(zip(bounds[:-1], bounds[1:])):
        bx.axvspan(a / S_TOTAL, b / S_TOTAL, color=["#fdeccb", "#e6f0fb", "#e9e1f3"][i], alpha=0.8, lw=0)
        bx.text((a + b) / 2 / S_TOTAL, 196, "①②③"[i], ha="center", fontsize=15)
    bx.set_xlim(0, 1.025)  # 終点の点が枠で切れないように、右に少し余白を取る
    bx.set_ylim(-10, 210)
    bx.set_yticks([0, 90, 180])
    bx.set_yticklabels(["0°", "90°", "180°"])
    bx.set_xticks([])
    bx.set_ylabel("進行方向からのベクトルのずれ角", fontsize=12)
    bx.set_xlabel("経路に沿って →", fontsize=12)
    bx.set_title("ベクトル自身は回らない。\n進行方向のほうが曲がり角で回る", fontsize=12.5)
    (curve,) = bx.plot([], [], color=C_VEC, lw=3)
    (bdot,) = bx.plot([], [], "o", color=C_VEC, ms=8)
    for y in (0, 90, 180):
        bx.axhline(y, color="#bbb", lw=0.7, ls=":")

    title = fig.text(0.5, 0.955, "球面上の並行移動：一周して戻ると、ベクトルは $90^\\circ$ 回って戻る", ha="center", fontsize=20, fontweight="bold")
    stage = fig.text(0.30, 0.085, "", ha="center", fontsize=15)
    final = fig.text(0.5, 0.03, "", ha="center", fontsize=14, color="#222")
    final.set_visible(False)

    return fig, ax, bx, dict(ghost=ghost, trail=trail, dot=dot, curve=curve, bdot=bdot, stage=stage, final=final, title=title, qs=[], extra=[])


STAGES = [
    "① 北極 → A（子午線に沿って）：ベクトルは進行方向と平行",
    "② A → B（赤道に沿って）：ベクトルは進行方向と垂直（90°）",
    "③ B → 北極（子午線に沿って）：ベクトルは進行方向と逆向き（180°）",
]


def make_update(fig, ax, bx, art, ss, P, V, rel, n_move, n_total):
    n = len(ss) - 1

    def update(f):
        k = int(round(min(f, n_move) / n_move * n))
        for q in art["qs"]:
            q.remove()
        art["qs"].clear()
        base, vec = 1.03 * P[k], 0.5 * V[k]
        art["qs"].append(ax.quiver(*base, *vec, color=C_VEC, lw=4.5, arrow_length_ratio=0.28))
        art["trail"].set_data_3d(*(1.01 * P[: k + 1]).T)
        art["dot"].set_data_3d([P[k, 0]], [P[k, 1]], [P[k, 2]])
        art["curve"].set_data(ss[: k + 1] / S_TOTAL, rel[: k + 1])
        art["bdot"].set_data([ss[k] / S_TOTAL], [rel[k]])
        seg = min(int(ss[k] // (np.pi / 2)), 2)
        for e in art["extra"]:
            e.remove()
        art["extra"].clear()
        if f < n_move:
            art["stage"].set_x(0.30)
            art["stage"].set_text(STAGES[seg])
            art["final"].set_visible(False)
            ax.view_init(elev=26, azim=42)
        else:  # 終わりの画面：カメラを真上に回し、出発時と帰着時のベクトルの間の角度を示す
            t = np.clip((f - n_move) / 60.0, 0.0, 1.0)
            s = t * t * (3 - 2 * t)  # smoothstep
            ax.view_init(elev=26 + (82 - 26) * s, azim=42 + (-90 - 42) * s)
            art["stage"].set_x(0.5)
            art["stage"].set_text("④ 一周して戻ると、運ばれたベクトル（橙）は出発時（青）から 90° ずれる")
            v0, v1 = V[0], V[-1]
            tt = np.linspace(0, np.pi / 2, 40)
            arc = np.array([lift_pole + 0.30 * (np.cos(a) * v0 + np.sin(a) * v1) for a in tt])
            (ln,) = ax.plot(*arc.T, color=C_ARC, lw=3.6)
            mid = lift_pole + 0.44 * (np.cos(np.pi / 4) * v0 + np.sin(np.pi / 4) * v1)
            tx = ax.text(*(mid + [0, 0, 0.05]), "90°", color=C_ARC, fontsize=18, fontweight="bold", ha="center",
                         bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
            art["extra"].extend([ln, tx])
            art["final"].set_text("曲がり角の合計は $90^\\circ\\times3=270^\\circ$（平面なら $360^\\circ$）。不足の $90^\\circ$ が回転角 ＝ "
                                  "$K\\times$面積 ＝ $\\dfrac{1}{a^2}\\cdot\\dfrac{4\\pi a^2}{8}=\\dfrac{\\pi}{2}$")
            art["final"].set_visible(True)
        return []

    lift_pole = 1.03 * P[0]
    return update


def render(name_stem, ss, P, V, rel, fps, dpi, step, total_move_sec=9.0, hold_sec=3.5, writer="mp4"):
    n_move = int(total_move_sec * 30)
    n_total = n_move + int(hold_sec * 30)
    frames = list(range(0, n_total + 1, step))
    fig, ax, bx, art = build_figure(ss, P, V, rel)
    update = make_update(fig, ax, bx, art, ss, P, V, rel, n_move, n_total)
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    if writer == "mp4":
        w = animation.FFMpegWriter(fps=fps, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "20"])
        path = OUT / f"{name_stem}.mp4"
    else:
        w = animation.PillowWriter(fps=fps)
        path = OUT / f"{name_stem}.gif"
    ani.save(path, writer=w, dpi=dpi)
    plt.close(fig)
    print(f"saved {path.name}: {path.stat().st_size / 1e6:.2f} MB, {len(frames)} frames @ {fps}fps")
    return path


def anim01_parallel_transport(mp4=False):
    ss, P, T, V, rel = transport()
    rot = verify(P, V, rel)
    print(f"[anim01] 一周後の回転角 = {rot:.3f}°（期待値 90°）、終点のベクトル = {np.round(V[-1], 4)}")
    if mp4:
        render("anim01_parallel_transport", ss, P, V, rel, fps=30, dpi=100, step=1, writer="mp4")
    render("anim01_parallel_transport", ss, P, V, rel, fps=10, dpi=55, step=3, writer="gif")


# ================================================================== anim02: 混合偏微分は交換する（と、交換しない例）
C_I, C_J = "#1f77b4", "#e67e00"  # i→j（青）、j→i（橙）
C_GAP = "#d62728"


def lie_bracket_numeric(p, h=1e-6):
    """平面の単位ベクトル場 X=e_r, Y=e_θ の交換子 [X,Y]=(X·∇)Y-(Y·∇)X を、中心差分で求める（独立な検算用）"""
    def X(q):
        return q / np.linalg.norm(q)

    def Y(q):
        return np.array([-q[1], q[0]]) / np.linalg.norm(q)

    def jac(F):
        J = np.zeros((2, 2))
        for k in range(2):
            d = np.zeros(2)
            d[k] = h
            J[:, k] = (F(p + d) - F(p - d)) / (2 * h)
        return J

    return jac(Y) @ X(p) - jac(X) @ Y(p)


def anim02_mixed_partials(mp4=False):
    # ---------------------------------------------------------------- 前半: 曲面 r(u,v)=(u,v,f(u,v))
    fa, fb = 1.1, 0.8

    def f(u, v):
        return 0.5 * np.sin(fa * u) * np.cos(fb * v) + 0.12 * (u**2 + v**2)

    def R(u, v):
        u, v = np.broadcast_arrays(u, v)
        return np.array([u, v, f(u, v)])

    def f_uv(u, v):
        return -0.5 * fa * fb * np.cos(fa * u) * np.sin(fb * v)

    u0, v0 = 0.30, 0.40
    P0 = R(u0, v0)
    r_uv = np.array([0.0, 0.0, f_uv(u0, v0)])  # r_ij = ∂_u∂_v r = (0, 0, f_uv)
    eps_list = np.geomspace(0.85, 0.04, 140)

    def D_ij(e):  # i 方向に動かしてから j 方向の変化を測り、原点での j 方向の変化を引く
        return (R(u0 + e, v0 + e) - R(u0 + e, v0)) - (R(u0, v0 + e) - R(u0, v0))

    def D_ji(e):  # 順序を入れ替えたもの
        return (R(u0 + e, v0 + e) - R(u0, v0 + e)) - (R(u0 + e, v0) - R(u0, v0))

    Dij = np.array([D_ij(e) / e**2 for e in eps_list])
    Dji = np.array([D_ji(e) / e**2 for e in eps_list])
    assert np.max(np.abs(Dij - Dji)) < 1e-12, "有限差分でも、i と j の順序によらず一致するはず"
    err = np.abs(Dij[:, 2] - r_uv[2])
    # 主張できるのは「ε→0 で収束する」こと（誤差が厳密に単調に減るとは限らない）。
    # 収束の確認: 最後の誤差が最初の 1/5 以下で、|r_ij| の 10% 以内。誤差は ε にほぼ比例（ε を半分にすると誤差も約半分）。
    # （ε が 0.85→0.04 の範囲では、誤差は約 0.047→0.005 に縮む。比は約 0.11）
    assert err[-1] < 0.2 * err[0] and err[-1] < 0.1 * abs(r_uv[2]), "ε→0 で D/ε² が r_ij に収束するはず"
    e_half = 0.02
    err_a = abs(D_ij(2 * e_half)[2] / (2 * e_half) ** 2 - r_uv[2])
    err_b = abs(D_ij(e_half)[2] / e_half**2 - r_uv[2])
    assert 1.7 < err_a / err_b < 2.3, f"誤差が ε にほぼ比例するはず（比 = {err_a / err_b:.2f}）"
    print(f"[anim02] D/ε²: ε={eps_list[0]:.2f} で {Dij[0, 2]:+.4f}、ε={eps_list[-1]:.2f} で {Dij[-1, 2]:+.4f}、r_ij の z 成分 = {r_uv[2]:+.4f}")

    # ---------------------------------------------------------------- 後半: 平面の単位ベクトル場 e_r, e_θ
    r0, th0 = 1.2, np.deg2rad(30)

    def pol(r, th):
        return np.array([r * np.cos(th), r * np.sin(th)])

    t_list = np.geomspace(0.9, 0.05, 140)

    def end_A(t):  # X=e_r を t、次に Y=e_θ を t（弧長）
        return pol(r0 + t, th0 + t / (r0 + t))

    def end_B(t):  # Y=e_θ を t（弧長）、次に X=e_r を t
        return pol(r0 + t, th0 + t / r0)

    gaps = np.array([np.linalg.norm(end_B(t) - end_A(t)) for t in t_list]) / t_list**2
    br = lie_bracket_numeric(pol(r0, th0))
    e_th0 = np.array([-np.sin(th0), np.cos(th0)])
    assert abs(np.linalg.norm(br) - 1 / r0) < 1e-6 and abs(abs(br @ e_th0) - 1 / r0) < 1e-6, "[e_r, e_θ] = e_θ / r のはず"
    assert abs(gaps[-1] - 1 / r0) < 0.01 / r0, "着く点のずれ / t² が |[X,Y]| = 1/r に近づくはず"
    print(f"[anim02] 単位ベクトル場の枠: ずれ/t² = {gaps[0]:.4f}（t=0.9）→ {gaps[-1]:.4f}（t=0.05）、|[X,Y]| = 1/r = {1 / r0:.4f}")

    # ---------------------------------------------------------------- 図の準備
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="white")
    ax3 = fig.add_axes([0.0, 0.14, 0.60, 0.76], projection="3d")
    ax2 = fig.add_axes([0.04, 0.17, 0.52, 0.70])
    bx1 = fig.add_axes([0.67, 0.27, 0.30, 0.46])
    bx2 = fig.add_axes([0.67, 0.27, 0.30, 0.46])

    # 3D の曲面
    uu, vv = np.meshgrid(np.linspace(-0.3, 1.5, 50), np.linspace(-0.2, 1.5, 50))
    ax3.plot_surface(uu, vv, f(uu, vv), color="#cfe0f5", alpha=0.35, linewidth=0, shade=False)
    for c in np.linspace(-0.3, 1.5, 10):
        s = np.linspace(-0.2, 1.5, 60)
        ax3.plot(c + 0 * s, s, f(c + 0 * s, s), color="#9ab5d6", lw=0.5)
    for c in np.linspace(-0.2, 1.5, 9):
        s = np.linspace(-0.3, 1.5, 60)
        ax3.plot(s, c + 0 * s, f(s, c + 0 * s), color="#9ab5d6", lw=0.5)
    ax3.set_box_aspect((1.2, 1.1, 0.7), zoom=1.2)
    ax3.set_xlim(-0.3, 1.5)
    ax3.set_ylim(-0.2, 1.5)
    ax3.set_zlim(-0.1, 1.0)
    ax3.view_init(elev=30, azim=-58)
    ax3.set_axis_off()
    ax3.plot(*P0, "ko", ms=6)
    (route1,) = ax3.plot([], [], [], color=C_I, lw=3.2)
    (route2,) = ax3.plot([], [], [], color=C_J, lw=3.2)
    (para,) = ax3.plot([], [], [], color="#888", lw=1.4, ls="--")
    (gap3,) = ax3.plot([], [], [], color=C_GAP, lw=6)
    (pts3,) = ax3.plot([], [], [], "o", color="#333", ms=5)
    ax3.text2D(0.02, 0.97, "■ 青：$i$ 方向 → $j$ 方向", color=C_I, transform=ax3.transAxes, fontsize=13)
    ax3.text2D(0.02, 0.92, "■ 橙：$j$ 方向 → $i$ 方向", color=C_J, transform=ax3.transAxes, fontsize=13)
    ax3.text2D(0.02, 0.87, "■ 赤：平行四辺形の4つ目の頂点からのずれ $D$", color=C_GAP, transform=ax3.transAxes, fontsize=13)
    ax3.text2D(0.02, 0.82, "→ 黒：$\\mathbf{r}_{ij}$（3倍に拡大）　暗い赤：$D/\\varepsilon^2$（3倍）", color="#333", transform=ax3.transAxes, fontsize=12)

    # 右（前半）: D/ε² の z 成分
    bx1.axhline(r_uv[2], color="k", lw=1.6, ls="--")
    bx1.text(0.5, r_uv[2], "$\\mathbf{r}_{ij}$ の $z$ 成分\n（正確な値）", fontsize=11, va="bottom", ha="center")
    (c_ij,) = bx1.plot([], [], color=C_I, lw=3.4, label="$i\\to j$ の順")
    (c_ji,) = bx1.plot([], [], color=C_J, lw=2.4, ls=(0, (4, 3)), label="$j\\to i$ の順")
    (d1,) = bx1.plot([], [], "o", color=C_I, ms=8)
    bx1.set_xscale("log")
    bx1.set_xlim(0.9, 0.035)
    bx1.set_xticks([0.5, 0.2, 0.1, 0.05])
    bx1.set_xticklabels(["0.5", "0.2", "0.1", "0.05"])
    bx1.minorticks_off()  # 対数軸の細かい目盛りラベルが重なって読めなくなるのを防ぐ
    lo = min(Dij[:, 2].min(), r_uv[2]) - 0.01
    hi = max(Dij[:, 2].max(), r_uv[2]) + 0.03
    bx1.set_ylim(lo, hi)
    bx1.set_xlabel("刻み幅 $\\varepsilon$（小さくなる →）", fontsize=12)
    bx1.set_ylabel("$D/\\varepsilon^2$ の $z$ 成分", fontsize=12)
    bx1.set_title("$\\varepsilon\\to0$ で、順序によらず\n$\\mathbf{r}_{ij}$ に収束する", fontsize=12.5)
    bx1.legend(loc="lower left", fontsize=11)

    # 平面（後半）
    for rr in (0.6, 1.2, 1.8, 2.4):
        a = np.linspace(0, np.pi / 2, 100)
        ax2.plot(rr * np.cos(a), rr * np.sin(a), color="#d4dbe6", lw=0.8)
    for dth in np.deg2rad(np.arange(0, 91, 15)):
        ax2.plot([0, 2.5 * np.cos(dth)], [0, 2.5 * np.sin(dth)], color="#d4dbe6", lw=0.8)
    ax2.plot(*pol(r0, th0), "ko", ms=7)
    ax2.text(*(pol(r0, th0) + [-0.22, -0.12]), "出発点", fontsize=12)
    (rA,) = ax2.plot([], [], color=C_I, lw=3.2)
    (rB,) = ax2.plot([], [], color=C_J, lw=3.2)
    (gap2,) = ax2.plot([], [], color=C_GAP, lw=5)
    (pA,) = ax2.plot([], [], "o", color=C_I, ms=7)
    (pB,) = ax2.plot([], [], "o", color=C_J, ms=7)
    ax2.set_aspect("equal")
    ax2.set_xlim(0.1, 2.5)
    ax2.set_ylim(0.0, 1.75)
    ax2.axis("off")
    ax2.text(0.12, 1.66, "■ 青：$X=\\hat e_r$ → $Y=\\hat e_\\theta$（それぞれ長さ $t$）", color=C_I, fontsize=13, va="top")
    ax2.text(0.12, 1.55, "■ 橙：$Y=\\hat e_\\theta$ → $X=\\hat e_r$", color=C_J, fontsize=13, va="top")
    ax2.text(0.12, 1.44, "■ 赤：着く点のずれ（$\\propto t^2$）", color=C_GAP, fontsize=13, va="top")
    ax2.set_visible(False)

    # 右（後半）: ずれ / t²
    bx2.axhline(0, color=C_I, lw=3.0)
    bx2.text(0.45, 0.0, "座標基底 $\\partial_r,\\partial_\\theta$：常に 0", color=C_I, fontsize=11, va="bottom", ha="center")
    bx2.axhline(1 / r0, color="k", lw=1.4, ls="--")
    bx2.text(0.45, 1 / r0, "$|[X,Y]|=1/r$", fontsize=11, va="bottom", ha="center")
    (c_gap,) = bx2.plot([], [], color=C_GAP, lw=3.4)
    (d2,) = bx2.plot([], [], "o", color=C_GAP, ms=8)
    bx2.set_xscale("log")
    bx2.set_xlim(0.95, 0.045)
    bx2.set_xticks([0.5, 0.2, 0.1, 0.05])
    bx2.set_xticklabels(["0.5", "0.2", "0.1", "0.05"])
    bx2.minorticks_off()
    bx2.set_ylim(-0.12, 1.2)
    bx2.set_xlabel("刻み幅 $t$（小さくなる →）", fontsize=12)
    bx2.set_ylabel("着く点のずれ $/\\,t^2$", fontsize=12)
    bx2.set_title("単位ベクトルの枠では、$t\\to0$ でも\nずれ$/t^2$ は 0 に近づかない", fontsize=12.5)
    bx2.set_visible(False)

    title = fig.text(0.5, 0.955, "", ha="center", fontsize=20, fontweight="bold")
    line1 = fig.text(0.5, 0.095, "", ha="center", fontsize=14.5)
    line2 = fig.text(0.5, 0.035, "", ha="center", fontsize=14.5)

    n1, n2 = 240, 195  # 前半・後半のフレーム数（30fps 換算）
    hold1, hold2 = 40, 45
    tmp = []

    def update(f):
        for a in tmp:
            a.remove()
        tmp.clear()
        phase1 = f < n1
        ax3.set_visible(phase1)
        bx1.set_visible(phase1)
        ax2.set_visible(not phase1)
        bx2.set_visible(not phase1)
        if phase1:
            k = int(round(min(f, n1 - hold1 - 1) / (n1 - hold1 - 1) * (len(eps_list) - 1)))
            e = eps_list[k]
            P1, P2, P3 = R(u0 + e, v0), R(u0, v0 + e), R(u0 + e, v0 + e)
            Q = P1 + P2 - P0
            s = np.linspace(0, e, 30)
            r1 = np.concatenate([R(u0 + s, v0 + 0 * s), R(u0 + e + 0 * s, v0 + s)], axis=1)
            r2 = np.concatenate([R(u0 + 0 * s, v0 + s), R(u0 + s, v0 + e + 0 * s)], axis=1)
            route1.set_data_3d(*r1)
            route2.set_data_3d(*r2)
            loop = np.array([P0, P1, Q, P2, P0]).T
            para.set_data_3d(*loop)
            gap3.set_data_3d(*np.array([Q, P3]).T)
            pts3.set_data_3d(*np.array([P0, P1, P2, P3]).T)
            lift = P0 + np.array([0, 0, 0.0])
            tmp.append(ax3.quiver(*lift, *(3 * r_uv), color="k", lw=2.0, arrow_length_ratio=0.25))
            tmp.append(ax3.quiver(*lift, *(3 * Dij[k]), color="#7a0f12", lw=4.0, arrow_length_ratio=0.25))
            for name, p, off in (("$P_1$", P1, (0.04, -0.07, 0.0)), ("$P_2$", P2, (-0.07, 0.04, 0.0)), ("$P_3$", P3, (0.04, 0.04, 0.05))):
                tmp.append(ax3.text(*(p + np.array(off)), name, fontsize=15, fontweight="bold"))
            c_ij.set_data(eps_list[: k + 1], Dij[: k + 1, 2])
            c_ji.set_data(eps_list[: k + 1], Dji[: k + 1, 2])
            d1.set_data([e], [Dij[k, 2]])
            title.set_text("混合偏微分は交換する：$\\partial_i\\partial_j\\mathbf{r}=\\partial_j\\partial_i\\mathbf{r}$")
            line1.set_text(f"座標線に沿って進む2通りの経路は、同じ点 $P_3$ に着く（$\\varepsilon={e:.2f}$）。"
                           "$D=\\mathbf{r}(P_3)-\\mathbf{r}(P_1)-\\mathbf{r}(P_2)+\\mathbf{r}(P_0)$")
            line2.set_text("$D/\\varepsilon^2\\to\\mathbf{r}_{ij}$（$i,j$ を入れ替えても同じ）。だから $\\Gamma^k{}_{ij}=\\Gamma^k{}_{ji}$、$\\mathbf{r}_{ijl}=\\mathbf{r}_{ilj}$")
        else:
            g = f - n1
            k = int(round(min(g, n2 - hold2 - 1) / (n2 - hold2 - 1) * (len(t_list) - 1)))
            t = t_list[k]
            sr = np.linspace(0, t, 30)
            arcA = np.linspace(th0, th0 + t / (r0 + t), 30)
            arcB = np.linspace(th0, th0 + t / r0, 30)
            A = np.concatenate([pol(r0 + sr, th0 + 0 * sr), pol(r0 + t + 0 * arcA, arcA)], axis=1)
            B = np.concatenate([pol(r0 + 0 * arcB, arcB), pol(r0 + sr, th0 + t / r0 + 0 * sr)], axis=1)
            rA.set_data(*A)
            rB.set_data(*B)
            eA, eB = end_A(t), end_B(t)
            gap2.set_data(*np.array([eA, eB]).T)
            pA.set_data([eA[0]], [eA[1]])
            pB.set_data([eB[0]], [eB[1]])
            c_gap.set_data(t_list[: k + 1], gaps[: k + 1])
            d2.set_data([t], [gaps[k]])
            title.set_text("座標基底でない枠では、交換しない：$[X,Y]\\neq0$")
            line1.set_text(f"単位ベクトル場 $X=\\hat e_r,\\ Y=\\hat e_\\theta$ で2通りに進むと、着く点が $t^2/r$ だけずれる（$t={t:.2f}$）。")
            line2.set_text("$[\\hat e_r,\\hat e_\\theta]=\\hat e_\\theta/r\\neq0$。座標基底 $\\partial_r,\\partial_\\theta$ なら、$[\\partial_r,\\partial_\\theta]=0$ で、ずれは常に 0。")
        return []

    total = n1 + n2
    frames = list(range(0, total, 3))
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    path = OUT / "anim02_mixed_partials.gif"
    ani.save(path, writer=animation.PillowWriter(fps=10), dpi=55)
    print(f"saved {path.name}: {path.stat().st_size / 1e6:.2f} MB, {len(frames)} frames @10fps")
    if mp4:
        ani2 = animation.FuncAnimation(fig, update, frames=list(range(total)), blit=False)
        p2 = OUT / "anim02_mixed_partials.mp4"
        ani2.save(p2, writer=animation.FFMpegWriter(fps=30, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]), dpi=100)
        print(f"saved {p2.name}: {p2.stat().st_size / 1e6:.2f} MB")
    plt.close(fig)


# ================================================================== anim03: 偏微分は交換するが、共変微分は交換しない
def anim03_holonomy(mp4=False):
    """球面上の小さな「座標の四角形」を、2通りの順序で回って並行移動する。位置は一致するが、ベクトルは R^l_{kij} だけずれる。"""
    a = 1.0
    th0, ph0 = np.deg2rad(55.0), np.deg2rad(20.0)

    def pt(th, ph):
        return sphere(th, ph)

    def e_th(th, ph):
        return np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])

    def e_ph(th, ph):
        return np.array([-np.sin(ph), np.cos(ph), 0.0])  # 単位ベクトル（座標基底 ∂_φ の長さは sinθ）

    def transport_edge(v, th_a, ph_a, th_b, ph_b, n=400):
        """座標線に沿って (th_a,ph_a)→(th_b,ph_b) へ、v を並行移動する（各ステップで接平面に射影）"""
        ths, phs = np.linspace(th_a, th_b, n + 1), np.linspace(ph_a, ph_b, n + 1)
        for k in range(1, n + 1):
            nrm = pt(ths[k], phs[k])
            v = v - (v @ nrm) * nrm
        return v

    def loop(eps, order, v0):
        """order='ij': θ 方向 → φ 方向（… の順で四角形の2辺を進んで、反対側の頂点に着く）"""
        if order == "ij":
            corners = [(th0, ph0), (th0 + eps, ph0), (th0 + eps, ph0 + eps)]
        else:
            corners = [(th0, ph0), (th0, ph0 + eps), (th0 + eps, ph0 + eps)]
        v = v0.copy()
        for (ta, pa), (tb, pb) in zip(corners[:-1], corners[1:]):
            v = transport_edge(v, ta, pa, tb, pb)
        return v, corners

    v0 = e_th(th0, ph0) * np.cos(np.deg2rad(35)) + e_ph(th0, ph0) * np.sin(np.deg2rad(35))  # 任意の向きのベクトル
    v0 /= np.linalg.norm(v0)

    # ---- 検算: ずれ ≈ ε² R^l_{kij} V^k（球面では R^θ_{φθφ}=sin²θ, R^φ_{θθφ}=-1。座標成分で比較）
    def comps(v):  # 接ベクトル v を座標成分 (v^θ, v^φ) に分解する（単位基底に直して、φ 成分は sinθ で割る）
        return np.array([v @ e_th(th0, ph0), (v @ e_ph(th0, ph0)) / np.sin(th0)])

    eps_chk = 0.02
    vA, _ = loop(eps_chk, "ij", v0)
    vB, _ = loop(eps_chk, "ji", v0)
    delta = comps(vB - vA)  # (V の差) = 2通りの順序の差
    # 定義 (∇_i∇_j - ∇_j∇_i) V^l = R^l_{kij} V^k に対応して、i=θ, j=φ。V^k = (v^θ, v^φ)。
    Vc = comps(v0)
    # R^θ_{kθφ}: k=φ のみ非零（= sin²θ）、R^φ_{kθφ}: k=θ のみ非零（= -1）。ここで運ばれる量の差は、i と j の順序の入れ替えに対応
    pred = np.array([np.sin(th0) ** 2 * Vc[1], -1.0 * Vc[0]]) * eps_chk**2
    ratio = np.linalg.norm(delta) / np.linalg.norm(pred)
    assert 0.9 < ratio < 1.1, f"ずれの大きさが ε² R V と合わない（比 = {ratio:.3f}）"
    assert np.allclose(np.abs(delta), np.abs(pred), rtol=0.1, atol=1e-6), f"成分も合うはず: {delta} vs {pred}"
    # 位置は一致する（どちらの経路も同じ頂点）。ずれは ε² に比例する
    d1 = np.linalg.norm(loop(0.04, "ij", v0)[0] - loop(0.04, "ji", v0)[0])
    d2 = np.linalg.norm(loop(0.02, "ij", v0)[0] - loop(0.02, "ji", v0)[0])
    assert 3.6 < d1 / d2 < 4.4, f"ずれは ε² に比例するはず（比 = {d1 / d2:.2f}）"
    print(f"[anim03] ε=0.02: ずれ(数値) = {np.round(delta, 6)}、ε² R V(理論) = {np.round(pred, 6)}、大きさの比 = {ratio:.3f}。ε を半分にするとずれは 1/{d1 / d2:.2f}")

    # ---- 描画
    # 方針: 四角形を「画面上でつねに同じ大きさ」で描く（座標を ε で割った正規化座標で描く）。
    # こうすると ε を小さくしても形が潰れず、ベクトルのずれを一定の拡大率で比べられる。
    C_A, C_B, C_D = "#1f77b4", "#e67e00", "#d62728"
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="white")
    ax = fig.add_axes([0.04, 0.17, 0.52, 0.66])
    bx = fig.add_axes([0.68, 0.30, 0.29, 0.42])

    eps_list = np.geomspace(0.5, 0.05, 90)
    Amp = 9.0 / (0.5**2)  # ずれの拡大率の基準: ε=0.5 のずれが画面上で少し見える長さになるようにする（ずれ ∝ ε²）
    dev = np.array([np.linalg.norm(loop(e, "ji", v0)[0] - loop(e, "ij", v0)[0]) for e in eps_list]) / eps_list**2
    r_pred = np.linalg.norm(
        np.array([np.sin(th0) ** 2 * Vc[1] * np.sin(th0) * 0 + np.sin(th0) ** 2 * Vc[1], -1.0 * Vc[0] * np.sin(th0)])
    )  # 単位基底での |R^l_{kθφ} V^k| の大きさ（φ 成分は sinθ 倍して単位基底に直す）

    def unit_frame_xy(vec):
        """接ベクトルを、点 (th0,ph0) の単位基底 (e_θ, e_φ) の成分（画面上の x=φ 方向, y=θ 方向の逆）に直す"""
        return np.array([vec @ e_ph(th0, ph0), -(vec @ e_th(th0, ph0))])

    # 画面: x=φ 方向、y=−θ 方向（上が北＝θ が小さい側）。四角形は [0,1]×[0,1]（ε で正規化）
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=float)
    ax.plot(sq[:, 0], sq[:, 1], color="#e2e6ee", lw=1.0, zorder=0)
    ax.set_aspect("equal")
    ax.set_xlim(-0.55, 1.75)
    ax.set_ylim(-0.95, 2.0)
    ax.axis("off")
    # 経路（φ 方向を右、θ 方向を下とする）。順 'ij' は θ 方向（下）→ φ 方向（右）、'ji' は φ 方向（右）→ θ 方向（下）
    P0_, P1_, P2_, P3_ = np.array([0.0, 1.0]), np.array([0.0, 0.0]), np.array([1.0, 1.0]), np.array([1.0, 0.0])
    # P0 左上=出発点、P1 左下（θ 方向に進んだ点）、P2 右上（φ 方向に進んだ点）、P3 右下=到着点
    ax.plot(*np.array([P0_, P1_, P3_]).T, color=C_A, lw=4.0, solid_capstyle="round", zorder=2)
    ax.plot(*np.array([P0_, P2_, P3_]).T, color=C_B, lw=4.0, solid_capstyle="round", zorder=2)
    for p, name, off, ha in ((P0_, "出発点", (-0.07, 0.0), "right"), (P3_, "到着点\n（どちらの経路も同じ点）", (-0.10, -0.06), "right")):
        ax.plot(*p, "o", color="#222", ms=8, zorder=5)
        ax.text(p[0] + off[0], p[1] + off[1], name, fontsize=12.5, ha=ha, va="center" if off[1] == 0 else "top")
    ax.annotate("", xy=(0.52, 0.06), xytext=(0.30, 0.06), arrowprops=dict(arrowstyle="-|>", color=C_A, lw=2), zorder=3)
    ax.annotate("", xy=(0.04, 0.52), xytext=(0.04, 0.74), arrowprops=dict(arrowstyle="-|>", color=C_A, lw=2), zorder=3)
    ax.text(0.55, 1.07, "$\\phi$ 方向 →", fontsize=12, color="#555", ha="center")
    ax.text(-0.13, 0.5, "$\\theta$\n方向\n↓", fontsize=12, color="#555", ha="center", va="center")
    ax.text(-0.5, 1.95, "■ 青：$\\theta$ 方向 → $\\phi$ 方向 の順に運ぶ", color=C_A, fontsize=13, va="top")
    ax.text(-0.5, 1.85, "■ 橙：$\\phi$ 方向 → $\\theta$ 方向 の順に運ぶ", color=C_B, fontsize=13, va="top")
    ax.text(-0.5, 1.75, "■ 灰：出発点のベクトル（どちらの経路でも同じ）", color="#555", fontsize=13, va="top")
    ax.text(-0.5, 1.60, "（四角形の大きさは $\\varepsilon$ で正規化して描画）", color="#666", fontsize=11, va="top")

    bx.axhline(0, color="#9aa", lw=1.0)
    (cv,) = bx.plot([], [], color=C_D, lw=3.2)
    (dt,) = bx.plot([], [], "o", color=C_D, ms=8)
    bx.set_xscale("log")
    bx.set_xlim(0.55, 0.045)
    bx.set_xticks([0.5, 0.2, 0.1, 0.05])
    bx.set_xticklabels(["0.5", "0.2", "0.1", "0.05"])
    bx.minorticks_off()
    bx.set_ylim(0, max(dev.max(), r_pred) * 1.35)
    bx.set_xlabel("刻み幅 $\\varepsilon$（小さくなる →）", fontsize=12)
    bx.set_ylabel("ベクトルのずれ $/\\,\\varepsilon^2$", fontsize=12)
    bx.set_title("ずれ$/\\varepsilon^2$ は $\\varepsilon\\to0$ で 0 にならず、\n一定値（曲率）に近づく", fontsize=12.5)
    bx.axhline(dev[-1], color="k", lw=1.2, ls="--")
    bx.text(0.22, dev[-1] * 1.03, "$|R^l{}_{kij}V^k|$（ずれの極限）", fontsize=11, va="bottom", ha="center")

    fig.text(0.5, 0.955, "偏微分は交換するが、共変微分（並行移動）は交換しない", ha="center", fontsize=20, fontweight="bold")
    l1 = fig.text(0.5, 0.095, "", ha="center", fontsize=14.5)
    l2 = fig.text(0.5, 0.035, "", ha="center", fontsize=14.5)
    tmp = []
    n_frames, hold = 120, 40

    def update(f):
        for t in tmp:
            t.remove()
        tmp.clear()
        k = int(round(min(f, n_frames - hold - 1) / (n_frames - hold - 1) * (len(eps_list) - 1)))
        e = eps_list[k]
        vA, _ = loop(e, "ij", v0)
        vB, _ = loop(e, "ji", v0)
        vstart = unit_frame_xy(v0)
        L = 0.42
        # 出発点で: 運ぶベクトル（共通）
        tmp.append(ax.annotate("", xy=P0_ + L * vstart, xytext=P0_, arrowprops=dict(arrowstyle="-|>", color="#555", lw=3), zorder=4))
        # 到着点で: 2通りのベクトルと、そのずれ（ずれは Amp·ε² で拡大して、始点から赤い矢印で示す）
        a_xy, b_xy = unit_frame_xy(vA), unit_frame_xy(vB)
        # 実際のずれは ε² 程度でほぼ見えないので、「ずれ/ε²」を一定倍した大きさで、橙のベクトルを青からずらして描く。
        # （ε が小さくなっても拡大後のずれは変わらない＝ずれ ∝ ε² の意味。矢印は「ずれの向きと相対的な大きさ」を表す）
        d_xy = (b_xy - a_xy) / (e * e) * 0.22
        tip_a = P3_ + L * a_xy
        tip_b = tip_a + d_xy
        tmp.append(ax.annotate("", xy=tip_a, xytext=P3_, arrowprops=dict(arrowstyle="-|>", color=C_A, lw=3), zorder=4))
        tmp.append(ax.annotate("", xy=tip_b, xytext=P3_, arrowprops=dict(arrowstyle="-|>", color=C_B, lw=3), zorder=4))
        tmp.append(ax.annotate("", xy=tip_b, xytext=tip_a, arrowprops=dict(arrowstyle="-|>", color=C_D, lw=3.6), zorder=6))
        tmp.append(ax.text(P3_[0] + 0.30, P3_[1] + 0.30, "赤：ずれ（$\\varepsilon^2$ で割って\n拡大して表示）", color=C_D, fontsize=12, va="center"))
        cv.set_data(eps_list[: k + 1], dev[: k + 1])
        dt.set_data([e], [dev[k]])
        l1.set_text(f"座標の四角形（辺の長さ $\\varepsilon={e:.2f}$）を2通りの順に回って、同じベクトル $V$ を並行移動する。")
        l2.set_text("着く点は同じでも、ベクトルは $(\\nabla_i\\nabla_j-\\nabla_j\\nabla_i)V^l=R^l{}_{kij}V^k$ のぶんだけずれる（ずれ $\\propto\\varepsilon^2$）。")
        return []

    frames = list(range(0, n_frames, 2))
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    path = OUT / "anim03_holonomy_square.gif"
    ani.save(path, writer=animation.PillowWriter(fps=10), dpi=55)
    print(f"saved {path.name}: {path.stat().st_size / 1e6:.2f} MB, {len(frames)} frames @10fps")
    if mp4:
        ani2 = animation.FuncAnimation(fig, update, frames=list(range(n_frames)), blit=False)
        p2 = OUT / "anim03_holonomy_square.mp4"
        ani2.save(p2, writer=animation.FFMpegWriter(fps=30, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]), dpi=100)
        print(f"saved {p2.name}: {p2.stat().st_size / 1e6:.2f} MB")
    plt.close(fig)


# ================================================================== 共通: GIF 書き出し
def save_gif(fig, update, n_frames, stem, mp4=False, step=1):
    frames = list(range(0, n_frames, step))
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=False)
    path = OUT / f"{stem}.gif"
    ani.save(path, writer=animation.PillowWriter(fps=10), dpi=55)
    print(f"saved {path.name}: {path.stat().st_size / 1e6:.2f} MB, {len(frames)} frames @10fps")
    if mp4:
        ani2 = animation.FuncAnimation(fig, update, frames=list(range(n_frames)), blit=False)
        p2 = OUT / f"{stem}.mp4"
        ani2.save(p2, writer=animation.FFMpegWriter(fps=10, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "20"]), dpi=100)
        print(f"saved {p2.name}: {p2.stat().st_size / 1e6:.2f} MB")
    plt.close(fig)


# ================================================================== anim04: 極座標の基底ベクトルの変化と Γ
def anim04_polar_basis(mp4=False):
    """点を動かすと基底ベクトルが変わる。その変化率を基底で展開した係数が Γ（有限差分で数値的に求める）。"""
    def e_r(th):
        return np.array([np.cos(th), np.sin(th)])

    def e_th(r, th):
        return r * np.array([-np.sin(th), np.cos(th)])

    def sg(x):
        """表示用: 浮動小数点の誤差（±1e-9 など）で '+0.000' と '-0.000' がちらつかないよう、0 は符号なしの 0.000 にする"""
        return "0.000" if abs(x) < 5e-4 else f"{x:+.3f}"

    def coeffs(d, r, th):  # d = c^r e_r + c^θ e_θ を解く
        return np.linalg.solve(np.column_stack([e_r(th), e_th(r, th)]), d)

    h = 1e-6

    def gammas(r, th):
        d_th_eth = (e_th(r, th + h) - e_th(r, th - h)) / (2 * h)
        d_th_er = (e_r(th + h) - e_r(th - h)) / (2 * h)
        d_r_eth = (e_th(r + h, th) - e_th(r - h, th)) / (2 * h)
        return d_th_eth, d_th_er, d_r_eth, coeffs(d_th_eth, r, th), coeffs(d_th_er, r, th), coeffs(d_r_eth, r, th)

    for r, th in ((1.5, 0.4), (0.8, 1.9), (2.3, 3.0)):  # 本文 Part VI §1: Γ^r_θθ=-r, Γ^θ_rθ=1/r, Γ^θ_θθ=0, Γ^r_rθ=0
        _, _, _, c1, c2, c3 = gammas(r, th)
        assert np.allclose(c1, [-r, 0], atol=1e-6) and np.allclose(c2, [0, 1 / r], atol=1e-6) and np.allclose(c3, [0, 1 / r], atol=1e-6)
    print("[anim04] 有限差分で求めた係数が Γ^r_θθ=-r, Γ^θ_θθ=0, Γ^θ_rθ=1/r, Γ^r_rθ=0 に一致")

    C_R, C_T, C_D = "#1f77b4", "#d62728", "#2ca02c"
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="white")
    ax = fig.add_axes([0.03, 0.10, 0.55, 0.80])
    for rr in (0.5, 1.0, 1.5, 2.0, 2.5):
        a = np.linspace(0, np.pi, 200)
        ax.plot(rr * np.cos(a), rr * np.sin(a), color="#dde3ec", lw=0.8)
    for d in np.deg2rad(np.arange(0, 181, 20)):
        ax.plot([0, 2.6 * np.cos(d)], [0, 2.6 * np.sin(d)], color="#dde3ec", lw=0.8)
    ax.set_aspect("equal")
    ax.set_xlim(-1.5, 2.7)
    ax.set_ylim(-0.3, 2.9)
    ax.axis("off")
    ax.plot(0, 0, "ko", ms=4)
    title = fig.text(0.5, 0.955, "", ha="center", fontsize=20, fontweight="bold")
    t1 = fig.text(0.60, 0.78, "", fontsize=16)
    t2 = fig.text(0.60, 0.68, "", fontsize=16)
    t3 = fig.text(0.60, 0.58, "", fontsize=16)
    t4 = fig.text(0.60, 0.47, "", fontsize=13.5, color="#555", va="top")
    t5 = fig.text(0.60, 0.30, "", fontsize=13.5, color="#555", va="top")
    fig.text(0.04, 0.045, "■ 青：$\\mathbf{e}_r$（長さ 1）　■ 赤：$\\mathbf{e}_\\theta$（長さ $r$）　■ 緑：その点での基底ベクトルの変化率（長さ・向きは実際のもの）",
             fontsize=13, color="#333")
    s = 0.6
    n1, n2, hold = 44, 44, 8
    tmp = []

    def arrow(p, v, col, lw=3.0, z=4, alpha=1.0):
        tmp.append(ax.annotate("", xy=p + s * v, xytext=p, arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=alpha), zorder=z))

    def update(f):
        for t in tmp:
            t.remove()
        tmp.clear()
        if f < n1 + hold:  # 前半: θ を動かす（r 固定）
            r = 1.5
            k = min(f, n1 - 1) / (n1 - 1)
            th = np.deg2rad(20 + 100 * k)
            ghosts = np.deg2rad(20 + 100 * np.linspace(0, k, 6))
            for g in ghosts[:-1]:
                p = r * e_r(g)
                arrow(p, e_th(r, g), C_T, 1.6, 2, 0.25)
                arrow(p, e_r(g), C_R, 1.6, 2, 0.25)
            p = r * e_r(th)
            arrow(p, e_r(th), C_R)
            arrow(p, e_th(r, th), C_T)
            d1, d2, _, c1, c2, _ = gammas(r, th)
            tmp.append(ax.annotate("", xy=p + e_th(r, th) * s + s * d1, xytext=p + e_th(r, th) * s, arrowprops=dict(arrowstyle="-|>", color=C_D, lw=3.4), zorder=6))
            a = np.linspace(np.deg2rad(20), th, 60)
            tmp.append(ax.plot(r * np.cos(a), r * np.sin(a), color="#999", lw=1.2, ls="--")[0])
            title.set_text("$\\theta$ 方向に動かす：基底ベクトルは回る")
            t1.set_text(f"$\\partial_\\theta\\mathbf{{e}}_\\theta=\\Gamma^r{{}}_{{\\theta\\theta}}\\mathbf{{e}}_r+\\Gamma^\\theta{{}}_{{\\theta\\theta}}\\mathbf{{e}}_\\theta$")
            t2.set_text(f"$\\Gamma^r{{}}_{{\\theta\\theta}}={sg(c1[0])}\\ \\ (=-r=-{r:.2f})$")
            t3.set_text(f"$\\Gamma^\\theta{{}}_{{\\theta\\theta}}={sg(c1[1])}$")
            # 変わるもの（デカルト成分）と、変わらないもの（Γ）の対比
            t4.set_text(f"変わるもの：$\\partial_\\theta\\mathbf{{e}}_\\theta$ のデカルト成分\n$=({d1[0]:+.2f},\\ {d1[1]:+.2f})$（$\\theta={np.rad2deg(th):.0f}^\\circ$）")
            t5.set_text("変わらないもの：展開係数 $\\Gamma$\n（$\\theta$ によらず $r$ だけで決まる）")
        else:  # 後半: r を動かす（θ 固定）
            th = np.deg2rad(40)
            k = min(f - n1 - hold, n2 - 1) / (n2 - 1)
            r = 0.8 + 1.2 * k
            for rg in 0.8 + 1.2 * np.linspace(0, k, 6)[:-1]:
                p = rg * e_r(th)
                arrow(p, e_th(rg, th), C_T, 1.6, 2, 0.25)
                arrow(p, e_r(th), C_R, 1.6, 2, 0.25)
            p = r * e_r(th)
            arrow(p, e_r(th), C_R)
            arrow(p, e_th(r, th), C_T)
            _, _, d3, _, _, c3 = gammas(r, th)
            tmp.append(ax.annotate("", xy=p + e_th(r, th) * s + s * d3, xytext=p + e_th(r, th) * s, arrowprops=dict(arrowstyle="-|>", color=C_D, lw=3.4), zorder=6))
            tmp.append(ax.plot([0, 2.5 * np.cos(th)], [0, 2.5 * np.sin(th)], color="#999", lw=1.2, ls="--")[0])
            title.set_text("$r$ 方向に動かす：$\\mathbf{e}_\\theta$ の長さが変わる")
            t1.set_text("$\\partial_r\\mathbf{e}_\\theta=\\Gamma^r{}_{r\\theta}\\mathbf{e}_r+\\Gamma^\\theta{}_{r\\theta}\\mathbf{e}_\\theta$")
            t2.set_text(f"$\\Gamma^r{{}}_{{r\\theta}}={sg(c3[0])}$")
            t3.set_text(f"$\\Gamma^\\theta{{}}_{{r\\theta}}={sg(c3[1])}\\ \\ (=1/r={1 / r:.3f})$")
            t4.set_text("$\\mathbf{e}_\\theta$ は向きを変えず、$r$ に比例して\n長くなる（変化率は $\\mathbf{e}_\\theta/r$）")
            t5.set_text("下の添字は対称：\n$\\Gamma^\\theta{}_{r\\theta}=\\Gamma^\\theta{}_{\\theta r}$（前半の $\\partial_\\theta\\mathbf{e}_r$ と同じ値）")
        return []

    save_gif(fig, update, n1 + hold + n2 + hold, "anim04_polar_basis", mp4)


# ================================================================== anim05: δ による添字のすり替え
def anim05_delta(mp4=False):
    g = np.array([[2.0, 1.0, 0.0], [1.0, 3.0, 1.0], [0.0, 1.0, 2.0]])
    gi = np.linalg.inv(g)
    assert np.allclose(gi @ g, np.eye(3)), "g^{ik} g_{kj} = δ^i_j"
    V = np.array([5.0, 7.0, 9.0])
    assert np.allclose(np.eye(3) @ V, V)
    print("[anim05] g^{ik}g_{kj}=δ^i_j、δ^i_j V^j=V^i を数値で確認済み")

    CI, CJ, CK = "#1f77b4", "#2ca02c", "#d62728"
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="white")
    ax = fig.add_axes([0.02, 0.22, 0.96, 0.62])
    title = fig.text(0.5, 0.955, "", ha="center", fontsize=20, fontweight="bold")
    l1 = fig.text(0.5, 0.135, "", ha="center", fontsize=17)
    l2 = fig.text(0.5, 0.065, "", ha="center", fontsize=15, color="#555")

    def grid(x0, y0, M, label, rows=(), cols=(), cell=None, hide=False, fmt="{:.2f}", band=None):
        """3x3（または 3x1）の表。rows/cols を色帯で強調、cell=(i,j) を黄色で強調"""
        nr, nc = M.shape
        for i in range(nr):
            for j in range(nc):
                fc = "white"
                if i in rows:
                    fc = "#dbeafe"
                if j in cols:
                    fc = "#dcfce7" if i not in rows else "#d6f0e0"
                if cell == (i, j):
                    fc = "#fff0a0"
                ax.add_patch(Rectangle((x0 + j, y0 - i - 1), 1, 1, fc=fc, ec="#555", lw=1.4, zorder=1))
                if not (hide and cell != (i, j) and True):
                    pass
                ax.text(x0 + j + 0.5, y0 - i - 0.5, fmt.format(M[i, j]), ha="center", va="center", fontsize=16, zorder=3)
        ax.text(x0 + nc / 2, y0 + 0.35, label, ha="center", fontsize=18)

    n_cells, per = 9, 4
    n_rows, per2 = 3, 4
    holdA = 6
    nA = n_cells * per + holdA
    nB = n_rows * per2 + holdA

    def update(f):
        ax.clear()
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 6.2)
        ax.set_aspect("equal")
        ax.axis("off")
        if f < nA:
            title.set_text("計量 × 逆計量 $=\\delta$：和を取る $k$ が消え、$i,j$ が残る")
            idx = min(f // per, n_cells - 1)
            ph = f % per if f < n_cells * per else 3
            i, j = divmod(idx, 3)
            done = np.full((3, 3), np.nan)
            for q in range(idx + (1 if ph >= 3 else 0)):
                a, b = divmod(q, 3)
                done[a, b] = (gi @ g)[a, b]
            if f >= n_cells * per:
                done = gi @ g
            cur = (i, j) if f < n_cells * per else None
            # 左: g^{ik}（行 i を強調）, 中: g_{kj}（列 j を強調）, 右: 結果 δ^i_j
            grid(1.0, 5.2, gi, "$g^{ik}$", rows=(i,) if cur else ())
            grid(6.0, 5.2, g, "$g_{kj}$", cols=(j,) if cur else ())
            ax.text(5.0, 3.7, "×", fontsize=26, ha="center", va="center")
            ax.text(10.2, 3.7, "＝", fontsize=26, ha="center", va="center")
            for a in range(3):
                for b in range(3):
                    fc = "#fff0a0" if cur == (a, b) else "white"
                    ax.add_patch(Rectangle((11.0 + b, 5.2 - a - 1), 1, 1, fc=fc, ec="#555", lw=1.4, zorder=1))
                    if not np.isnan(done[a, b]):
                        ax.text(11.0 + b + 0.5, 5.2 - a - 0.5, f"{done[a, b]:.0f}", ha="center", va="center", fontsize=18, fontweight="bold", zorder=3)
            ax.text(12.5, 5.55, "$\\delta^i{}_j$", ha="center", fontsize=18)
            if cur:
                terms = [gi[i, k] * g[k, j] for k in range(3)]
                if ph == 0:
                    l1.set_text(f"$(i,j)=({i + 1},{j + 1})$：$g^{{ik}}$ の第 {i + 1} 行（青）と $g_{{kj}}$ の第 {j + 1} 列（緑）を、$k$ について足す")
                else:
                    l1.set_text(f"$\\sum_k g^{{{i + 1}k}}g_{{k{j + 1}}}=" + "+".join(f"({gi[i, k]:.2f})({g[k, j]:.0f})" for k in range(3)) + f"={sum(terms):.0f}$")
                l2.set_text("$k$ は上下でペアになって和の中に消え、残った $i$（上）と $j$（下）が $\\delta^i{}_j$ の添字になる"
                            + ("" if ph < 2 else f"　→ {'$i=j$ なので 1' if i == j else '$i\\neq j$ なので 0'}"))
            else:
                l1.set_text("結果は単位行列：$g^{ik}g_{kj}=\\delta^i{}_j$（対角は 1、それ以外は 0）")
                l2.set_text("$\\delta^i{}_j$ は「$i=j$ のときだけ 1」。次は、これを掛けると添字がすり替わる様子を見る")
        else:
            title.set_text("$\\delta$ は添字のすり替え：$\\delta^i{}_jV^j=V^i$")
            f2 = f - nA
            idx = min(f2 // per2, n_rows - 1)
            ph = f2 % per2 if f2 < n_rows * per2 else 3
            i = idx
            done = np.full(3, np.nan)
            for q in range(idx + (1 if ph >= 3 else 0)):
                done[q] = V[q]
            if f2 >= n_rows * per2:
                done = V.copy()
            cur = i if f2 < n_rows * per2 else None
            I3 = np.eye(3)
            grid(1.0, 5.2, I3, "$\\delta^i{}_j$", rows=(cur,) if cur is not None else (), fmt="{:.0f}")
            grid(6.0, 5.2, V.reshape(3, 1), "$V^j$", fmt="{:.0f}")
            ax.text(5.0, 3.7, "×", fontsize=26, ha="center", va="center")
            ax.text(8.2, 3.7, "＝", fontsize=26, ha="center", va="center")
            for a in range(3):
                fc = "#fff0a0" if cur == a else "white"
                ax.add_patch(Rectangle((9.0, 5.2 - a - 1), 1, 1, fc=fc, ec="#555", lw=1.4, zorder=1))
                if not np.isnan(done[a]):
                    ax.text(9.5, 5.2 - a - 0.5, f"{done[a]:.0f}", ha="center", va="center", fontsize=18, fontweight="bold", zorder=3)
            ax.text(9.5, 5.55, "$V^i$", ha="center", fontsize=18)
            if cur is not None:
                ax.add_patch(Rectangle((6.0, 5.2 - cur - 1), 1, 1, fc="#fde68a", ec="#d97706", lw=3, zorder=2))
                ax.text(6.5, 5.2 - cur - 0.5, f"{V[cur]:.0f}", ha="center", va="center", fontsize=16, zorder=4)
                if ph == 0:
                    l1.set_text(f"$i={cur + 1}$：$\\delta^{{{cur + 1}}}{{}}_jV^j$ を $j$ について足す（行 {cur + 1}）")
                else:
                    l1.set_text(f"$\\delta^{{{cur + 1}}}{{}}_1V^1+\\delta^{{{cur + 1}}}{{}}_2V^2+\\delta^{{{cur + 1}}}{{}}_3V^3=" +
                                "+".join(f"{int(I3[cur, j])}\\cdot{V[j]:.0f}" for j in range(3)) + f"={V[cur]:.0f}=V^{{{cur + 1}}}$")
                l2.set_text("$j=i$ の項だけが生き残る（橙の枠）。上付きの $j$ が $i$ にすり替わった")
            else:
                l1.set_text("$\\delta^i{}_jV^j=V^i$：$\\delta$ を掛けて和を取ると、$V$ はそのまま、添字だけが $j\\to i$ に付け替わる")
                l2.set_text("下付きに使えば $\\delta^i{}_jV_i=V_j$（$i\\to j$）。計量による添字の上げ下げも、この仕組み")
        return []

    save_gif(fig, update, nA + nB, "anim05_delta_substitution", mp4)


# ================================================================== anim06: ガウス正規座標（付録 C）
def anim06_gaussian_normal(mp4=False):
    """平坦な (y,t) 時空（計量 dy²-dt²）で、曲がった断面 Σ: t=0.4y² から法線方向に測地線を伸ばす。隣の測地線との間隔 g(τ) が広がる。"""
    c2 = 0.4

    def X(y):
        return np.array([y, c2 * y * y])

    def n(y):  # Σ に「垂直」（ローレンツ計量）な、未来向きの単位ベクトル
        s = 2 * c2 * y
        return np.array([s, 1.0]) / np.sqrt(1 - s * s)

    def eta(u, v):
        return u[0] * v[0] - u[1] * v[1]

    def point(y, tau):
        return X(y) + tau * n(y)

    h = 1e-5

    def g_of(y, tau):  # 誘導計量 g(τ) = ḡ(∂_y point, ∂_y point)
        d = (point(y + h, tau) - point(y - h, tau)) / (2 * h)
        return eta(d, d)

    for y in (0.0, 0.5, -0.7):
        Xpp = np.array([0.0, 2 * c2])
        nn = n(y)
        assert abs(eta(nn, nn) + 1) < 1e-12 and abs(eta((X(y + h) - X(y - h)) / (2 * h), nn)) < 1e-6
        Kij = eta((X(y + h) - 2 * X(y) + X(y - h)) / h**2, nn)  # K_ij = ḡ(X'', n)（C-1-4 と同じ定義）
        dg = (g_of(y, 1e-3) - g_of(y, -1e-3)) / 2e-3
        assert abs(dg - (-2 * Kij)) < 1e-4, f"∂τ g = -2K のはず: {dg} vs {-2 * Kij}"
    print(f"[anim06] K_ij = ḡ(X'',n) = {Kij:+.4f}（y=-0.7）、∂τ g = -2K を数値で確認。y=0 では K=-0.8, ∂τ g=+1.6")

    C_B, C_K = "#2563a8", "#d62728"
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor="white")
    ax = fig.add_axes([0.03, 0.14, 0.52, 0.72])
    bx = fig.add_axes([0.66, 0.27, 0.31, 0.45])
    ys = np.linspace(-1.1, 1.1, 300)
    ax.plot(*np.array([X(y) for y in ys]).T, color="k", lw=3.2)
    ax.text(1.05, c2 * 1.1**2 + 0.05, "$\\Sigma\\ (\\tau=0)$", fontsize=14)
    ax.set_xlim(-1.6, 1.9)
    ax.set_ylim(-0.25, 1.95)
    ax.set_aspect("equal")
    ax.set_xlabel("空間 $y$")
    ax.set_ylabel("時間 $t$")
    taus = np.linspace(0, 1.0, 60)
    gs = np.array([g_of(0.0, t) for t in taus])
    bx.plot(taus, gs, color="#bbb", lw=1.4)
    bx.axhline(1, color="#888", lw=1, ls=":")
    bx.plot(taus, 1 + 1.6 * taus, color="k", lw=1.3, ls="--")
    bx.text(0.55, 1 + 1.6 * 0.55 - 0.18, "接線：傾き $-2K=+1.6$", fontsize=11.5, ha="left")
    (curve,) = bx.plot([], [], color=C_K, lw=3.4)
    (dot,) = bx.plot([], [], "o", color=C_K, ms=8)
    bx.set_xlim(0, 1.0)
    bx.set_ylim(0.8, gs.max() * 1.1)
    bx.set_xlabel("$\\tau$（法線方向に進んだ固有時間）", fontsize=12)
    bx.set_ylabel("$g(\\tau)$（隣り合う測地線の間隔$^2$）", fontsize=12)
    bx.set_title("間隔が広がる：$\\partial_\\tau g>0$\n$\\Rightarrow K_{ij}=-\\frac{1}{2}\\partial_\\tau g_{ij}<0$", fontsize=12.5)
    title = fig.text(0.5, 0.955, "ガウス正規座標：断面から法線方向に測地線を伸ばす", ha="center", fontsize=20, fontweight="bold")
    l1 = fig.text(0.5, 0.075, "", ha="center", fontsize=15)
    tmp = []
    n_frames, hold = 70, 20
    y_list = np.linspace(-1.0, 1.0, 11)

    def update(f):
        for t in tmp:
            t.remove()
        tmp.clear()
        k = min(f, n_frames - hold - 1) / (n_frames - hold - 1)
        tau = k * 1.0
        for y in y_list:
            a, b = point(y, 0), point(y, tau)
            tmp.append(ax.plot([a[0], b[0]], [a[1], b[1]], color=C_B, lw=1.4, alpha=0.8)[0])
        sl = np.array([point(y, tau) for y in ys])
        tmp.append(ax.plot(sl[:, 0], sl[:, 1], color=C_B, lw=3.0)[0])
        lab = point(0.7, tau)
        tmp.append(ax.text(lab[0] + 0.1, lab[1] - 0.05, f"$\\Sigma_\\tau\\ (\\tau={tau:.2f})$", color=C_B, fontsize=13, ha="left", va="top"))
        y1, y2 = -0.12, 0.12  # 近くの2本の測地線の間隔を矢印で示す
        for yy, col in ((y1, C_K), (y2, C_K)):
            tmp.append(ax.plot(*point(yy, tau), "o", color=C_K, ms=5, zorder=5)[0])
        p1, p2 = point(y1, tau), point(y2, tau)
        tmp.append(ax.annotate("", xy=p2 + [0, 0.07], xytext=p1 + [0, 0.07], arrowprops=dict(arrowstyle="<->", color=C_K, lw=2.2), zorder=6))
        a1, a2 = point(y1, 0), point(y2, 0)
        tmp.append(ax.annotate("", xy=a2 + [0, -0.09], xytext=a1 + [0, -0.09], arrowprops=dict(arrowstyle="<->", color="#444", lw=1.8), zorder=6))
        i = int(round(k * (len(taus) - 1)))
        curve.set_data(taus[: i + 1], gs[: i + 1])
        dot.set_data([taus[i]], [gs[i]])
        l1.set_text("断面ごとの法線方向の測地線（青）は、時間 $\\tau$ とともに間隔が広がる。赤の矢印は隣り合う2本の間隔（$\\tau=0$ の黒より広い）")
        return []

    save_gif(fig, update, n_frames, "anim06_gaussian_normal", mp4)


ANIMS = {"anim01": anim01_parallel_transport, "anim02": anim02_mixed_partials, "anim03": anim03_holonomy, "anim04": anim04_polar_basis, "anim05": anim05_delta, "anim06": anim06_gaussian_normal}


def main():
    import argparse

    ap = argparse.ArgumentParser(description="研究ノート用のアニメーション（GIF）を生成する")
    ap.add_argument("names", nargs="*", choices=[*ANIMS, []][:-1] or None, help="生成する名前（省略すると全部）")
    ap.add_argument("--mp4", action="store_true", help="GIF に加えて MP4 も書き出す（ffmpeg が必要）")
    args = ap.parse_args()
    for name in args.names or list(ANIMS):
        ANIMS[name](mp4=args.mp4)


if __name__ == "__main__":
    main()
