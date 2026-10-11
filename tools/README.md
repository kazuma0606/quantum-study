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

## push 前の Codex 監査

`.githooks/pre-push` は `tools/codex_pre_push.py` を呼び、push 対象のコミット差分を読み取り専用で確認します。CSV、ログ、バイナリ、`results/` 以下の生成物は差分レビューの対象から外します。未コミットの作業ファイルを誤って読むことを防ぐため、対象コミットから一時的なスナップショットを作って Codex に渡します。スナップショットには、文脈確認用にコミット済みの他のファイルも含まれます（CSV と `results/` 以下を除く）。機密情報をコミットした場合は Codex に渡る可能性があります。

結果は `.codex/audit-reports/` に Markdown で保存され、Git には追加されません。Claude Code に修正を頼むときは、このレポートを指定して、各指摘を先に検討してもらってください。指摘があっても push は止めません。Codex が使えない場合や監査に失敗した場合は、元の差分起点を `.codex/audit-reports/pending/` に保存し、次回の同じリモート・ブランチへの push で新しいコミットも含めて再試行します。履歴の書き換えなどで保存した起点がローカルから消えた場合は警告を出し、今回の push 範囲のみを監査します。次の push がなければ再試行は始まりません。同じコミット差分の成功済みレポートは再利用します。hook は監査の完了まで待ち、開始時に最大15分と表示します。Markdown の空白・空行だけの差分は自動でスキップします。コードや設定ファイルの空白変更は意味を変え得るため監査します。文体だけの変更など、内容を確認して監査不要と判断した Markdown コミットには `Audit-Skip: style` というコミット本文の行を付けられます。push 範囲のすべてのコミットにこの行がある場合だけスキップします。

ローカルで hook を有効にするには `git config core.hooksPath .githooks` を実行します。コミットを指定したドライランは次のとおりです。

```bash
uv run --no-sync python tools/codex_pre_push.py --dry-run --range HEAD~1 HEAD
```

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
