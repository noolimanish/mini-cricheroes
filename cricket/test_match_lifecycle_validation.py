from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
)

from cricket.services.innings_service import InningsService


class MatchLifecycleValidationTestCase(TestCase):

    def setUp(self):
        self.player1 = Player.objects.create(
            player_id="MLV1",
            name="Player One",
            email="mlv1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="MLV2",
            name="Player Two",
            email="mlv2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="MLV3",
            name="Bowler",
            email="mlv3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="MLVT1",
            team_name="Team One",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1,
            self.player2,
        )

        self.team2 = Team.objects.create(
            team_id="MLVT2",
            team_name="Team Two",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="MLV1",
            team1=self.team1,
            team2=self.team2,
            ground="Lifecycle Ground",
            ball_type="tennis",
            overs=20,
            status="scheduled",
            toss_winner=self.team1,
            toss_decision="bat",
            batting_team=self.team1,
            bowling_team=self.team2,
        )

        self.service = InningsService()

    def test_innings_cannot_be_created_before_match_starts(self):
        with self.assertRaisesMessage(
            ValueError,
            "Match must be live to create an innings."
        ):
            self.service.create_innings(
                self.match,
                self.team1,
                self.team2,
                20,
            )


    def test_innings_cannot_be_created_after_match_completion(self):
        self.match.status = "completed"
        self.match.save()

        with self.assertRaisesMessage(
            ValueError,
            "Match must be live to create an innings."
        ):
            self.service.create_innings(
                self.match,
                self.team1,
                self.team2,
                20,
            )