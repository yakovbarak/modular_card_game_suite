"""FastAPI application around one in-memory ClownGame session."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status

from modular_card_game_suite.games.clown_game import (
    GameOverError,
    IllegalMoveError,
    InvalidCardIndexError,
    NotPlayerTurnError,
)
from modular_card_game_suite.server.logging_config import (
    DEFAULT_LOG_PATH,
    LOGGER_NAME,
    configure_logging,
)
from modular_card_game_suite.server.models import (
    ActionResponse,
    HealthResponse,
    JoinPlayerRequest,
    JoinPlayerResponse,
    PlayCardRequest,
    PlayerStateResponse,
    SessionResetResponse,
)
from modular_card_game_suite.server.session import (
    GameNotReadyError,
    GameSession,
    SessionFullError,
    UnknownPlayerError,
)


def create_app(
    session: GameSession | None = None,
    log_path: Path = DEFAULT_LOG_PATH,
) -> FastAPI:
    """Create an application with an injectable deterministic session."""

    active_session = session if session is not None else GameSession()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        logger = configure_logging(log_path)
        application.state.logger = logger
        logger.info("Server startup")
        yield
        logger.info("Server shutdown")

    app = FastAPI(title="Modular Card Game Suite", lifespan=lifespan)
    app.state.session = active_session
    app.state.logger = logging.getLogger(LOGGER_NAME)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/session/reset", response_model=SessionResetResponse)
    def reset_session() -> SessionResetResponse:
        active_session.reset()
        app.state.logger.info("Session reset requested.")
        return SessionResetResponse(
            status="reset",
            message="Session reset. New players may now join.",
        )

    @app.post(
        "/players",
        response_model=JoinPlayerResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def join_player(request: JoinPlayerRequest) -> JoinPlayerResponse:
        try:
            response = active_session.join(request.name)
        except SessionFullError as error:
            app.state.logger.warning("Player join rejected: %s", error)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(error),
            ) from error

        app.state.logger.info(
            "Player joined: index=%s display_name=%s",
            response.player_index,
            response.display_name,
        )
        if response.game_started:
            app.state.logger.info("Game started")
        return response

    @app.get(
        "/players/{player_id}/state",
        response_model=PlayerStateResponse,
    )
    def get_player_state(player_id: str) -> PlayerStateResponse:
        try:
            return active_session.get_state(player_id)
        except UnknownPlayerError as error:
            raise _http_error(error) from error

    @app.post(
        "/players/{player_id}/actions/play",
        response_model=ActionResponse,
    )
    def play_card(player_id: str, request: PlayCardRequest) -> ActionResponse:
        try:
            response = active_session.play(player_id, request.hand_index)
        except (
            UnknownPlayerError,
            GameNotReadyError,
            GameOverError,
            NotPlayerTurnError,
            InvalidCardIndexError,
            IllegalMoveError,
        ) as error:
            app.state.logger.warning("Play rejected: %s", error)
            raise _http_error(error) from error

        app.state.logger.info("Play accepted: player_id=%s", player_id)
        if response.state.game_over:
            app.state.logger.info(
                "Game over: winner=%s",
                response.state.winner_display_name,
            )
        return response

    @app.post(
        "/players/{player_id}/actions/draw",
        response_model=ActionResponse,
    )
    def draw_card(player_id: str) -> ActionResponse:
        try:
            response = active_session.draw(player_id)
        except (
            UnknownPlayerError,
            GameNotReadyError,
            GameOverError,
            NotPlayerTurnError,
        ) as error:
            app.state.logger.warning("Draw rejected: %s", error)
            raise _http_error(error) from error

        app.state.logger.info("Draw accepted: player_id=%s", player_id)
        return response

    return app


def _http_error(error: Exception) -> HTTPException:
    if isinstance(error, UnknownPlayerError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(
        error,
        (GameNotReadyError, GameOverError, NotPlayerTurnError),
    ):
        status_code = status.HTTP_409_CONFLICT
    else:
        status_code = status.HTTP_400_BAD_REQUEST
    detail = (
        f"Illegal move. {error}"
        if isinstance(error, IllegalMoveError)
        else str(error)
    )
    return HTTPException(status_code=status_code, detail=detail)


app = create_app()
