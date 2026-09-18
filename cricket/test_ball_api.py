from django.test import TestCase
from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.test_helpers import authenticate_client


class RecordBallAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        authenticate_client(self.client)

        self.striker = Player.objects.create(
            player_id="BALLP1",
            name="Striker",
            email="ballp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="BALLP2",
            name="Non Striker",
            email="ballp2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="BALLP3",
            name="Bowler",
            email="ballp3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.batting_team = Team.objects.create(
            team_id="BALLT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.batting_team.players.add(
            self.striker,
            self.non_striker
        )

        self.bowling_team = Team.objects.create(
            team_id="BALLT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.bowling_team.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="BALLM1",
            team1=self.batting_team,
            team2=self.bowling_team,
            ground="Ball Ground",
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
            striker=self.striker,
            non_striker=self.non_striker,
            current_bowler=self.bowler,
        )

    def test_record_normal_ball(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 4,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["runs"],
            4
        )

        self.assertEqual(
            response.data["is_legal"],
            True
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            4
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1
        )

    def test_record_wide(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 0,
                "extra_type": "wide",
                "extra_runs": 1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["extra_type"],
            "wide"
        )

        self.assertEqual(
            response.data["is_legal"],
            False
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            1
        )

        self.assertEqual(
            self.innings.balls_bowled,
            0
        )

    def test_record_no_ball(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 0,
                "extra_type": "no-ball",
                "extra_runs": 1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["is_legal"],
            False
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            1
        )

        self.assertEqual(
            self.innings.balls_bowled,
            0
        )

    def test_record_bye(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 0,
                "extra_type": "bye",
                "extra_runs": 2,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["extra_type"],
            "bye"
        )

        self.assertEqual(
            response.data["is_legal"],
            True
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            2
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1
        )

    def test_negative_runs_rejected(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": -1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Runs cannot be negative."
        )

    def test_negative_extra_runs_rejected(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 0,
                "extra_type": "wide",
                "extra_runs": -1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Extra runs cannot be negative."
        )

    def test_invalid_extra_type(self):
        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 0,
                "extra_type": "invalid",
                "extra_runs": 1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_innings_not_found(self):
        response = self.client.post(
            "/matches/BALLM1/innings/99/balls/",
            {
                "runs": 1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.assertEqual(
            response.data["error"],
            "Innings not found."
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/innings/1/balls/",
            {
                "runs": 1,
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

    def test_ball_requires_opening_batsmen(self):
        self.innings.striker = None
        self.innings.non_striker = None
        self.innings.save()

        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Opening batsmen must be set before recording a ball."
        )

    def test_ball_requires_bowler(self):
        self.innings.current_bowler = None
        self.innings.save()

        response = self.client.post(
            "/matches/BALLM1/innings/1/balls/",
            {
                "runs": 1,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Bowler must be set before recording a ball."
        )