# tools ― ノート・図・ノートブックを作るための補助スクリプト

> **作成** 2026-10-04　**更新** 2026-10-10
> 研究ノートとノートブックを作るための補助スクリプトの一覧。リンクや記法の点検、図の書き出し、ノートブックの生成、見出しの日付の更新。

研究ノートとノートブックを作るときに、くり返し使うスクリプトです。どれもリポジトリのルートから実行します。手順の約束事は `.claude/skills/` の Skill（`research-note`、`note-figures`、`notebook-gen`、`quantum-experiment`）にまとめてあります。

## 点検用

| スクリプト | 用途 | 実行 |
|---|---|---|
| `linkcheck.py` | README・docs・研究ノートの相対リンクの行き先が存在するか | `uv run python tools/linkcheck.py .` |
| `update_md_headers.py` | Markdown の先頭の「作成日・更新日・要約」の見出しの日付を、git の記録からそろえる（見出しだけの変更は更新に数えない）。コミットの前に実行する | `uv run python tools/update_md_headers.py`（確かめるだけなら `--check`） |
| `scan_bars.py` | ブラケット記法の縦棒 `\|` の抜けを探す（表の中で消える不具合） | `uv run python tools/scan_bars.py ノート.md` |
| `check_widget_arrays.py` | ノートブックのスライダーを全部動かし、FigureWidget に numpy 配列が残っていないか | `uv run python tools/check_widget_arrays.py a.ipynb b.ipynb` |
| `render_all_figs.py` | ノートブックの図（`fig*`）をセルごとに HTML に書き出す | `uv run python tools/render_all_figs.py a.ipynb 出力フォルダ` |
| `screenshot_html.ps1` | 書き出した HTML を Edge のヘッドレスモードで PNG にする（画像を見て確認するため） | `powershell -ExecutionPolicy Bypass -File tools/screenshot_html.ps1 出力フォルダ` |

目次の生成と整合性の検査は、`研究ノート/tools/build_toc.py` にあります（`--check` で書き込まずに検査）。

## ノートブックの生成スクリプト（`notebook_generators/`）

ノートブックは手で編集せず、これらのスクリプトで生成します（セル ID を固定しているので、作り直しても差分は変更した箇所だけになる）。ノートブックを直すときは、スクリプトを直して作り直します。

| スクリプト | 生成するノートブック |
|---|---|
| `make_01_pauli_bloch.py` | `notebooks/01_pauli_bloch/`（2冊） |
| `make_02_su2_rotation.py` | `notebooks/02_su2_rotation/`（2冊） |
| `make_03_angular_momentum.py` | `notebooks/03_angular_momentum/`（2冊） |
| `make_00_taylor_series.py` | `notebooks/foundations/00_taylor_series/`（3冊） |
| `make_14_chaos.py` | `notebooks/learning/14_chaos/`（2冊） |
| `make_03_christoffel_riemann_a.py` | `notebooks/foundations/03_christoffel_riemann/` の 01・02（引数に出力フォルダ） |
| `make_03_christoffel_riemann_b.py` | 同じく 03〜05（引数に出力フォルダ） |

```bash
uv run python tools/notebook_generators/make_00_taylor_series.py
uv run python tools/notebook_generators/make_03_christoffel_riemann_a.py notebooks/foundations/03_christoffel_riemann
```

（2026年10月4日に、どのスクリプトもコミット済みのノートブックの中身をそのまま再現することを確認済み。クリストッフェル記号の2本は、セル ID を固定する前に作ったため、作り直すとセル ID だけが変わる。）
