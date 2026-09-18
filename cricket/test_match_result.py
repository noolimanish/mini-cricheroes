from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.innings_service import InningsService


class MatchResultTestCase(TestCase):

    def setUp(self):
        self.batsman1 = Player.objects.create(
            player_id="MR1",
            name="Batsman 1",
            email="mr1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.batsman2 = Player.objects.create(
            player_id="MR2",
            name="Batsman 2",
            email="mr2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="MR3",
            name="Bowler",
            email="mr3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="MRT1",
            team_name="India",
            captain=self.batsman1,
        )

        self.team1.players.add(
            self.batsman1,
            self.batsman2,
        )

        self.team2 = Team.objects.create(
            team_id="MRT2",
            team_name="Australia",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="MR001",
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

        self.service = InningsService()

    def test_chasing_team_completes_innings_after_reaching_target(self):
        first_innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
        )

        second_innings = Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=151,
        )

        self.assertTrue(
            self.service.is_innings_complete(second_innings)
        )

    def test_chasing_team_is_not_complete_before_target(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=150,
        )

        second_innings = Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            total_runs=149,
        )

        self.assertFalse(
            self.service.is_innings_complete(second_innings)
        )
        
    def test_chasing_team_completes_after_recording_target_run(self):
        first_innings = Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=10,
        )

        second_innings = Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            striker=self.batsman1,
            non_striker=self.batsman2,
            current_bowler=self.bowler,
            total_runs=10,
        )

        self.service.record_ball(
            innings=second_innings,
            runs=1,
        )

        second_innings.refresh_from_db()

        self.assertEqual(
            second_innings.total_runs,
            11,
        )

        self.assertTrue(
            self.service.is_innings_complete(second_innings)
        )

    def test_chasing_team_does_not_complete_before_target(self):
        Innings.objects.create(
            innings_number=1,
            match=self.match,
            batting_team=self.team1,
            bowling_team=self.team2,
            overs=20,
            total_runs=10,
        )

        second_innings = Innings.objects.create(
            innings_number=2,
            match=self.match,
            batting_team=self.team2,
            bowling_team=self.team1,
            overs=20,
            striker=self.batsman1,
            non_striker=self.batsman2,
            current_bowler=self.bowler,
            total_runs=8,
        )

        self.service.record_ball(
            innings=second_innings,
            runs=1,
        )

        second_innings.refresh_from_db()

        self.assertEqual(
            second_innings.total_runs,
            9,
        )

        self.assertFalse(
            self.service.is_innings_complete(second_innings)
        )