from subprocess import CompletedProcess
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import subprocess
from pathlib import Path
import os
import re
import platform
from datetime import timedelta


def _get_system_timezone_name() -> str:
    """
    Attempts to retrieve the system's timezone name using various methods.
    """
    # Try timedatectl for Linux systems
    if platform.system() == "Linux":
        try:
            result = subprocess.run(
                ["timedatectl", "show", "--property=Timezone", "--value"],
                capture_output=True,
                text=True,
                check=True,
                timeout=1,
            )
            if result.stdout:
                return result.stdout.strip()
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            pass

    # Try reading /etc/localtime symlink for Unix-like systems
    try:
        result = subprocess.run(
            ["readlink", "/etc/localtime"],
            capture_output=True,
            text=True,
            check=True,
            timeout=1,
        )
        if result.stdout:
            # Extract timezone name from path like /usr/share/zoneinfo/America/New_York
            path_parts = result.stdout.strip().split("zoneinfo/")
            if len(path_parts) > 1:
                return path_parts[-1]
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Fallback to UTC if no system timezone can be determined
    return "UTC"


def str_to_timezone(tz_str: str) -> ZoneInfo | timezone:
    try:
        return ZoneInfo(tz_str)  # IANA timezone
    except Exception:
        try:
            # Attempt to parse as UTC offset
            match = re.match(r"([+-])(\d{1,2})(?::?(\d{2}))?", tz_str)
            if match:
                sign, hours_str, minutes_str = match.groups()
                hours = int(hours_str)
                minutes = int(minutes_str) if minutes_str else 0
                offset = timedelta(hours=hours, minutes=minutes)
                if sign == "-":
                    offset = -offset
                return timezone(offset)
            else:
                raise ValueError("Invalid timezone string format")
        except ValueError:
            return timezone.utc  # fallback


def create_human_readable_timestamp(
    dt_object: datetime | None = None,
    target_tz: str = "America/Chicago",
    fmt: str = "%Y-%m-%d %I:%M:%S %p",
) -> str:
    """Creates a formatted, human-readable timestamp from a datetime object.

    This function is optimized to cache ZoneInfo lookups, making it highly
    performant for repeated calls with the same target timezone.

    Args:
        dt_object: An optional timezone-aware datetime object. If naive, it's
                   assumed to be in UTC. If None, defaults to utcnow().
        target_tz: The IANA timezone name to convert the time to for display.
        fmt: The strftime format string for the output.

    Returns:
        A formatted string representation of the timestamp.
    """
    if dt_object is None:
        source_dt: datetime = datetime.now(timezone.utc)
    elif dt_object.tzinfo is None:
        source_dt: datetime = dt_object.replace(tzinfo=timezone.utc)
    else:
        source_dt = dt_object

    display_tz: ZoneInfo = ZoneInfo(target_tz)
    local_dt: datetime = source_dt.astimezone(display_tz)

    return local_dt.strftime(fmt)


def nix_run_prefix(command: str) -> tuple[str, ...]:
    """Returns the prefix for nix commands."""
    return (
        str(which_nix()),
        "run",
        "--extra-experimental-features",
        "nix-command flakes",
        f"nixpkgs#{command}",
        "--",
    )


def which_nix() -> Path:
    """Returns the path to the nix executable."""
    result: CompletedProcess[str] = subprocess.run(
        ["which", "nix"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Nix not found. Please install it."
    nix: Path = Path(result.stdout.strip())
    assert nix.exists(), "Nix not found. Please install it."
    return nix


def which_executable(executable: str) -> Path:
    """Returns the path to the nix executable."""
    result: CompletedProcess[str] = subprocess.run(
        ["which", executable],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"{executable} not found."
    location: Path = Path(result.stdout.strip())
    assert location.exists(), f"{executable} not found."
    assert location.is_file(), f"{executable} is not a file."
    assert os.access(location, os.X_OK), f"{executable} is not executable."
    return location
