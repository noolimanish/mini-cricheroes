from django.test import TestCase

from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class ScorecardResultAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.player1 = Player.objects.create(
            player_id="RES1",
            name="Player One",
            email="res1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="RES2",
            name="Player Two",
            email="res2@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.team1 = Team.objects.create(
            team_id="REST1",
            team_name="India",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1
        )

        self.team2 = Team.objects.create(
            team_id="REST2",
            team_name="Australia",
            captain=self.player2,
        )

        self.team2.players.add(
            self.player2
        )

        self.match = Match.objects.create(
            match_id="RES001",
            team1=self.team1,
            team2=self.team2,
            ground="Result Ground",
            ball_type="leather",
            overs=20,
            status="completed",
            winner=self.team1,
            result_type="runs",
            result_margin=4,
        )

    def test_scorecard_returns_runs_result(self):

        response = self.client.get(
            "/matches/RES001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["result"],
            "India won by 4 runs"
        )

    def test_scorecard_returns_wickets_result(self):

        self.match.winner = self.team2
        self.match.result_type = "wickets"
        self.match.result_margin = 3

        self.match.save(
            update_fields=[
                "winner",
                "result_type",
                "result_margin",
            ]
        )

        response = self.client.get(
            "/matches/RES001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["result"],
            "Australia won by 3 wickets"
        )

    def test_scorecard_returns_tie_result(self):

        self.match.winner = None
        self.match.result_type = "tie"
        self.match.result_margin = 0

        self.match.save(
            update_fields=[
                "winner",
                "result_type",
                "result_margin",
            ]
        )

        response = self.client.get(
            "/matches/RES001/scorecard/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["result"],
            "Match tied"
        )