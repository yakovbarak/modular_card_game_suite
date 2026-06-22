"""Generic card abstractions."""

from abc import ABC, abstractmethod


class Card(ABC):
    """Minimal base abstraction for deck-specific cards."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Stable card identifier."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable card name."""
