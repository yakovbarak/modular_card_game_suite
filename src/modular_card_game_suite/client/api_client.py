"""HTTP API client for the terminal ClownGame client."""

import json
from typing import Any, Literal, NotRequired, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT_SECONDS = 5


class ClientError(Exception):
    """Base client-facing error."""


class ServerConnectionError(ClientError):
    """Raised when the server cannot be reached."""


class ServerResponseError(ClientError):
    """Raised when the server response cannot be used by the client."""


class ApiError(ClientError):
    """Raised when the server returns a structured error response."""


class HandCard(TypedDict):
    """One card in the current player's hand."""

    index: int
    display_name: str
    playable: bool


class PlayerState(TypedDict):
    """Player-private state returned by the server."""

    player_id: str
    display_name: str
    opponent_display_name: str | None
    hand: list[HandCard]
    opponent_card_count: int
    current_face_up_card: str | None
    draw_deck_count: int
    is_your_turn: bool
    game_started: bool
    game_over: bool
    winner_display_name: str | None
    last_opponent_action: str | None


class JoinResponse(TypedDict):
    """Player identity assigned by the server."""

    player_id: str
    display_name: str
    player_index: int
    game_started: bool


class ActionResponse(TypedDict):
    """Action result returned by the server."""

    message: str
    state: PlayerState


class HealthResponse(TypedDict):
    """Health response returned by the server."""

    status: str


class ErrorResponse(TypedDict):
    """Structured server error payload."""

    detail: NotRequired[str | list[object]]


HttpMethod = Literal["GET", "POST"]


class ApiClient:
    """Small wrapper around the Sprint 3 HTTP API."""

    def __init__(
        self,
        server_url: str = DEFAULT_SERVER_URL,
        timeout_seconds: int = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        self.server_url = server_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds

    def health_check(self) -> bool:
        """Return whether the server health endpoint reports ok."""

        try:
            payload = self._request("GET", "health")
        except ClientError:
            return False
        return payload.get("status") == "ok"

    def join_player(self, name: str) -> JoinResponse:
        """Join the active server session."""

        payload = self._request("POST", "players", {"name": name})
        return _as_join_response(payload)

    def get_state(self, player_id: str) -> PlayerState:
        """Fetch the current private state for one player."""

        payload = self._request("GET", f"players/{player_id}/state")
        return _as_player_state(payload)

    def play_card(self, player_id: str, hand_index: int) -> ActionResponse:
        """Play a zero-based hand index."""

        payload = self._request(
            "POST",
            f"players/{player_id}/actions/play",
            {"hand_index": hand_index},
        )
        return _as_action_response(payload)

    def draw_card(self, player_id: str) -> ActionResponse:
        """Draw a card or skip when no cards are available."""

        payload = self._request("POST", f"players/{player_id}/actions/draw")
        return _as_action_response(payload)

    def _request(
        self,
        method: HttpMethod,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        body = None
        headers: dict[str, str] = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(
            urljoin(self.server_url, path),
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return _decode_payload(response.read())
        except HTTPError as error:
            raise ApiError(_format_http_error(error)) from error
        except (TimeoutError, URLError) as error:
            raise ServerConnectionError(
                f"Could not connect to server at {self.server_url.rstrip('/')}."
            ) from error


def _decode_payload(body: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ServerResponseError("Invalid server response.") from error
    if not isinstance(payload, dict):
        raise ServerResponseError("Invalid server response.")
    return payload


def _format_http_error(error: HTTPError) -> str:
    try:
        payload = _decode_payload(error.read())
    except ServerResponseError:
        return f"Server returned HTTP {error.code}."

    detail = payload.get("detail", f"Server returned HTTP {error.code}.")
    if isinstance(detail, str):
        return detail
    return "Server rejected the request."


def _as_join_response(payload: dict[str, Any]) -> JoinResponse:
    try:
        return {
            "player_id": str(payload["player_id"]),
            "display_name": str(payload["display_name"]),
            "player_index": int(payload["player_index"]),
            "game_started": bool(payload["game_started"]),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise ServerResponseError("Invalid join response from server.") from error


def _as_player_state(payload: dict[str, Any]) -> PlayerState:
    try:
        hand = [_as_hand_card(card) for card in payload["hand"]]
        return {
            "player_id": str(payload["player_id"]),
            "display_name": str(payload["display_name"]),
            "opponent_display_name": _optional_str(payload["opponent_display_name"]),
            "hand": hand,
            "opponent_card_count": int(payload["opponent_card_count"]),
            "current_face_up_card": _optional_str(payload["current_face_up_card"]),
            "draw_deck_count": int(payload["draw_deck_count"]),
            "is_your_turn": bool(payload["is_your_turn"]),
            "game_started": bool(payload["game_started"]),
            "game_over": bool(payload["game_over"]),
            "winner_display_name": _optional_str(payload["winner_display_name"]),
            "last_opponent_action": _optional_str(payload["last_opponent_action"]),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise ServerResponseError("Invalid state response from server.") from error


def _as_hand_card(payload: object) -> HandCard:
    if not isinstance(payload, dict):
        raise ServerResponseError("Invalid state response from server.")
    try:
        return {
            "index": int(payload["index"]),
            "display_name": str(payload["display_name"]),
            "playable": bool(payload["playable"]),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise ServerResponseError("Invalid state response from server.") from error


def _as_action_response(payload: dict[str, Any]) -> ActionResponse:
    try:
        state_payload = payload["state"]
        if not isinstance(state_payload, dict):
            raise ServerResponseError("Invalid action response from server.")
        return {
            "message": str(payload["message"]),
            "state": _as_player_state(state_payload),
        }
    except KeyError as error:
        raise ServerResponseError("Invalid action response from server.") from error


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)
