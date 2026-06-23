"""Pure in-memory ClownGame implementation."""

from collections.abc import Sequence
from random import Random

from modular_card_game_suite.decks.regular import RegularCard, RegularDeck
from modular_card_game_suite.engine import EmptyDeckError
from modular_card_game_suite.games.clown_game.errors import (
    GameAlreadyStartedError,
    GameNotStartedError,
    GameOverError,
    IllegalMoveError,
    InvalidCardIndexError,
    InvalidPlayerError,
    NotPlayerTurnError,
)
from modular_card_game_suite.games.common import (
    CardView,
    Player,
    PlayerView,
    PublicEvent,
    build_display_names,
)

PLAYER_COUNT = 2
STARTING_HAND_SIZE = 8


class ClownGame:
    """Pure Python implementation of the Sprint 2 ClownGame MVP.

    Hand indexes are zero-based. A later CLI can translate one-based user input
    into this internal API.
    """

    def __init__(self, seed: int | None = None, rng: Random | None = None) -> None:
        self._rng = rng if rng is not None else Random(seed)
        self.players: list[Player[RegularCard]] = []
        self.draw_deck: RegularDeck | None = None
        self.discard_pile: list[RegularCard] = []
        self.current_face_up_card: RegularCard | None = None
        self.current_player_index: int | None = None
        self.winner_index: int | None = None
        self.event_log: list[PublicEvent] = []

    @property
    def is_started(self) -> bool:
        return self.draw_deck is not None

    @property
    def is_game_over(self) -> bool:
        return self.winner_index is not None

    def start(self, player_names: Sequence[str]) -> None:
        """Start a new two-player game."""

        if self.is_started:
            raise GameAlreadyStartedError("ClownGame has already started.")
        if len(player_names) != PLAYER_COUNT:
            raise InvalidPlayerError("ClownGame requires exactly 2 players.")

        display_names = build_display_names(player_names, PLAYER_COUNT)
        self.players = [
            Player(
                index=index,
                name=name,
                display_name=display_names[index],
                hand=[],
            )
            for index, name in enumerate(player_names)
        ]
        for player in self.players:
            self.event_log.append(
                PublicEvent(
                    event_type="player_registered",
                    message=f"{player.display_name} joined the game.",
                    player_index=player.index,
                )
            )

        cards = list(RegularDeck().cards)
        self._rng.shuffle(cards)
        self.draw_deck = RegularDeck(cards)

        for player in self.players:
            for _ in range(STARTING_HAND_SIZE):
                player.hand.append(self.draw_deck.draw())

        self.current_face_up_card = self.draw_deck.draw()
        self.current_player_index = self._rng.randrange(PLAYER_COUNT)
        starting_player = self.players[self.current_player_index]
        self.event_log.append(
            PublicEvent(event_type="game_started", message="ClownGame started.")
        )
        self.event_log.append(
            PublicEvent(
                event_type="starting_player_selected",
                message=f"{starting_player.display_name} starts.",
                player_index=starting_player.index,
            )
        )

    def get_current_player(self) -> Player[RegularCard]:
        self._require_started()
        return self.players[self._require_current_player_index()]

    def get_player_hand(self, player_index: int) -> tuple[RegularCard, ...]:
        player = self._get_player(player_index)
        return tuple(player.hand)

    def get_playable_cards(self, player_index: int) -> tuple[RegularCard, ...]:
        player = self._get_player(player_index)
        return tuple(card for card in player.hand if self._is_playable(card))

    def play_card(self, player_index: int, hand_index: int) -> RegularCard:
        """Play the card at zero-based ``hand_index`` for ``player_index``."""

        self._require_action_allowed(player_index)
        player = self.players[player_index]
        if hand_index < 0 or hand_index >= len(player.hand):
            raise InvalidCardIndexError(f"No card at hand index {hand_index}.")
        card = player.hand[hand_index]
        if not self._is_playable(card):
            raise IllegalMoveError(f"{card.display_name} is not playable.")

        played_card = player.hand.pop(hand_index)
        old_face_up = self._require_face_up_card()
        self.discard_pile.append(old_face_up)
        self.current_face_up_card = played_card
        self.event_log.append(
            PublicEvent(
                event_type="player_played_card",
                message=f"{player.display_name} played {played_card.display_name}.",
                player_index=player.index,
                card_display_name=played_card.display_name,
            )
        )

        if not player.hand:
            self.winner_index = player.index
            self.event_log.append(
                PublicEvent(
                    event_type="player_won",
                    message=f"{player.display_name} won.",
                    player_index=player.index,
                )
            )
        else:
            self._switch_turn()

        return played_card

    def draw_card(self, player_index: int) -> RegularCard | None:
        """Draw one card for ``player_index`` or skip if no card is available."""

        self._require_action_allowed(player_index)
        player = self.players[player_index]
        drawn_card = self._draw_available_card()

        if drawn_card is None:
            self.event_log.append(
                PublicEvent(
                    event_type="player_skipped_turn",
                    message=f"{player.display_name} skipped their turn.",
                    player_index=player.index,
                )
            )
            self._switch_turn()
            return None

        player.hand.append(drawn_card)
        self.event_log.append(
            PublicEvent(
                event_type="player_drew_card",
                message=f"{player.display_name} drew a card.",
                player_index=player.index,
            )
        )
        self._switch_turn()
        return drawn_card

    def get_player_view(self, player_index: int) -> PlayerView:
        player = self._get_player(player_index)
        opponent = self.players[1 - player.index]
        return PlayerView(
            own_display_name=player.display_name,
            opponent_display_name=opponent.display_name,
            own_hand=tuple(
                CardView(
                    display_name=card.display_name,
                    playable=self._is_playable(card),
                )
                for card in player.hand
            ),
            opponent_card_count=len(opponent.hand),
            current_face_up_card=self._require_face_up_card().display_name,
            draw_deck_count=len(self._require_draw_deck()),
            is_player_turn=self.current_player_index == player.index,
            is_game_over=self.is_game_over,
            winner_display_name=self.get_winner_display_name(),
            last_public_opponent_action=self._last_public_action_for(opponent.index),
        )

    def get_winner(self) -> Player[RegularCard] | None:
        self._require_started()
        if self.winner_index is None:
            return None
        return self.players[self.winner_index]

    def get_winner_display_name(self) -> str | None:
        if self.winner_index is None:
            return None
        return self.players[self.winner_index].display_name

    def _draw_available_card(self) -> RegularCard | None:
        draw_deck = self._require_draw_deck()
        try:
            return draw_deck.draw()
        except EmptyDeckError:
            if not self.discard_pile:
                return None

        reshuffled_cards = list(self.discard_pile)
        self._rng.shuffle(reshuffled_cards)
        self.discard_pile.clear()
        self.draw_deck = RegularDeck(reshuffled_cards)
        return self._require_draw_deck().draw()

    def _is_playable(self, card: RegularCard) -> bool:
        face_up_card = self._require_face_up_card()
        return (
            card.suit == face_up_card.suit
            or card.rank.order > face_up_card.rank.order
        )

    def _require_action_allowed(self, player_index: int) -> None:
        self._get_player(player_index)
        self._require_started()
        if self.is_game_over:
            raise GameOverError("ClownGame is over.")
        if player_index != self._require_current_player_index():
            raise NotPlayerTurnError("It is not this player's turn.")

    def _get_player(self, player_index: int) -> Player[RegularCard]:
        self._require_started()
        if player_index < 0 or player_index >= len(self.players):
            raise InvalidPlayerError(f"Unknown player index {player_index}.")
        return self.players[player_index]

    def _switch_turn(self) -> None:
        self.current_player_index = 1 - self._require_current_player_index()

    def _last_public_action_for(self, player_index: int) -> str | None:
        action_events = {
            "player_played_card",
            "player_drew_card",
            "player_skipped_turn",
            "player_won",
        }
        for event in reversed(self.event_log):
            if event.player_index == player_index and event.event_type in action_events:
                return event.message
        return None

    def _require_started(self) -> None:
        if not self.is_started:
            raise GameNotStartedError("ClownGame has not started.")

    def _require_draw_deck(self) -> RegularDeck:
        self._require_started()
        if self.draw_deck is None:
            raise GameNotStartedError("ClownGame has not started.")
        return self.draw_deck

    def _require_face_up_card(self) -> RegularCard:
        self._require_started()
        if self.current_face_up_card is None:
            raise GameNotStartedError("ClownGame has not started.")
        return self.current_face_up_card

    def _require_current_player_index(self) -> int:
        self._require_started()
        if self.current_player_index is None:
            raise GameNotStartedError("ClownGame has not started.")
        return self.current_player_index
