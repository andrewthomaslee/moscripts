# Standard Library
from datetime import datetime, timezone
import subprocess

# Third Party
import pytest

# My Imports
from moscripts.utilities import (
    create_human_readable_timestamp,
    which_nix,
    nix_run_prefix,
    which_executable,
)


# -------------------------------------UTILITIES--------------------------------------#


def test_create_human_readable_timestamp():
    assert create_human_readable_timestamp() == create_human_readable_timestamp(
        datetime.now(timezone.utc)
    )


def test_which_nix():
    assert which_nix().exists()


def test_nix_run_prefix():
    nix = str(which_nix())
    assert nix_run_prefix("uv") == (
        nix,
        "run",
        "--extra-experimental-features",
        "nix-command",
        "nixpkgs#uv",
        "--",
    )
    assert nix_run_prefix("marimo") == (
        nix,
        "run",
        "--extra-experimental-features",
        "nix-command",
        "nixpkgs#marimo",
        "--",
    )


@pytest.mark.skip(reason="no way of currently testing this")
def test_nix_run_prefix_subprocess_nixpkgs_download():
    result = subprocess.run(
        [*nix_run_prefix("uv"), "--version"], capture_output=True, text=True
    )
    assert result.stdout.startswith("uv")
    assert result.stderr == ""

    result = subprocess.run(
        [*nix_run_prefix("mpv"), "--version"], capture_output=True, text=True
    )
    assert result.stdout.startswith("mpv")
    assert result.stderr == ""


def test_which_executable():
    assert which_executable("which").exists()
    assert which_executable("nix").exists()
