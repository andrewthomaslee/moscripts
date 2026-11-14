import subprocess
import sys
from subprocess import CompletedProcess

from typer import Exit, colors, secho

from moscripts.utilities import tool_prefix

GUM: tuple[str, ...] = tool_prefix("gum")


def gum_confirm(message: str) -> bool:
    """Display interactive gum confirm interface and return user's choice."""
    cmd: list[str] = [
        *GUM,
        "confirm",
        message,
    ]

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
        *GUM,
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
