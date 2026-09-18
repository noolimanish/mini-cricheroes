from django.test import TestCase
from rest_framework.test import APIClient

from cricket.models import Player, Team, Match
from cricket.test_helpers import authenticate_client

class MatchStatusAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="MSA1",
            name="Player One",
            email="msa1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="MSA2",
            name="Player Two",
            email="msa2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="MSA3",
            name="Bowler",
            email="msa3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="MSAT1",
            team_name="Team One",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1,
            self.player2,
        )

        self.team2 = Team.objects.create(
            team_id="MSAT2",
            team_name="Team Two",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="MSA1",
            team1=self.team1,
            team2=self.team2,
            ground="API Ground",
            ball_type="tennis",
            overs=20,
            status="scheduled",
        )

    def test_start_match_requires_toss(self):
        response = self.client.post(
            "/matches/MSA1/start/"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Toss must be conducted before starting the match.",
        )

    def test_start_match_success(self):
        self.match.toss_winner = self.team1
        self.match.toss_decision = "bat"
        self.match.batting_team = self.team1
        self.match.bowling_team = self.team2

        self.match.save()

        response = self.client.post(
            "/matches/MSA1/start/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "live",
        )

        self.assertEqual(
            response.data["status"],
            "live",
        )

    def test_start_completed_match_fails(self):
        self.match.status = "completed"
        self.match.save()

        response = self.client.post(
            "/matches/MSA1/start/"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Completed match cannot be started again.",
        )
    
    def test_complete_match_requires_live_status(self):
        response = self.client.post(
            "/matches/MSA1/complete/"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Only a live match can be completed.",
        )

    def test_complete_match_success(self):
        self.match.toss_winner = self.team1
        self.match.toss_decision = "bat"
        self.match.batting_team = self.team1
        self.match.bowling_team = self.team2

        self.match.save()

        self.client.post(
            "/matches/MSA1/start/"
        )

        response = self.client.post(
            "/matches/MSA1/complete/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "completed",
        )

        self.assertEqual(
            response.data["status"],
            "completed",
        )

    def test_completed_match_cannot_be_completed_again(self):
        self.match.status = "completed"
        self.match.save()

        response = self.client.post(
            "/matches/MSA1/complete/"
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Only a live match can be completed.",
        )