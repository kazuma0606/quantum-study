"""ノート3 の検算スクリプトを実行し、不一致が 0 件であることを確かめる。"""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "verify_note3.py"


def test_verify_note3_has_no_mismatch():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, encoding="utf-8", check=False
    )
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-2000:]
    assert "不一致 0 件" in result.stdout
