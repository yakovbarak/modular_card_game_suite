from collections.abc import Iterator
from email.message import Message
from io import BytesIO
from typing import cast
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from modular_card_game_suite.client import api_client
from modular_card_game_suite.client.api_client import ApiClient, ApiError


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


@pytest.fixture
def requests_seen(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[list[tuple[str, str, bytes | None]]]:
    seen: list[tuple[str, str, bytes | None]] = []

    def fake_urlopen(request: Request, timeout: int) -> FakeResponse:
        seen.append(
            (
                request.get_method(),
                request.full_url,
                cast(bytes | None, request.data),
            )
        )
        return FakeResponse(response_for(request.full_url))

    monkeypatch.setattr(api_client, "urlopen", fake_urlopen)
    yield seen


def response_for(url: str) -> bytes:
    if url.endswith("/health"):
        return b'{"status":"ok"}'
    if url.endswith("/players"):
        return (
            b'{"player_id":"player-one-token","display_name":"Yakov (Player 1)",'
            b'"player_index":0,"game_started":false}'
        )
    if url.endswith("/state"):
        return state_response()
    if url.endswith("/actions/play"):
        return b'{"message":"You played 9 of Clubs.","state":' + state_response() + b"}"
    if url.endswith("/actions/draw"):
        return (
            b'{"message":"You drew 7 of Spades from the deck.","state":'
            + state_response()
            + b"}"
        )
    if url.endswith("/quit"):
        return b'{"status":"quit","message":"You quit the game."}'
    raise AssertionError(f"Unexpected URL {url}")


def state_response() -> bytes:
    return (
        b'{"player_id":"player-one-token","display_name":"Yakov (Player 1)",'
        b'"opponent_display_name":"Olga (Player 2)",'
        b'"hand":[{"index":0,"display_name":"9 of Clubs","playable":true}],'
        b'"opponent_card_count":6,"current_face_up_card":"7 of Hearts",'
        b'"draw_deck_count":31,"is_your_turn":true,"game_started":true,'
        b'"game_over":false,"winner_display_name":null,'
        b'"last_opponent_action":null}'
    )


def test_health_check_success(
    requests_seen: list[tuple[str, str, bytes | None]],
) -> None:
    client = ApiClient("http://example.test")

    assert client.health_check() is True
    assert requests_seen[0] == ("GET", "http://example.test/health", None)


def test_join_success(requests_seen: list[tuple[str, str, bytes | None]]) -> None:
    client = ApiClient("http://example.test")

    response = client.join_player("Yakov")

    assert response["player_id"] == "player-one-token"
    assert response["display_name"] == "Yakov (Player 1)"
    assert requests_seen[0][0] == "POST"
    assert requests_seen[0][1] == "http://example.test/players"
    assert requests_seen[0][2] == b'{"name": "Yakov"}'


def test_state_retrieval(
    requests_seen: list[tuple[str, str, bytes | None]],
) -> None:
    client = ApiClient("http://example.test")

    state = client.get_state("player-one-token")

    assert state["current_face_up_card"] == "7 of Hearts"
    assert state["hand"][0]["display_name"] == "9 of Clubs"
    assert requests_seen[0][1] == "http://example.test/players/player-one-token/state"


def test_play_sends_zero_based_hand_index(
    requests_seen: list[tuple[str, str, bytes | None]],
) -> None:
    client = ApiClient("http://example.test")

    response = client.play_card("player-one-token", 0)

    assert response["message"] == "You played 9 of Clubs."
    assert requests_seen[0][2] == b'{"hand_index": 0}'


def test_draw_call(requests_seen: list[tuple[str, str, bytes | None]]) -> None:
    client = ApiClient("http://example.test")

    response = client.draw_card("player-one-token")

    assert response["message"] == "You drew 7 of Spades from the deck."
    assert requests_seen[0][0] == "POST"
    assert requests_seen[0][1].endswith("/players/player-one-token/actions/draw")


def test_quit_call(requests_seen: list[tuple[str, str, bytes | None]]) -> None:
    client = ApiClient("http://example.test")

    response = client.quit_player("player-one-token")

    assert response == {"status": "quit", "message": "You quit the game."}
    assert requests_seen[0][0] == "POST"
    assert requests_seen[0][1].endswith("/players/player-one-token/quit")


def test_server_error_response_becomes_clean_client_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Request, timeout: int) -> FakeResponse:
        body = BytesIO(b'{"detail":"Illegal move. 3 of Spades cannot be played."}')
        raise HTTPError(request.full_url, 400, "Bad Request", Message(), body)

    monkeypatch.setattr(api_client, "urlopen", fake_urlopen)
    client = ApiClient("http://example.test")

    with pytest.raises(
        ApiError,
        match="Illegal move. 3 of Spades cannot be played.",
    ):
        client.play_card("player-one-token", 0)
