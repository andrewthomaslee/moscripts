from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import subprocess
from pathlib import Path



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



def nix_run_prefix(command:str)-> tuple[str]:
    """Returns the prefix for nix commands."""
    return (str(which_nix()), "run", f"nixpkgs#{command}", "--")


def which_nix() -> Path:
    """Returns the path to the nix executable."""
    result = subprocess.run(
        ["which", "nix"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Nix not found. Please install it."
    nix: Path = Path(result.stdout.strip())
    assert nix.exists(), "Nix not found. Please install it."
    return nix

