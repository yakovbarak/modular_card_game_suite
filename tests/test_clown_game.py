import pytest

from modular_card_game_suite.decks.regular import (
    RegularCard,
    RegularDeck,
    RegularRank,
    RegularSuit,
)
from modular_card_game_suite.games.clown_game import (
    ClownGame,
    GameAlreadyStartedError,
    GameNotStartedError,
    GameOverError,
    IllegalMoveError,
    InvalidCardIndexError,
    InvalidPlayerError,
    NotPlayerTurnError,
)


def card(rank: RegularRank, suit: RegularSuit) -> RegularCard:
    return RegularCard(rank=rank, suit=suit)


def started_game() -> ClownGame:
    game = ClownGame(seed=1)
    game.start(["Alice", "Bob"])
    game.current_player_index = 0
    return game


def test_game_starts_with_required_setup_state() -> None:
    game = ClownGame(seed=123)

    game.start(["Alice", "Bob"])

    assert len(game.players) == 2
    assert [len(player.hand) for player in game.players] == [8, 8]
    assert game.current_face_up_card is not None
    assert game.draw_deck is not None
    assert len(game.draw_deck) == 35
    assert game.discard_pile == []
    assert game.current_player_index in {0, 1}


def test_seeded_setup_is_deterministic() -> None:
    first = ClownGame(seed=42)
    second = ClownGame(seed=42)

    first.start(["Alice", "Bob"])
    second.start(["Alice", "Bob"])

    assert [[card.id for card in player.hand] for player in first.players] == [
        [card.id for card in player.hand] for player in second.players
    ]
    assert first.current_face_up_card == second.current_face_up_card
    assert first.current_player_index == second.current_player_index
    assert first.draw_deck is not None
    assert second.draw_deck is not None
    assert [card.id for card in first.draw_deck.cards] == [
        card.id for card in second.draw_deck.cards
    ]


def test_start_requires_exactly_two_players_and_only_starts_once() -> None:
    game = ClownGame(seed=1)

    with pytest.raises(InvalidPlayerError):
        game.start(["Alice"])

    game.start(["Alice", "Bob"])

    with pytest.raises(GameAlreadyStartedError):
        game.start(["Carol", "Dana"])


def test_duplicate_names_get_numbered_display_names() -> None:
    game = ClownGame(seed=1)

    game.start(["Yakov", "Yakov"])

    assert [player.display_name for player in game.players] == [
        "Yakov (Player 1)",
        "Yakov (Player 2)",
    ]


def test_actions_before_start_are_rejected() -> None:
    game = ClownGame(seed=1)

    with pytest.raises(GameNotStartedError):
        game.get_current_player()
    with pytest.raises(GameNotStartedError):
        game.play_card(0, 0)
    with pytest.raises(GameNotStartedError):
        game.draw_card(0)
    with pytest.raises(GameNotStartedError):
        game.get_player_view(0)


def test_playability_rules_and_view_markers() -> None:
    game = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    lower_same_suit = card(RegularRank.THREE, RegularSuit.HEARTS)
    higher_other_suit = card(RegularRank.NINE, RegularSuit.CLUBS)
    lower_other_suit = card(RegularRank.FOUR, RegularSuit.CLUBS)
    game.players[0].hand = [lower_same_suit, higher_other_suit, lower_other_suit]

    assert game.get_playable_cards(0) == (lower_same_suit, higher_other_suit)

    view = game.get_player_view(0)

    assert [card_view.playable for card_view in view.own_hand] == [
        True,
        True,
        False,
    ]


def test_current_player_can_play_legal_card_and_turn_switches() -> None:
    game = started_game()
    old_face_up = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    played = card(RegularRank.THREE, RegularSuit.HEARTS)
    other = card(RegularRank.FOUR, RegularSuit.CLUBS)
    game.current_face_up_card = old_face_up
    game.players[0].hand = [played, other]

    result = game.play_card(0, 0)

    assert result == played
    assert game.current_face_up_card == played
    assert game.discard_pile == [old_face_up]
    assert game.players[0].hand == [other]
    assert game.current_player_index == 1


def test_playing_last_card_ends_game_and_records_win() -> None:
    game = started_game()
    played = card(RegularRank.THREE, RegularSuit.HEARTS)
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [played]

    game.play_card(0, 0)

    assert game.is_game_over
    assert game.get_winner() == game.players[0]
    assert game.get_winner_display_name() == "Alice"
    assert game.current_player_index == 0
    assert game.event_log[-1].event_type == "player_won"


def test_illegal_moves_do_not_change_state() -> None:
    game = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.THREE, RegularSuit.CLUBS)]
    before = snapshot(game)

    with pytest.raises(NotPlayerTurnError):
        game.play_card(1, 0)
    assert snapshot(game) == before

    with pytest.raises(InvalidCardIndexError):
        game.play_card(0, 4)
    assert snapshot(game) == before

    with pytest.raises(InvalidCardIndexError):
        game.play_card(0, -1)
    assert snapshot(game) == before

    with pytest.raises(IllegalMoveError):
        game.play_card(0, 0)
    assert snapshot(game) == before


def test_invalid_player_is_rejected() -> None:
    game = started_game()

    with pytest.raises(InvalidPlayerError):
        game.get_player_hand(2)


def test_cannot_act_after_game_over() -> None:
    game = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.EIGHT, RegularSuit.CLUBS)]
    game.play_card(0, 0)

    with pytest.raises(GameOverError):
        game.draw_card(0)
    with pytest.raises(GameOverError):
        game.play_card(0, 0)


