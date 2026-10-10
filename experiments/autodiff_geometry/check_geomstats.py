"""geomstats（リーマン幾何の Python ライブラリ）の PullbackMetric が、はめ込み写像から計量 g=J^T J を自動微分で作り、
クリストッフェル記号と曲率を返すことを、極座標の平面と単位球面で確かめる。

geomstats 2.8.0 は NumPy 2 では import できない（`numpy.trapz` が NumPy 2.0 で削除されたため）。
プロジェクトの環境（NumPy 2.5）とは別に、NumPy 1.x の一時環境で実行する:
    uv run --no-project --python 3.12 --with geomstats --with autograd --with "numpy<2" \
        python experiments/autodiff_geometry/check_geomstats.py
バックエンドは autograd を使う（メタデータ上、backends の extras は autograd と pytorch。TensorFlow は test-scripts だけ）。
"""

import os

os.environ.setdefault("GEOMSTATS_BACKEND", "autograd")

import geomstats.backend as gs
import numpy as np
from geomstats.geometry.base import ImmersedSet
from geomstats.geometry.euclidean import Euclidean


class PolarPlane(ImmersedSet):
    """極座標 (r, θ) の平面。デカルト座標 (x, y) へのはめ込みで、計量は J^T J。"""

    def __init__(self):
        super().__init__(dim=2)

    def _define_embedding_space(self):
        return Euclidean(dim=2)

    def immersion(self, point):
        r, th = point[..., 0], point[..., 1]
        return gs.stack([r * gs.cos(th), r * gs.sin(th)], axis=-1)


class UnitSphereChart(ImmersedSet):
    """単位球面の座標 (θ, φ)。R^3 へのはめ込み。"""

    def __init__(self):
        super().__init__(dim=2)

    def _define_embedding_space(self):
        return Euclidean(dim=3)

    def immersion(self, point):
        th, ph = point[..., 0], point[..., 1]
        return gs.stack([gs.sin(th) * gs.cos(ph), gs.sin(th) * gs.sin(ph), gs.cos(th)], axis=-1)


def main():
    print("backend:", gs.__name__)
    polar = PolarPlane()
    r0, th0 = 2.0, 0.7
    q = gs.array([r0, th0])
    g = np.asarray(polar.metric.metric_matrix(q))
    gam = np.asarray(polar.metric.christoffels(q))
    scal = float(np.asarray(polar.metric.scalar_curvature(q)))
    print("極座標 g =", g.tolist(), " Γ^r_θθ =", gam[0, 1, 1], " Γ^θ_rθ =", gam[1, 0, 1], " スカラー曲率 =", scal)
    assert np.allclose(g, np.diag([1.0, r0**2]))
    assert np.isclose(gam[0, 1, 1], -r0) and np.isclose(gam[1, 0, 1], 1 / r0)
    assert abs(scal) < 1e-10  # Γ は 0 でないが平坦

    sph = UnitSphereChart()
    th, ph = 0.9, 0.4
    p = gs.array([th, ph])
    gs_ = np.asarray(sph.metric.christoffels(p))
    scal_s = float(np.asarray(sph.metric.scalar_curvature(p)))
    ricci = np.asarray(sph.metric.ricci_tensor(p))
    print("単位球面 Γ^θ_φφ =", gs_[0, 1, 1], " Γ^φ_θφ =", gs_[1, 0, 1], " スカラー曲率 =", scal_s)
    assert np.isclose(gs_[0, 1, 1], -np.sin(th) * np.cos(th)) and np.isclose(gs_[1, 0, 1], 1 / np.tan(th))
    assert np.isclose(scal_s, 2.0)
    assert np.allclose(ricci, np.diag([1.0, np.sin(th) ** 2]), atol=1e-12)  # 単位球面では Ric = g
    print("すべて一致")


if __name__ == "__main__":
    main()
