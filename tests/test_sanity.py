import subprocess
import moscripts

def test_greet(capsys):
    moscripts.greet()
    captured = capsys.readouterr()
    assert captured.out == "Hello from moscripts!\n"
    assert captured.err == ""

def test_hello(capsys):
    subprocess.run(["./apps/hello.py"])
    captured = capsys.readouterr()
    assert captured.out == "Hello from moscripts hello app!\n"
    assert captured.err == ""
