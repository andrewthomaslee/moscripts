import subprocess
from subprocess import CompletedProcess
from typing import Any
import sys
from pathlib import Path
import moscripts

test_dir: Path = Path(__file__).parent
app_dir: Path = test_dir.parent / "apps"


def test_greet(capsys) -> None:
    moscripts.greet()
    captured: Any = capsys.readouterr()
    assert captured.out == "Hello from moscripts!\n"
    assert captured.err == ""
    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(app_dir / "greet.py")], capture_output=True, text=True
    )
    assert result.stdout == "Hello from moscripts!\n"
    assert result.stderr == ""


def test_hello() -> None:
    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(app_dir / "hello.py")], capture_output=True, text=True
    )
    assert result.stdout == "Hello from moscripts hello app!\n"
    assert result.stderr == ""
