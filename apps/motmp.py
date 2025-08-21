#!/usr/bin/env python

# Standard Library
import os
import subprocess
from uuid import uuid4
from pathlib import Path
from typing import Iterable
from datetime import datetime, timezone

# Third Party
from typer import Argument, Exit, Option, Typer, colors, confirm, secho
from rich import print

# My Imports
from moscripts.utilities import nix_run_prefix

# Globals
HOME = Path.home()
MOTMP = HOME / ".cache" / "marimo" / "motmp"
VENV = MOTMP / ".venv"

uv_cmd_prefix: tuple[str] = nix_run_prefix("uv")


def init_motmp() -> None:
    """Initializes a virtual environment for MOTMP and build file structure."""
    secho("Initializing MOTMP...", fg=colors.BRIGHT_GREEN)
    assert HOME.exists(), "Home directory does not exist."

    if not MOTMP.exists():
        MOTMP.mkdir(parents=True, exist_ok=True)
        secho(f"Created {MOTMP}", fg=colors.BRIGHT_GREEN)

    if not VENV.exists():
        secho(f"VENV not found at {VENV}", fg=colors.YELLOW)
        if confirm("Create VENV?", default=True):
            try:
                subprocess.run(
                    [*uv_cmd_prefix, "init", "--bare", "--name", "motmp"],
                    check=True,
                    cwd=MOTMP,
                )
                subprocess.run(
                    [
                        *uv_cmd_prefix,
                        "add",
                        "marimo[recommended]",
                        "python-lsp-server",
                        "websockets",
                        "watchdog",
                    ],
                    check=True,
                    cwd=MOTMP,
                )
            except subprocess.CalledProcessError as e:
                secho(
                    f"Failed to create virtual environment: {e}",
                    fg=colors.RED,
                    err=True,
                )
                raise e
        else:
            secho("womp womp", fg=colors.RED)
            raise Exit(1)
    secho("🎉 Setup complete.", fg=colors.GREEN)


def scan_motmp(directory: Path = MOTMP) -> Iterable[tuple[Path, Path | None]]:
    """Scans a directory for MOTMP files."""
    SESSION = directory / "__marimo__" / "session"
    motmp_files: Iterable[tuple[Path, Path | None]] = [
        (file, SESSION / str(file.name + ".json"))
        if Path(SESSION / str(file.name + ".json")).exists()
        else (file, None)
        for file in directory.iterdir()
        if "motmp" in file.name and file.name.endswith(".py")
    ]
    return motmp_files


def sort_motmp_files(
    motmp_files: Iterable[tuple[Path, Path | None]], reverse: bool = True
) -> dict[str, str]:
    """Sorts MOTMP files by created time."""
    return {
        str(file.stem): datetime.fromtimestamp(
            file.stat().st_ctime, tz=timezone.utc
        ).strftime("%m-%d @ %I:%M %p")
        for file, session_file in sorted(
            motmp_files, key=lambda x: x[0].stat().st_ctime, reverse=reverse
        )
    }


def wipe_motmp(motmp_files: Iterable[tuple[Path, Path | None]]) -> None:
    """Wipes a directory of MOTMP files."""
    for motmp_file, session_file in motmp_files:
        try:
            motmp_file.unlink()
        except Exception as e:
            secho(f"Failed to wipe {motmp_file}: {e}", fg=colors.RED, err=True)
            pass
        try:
            if session_file:
                session_file.unlink()
        except Exception as e:
            secho(f"Failed to wipe {session_file}: {e}", fg=colors.RED, err=True)
            pass


def create_motmp(directory: Path = MOTMP) -> Path:
    """Creates a new MOTMP file."""
    file_name: str = f"motmp_{uuid4()}.py".replace("-", "_")
    motmp_file: Path = Path(directory) / file_name
    try:
        motmp_file.touch(mode=0o644)
    except Exception as e:
        secho(f"Failed to create {motmp_file}: {e}", fg=colors.RED, err=True)
        raise e
    return motmp_file


def launch_motmp(motmp_file: Path, venv: Path = VENV) -> None:
    """Launches a MOTMP file using a virtual environment."""
    marimo_executable: Path = venv / "bin" / "marimo"
    if not marimo_executable.exists():
        raise FileNotFoundError(f"marimo not found in {venv}")

    cmd: list[str] = [
        str(marimo_executable),
        "edit",
        str(motmp_file),
        "--no-token",
    ]
    print(cmd)
    try:
        os.execv(str(marimo_executable), cmd)
    except Exception as e:
        secho(f"Failed to launch {motmp_file}: {e}", fg=colors.RED, err=True)
        raise e


