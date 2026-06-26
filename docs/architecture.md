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
