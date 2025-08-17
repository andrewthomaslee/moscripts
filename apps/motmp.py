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

# Globals
HOME = Path.home()
MOTMP = HOME / ".cache" / "marimo" / "motmp"
VENV = MOTMP / ".venv"


def init_motmp() -> None:
    """Initializes a virtual environment for MOTMP and build file structure."""
    secho("Initializing motmp...", fg=colors.YELLOW)
    assert HOME.exists(), "Home directory does not exist."

    if not MOTMP.exists():
        MOTMP.mkdir(parents=True, exist_ok=True)
        secho(f"Created {MOTMP}", fg=colors.GREEN)

    
    if not VENV.exists():
        secho(f"Virtual environment not found at {VENV}", fg=colors.YELLOW)
        if confirm("Create virtual environment?", default=True):
            try:
                subprocess.run(
                    ["uv", "init", "--bare", "--name", "motmp"],
                    check=True,
                    cwd=MOTMP,
                )
                subprocess.run(
                    ["uv", "add", "marimo[recommended]", "python-lsp-server", "websockets", "watchdog"],
                    check=True,
                    cwd=MOTMP,
                )
            except subprocess.CalledProcessError as e:
                secho(f"Failed to create virtual environment: {e}", fg=colors.RED, err=True)
                raise e
        else:
            secho("womp womp", fg=colors.RED)
            raise Exit(1)
    secho("🎉 Setup MOTMP complete.", fg=colors.GREEN)


def scan_motmp(directory: Path = MOTMP) -> Iterable[tuple[Path, Path | None]]:
    """Scans a directory for MOTMP files."""
    SESSION = directory / "__marimo__" / "session"
    motmp_files: Iterable[tuple[Path, Path | None]] = [
        (file, SESSION / str(file.name + ".json")) if Path(SESSION / str(file.name + ".json")).exists() else (file, None)
        for file in directory.iterdir()
        if "motmp" in file.name and file.name.endswith(".py")
    ]
    return motmp_files

    
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
    print("Command:  ", cmd)
    try:
        os.execv(str(marimo_executable), cmd)
    except Exception as e:
        secho(f"Failed to launch {motmp_file}: {e}", fg=colors.RED, err=True)
        raise e


app = Typer(add_completion=False)

@app.command()
def motmp(
    directory: Path = Argument(MOTMP, help="Location to place MOTMP files."),
    venv: Path = Option(VENV, help="Location of the virtual environment."),
    scan: bool = Option(False, help="Scan the directory for MOTMP files."),
) -> None:
    """Create and edit temp marimo notebooks."""

    if not directory.exists():
        secho(f"🚨 Directory not found at {directory}", fg=colors.RED)
        raise Exit(1)

    if not MOTMP.exists():
        try:
            init_motmp()
        except Exception as e:
            secho(f"Failed to initialize motmp: {e}", fg=colors.RED, err=True)
            raise e

    if not venv.exists():
        secho(f"🚨 Virtual environment not found at {venv}", fg=colors.RED)
        raise Exit(1)
        

    if scan:
        motmp_files: Iterable[tuple[Path, Path | None]] = scan_motmp(directory)
        secho(f"🔎 Found {len(motmp_files)} MOTMP files.", fg=colors.YELLOW)
        print(motmp_files)
        if confirm("🗑️ Wipe files?", default=True):
            wipe_motmp(motmp_files)
        
        raise Exit(0)


    motmp_file: Path = create_motmp(directory)
    assert motmp_file.exists(), "Failed to create MOTMP file."
    try:
        secho(f"🚀 Launching {motmp_file}", fg=colors.YELLOW)
        launch_motmp(motmp_file, venv)
    except Exception as e:
        secho(f"Failed to launch {motmp_file}: {e}", fg=colors.RED, err=True)
        raise e


if __name__ == "__main__":
    app()