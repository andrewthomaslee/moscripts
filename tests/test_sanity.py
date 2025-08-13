import subprocess
import moscripts

def test_greet(capsys):
    moscripts.greet()
    captured = capsys.readouterr()
    assert captured.out == "Hello from moscripts!\n"
    assert captured.err == ""

def test_hello(capsys):
    result = subprocess.run(["./apps/hello.py"], capture_output=True, text=True)
    assert result.stdout == "Hello from moscripts hello app!\n"
    assert result.stderr == ""
