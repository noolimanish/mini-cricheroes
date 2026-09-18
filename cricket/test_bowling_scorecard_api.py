from django.test import TestCase

from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
    BowlerStats,
)


class BowlingScorecardAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.batsman = Player.objects.create(
            player_id="BOW1",
            name="Batsman",
            email="bow1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.bowler = Player.objects.create(
            player_id="BOW2",
            name="Bowler",
            email="bow2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="BOWT1",
            team_name="India",
            captain=self.batsman,
        )

        self.team1.players.add(
            self.batsman
        )

        self.team2 = Team.objects.create(
            team_id="BOWT2",
            team_name="Australia",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="BOW001",
            team1=self.team1,
            team2=self.team2,
            ground="Bowling Scorecard Ground",
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
            total_runs=28,
            wickets_fallen=2,
        )

        self.bowler_stats = BowlerStats.objects.create(
            innings=self.innings,
            player=self.bowler,
            balls_bowled=24,
            runs_conceded=28,
            wickets=2,
            wides=1,
            no_balls=0,
        )

    def test_scorecard_returns_bowling_stats(self):
        response = self.client.get(
            "/matches/BOW001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        innings = response.data["innings"][0]

        self.assertEqual(
            len(innings["bowling_stats"]),
            1
        )

        bowler = innings["bowling_stats"][0]

        self.assertEqual(
            bowler["player"],
            "BOW2"
        )

        self.assertEqual(
            bowler["overs"],
            "4.0"
        )

        self.assertEqual(
            bowler["balls_bowled"],
            24
        )

        self.assertEqual(
            bowler["runs_conceded"],
            28
        )

        self.assertEqual(
            bowler["wickets"],
            2
        )

        self.assertEqual(
            bowler["wides"],
            1
        )

        self.assertEqual(
            bowler["no_balls"],
            0
        )

        self.assertEqual(
            bowler["economy"],
            7.0
        )

    def test_economy_is_zero_when_no_balls_bowled(self):
        self.bowler_stats.balls_bowled = 0
        self.bowler_stats.runs_conceded = 0

        self.bowler_stats.save(
            update_fields=[
                "balls_bowled",
                "runs_conceded",
            ]
        )

        response = self.client.get(
            "/matches/BOW001/scorecard/"
        )

        bowler = response.data[
            "innings"
        ][0][
            "bowling_stats"
        ][0]

        self.assertEqual(
            bowler["economy"],
            0.0
        )

    def test_bowler_overs_handle_partial_over(self):
        self.bowler_stats.balls_bowled = 25

        self.bowler_stats.save(
            update_fields=[
                "balls_bowled"
            ]
        )

        response = self.client.get(
            "/matches/BOW001/scorecard/"
        )

        bowler = response.data[
            "innings"
        ][0][
            "bowling_stats"
        ][0]

        self.assertEqual(
            bowler["overs"],
            "4.1"
        )