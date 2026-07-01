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
* The MVP does not support reconnect or resume.
* The server should run as a single Uvicorn worker/process because session state
  is held in process memory.

## Approved Sprint 6 Decisions

* The server supports resetting the single in-memory MVP session.
* Session reset returns the server to an empty pre-game state without killing or
  restarting the process.
* Reset clears registered players, player IDs, current game state, and public
  event/session state held by the active in-memory game.
* Old player IDs become invalid after reset and are rejected by state and action
  endpoints.
* New players may join after reset, and a new ClownGame starts normally when the
  second new player joins.
* Reset is a local MVP/demo convenience, not authenticated production admin
  functionality.
* Reset does not provide save/load, reconnect/resume, multiple sessions,
  WebSockets, authentication, or an admin UI.

## Approved Sprint 7 Decisions

* A minimal reusable game interface/protocol exists in the shared game-domain
  module.
* The interface includes `Game`, `GameView`, `GameAction`,
  `GameActionResult`, and a shared `GameError` base.
* `GameAction` carries an action type plus a generic payload so adapters can
  submit actions without hard-coding endpoint details into game rules.
* `GameView` exposes only minimal common adapter signals: turn ownership,
  game-over status, winner display name, and latest public opponent action.
* ClownGame conforms to the game protocol and implements `submit_action()` for
  its current `play_card` and `draw_card` actions.
* Adapters should interact with games through the interface where practical.
  The current server session now translates existing ClownGame-shaped HTTP
  endpoints into internal `GameAction` requests.
* Common reusable game-domain concepts belong in shared modules such as
  `modular_card_game_suite.games.common`.
* Game-specific concepts remain inside game modules. ClownGame-specific fields
  such as face-up card, draw-deck count, playable hand cards, and opponent card
  count remain in the ClownGame view used by the MVP API.
* The current server API remains ClownGame-shaped for MVP compatibility.
* Future games should implement the game interface.
* The future host-or-join launcher flow belongs in an application/launcher
  layer, not inside game rules, deck modules, or the core game protocol.
