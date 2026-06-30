from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import modular_card_game_suite.server.main as server_main
from modular_card_game_suite.decks.regular import (
    RegularCard,
    RegularDeck,
    RegularRank,
    RegularSuit,
)
from modular_card_game_suite.games.clown_game import ClownGame
from modular_card_game_suite.server.app import create_app
from modular_card_game_suite.server.session import GameSession


def card(rank: RegularRank, suit: RegularSuit) -> RegularCard:
    return RegularCard(rank=rank, suit=suit)


def deterministic_session() -> GameSession:
    player_ids: Iterator[str] = iter(
        (
            "player-one-token",
            "player-two-token",
            "player-three-token",
            "player-four-token",
            "player-five-token",
            "player-six-token",
        )
    )
    return GameSession(
        game_factory=lambda: ClownGame(seed=42),
        id_factory=lambda: next(player_ids),
    )


@pytest.fixture
def session() -> GameSession:
    return deterministic_session()


@pytest.fixture
def client(session: GameSession, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(session=session, log_path=tmp_path / "server.log")
    with TestClient(app) as test_client:
        yield test_client


def join_two_players(client: TestClient) -> tuple[dict[str, object], dict[str, object]]:
    first = client.post("/players", json={"name": "Alice"}).json()
    second = client.post("/players", json={"name": "Bob"}).json()
    return first, second


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reset_endpoint_returns_success_before_players_join(
    client: TestClient,
) -> None:
    response = client.post("/session/reset")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {
        "status": "reset",
        "message": "Session reset. New players may now join.",
    }


def test_reset_after_one_player_allows_clean_first_join_again(
    client: TestClient,
) -> None:
    old_join = client.post("/players", json={"name": "Alice"}).json()

    reset_response = client.post("/session/reset")
    new_join_response = client.post("/players", json={"name": "Carol"})

    assert reset_response.status_code == 200
    assert client.get(f"/players/{old_join['player_id']}/state").status_code == 404
    assert new_join_response.status_code == 201
    assert new_join_response.json() == {
        "player_id": "player-two-token",
        "display_name": "Carol (Player 1)",
        "player_index": 0,
        "game_started": False,
    }


def test_reset_after_started_game_invalidates_old_players_and_starts_new_game(
    client: TestClient,
    session: GameSession,
) -> None:
    old_first, old_second = join_two_players(client)
    game = session.game
    assert game is not None
    game.current_player_index = 0
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.THREE, RegularSuit.HEARTS)]
    assert client.post(
        f"/players/{old_first['player_id']}/actions/play",
        json={"hand_index": 0},
    ).status_code == 200

    reset_response = client.post("/session/reset")
    stale_state = client.get(f"/players/{old_first['player_id']}/state")
    stale_play = client.post(
        f"/players/{old_first['player_id']}/actions/play",
        json={"hand_index": 0},
    )
    stale_draw = client.post(f"/players/{old_second['player_id']}/actions/draw")
    new_first = client.post("/players", json={"name": "Dana"})
    new_second = client.post("/players", json={"name": "Eli"})

    assert reset_response.status_code == 200
    assert session.game is not None
    assert stale_state.status_code == 404
    assert stale_play.status_code == 404
    assert stale_draw.status_code == 404
    assert new_first.status_code == 201
    assert new_first.json() == {
        "player_id": "player-three-token",
        "display_name": "Dana (Player 1)",
        "player_index": 0,
        "game_started": False,
    }
    assert new_second.status_code == 201
    assert new_second.json() == {
        "player_id": "player-four-token",
        "display_name": "Eli (Player 2)",
        "player_index": 1,
        "game_started": True,
    }

    new_state = client.get("/players/player-three-token/state").json()
    assert new_state["display_name"] == "Dana (Player 1)"
    assert new_state["opponent_display_name"] == "Eli (Player 2)"
    assert new_state["game_started"] is True
    assert new_state["last_opponent_action"] is None
    assert new_state["current_face_up_card"] != "3 of Hearts"
    assert "Alice" not in str(new_state)
    assert "Bob" not in str(new_state)


