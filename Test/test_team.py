import pytest

from backend.player import Player
from backend.team import Team
from backend.player_registry import registry


def setup_players():

    registry.players.clear()

    player1 = Player(
        "Manish",
        "manish@example.com",
        "All Rounder",
        "Right-handed",
        "seam",
        "right-arm-fast"
    )

    player2 = Player(
        "Rohit",
        "rohit@example.com",
        "Batsman",
        "Left-handed"
    )

    registry.add_player("P101", player1)
    registry.add_player("P102", player2)


def test_team_creation():

    team = Team("Team 1", "T001")

    assert team.team_name == "Team 1"
    assert team.team_id == "T001"
    assert team.player_ids == []


def test_add_player():

    setup_players()

    team = Team("Team 1", "T001")

    team.add_player("P101")

    assert "P101" in team.player_ids


def test_add_unknown_player():

    setup_players()

    team = Team("Team 1", "T001")

    with pytest.raises(ValueError):

        team.add_player("P999")


def test_add_duplicate_player():

    setup_players()

    team = Team("Team 1", "T001")

    team.add_player("P101")

    with pytest.raises(ValueError):

        team.add_player("P101")


def test_set_captain():

    setup_players()

    team = Team("Team 1", "T001")

    team.add_player("P101")

    team.set_captain("P101")

    assert team.captain_id == "P101"


def test_set_captain_not_in_team():

    setup_players()

    team = Team("Team 1", "T001")

    with pytest.raises(ValueError):

        team.set_captain("P101")