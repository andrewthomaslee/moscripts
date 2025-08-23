#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typer",
# ]
# ///

from typing import LiteralString
import string
import typer
from typer import Typer
import secrets
from collections.abc import Iterable


def generate_random_password(length: int, character_set: Iterable[str]) -> str:
    """Generates a cryptographically secure random password.

    This function creates a password of a specified length by randomly choosing
    characters from the provided character set. It uses the `secrets` module
    to ensure the generated password is secure.

    Args:
        length: The desired length of the password. Must be a positive integer.
        character_set: An iterable of characters (e.g., a string or a list)
            to use for generating the password.

    Returns:
        A string representing the randomly generated password.

    Raises:
        ValueError: If the length is not a positive integer or if the
            character_set is empty.
    """
    char_list: list[str] = list(character_set)

    if length <= 0:
        raise ValueError("Password length must be a positive integer.")

    if not char_list:
        raise ValueError(
            "Character set cannot be empty. Please enable at least one character type (e.g., --lowercase) or provide a --custom set."
        )

    password_chars: list[str] = [secrets.choice(char_list) for _ in range(length)]
    return "".join(password_chars)


app: Typer = typer.Typer(
    name="passgen",
    help="A secure, customizable password generator CLI.",
    add_completion=False,
)

LIMITED_SYMBOLS = "!#$%&?@"


@app.command()
def generate(
    length: int = typer.Option(
        64,
        "--length",
        "-l",
        help="The desired length of the password.",
        min=1,
        show_default=True,
    ),
    include_lowercase: bool = typer.Option(
        True,
        "--lowercase/--no-lowercase",
        help="Include lowercase letters (a-z).",
        show_default=True,
    ),
    include_uppercase: bool = typer.Option(
        True,
        "--uppercase/--no-uppercase",
        help="Include uppercase letters (A-Z).",
        show_default=True,
    ),
    include_digits: bool = typer.Option(
        True,
        "--digits/--no-digits",
        help="Include digits (0-9).",
        show_default=True,
    ),
    include_symbols: bool = typer.Option(
        True,
        "--symbols/--no-symbols",
        help=f"Include symbols. Defaults to a limited set: ({LIMITED_SYMBOLS})",
        show_default=True,
    ),
    use_all_symbols: bool = typer.Option(
        False,
        "--all-symbols",
        help="Use the full set of punctuation symbols instead of the limited default.",
        show_default=False,
    ),
    custom_chars: str | None = typer.Option(
        None,
        "--custom",
        "-c",
        help="Use a custom set of characters, ignoring other character type flags.",
        show_default=False,
    ),
    cli: bool = typer.Option(
        False,
        help="Print just the password",
        show_default=False,
    ),
) -> None:
    """Generates a secure random password and prints it to the console."""
    character_set_parts: list[str] = []

    if custom_chars:
        character_set: str = custom_chars
    else:
        if include_lowercase:
            character_set_parts.append(string.ascii_lowercase)
        if include_uppercase:
            character_set_parts.append(string.ascii_uppercase)
        if include_digits:
            character_set_parts.append(string.digits)
        if include_symbols:
            symbol_set: LiteralString = (
                string.punctuation if use_all_symbols else LIMITED_SYMBOLS
            )
            character_set_parts.append(symbol_set)

        character_set = "".join(character_set_parts)

    if cli:
        password: str = generate_random_password(length, character_set)
        typer.secho(password, fg=typer.colors.GREEN, bold=True)
    else:
        password: str = generate_random_password(length, character_set)
        typer.secho("Generated Password:", fg=typer.colors.BRIGHT_CYAN, bold=True)
        typer.secho(f"{length=}", fg=typer.colors.CYAN)
        typer.secho(f"{character_set=}", fg=typer.colors.CYAN)
        typer.secho("---", fg=typer.colors.YELLOW)
        typer.secho(password, fg=typer.colors.GREEN, bold=True)
        typer.secho("---", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    app()
