"""Terminal rendering helpers for the CLI client."""

from modular_card_game_suite.client.api_client import PlayerState


def format_help() -> str:
    """Return available command help text."""

    return "\n".join(
        [
            "Available commands:",
            "help - show available commands",
            "status - show current game status",
            "hand - show your hand",
            "play {index} - play a card from your hand",
            "draw - draw a card",
            "quit - exit the client",
        ]
    )


def format_hand(state: PlayerState) -> str:
    """Format the current player's hand with one-based indexes."""

    lines = ["Your hand:"]
    for user_index, card in enumerate(state["hand"], start=1):
        marker = " [playable]" if card["playable"] else ""
        lines.append(f"{user_index}. {card['display_name']}{marker}")
    return "\n".join(lines)


def format_status(state: PlayerState) -> str:
    """Format a compact game status summary."""

    lines = [
        f"Top card: {_value_or_waiting(state['current_face_up_card'])}",
        f"Draw deck: {state['draw_deck_count']} cards",
        (
            "Opponent: "
            f"{_value_or_waiting(state['opponent_display_name'])}, "
            f"{state['opponent_card_count']} cards"
        ),
    ]
    if state["last_opponent_action"]:
        lines.append(f"Opponent last action: {state['last_opponent_action']}")
    lines.append(f"Game over: {'yes' if state['game_over'] else 'no'}")
    return "\n".join(lines)


def format_turn_summary(state: PlayerState) -> str:
    """Format the full prompt-time turn summary."""

    lines = ["It is your turn.", "", format_status(state), "", format_hand(state)]
    return "\n".join(lines)


def format_waiting() -> str:
    """Format the waiting-mode message."""

    return "Waiting for opponent..."


def format_game_over(state: PlayerState) -> str:
    """Format a game-over message from the current player's perspective."""

    winner = state["winner_display_name"]
    if winner == state["display_name"]:
        return "You Won!!!"
    return f"Game over. {winner} won." if winner else "Game over."


def _value_or_waiting(value: str | None) -> str:
    return value if value is not None else "waiting"
