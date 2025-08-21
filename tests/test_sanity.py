import subprocess
import sys
from pathlib import Path
import moscripts

test_dir = Path(__file__).parent
app_dir = test_dir.parent / "apps"

def test_greet(capsys):
    moscripts.greet()
    captured = capsys.readouterr()
    assert captured.out == "Hello from moscripts!\n"
    assert captured.err == ""
    result = subprocess.run([sys.executable, str( app_dir / "greet.py")], capture_output=True, text=True)
    assert result.stdout == "Hello from moscripts!\n"
    assert result.stderr == ""

def test_hello():
    result = subprocess.run([sys.executable, str( app_dir / "hello.py")], capture_output=True, text=True)
    assert result.stdout == "Hello from moscripts hello app!\n"
    assert result.stderr == ""


