from typing import cast

import pytest

from modular_card_game_suite.client import main as client_main
from modular_card_game_suite.client.api_client import (
    ActionResponse,
    ApiError,
    JoinResponse,
    PlayerState,
)
from modular_card_game_suite.client.main import run_client


class FakeApiClient:
    server_url = "http://127.0.0.1:8000/"

    def __init__(self) -> None:
        self.play_indexes: list[int] = []

    def health_check(self) -> bool:
        return True

    def join_player(self, name: str) -> JoinResponse:
        assert name == "Yakov"
        return {
            "player_id": "player-one-token",
            "display_name": "Yakov (Player 1)",
            "player_index": 0,
            "game_started": True,
        }

    def get_state(self, player_id: str) -> PlayerState:
        assert player_id == "player-one-token"
        return turn_state()

    def play_card(self, player_id: str, hand_index: int) -> ActionResponse:
        assert player_id == "player-one-token"
        self.play_indexes.append(hand_index)
        return {
            "message": "You played 9 of Clubs.",
            "state": turn_state(is_your_turn=False),
        }

    def draw_card(self, player_id: str) -> ActionResponse:
        raise AssertionError("draw_card should not be called")


def turn_state(**overrides: object) -> PlayerState:
    state = {
        "player_id": "player-one-token",
        "display_name": "Yakov (Player 1)",
        "opponent_display_name": "Olga (Player 2)",
        "hand": [{"index": 0, "display_name": "9 of Clubs", "playable": True}],
        "opponent_card_count": 6,
        "current_face_up_card": "7 of Hearts",
        "draw_deck_count": 31,
        "is_your_turn": True,
        "game_started": True,
        "game_over": False,
        "winner_display_name": None,
        "last_opponent_action": None,
    }
    return cast(PlayerState, state | overrides)


def test_run_client_joins_plays_then_quits_without_prompting_while_waiting() -> None:
    api_client = FakeApiClient()
    inputs = iter(["Yakov", "play 1", "quit"])
    output: list[str] = []

    result = run_client(
        api_client,  # type: ignore[arg-type]
        input_func=lambda prompt: next(inputs),
        output_func=output.append,
        sleep_func=lambda seconds: None,
    )

    assert result == 0
    assert api_client.play_indexes == [0]
    assert "Joined as Yakov (Player 1)." in output
    assert "You played 9 of Clubs." in output


def test_run_client_continues_turn_after_api_rejects_command() -> None:
    class FirstPlayRejectedApiClient(FakeApiClient):
        def play_card(self, player_id: str, hand_index: int) -> ActionResponse:
            assert player_id == "player-one-token"
            self.play_indexes.append(hand_index)
            if len(self.play_indexes) == 1:
                raise ApiError("Illegal move. Card cannot be played.")
            return {
                "message": "You played 9 of Clubs.",
                "state": turn_state(is_your_turn=False),
            }

    api_client = FirstPlayRejectedApiClient()
    inputs = iter(["Yakov", "play 1", "play 1", "quit"])
    output: list[str] = []

    result = run_client(
        api_client,  # type: ignore[arg-type]
        input_func=lambda prompt: next(inputs),
        output_func=output.append,
        sleep_func=lambda seconds: None,
    )

    assert result == 0
    assert api_client.play_indexes == [0, 0]
    assert "Illegal move. Card cannot be played." in output
    assert "You played 9 of Clubs." in output


def test_main_builds_api_client_with_server_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    class FakeMainApiClient:
        def __init__(self, server_url: str) -> None:
            calls.append(server_url)

    def fake_run_client(api_client: object) -> int:
        assert isinstance(api_client, FakeMainApiClient)
        return 0

    monkeypatch.setattr(client_main, "ApiClient", FakeMainApiClient)
    monkeypatch.setattr(client_main, "run_client", fake_run_client)

    assert client_main.main(["--server-url", "http://127.0.0.1:8001"]) == 0
    assert calls == ["http://127.0.0.1:8001"]


def test_run_client_exits_cleanly_when_server_is_unreachable() -> None:
    class UnreachableApiClient(FakeApiClient):
        def health_check(self) -> bool:
            return False

    output: list[str] = []

    result = run_client(
        UnreachableApiClient(),  # type: ignore[arg-type]
        output_func=output.append,
    )

    assert result == 1
    assert output == [
        "Could not connect to server at http://127.0.0.1:8000.",
        "Make sure the server is running.",
    ]


def test_run_client_prints_join_error_cleanly() -> None:
    class JoinRejectedApiClient(FakeApiClient):
        def join_player(self, name: str) -> JoinResponse:
            raise ApiError("The active game already has two players and has started.")

    output: list[str] = []

    result = run_client(
        JoinRejectedApiClient(),  # type: ignore[arg-type]
        input_func=lambda prompt: "Carol",
        output_func=output.append,
    )

    assert result == 1
    assert output == ["The active game already has two players and has started."]


def test_run_client_handles_help_status_hand_draw_and_game_over() -> None:
    class DrawWinningApiClient(FakeApiClient):
        def draw_card(self, player_id: str) -> ActionResponse:
            return {
                "message": "You drew 7 of Spades from the deck.",
                "state": turn_state(
                    game_over=True,
                    winner_display_name="Yakov (Player 1)",
                ),
            }

    inputs = iter(["Yakov", "help", "status", "hand", "draw"])
    output: list[str] = []

    result = run_client(
        DrawWinningApiClient(),  # type: ignore[arg-type]
        input_func=lambda prompt: next(inputs),
        output_func=output.append,
    )

    assert result == 0
    assert any("Available commands:" in message for message in output)
    assert any("Top card: 7 of Hearts" in message for message in output)
    assert any("Your hand:" in message for message in output)
    assert "You drew 7 of Spades from the deck." in output
    assert "You Won!!!" in output


def test_run_client_waits_until_turn() -> None:
    class WaitingApiClient(FakeApiClient):
        def __init__(self) -> None:
            super().__init__()
            self.states = iter(
                [
                    turn_state(is_your_turn=False, game_started=False),
                    turn_state(is_your_turn=True, game_started=True),
                ]
            )

        def get_state(self, player_id: str) -> PlayerState:
            return next(self.states)

    inputs = iter(["Yakov", "quit"])
    output: list[str] = []
    sleeps: list[float] = []

    result = run_client(
        WaitingApiClient(),  # type: ignore[arg-type]
        input_func=lambda prompt: next(inputs),
        output_func=output.append,
        sleep_func=sleeps.append,
    )

    assert result == 0
    assert "Waiting for opponent..." in output
    assert sleeps == [1]


def test_run_client_reports_opponent_win() -> None:
    class GameOverApiClient(FakeApiClient):
        def get_state(self, player_id: str) -> PlayerState:
            return turn_state(
                is_your_turn=False,
                game_over=True,
                winner_display_name="Olga (Player 2)",
            )

    output: list[str] = []

    result = run_client(
        GameOverApiClient(),  # type: ignore[arg-type]
        input_func=lambda prompt: "Yakov",
        output_func=output.append,
    )

    assert result == 0
    assert "Game over. Olga (Player 2) won." in output
