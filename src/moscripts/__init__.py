"""moscripts: small Python CLIs packaged with Nix (uv2nix)."""

from datetime import timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .utilities import _get_system_timezone_name, str_to_timezone

# Globals
HOME: Path = Path.home()
TZ: timezone | ZoneInfo = str_to_timezone(_get_system_timezone_name())
