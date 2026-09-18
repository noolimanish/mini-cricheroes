from django.test import TestCase

from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
    BatsmanStats,
)


class BattingScorecardAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.batsman1 = Player.objects.create(
            player_id="BSC1",
            name="Batsman 1",
            email="bsc1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.batsman2 = Player.objects.create(
            player_id="BSC2",
            name="Batsman 2",
            email="bsc2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="BSC3",
            name="Bowler",
            email="bsc3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="BSCT1",
            team_name="India",
            captain=self.batsman1,
        )

        self.team1.players.add(
            self.batsman1,
            self.batsman2,
        )

        self.team2 = Team.objects.create(
            team_id="BSCT2",
            team_name="Australia",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="BSC001",
            team1=self.team1,
            team2=self.team2,
            ground="Scorecard Ground",
            ball_type="tennis",
            overs=20,
            status="live",
        )

        self.innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=52,
            wickets_fallen=1,
        )

        self.batsman_stats = BatsmanStats.objects.create(
            innings=self.innings,
            player=self.batsman1,
            runs=52,
            balls_faced=40,
            fours=6,
            sixes=2,
            is_out=True,
            dismissal_type="bowled",
        )

    def test_scorecard_returns_batting_stats(self):
        response = self.client.get(
            "/matches/BSC001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data["innings"]),
            1
        )

        innings = response.data["innings"][0]

        self.assertEqual(
            innings["total_runs"],
            52
        )

        self.assertEqual(
            len(innings["batting_stats"]),
            1
        )

        batsman = innings["batting_stats"][0]

        self.assertEqual(
            batsman["player"],
            "BSC1"
        )

        self.assertEqual(
            batsman["runs"],
            52
        )

        self.assertEqual(
            batsman["balls_faced"],
            40
        )

        self.assertEqual(
            batsman["fours"],
            6
        )

        self.assertEqual(
            batsman["sixes"],
            2
        )

        self.assertEqual(
            batsman["strike_rate"],
            130.0
        )

        self.assertTrue(
            batsman["is_out"]
        )

        self.assertEqual(
            batsman["dismissal_type"],
            "bowled"
        )

    def test_strike_rate_is_zero_when_no_balls_faced(self):
        self.batsman_stats.balls_faced = 0
        self.batsman_stats.runs = 0

        self.batsman_stats.save(
            update_fields=[
                "balls_faced",
                "runs",
            ]
        )

        response = self.client.get(
            "/matches/BSC001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        batsman = response.data[
            "innings"
        ][0][
            "batting_stats"
        ][0]

        self.assertEqual(
            batsman["strike_rate"],
            0.0
        )

    def test_scorecard_returns_404_for_unknown_match(self):
        response = self.client.get(
            "/matches/UNKNOWN/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertEqual(
            response.data["error"],
            "Match not found."
        )