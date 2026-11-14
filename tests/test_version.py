import re
from types import ModuleType

import pytest
from typer.testing import CliRunner

from moscripts import human_timestamp, motmp, mpv_playlists, password_generator


@pytest.mark.parametrize(
    "module", [human_timestamp, motmp, mpv_playlists, password_generator]
)
def test_version(module: ModuleType) -> None:
    """Every CLI answers --version with `moscripts <version>` and exits 0."""
    result = CliRunner().invoke(module.app, ["--version"])
    assert result.exit_code == 0, result.output
    assert re.fullmatch(r"moscripts \d+\.\d+\.\d+\n", result.output), result.output
