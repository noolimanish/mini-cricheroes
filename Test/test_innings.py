import pytest

from backend.player import Player
from backend.team import Team
from backend.innings import Innings
from backend.player_registry import registry


def setup_innings():

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

    innings = Innings(
        batting_team,
        bowling_team,
        2
    )

    innings.current_bowler_id = "P101"

    return innings


def test_innings_creation():

    innings = setup_innings()

    assert innings.overs == 2
    assert innings.total_runs == 0
    assert innings.wickets_fallen == 0
    assert innings.balls_bowled == 0
    assert innings.balls == []
    assert innings.overs_data == []


def test_set_opening_batsmen():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    assert innings.striker_id == "P101"
    assert innings.non_striker_id == "P102"

    assert "P101" in innings.batsmen_used
    assert "P102" in innings.batsmen_used

    assert "P101" in innings.batsman_stats
    assert "P102" in innings.batsman_stats


def test_same_player_cannot_open_both_ends():

    innings = setup_innings()

    with pytest.raises(ValueError):

        innings.set_opening_batsmen(
            "P101",
            "P101"
        )


def test_unknown_opening_batsman_rejected():

    innings = setup_innings()

    with pytest.raises(ValueError):

        innings.set_opening_batsmen(
            "P999",
            "P102"
        )


def test_create_over_requires_bowler():

    innings = setup_innings()

    innings.current_bowler_id = None

    with pytest.raises(ValueError):

        innings.create_over()


def test_create_over():

    innings = setup_innings()

    over = innings.create_over()

    assert over.over_number == 1
    assert over.bowler_id == "P101"
    assert innings.current_over == 1
    assert len(innings.overs_data) == 1


def test_normal_ball():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    ball = innings.record_ball(
        runs=4
    )

    assert ball.runs == 4
    assert innings.total_runs == 4
    assert innings.balls_bowled == 1
    assert len(innings.balls) == 1

    stats = innings.batsman_stats["P101"]

    assert stats.runs == 4
    assert stats.balls_faced == 1
    assert stats.fours == 1


def test_single_run_changes_strike():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    innings.record_ball(
        runs=1
    )

    assert innings.striker_id == "P102"
    assert innings.non_striker_id == "P101"


def test_wide_does_not_count_as_legal_ball():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    ball = innings.record_ball(
        runs=0,
        extra_type="wide",
        extra_runs=1
    )

    assert ball.is_legal is False
    assert innings.total_runs == 1
    assert innings.balls_bowled == 0


def test_bye_counts_as_legal_ball():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    ball = innings.record_ball(
        runs=0,
        extra_type="bye",
        extra_runs=1
    )

    assert ball.is_legal is True
    assert innings.total_runs == 1
    assert innings.balls_bowled == 1


def test_leg_bye_counts_as_legal_ball():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    ball = innings.record_ball(
        runs=0,
        extra_type="leg-bye",
        extra_runs=1
    )

    assert ball.is_legal is True
    assert innings.total_runs == 1
    assert innings.balls_bowled == 1


def test_no_ball_does_not_count_as_legal_ball():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    ball = innings.record_ball(
        runs=0,
        extra_type="no-ball",
        extra_runs=1
    )

    assert ball.is_legal is False
    assert innings.total_runs == 1
    assert innings.balls_bowled == 0


def test_negative_runs_rejected():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    with pytest.raises(ValueError):

        innings.record_ball(
            runs=-1
        )


def test_invalid_extra_rejected():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    with pytest.raises(ValueError):

        innings.record_ball(
            extra_type="invalid",
            extra_runs=1
        )


def test_six_legal_balls_complete_over():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    for _ in range(6):

        innings.record_ball(
            runs=0
        )

    assert innings.balls_bowled == 6
    assert innings.overs_display == "1.0"
    assert innings.overs_completed == 1


def test_new_over_created_after_six_balls():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    for _ in range(6):

        innings.record_ball(
            runs=0
        )

    innings.record_ball(
        runs=2
    )

    assert len(innings.overs_data) == 2
    assert innings.current_over == 2
    assert innings.overs_data[1].over_number == 2


def test_wicket():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    ball = innings.record_wicket(
        "bowled"
    )

    assert ball.wicket is True
    assert ball.wicket_type == "bowled"

    assert innings.wickets_fallen == 1
    assert "P101" in innings.batsmen_out

    assert innings.batsman_stats["P101"].is_out is True


def test_replace_dismissed_batsman():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    innings.record_wicket(
        "bowled"
    )

    innings.replace_batsman(
        "P103"
    )

    assert innings.striker_id == "P103"
    assert "P103" in innings.batsmen_used
    assert "P103" in innings.batsman_stats


def test_replace_unknown_batsman_rejected():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    innings.record_wicket(
        "bowled"
    )

    with pytest.raises(ValueError):

        innings.replace_batsman(
            "P999"
        )


def test_replace_without_wicket_rejected():

    innings = setup_innings()

    innings.set_opening_batsmen(
        "P101",
        "P102"
    )

    with pytest.raises(ValueError):

        innings.replace_batsman(
            "P103"
        )