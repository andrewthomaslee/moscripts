import os
from pathlib import Path

from rich import print
from typer import Argument, Exit, Option, Typer, colors, secho

from moscripts.gum import gum_choose
from moscripts.utilities import tool_prefix

# Globals
HOME: Path = Path.home()
PLAYLISTS: Path = HOME / "Music" / "Playlists"


def find_playlists(directory: Path) -> list[Path]:
    """Lists the playlists in a directory, failing with a clear message."""
    if not directory.is_dir():
        secho(
            f"🚨 Playlists directory not found. Please create it at `{directory}`.",
            fg=colors.RED,
            err=True,
        )
        raise Exit(1)
    playlists: list[Path] = sorted(directory.iterdir())
    if not playlists:
        secho(
            f"🚨 No playlists found. Please create at least one in `{directory}`.",
            fg=colors.RED,
            err=True,
        )
        raise Exit(1)
    return playlists


app: Typer = Typer(add_completion=False)


@app.command()
def mpv_playlists(
    playlist: str | None = Argument(
        None, help="Playlist name or path. Defaults to the first playlist."
    ),
    scan: bool = Option(False, help="Scan the directory for playlists."),
    shuffle: bool = Option(True, help="Shuffle the playlist."),
    directory: Path = Option(PLAYLISTS, help="Directory holding the playlists."),
) -> None:
    """Launches mpv with a playlist."""
    playlists: list[Path] = find_playlists(directory)

    if scan:
        secho(f"🔎 Found {len(playlists)} Playlists.", fg=colors.BRIGHT_CYAN)
        choices: list[str] = [str(playlist.name) for playlist in playlists]
        playlist = gum_choose(choices)

    if playlist is None:
        selected: Path = playlists[0]
    else:
        candidate: Path = Path(playlist)
        selected = candidate if candidate.is_absolute() else directory / candidate

    if selected not in playlists:
        secho(f"🚨 Playlist not found: {selected}", fg=colors.RED, err=True)
        raise Exit(1)

    secho(f"🎵 Launching {selected}", fg=colors.BRIGHT_GREEN)
    mpv_cmd_prefix: tuple[str, ...] = tool_prefix("mpv")
    mpv_cmd_options: tuple[str, ...] = (
        ("--loop-playlist", "--no-video", "--shuffle")
        if shuffle
        else ("--loop-playlist", "--no-video")
    )
    cmd: tuple[str, ...] = (
        *mpv_cmd_prefix,
        *mpv_cmd_options,
        str(selected),
    )
    # Flush: execv replaces the process and drops buffered output.
    print(cmd, flush=True)
    try:
        os.execv(mpv_cmd_prefix[0], cmd)
    except Exception as e:
        secho(f"Failed to launch {selected}: {e}", fg=colors.RED, err=True)
        raise e


if __name__ == "__main__":
    app()
