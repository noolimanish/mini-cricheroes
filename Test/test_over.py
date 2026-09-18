import pytest

from backend.ball import Ball
from backend.over import Over


def create_ball(runs=0):

    ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    ball.runs = runs

    return ball


def test_over_creation():

    over = Over(1, "P103")

    assert over.over_number == 1
    assert over.bowler_id == "P103"
    assert over.balls == []
    assert over.legal_balls == 0


def test_add_legal_ball():

    over = Over(1, "P103")

    ball = create_ball(4)

    over.add_ball(ball)

    assert len(over.balls) == 1
    assert over.legal_balls == 1


def test_add_six_legal_balls():

    over = Over(1, "P103")

    for _ in range(6):
        over.add_ball(create_ball())

    assert len(over.balls) == 6
    assert over.legal_balls == 6


def test_seventh_legal_ball_rejected():

    over = Over(1, "P103")

    for _ in range(6):
        over.add_ball(create_ball())

    with pytest.raises(ValueError):
        over.add_ball(create_ball())


def test_wide_does_not_count_as_legal_ball():

    over = Over(1, "P103")

    wide_ball = Ball(
        1,
        "P101",
        "P102",
        "P103"
    )

    wide_ball.extra_type = "wide"
    wide_ball.extras = 1
    wide_ball.is_legal = False

    over.add_ball(wide_ball)

    assert len(over.balls) == 1
    assert over.legal_balls == 0