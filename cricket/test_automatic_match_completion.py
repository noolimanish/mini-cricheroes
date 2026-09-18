from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.innings_service import InningsService


class AutomaticMatchCompletionTestCase(TestCase):

    def setUp(self):
        self.batsman1 = Player.objects.create(
            player_id="AMC1",
            name="Batsman 1",
            email="amc1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.batsman2 = Player.objects.create(
            player_id="AMC2",
            name="Batsman 2",
            email="amc2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="AMC3",
            name="Bowler",
            email="amc3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="AMCT1",
            team_name="India",
            captain=self.batsman1,
        )

        self.team1.players.add(
            self.batsman1,
            self.batsman2,
        )

        self.team2 = Team.objects.create(
            team_id="AMCT2",
            team_name="Australia",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="AMC001",
            team1=self.team1,
            team2=self.team2,
            ground="Automatic Completion Ground",
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

        self.service = InningsService()

    def test_match_completes_automatically_when_chasing_team_reaches_target(self):
        first_innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=100,
            balls_bowled=120,
            current_over=20,
        )

        second_innings = Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=100,
            striker=self.batsman1,
            non_striker=self.batsman2,
            current_bowler=self.bowler,
        )

        self.service.record_ball(
            innings=second_innings,
            runs=1,
        )

        self.match.refresh_from_db()

        second_innings.refresh_from_db()

        self.assertEqual(
            second_innings.total_runs,
            101,
        )

        self.assertTrue(
            self.service.is_innings_complete(second_innings)
        )

        self.assertEqual(
            self.match.status,
            "completed",
        )

        self.assertEqual(
            self.match.winner,
            self.team2,
        )

        self.assertEqual(
            self.match.result_type,
            "wickets",
        )

        self.assertEqual(
            self.match.result_margin,
            10,
        )