"""One active in-memory ClownGame session."""

from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from modular_card_game_suite.games.clown_game import ClownGame
from modular_card_game_suite.games.common import Game, GameAction, PlayerView
from modular_card_game_suite.server.models import (
    ActionResponse,
    HandCardResponse,
    JoinPlayerResponse,
    PlayerQuitResponse,
    PlayerStateResponse,
)


class SessionError(Exception):
    """Base error for server session state violations."""


class UnknownPlayerError(SessionError):
    """Raised when an opaque player ID is not part of the session."""


class SessionFullError(SessionError):
    """Raised when a player tries to join a full session."""


class GameNotReadyError(SessionError):
    """Raised when an action is attempted before the game starts."""


class SessionBlockedError(SessionError):
    """Raised when the active session cannot currently accept game actions."""


@dataclass(frozen=True)
class SessionPlayer:
    """Server identity mapped to a ClownGame player index."""

    player_id: str
    name: str
    display_name: str
    player_index: int


class GameSession:
    """Manage exactly one two-player ClownGame for one server process."""

    def __init__(
        self,
        game_factory: Callable[[], Game[PlayerView]] = ClownGame,
        id_factory: Callable[[], str] = lambda: uuid4().hex,
    ) -> None:
        self._game_factory = game_factory
        self._id_factory = id_factory
        self._lock = RLock()
        self._players: list[SessionPlayer] = []
        self._players_by_id: dict[str, SessionPlayer] = {}
        self._session_status = "waiting_for_players"
        self._blocked_message: str | None = None
        self._vacated_player_index: int | None = None
        self.game: Game[PlayerView] | None = None

    @property
    def game_started(self) -> bool:
        return self.game is not None

    def reset(self) -> None:
        """Return the in-memory session to its initial empty state."""

        with self._lock:
            self._players.clear()
            self._players_by_id.clear()
            self._session_status = "waiting_for_players"
            self._blocked_message = None
            self._vacated_player_index = None
            self.game = None

    def join(self, name: str) -> JoinPlayerResponse:
        """Join the session and start the game when player two arrives."""

        with self._lock:
            if self._session_status == "waiting_for_replacement":
                return self._join_replacement(name)

            if len(self._players) >= 2:
                raise SessionFullError(
                    "The active game already has two players and has started."
                )

            player_index = len(self._players)
            player = SessionPlayer(
                player_id=self._id_factory(),
                name=name,
                display_name=f"{name} (Player {player_index + 1})",
                player_index=player_index,
            )
            self._players.append(player)
            self._players_by_id[player.player_id] = player

            if len(self._players) == 2:
                self._start_game()

            return JoinPlayerResponse(
                player_id=player.player_id,
                display_name=player.display_name,
                player_index=player.player_index,
                game_started=self.game_started,
            )

    def quit(self, player_id: str) -> PlayerQuitResponse:
        """Mark a player as gone and block the session if the game needs them."""

        with self._lock:
            player = self._get_player(player_id)
            self._players_by_id.pop(player.player_id)
            self._players = [
                joined
                for joined in self._players
                if joined.player_id != player.player_id
            ]

            if self.game is None:
                self._session_status = "waiting_for_players"
                self._blocked_message = None
                self._vacated_player_index = None
            elif self._players:
                self.game = None
                self._session_status = "waiting_for_replacement"
                self._vacated_player_index = player.player_index
                self._blocked_message = (
                    f"{player.display_name} quit the game."
                )
            else:
                self.game = None
                self._session_status = "waiting_for_players"
                self._blocked_message = None
                self._vacated_player_index = None

            return PlayerQuitResponse(
                status="quit",
                message="You quit the game.",
            )

    def get_state(self, player_id: str) -> PlayerStateResponse:
        """Return state visible to one opaque player identity."""

        with self._lock:
            player = self._get_player(player_id)
            if self.game is None:
                return self._waiting_state(player)
            return self._started_state(player)

    def play(self, player_id: str, hand_index: int) -> ActionResponse:
        """Play one card and return the updated private state."""

        with self._lock:
            player = self._get_player(player_id)
            self._reject_if_blocked()
            game = self._require_game()
            action_result = game.submit_action(
                player.player_index,
                GameAction("play_card", {"hand_index": hand_index}),
            )
            return ActionResponse(
                message=action_result.message,
                state=self._started_state_from_view(player, action_result.view),
            )

    def draw(self, player_id: str) -> ActionResponse:
        """Draw a card or skip and return the updated private state."""

        with self._lock:
            player = self._get_player(player_id)
            self._reject_if_blocked()
            game = self._require_game()
            action_result = game.submit_action(
                player.player_index,
                GameAction("draw_card"),
            )
            return ActionResponse(
                message=action_result.message,
                state=self._started_state_from_view(player, action_result.view),
            )

    def _get_player(self, player_id: str) -> SessionPlayer:
        try:
            return self._players_by_id[player_id]
        except KeyError as error:
            raise UnknownPlayerError("Unknown player ID.") from error

    def _reject_if_blocked(self) -> None:
        if self._session_status == "waiting_for_replacement":
            raise SessionBlockedError(
                "The game cannot continue until a replacement player joins."
            )

    def _require_game(self) -> Game[PlayerView]:
        if self.game is None:
            raise GameNotReadyError(
                "The game has not started. Waiting for a second player."
            )
        return self.game

    def _waiting_state(self, player: SessionPlayer) -> PlayerStateResponse:
        if self._session_status == "waiting_for_replacement":
            return PlayerStateResponse(
                player_id=player.player_id,
                display_name=player.display_name,
                opponent_display_name=None,
                hand=[],
                opponent_card_count=0,
                current_face_up_card=None,
                draw_deck_count=0,
                is_your_turn=False,
                game_started=False,
                game_over=False,
                winner_display_name=None,
                last_opponent_action=None,
                session_status="waiting_for_replacement",
                message=self._blocked_message,
                available_session_actions=[
                    "reset_session",
                    "wait_for_replacement",
                ],
            )

        opponent = next(
            (
                joined
                for joined in self._players
                if joined.player_index != player.player_index
            ),
            None,
        )
        return PlayerStateResponse(
            player_id=player.player_id,
            display_name=player.display_name,
            opponent_display_name=(
                opponent.display_name if opponent is not None else None
            ),
            hand=[],
            opponent_card_count=0,
            current_face_up_card=None,
            draw_deck_count=0,
            is_your_turn=False,
            game_started=False,
            game_over=False,
            winner_display_name=None,
            last_opponent_action=None,
            session_status="waiting_for_players",
        )

    def _started_state(self, player: SessionPlayer) -> PlayerStateResponse:
        game = self._require_game()
        view = game.get_player_view(player.player_index)
        return self._started_state_from_view(player, view)

    def _started_state_from_view(
        self,
        player: SessionPlayer,
        view: PlayerView,
    ) -> PlayerStateResponse:
        return PlayerStateResponse(
            player_id=player.player_id,
            display_name=view.own_display_name,
            opponent_display_name=view.opponent_display_name,
            hand=[
                HandCardResponse(
                    index=index,
                    display_name=card.display_name,
                    playable=card.playable,
                )
                for index, card in enumerate(view.own_hand)
            ],
            opponent_card_count=view.opponent_card_count,
            current_face_up_card=view.current_face_up_card,
            draw_deck_count=view.draw_deck_count,
            is_your_turn=view.is_player_turn,
            game_started=True,
            game_over=view.is_game_over,
            winner_display_name=view.winner_display_name,
            last_opponent_action=view.last_public_opponent_action,
            session_status="active",
        )

    def _join_replacement(self, name: str) -> JoinPlayerResponse:
        if self._vacated_player_index is None or len(self._players) != 1:
            raise SessionFullError("The session is not ready for a replacement player.")

        replacement = SessionPlayer(
            player_id=self._id_factory(),
            name=name,
            display_name=f"{name} (Player {self._vacated_player_index + 1})",
            player_index=self._vacated_player_index,
        )
        self._players.append(replacement)
        self._players.sort(key=lambda player: player.player_index)
        self._players_by_id[replacement.player_id] = replacement
        self._blocked_message = None
        self._vacated_player_index = None
        self._start_game()
        return JoinPlayerResponse(
            player_id=replacement.player_id,
            display_name=replacement.display_name,
            player_index=replacement.player_index,
            game_started=True,
        )

    def _start_game(self) -> None:
        game = self._game_factory()
        game.start([joined.display_name for joined in self._players])
        self.game = game
        self._session_status = "active"
