import pytest

from backend.player import Player
from backend.team import Team
from backend.services.match_service import MatchService
from backend.player_registry import registry


def setup_teams():

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

    team1 = Team("Team 1", "T001")
    team2 = Team("Team 2", "T002")

    team1.add_player("P101")
    team2.add_player("P102")

    team1.set_captain("P101")
    team2.set_captain("P102")

    return team1, team2


def test_create_match():

    team1, team2 = setup_teams()

    service = MatchService()

    match = service.create_match(
        "M001",
        team1,
        team2,
        "Uppal Ground",
        "Tennis",
        10
    )

    assert match.match_id == "M001"
    assert match.team1 == team1
    assert match.team2 == team2
    assert match.overs == 10
    assert match.status == "scheduled"


def test_conduct_toss():

    team1, team2 = setup_teams()

    service = MatchService()

    match = service.create_match(
        "M001",
        team1,
        team2,
        "Uppal Ground",
        "Tennis",
        10
    )

    result = service.conduct_toss(
        match,
        team1,
        "heads"
    )

    assert result[0] == "heads"
    assert result[1] in (team1, team2)
    assert result[2] in ("heads", "tails")


def test_choose_toss_decision():

    team1, team2 = setup_teams()

    service = MatchService()

    match = service.create_match(
        "M001",
        team1,
        team2,
        "Uppal Ground",
        "Tennis",
        10
    )

    match.toss_winner = team1

    batting_team, bowling_team = (
        service.choose_toss_decision(
            match,
            "bat"
        )
    )

    assert batting_team == team1
    assert bowling_team == team2
    assert match.toss_decision == "bat"


def test_invalid_match_creation():

    team1, team2 = setup_teams()

    service = MatchService()

    with pytest.raises(ValueError):

        service.create_match(
            "M001",
            team1,
            team2,
            "Uppal Ground",
            "Football",
            10
        )


def test_invalid_toss_decision():

    team1, team2 = setup_teams()

    service = MatchService()

    match = service.create_match(
        "M001",
        team1,
        team2,
        "Uppal Ground",
        "Tennis",
        10
    )

    match.toss_winner = team1

    with pytest.raises(ValueError):

        service.choose_toss_decision(
            match,
            "invalid"
        )