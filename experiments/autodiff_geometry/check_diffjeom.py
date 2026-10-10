"""diffjeom（JAX で書かれた小さな微分幾何ライブラリ）が、自作の christoffel_from_metric と同じ値を返すかを確かめる。

diffjeom は計量の関数 g(x) だけから、クリストッフェル記号・リーマン曲率・リッチ曲率を自動微分（jacfwd）で作る。
添字の並びは Gamma[i, j, k] = Γ^i_{jk}（上付きが先頭）で、自作の関数と同じ。

diffjeom はプロジェクトの依存に入れていないので、一時的に足して実行する:
    uv run --with diffjeom python experiments/autodiff_geometry/check_diffjeom.py
"""

import sys
from pathlib import Path

import diffjeom as dj
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import autodiff_geometry as ag  # noqa: E402


def sphere_metric(p):
    return jnp.diag(jnp.array([1.0, jnp.sin(p[0]) ** 2]))


def main():
    q = jnp.array([ag.R0, ag.TH0])
    ours = ag.christoffel_from_metric(ag.metric_polar, q)
    theirs = np.asarray(dj.get_christoffel2(q, ag.metric_polar))
    print("極座標：自作と diffjeom の Γ の最大差", np.abs(ours - theirs).max())
    assert np.allclose(ours, theirs, atol=1e-12)
    print("  Γ^r_θθ =", theirs[0, 1, 1], "（-r =", -ag.R0, "）  Γ^θ_rθ =", theirs[1, 0, 1], "（1/r =", 1 / ag.R0, "）")

    riem = np.asarray(dj.get_riemann(q, ag.metric_polar))
    ricci_scalar = float(dj.get_ricci_scalar(q, ag.metric_polar))
    print("極座標：Γ は 0 でないが、リーマン曲率は 0（平坦）。max|R| =", np.abs(riem).max(), " スカラー曲率 =", ricci_scalar)
    assert np.allclose(riem, 0.0, atol=1e-10) and abs(ricci_scalar) < 1e-10

    p = jnp.array([0.9, 0.4])
    gamma_s = np.asarray(dj.get_christoffel2(p, sphere_metric))
    assert np.isclose(gamma_s[0, 1, 1], -np.sin(0.9) * np.cos(0.9))  # Γ^θ_φφ
    assert np.isclose(gamma_s[1, 0, 1], 1 / np.tan(0.9))  # Γ^φ_θφ
    riem_s = np.asarray(dj.get_riemann(p, sphere_metric))
    scalar_s = float(dj.get_ricci_scalar(p, sphere_metric))
    print("単位球面：R^θ_{φθφ} =", riem_s[0, 1, 0, 1], "（sin²θ =", np.sin(0.9) ** 2, "）  スカラー曲率 =", scalar_s, "（2）")
    assert np.isclose(riem_s[0, 1, 0, 1], np.sin(0.9) ** 2) and np.isclose(scalar_s, 2.0)
    print("すべて一致")


if __name__ == "__main__":
    main()
