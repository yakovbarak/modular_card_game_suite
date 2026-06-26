# Sprint 3 Report

## 1. Sprint Summary

Sprint 3 implemented a FastAPI JSON server around the existing pure in-memory
ClownGame. The server supports exactly one two-player session, opaque player
identities, automatic game start, player-private state, play and draw actions,
clean HTTP error mapping, deterministic test injection, and overwritten
server-only developer logging.

No terminal CLI, polling client, WebSockets, persistence, multiple sessions,
external plugin loading, bots, UI rendering, or generic Game interface was
added.

## 2. Definition of Done Checklist

* Dedicated Sprint 3 branch exists: done
* Work is divided into meaningful commits: done
* FastAPI dependency is added: done
* Uvicorn dependency is added: done
* Test-client dependency is added: done
* Server package and module entry point exist: done
* Server defaults to port 8000 and accepts a custom port: done
* Health endpoint exists: done
* First and second players can join: done
* Game starts automatically after player two joins: done
* Third player and join-after-start attempts are rejected: done
* Player-private state endpoint exists: done
* Play and draw endpoints exist: done
* API request and response models are JSON-only: done
* Domain and session errors map to clean HTTP errors: done
* Opponent hands and draw-deck order are not exposed: done
* Overwritten server developer log exists: done
* README server usage is documented: done
* Approved architecture decisions are documented: done
* Required server tests exist: done
* Required quality commands pass: done
* Sprint report and architect handoff exist: done
* Pull request is created for user review: done

## 3. File-Change Summary

* Added packaging metadata and editable installation support in
  `pyproject.toml` and `requirements.txt`.
* Added `src/modular_card_game_suite/server/` with the FastAPI app, JSON models,
  one-session manager, logging configuration, and module entry point.
* Added `tests/test_server.py`.
* Updated `README.md`, `docs/architecture.md`, and `docs/backlog.md`.
* Added the Sprint 3 report and architect handoff.

## 4. Tests Added/Changed

Server tests cover health, entry-point default/custom ports, name validation,
first-player waiting state, second-player automatic start, duplicate names,
third-player rejection, unknown players, private state, deck-order privacy,
pre-start actions, wrong-turn actions, invalid indexes, illegal plays, legal
plays, voluntary draw, skipped draw, winning play, post-game rejection, action
state payloads, and overwritten event logging.

Existing Sprint 1 and Sprint 2 tests remain unchanged and passing.

## 5. Commands Run and Results

* `python -m pytest`: passed, 46 tests passed.
* `python -m pytest --cov=src`: passed, 46 tests passed, 97% total source
  coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 19 source files.
* `python -m modular_card_game_suite.server --help`: passed and showed default
  entry-point arguments.

## 6. Coverage Milestone Status

Coverage passed at 97% total source coverage. The server application, models,
session manager, and logging configuration are fully covered. Uncovered server
lines are limited to the thin executable module wrapper and direct Uvicorn
startup path.

## 7. Manual Verification Checklist

* Editable installation from `requirements.txt`: done.
* Module entry point resolves: done.
* Default port 8000 is configured: done.
* Custom port argument is accepted: done.
* Health endpoint through a live local server: done.
* Server log file is created and overwritten: done.
* Log startup, join, game-start, rejection, and shutdown events: done.

## 8. Known Limitations

* The server supports one active game and cannot reset without restarting.
* Player identities exist only for the lifetime of the server process.
* There is no authentication beyond possession of the opaque player ID.
* The terminal CLI client and HTTP polling loop are not implemented.
* Event payloads remain simple public-safe strings.

## 9. Risks / Concerns

* The one-process in-memory session is intentionally unsuitable for multiple
  Uvicorn workers; each worker would have independent state.
* API display names always include `(Player 1)` or `(Player 2)` to remain stable
  before and after duplicate-name detection.
* Dependencies are intentionally unpinned, matching the existing project
  convention, so later installs may resolve newer compatible releases.

## 10. Proposed Backlog Items, If Any

* Implement the approved terminal CLI client and HTTP polling.
* Add an explicit session reset or multiple-session model in a later sprint.
* Consider structured event payloads before richer client rendering.
* Consider moving shared game-domain concepts into engine-level modules.

## 11. Proposed Architecture Document Changes, If Any

All approved Sprint 3 architecture decisions were added. No additional
architecture changes are proposed for approval in this sprint.

## 12. Questions for Architect/User

* Should the next client treat an opaque player ID as sufficient session
  identity, or should a separate reconnect token be designed later?
* Should a future reset endpoint arrive before or together with multiple
  sessions?

## 13. How to Review This PR

1. Review `server/session.py` for the one-session lifecycle and privacy mapping.
2. Review `server/app.py` for routes and HTTP error mapping.
3. Review `server/models.py` for the public JSON contract.
4. Review `server/logging_config.py` and confirm logs remain git-ignored.
5. Review `tests/test_server.py` against the Sprint 3 behavior list.
6. Run the four required quality commands.
7. Start the server and call `GET /health`.
8. Confirm no CLI, WebSocket, persistence, plugin, bot, UI, or multi-session
   scope was added.

## 14. Architect Handoff Prompt

See `docs/sprints/sprint-003-architect-handoff.md` for the copy-paste-ready
architect prompt.
