"""Shared game-domain models and helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from modular_card_game_suite.engine import Card


class GameError(Exception):
    """Base error for game rule, action, and state violations."""


@dataclass(frozen=True)
class GameAction:
    """A minimal adapter-facing action request for a game."""

    action_type: str
    payload: Mapping[str, object] = field(default_factory=dict)


@runtime_checkable
class GameView(Protocol):
    """Minimal game view fields common adapters can rely on."""

    @property
    def is_player_turn(self) -> bool:
        """Return whether this view's player may act now."""

    @property
    def is_game_over(self) -> bool:
        """Return whether the game has ended."""

    @property
    def winner_display_name(self) -> str | None:
        """Return the winner display name when the game has ended."""

    @property
    def last_public_opponent_action(self) -> str | None:
        """Return the latest public opponent action visible to this player."""


@dataclass(frozen=True)
class GameActionResult[ViewT: GameView]:
    """Result of applying one adapter-facing game action."""

    action_type: str
    player_index: int
    message: str
    view: ViewT
    payload: Mapping[str, object] = field(default_factory=dict)


@runtime_checkable
class Game[ViewT: GameView](Protocol):
    """Minimal protocol implemented by in-memory games."""

    @property
    def is_started(self) -> bool:
        """Return whether the game has been started."""

    @property
    def is_game_over(self) -> bool:
        """Return whether the game has ended."""

    @property
    def current_player_index(self) -> int | None:
        """Return the player whose turn it is, if the game has started."""

    @property
    def event_log(self) -> Sequence[PublicEvent]:
        """Return public events emitted by the game."""

    def start(self, player_names: Sequence[str]) -> None:
        """Start a new game for the given player names."""

    def get_player_view(self, player_index: int) -> ViewT:
        """Return the player-specific view for one player."""

    def submit_action(
        self,
        player_index: int,
        action: GameAction,
    ) -> GameActionResult[ViewT]:
        """Apply one generic action request for a player."""


@dataclass
class Player[CardT: Card]:
    """Reusable player state for in-memory games."""

    index: int
    name: str
    display_name: str
    hand: list[CardT]


@dataclass(frozen=True)
class PublicEvent:
    """A public event visible to all players."""

    event_type: str
    message: str
    player_index: int | None = None
    card_display_name: str | None = None


@dataclass(frozen=True)
class CardView:
    """A player-visible card with game-specific metadata."""

    display_name: str
    playable: bool


@dataclass(frozen=True)
class PlayerView:
    """A player-specific view that hides opponent hand and deck order."""

    own_display_name: str
    opponent_display_name: str
    own_hand: tuple[CardView, ...]
    opponent_card_count: int
    current_face_up_card: str
    draw_deck_count: int
    is_player_turn: bool
    is_game_over: bool
    winner_display_name: str | None
    last_public_opponent_action: str | None


def build_display_names(
    player_names: Sequence[str],
    player_count: int,
) -> tuple[str, ...]:
    """Return display names, numbering duplicate names by player position."""

    if len(player_names) != player_count:
        raise ValueError("Player name count must match player count.")

    duplicate_names = {name for name in player_names if player_names.count(name) > 1}
    return tuple(
        f"{name} (Player {index + 1})" if name in duplicate_names else name
        for index, name in enumerate(player_names)
    )
