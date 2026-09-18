from django.test import TestCase
from rest_framework.test import APIClient
from cricket.test_helpers import authenticate_client
from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class OpeningBatsmenAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="OP1",
            name="Batsman One",
            email="op1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="OP2",
            name="Batsman Two",
            email="op2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.player3 = Player.objects.create(
            player_id="OP3",
            name="Bowler",
            email="op3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="OT1",
            team_name="Batting Team",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1,
            self.player2
        )

        self.team2 = Team.objects.create(
            team_id="OT2",
            team_name="Bowling Team",
            captain=self.player3,
        )

        self.team2.players.add(
            self.player3
        )

        self.match = Match.objects.create(
            match_id="OPEN1",
            team1=self.team1,
            team2=self.team2,
            ground="Test Ground",
            ball_type="tennis",
            overs=20,
            status="scheduled",
            toss_call="heads",
            toss_result="heads",
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
        )

    def test_set_opening_batsmen(self):
        response = self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {
                "striker_id": "OP1",
                "non_striker_id": "OP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.striker_id,
            "OP1"
        )

        self.assertEqual(
            self.innings.non_striker_id,
            "OP2"
        )

    def test_players_must_be_different(self):
        response = self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {
                "striker_id": "OP1",
                "non_striker_id": "OP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Striker and non-striker must be different."
        )

    def test_striker_must_be_in_batting_team(self):
        response = self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {
                "striker_id": "OP3",
                "non_striker_id": "OP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "OP3 is not part of the batting team."
        )

    def test_non_striker_must_be_in_batting_team(self):
        response = self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {
                "striker_id": "OP1",
                "non_striker_id": "OP3",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "OP3 is not part of the batting team."
        )

    def test_missing_players(self):
        response = self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "striker_id and non_striker_id are required."
        )

    def test_innings_not_found(self):
        response = self.client.post(
            "/matches/OPEN1/innings/99/opening-batsmen/",
            {
                "striker_id": "OP1",
                "non_striker_id": "OP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/innings/1/opening-batsmen/",
            {
                "striker_id": "OP1",
                "non_striker_id": "OP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_opening_batsmen_cannot_be_set_twice(self):
        self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {
                "striker_id": "OP1",
                "non_striker_id": "OP2",
            },
            format="json"
        )

        response = self.client.post(
            "/matches/OPEN1/innings/1/opening-batsmen/",
            {
                "striker_id": "OP2",
                "non_striker_id": "OP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Opening batsmen have already been set."
        )