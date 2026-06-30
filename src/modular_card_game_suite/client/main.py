"""Terminal CLI orchestration for ClownGame."""

import argparse
import time
from collections.abc import Callable, Sequence

from modular_card_game_suite.client.api_client import (
    DEFAULT_SERVER_URL,
    ApiClient,
    ApiError,
    ClientError,
    PlayerState,
)
from modular_card_game_suite.client.command_parser import (
    CommandParseError,
    parse_command,
)
from modular_card_game_suite.client.renderer import (
    format_game_over,
    format_hand,
    format_help,
    format_status,
    format_turn_summary,
    format_waiting,
)

POLL_INTERVAL_SECONDS = 1
SESSION_INVALID_MESSAGE = (
    "Your session is no longer valid. The server may have been reset. "
    "Please restart the client."
)

InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]
SleepFunc = Callable[[float], None]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the terminal client."""

    parser = argparse.ArgumentParser(description="Play ClownGame in a terminal.")
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    args = parser.parse_args(argv)
    return run_client(ApiClient(args.server_url))


def run_client(
    api_client: ApiClient,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
    sleep_func: SleepFunc = time.sleep,
    poll_interval_seconds: float = POLL_INTERVAL_SECONDS,
) -> int:
    """Run the user-facing client loop."""

    if not api_client.health_check():
        output_func(
            f"Could not connect to server at {api_client.server_url.rstrip('/')}."
        )
        output_func("Make sure the server is running.")
        return 1

    try:
        name = input_func("Enter your name: ")
        join = api_client.join_player(name)
    except ClientError as error:
        output_func(str(error))
        return 1

    player_id = join["player_id"]
    output_func(f"Joined as {join['display_name']}.")

    try:
        while True:
            state = _wait_for_turn(
                api_client,
                player_id,
                output_func,
                sleep_func,
                poll_interval_seconds,
            )
            if state["game_over"]:
                output_func(format_game_over(state))
                return 0

            output_func(format_turn_summary(state))
            while state["is_your_turn"] and not state["game_over"]:
                raw_command = input_func("Play your turn > ")
                try:
                    command = parse_command(raw_command)
                except CommandParseError as error:
                    output_func(str(error))
                    continue

                if command.name == "quit":
                    return 0
                if command.name == "help":
                    output_func(format_help())
                elif command.name == "status":
                    output_func(format_status(state))
                elif command.name == "hand":
                    output_func(format_hand(state))
                elif command.name == "play":
                    assert command.hand_index is not None
                    try:
                        action = api_client.play_card(player_id, command.hand_index)
                    except ApiError as error:
                        if _is_session_invalid(error):
                            raise ClientError(SESSION_INVALID_MESSAGE) from error
                        output_func(str(error))
                        continue
                    else:
                        output_func(action["message"])
                        state = action["state"]
                elif command.name == "draw":
                    try:
                        action = api_client.draw_card(player_id)
                    except ApiError as error:
                        if _is_session_invalid(error):
                            raise ClientError(SESSION_INVALID_MESSAGE) from error
                        output_func(str(error))
                        continue
                    else:
                        output_func(action["message"])
                        state = action["state"]

                if state["game_over"]:
                    output_func(format_game_over(state))
                    return 0
                if not state["is_your_turn"]:
                    break
    except ClientError as error:
        output_func(str(error))
        return 1


def _wait_for_turn(
    api_client: ApiClient,
    player_id: str,
    output_func: OutputFunc,
    sleep_func: SleepFunc,
    poll_interval_seconds: float,
) -> PlayerState:
    waiting_message_printed = False
    while True:
        try:
            state = api_client.get_state(player_id)
        except ApiError as error:
            if _is_session_invalid(error):
                raise ClientError(SESSION_INVALID_MESSAGE) from error
            raise
        if state["game_over"] or state["is_your_turn"]:
            return state
        if not waiting_message_printed:
            output_func(format_waiting())
            waiting_message_printed = True
        sleep_func(poll_interval_seconds)


def _is_session_invalid(error: ApiError) -> bool:
    return str(error) == "Unknown player ID."
