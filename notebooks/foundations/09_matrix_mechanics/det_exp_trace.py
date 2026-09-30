# det(e^A) = e^(tr A) の検証
# 対応ノート: 研究ノート/det_exp_trace_proof.md
# 証明1（対角化できる場合）を式番号通りに追う

import numpy as np
from sympy import (
    Matrix, symbols, exp, det, trace,
    diag, eye, simplify, pprint, latex
)

# ============================================================
# 数値検証（NumPy）
# ============================================================

def verify_numerically(A_np: np.ndarray) -> dict:
    """
    det(e^A) = e^(tr A) を数値的に検証する。

    Parameters
    ----------
    A_np : np.ndarray
        正方行列

    Returns
    -------
    dict : lhs, rhs, 一致するか
    """
    from scipy.linalg import expm
    exp_A = expm(A_np)
    lhs = np.linalg.det(exp_A)         # det(e^A)
    rhs = np.exp(np.trace(A_np))       # e^(tr A)
    return {
        "det(exp(A))": lhs,
        "exp(tr(A))": rhs,
        "match": np.isclose(lhs, rhs),
    }


# ============================================================
# 記号検証（SymPy）：証明1を式番号通りに追う
# ============================================================

def matrix_is_zero(M: Matrix) -> bool:
    """行列の全成分が記号的にゼロかを確認する。"""
    return all(simplify(M[i, j]) == 0
               for i in range(M.shape[0])
               for j in range(M.shape[1]))


def proof1_step_by_step(A: Matrix) -> dict:
    """
    証明1（対角化できる場合）を式番号通りに実行する。

    式1  : A = P Λ P^{-1}
    式2  : Pe^X P^{-1} = e^{PXP^{-1}}  （相似変換を指数に通す）
    式3-4: e^A = Pe^Λ P^{-1}
    式5-8: det(e^A) = det(e^Λ)          （det(P)det(P^{-1})=1 で消去）
    式9-12: e^Λ = diag(e^λ1, ..., e^λn)
    式13-14: det(e^Λ) = e^(Σλi)
    式15-20: Σλi = tr(Λ) = tr(A)
    """
    from sympy import nsimplify, trigsimp

    results = {}
    n = A.shape[0]

    # --- 式1: A = P Λ P^{-1} ---
    P, Lambda = A.diagonalize()
    P_inv = P.inv()
    diff1 = A - P * Lambda * P_inv
    results["式1: A == P Λ P^{-1}"] = matrix_is_zero(diff1)

    # --- 式3-4: e^A = Pe^Λ P^{-1} ---
    # 対角行列なので成分ごとに exp を適用（式9-12）
    eigenvalues = [Lambda[i, i] for i in range(n)]
    exp_Lambda = diag(*[exp(lam) for lam in eigenvalues])
    exp_A_via_similarity = P * exp_Lambda * P_inv
    exp_A_direct = A.exp()
    diff4 = exp_A_via_similarity - exp_A_direct
    results["式4: Pe^Λ P^{-1} == e^A"] = matrix_is_zero(diff4)

    # --- 式5-8: det(P)det(P^{-1}) = 1 で消去 ---
    det_P = det(P)
    det_P_inv = det(P_inv)
    results["式7: det(P)det(P^{-1}) == 1"] = simplify(det_P * det_P_inv - 1) == 0

    # --- 式12: e^Λ は対角行列 ---
    # diag で作っているので定義上 True
    results["式12: e^Λ は対角"] = exp_Lambda == diag(*[exp_Lambda[i, i] for i in range(n)])

    # --- 式13-14: det(e^Λ) = e^(Σλi) ---
    det_exp_Lambda = det(exp_Lambda)           # 対角成分の積
    rhs_lambda = exp(sum(eigenvalues))
    results["式14: det(e^Λ) == e^(Σλi)"] = simplify(det_exp_Lambda - rhs_lambda) == 0

    # --- 式17-20: Σλi = tr(Λ) = tr(A) ---
    tr_Lambda = trace(Lambda)
    tr_A = trace(A)
    results["式20: tr(Λ) == tr(A)"] = simplify(tr_Lambda - tr_A) == 0

    # --- 最終: det(e^A) = e^(tr A) ---
    lhs = det(exp_A_direct)
    rhs = exp(tr_A)
    results["結論: det(e^A) == e^(tr A)"] = simplify(lhs - rhs) == 0

    return results


# ============================================================
# 実行例
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("証明1 記号検証（SymPy）")
    print("=" * 60)

    # 2×2 の対角化可能な行列
    A_sym = Matrix([[2, 1],
                    [0, 3]])
    print("\nA =")
    pprint(A_sym)

    results = proof1_step_by_step(A_sym)
    for label, ok in results.items():
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {label}")

    print()
    print("=" * 60)
    print("数値検証（NumPy + SciPy）")
    print("=" * 60)

    # 同じ行列を NumPy で
    A_np = np.array([[2, 1],
                     [0, 3]], dtype=float)
    r = verify_numerically(A_np)
    print(f"\n  det(exp(A)) = {r['det(exp(A))']:.10f}")
    print(f"  exp(tr(A))  = {r['exp(tr(A))']:.10f}")
    print(f"  一致        : {r['match']}")

    print()
    print("=" * 60)
    print("3×3 の対角化可能な行列でも検証")
    print("=" * 60)

    A_3 = Matrix([[1, 2, 0],
                  [0, 3, 1],
                  [0, 0, 2]])
    print("\nA =")
    pprint(A_3)
    results_3 = proof1_step_by_step(A_3)
    for label, ok in results_3.items():
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {label}")
