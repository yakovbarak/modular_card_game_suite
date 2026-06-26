"""Command parsing for the terminal client."""

from dataclasses import dataclass
from typing import Literal

CommandName = Literal["help", "status", "hand", "play", "draw", "quit"]


class CommandParseError(ValueError):
    """Raised when a user command cannot be parsed."""


@dataclass(frozen=True)
class Command:
    """A parsed user command."""

    name: CommandName
    hand_index: int | None = None


def parse_command(raw_command: str) -> Command:
    """Parse one explicit CLI command.

    The `play` command accepts one-based user input and returns a zero-based
    API hand index.
    """

    parts = raw_command.strip().split()
    if not parts:
        raise CommandParseError("Unknown command. Type help for available commands.")

    command = parts[0].lower()
    if command in {"help", "status", "hand", "draw", "quit"} and len(parts) == 1:
        return Command(name=command)  # type: ignore[arg-type]

    if command == "play":
        if len(parts) != 2:
            raise CommandParseError("Invalid command format. Usage: play {index}.")
        try:
            user_index = int(parts[1])
        except ValueError as error:
            raise CommandParseError(
                "Invalid card index. Type hand to see your cards."
            ) from error
        if user_index < 1:
            raise CommandParseError(
                "Invalid card index. Type hand to see your cards."
            )
        return Command(name="play", hand_index=user_index - 1)

    raise CommandParseError("Unknown command. Type help for available commands.")
