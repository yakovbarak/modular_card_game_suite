"""Developer file logging for the server adapter."""

import logging
from pathlib import Path

LOGGER_NAME = "modular_card_game_suite.server"
DEFAULT_LOG_PATH = Path("logs/server.log")


def configure_logging(log_path: Path = DEFAULT_LOG_PATH) -> logging.Logger:
    """Configure an overwritten server-only developer log."""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()

    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    return logger
