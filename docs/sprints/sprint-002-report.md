# Sprint 2 Report

## 1. Sprint Summary

Sprint 2 implemented the pure in-memory ClownGame engine for exactly two
players. The game can be started, dealt, played, drawn from, reshuffled, skipped
when no draw cards are available, won, inspected through player-specific views,
and audited through an in-memory public event log.

No FastAPI server, CLI client, networking, external plugin loading, save/load,
multiple sessions, full generic `Game` interface, bot players, or UI logic was
added.

One minimal Sprint 1 abstraction extension was made: `RegularDeck` now accepts
an optional iterable of `RegularCard` objects. The default constructor still
creates the regular 52-card deck. ClownGame uses this to rebuild a draw deck
from shuffled discard cards during reshuffle.

## 2. Definition of Done Checklist

* ClownGame pure Python implementation exists: done
* ClownGame supports exactly 2 players: done
* ClownGame setup/deal/start works: done
* ClownGame supports legal card play: done
* ClownGame rejects illegal card play: done
* ClownGame supports voluntary draw: done
* ClownGame handles empty draw deck reshuffle: done
* ClownGame handles skip when no draw cards are available: done
* ClownGame detects winner: done
* ClownGame exposes player-specific views without leaking opponent hand or deck
  order: done
* ClownGame records public events: done
* Tests cover all required Sprint 2 behaviors: done
* README is updated if needed: done
* Sprint 2 report exists: done
* Sprint 2 architect handoff file exists: done
* Required commands were run and results reported: done

## 3. File-Change Summary

* Added `src/modular_card_game_suite/games/clown_game/`.
* Added shared game-domain `Player`, `PublicEvent`, `CardView`, `PlayerView`,
  and `build_display_names` in `games/common.py`.
* Added typed ClownGame domain errors.
* Added `ClownGame`.
* Added zero-based hand-index play API.
* Added deterministic setup support through `seed` or injected `random.Random`.
* Added in-memory public event log.
* Added player-specific views that hide opponent hand contents and deck order.
* Extended `RegularDeck` to accept an optional iterable of existing cards.
* Updated `README.md` to mention Sprint 2 ClownGame behavior.
* Added Sprint 2 report and architect handoff files.

## 4. Tests Added/Changed

* Added `tests/test_clown_game.py`.
* Added `tests/test_game_common.py`.
* Tests cover setup, deterministic setup, duplicate display names, pre-start
  errors, playability rules, playable markers in player views, legal play,
  turn switching, win detection, illegal action rejection, state preservation
  after illegal moves, voluntary draw, opponent draw privacy, empty deck
  reshuffle, empty deck skip, player-specific views, and event logging.
* Existing regular deck tests continue to pass.

## 5. Commands Run and Results

* `python -m pytest`: passed, 31 tests passed.
* `python -m pytest --cov=src`: passed, 31 tests passed, 97% total source
  coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 12 source files.

## 6. Coverage Milestone Status

Coverage run passed with 97% total source coverage. The uncovered lines are
minor defensive branches in ClownGame accessors and error checks, not known
missing required behavior.

## 7. Manual Verification Checklist

* Game starts with exactly two players: done.
* Each player receives 8 cards: done.
* Initial face-up card is set: done.
* Draw deck has 35 cards after setup: done.
* Discard pile starts empty: done.
* Starting player is one of the two players: done.
* Same-suit lower-rank card is playable: done.
* Higher-rank different-suit card is playable: done.
* Lower-rank different-suit card is not playable: done.
* Legal play moves old face-up card to discard pile: done.
* Legal play makes played card the new face-up card: done.
* Draw adds exactly one card and ends turn: done.
* Empty draw deck reshuffles older discard cards only: done.
* Empty draw deck with no older discard cards skips turn: done.
* Winner is set immediately after last card is played: done.
* Player views hide opponent hand contents and deck order: done.
* Event log records play, draw, skip, and win events: done.

## 8. Known Limitations

* ClownGame intentionally supports exactly two players only.
* Hand-index actions use zero-based indexes in the Python API.
* Event messages are simple English strings and are not localized.
* No server/client, persistence, bot, plugin, or generic game interface exists
  yet.

## 9. Risks / Concerns

* The `RegularDeck(cards=...)` extension should be reviewed by the architect as
  the minimal approved way to rebuild decks from known cards.
* Public event messages may eventually need structured payloads for richer UI
  rendering, but Sprint 2 keeps them simple and public-safe.

## 10. Proposed Backlog Items, If Any

* Add a CLI adapter that translates one-based user input to ClownGame's
  zero-based hand indexes.
* Consider structured public event payloads before building the client display.
* Consider whether a reusable card stack/deck-from-cards abstraction belongs in
  `engine/` before adding more games.

## 11. Proposed Architecture Document Changes, If Any

* Document that games may expose pure Python domain APIs before server/client
  adapters exist.
* Document the accepted approach for rebuilding draw decks from existing cards,
  either by keeping `RegularDeck(cards=...)` or introducing a shared engine
  abstraction later.

## 12. Questions for Architect/User

* Should ClownGame public events stay as simple strings, or should Sprint 3 move
  them toward structured event payloads for client rendering?
* Should `RegularDeck(cards=...)` be treated as the approved long-term approach
  for deck reconstruction?

## 13. How to Review This PR

1. Review `src/modular_card_game_suite/games/clown_game/game.py` for game rules,
   turn handling, reshuffle/skip behavior, win detection, and view privacy.
2. Review `src/modular_card_game_suite/games/clown_game/errors.py` for typed
   domain errors.
3. Review the minimal `RegularDeck(cards=...)` extension in
   `src/modular_card_game_suite/decks/regular/deck.py`.
4. Review `tests/test_clown_game.py` against the Sprint 2 requirements.
5. Run:

   ```powershell
   python -m pytest
   python -m pytest --cov=src
   python -m ruff check .
   python -m mypy src
   ```

6. Confirm no server/client/networking/future-sprint scope was added.

## 14. Architect Handoff Prompt

See `docs/sprints/sprint-002-architect-handoff.md` for the copy-paste-ready
architect prompt.
