"""Shared game-domain models and helpers."""

from collections.abc import Sequence
from dataclasses import dataclass

from modular_card_game_suite.engine import Card


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
