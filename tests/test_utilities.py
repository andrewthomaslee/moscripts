from datetime import UTC, datetime

import pytest

from moscripts import utilities
from moscripts.utilities import (
    create_human_readable_timestamp,
    nix_run_prefix,
    tool_prefix,
    which_executable,
)

# -------------------------------------UTILITIES--------------------------------------#


def test_create_human_readable_timestamp() -> None:
    assert create_human_readable_timestamp() == create_human_readable_timestamp(
        datetime.now(UTC)
    )


def test_nix_run_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(utilities, "which_nix", lambda: "/bin/nix")
    for command in ("uv", "marimo"):
        assert nix_run_prefix(command) == (
            "/bin/nix",
            "run",
            "--extra-experimental-features",
            "nix-command flakes",
            f"nixpkgs#{command}",
            "--",
        )


def test_tool_prefix_prefers_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(utilities.shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    assert tool_prefix("gum") == ("/usr/bin/gum",)


def test_tool_prefix_falls_back_to_nix_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        utilities.shutil, "which", lambda cmd: "/bin/nix" if cmd == "nix" else None
    )
    monkeypatch.setattr(utilities, "which_nix", lambda: "/bin/nix")
    assert tool_prefix("mpv") == nix_run_prefix("mpv")


def test_tool_prefix_without_nix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(utilities.shutil, "which", lambda cmd: None)
    assert tool_prefix("uv") == ("uv",)


def test_tool_prefix_finds_gum() -> None:
    # The pytest check puts the pinned gum on PATH.
    assert tool_prefix("gum")[0].endswith("/gum")


def test_which_executable() -> None:
    assert which_executable("which").exists()
