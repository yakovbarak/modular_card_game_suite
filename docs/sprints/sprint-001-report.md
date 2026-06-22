# Sprint 1 Report

## 1. Sprint Summary

Sprint 1 established the project/domain foundation for Modular Card Game Suite.
The repository now contains a Python 3.13.6 `src/` layout package, generic card
and deck abstractions, a built-in regular 52-card deck with deterministic
creation order, tests, tooling configuration, README, license, backlog, and
architecture documentation.

No game rules, ClownGame implementation, server/client code, external plugin
loading, save/load behavior, CI, or versioning strategy were added.

## 2. Definition of Done Checklist

* Project uses `src/` layout with package `modular_card_game_suite`: done
* `requirements.txt` exists with Sprint 1 dev dependencies: done
* `pyproject.toml` configures pytest, coverage, ruff, and mypy: done
* `.gitignore` exists: done
* `LICENSE` exists with MIT License: done
* `README.md` exists and includes required sections: done
* `docs/architecture.md` exists: done
* `docs/backlog.md` exists: done
* `docs/sprints/sprint-001-report.md` exists: done
* `docs/sprints/sprint-001-architect-handoff.md` exists: done
* Minimal base card abstraction exists: done
* Minimal base deck abstraction exists: done
* Regular deck implementation exists: done
* `EmptyDeckError` exists: done
* `draw()`, `shuffle(seed=None)`, `len(deck)`, and read-only `deck.cards` work: done
* Tests cover the required Sprint 1 behaviors: done
* `python -m pytest` run and result reported: done
* `python -m pytest --cov=src` run and result reported: done
* `python -m ruff check .` run and result reported: done
* `python -m mypy src` run and result reported: done
* Sprint report includes all required sections: done
* Architect handoff prompt reflects the actual final state: done

## 3. File-Change Summary

* Added Python package structure under `src/modular_card_game_suite`.
* Added generic `Card`, `Deck`, and `EmptyDeckError` abstractions under
  `engine/`.
* Added regular 52-card deck implementation under `decks/regular/`.
* Added reserved `games/` package with no game implementation.
* Added Sprint 1 automated tests under `tests/`.
* Added `requirements.txt` with `pytest`, `pytest-cov`, `ruff`, and `mypy`.
* Added `pyproject.toml` configuration for pytest, coverage, ruff, and mypy.
* Added `README.md`, `LICENSE`, `.gitignore`, architecture docs, backlog, sprint
  report, and architect handoff.

## 4. Tests Added/Changed

* Added `tests/test_regular_deck.py`.
* Tests cover package import, regular deck size, no jokers, card uniqueness,
  display names, deterministic rank-first/suit-second order, top-card draw
  behavior, deck length changes, empty deck errors, read-only card access,
  seeded and unseeded shuffle invariants, and base abstraction satisfaction.

## 5. Commands Run and Results

* `python --version`: passed, `Python 3.13.6`.
* `python -m pip install -r requirements.txt`: initial sandboxed attempt was
  blocked by network restrictions; rerun with approved network access succeeded.
* `python -m pytest`: passed, 11 tests passed.
* `python -m pytest --cov=src`: passed, 11 tests passed, 100% source coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 8 source files.

## 6. Coverage Milestone Status

Coverage run passed with 100% source coverage for Sprint 1 code. This is not a
required long-term coverage target, but Sprint 1 behavior is meaningfully
covered.

## 7. Manual Verification Checklist

* Package imports: done.
* Regular deck has 52 unique non-joker cards: done.
* Regular deck order starts with `2 of Clubs`: done.
* Regular deck order ends with `Ace of Spades`: done.
* Drawing removes the top card: done.
* Empty draw raises `EmptyDeckError`: done.
* Seeded shuffle is deterministic: done.
* Unseeded shuffle preserves count and uniqueness: done.
* `deck.cards` returns a tuple and does not expose the internal mutable list:
  done.
* Base abstractions are satisfied by the regular deck/card implementation: done.

## 8. Known Limitations

* Sprint 1 intentionally includes no game rules.
* Sprint 1 intentionally includes no ClownGame implementation.
* Sprint 1 intentionally includes no server/client implementation.
* Sprint 1 intentionally includes no external plugin system.
* Sprint 1 intentionally includes no save/load behavior.
* Sprint 1 intentionally includes no CI configuration.
* Sprint 1 intentionally includes no version constant or versioning strategy.

## 9. Risks / Concerns

* None known.

## 10. Proposed Backlog Items, If Any

* None.

## 11. Proposed Architecture Document Changes, If Any

* None.

## 12. Questions for Architect/User

* None.

## 13. How to Review This PR

1. Review `src/modular_card_game_suite/engine/` for the generic abstraction
   boundary.
2. Review `src/modular_card_game_suite/decks/regular/` for regular deck order,
   display names, drawing, shuffling, and card access behavior.
3. Review `tests/test_regular_deck.py` against the Sprint 1 required behavior.
4. Run:

   ```powershell
   python -m pytest
   python -m pytest --cov=src
   python -m ruff check .
   python -m mypy src
   ```

5. Confirm no future-sprint scope was added.

## 14. Architect Handoff Prompt

See `docs/sprints/sprint-001-architect-handoff.md` for the copy-paste-ready
architect prompt.
