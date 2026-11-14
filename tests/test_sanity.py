import subprocess
import sys
from datetime import UTC
from subprocess import CompletedProcess

import moscripts
from moscripts.utilities import _get_system_timezone_name, str_to_timezone

HUMAN_TIMESTAMP: list[str] = [sys.executable, "-m", "moscripts.human_timestamp"]


def test_import() -> None:
    assert moscripts.HOME is not None
    assert moscripts.TZ is not None


def test_cli_modules_import() -> None:
    """Every CLI imports without side effects (no nix, no ~/Music needed)."""
    import importlib

    for name in ("motmp", "mpv_playlists", "password_generator", "human_timestamp"):
        module = importlib.import_module(f"moscripts.{name}")
        assert module.app is not None


def test_human_timestamp() -> None:
    result: CompletedProcess[str] = subprocess.run(
        HUMAN_TIMESTAMP,
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [*HUMAN_TIMESTAMP, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [
            *HUMAN_TIMESTAMP,
            "-t",
            "America/New_York",
        ],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [*HUMAN_TIMESTAMP, "-t", "UTC"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [*HUMAN_TIMESTAMP, "-f", "%Y"],
        capture_output=True,
        text=True,
    )
    assert result.stdout != ""
    assert result.stderr == ""

    result: CompletedProcess[str] = subprocess.run(
        [*HUMAN_TIMESTAMP, "-t", "FAIL"],
        capture_output=True,
        text=True,
    )
    assert result.stderr != ""


def test_str_to_timezone() -> None:
    from datetime import datetime, timedelta, timezone
    from zoneinfo import ZoneInfo

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
    assert tz_fallback == UTC

    # Test empty string fallback to UTC
    tz_empty_fallback = str_to_timezone("")
    assert tz_empty_fallback == UTC

    # Test system timezone getter
    system_tz_name = _get_system_timezone_name()
    assert isinstance(system_tz_name, str)
    assert system_tz_name != ""
    # Further checks could involve mocking subprocess to control output
    # For now, just ensure it returns a string and is not empty
