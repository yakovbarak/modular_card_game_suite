from modular_card_game_suite.client.api_client import (
    ActionResponse,
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
    state: PlayerState = {
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
    state.update(overrides)
    return state


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
