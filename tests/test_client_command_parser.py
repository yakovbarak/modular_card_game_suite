import pytest

from modular_card_game_suite.client.command_parser import (
    CommandParseError,
    parse_command,
)


@pytest.mark.parametrize(
    ("raw_command", "expected_name"),
    [
        ("help", "help"),
        ("status", "status"),
        ("hand", "hand"),
        ("draw", "draw"),
        ("quit", "quit"),
    ],
)
def test_parse_simple_commands(raw_command: str, expected_name: str) -> None:
    command = parse_command(raw_command)

    assert command.name == expected_name
    assert command.hand_index is None


def test_parse_play_translates_one_based_index_to_zero_based() -> None:
    command = parse_command("play 1")

    assert command.name == "play"
    assert command.hand_index == 0


@pytest.mark.parametrize("raw_command", ["play", "play abc", "play 0"])
def test_reject_invalid_play_commands(raw_command: str) -> None:
    with pytest.raises(CommandParseError):
        parse_command(raw_command)


def test_reject_unknown_command() -> None:
    with pytest.raises(CommandParseError, match="Unknown command"):
        parse_command("dance")