def test_reset_clears_third_player_rejection_and_duplicate_names_stay_clean(
    client: TestClient,
) -> None:
    join_two_players(client)
    rejected_before_reset = client.post("/players", json={"name": "Carol"})

    client.post("/session/reset")
    first = client.post("/players", json={"name": "Yakov"})
    second = client.post("/players", json={"name": "Yakov"})

    assert rejected_before_reset.status_code == 409
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["display_name"] == "Yakov (Player 1)"
    assert second.json()["display_name"] == "Yakov (Player 2)"


def test_server_entrypoint_defaults_and_accepts_custom_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, int]] = []

    def fake_run(application: str, host: str, port: int) -> None:
        calls.append((application, host, port))

    monkeypatch.setattr(server_main.uvicorn, "run", fake_run)

    server_main.main([])
    server_main.main(["--port", "8001"])

    assert calls == [
        ("modular_card_game_suite.server.app:app", "127.0.0.1", 8000),
        ("modular_card_game_suite.server.app:app", "127.0.0.1", 8001),
    ]


def test_first_player_joins_and_gets_waiting_state(client: TestClient) -> None:
    response = client.post("/players", json={"name": "  Yakov  "})

    assert response.status_code == 201
    assert response.json() == {
        "player_id": "player-one-token",
        "display_name": "Yakov (Player 1)",
        "player_index": 0,
        "game_started": False,
    }

    state_response = client.get("/players/player-one-token/state")
    state = state_response.json()
    assert state_response.status_code == 200
    assert state["game_started"] is False
    assert state["is_your_turn"] is False
    assert state["hand"] == []
    assert state["opponent_display_name"] is None
    assert state["current_face_up_card"] is None


def test_blank_player_name_is_rejected_as_json(client: TestClient) -> None:
    response = client.post("/players", json={"name": "   "})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_second_player_starts_game_and_duplicate_names_are_allowed(
    client: TestClient,
) -> None:
    waiting_join = client.post("/players", json={"name": "Yakov"}).json()

    assert waiting_join["game_started"] is False

    second_response = client.post("/players", json={"name": "Yakov"})

    assert second_response.status_code == 201
    assert second_response.json() == {
        "player_id": "player-two-token",
        "display_name": "Yakov (Player 2)",
        "player_index": 1,
        "game_started": True,
    }
    first_state = client.get("/players/player-one-token/state").json()
    assert first_state["display_name"] == "Yakov (Player 1)"
    assert first_state["opponent_display_name"] == "Yakov (Player 2)"


def test_third_player_and_join_after_start_are_rejected(client: TestClient) -> None:
    join_two_players(client)

    response = client.post("/players", json={"name": "Carol"})

    assert response.status_code == 409
    assert response.json() == {
        "detail": "The active game already has two players and has started."
    }


def test_invalid_player_state_is_rejected(client: TestClient) -> None:
    response = client.get("/players/not-a-player/state")

    assert response.status_code == 404
    assert response.json() == {"detail": "Unknown player ID."}


def test_started_states_are_private_and_do_not_expose_deck_order(
    client: TestClient,
) -> None:
    first, second = join_two_players(client)

    first_state = client.get(f"/players/{first['player_id']}/state").json()
    second_state = client.get(f"/players/{second['player_id']}/state").json()

    assert first_state["game_started"] is True
    assert second_state["game_started"] is True
    assert len(first_state["hand"]) == 8
    assert len(second_state["hand"]) == 8
    assert first_state["opponent_card_count"] == 8
    assert second_state["opponent_card_count"] == 8
    assert {first_state["is_your_turn"], second_state["is_your_turn"]} == {
        True,
        False,
    }
    assert all(
        set(hand_card) == {"index", "display_name", "playable"}
        for hand_card in first_state["hand"]
    )
    assert "opponent_hand" not in first_state
    assert "draw_deck" not in first_state
    first_payload = str(first_state)
    for opponent_card in second_state["hand"]:
        assert opponent_card["display_name"] not in first_payload


def test_actions_reject_invalid_player_and_pre_start_game(
    client: TestClient,
) -> None:
    client.post("/players", json={"name": "Alice"})

    invalid = client.post("/players/not-a-player/actions/draw")
    pre_start = client.post("/players/player-one-token/actions/draw")

    assert invalid.status_code == 404
    assert pre_start.status_code == 409
    assert "Waiting for a second player" in pre_start.json()["detail"]


