from django.test import TestCase
from rest_framework.test import APIClient
from cricket.test_helpers import authenticate_client
from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class MatchResultAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="RA1",
            name="India Player",
            email="ra1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="RA2",
            name="Australia Player",
            email="ra2@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.team1 = Team.objects.create(
            team_id="RAT1",
            team_name="India",
            captain=self.player1,
        )

        self.team1.players.add(self.player1)

        self.team2 = Team.objects.create(
            team_id="RAT2",
            team_name="Australia",
            captain=self.player2,
        )

        self.team2.players.add(self.player2)

        self.match = Match.objects.create(
            match_id="RA001",
            team1=self.team1,
            team2=self.team2,
            ground="Result Ground",
            ball_type="tennis",
            overs=20,
            status="live",
            toss_winner=self.team1,
            toss_call="heads",
            toss_result="heads",
            toss_decision="bat",
            batting_team=self.team1,
            bowling_team=self.team2,
        )

    def test_team1_wins_by_runs(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=130,
            balls_bowled=120,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["winner"],
            "RAT1",
        )

        self.assertEqual(
            response.data["result_type"],
            "runs",
        )

        self.assertEqual(
            response.data["result_margin"],
            20,
        )

    def test_team2_wins_by_wickets(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=151,
            balls_bowled=100,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["winner"],
            "RAT2",
        )

        self.assertEqual(
            response.data["result_type"],
            "wickets",
        )

        self.assertEqual(
            response.data["result_margin"],
            10,
        )

    def test_match_tied(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.data["winner"],
        )

        self.assertEqual(
            response.data["result_type"],
            "tie",
        )

        self.assertEqual(
            response.data["result_margin"],
            0,
        )
        
    def test_result_cannot_be_calculated_before_both_innings_complete(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=100,
            balls_bowled=50,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Both innings must be completed before calculating result.",
        )

    def test_result_cannot_be_calculated_without_two_innings(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Both innings must be completed before calculating result.",
        )

    def test_result_cannot_be_calculated_after_match_completed(self):
        self.match.status = "completed"
        self.match.save()

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Match is already completed.",
        )
    def test_second_innings_completion_calculates_match_result(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=151,
            balls_bowled=100,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "completed",
        )

        self.assertEqual(
            self.match.winner,
            self.team2,
        )


    def test_result_cannot_be_calculated_when_second_innings_is_incomplete(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
            balls_bowled=120,
        )

        Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=100,
            balls_bowled=50,
        )

        response = self.client.post(
            "/matches/RA001/result/",
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Both innings must be completed before calculating result.",
        )