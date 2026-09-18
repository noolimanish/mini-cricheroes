import pytest

from backend.bowler_stats import BowlerStats


def test_bowler_stats_creation():

    stats = BowlerStats("P103")

    assert stats.player_id == "P103"
    assert stats.balls_bowled == 0
    assert stats.runs_conceded == 0
    assert stats.wickets == 0
    assert stats.wides == 0
    assert stats.no_balls == 0
    assert stats.overs == "0.0"
    assert stats.economy == 0.0


def test_record_legal_ball():

    stats = BowlerStats("P103")

    stats.record_ball(
        4,
        legal=True
    )

    assert stats.runs_conceded == 4
    assert stats.balls_bowled == 1


def test_record_illegal_ball():

    stats = BowlerStats("P103")

    stats.record_ball(
        1,
        legal=False
    )

    assert stats.runs_conceded == 1
    assert stats.balls_bowled == 0


def test_record_wide():

    stats = BowlerStats("P103")

    stats.record_wide()

    assert stats.wides == 1


def test_record_no_ball():

    stats = BowlerStats("P103")

    stats.record_no_ball()

    assert stats.no_balls == 1


def test_record_wicket():

    stats = BowlerStats("P103")

    stats.record_wicket()

    assert stats.wickets == 1


def test_negative_runs_rejected():

    stats = BowlerStats("P103")

    with pytest.raises(ValueError):

        stats.record_ball(-1)


def test_overs():

    stats = BowlerStats("P103")

    for _ in range(7):

        stats.record_ball(0, legal=True)

    assert stats.balls_bowled == 7
    assert stats.overs == "1.1"


def test_economy():

    stats = BowlerStats("P103")

    for _ in range(6):

        stats.record_ball(
            3,
            legal=True
        )

    assert stats.balls_bowled == 6
    assert stats.runs_conceded == 18
    assert stats.economy == 18.0