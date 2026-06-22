from collections.abc import Sequence

import pytest

import modular_card_game_suite
from modular_card_game_suite.decks.regular import (
    RegularCard,
    RegularDeck,
    RegularRank,
    RegularSuit,
)
from modular_card_game_suite.engine import Card, Deck, EmptyDeckError


def test_package_import_works() -> None:
    assert modular_card_game_suite.__name__ == "modular_card_game_suite"


def test_regular_deck_creates_52_unique_cards_with_no_jokers() -> None:
    deck = RegularDeck()

    assert len(deck) == 52
    assert len(deck.cards) == 52
    assert len({card.id for card in deck.cards}) == 52
    assert all("Joker" not in card.display_name for card in deck.cards)


def test_regular_card_display_names_match_required_format() -> None:
    assert RegularCard(RegularRank.NINE, RegularSuit.CLUBS).display_name == "9 of Clubs"
    assert (
        RegularCard(RegularRank.QUEEN, RegularSuit.HEARTS).display_name
        == "Queen of Hearts"
    )
    assert (
        RegularCard(RegularRank.ACE, RegularSuit.SPADES).display_name
        == "Ace of Spades"
    )


def test_regular_deck_order_is_rank_first_then_suit() -> None:
    deck = RegularDeck()

    expected_names = [
        f"{rank.display_name} of {suit.display_name}"
        for rank in RegularRank
        for suit in RegularSuit
    ]

    assert [card.display_name for card in deck.cards] == expected_names
    assert deck.cards[0].display_name == "2 of Clubs"
    assert deck.cards[-1].display_name == "Ace of Spades"


def test_draw_returns_and_removes_top_card() -> None:
    deck = RegularDeck()

    drawn = deck.draw()

    assert drawn.display_name == "2 of Clubs"
    assert len(deck) == 51
    assert deck.cards[0].display_name == "2 of Diamonds"


def test_drawing_all_cards_empties_deck_then_raises() -> None:
    deck = RegularDeck()

    drawn_cards = [deck.draw() for _ in range(52)]

    assert len(drawn_cards) == 52
    assert len(deck) == 0
    with pytest.raises(EmptyDeckError):
        deck.draw()


def test_cards_property_does_not_expose_mutable_internal_list() -> None:
    deck = RegularDeck()
    cards = deck.cards

    assert isinstance(cards, tuple)
    assert isinstance(cards, Sequence)

    changed_copy = list(cards)
    changed_copy.pop(0)

    assert len(changed_copy) == 51
    assert len(deck) == 52
    assert deck.cards[0].display_name == "2 of Clubs"


def test_seeded_shuffle_is_deterministic() -> None:
    first_deck = RegularDeck()
    second_deck = RegularDeck()

    first_deck.shuffle(seed=123)
    second_deck.shuffle(seed=123)

    assert [card.id for card in first_deck.cards] == [
        card.id for card in second_deck.cards
    ]


def test_seeded_shuffle_preserves_card_count_and_uniqueness() -> None:
    deck = RegularDeck()

    deck.shuffle(seed=123)

    assert len(deck) == 52
    assert len({card.id for card in deck.cards}) == 52


def test_unseeded_shuffle_preserves_card_count_and_uniqueness() -> None:
    deck = RegularDeck()

    deck.shuffle()

    assert len(deck) == 52
    assert len({card.id for card in deck.cards}) == 52


def test_regular_implementation_satisfies_base_abstractions() -> None:
    deck = RegularDeck()
    card = deck.cards[0]

    assert isinstance(deck, Deck)
    assert isinstance(card, Card)
