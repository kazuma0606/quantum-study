---
name: note-figures
description: 研究ノート用の図（matplotlib の PNG）を作るときの手順と約束事。図のスクリプトの置き場所と書き方、本文の式との assert による照合、日本語フォントと mathtext の落とし穴、画像での確認を含む。ノートに図を追加・修正するときに使う。
---

# ノート用の図の作り方

## 置き場所と命名

- スクリプト：ノートと同じフォルダの `figures/make_<主題>_figures.py`。図ごとに関数（`ps01()` など）を作り、`FIGS = {"ps01": ps01, ...}` と引数で1つだけ作れるようにする。
- 画像：`figures/<接頭辞><番号>_<内容>.png`（例 `mexp03_bch_orders.png`）。接頭辞はノートごとに決める（既存：flm, ps, mexp, det, pauli, nf, dz, lb, mani など。重ならないように）。
- スクリプトの docstring に、実行方法と「出力ファイル名・どの Part の図か・何を描くか」の一覧を書く。

## 雛形

```python
OUT = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Yu Gothic", "Meiryo", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "cm"
C_A, C_B, C_BAD, C_GRAY, C_C = "#1f77b4", "#e67e00", "#d62728", "#888888", "#2ca02c"
...
fig.savefig(OUT / "xx01_name.png", dpi=150)
```

## 本文との照合（必須）

- 描く値が本文の式と一致することを、保存の前に `assert` で確かめる（例：傾きが 2、級数の和が式と一致、行列式が積と一致、ヒストグラムと公式の差が許容範囲）。コメントに本文の式番号を書く（`# 式 (III-7)`）。
- 許容値は、実際に計算して確かめてから決める。統計的な比較（ヒストグラム）は、範囲外のサンプルも含めた全体で正規化する。
- 本文にも、図の値（最大誤差、傾きなど）を「スクリプトで確認」と書ける形で使う。

## mathtext・文字列の落とし穴

- `\frac12` は使えない → `\frac{1}{2}`。`\dfrac` も不可 → `\frac`。
- `\ge` は不可 → `\geq`。
- `\mathbf z` のように波かっこなしは不可 → `\mathbf{z}`。
- Python の通常の文字列では `\t`（タブ）、`\n` などに注意 → `"\\times"` のように二重にするか、raw 文字列を使う。
- 凡例・タイトルの日本語と数式の混在は可。長すぎるタイトルは2行に。

## 確認

- 生成したら、**必ず Read ツールで画像を見て**、文字の重なり、凡例が線に重なっていないか、軸の目盛りの混雑を確認し、直す。
- 3D の図は目盛りを `[-1, 0, 1]` などに減らす。
- `__pycache__` ができたら消す（スクリプトを import して調べたとき）。
