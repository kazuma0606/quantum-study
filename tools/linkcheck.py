"""README・docs・研究ノートの相対リンクの行き先が存在するかを調べる。

実行（リポジトリのルートから）: uv run python tools/linkcheck.py .
"""
import re, sys
from pathlib import Path
from urllib.parse import unquote

root = Path(sys.argv[1])
files = [root / "README.md", root / "REQUIREMENTS.md", root / "CLAUDE.md"] + sorted((root / "docs").glob("*.md")) + sorted((root / "研究ノート").rglob("*.md"))
bad = []
n = 0
for f in files:
    if not f.exists():
        continue
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"```.*?```", "", t, flags=re.S)  # コードブロックは除く
    t = re.sub(r"\$\$.*?\$\$", "", t, flags=re.S)  # 数式ブロックは除く
    t = re.sub(r"\$[^$\n]*\$", "", t)  # 行内数式の中の ](...) を誤検出しない
    for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", t):
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        n += 1
        target = unquote(href.split("#")[0])
        if not target:
            continue
        p = (f.parent / target).resolve()
        if not p.exists():
            bad.append((str(f.relative_to(root)), href))
print(f"相対リンク {n} 本を検査")
if bad:
    print(f"行き先がないリンク {len(bad)} 件:")
    for f, h in bad:
        print(f"  {f}: {h}")
else:
    print("行き先がないリンク: 0 件")