def validate_motmp_file(destination: Path) -> Path:
    """Validates a MOTMP file. Returns the validated file path."""
    assert destination.exists(), "Destination not found."
    if destination.is_dir():
        return create_motmp(destination)
    elif destination.is_file():
        assert destination.suffix == ".py", "Destination must be a Python file."
        return destination


def validate_venv(venv: Path, post_init: bool = False) -> Path:
    """Validates a virtual environment. Returns the validated virtual environment path or None."""
    result = venv if venv.exists() else VENV
    try:
        assert result.exists(), f"🚨 Virtual environment not found at {venv}"
        assert result.is_dir(), f"🚨 Virtual environment is not a directory at {venv}"
        assert Path(result / "bin" / "python").exists(), (
            f"🚨 python not found in {venv}"
        )
        assert Path(result / "bin" / "marimo").exists(), (
            f"🚨 marimo not found in {venv}"
        )
    except AssertionError as e:
        if (
            confirm("Invaild `.venv`. Create a new one?", default=True)
            and not post_init
        ):
            init_motmp()
            validate_venv(venv, post_init=True)
        else:
            secho(f"🚨 Invalid virtual environment at {venv}\n{e}", fg=colors.RED)
            raise Exit(1)
    return result


app = Typer(add_completion=False)


@app.command()
def motmp(
    destination: Path = Argument(
        MOTMP, help="Location to place MOTMP file or a MOTMP file to launch."
    ),
    venv: Path = Option(
        None,
        help=f"Location of the virtual environment. Tries to find a `.venv` in cwd. Falls back to `{VENV}`.",
    ),
    scan: bool = Option(False, help="Scan the directory for MOTMP files."),
    prev: int = Option(
        None,
        help="Launch the previous MOTMP file by index ordered by creation time. Use `0` for the newest and `-1` for the oldest.",
    ),
) -> None:
    """Create and edit temp marimo notebooks."""
    # Try initializing MOTMP
    if not MOTMP.exists():
        init_motmp()

    # Sanity checks
    CWD = Path.cwd()
    assert CWD.exists(), f"🚨 Current working directory not found at {CWD}"
    assert destination.exists(), f"Destination not found. {destination}"

    # Scan for MOTMP files
    if scan and destination.is_dir():
        motmp_files: Iterable[tuple[Path, Path | None]] = scan_motmp(destination)
        if len(motmp_files) > 0:
            secho(f"🔎 Found {len(motmp_files)} MOTMP files.", fg=colors.YELLOW)
        else:
            secho("🔎 Found no MOTMP files.", fg=colors.YELLOW)
            raise Exit(0)
        print(sort_motmp_files(motmp_files))
        if confirm("🗑️ Wipe files?", default=False):
            wipe_motmp(motmp_files)

        raise Exit(0)
    elif scan and destination.is_file():
        secho("🚨 Cannot scan a file. Please specify a directory.", fg=colors.RED)
        raise Exit(1)

    # Validate venv
    if venv is None:
        # Attempt to find a virtual environment
        if (
            confirm(f"Use .venv in cwd=`{str(CWD.stem)}`?", default=True)
            and Path(CWD / ".venv").exists()
        ):
            venv = CWD / ".venv"
    try:
        venv = validate_venv(venv)
    except Exception:
        venv = VENV

    secho(f"Using venv=`{str(venv)}`", fg=colors.BRIGHT_MAGENTA)

    if prev:
        motmp_file: Path = Path(
            destination
            / str(list(sort_motmp_files(scan_motmp(destination)).keys())[prev] + ".py")
        )
    else:
        motmp_file: Path = validate_motmp_file(destination)

    assert motmp_file.exists(), "Failed to create MOTMP file."
    assert venv.exists(), "Failed to find virtual environment."
    try:
        secho(f"🚀 Launching {motmp_file}", fg=colors.BRIGHT_GREEN)
        launch_motmp(motmp_file, venv)
    except Exception as e:
        secho(f"Failed to launch {motmp_file}: {e}", fg=colors.RED, err=True)
        raise e


if __name__ == "__main__":
    app()
