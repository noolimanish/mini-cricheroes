from django.test import TestCase
from rest_framework.test import APIClient

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.test_helpers import authenticate_client


class ReplaceBatsmanAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        authenticate_client(self.client)

        self.striker = Player.objects.create(
            player_id="RP1",
            name="Striker",
            email="rp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="RP2",
            name="Non Striker",
            email="rp2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="RP3",
            name="Bowler",
            email="rp3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.new_batsman = Player.objects.create(
            player_id="RP4",
            name="New Batsman",
            email="rp4@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.team1 = Team.objects.create(
            team_id="RT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.team1.players.add(
            self.striker,
            self.non_striker,
            self.new_batsman
        )

        self.team2 = Team.objects.create(
            team_id="RT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler
        )

        self.match = Match.objects.create(
            match_id="REPL1",
            team1=self.team1,
            team2=self.team2,
            ground="Replacement Ground",
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

    def record_wicket(self):
        response = self.client.post(
            "/matches/REPL1/innings/1/wicket/",
            {
                "wicket_type": "bowled",
                "player_out_id": "RP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_replace_dismissed_striker(self):
        self.record_wicket()

        response = self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP4",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["striker"],
            "RP4"
        )

        self.assertEqual(
            response.data["non_striker"],
            "RP2"
        )

    def test_replace_dismissed_non_striker(self):
        response = self.client.post(
            "/matches/REPL1/innings/1/wicket/",
            {
                "wicket_type": "run-out",
                "player_out_id": "RP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        response = self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP4",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["striker"],
            "RP1"
        )

        self.assertEqual(
            response.data["non_striker"],
            "RP4"
        )

    def test_new_batsman_required(self):
        response = self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_replacement_player_must_be_in_batting_team(self):
        self.record_wicket()

        response = self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP3",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_replacement_player_cannot_already_be_at_crease(self):
        self.record_wicket()

        response = self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP2",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cannot_replace_without_wicket(self):
        response = self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP4",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP4",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_innings_not_found(self):
        response = self.client.post(
            "/matches/REPL1/innings/99/replace-batsman/",
            {
                "new_batsman_id": "RP4",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_replacement_persists(self):
        self.record_wicket()

        self.client.post(
            "/matches/REPL1/innings/1/replace-batsman/",
            {
                "new_batsman_id": "RP4",
            },
            format="json"
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.striker_id,
            "RP4"
        )

        self.assertEqual(
            self.innings.non_striker_id,
            "RP2"
        )