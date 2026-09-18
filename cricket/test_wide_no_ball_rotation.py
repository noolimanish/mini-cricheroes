from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.innings_service import InningsService


class WideNoBallRotationTestCase(TestCase):

    def setUp(self):
        self.striker = Player.objects.create(
            player_id="WN1",
            name="Striker",
            email="wn1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="WN2",
            name="Non Striker",
            email="wn2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="WN3",
            name="Bowler",
            email="wn3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="WNT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.team1.players.add(
            self.striker,
            self.non_striker,
        )

        self.team2 = Team.objects.create(
            team_id="WNT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="WIDE1",
            team1=self.team1,
            team2=self.team2,
            ground="Wide Ground",
            ball_type="tennis",
            overs=20,
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
            overs=20,
            striker=self.striker,
            non_striker=self.non_striker,
            current_bowler=self.bowler,
        )

        self.service = InningsService()

    def test_wide_does_not_count_as_legal_ball(self):
        self.service.record_ball(
            innings=self.innings,
            runs=0,
            extra_type="wide",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.balls_bowled,
            0,
        )

        self.assertEqual(
            self.innings.total_runs,
            1,
        )

    def test_wide_does_not_rotate_strike_for_one_extra(self):
        self.service.record_ball(
            innings=self.innings,
            runs=0,
            extra_type="wide",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.striker_id,
            "WN1",
        )

        self.assertEqual(
            self.innings.non_striker_id,
            "WN2",
        )

    def test_two_wides_rotate_strike(self):
        self.service.record_ball(
            innings=self.innings,
            runs=0,
            extra_type="wide",
            extra_runs=2,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.striker_id,
            "WN2",
        )

        self.assertEqual(
            self.innings.non_striker_id,
            "WN1",
        )

    def test_no_ball_does_not_count_as_legal_ball(self):
        self.service.record_ball(
            innings=self.innings,
            runs=0,
            extra_type="no-ball",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.balls_bowled,
            0,
        )

        self.assertEqual(
            self.innings.total_runs,
            1,
        )

    def test_no_ball_with_one_bat_run_rotates_strike(self):
        self.service.record_ball(
            innings=self.innings,
            runs=1,
            extra_type="no-ball",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.striker_id,
            "WN2",
        )

        self.assertEqual(
            self.innings.non_striker_id,
            "WN1",
        )

