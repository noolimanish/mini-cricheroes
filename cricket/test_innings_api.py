from django.test import TestCase
from rest_framework.test import APIClient
from cricket.test_helpers import authenticate_client
from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class MatchInningsAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="IP1",
            name="India Player",
            email="ip1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="IP2",
            name="Australia Player",
            email="ip2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="IT1",
            team_name="India",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1
        )

        self.team2 = Team.objects.create(
            team_id="IT2",
            team_name="Australia",
            captain=self.player2,
        )

        self.team2.players.add(
            self.player2
        )

        self.match = Match.objects.create(
            match_id="INN1",
            team1=self.team1,
            team2=self.team2,
            ground="Test Ground",
            ball_type="tennis",
            overs=20,
            status="scheduled",
        )

    def prepare_match(self):
        self.match.toss_winner = self.team1
        self.match.toss_call = "heads"
        self.match.toss_result = "heads"
        self.match.toss_decision = "bat"
        self.match.batting_team = self.team1
        self.match.bowling_team = self.team2
        self.match.status = "live"

        self.match.save()

    def test_create_innings(self):
        self.prepare_match()

        response = self.client.post(
            "/matches/INN1/innings/",
            {
                "overs": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["innings_number"],
            1
        )

        self.assertEqual(
            response.data["batting_team"],
            "IT1"
        )

        self.assertEqual(
            response.data["bowling_team"],
            "IT2"
        )

        self.assertEqual(
            response.data["overs"],
            20
        )

        self.assertEqual(
            Innings.objects.count(),
            1
        )

    def test_create_innings_without_toss_decision(self):
        self.match.status = "live"
        self.match.save()

        response = self.client.post(
            "/matches/INN1/innings/",
            {
                "overs": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Toss decision must be made before creating an innings."
        )

    def test_create_innings_missing_overs(self):
        self.prepare_match()

        response = self.client.post(
            "/matches/INN1/innings/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Overs is required."
        )

    def test_create_innings_invalid_overs(self):
        self.prepare_match()

        response = self.client.post(
            "/matches/INN1/innings/",
            {
                "overs": 0,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Overs must be a positive integer."
        )

    def test_create_innings_invalid_overs_type(self):
        self.prepare_match()

        response = self.client.post(
            "/matches/INN1/innings/",
            {
                "overs": "abc",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Overs must be a positive integer."
        )

    def test_create_innings_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/innings/",
            {
                "overs": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertEqual(
            response.data["error"],
            "Match not found."
        )

    def test_create_second_innings_requires_first_innings_completion(self):
        self.prepare_match()

        response = self.client.post(
            "/matches/INN1/innings/",
            {
                "overs": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        response = self.client.post(
            "/matches/INN1/innings/",
            {
                "overs": 20,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "First innings is not complete."
        )