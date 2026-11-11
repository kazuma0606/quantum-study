# Aaronson–Ambainis 予想の論文を読むノートの検算

> **作成** 2026-11-11　**更新** 2026-11-11
> 研究ノート「09_論文読解/aaronson_ambainis/」の、式と数値例を確かめるスクリプトとテスト。ノート1（離散立方体上の関数と多項式）の 168 件。

ノート [01_functions_on_discrete_cube.md](../../研究ノート/09_論文読解/aaronson_ambainis/01_functions_on_discrete_cube.md) の、番号つきの式と数値例を確かめます。

```bash
uv run python experiments/aaronson_ambainis/verify_note1.py   # 検査ごとに「一致」「不一致」を表示する
uv run pytest experiments/aaronson_ambainis -q                # 不一致が 0 件であることを確かめる
```

| ファイル | 内容 |
|---|---|
| `verify_note1.py` | ノート1 の検算（168 件）。一般の式は、$n=0$〜$4$ のすべての点と部分集合、乱数の関数で、分数のまま確かめる。数値例は、本文に書いた値と照らす |
| `tests/test_verify_note1.py` | `verify_note1.py` を実行し、不一致が 0 件であることを確かめる |

確かめている式は、ノートの (II-5)、(II-8)、(II-11)〜(II-13)、(III-2)〜(III-6)、(III-8)〜(III-10)、(IV-3)〜(IV-5)、(V-2)〜(V-5) です。論文の PDF は読みません。
