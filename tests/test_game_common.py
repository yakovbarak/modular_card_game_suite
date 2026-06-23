import pytest

from modular_card_game_suite.games import build_display_names


def test_build_display_names_keeps_unique_names() -> None:
    assert build_display_names(["Alice", "Bob", "Carol"], 3) == (
        "Alice",
        "Bob",
        "Carol",
    )


def test_build_display_names_numbers_only_duplicate_names() -> None:
    assert build_display_names(["Yakov", "Maya", "Yakov", "Maya"], 4) == (
        "Yakov (Player 1)",
        "Maya (Player 2)",
        "Yakov (Player 3)",
        "Maya (Player 4)",
    )


def test_build_display_names_rejects_count_mismatch() -> None:
    with pytest.raises(ValueError):
        build_display_names(["Alice", "Bob"], 3)
