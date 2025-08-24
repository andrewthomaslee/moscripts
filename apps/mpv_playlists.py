#!/usr/bin/env python

# Standard Library
import os
from pathlib import Path

# Third Party
from typer import Argument, Option, Typer, colors, secho, Exit
from rich import print

# My Imports
from moscripts.utilities import nix_run_prefix
from moscripts.gum import gum_choose

# Globals
HOME: Path = Path.home()
PLAYLISTS: Path = HOME / "Music" / "Playlists"

assert PLAYLISTS.exists(), (
    "Playlists directory does not exist. Please create it at `~/Music/Playlists`."
)
assert PLAYLISTS.is_dir(), (
    "Playlists directory is not a directory. Please create it at `~/Music/Playlists`."
)

playlists: list[Path] = list(PLAYLISTS.iterdir())
assert len(playlists) > 0, (
    "No playlists found. Please create at least one playlist in `~/Music/Playlists`."
)

app: Typer = Typer(add_completion=False)


@app.command()
def mpv_playlists(
    playlist: Path = Argument(playlists[0], help="Playlist name."),
    scan: bool = Option(False, help="Scan the directory for playlists."),
    shuffle: bool = Option(True, help="Shuffle the playlist."),
) -> None:
    """Launches mpv with a playlist."""
    if scan:
        secho(f"🔎 Found {len(playlists)} Playlists.", fg=colors.BRIGHT_CYAN)
        choices: list[str] = [str(playlist.stem) for playlist in playlists]
        result: str | None = gum_choose(choices)
        if result is not None:
            playlist: Path = PLAYLISTS / result
        else:
            secho("🚨 Cancelled.", fg=colors.RED)
            raise Exit(1)

    assert playlist in playlists, "Playlist not found."

    secho(f"🎵 Launching {playlist}", fg=colors.BRIGHT_GREEN)
    mpv_cmd_prefix: tuple[str, ...] = nix_run_prefix("mpv")
    mpv_cmd_options: tuple[str, ...] = (
        ("--loop-playlist", "--no-video", "--shuffle")
        if shuffle
        else ("--loop-playlist", "--no-video")
    )
    cmd: tuple[str, ...] = (
        *mpv_cmd_prefix,
        *mpv_cmd_options,
        str(playlist),
    )
    print(cmd)
    try:
        os.execv(mpv_cmd_prefix[0], cmd)
    except Exception as e:
        secho(f"Failed to launch {playlist}: {e}", fg=colors.RED, err=True)
        raise e
    finally:
        return None


if __name__ == "__main__":
    app()
