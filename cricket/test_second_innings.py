from django.test import TestCase
from rest_framework.test import APIClient
from cricket.test_helpers import authenticate_client
from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)


class SecondInningsAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.batsman1 = Player.objects.create(
            player_id="SI1",
            name="Batsman 1",
            email="si1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.batsman2 = Player.objects.create(
            player_id="SI2",
            name="Batsman 2",
            email="si2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler1 = Player.objects.create(
            player_id="SI3",
            name="Bowler 1",
            email="si3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.bowler2 = Player.objects.create(
            player_id="SI4",
            name="Bowler 2",
            email="si4@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="spin",
            bowling_style="right-arm-spin",
        )

        self.team1 = Team.objects.create(
            team_id="SIT1",
            team_name="India",
            captain=self.batsman1,
        )

        self.team1.players.add(
            self.batsman1,
            self.batsman2,
        )

        self.team2 = Team.objects.create(
            team_id="SIT2",
            team_name="Australia",
            captain=self.bowler1,
        )

        self.team2.players.add(
            self.bowler1,
            self.bowler2,
        )

        self.match = Match.objects.create(
            match_id="SIM001",
            team1=self.team1,
            team2=self.team2,
            ground="Second Innings Ground",
            ball_type="tennis",
            overs=1,
            status="live",
            toss_winner=self.team1,
            toss_call="heads",
            toss_result="heads",
            toss_decision="bat",
            batting_team=self.team1,
            bowling_team=self.team2,
        )

    def create_first_innings(self):
        response = self.client.post(
            "/matches/SIM001/innings/",
            {"overs": 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        return Innings.objects.get(
            match=self.match,
            innings_number=1,
        )

    def complete_first_innings(self, innings):
        innings.balls_bowled = 6
        innings.current_over = 1
        innings.save(
            update_fields=[
                "balls_bowled",
                "current_over",
            ]
        )

    def test_create_second_innings(self):
        first_innings = self.create_first_innings()

        self.complete_first_innings(first_innings)

        response = self.client.post(
            "/matches/SIM001/innings/",
            {"overs": 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        second_innings = Innings.objects.get(
            match=self.match,
            innings_number=2,
        )

        self.assertEqual(
            second_innings.batting_team,
            self.team2,
        )

        self.assertEqual(
            second_innings.bowling_team,
            self.team1,
        )

    def test_second_innings_cannot_start_before_first_completes(self):
        self.create_first_innings()

        response = self.client.post(
            "/matches/SIM001/innings/",
            {"overs": 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "First innings is not complete.",
        )

    def test_third_innings_is_rejected(self):
        first_innings = self.create_first_innings()
        self.complete_first_innings(first_innings)

        response = self.client.post(
            "/matches/SIM001/innings/",
            {"overs": 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        second_innings = Innings.objects.get(
            match=self.match,
            innings_number=2,
        )

        second_innings.balls_bowled = 6
        second_innings.current_over = 1
        second_innings.save(
            update_fields=[
                "balls_bowled",
                "current_over",
            ]
        )

        response = self.client.post(
            "/matches/SIM001/innings/",
            {"overs": 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["error"],
            "Both innings have already been created.",
        )

    def test_second_innings_can_start_after_tenth_wicket(self):
        first_innings = self.create_first_innings()

        first_innings.wickets_fallen = 10
        first_innings.save(
            update_fields=["wickets_fallen"]
        )

        response = self.client.post(
            "/matches/SIM001/innings/",
            {"overs": 1},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        second_innings = Innings.objects.get(
            match=self.match,
            innings_number=2,
        )

        self.assertEqual(
            second_innings.batting_team,
            self.team2,
        )

        self.assertEqual(
            second_innings.bowling_team,
            self.team1,
        )