# Modular Card Game Suite

Modular Card Game Suite is a Python project that will grow into a modular suite
for card games, decks, local servers, and clients. Sprint 2 adds the first pure
in-memory game implementation: ClownGame, playable and testable through Python
objects and method calls.

## Python Version

Use Python 3.13.6.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

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
* `tests/`: automated tests for deck and ClownGame behavior.
* `docs/`: architecture, backlog, sprint report, and architect handoff notes.

## Current Limitations

* No server/client yet.
* No external plugins yet.
* No save/load yet.
* No CI yet.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
