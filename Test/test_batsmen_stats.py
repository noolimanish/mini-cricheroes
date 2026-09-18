import pytest

from backend.batsman_stats import BatsmanStats


def test_batsman_stats_creation():

    stats = BatsmanStats("P101")

    assert stats.player_id == "P101"
    assert stats.runs == 0
    assert stats.balls_faced == 0
    assert stats.fours == 0
    assert stats.sixes == 0
    assert stats.is_out is False
    assert stats.dismissal_type is None


def test_record_runs():

    stats = BatsmanStats("P101")

    stats.record_runs(4)

    assert stats.runs == 4
    assert stats.balls_faced == 1
    assert stats.fours == 1
    assert stats.sixes == 0


def test_record_six():

    stats = BatsmanStats("P101")

    stats.record_runs(6)

    assert stats.runs == 6
    assert stats.balls_faced == 1
    assert stats.fours == 0
    assert stats.sixes == 1


def test_multiple_runs():

    stats = BatsmanStats("P101")

    stats.record_runs(1)
    stats.record_runs(2)
    stats.record_runs(4)

    assert stats.runs == 7
    assert stats.balls_faced == 3
    assert stats.fours == 1
    assert stats.sixes == 0


def test_record_out():

    stats = BatsmanStats("P101")

    stats.record_runs(10)
    stats.record_out("bowled")

    assert stats.runs == 10
    assert stats.balls_faced == 1
    assert stats.is_out is True
    assert stats.dismissal_type == "bowled"


def test_negative_runs_rejected():

    stats = BatsmanStats("P101")

    with pytest.raises(ValueError):

        stats.record_runs(-1)


def test_strike_rate():

    stats = BatsmanStats("P101")

    stats.record_runs(10)
    stats.record_runs(5)

    assert stats.strike_rate == 750.0