# Aaronson–Ambainis 予想の論文を読むノートの検算

> **作成** 2026-11-11　**更新** 2026-11-12
> 研究ノート「09_論文読解/aaronson_ambainis/」の、式と数値例を確かめるスクリプトとテスト。ノート1（離散立方体上の関数と多項式）の 168 件、ノート2（受理確率は多項式になる）の 119 件、ノート3（予想から古典アルゴリズムへ）の 54 件。

ノート [01_functions_on_discrete_cube.md](../../研究ノート/09_論文読解/aaronson_ambainis/01_functions_on_discrete_cube.md)、[02_acceptance_probability_polynomial.md](../../研究ノート/09_論文読解/aaronson_ambainis/02_acceptance_probability_polynomial.md)、[03_conjecture_to_classical_algorithm.md](../../研究ノート/09_論文読解/aaronson_ambainis/03_conjecture_to_classical_algorithm.md) の、番号つきの式と数値例を確かめます。

```bash
uv run python experiments/aaronson_ambainis/verify_note1.py   # 検査ごとに「一致」「不一致」を表示する
uv run python experiments/aaronson_ambainis/verify_note2.py
uv run python experiments/aaronson_ambainis/verify_note3.py
uv run pytest experiments/aaronson_ambainis -q                # 不一致が 0 件であることを確かめる
```

| ファイル | 内容 |
|---|---|
| `verify_note1.py` | ノート1 の検算（168 件）。一般の式は、$n=0$〜$4$ のすべての点と部分集合、乱数の関数で、分数のまま確かめる。数値例は、本文に書いた値と照らす |
| `tests/test_verify_note1.py` | `verify_note1.py` を実行し、不一致が 0 件であることを確かめる |
| `verify_note2.py` | ノート2 の検算（119 件）。一般の主張は、$N=1$〜$3$、作業レジスタの次元 $W=1,2$、クエリの回数 $T=0$〜$3$ で、乱数のユニタリ行列と初期状態を作り、すべての入力 $X$ で、ノートの式で作った多項式の値と、行列の積で求めた振幅・受理確率を比べる。数値例は、本文に書いた値と照らす |
| `tests/test_verify_note2.py` | `verify_note2.py` を実行し、不一致が 0 件であることを確かめる |
| `verify_note3.py` | ノート3 の検算（54 件）。一般の主張は、$N=1$〜$4$ のすべての点で、乱数の分数係数の多項式（値を $[0,1]$ に収めたもの）を作って確かめる。アルゴリズム $C$ を実際に走らせ、総影響力の減り方の式、クエリの回数の平均、止まらない入力と誤差が $\varepsilon$ を超える入力の割合を、分数のまま確かめる。数値例は、本文に書いた値と照らす |
| `tests/test_verify_note3.py` | `verify_note3.py` を実行し、不一致が 0 件であることを確かめる |

確かめている式は、ノート1 では (II-5)、(II-8)、(II-11)〜(II-13)、(III-2)〜(III-6)、(III-8)〜(III-10)、(IV-3)〜(IV-5)、(V-2)〜(V-5)、ノート2 では (II-3)、(II-4) の $O_X$ のユニタリ性、(III-1)〜(III-4)、(IV-1)〜(IV-3)、(V-1)、ノート3 では (II-2)、(II-4)、(II-6)〜(II-8)、(II-10)、(III-1)〜(III-4)、(IV-3)〜(IV-7) です（(IV-1) は論文の主張を仮定として使う式なので、小さい例で成り立つことを参考に確かめるだけです）。論文の PDF は読みません。
