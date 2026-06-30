# Sprint 7 Report

## Sprint Summary

Sprint 7 introduced a minimal reusable game interface in the shared game-domain
layer. The new boundary defines `Game`, `GameView`, `GameAction`,
`GameActionResult`, and `GameError` in `games/common.py`. ClownGame now conforms
to the protocol and implements `submit_action()` for the existing `play_card`
and `draw_card` actions while preserving its direct rule methods.

The FastAPI server API remains unchanged. The server session now translates the
existing ClownGame-shaped HTTP endpoints into internal `GameAction` requests.
CLI behavior, session reset behavior, and user-facing response payloads remain
unchanged.

## Definition of Done Checklist

* dedicated sprint branch exists: done (`sprint/007-game-interface`)
* work is divided into meaningful commits: done
* PR is created for user review: done
* minimal reusable game interface/protocol exists: done
* ClownGame conforms to the interface/protocol: done
* common reusable concepts are not placed inside `games/clown_game/`: done
* game-specific ClownGame concepts remain inside ClownGame modules: done
* server still works with ClownGame: done
* CLI still works with server: partially done
* session reset still works: done
* existing user-facing behavior is preserved: done
* future host-or-join flow is not implemented but is not blocked by the design:
  done
* interface-level tests are added: done
* regression tests pass: done
* README is updated if needed: done
* approved architecture decisions are documented: done
* required quality commands are run and reported: done
* Sprint 7 report exists: done
* Sprint 7 architect handoff file exists: done

## File-Change Summary

* `src/modular_card_game_suite/games/common.py`: added the minimal shared game
  protocol, action model, action result, view protocol, and `GameError` base.
* `src/modular_card_game_suite/games/clown_game/game.py`: added
  `submit_action()` and typed action payload validation while preserving
  `play_card()` and `draw_card()`.
* `src/modular_card_game_suite/games/clown_game/errors.py`: made
  `ClownGameError` inherit from `GameError` and added
  `InvalidGameActionError`.
* `src/modular_card_game_suite/games/__init__.py`: exported shared game
  interface types.
* `src/modular_card_game_suite/games/clown_game/__init__.py`: exported
  `InvalidGameActionError`.
* `src/modular_card_game_suite/server/session.py`: translated existing play and
  draw endpoint behavior into internal `GameAction` submissions.
* `tests/test_game_interface.py`: added interface/protocol behavior tests.
* `README.md`: clarified that `games/` now includes the minimal game interface.
* `docs/architecture.md`: documented approved Sprint 7 decisions.
* `docs/backlog.md`: added approved roadmap backlog items.
* `docs/sprints/sprint-007-report.md`: added this report.
* `docs/sprints/sprint-007-architect-handoff.md`: added architect handoff.

## Tests Added/Changed

* Added coverage that ClownGame conforms to the runtime-checkable `Game`
  protocol.
* Added coverage that ClownGame errors inherit from the shared `GameError`.
* Added coverage that an adapter can get player-specific state through the
  interface.
* Added coverage that an adapter can submit valid `play_card` and `draw_card`
  actions through the interface.
* Added coverage that invalid interface actions raise clear typed errors.
* Added coverage that game-over state and winner visibility are available
  through the interface.
* Existing server tests continue to cover ClownGame-shaped endpoints and session
  reset behavior.

## Commands Run and Results

* `python -m pytest`: passed, 90 tests.
* `python -m pytest --cov=src`: passed, 90 tests, 95% total coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 25 source files.

## Coverage Milestone Status

Total coverage is 95%. The new shared interface module reports 100% coverage.
Server session, server app, server models, and logging remain at 100% coverage.

## Manual Verification Checklist

Manual verification with a real local server process used:

```powershell
python -m modular_card_game_suite.server --port 8017
```

HTTP calls were made with PowerShell `Invoke-RestMethod`.

* server starts and `/health` returns ok: done
* two players can join: done
* game starts after the second player joins: done
* player state exposes hand data: done
* illegal play is rejected cleanly: done
* draw works: done
* draw switches turn: done
* legal play works after the turn switch: done
* `POST /session/reset` still works: done
* old player IDs are invalid after reset: done
* new players can join after reset: done
* new game starts after reset: done
* `logs/server.log` contains the reset event: done

Full two-interactive-client manual verification was not completed in this
non-interactive environment. CLI behavior is covered by the existing automated
client tests, including command parsing, one-based indexes, recoverable illegal
commands/actions, game-over handling, and reset invalidation handling.

Reusable/common placement was manually reviewed: the new interface types and
existing reusable game-domain models live in `games/common.py`; ClownGame-only
rules and action interpretation remain under `games/clown_game/`.

## Known Limitations

* The server API remains ClownGame-shaped for MVP compatibility.
* The server still constructs ClownGame directly; no game registry or plugin
  dispatch was added.
* Host-or-join launcher flow is not implemented in Sprint 7.

## Risks / Concerns

* `PlayerView` still contains ClownGame-specific fields because the current MVP
  API and CLI depend on them. The generic `GameView` protocol intentionally
  exposes only the common subset.
* Future games may need their own view models and action payload conventions.
  Sprint 7 keeps that flexible instead of creating a broad registry too early.

## Proposed Backlog Items

* None.

## Proposed Architecture Document Changes

* Completed the approved Sprint 7 game-interface notes in
  `docs/architecture.md`.

## Questions for Architect/User

* None.

## How to Review This PR

1. Review the shared interface types in `games/common.py`.
2. Review ClownGame's `submit_action()` implementation and
   `InvalidGameActionError`.
3. Review `GameSession.play()` and `GameSession.draw()` to confirm HTTP
   compatibility is preserved.
4. Review `tests/test_game_interface.py` for the new protocol coverage.
5. Review Sprint 7 architecture/backlog documentation.
6. Run `python -m pytest`, `python -m pytest --cov=src`,
   `python -m ruff check .`, and `python -m mypy src`.

## Architect Handoff Prompt

See `docs/sprints/sprint-007-architect-handoff.md`.
