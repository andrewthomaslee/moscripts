import subprocess
from subprocess import CompletedProcess
import sys
from pathlib import Path
import moscripts

test_dir: Path = Path(__file__).parent
app_dir: Path = test_dir.parent / "apps"
pythonScript_dir: Path = test_dir.parent / "pythonScripts"


def test_import() -> None:
    assert moscripts.hello is not None
    assert moscripts.NIX is not None
    assert moscripts.HOME is not None


def test_hello() -> None:
    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(app_dir / "hello.py")], capture_output=True, text=True
    )
    assert result.stdout == "Hello from moscripts hello app!\n"
    assert result.stderr == ""


def test_human_timestamp() -> None:
    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(pythonScript_dir / "human_timestamp.py")],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(pythonScript_dir / "human_timestamp.py"), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [
            sys.executable,
            str(pythonScript_dir / "human_timestamp.py"),
            "-t",
            "America/New_York",
        ],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(pythonScript_dir / "human_timestamp.py"), "-t", "UTC"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(pythonScript_dir / "human_timestamp.py"), "-f", "%Y"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [sys.executable, str(pythonScript_dir / "human_timestamp.py"), "-t", "FAIL"],
        capture_output=True,
        text=True,
    )
    assert result.stderr != ""
