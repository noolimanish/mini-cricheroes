import pytest

from backend.player import Player


def test_valid_player_creation():

    player = Player(
        "Manish",
        "manish@example.com",
        "All Rounder",
        "Right-handed",
        "seam",
        "right-arm-fast"
    )

    assert player.name == "Manish"
    assert player.email == "manish@example.com"
    assert player.role == "all-rounder"


def test_invalid_role():

    with pytest.raises(ValueError):

        Player(
            "Manish",
            "manish@example.com",
            "Footballer",
            "Right-handed"
        )


def test_bowler_requires_bowling_type():

    with pytest.raises(ValueError):

        Player(
            "Manish",
            "manish@example.com",
            "Bowler",
            "Right-handed"
        )


def test_bowler_requires_bowling_style():

    with pytest.raises(ValueError):

        Player(
            "Manish",
            "manish@example.com",
            "Bowler",
            "Right-handed",
            "seam"
        )


def test_batsman_creation():

    player = Player(
        "Rahul",
        "rahul@example.com",
        "Batsman",
        "Right-handed"
    )

    assert player.role == "batsman"
    assert player.batting_style == "Right-handed"