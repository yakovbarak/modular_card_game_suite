"""JSON request and response models for the server API."""

from pydantic import BaseModel, Field, field_validator


class JoinPlayerRequest(BaseModel):
    """Request body for joining the active server session."""

    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Player name must not be blank.")
        return name


class JoinPlayerResponse(BaseModel):
    """Identity assigned to a newly joined player."""

    player_id: str
    display_name: str
    player_index: int
    game_started: bool


class HandCardResponse(BaseModel):
    """One card in the requesting player's hand."""

    index: int
    display_name: str
    playable: bool


class PlayerStateResponse(BaseModel):
    """Private state visible to one player."""

    player_id: str
    display_name: str
    opponent_display_name: str | None
    hand: list[HandCardResponse]
    opponent_card_count: int
    current_face_up_card: str | None
    draw_deck_count: int
    is_your_turn: bool
    game_started: bool
    game_over: bool
    winner_display_name: str | None
    last_opponent_action: str | None


class PlayCardRequest(BaseModel):
    """Request body for playing a zero-based hand index."""

    hand_index: int


class ActionResponse(BaseModel):
    """Result of a play or draw action."""

    message: str
    state: PlayerStateResponse


class HealthResponse(BaseModel):
    """Health check payload."""

    status: str
