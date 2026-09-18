import pytest

from backend.ball import Ball


def test_ball_creation():

    ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    assert ball.ball_number == 1
    assert ball.striker_id == "P101"
    assert ball.non_striker_id == "P102"
    assert ball.bowler_id == "P103"
    assert ball.runs == 0
    assert ball.extras == 0
    assert ball.is_legal is True
    assert ball.wicket is False


def test_set_extra():

    ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    ball.set_extra("wide", 1)

    assert ball.extra_type == "wide"
    assert ball.extras == 1
    assert ball.is_legal is False


def test_invalid_extra_type():

    ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    with pytest.raises(ValueError):

        ball.set_extra("invalid", 1)


def test_set_wicket():

    ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    ball.set_wicket(
        "P101",
        "bowled"
    )

    assert ball.wicket is True
    assert ball.player_out_id == "P101"
    assert ball.wicket_type == "bowled"


def test_ball_string_representation():

    ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    assert str(ball)