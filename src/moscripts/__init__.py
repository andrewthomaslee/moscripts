from pathlib import Path
from datetime import timezone
from zoneinfo import ZoneInfo
from .utilities import which_nix, str_to_timezone, _get_system_timezone_name

# Globals
HOME: Path = Path.home()
NIX: Path = which_nix()
TZ: timezone | ZoneInfo = str_to_timezone(_get_system_timezone_name())


def hello() -> None:
    print("Hello from moscripts hello app!")
