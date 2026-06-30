# Architecture

## Approved Sprint 1 Decisions

* The project is a Python application using Python 3.13.6.
* The package/import name is `modular_card_game_suite`.
* The project uses a `src/` layout.
* Generic engine abstractions live under `modular_card_game_suite.engine`.
* Built-in deck implementations live under `modular_card_game_suite.decks`.
* Future game implementations will live under `modular_card_game_suite.games`.
* Sprint 1 includes a minimal generic card abstraction with `id` and
  `display_name`.
* Sprint 1 includes a minimal generic deck abstraction with read-only card
  access, dynamic length, drawing, and shuffling.
* Cards are deck-specific. The generic engine does not assume suits, ranks,
  colors, actions, or other deck-specific concepts.
* Sprint 1 includes one built-in regular 52-card deck with no jokers.
* Regular deck rank and suit concepts are scoped to the regular deck
  implementation.
* Sprint 1 does not include game rules, a server, clients, external plugins,
  save/load behavior, CI, or versioning strategy.

## Approved Sprint 3 Decisions

* The pure game engine is independent from server and client adapters.
* The FastAPI server is an adapter around the pure ClownGame engine.
* Sprint 3 supports one active in-memory game session per server process.
* Common or reusable game classes must live in a common/shared module, not
  inside a specific game implementation.

## Approved Sprint 4 Decisions

* The CLI is an adapter over the server API.
* The CLI uses HTTP polling for the MVP.
* Client transport and API calls are encapsulated to allow future replacement.
* Terminal rendering is separated from transport and command parsing.
* CLI user-facing card indexes are one-based, while server/API indexes are
  zero-based.

## Approved Sprint 5 Hardening Clarifications

* Recoverable active-turn command errors must not exit the CLI turn loop.
* Server-side action rejections for `play` and `draw` are user-facing client
  errors during active turn mode and should allow the player to retry.
* The MVP uses one active in-memory server session per process.
* A fresh game requires restarting the server process.
* The MVP does not support reconnect or resume.
* The server should run as a single Uvicorn worker/process because session state
  is held in process memory.
