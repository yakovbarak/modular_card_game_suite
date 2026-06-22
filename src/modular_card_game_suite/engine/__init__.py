"""Generic engine abstractions."""

from modular_card_game_suite.engine.cards import Card
from modular_card_game_suite.engine.decks import Deck, EmptyDeckError

__all__ = ["Card", "Deck", "EmptyDeckError"]
