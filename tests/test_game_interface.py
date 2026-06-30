import pytest

from modular_card_game_suite.decks.regular import (
    RegularCard,
    RegularDeck,
    RegularRank,
    RegularSuit,
)
from modular_card_game_suite.games import Game, GameAction, GameError, PlayerView
from modular_card_game_suite.games.clown_game import (
    ClownGame,
    ClownGameError,
    InvalidGameActionError,
)


def card(rank: RegularRank, suit: RegularSuit) -> RegularCard:
    return RegularCard(rank=rank, suit=suit)


def started_game() -> ClownGame:
    game = ClownGame(seed=1)
    game.start(["Alice", "Bob"])
    game.current_player_index = 0
    return game


def test_clown_game_conforms_to_game_protocol() -> None:
    game = started_game()

    assert isinstance(game, Game)
    assert issubclass(ClownGameError, GameError)


def test_adapter_can_get_player_specific_view_through_interface() -> None:
    game: Game[PlayerView] = started_game()

    view = game.get_player_view(0)

    assert view.own_display_name == "Alice"
    assert view.opponent_display_name == "Bob"
    assert view.is_player_turn is True
    assert view.is_game_over is False


def test_adapter_can_submit_valid_play_action_through_interface() -> None:
    game: Game[PlayerView] = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [
        card(RegularRank.THREE, RegularSuit.HEARTS),
        card(RegularRank.FOUR, RegularSuit.CLUBS),
    ]

    result = game.submit_action(0, GameAction("play_card", {"hand_index": 0}))

    assert result.action_type == "play_card"
    assert result.player_index == 0
    assert result.message == "You played 3 of Hearts."
    assert result.payload == {"card_display_name": "3 of Hearts"}
    assert result.view.current_face_up_card == "3 of Hearts"
    assert result.view.is_player_turn is False


def test_adapter_can_submit_valid_draw_action_through_interface() -> None:
    game: Game[PlayerView] = started_game()
    game.draw_deck = RegularDeck([card(RegularRank.ACE, RegularSuit.SPADES)])

    result = game.submit_action(0, GameAction("draw_card"))

    assert result.action_type == "draw_card"
    assert result.message == "You drew Ace of Spades from the deck."
    assert result.payload == {"card_display_name": "Ace of Spades"}
    assert result.view.is_player_turn is False


def test_invalid_interface_actions_raise_clear_typed_errors() -> None:
    game: Game[PlayerView] = started_game()

    with pytest.raises(
        InvalidGameActionError,
        match="Unsupported ClownGame action 'trade_card'",
    ):
        game.submit_action(0, GameAction("trade_card"))

    with pytest.raises(
        InvalidGameActionError,
        match="requires integer payload field 'hand_index'",
    ):
        game.submit_action(0, GameAction("play_card", {"hand_index": "0"}))


def test_game_over_status_is_visible_through_interface() -> None:
    game: Game[PlayerView] = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.EIGHT, RegularSuit.CLUBS)]

    result = game.submit_action(0, GameAction("play_card", {"hand_index": 0}))

    assert game.is_game_over is True
    assert game.current_player_index == 0
    assert result.message == "You Won!!!"
    assert result.view.is_game_over is True
    assert result.view.winner_display_name == "Alice"
