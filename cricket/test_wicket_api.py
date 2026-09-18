from django.test import TestCase
from rest_framework.test import APIClient
from cricket.test_helpers import authenticate_client
from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class RecordWicketAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.striker = Player.objects.create(
            player_id="WP1",
            name="Striker",
            email="wp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="WP2",
            name="Non Striker",
            email="wp2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="WP3",
            name="Bowler",
            email="wp3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="WT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.team1.players.add(
            self.striker,
            self.non_striker
        )

        self.team2 = Team.objects.create(
            team_id="WT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="WICK1",
            team1=self.team1,
            team2=self.team2,
            ground="Wicket Ground",
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

    def test_bowled_wicket(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {
                "wicket_type": "bowled",
                "player_out_id": "WP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["wicket"],
            True
        )

        self.assertEqual(
            response.data["wicket_type"],
            "bowled"
        )

        self.assertEqual(
            response.data["player_out"],
            "WP1"
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.wickets_fallen,
            1
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1
        )

    def test_run_out(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {
                "wicket_type": "run-out",
                "player_out_id": "WP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["wicket_type"],
            "run-out"
        )

    def test_wicket_with_runs(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {
                "wicket_type": "run-out",
                "player_out_id": "WP1",
                "runs": 2,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["runs"],
            2
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            2
        )

    def test_invalid_wicket_type(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {
                "wicket_type": "invalid",
                "player_out_id": "WP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_player_out_must_be_current_batsman(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {
                "wicket_type": "bowled",
                "player_out_id": "WP3",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_missing_fields(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_negative_runs(self):
        response = self.client.post(
            "/matches/WICK1/innings/1/wicket/",
            {
                "wicket_type": "bowled",
                "player_out_id": "WP1",
                "runs": -1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/innings/1/wicket/",
            {
                "wicket_type": "bowled",
                "player_out_id": "WP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_innings_not_found(self):
        response = self.client.post(
            "/matches/WICK1/innings/99/wicket/",
            {
                "wicket_type": "bowled",
                "player_out_id": "WP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )