"""Generic deck abstractions."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar

from modular_card_game_suite.engine.cards import Card

CardT = TypeVar("CardT", bound=Card)


class EmptyDeckError(Exception):
    """Raised when attempting to draw from an empty deck."""


class Deck[CardT: Card](ABC):
    """Minimal base abstraction for mutable decks."""

    @property
    @abstractmethod
    def cards(self) -> Sequence[CardT]:
        """Read-only view of cards in current deck order."""

    @abstractmethod
    def draw(self) -> CardT:
        """Remove and return the top card."""

    @abstractmethod
    def shuffle(self, seed: int | None = None) -> None:
        """Shuffle the deck in place."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the current number of cards."""
