from subprocess import CompletedProcess
import subprocess
from pathlib import Path
from moscripts.utilities import which_executable
import sys
from typer import Exit, secho, colors

GUM: Path = which_executable("gum")


def gum_confirm(message: str) -> bool:
    """Display interactive gum confirm interface and return user's choice."""
    cmd: list[str] = [
        str(GUM),
        "confirm",
        message,
    ]

    try:
        result: CompletedProcess[str] = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
        )
        # gum confirm returns 0 for yes, 1 for no, 130 for cancellation (SIGINT)
        if result.returncode == 0:
            return True
        elif result.returncode == 1:
            return False
        else:
            # Any other non-zero return code indicates cancellation or an error
            secho("🚨 Cancelled.", fg=colors.RED)
            raise Exit(1)

    except (KeyboardInterrupt, subprocess.CalledProcessError, FileNotFoundError) as e:
        # Handle user cancellation (KeyboardInterrupt), subprocess errors, or gum not found
        raise e


def gum_choose(
    choices: list[str],
    header: str = "Choose:",
    cursor: str = "> ",
    height: int = 10,
    limit: int = 1,
) -> str:
    """Display interactive gum choose interface and return selection."""
    if not choices:
        raise ValueError("No choices provided.")

    cmd: list[str] = [
        str(GUM),
        "choose",
        "--header",
        header,
        "--cursor",
        cursor,
        "--height",
        str(height),
        "--limit",
        str(limit),
    ] + choices

    try:
        result: CompletedProcess[str] = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
        )

        if result.returncode != 0:
            secho("🚨 Cancelled.", fg=colors.RED)
            raise Exit(1)

        return result.stdout.strip()

    except (KeyboardInterrupt, subprocess.CalledProcessError, FileNotFoundError) as e:
        # Handle user cancellation (KeyboardInterrupt), subprocess errors, or gum not found
        raise e
