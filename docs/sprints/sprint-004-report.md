# Sprint 4 Report

## 1. Sprint Summary

Sprint 4 implemented the terminal-based ClownGame CLI client. The client starts
with `python -m modular_card_game_suite.client`, checks server health, joins the
existing one-session FastAPI server, polls while waiting, shows a turn summary,
and supports explicit `help`, `status`, `hand`, `play {index}`, `draw`, and
`quit` commands.

The client keeps HTTP API communication, command parsing, terminal rendering,
and CLI orchestration separated so a future transport or richer UI can replace
one layer without rewriting the others.

No WebSockets, GUI/TUI framework, Textual, save/load, multiple sessions,
external plugin loading, bots, authentication, versioning strategy, CI, or
session reset was added.

## 2. Definition of Done Checklist

* Dedicated Sprint 4 branch exists: done
* Work is divided into meaningful commits: done
* CLI client package exists: done
* Client can be started with `python -m modular_card_game_suite.client`: done
* Client supports default server URL `http://127.0.0.1:8000`: done
* Client supports `--server-url`: done
* Client checks server health on startup: done
* Client supports joining with a player name: done
* Client stores returned `player_id`: done
* First client waits for opponent: done
* Game starts automatically after second client joins: done
* Waiting client polls automatically: done
* Waiting mode blocks commands by not showing a command prompt: done
* Turn mode shows full turn summary: done
* Prompt changes to `Play your turn >`: done
* Commands are supported: `help`, `status`, `hand`, `play {index}`, `draw`,
  `quit`: done
* CLI uses one-based indexes for `play {index}`: done
* API client translates to zero-based indexes: done
* Client displays playable markers: done
* Client displays successful play/draw messages: done
* Client displays win/loss messages: done
* Client handles invalid commands and server errors cleanly: done
* API client logic is separated from rendering/command parsing: done
* README is updated with CLI usage: done
* Approved architecture decisions are added to `docs/architecture.md`: done
* Tests cover required Sprint 4 behavior: done
* Manual verification checklist is completed or exceptions are clearly stated:
  done
* Required quality commands are run and reported: done
* Sprint 4 report exists: done
* Sprint 4 architect handoff file exists: done
* PR is created for user review: pending until branch push succeeds

## 3. File-Change Summary

* Added `src/modular_card_game_suite/client/` with the module entry point,
  CLI loop, API client, command parser, and renderer.
* Added client tests for command parsing, renderer output, API-client behavior,
  and non-blocking CLI flow pieces.
* Updated `README.md` with server and two-client startup instructions, command
  reference, server URL override, and MVP limitations.
* Updated `docs/architecture.md` with approved Sprint 4 architecture decisions.
* Updated `docs/backlog.md` by removing completed CLI/polling items and keeping
  already-approved future items.
* Added this Sprint 4 report and the Sprint 4 architect handoff.

## 4. Tests Added/Changed

Added tests for:

* command parsing of `help`, `status`, `hand`, `draw`, `quit`, and `play 1`
* invalid `play`, `play abc`, and `play 0`
* one-based display and playable markers in hand rendering
* status rendering of top card, draw deck count, and opponent count
* win/loss game-over rendering
* API health, join, state, play, draw, zero-based play payload, and clean server
  error handling
* CLI startup, server-unreachable handling, join rejection, waiting polling,
  command routing, draw success, and game-over output

Existing Sprint 1, Sprint 2, and Sprint 3 tests remain passing.

## 5. Commands Run and Results

* `python -m pytest`: passed, 73 tests passed.
* `python -m pytest --cov=src`: passed, 73 tests passed, 94% total source
  coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 25 source files.
* `python -m modular_card_game_suite.client --help`: passed and showed the
  `--server-url` argument.

## 6. Coverage Milestone Status

Coverage passed at 94% total source coverage. The lower total compared with
Sprint 3 comes from the new interactive CLI loop and executable module wrappers,
which are deliberately kept thin. Parser, renderer, API-client behavior, and
practical CLI branches are covered with focused tests.

## 7. Manual Verification Checklist

* Start server with `python -m modular_card_game_suite.server`: done.
* Start client 1 with `python -m modular_card_game_suite.client`: done.
* Enter player name: done.
* Start client 2: done.
* Enter player name: done.
* Verify game starts automatically: done.
* Verify one client shows `Play your turn >`: done.
* Verify the other client shows waiting for opponent: done.
* Verify `hand` shows one-based indexes and playable markers: done.
* Verify `play {index}` works for a legal card: done.
* Verify `draw` works: done.
* Verify turn switches automatically: done.
* Verify invalid command shows clean error: done.
* Verify game-over message: not done; game over was not manually reached.

Manual verification used live local server and two client subprocesses with
unbuffered terminal output on dynamic localhost ports. One run verified draw and
turn switching; a second run selected the first displayed playable one-based
index and verified a legal `play {index}` action.

## 8. Known Limitations

* No reconnect/resume.
* No save/load.
* One active session per server.
* Local HTTP polling only.
* No external plugins yet.
* Manual live verification did not reach game over.

## 9. Risks / Concerns

* Polling is intentionally simple and can feel delayed by up to one second.
* The client stores the bearer-style opaque player ID only in process memory.
* The client exits on normal API/client errors rather than attempting reconnect.
* The server still has no reset endpoint, so repeated manual sessions require a
  server restart.
* Dependencies remain unpinned, matching the existing project convention.

## 10. Proposed Backlog Items, If Any

* Add reconnect/resume later.
* Replace HTTP polling with WebSockets or another push mechanism later.
* Add richer TUI/GUI later.
* Add session reset or multiple sessions later.

## 11. Proposed Architecture Document Changes, If Any

The approved Sprint 4 architecture decisions were added to
`docs/architecture.md`. No additional architecture changes are proposed.

## 12. Questions for Architect/User

* Should Sprint 5 prioritize reconnect/resume, session reset, or multiple
  sessions before richer UI work?
* Is exiting immediately after game over acceptable, or should the client wait
  for Enter before closing?

## 13. How to Review This PR

1. Review `src/modular_card_game_suite/client/api_client.py` for API boundaries
   and error handling.
2. Review `src/modular_card_game_suite/client/command_parser.py` for explicit
   command parsing and one-based to zero-based index translation.
3. Review `src/modular_card_game_suite/client/renderer.py` for user-facing
   formatting and playable markers.
4. Review `src/modular_card_game_suite/client/main.py` for health check, join,
   waiting, polling, command loop, and game-over behavior.
5. Review the new client tests against the Sprint 4 behavior list.
6. Run the four required quality commands.
7. Start one server and two clients and play at least one turn from each side.
8. Confirm no WebSockets, GUI/TUI framework, persistence, plugin loading,
   authentication, bots, CI, or multi-session scope was added.

## 14. Architect Handoff Prompt

See `docs/sprints/sprint-004-architect-handoff.md` for the copy-paste-ready
architect prompt.
