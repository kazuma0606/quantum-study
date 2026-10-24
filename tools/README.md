# tools ― ノート・図・ノートブックを作るための補助スクリプト

> **作成** 2026-10-04　**更新** 2026-10-11
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

研究ノートの変更では、`docs/note_style.md` と `docs/concepts.md` を参照し、数式・科学的内容に加えて、前提と記号を使う前に説明しているか、導出の順序、等号の根拠、初出概念の動機と具体例、結論の根拠を点検します。他の文章でも、論旨と理解を妨げる不明瞭さを点検します。指摘は変更されたファイルの、差分に関係する箇所だけに絞ります。好みだけの文体指摘は対象にしません。

結果は `.codex/audit-reports/` に Markdown・JSON・SQLite（`audit.sqlite3`）で保存され、Git には追加されません。**指摘がある場合、前回の指摘が残る場合、根拠のない主張がある場合、または監査を完了できない場合は push を中断します。** コミットや作業ファイルは巻き戻しません。修正をコミットして再度 push すると、前回の指摘を一件ずつ再監査します。指摘がなくなれば push が続行します。同じ差分の判定は再利用します。監査に失敗した場合は元の差分起点を `.codex/audit-reports/pending/` に保存し、次回の同じリモート・ブランチへの push で再試行します。履歴の書き換えで起点が消えた場合は警告し、今回の push 範囲のみを監査します。hook は監査の完了まで最大15分待ちます。Markdown の空白・空行だけの差分も監査します。`Audit-Skip: style` による省略は行いません。

SQLite には、監査の範囲と判定、指摘、Claude Code の応答、主要な主張と根拠の分類、次回監査での解消判定、評価ケースの成績を保存します。指摘への応答は証拠とともに登録します。`fix` は修正、`dispute` は根拠つき反論、`human` は人の判断待ちです。応答だけでは push の停止は解除されず、次のコミットの監査で Codex が再判定します。意見が二往復しても解決しない場合は人が判定し、必要ならその push に限り `git push --no-verify` を使います。

```bash
uv run --no-sync python tools/audit_workflow.py recent
uv run --no-sync python tools/audit_workflow.py findings <audit_id>
uv run --no-sync python tools/audit_workflow.py claims <audit_id>
uv run --no-sync python tools/audit_workflow.py respond <finding_id> fix --rationale "修正内容" --evidence "研究ノート/example.md:42"
uv run --no-sync python tools/audit_workflow.py responses <finding_id>
uv run --no-sync python tools/audit_workflow.py search "端点"
```

レビューの検出率と誤検出を測るには、`tools/audit_eval_cases.json` の既知の問題例と安全な例を使います。評価は **明示的に実行したときだけ** Codex を各ケースに呼び、結果を SQLite の `eval_runs` に保存します。ケースごとに最大15分かかります。

```bash
uv run --no-sync python tools/audit_eval.py --case endpoint_counterexample
uv run --no-sync python tools/audit_eval.py
uv run --no-sync python tools/audit_eval.py --summary
uv run --no-sync python tools/audit_eval.py --regression
```

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
