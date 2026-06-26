"""Command-line entry point for the FastAPI server."""

import argparse
from collections.abc import Sequence

import uvicorn


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the card game server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser


def main(arguments: Sequence[str] | None = None) -> None:
    """Run Uvicorn on the configured host and port."""

    options = build_parser().parse_args(arguments)
    uvicorn.run(
        "modular_card_game_suite.server.app:app",
        host=options.host,
        port=options.port,
    )
