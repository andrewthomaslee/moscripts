#!/usr/bin/env python3

import typer
from moscripts.utilities import create_human_readable_timestamp

app: typer.Typer = typer.Typer(
    name="human-timestamp",
    help="A simple human-readable timestamp CLI.",
    add_completion=False,
    pretty_exceptions_enable=False,
)

@app.command()
def create(
    target_tz: str = typer.Option(
        "America/Chicago",
        "--target-tz",
        "-t",
        help="The target timezone to convert the timestamp to.",
        show_default=True,
    ),
    fmt: str = typer.Option(
        "%Y-%m-%d %I:%M:%S %p",
        "--format",
        "-f",
        help="The format string to use for the timestamp.",
        show_default=True,
    ),
) -> None:
    """Creates a human-readable timestamp and prints it to the console."""
    try:
        human_time: str = create_human_readable_timestamp(target_tz=target_tz, fmt=fmt)
        typer.secho(human_time, fg=typer.colors.CYAN)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
