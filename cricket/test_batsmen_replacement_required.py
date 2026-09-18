from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.innings_service import InningsService


class BatsmanReplacementRequiredTestCase(TestCase):

    def setUp(self):
        self.striker = Player.objects.create(
            player_id="BR1",
            name="Striker",
            email="br1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="BR2",
            name="Non Striker",
            email="br2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.new_batsman = Player.objects.create(
            player_id="BR3",
            name="New Batsman",
            email="br3@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.bowler = Player.objects.create(
            player_id="BR4",
            name="Bowler",
            email="br4@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="BRT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.team1.players.add(
            self.striker,
            self.non_striker,
            self.new_batsman,
        )

        self.team2 = Team.objects.create(
            team_id="BRT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="BREPLACE1",
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

        self.service = InningsService()

    def test_ball_cannot_be_recorded_before_batsman_replacement(self):
        self.service.record_wicket(
            innings=self.innings,
            wicket_type="bowled",
            player_out_id="BR1",
            runs=0,
        )

        with self.assertRaisesMessage(
            ValueError,
            "New batsman must be selected before recording the next ball."
        ):
            self.service.record_ball(
                innings=self.innings,
                runs=0,
            )

    def test_ball_can_be_recorded_after_batsman_replacement(self):
        self.service.record_wicket(
            innings=self.innings,
            wicket_type="bowled",
            player_out_id="BR1",
            runs=0,
        )

        self.service.replace_batsman(
            innings=self.innings,
            new_batsman_id="BR3",
        )

        ball = self.service.record_ball(
            innings=self.innings,
            runs=1,
        )

        self.assertIsNotNone(ball)

    def test_ball_can_be_recorded_without_previous_wicket(self):
        ball = self.service.record_ball(
            innings=self.innings,
            runs=1,
        )

        self.assertIsNotNone(ball)