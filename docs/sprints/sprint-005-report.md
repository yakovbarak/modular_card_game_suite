# Sprint 5 Report

## Sprint Summary

Sprint 5 hardened the playable MVP without adding major product features. The
work strengthened active-turn CLI error-recovery tests, verified game-over
behavior through existing engine/server/client layers, pinned direct dependency
versions, improved MVP demo documentation, and documented the current one-session
server limitations.

## Definition of Done Checklist

* dedicated sprint branch exists: done (`sprint/005-mvp-hardening`)
* work is divided into meaningful commits: done
* PR is created for user review: done
* all previous tests still pass: done
* meaningful new hardening tests are added: done
* recoverable active-turn client errors are tested: done
* game-over behavior is better verified: done
* MVP flow verification is documented: done
* README is improved for MVP demo usage: done
* approved hardening architecture notes are documented: done
* dependency pinning decision is made and reported: done
* coverage milestone status is assessed: done
* required quality commands are run and reported: done
* Sprint 5 report exists: done
* Sprint 5 architect handoff file exists: done

## File-Change Summary

* `tests/test_client_main.py`: added active-turn recovery tests for invalid
  indexes, unknown commands, rejected draw actions, and draw-to-waiting flow.
* `requirements.txt`: pinned direct dependencies to the installed verified
  versions and replaced `httpx2` with `httpx`.
* `README.md`: expanded MVP demo instructions, command behavior, recoverable
  illegal moves, and current limitations.
* `docs/architecture.md`: added approved Sprint 5 hardening clarifications.
* `docs/backlog.md`: added the approved future session reset item and removed
  dependency pinning because Sprint 5 completed it.
* `docs/sprints/sprint-005-report.md`: added this report.
* `docs/sprints/sprint-005-architect-handoff.md`: added architect handoff.

## Tests Added/Changed

* Added coverage that invalid active-turn `play 0` stays in the turn loop and a
  later valid `play 1` still succeeds.
* Added coverage that an unknown active-turn command stays in the turn loop and
  a later valid `play 1` still succeeds.
* Added coverage that a server-side `draw` rejection is recoverable and a later
  `draw` is accepted.
* Added coverage that a successful `draw` moves the client from turn mode into
  waiting mode.

Existing tests already cover engine win detection, server winning play response,
renderer winner/loser formatting, CLI game-over handling, server privacy, hand
one-based rendering, and API zero-based play requests.

## Commands Run and Results

* `python -m pytest`: passed, 78 tests.
* `python -m pytest --cov=src`: passed, 78 tests, 94% total coverage.
* `python -m ruff check .`: passed.
* `python -m mypy src`: passed, no issues in 25 source files.

## Coverage Milestone Status

Coverage is meaningful for the Sprint 5 MVP surface:

* deck behavior: covered
* ClownGame setup/rules/draw/reshuffle/skip/win: covered
* player-specific privacy: covered
* server join/state/play/draw/error behavior: covered
* CLI parser/renderer/API client: covered
* recoverable CLI action errors: strengthened this sprint

Total coverage is 94%. Remaining low-value gaps are mostly module entrypoint
shims and uncommon API response error branches.

## Manual Verification Checklist

Manual process verification was performed with a real local server process and
two real CLI client processes on alternate ports:

* server starts: done
* server health returns ok: done
* client 1 joins: done
* client 1 waits while alone: done
* client 2 joins: done
* game starts automatically: done
* one client enters turn mode: done
* other client waits: done
* `help` works: done
* `status` works: done
* `hand` works with one-based indexes and playable markers: done
* illegal command is recoverable: done
* illegal play is recoverable: done
* draw works: done
* turn switches: done
* server log is created/overwritten at `logs/server.log`: done

A direct HTTP manual pass additionally verified:

* first join reports `game_started=false`: done
* second join reports `game_started=true`: done
* legal play works: done
* legal play switches turn: done
* opponent hand privacy is preserved: done

The scripted terminal subprocess verification required cleanup for one client
after stdin timing was exhausted, so it should not be treated as a full
interactive human rehearsal. Game-over was not manually played to completion;
automated engine, server, renderer, and CLI tests cover game-over behavior.

## Known Limitations

* The MVP supports exactly one in-memory server session per process.
* A fresh game requires restarting the server.
* Reconnect/resume is not supported.
* Save/load is not supported.
* Multiple sessions are not supported.
* The server should run as one Uvicorn worker/process because state is in memory.
* HTTP polling is used; WebSockets are not implemented.

## Risks / Concerns

* Scripted full terminal-process tests remain timing-sensitive. Sprint 5 keeps
  stable component tests as the primary automated verification path.
* Direct dependency versions are now pinned from the current local environment.
  Future dependency upgrades should be deliberate.

## Proposed Backlog Items

* None.

## Proposed Architecture Document Changes

* Completed the approved hardening clarifications in `docs/architecture.md`.

## Questions for Architect/User

* None.

## How to Review This PR

1. Review the test additions in `tests/test_client_main.py`.
2. Review the pinned direct dependencies in `requirements.txt`.
3. Review the README demo flow and limitation wording.
4. Review the Sprint 5 architecture clarifications and backlog adjustment.
5. Run `python -m pytest`, `python -m pytest --cov=src`,
   `python -m ruff check .`, and `python -m mypy src`.

## Architect Handoff Prompt

See `docs/sprints/sprint-005-architect-handoff.md`.