def test_play_rejects_wrong_turn_invalid_index_and_illegal_move(
    client: TestClient,
    session: GameSession,
) -> None:
    join_two_players(client)
    game = session.game
    assert game is not None
    game.current_player_index = 0
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.THREE, RegularSuit.CLUBS)]

    wrong_turn = client.post(
        "/players/player-two-token/actions/play",
        json={"hand_index": 0},
    )
    invalid_index = client.post(
        "/players/player-one-token/actions/play",
        json={"hand_index": 9},
    )
    illegal = client.post(
        "/players/player-one-token/actions/play",
        json={"hand_index": 0},
    )

    assert wrong_turn.status_code == 409
    assert invalid_index.status_code == 400
    assert illegal.status_code == 400
    assert illegal.json()["detail"].startswith("Illegal move.")


def test_current_player_can_play_and_response_contains_updated_state(
    client: TestClient,
    session: GameSession,
) -> None:
    join_two_players(client)
    game = session.game
    assert game is not None
    game.current_player_index = 0
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [
        card(RegularRank.THREE, RegularSuit.HEARTS),
        card(RegularRank.FOUR, RegularSuit.CLUBS),
    ]

    response = client.post(
        "/players/player-one-token/actions/play",
        json={"hand_index": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "You played 3 of Hearts."
    assert payload["state"]["current_face_up_card"] == "3 of Hearts"
    assert payload["state"]["is_your_turn"] is False
    assert len(payload["state"]["hand"]) == 1


def test_current_player_can_draw_voluntarily(
    client: TestClient,
    session: GameSession,
) -> None:
    join_two_players(client)
    game = session.game
    assert game is not None
    game.current_player_index = 0
    game.draw_deck = RegularDeck(
        [card(RegularRank.ACE, RegularSuit.SPADES)]
    )
    before_count = len(game.players[0].hand)

    response = client.post("/players/player-one-token/actions/draw")

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "You drew Ace of Spades from the deck."
    assert len(payload["state"]["hand"]) == before_count + 1
    assert payload["state"]["is_your_turn"] is False


def test_winning_play_returns_winning_message_and_state(
    client: TestClient,
    session: GameSession,
) -> None:
    join_two_players(client)
    game = session.game
    assert game is not None
    game.current_player_index = 0
    game.current_face_up_card = card(RegularRank.SEVEN, RegularSuit.HEARTS)
    game.players[0].hand = [card(RegularRank.EIGHT, RegularSuit.CLUBS)]

    response = client.post(
        "/players/player-one-token/actions/play",
        json={"hand_index": 0},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "You Won!!!"
    assert payload["state"]["game_over"] is True
    assert payload["state"]["winner_display_name"] == "Alice (Player 1)"

    after_game = client.post("/players/player-one-token/actions/draw")
    assert after_game.status_code == 409


def test_draw_skip_message_when_no_cards_are_available(
    client: TestClient,
    session: GameSession,
) -> None:
    join_two_players(client)
    game = session.game
    assert game is not None
    game.current_player_index = 0
    game.draw_deck = RegularDeck([])
    game.discard_pile = []

    response = client.post("/players/player-one-token/actions/draw")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "No cards available to draw. Your turn was skipped."
    )


def test_logging_overwrites_file_and_records_server_events(tmp_path: Path) -> None:
    log_path = tmp_path / "logs" / "server.log"
    log_path.parent.mkdir()
    log_path.write_text("old log content", encoding="utf-8")
    app = create_app(session=deterministic_session(), log_path=log_path)

    with TestClient(app) as client:
        client.post("/players", json={"name": "Alice"})
        client.post("/players", json={"name": "Bob"})
        client.post("/players/not-a-player/actions/draw")
        client.post("/session/reset")

    log_content = log_path.read_text(encoding="utf-8")
    assert "old log content" not in log_content
    assert "Server startup" in log_content
    assert "Player joined" in log_content
    assert "Game started" in log_content
    assert "Draw rejected" in log_content
    assert "Session reset requested." in log_content
    assert "Server shutdown" in log_content