def test_current_player_can_draw_voluntarily_even_with_playable_card() -> None:
    game = started_game()
    drawn = card(RegularRank.ACE, RegularSuit.SPADES)
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.EIGHT, RegularSuit.CLUBS)]
    game.draw_deck = RegularDeck([drawn])

    result = game.draw_card(0)

    assert result == drawn
    assert game.players[0].hand[-1] == drawn
    assert game.draw_deck is not None
    assert len(game.draw_deck) == 0
    assert game.current_player_index == 1
    assert game.get_player_view(0).own_hand[-1].display_name == "Ace of Spades"
    opponent_view = game.get_player_view(1)
    assert opponent_view.last_public_opponent_action == "Alice drew a card."
    assert "Ace of Spades" not in opponent_view.last_public_opponent_action


def test_empty_draw_deck_reshuffles_discard_and_draws_one_card() -> None:
    game = started_game()
    current_face_up = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    first_discard = card(RegularRank.TWO, RegularSuit.CLUBS)
    second_discard = card(RegularRank.THREE, RegularSuit.DIAMONDS)
    before_hand_ids = [card.id for card in game.players[0].hand]
    opponent_hand_ids = [card.id for card in game.players[1].hand]
    game.current_face_up_card = current_face_up
    game.draw_deck = RegularDeck([])
    game.discard_pile = [first_discard, second_discard]

    drawn = game.draw_card(0)

    assert drawn in {first_discard, second_discard}
    assert game.current_face_up_card == current_face_up
    assert game.discard_pile == []
    assert game.draw_deck is not None
    assert len(game.draw_deck) == 1
    assert [card.id for card in game.players[0].hand[:-1]] == before_hand_ids
    assert [card.id for card in game.players[1].hand] == opponent_hand_ids
    assert game.players[0].hand[-1] == drawn
    assert game.current_player_index == 1


def test_empty_draw_deck_with_no_discard_skips_turn() -> None:
    game = started_game()
    before_hands = [
        [card.id for card in game.players[0].hand],
        [card.id for card in game.players[1].hand],
    ]
    game.draw_deck = RegularDeck([])
    game.discard_pile = []

    drawn = game.draw_card(0)

    assert drawn is None
    assert [
        [card.id for card in game.players[0].hand],
        [card.id for card in game.players[1].hand],
    ] == before_hands
    assert game.current_player_index == 1
    assert game.event_log[-1].event_type == "player_skipped_turn"


def test_player_specific_view_hides_opponent_hand_and_shows_public_state() -> None:
    game = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.THREE, RegularSuit.HEARTS)]
    game.players[1].hand = [
        card(RegularRank.ACE, RegularSuit.SPADES),
        card(RegularRank.KING, RegularSuit.CLUBS),
    ]
    game.play_card(0, 0)

    view = game.get_player_view(1)

    assert view.own_display_name == "Bob"
    assert view.opponent_display_name == "Alice"
    assert [card_view.display_name for card_view in view.own_hand] == [
        "Ace of Spades",
        "King of Clubs",
    ]
    assert view.opponent_card_count == 0
    assert view.current_face_up_card == "3 of Hearts"
    assert view.draw_deck_count == 35
    assert view.is_player_turn is False
    assert view.is_game_over is True
    assert view.winner_display_name == "Alice"
    assert view.last_public_opponent_action == "Alice won."
    assert "Ace of Spades" not in repr(game.get_player_view(0))


def test_last_public_opponent_action_reports_draw_without_card_identity() -> None:
    game = started_game()
    drawn = card(RegularRank.ACE, RegularSuit.SPADES)
    game.draw_deck = RegularDeck([drawn])

    game.draw_card(0)

    view = game.get_player_view(1)

    assert view.last_public_opponent_action == "Alice drew a card."
    assert "Ace of Spades" not in view.last_public_opponent_action


def test_event_log_records_play_draw_skip_and_win() -> None:
    game = started_game()
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [
        card(RegularRank.THREE, RegularSuit.HEARTS),
        card(RegularRank.FOUR, RegularSuit.HEARTS),
    ]
    game.draw_deck = RegularDeck([card(RegularRank.ACE, RegularSuit.SPADES)])

    game.play_card(0, 0)
    game.draw_card(1)
    game.draw_deck = RegularDeck([])
    game.discard_pile = []
    game.draw_card(0)
    game.current_face_up_card = card(RegularRank.TWO, RegularSuit.HEARTS)
    game.players[1].hand = [card(RegularRank.ACE, RegularSuit.CLUBS)]
    game.play_card(1, 0)

    event_types = [event.event_type for event in game.event_log]
    assert "player_played_card" in event_types
    assert "player_drew_card" in event_types
    assert "player_skipped_turn" in event_types
    assert "player_won" in event_types


def snapshot(game: ClownGame) -> tuple[object, ...]:
    draw_ids = None
    if game.draw_deck is not None:
        draw_ids = tuple(card.id for card in game.draw_deck.cards)
    return (
        tuple(tuple(card.id for card in player.hand) for player in game.players),
        draw_ids,
        tuple(card.id for card in game.discard_pile),
        game.current_face_up_card.id if game.current_face_up_card else None,
        game.current_player_index,
        game.winner_index,
        tuple((event.event_type, event.message) for event in game.event_log),
    )
