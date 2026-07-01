# Sprint 7 Architect Handoff

Architect, please review Sprint 7 for Modular Card Game Suite and define Sprint
8.

Sprint 7 added a minimal reusable game interface / modularity boundary. It did
not add host-or-join launcher behavior, server process management from the
client, a second game, Uno or any other game, graphical UI, plugin loading,
save/load, reconnect/resume, multiple sessions, WebSockets, bots,
authentication, or CI.

Completed:

* Added shared `GameError`, `GameAction`, `GameView`, `GameActionResult`, and
  `Game` protocol in `modular_card_game_suite.games.common`.
* Exported the shared interface types from `modular_card_game_suite.games`.
* Kept reusable game-domain concepts outside `games/clown_game/`.
* Kept ClownGame-specific state and view fields in ClownGame-specific modules.
* Made `ClownGameError` inherit from shared `GameError`.
* Added `InvalidGameActionError` for unsupported action types and invalid action
  payloads.
* Made ClownGame conform to the `Game[PlayerView]` protocol.
* Added `ClownGame.submit_action()` for `play_card` and `draw_card`.
* Kept existing `play_card()` and `draw_card()` domain methods intact.
* Updated the FastAPI session to type the active game behind
  `Game[PlayerView]`.
* Updated server play/draw methods to translate existing HTTP endpoints into
  internal `GameAction` requests.
* Preserved existing server routes and response payloads.
* Preserved existing CLI command names, card display, and one-based CLI index
  behavior.
* Preserved session reset behavior.
* Added interface-level tests for protocol conformance, player views, valid
  play/draw actions, typed action errors, and game-over visibility.
* Updated architecture documentation for the Sprint 7 interface decisions.
* Updated README with a small current-MVP architecture clarification.

Partially completed:

* Fully interactive two-terminal CLI manual verification was not directly driven
  in this shell. The same server API surface was manually verified with a real
  server process, and CLI behavior is covered by automated command parsing,
  rendering, API client, retry, and reset-invalidation tests.
* Sprint 7 is packaged for user review in a pull request.

Not completed:

* No host-or-join launcher flow.
* No server process management from the client.
* No second game.
* No Uno or other additional game.
* No graphical UI or GUI framework.
* No external plugin loading.
* No save/load.
* No reconnect/resume.
* No multiple sessions.
* No WebSockets or push updates.
* No bots.
* No authentication.
* No CI.
* No broad game registry or plugin system.

Commands run and results:

* `python -m pytest`: passed, 90 tests.
* `python -m pytest --cov=src`: passed, 90 tests, 95% total coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 25 source files.

Manual verification:

* Started real local servers with
  `python -m modular_card_game_suite.server --port 8765` and
  `python -m modular_card_game_suite.server --port 8766`.
* Confirmed `/health` returned ok.
* Joined two players.
* Confirmed the game started.
* Confirmed one player was active and the other was waiting.
* Confirmed player-private hand state was available.
* Confirmed a legal play succeeded and switched turns.
* Confirmed a draw succeeded, increased hand count, and ended the turn.
* Confirmed an illegal wrong-turn draw returned 409 without corrupting state.
* Confirmed `POST /session/reset` returned reset status.
* Confirmed old player IDs returned 404 after reset.
* Confirmed new players could join after reset.
* Confirmed a new game started after reset.
* Confirmed reset-invalidated clients exit cleanly through automated CLI
  regression tests.

Known issues:

* None known beyond the documented MVP limitations.

Risks / concerns:

* `GameAction` payloads are intentionally generic mappings. Each game must keep
  payload validation close to its own action interpreter and raise typed errors.
* The server remains ClownGame-specific at the HTTP/API layer for MVP
  compatibility. A broad registry was intentionally avoided until a second game
  proves what selection/dispatch actually needs.
* Host-or-join should remain an application/session concern in Sprint 8, not a
  ClownGame rule concern.

Proposed backlog items:

* Consider a small game factory or registry only when a second game is actually
  introduced.
* Consider structured event payloads when GUI requirements are clearer.

Proposed architecture questions:

* Should Sprint 8 keep the server session ClownGame-specific until Sprint 11, or
  introduce a small game selection/factory boundary as part of host-or-join?

Please review Sprint 7 for scope fit, interface minimality, compatibility with
the existing ClownGame MVP, reset regression safety, documentation accuracy, and
readiness for Sprint 8's host-or-join launcher flow.
