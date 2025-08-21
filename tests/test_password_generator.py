# Standard Library
import subprocess
from pathlib import Path
import sys

# Third Party

# My Imports


test_dir = Path(__file__).parent
app_dir = test_dir.parent / "apps"


def test_password_generator():
    result = subprocess.run(
        [sys.executable, str(app_dir / "password_generator.py")],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert "length=64" in result.stdout

    result = subprocess.run(
        [sys.executable, str(app_dir / "password_generator.py"), "--length", "32"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert "length=32" in result.stdout

    result = subprocess.run(
        [sys.executable, str(app_dir / "password_generator.py"), "--length", "300"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert "length=300" in result.stdout


def test_password_generator_chars():
    result = subprocess.run(
        [sys.executable, str(app_dir / "password_generator.py"), "--custom", "a"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert "character_set='a'" in result.stdout

    result = subprocess.run(
        [sys.executable, str(app_dir / "password_generator.py"), "--custom", "@"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert "character_set='@'" in result.stdout

    symbols = {
        "@",
        "#",
        "!",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "+",
        "{",
        "}",
        "[",
        "]",
        ";",
        ",",
        ".",
        "?",
        "|",
        "<",
        ">",
        "~",
        "=",
        "`",
        "'",
        "_",
    }
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(app_dir / "password_generator.py"),
                "--no-symbols",
                "--cli",
            ],
            capture_output=True,
            text=True,
        )
        assert result.stdout != ""
        assert result.stderr == ""
        assert all(symbol not in result.stdout.strip() for symbol in symbols)


def test_password_generator_no_lowercase():
    import string

    lowercase_chars = string.ascii_lowercase
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(app_dir / "password_generator.py"),
                "--cli",
                "--no-lowercase",
            ],
            capture_output=True,
            text=True,
        )
        assert result.stdout != ""
        assert result.stderr == ""
        assert all(char not in result.stdout for char in lowercase_chars)


def test_password_generator_no_uppercase():
    import string

    uppercase_chars = string.ascii_uppercase
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(app_dir / "password_generator.py"),
                "--cli",
                "--no-uppercase",
            ],
            capture_output=True,
            text=True,
        )
        assert result.stdout != ""
        assert result.stderr == ""
        assert all(char not in result.stdout.strip() for char in uppercase_chars)


def test_password_generator_no_digits():
    import string

    digit_chars = string.digits
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                str(app_dir / "password_generator.py"),
                "--cli",
                "--no-digits",
            ],
            capture_output=True,
            text=True,
        )
        assert result.stdout != ""
        assert result.stderr == ""
        assert all(char not in result.stdout.strip() for char in digit_chars)


def test_password_generator_length():
    result = subprocess.run(
        [
            sys.executable,
            str(app_dir / "password_generator.py"),
            "--cli",
            "--length",
            "32",
        ],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert len(result.stdout.strip()) == 32

    result = subprocess.run(
        [
            sys.executable,
            str(app_dir / "password_generator.py"),
            "--cli",
        ],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""
    assert len(result.stdout.strip()) == 64
