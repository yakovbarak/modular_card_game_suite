from modular_card_game_suite.client.api_client import PlayerState
from modular_card_game_suite.client.renderer import (
    format_game_over,
    format_hand,
    format_status,
)


def player_state(**overrides: object) -> PlayerState:
    state: PlayerState = {
        "player_id": "player-one-token",
        "display_name": "Yakov (Player 1)",
        "opponent_display_name": "Olga (Player 2)",
        "hand": [
            {"index": 0, "display_name": "3 of Hearts", "playable": True},
            {"index": 1, "display_name": "4 of Diamonds", "playable": False},
            {"index": 2, "display_name": "Ace of Spades", "playable": True},
        ],
        "opponent_card_count": 6,
        "current_face_up_card": "7 of Hearts",
        "draw_deck_count": 31,
        "is_your_turn": True,
        "game_started": True,
        "game_over": False,
        "winner_display_name": None,
        "last_opponent_action": "Olga drew a card.",
    }
    state.update(overrides)
    return state


def test_hand_display_uses_one_based_indexes_and_playable_markers() -> None:
    rendered = format_hand(player_state())

    assert "1. 3 of Hearts [playable]" in rendered
    assert "2. 4 of Diamonds" in rendered
    assert "2. 4 of Diamonds [playable]" not in rendered
    assert "3. Ace of Spades [playable]" in rendered
    assert "♥" not in rendered


def test_status_display_includes_core_state() -> None:
    rendered = format_status(player_state())

    assert "Top card: 7 of Hearts" in rendered
    assert "Draw deck: 31 cards" in rendered
    assert "Opponent: Olga (Player 2), 6 cards" in rendered
    assert "Opponent last action: Olga drew a card." in rendered


def test_game_over_message_for_winner() -> None:
    rendered = format_game_over(
        player_state(game_over=True, winner_display_name="Yakov (Player 1)")
    )

    assert rendered == "You Won!!!"


def test_game_over_message_for_loser() -> None:
    rendered = format_game_over(
        player_state(game_over=True, winner_display_name="Olga (Player 2)")
    )

    assert rendered == "Game over. Olga (Player 2) won."
