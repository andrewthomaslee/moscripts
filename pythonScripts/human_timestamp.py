#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typer",
# ]
# ///

import typer
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def create_human_readable_timestamp(
    dt_object: datetime | None = None,
    target_tz: str = "America/Chicago",
    fmt: str = "%Y-%m-%d %I:%M:%S %p",
) -> str:
    """Creates a formatted, human-readable timestamp from a datetime object.

    This function is optimized to cache ZoneInfo lookups, making it highly
    performant for repeated calls with the same target timezone.

    Args:
        dt_object: An optional timezone-aware datetime object. If naive, it's
                   assumed to be in UTC. If None, defaults to utcnow().
        target_tz: The IANA timezone name to convert the time to for display.
        fmt: The strftime format string for the output.

    Returns:
        A formatted string representation of the timestamp.
    """
    if dt_object is None:
        source_dt: datetime = datetime.now(timezone.utc)
    elif dt_object.tzinfo is None:
        source_dt: datetime = dt_object.replace(tzinfo=timezone.utc)
    else:
        source_dt = dt_object

    display_tz: ZoneInfo = ZoneInfo(target_tz)
    local_dt: datetime = source_dt.astimezone(display_tz)

    return local_dt.strftime(fmt)


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
