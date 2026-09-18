import pytest

from backend.player import Player
from backend.team import Team
from backend.services.innings_service import InningsService
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

    player3 = Player(
        "Virat",
        "virat@example.com",
        "Batsman",
        "Right-handed"
    )

    player4 = Player(
        "Rahul",
        "rahul@example.com",
        "Batsman",
        "Right-handed"
    )

    registry.add_player("P101", player1)
    registry.add_player("P102", player2)
    registry.add_player("P103", player3)
    registry.add_player("P104", player4)

    batting_team = Team(
        "Team 1",
        "T001"
    )

    bowling_team = Team(
        "Team 2",
        "T002"
    )

    batting_team.add_player("P101")
    batting_team.add_player("P102")
    batting_team.add_player("P103")
    batting_team.add_player("P104")

    bowling_team.add_player("P101")

    return batting_team, bowling_team


def setup_innings():

    batting_team, bowling_team = setup_teams()

    service = InningsService()

    innings = service.create_innings(
        batting_team,
        bowling_team,
        2
    )

    service.set_bowler(
        innings,
        "P101"
    )

    service.set_opening_batsmen(
        innings,
        "P102",
        "P103"
    )

    return service, innings


def test_create_innings():

    batting_team, bowling_team = setup_teams()

    service = InningsService()

    innings = service.create_innings(
        batting_team,
        bowling_team,
        2
    )

    assert innings.batting_team == batting_team
    assert innings.bowling_team == bowling_team
    assert innings.overs == 2
    assert innings.total_runs == 0


def test_set_opening_batsmen():

    service, innings = setup_innings()

    assert innings.striker_id == "P102"
    assert innings.non_striker_id == "P103"

    assert "P102" in innings.batsmen_used
    assert "P103" in innings.batsmen_used


def test_set_bowler():

    batting_team, bowling_team = setup_teams()

    service = InningsService()

    innings = service.create_innings(
        batting_team,
        bowling_team,
        2
    )

    service.set_bowler(
        innings,
        "P101"
    )

    assert innings.current_bowler_id == "P101"


def test_unknown_bowler_rejected():

    batting_team, bowling_team = setup_teams()

    service = InningsService()

    innings = service.create_innings(
        batting_team,
        bowling_team,
        2
    )

    with pytest.raises(ValueError):

        service.set_bowler(
            innings,
            "P999"
        )


def test_record_ball():

    service, innings = setup_innings()

    ball = service.record_ball(
        innings,
        runs=4
    )

    assert ball.runs == 4
    assert innings.total_runs == 4
    assert innings.balls_bowled == 1


def test_record_extra():

    service, innings = setup_innings()

    ball = service.record_ball(
        innings,
        runs=0,
        extra_type="wide",
        extra_runs=1
    )

    assert ball.extra_type == "wide"
    assert ball.is_legal is False
    assert innings.total_runs == 1


def test_record_wicket():

    service, innings = setup_innings()

    ball = service.record_wicket(
        innings,
        "bowled"
    )

    assert ball.wicket is True
    assert innings.wickets_fallen == 1
    assert "P102" in innings.batsmen_out
    assert innings.batsman_stats["P102"].is_out is True


def test_replace_batsman():

    service, innings = setup_innings()

    service.record_wicket(
        innings,
        "bowled"
    )

    service.replace_batsman(
        innings,
        "P104"
    )

    assert innings.striker_id == "P104"
    assert "P104" in innings.batsmen_used