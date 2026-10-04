"""実機の <Z_0>（1次と2次、N=2）を、1組のパラメータで同時に説明できる雑音モデルを探す（重みつき最小二乗、χ²）。

試すモデル（どれも、密度行列で各ステップのユニタリの後に2量子ビット脱分極 p を入れる）：
  (0) 脱分極だけ：p を当てはめる
  (1) 回転角のずれ：ZZ の角度を (1+ε) 倍、横磁場の角度を (1+η) 倍（ε, η, p を当てはめる）
  (2) 量子ビットごとの余分な Z 回転：1ステップごとに e^{-i(ζ0 Z_0 + ζ1 Z_1)}（周波数のずれ・ZZ クロストークの近似。ζ0, ζ1, p）
χ² は、28点（1次と2次、n = 1〜14）の (モデル - 実機)² / (統計誤差)² の和。点の数と同じくらいなら、統計誤差の範囲で合っている。

実行（リポジトリのルートから）:
    uv run python experiments/a5_trotter_noise/noise_model_fits.py results/hardware_main_o1_….csv results/hardware_main_o2_….csv
出力: results/noise_model_fits_N2.csv
"""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trotter_noise as tn  # noqa: E402

HERE = Path(__file__).resolve().parent
N, T = 2, 2.0
A, B = tn.tfim_parts(N)
Z0, Z1 = tn.op_on(tn.Z, 0, N), tn.op_on(tn.Z, 1, N)
PSI0 = np.eye(4, dtype=complex)[0]


def z_model(order: int, n: int, p: float, eps: float = 0.0, eta: float = 0.0, z0: float = 0.0, z1: float = 0.0) -> float:
    d = T / n
    Ae, Be = A * (1 + eps), B * (1 + eta)
    D = expm(-1j * (z0 * Z0 + z1 * Z1))
    if order == 1:
        U = expm(-1j * Be * d) @ D @ expm(-1j * Ae * d)
    else:
        half = expm(-1j * Be * d / 2)
        U = half @ D @ expm(-1j * Ae * d) @ half
    rho = np.outer(PSI0, PSI0.conj())
    for _ in range(n):
        rho = tn.noisy_step(rho, U, p, N)
    return float(np.real(np.trace(Z0 @ rho)))


def main() -> None:
    hw = {}
    for path in sys.argv[1:]:
        rows = list(csv.DictReader(Path(path).open(encoding="utf-8")))
        order = 1 if "_o1_" in Path(path).name else 2
        hw[order] = [(int(float(r["n_steps"])), float(r["z_readout_corrected"]), float(r["z_sem"])) for r in rows]

    def chi2(**kw) -> float:
        return sum(((z_model(o, n, **kw) - z) / s) ** 2 for o in hw for n, z, s in hw[o])

    results = []
    c, p = min((chi2(p=p), p) for p in np.linspace(0.0005, 0.03, 60))
    results.append({"model": "脱分極だけ", "chi2": c, "p": p})
    c, e, h, p = min((chi2(p=p, eps=e, eta=h), e, h, p) for e, h, p in
                     itertools.product(np.linspace(-0.12, 0.12, 25), np.linspace(-0.06, 0.06, 13), (0.0015, 0.003, 0.006)))
    results.append({"model": "回転角のずれ（ZZ と横磁場）", "chi2": c, "p": p, "eps_zz": e, "eta_x": h})
    g = np.linspace(-0.08, 0.08, 33)
    c, a, b, p = min((chi2(p=p, z0=a, z1=b), a, b, p) for a in g for b in g for p in (0.0015, 0.003, 0.006))
    results.append({"model": "量子ビットごとの余分な Z 回転", "chi2": c, "p": p, "zeta0": a, "zeta1": b})
    npts = sum(len(v) for v in hw.values())
    for r in results:
        r["n_points"] = npts
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    out = HERE / "results" / "noise_model_fits_N2.csv"
    keys = ["model", "chi2", "n_points", "p", "eps_zz", "eta_x", "zeta0", "zeta1"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(results)
    print(f"書き出し: {out}")


if __name__ == "__main__":
    main()
