from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.innings_service import InningsService


class InningsOversLimitTestCase(TestCase):

    def setUp(self):
        self.striker = Player.objects.create(
            player_id="OL1",
            name="Striker",
            email="ol1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="OL2",
            name="Non Striker",
            email="ol2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="OL3",
            name="Bowler",
            email="ol3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="OLT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.team1.players.add(
            self.striker,
            self.non_striker
        )

        self.team2 = Team.objects.create(
            team_id="OLT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="OVERLIMIT1",
            team1=self.team1,
            team2=self.team2,
            ground="Over Limit Ground",
            ball_type="tennis",
            overs=1,
            status="scheduled",
            toss_winner=self.team1,
            toss_decision="bat",
            batting_team=self.team1,
            bowling_team=self.team2,
        )

        self.innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=1,
            striker=self.striker,
            non_striker=self.non_striker,
            current_bowler=self.bowler,
        )

        self.service = InningsService()

    def test_cannot_record_ball_after_overs_limit(self):
        for _ in range(6):
            self.service.record_ball(
                innings=self.innings,
                runs=0
            )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.current_over,
            1
        )

        self.assertEqual(
            self.innings.balls_bowled,
            6
        )

        with self.assertRaisesMessage(
            ValueError,
            "Innings overs limit has been reached."
        ):
            self.service.record_ball(
                innings=self.innings,
                runs=0
            )

    def test_cannot_create_over_after_overs_limit(self):
        for _ in range(6):
            self.service.record_ball(
                innings=self.innings,
                runs=0
            )

        self.innings.refresh_from_db()

        with self.assertRaisesMessage(
            ValueError,
            "Innings overs limit has been reached."
        ):
            self.service.create_over(
                self.innings
            )

    def test_innings_does_not_create_extra_over(self):
        for _ in range(6):
            self.service.record_ball(
                innings=self.innings,
                runs=0
            )

        self.assertEqual(
            self.innings.overs_data.count(),
            1
        )