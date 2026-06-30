"""Domain errors for ClownGame."""

from modular_card_game_suite.games.common import GameError


class ClownGameError(GameError):
    """Base error for ClownGame rule and state violations."""


class GameNotStartedError(ClownGameError):
    """Raised when an action requires a started game."""


class GameAlreadyStartedError(ClownGameError):
    """Raised when starting an already-started game."""


class GameOverError(ClownGameError):
    """Raised when an action is attempted after the game is over."""


class NotPlayerTurnError(ClownGameError):
    """Raised when a player acts outside their turn."""


class InvalidPlayerError(ClownGameError):
    """Raised when an unknown player is referenced."""


class InvalidCardIndexError(ClownGameError):
    """Raised when a hand index does not refer to a card."""


class IllegalMoveError(ClownGameError):
    """Raised when a player attempts a rule-illegal move."""


class InvalidGameActionError(ClownGameError):
    """Raised when an adapter action cannot be interpreted by ClownGame."""
