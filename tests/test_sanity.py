import subprocess
from subprocess import CompletedProcess
import sys
from pathlib import Path
import moscripts
from moscripts.utilities import str_to_timezone, _get_system_timezone_name

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


def test_str_to_timezone() -> None:
    from zoneinfo import ZoneInfo
    from datetime import datetime, timezone, timedelta

    # Test IANA timezones
    tz_iana = str_to_timezone("America/New_York")
    assert isinstance(tz_iana, ZoneInfo)
    assert tz_iana.key == "America/New_York"

    # Test UTC offsets with colon
    tz_offset_plus = str_to_timezone("+05:30")
    assert isinstance(tz_offset_plus, timezone)
    assert tz_offset_plus.utcoffset(datetime.now()) == timedelta(hours=5, minutes=30)

    tz_offset_minus = str_to_timezone("-08:00")
    assert isinstance(tz_offset_minus, timezone)
    assert tz_offset_minus.utcoffset(datetime.now()) == timedelta(hours=-8)

    # Test UTC offsets without colon
    tz_offset_plus_no_colon = str_to_timezone("+0530")
    assert isinstance(tz_offset_plus_no_colon, timezone)
    assert tz_offset_plus_no_colon.utcoffset(datetime.now()) == timedelta(
        hours=5, minutes=30
    )

    # Test UTC offsets with only hours
    tz_offset_plus_hours = str_to_timezone("+05")
    assert isinstance(tz_offset_plus_hours, timezone)
    assert tz_offset_plus_hours.utcoffset(datetime.now()) == timedelta(hours=5)

    # Test invalid string fallback to UTC
    tz_fallback = str_to_timezone("INVALID_TZ_STRING")
    assert tz_fallback == timezone.utc

    # Test empty string fallback to UTC
    tz_empty_fallback = str_to_timezone("")
    assert tz_empty_fallback == timezone.utc

    # Test system timezone getter
    system_tz_name = _get_system_timezone_name()
    assert isinstance(system_tz_name, str)
    assert system_tz_name != ""
    # Further checks could involve mocking subprocess to control output
    # For now, just ensure it returns a string and is not empty
