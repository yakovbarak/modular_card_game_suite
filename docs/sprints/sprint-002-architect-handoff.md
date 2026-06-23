# Sprint 2 Architect Handoff Prompt

Architect, please review Sprint 2 for Modular Card Game Suite and define Sprint
3 after review.

## Completed

* Implemented pure in-memory ClownGame under
  `src/modular_card_game_suite/games/clown_game/`.
* Added shared game-domain `Player`, `PublicEvent`, `CardView`, `PlayerView`,
  and generalized `build_display_names(player_names, player_count)` in
  `src/modular_card_game_suite/games/common.py`.
* Added exactly-two-player game start with shuffled regular 52-card deck,
  8-card hands, one initial face-up card, 35 remaining draw cards, empty discard
  pile, and random starting player.
* Added deterministic setup through `seed` or injected `random.Random`.
* Added stable player indexes, display names, hands, and generalized
  duplicate-name display disambiguation such as `Yakov (Player 1)` and
  `Yakov (Player 2)`.
* Added legal-card logic:
  * same suit as current face-up card is playable.
  * higher rank than current face-up card is playable.
  * lower rank with different suit is not playable.
* Added zero-based `play_card(player_index, hand_index)` behavior.
* Added voluntary `draw_card(player_index)` behavior even when the player has a
  playable card.
* Added turn switching after successful play, draw, and skip.
* Added win detection when a player plays their last card.
* Added discard behavior where the previous face-up card moves to
  `discard_pile` and the played card becomes `current_face_up_card`.
* Added empty draw deck handling:
  * reshuffles older discard cards into the draw deck while leaving the current
    face-up card on the table.
  * draws one card after reshuffle.
  * skips the player's turn if no older discard cards exist.
  * leaves player hands untouched except for the drawn card.
* Added player-specific views that include own hand, playable flags, opponent
  card count, current face-up card, draw deck count, turn status, game-over
  status, winner, and last public opponent action.
* Added view privacy so opponent hand contents and deck order are not exposed.
* Added in-memory public event log for player registration, game start, starting
  player, play, draw, skip, and win events.
* Added typed domain errors for invalid game state and illegal actions.
* Added tests for required Sprint 2 setup, moves, illegal moves, draw,
  reshuffle, skip, views, privacy, event log behavior, and shared display-name
  handling.
* Updated `README.md` to mention pure in-memory ClownGame logic.
* Created Sprint 2 report and this architect handoff file.

## Partially Completed

* None.

## Not Completed

* None within Sprint 2 scope.

## Commands Run and Results

* `python -m pytest`: passed, 31 tests passed.
* `python -m pytest --cov=src`: passed, 31 tests passed, 97% total source
  coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 12 source files.

## Known Issues

* None known.

## Risks / Concerns

* Sprint 2 made one minimal Sprint 1 abstraction extension:
  `RegularDeck(cards=...)` now accepts an optional iterable of existing
  `RegularCard` objects. Default `RegularDeck()` behavior is unchanged. This is
  used for reshuffling older discard cards back into a draw deck.
* Public event messages are currently simple public-safe English strings. Future
  UI work may benefit from structured event payloads.

## Proposed Backlog Items

* Add a CLI adapter that translates one-based user input to ClownGame's
  zero-based hand indexes.
* Consider structured public event payloads before implementing client display.
* Consider whether a reusable engine-level card stack/deck reconstruction
  abstraction should replace or supplement `RegularDeck(cards=...)` before more
  games are added.

## Proposed Architecture Questions

* Should `RegularDeck(cards=...)` be accepted as the long-term deck
  reconstruction API, or should Sprint 3 introduce a generic engine-level
  abstraction for this?
* Should ClownGame events remain string-first for MVP client work, or should the
  event log move to structured payloads before server/client implementation?
* Should the architecture document explicitly describe the pattern of pure
  Python game engines with later server/client adapters?

## Review Request

Please review Sprint 2 for correctness, scope control, architecture fit, test
coverage, and privacy guarantees in player-specific views. After any review
issues are fixed, please define Sprint 3.
