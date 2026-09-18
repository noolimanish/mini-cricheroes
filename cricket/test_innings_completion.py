from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.innings_service import InningsService


class InningsCompletionTestCase(TestCase):

    def setUp(self):
        self.striker = Player.objects.create(
            player_id="IC1",
            name="Striker",
            email="ic1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.non_striker = Player.objects.create(
            player_id="IC2",
            name="Non Striker",
            email="ic2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="IC3",
            name="Bowler",
            email="ic3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="ICT1",
            team_name="Batting Team",
            captain=self.striker,
        )

        self.team1.players.add(
            self.striker,
            self.non_striker,
        )

        self.team2 = Team.objects.create(
            team_id="ICT2",
            team_name="Bowling Team",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="INNCOMP1",
            team1=self.team1,
            team2=self.team2,
            ground="Completion Ground",
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
            overs=1,
            striker=self.striker,
            non_striker=self.non_striker,
            current_bowler=self.bowler,
        )

        self.service = InningsService()

    def test_innings_complete_after_last_over(self):
        for _ in range(6):
            self.service.record_ball(
                innings=self.innings,
                runs=0,
            )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.balls_bowled,
            6,
        )

        self.assertEqual(
            self.innings.current_over,
            1,
        )

        with self.assertRaisesMessage(
            ValueError,
            "Innings overs limit has been reached."
        ):
            self.service.record_ball(
                innings=self.innings,
                runs=0,
            )

    def test_innings_complete_after_tenth_wicket(self):
        self.innings.wickets_fallen = 10

        self.innings.save(
            update_fields=["wickets_fallen"]
        )

        with self.assertRaisesMessage(
            ValueError,
            "All 10 wickets have fallen. Innings is complete."
        ):
            self.service.record_ball(
                innings=self.innings,
                runs=0,
            )