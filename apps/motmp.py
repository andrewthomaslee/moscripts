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
                    [*uv_cmd_prefix, "add", "marimo[recommended]", "python-lsp-server", "websockets", "watchdog"],
                    check=True,
                    cwd=MOTMP,
                )
            except subprocess.CalledProcessError as e:
                secho(f"Failed to create virtual environment: {e}", fg=colors.RED, err=True)
                raise e
        else:
            secho("womp womp", fg=colors.RED)
            raise Exit(1)
    secho("🎉 Setup complete.", fg=colors.GREEN)


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


app = Typer(add_completion=False)


@app.command()
def motmp(
    destination: Path = Argument(MOTMP, help="Location to place MOTMP file or a MOTMP file to launch."),
    venv: Path = Option(VENV, help="Location of the virtual environment."),
    scan: bool = Option(False, help="Scan the directory for MOTMP files."),
) -> None:
    """Create and edit temp marimo notebooks."""
    # Validate destination and venv
    assert destination.exists(), f"Destination not found. {destination}"
    if not MOTMP.exists():
        try:
            init_motmp()
        except Exception as e:
            secho(f"Failed to initialize motmp: {e}", fg=colors.RED, err=True)
            raise e
    if not venv.exists():
        secho(f"🚨 Virtual environment not found at {venv}", fg=colors.RED)
        raise Exit(1)

    # Scan for MOTMP files
    if scan and destination.is_dir():
        motmp_files: Iterable[tuple[Path, Path | None]] = scan_motmp(destination)
        if len(motmp_files) > 0:
            secho(f"🔎 Found {len(motmp_files)} MOTMP files.", fg=colors.YELLOW)
        else:
            secho("🔎 Found no MOTMP files.", fg=colors.YELLOW)
            raise Exit(0)
        print(motmp_files)
        if confirm("🗑️ Wipe files?", default=True):
            wipe_motmp(motmp_files)
        
        raise Exit(0)
    elif scan and destination.is_file():
        secho("🚨 Cannot scan a file. Please specify a directory.", fg=colors.RED)
        raise Exit(1)


    # Validate MOTMP file and launch
    motmp_file: Path = validate_motmp_file(destination)
    assert motmp_file.exists(), "Failed to create MOTMP file."
    try:
        secho(f"🚀 Launching {motmp_file}", fg=colors.BRIGHT_GREEN)
        launch_motmp(motmp_file, venv)
    except Exception as e:
        secho(f"Failed to launch {motmp_file}: {e}", fg=colors.RED, err=True)
        raise e


if __name__ == "__main__":
    app()