from django.test import TestCase
from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.test_helpers import authenticate_client


class SetBowlerAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        authenticate_client(self.client)

        self.batsman = Player.objects.create(
            player_id="BP1",
            name="Batsman",
            email="bp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.bowler = Player.objects.create(
            player_id="BP2",
            name="Bowler",
            email="bp2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.wrong_player = Player.objects.create(
            player_id="BP3",
            name="Wrong Player",
            email="bp3@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.batting_team = Team.objects.create(
            team_id="BT1",
            team_name="Batting Team",
            captain=self.batsman,
        )

        self.batting_team.players.add(
            self.batsman
        )

        self.bowling_team = Team.objects.create(
            team_id="BT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.bowling_team.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="BOWL1",
            team1=self.batting_team,
            team2=self.bowling_team,
            ground="Test Ground",
            ball_type="tennis",
            overs=20,
            status="scheduled",
            toss_winner=self.batting_team,
            toss_decision="bat",
            batting_team=self.batting_team,
            bowling_team=self.bowling_team,
        )

        self.innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.batting_team,
            bowling_team=self.bowling_team,
            overs=20,
        )

    def test_set_bowler(self):
        response = self.client.post(
            "/matches/BOWL1/innings/1/bowler/",
            {
                "bowler_id": "BP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.current_bowler_id,
            "BP2"
        )

    def test_bowler_must_be_in_bowling_team(self):
        response = self.client.post(
            "/matches/BOWL1/innings/1/bowler/",
            {
                "bowler_id": "BP3",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "BP3 is not part of the bowling team."
        )

    def test_missing_bowler(self):
        response = self.client.post(
            "/matches/BOWL1/innings/1/bowler/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "bowler_id is required."
        )

    def test_innings_not_found(self):
        response = self.client.post(
            "/matches/BOWL1/innings/99/bowler/",
            {
                "bowler_id": "BP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/innings/1/bowler/",
            {
                "bowler_id": "BP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_change_bowler(self):
        self.client.post(
            "/matches/BOWL1/innings/1/bowler/",
            {
                "bowler_id": "BP2",
            },
            format="json"
        )

        response = self.client.post(
            "/matches/BOWL1/innings/1/bowler/",
            {
                "bowler_id": "BP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.current_bowler_id,
            "BP2"
        )