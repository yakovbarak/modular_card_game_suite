# Modular Card Game Suite

Modular Card Game Suite is a Python project that will grow into a modular suite
for card games, decks, local servers, and clients. Sprint 5 hardens a
terminal-based ClownGame MVP with one local FastAPI server process and two
terminal clients using HTTP polling.

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

## Run the MVP Demo

### 1. Start the Server

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
automated tests, the terminal client, or manual HTTP tools such as PowerShell's
`Invoke-RestMethod`.

The MVP server holds exactly one in-memory game session. Reset the session when
you want a fresh game without restarting the server process:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/session/reset
```

The response is JSON:

```json
{
  "status": "reset",
  "message": "Session reset. New players may now join."
}
```

Session reset is a local MVP/demo convenience. It clears the current in-memory
players and game state, and old player IDs become invalid. Existing terminal
clients should be restarted after a reset. Reset is not save/load, reconnect,
resume, authentication, or multiple-session support.

### 2. Start Client 1

Open a second terminal window and run:

```powershell
python -m modular_card_game_suite.client
```

Enter a player name when prompted. Client 1 joins the active session and waits
until a second player joins.

### 3. Start Client 2

Open a third terminal window and run:

```powershell
python -m modular_card_game_suite.client
```

Enter a second player name. The game starts automatically after Client 2 joins.
One terminal enters turn mode, and the other terminal stays in waiting mode
until the turn switches.

The client connects to `http://127.0.0.1:8000` by default. Override the server
URL in either client when the server uses a different port:

```powershell
python -m modular_card_game_suite.client --server-url http://127.0.0.1:8001
```

Each client checks server health, asks for a player name, joins the one active
session, waits for the opponent when needed, and automatically updates when it
becomes that player's turn.

During your turn, the client shows `Play your turn >` and accepts:

* `help`: show available commands.
* `status`: show the current top card, draw deck count, opponent card count,
  opponent last action, and game-over status.
* `hand`: show your hand with one-based indexes and playable markers.
* `play {index}`: play a one-based hand index such as `play 1`. The client
  translates this to the server API's zero-based index.
* `draw`: draw a card or skip if no cards are available.
* `quit`: exit the client.

Illegal commands and illegal moves are recoverable during turn mode. The client
shows the error and keeps the player at the turn prompt so another command can
be tried. Fatal errors, such as an unreachable server or an invalid unexpected
server response, still exit cleanly. If the server session is reset while a
client is running, the old player ID becomes invalid; the client shows a clean
restart message and exits.

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
* `client/`: terminal CLI adapter, HTTP API client, command parser, and
  renderer.
* `tests/`: automated tests for deck, ClownGame, and server behavior.
* `docs/`: architecture, backlog, sprint report, and architect handoff notes.

## Current Limitations

* Exactly one active in-memory game session per server process.
* Session reset clears the one in-memory MVP session but does not preserve or
  resume existing clients.
* No reconnect/resume.
* No save/load.
* Run the server as one Uvicorn worker/process because session state is held in
  process memory.
* Local polling only; no WebSockets yet.
* No external plugins yet.
* No CI yet.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
