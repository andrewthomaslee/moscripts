#!/usr/bin/env python

# Standard Library
import os
import subprocess
from uuid import uuid4
from pathlib import Path
from typing import Iterable

# Third Party
from typer import Argument, Exit, Option, Typer, colors, confirm, secho
from rich import print

# My Imports
from moscripts.utilities import create_human_readable_timestamp, nix_run_prefix

# Globals
HOME = Path.home()
PLAYLISTS = HOME / "Music" / "Playlists"

assert PLAYLISTS.exists(), "Playlists directory does not exist. Please create it at `~/Music/Playlists`."
assert PLAYLISTS.is_dir(), "Playlists directory is not a directory. Please create it at `~/Music/Playlists`."

playlists = list(PLAYLISTS.iterdir())


app = Typer(add_completion=False)

@app.command()
def test():
    print(playlists)

    result = subprocess.run(
        ["nix", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Nix not found. Please install it."

if __name__ == "__main__":
    app()
