# Modular Card Game Suite

Modular Card Game Suite is a Python project that will grow into a modular suite
for card games, decks, local servers, and clients. Sprint 3 exposes the pure
in-memory ClownGame through a FastAPI JSON server with one active two-player
session.

## Python Version

Use Python 3.13.6.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The requirements install the project in editable mode so module entry points
work directly from the repository.

## Start the Server

The server listens on `http://127.0.0.1:8000` by default:

```powershell
python -m modular_card_game_suite.server
```

Override the port when needed:

```powershell
python -m modular_card_game_suite.server --port 8001
```

Check server health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The JSON API supports joining two players, reading player-private state, playing
a zero-based hand index, and drawing a card. It can be exercised with the
automated tests or manual HTTP tools such as PowerShell's `Invoke-RestMethod`.

The terminal CLI client is not implemented yet.

## Tests

```powershell
python -m pytest
```

## Coverage

```powershell
python -m pytest --cov=src
```

## Ruff

```powershell
python -m ruff check .
```

## Mypy

```powershell
python -m mypy src
```

## Architecture Overview

* `engine/`: generic card and deck abstractions shared by deck implementations.
* `decks/`: built-in deck implementations.
* `games/`: pure in-memory game implementations, including ClownGame.
* `server/`: FastAPI adapter and one active in-memory game session.
* `tests/`: automated tests for deck, ClownGame, and server behavior.
* `docs/`: architecture, backlog, sprint report, and architect handoff notes.

## Current Limitations

* Exactly one active in-memory game session per server process.
* No terminal CLI client yet.
* No external plugins yet.
* No save/load yet.
* No CI yet.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
