---
name: notebook-gen
description: Jupyter ノートブック（notebooks/ 以下）を生成スクリプトで作る・直すときの手順と約束事。nbformat による生成、セル ID の固定、型ヒント、plotly の FigureWidget とスライダーの注意、nbconvert での実行、スライダーの自動チェック、スクリーンショットでの確認を含む。ノートブックを作成・修正するときに使う。
---

# ノートブックの作り方

## 原則

- ノートブックは**手で編集しない**。`tools/notebook_generators/make_<フォルダ名>.py` を作り（または直し）、そこから生成する。出力なしで保存する。
- フォルダごとに README.md（ノートブックの一覧表、実行方法、関連ノートへのリンク）を置く。
- Python は `uv run` で実行する。

## 生成スクリプトの雛形

```python
OUT = Path("notebooks/…"); OUT.mkdir(parents=True, exist_ok=True)
def save(name, cells):
    for i, cell in enumerate(cells):
        cell.id = f"{Path(name).stem[:2]}-{i:02d}"   # セル ID を固定（作り直しても差分が出ない）
    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python"}
    nbformat.write(nb, OUT / name)
```

- リンクは辞書（`LINKS = {"PSNOTE": R + "…/note.md"}`）で管理し、Markdown の中のキーを置き換える。ノートブックの場所から研究ノートへは `../../../研究ノート/…`（深さに注意）。
- コードには型ヒントを付ける（`Matrix = NDArray[np.complex128]` などの別名を最初のセルで定義）。
- 各節に「**考えてみよう**」を置き、ノートの式を `assert` で確かめる。

## plotly とスライダーの注意（実際に起きた不具合）

- **FigureWidget のトレースには、numpy 配列ではなくリストを渡す**（`.tolist()`）。numpy 配列は型付き配列としてブラウザとやり取りされ、スライダーを動かしたときに「truth value of an array is ambiguous」で落ちる。
- FigureWidget の変数名は図ごとに変える（`fig_euler`、`fig_rot` など）。`fig` を使い回すと、後のセルを実行したあとにスライダーが壊れる。
- 静的な図（`go.Figure`）は `fig` でよい。

## 検証

```bash
uv run python tools/notebook_generators/make_xx.py
uv run jupyter nbconvert --to notebook --execute notebooks/…/a.ipynb --output-dir <一時フォルダ> --ExecutePreprocessor.timeout=500
uv run python tools/check_widget_arrays.py notebooks/…/*.ipynb      # 「問題のあるトレース： 0」
uv run python tools/render_all_figs.py notebooks/…/a.ipynb <一時フォルダ>
powershell -ExecutionPolicy Bypass -File tools/screenshot_html.ps1 <一時フォルダ>
```

- 実行の出力は一時フォルダに書き、リポジトリのノートブックは出力なしのまま。
- スクリーンショットを Read ツールで見て、凡例の `e^{…}`（plotly は TeX の波かっこを表示できない → `e^(…)` にする）、0 の対数軸への落ち込み、注釈の位置ずれを確認する。
- 数式の行区切り `\\` は、生成スクリプトを直すときにシェルのヒアドキュメントを通すと `\` に化ける。修正は Write ツールで作った Python スクリプトで行う。
