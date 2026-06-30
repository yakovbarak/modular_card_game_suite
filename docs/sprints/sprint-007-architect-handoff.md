# Sprint 7 Architect Handoff

Architect, please review Sprint 7 for Modular Card Game Suite and define Sprint
8.

Sprint 7 was a minimal game interface / modularity refactor. It did not add a
host-or-join launcher flow, server process management from the client, a second
game, Uno or any other game, graphical UI, GUI framework, external plugin
loading, save/load, reconnect/resume, multiple sessions, WebSockets, bots,
authentication, CI, or a broad game registry.

Completed:

* Added minimal shared game interface types in
  `src/modular_card_game_suite/games/common.py`:
  `Game`, `GameView`, `GameAction`, `GameActionResult`, and `GameError`.
* Kept the interface practical and small:
  `GameAction` is an action type plus payload, and `GameView` exposes only
  common adapter signals for turn state, game-over state, winner display name,
  and latest public opponent action.
* Made `ClownGameError` inherit from shared `GameError`.
* Added ClownGame-specific `InvalidGameActionError`.
* Added `ClownGame.submit_action()` for `play_card` and `draw_card`.
* Preserved existing `ClownGame.play_card()` and `ClownGame.draw_card()`.
* Preserved existing ClownGame rules, view data, event logging, and
  user-facing behavior.
* Updated `GameSession.play()` and `GameSession.draw()` to translate existing
  HTTP endpoint calls into internal `GameAction` submissions.
* Preserved the current FastAPI API:
  `POST /players/{player_id}/actions/play` and
  `POST /players/{player_id}/actions/draw`.
* Preserved CLI command names and behavior.
* Preserved Sprint 6 session reset behavior.
* Added interface tests covering conformance, player-specific view access,
  valid play, valid draw, typed invalid action errors, and game-over visibility.
* Documented approved Sprint 7 architecture decisions.
* Updated approved backlog roadmap items.

Partially completed:

* Full two-interactive-client manual verification was not completed in this
  non-interactive environment. A real local server HTTP manual pass verified
  join, game start, hand/state, illegal play rejection, draw, turn switch,
  legal play, reset, old-ID invalidation, new joins, new game start, and reset
  logging. Automated CLI tests continue to cover client command behavior.

Not completed:

* No host-or-join launcher flow.
* No server process management from the client.
* No second game.
* No graphical UI or GUI framework.
* No external plugin loading.
* No save/load.
* No reconnect/resume.
* No multiple sessions.
* No WebSockets.
* No bots.
* No authentication.
* No CI.
* No full game registry or plugin dispatch.

Commands run and results:

* `python -m pytest`: passed, 90 tests.
* `python -m pytest --cov=src`: passed, 90 tests, 95% total coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 25 source files.

Manual verification:

* Started a real local server with
  `python -m modular_card_game_suite.server --port 8017`.
* Confirmed `/health` returned ok.
* Joined two players with PowerShell `Invoke-RestMethod`.
* Confirmed the game started.
* Confirmed player state exposed hand data.
* Confirmed illegal play was rejected cleanly.
* Confirmed draw worked and switched turns.
* Confirmed legal play worked after the turn switch.
* Confirmed `POST /session/reset` still worked.
* Confirmed old player IDs returned 404 after reset.
* Confirmed new players could join after reset.
* Confirmed a new game started after reset.
* Confirmed `logs/server.log` contained `Session reset requested.`.

Known issues:

* None beyond the documented MVP limitations.

Risks / concerns:

* The current `PlayerView` still contains ClownGame-specific data because the
  MVP API and CLI depend on those fields. The generic `GameView` protocol is
  intentionally narrower.
* Future games may need distinct view models and action payload conventions.
* A game registry may become useful when the second game is introduced, but
  Sprint 7 did not add one to avoid premature plugin or dispatch complexity.

Proposed backlog items:

* None.

Proposed architecture questions:

* None.

Please review Sprint 7 for scope fit, interface minimality, ClownGame
conformance, server/client compatibility, reset compatibility, and readiness
for Sprint 8's host-or-join launcher flow.
