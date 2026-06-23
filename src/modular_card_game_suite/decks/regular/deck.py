"""Regular 52-card deck with no jokers."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from random import Random
from random import shuffle as random_shuffle

from modular_card_game_suite.engine import Card, Deck, EmptyDeckError


class RegularRank(Enum):
    """Ranks for a regular deck, in ascending order."""

    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("Jack", 11)
    QUEEN = ("Queen", 12)
    KING = ("King", 13)
    ACE = ("Ace", 14)

    def __init__(self, display_name: str, order: int) -> None:
        self.display_name = display_name
        self.order = order


class RegularSuit(Enum):
    """Suits for a regular deck, in deterministic order."""

    CLUBS = ("Clubs", 1)
    DIAMONDS = ("Diamonds", 2)
    HEARTS = ("Hearts", 3)
    SPADES = ("Spades", 4)

    def __init__(self, display_name: str, order: int) -> None:
        self.display_name = display_name
        self.order = order


@dataclass(frozen=True)
class RegularCard(Card):
    """A card from a regular 52-card deck."""

    rank: RegularRank
    suit: RegularSuit

    @property
    def id(self) -> str:
        return f"regular:{self.rank.name.lower()}:{self.suit.name.lower()}"

    @property
    def display_name(self) -> str:
        return f"{self.rank.display_name} of {self.suit.display_name}"


class RegularDeck(Deck[RegularCard]):
    """A mutable regular 52-card deck."""

    def __init__(self, cards: Iterable[RegularCard] | None = None) -> None:
        if cards is not None:
            self._cards = list(cards)
            return
        self._cards = [
            RegularCard(rank=rank, suit=suit)
            for rank in RegularRank
            for suit in RegularSuit
        ]

    @property
    def cards(self) -> tuple[RegularCard, ...]:
        return tuple(self._cards)

    def draw(self) -> RegularCard:
        if not self._cards:
            raise EmptyDeckError("Cannot draw from an empty deck.")
        return self._cards.pop(0)

    def shuffle(self, seed: int | None = None) -> None:
        if seed is None:
            random_shuffle(self._cards)
            return
        Random(seed).shuffle(self._cards)

    def __len__(self) -> int:
        return len(self._cards)
