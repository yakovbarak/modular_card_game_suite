# Modular Card Game Suite

Modular Card Game Suite is a Python project that will grow into a modular suite
for card games, decks, local servers, and clients. Sprint 1 establishes the
domain foundation only: generic card/deck abstractions and a built-in regular
52-card deck.

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
* `games/`: reserved for future game implementations.
* `tests/`: automated tests for Sprint 1 behavior.
* `docs/`: architecture, backlog, sprint report, and architect handoff notes.

## Sprint 1 Limitations

* No game rules yet.
* No ClownGame yet.
* No server/client yet.
* No external plugins yet.
* No save/load yet.
* No CI yet.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
