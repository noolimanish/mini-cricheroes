from django.test import TestCase

from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class ScorecardSummaryAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.batsman = Player.objects.create(
            player_id="SUM1",
            name="Batsman",
            email="sum1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.bowler = Player.objects.create(
            player_id="SUM2",
            name="Bowler",
            email="sum2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="SUMT1",
            team_name="India",
            captain=self.batsman,
        )

        self.team1.players.add(
            self.batsman
        )

        self.team2 = Team.objects.create(
            team_id="SUMT2",
            team_name="Australia",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="SUM001",
            team1=self.team1,
            team2=self.team2,
            ground="Summary Ground",
            ball_type="leather",
            overs=20,
            status="live",
        )

        self.innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            balls_bowled=120,
            total_runs=152,
            wickets_fallen=6,
        )

    def test_scorecard_returns_innings_summary(self):
        response = self.client.get(
            "/matches/SUM001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        innings = response.data["innings"][0]

        self.assertEqual(
            innings["score"],
            "152/6"
        )

        self.assertEqual(
            innings["overs_completed"],
            "20.0"
        )

        self.assertEqual(
            innings["run_rate"],
            7.6
        )

    def test_run_rate_is_calculated_correctly(self):
        self.innings.balls_bowled = 60
        self.innings.total_runs = 75

        self.innings.save(
            update_fields=[
                "balls_bowled",
                "total_runs",
            ]
        )

        response = self.client.get(
            "/matches/SUM001/scorecard/"
        )

        innings = response.data["innings"][0]

        self.assertEqual(
            innings["run_rate"],
            7.5
        )

    def test_summary_handles_zero_balls(self):
        self.innings.balls_bowled = 0
        self.innings.total_runs = 0

        self.innings.save(
            update_fields=[
                "balls_bowled",
                "total_runs",
            ]
        )

        response = self.client.get(
            "/matches/SUM001/scorecard/"
        )

        innings = response.data["innings"][0]

        self.assertEqual(
            innings["overs_completed"],
            "0.0"
        )

        self.assertEqual(
            innings["run_rate"],
            0.0
        )