from django.test import TestCase

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
)

from cricket.services.match_service import MatchService


class MatchStatusTestCase(TestCase):

    def setUp(self):
        self.player1 = Player.objects.create(
            player_id="MS1",
            name="Player 1",
            email="ms1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="MS2",
            name="Player 2",
            email="ms2@test.com",
            role="batsman",
            batting_style="left-hand",
        )

        self.bowler = Player.objects.create(
            player_id="MS3",
            name="Bowler",
            email="ms3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="MST1",
            team_name="Team 1",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1,
            self.player2,
        )

        self.team2 = Team.objects.create(
            team_id="MST2",
            team_name="Team 2",
            captain=self.bowler,
        )

        self.team2.players.add(
            self.bowler,
        )

        self.match = Match.objects.create(
            match_id="STATUS1",
            team1=self.team1,
            team2=self.team2,
            ground="Status Ground",
            ball_type="tennis",
            overs=20,
            status="scheduled",
            toss_winner=self.team1,
            toss_decision="bat",
            batting_team=self.team1,
            bowling_team=self.team2,
        )

        self.service = MatchService()

    def test_match_starts_as_scheduled(self):
        self.assertEqual(
            self.match.status,
            "scheduled",
        )

    def test_toss_does_not_start_match(self):
        self.service.conduct_toss(
            match=self.match,
            calling_team=self.team1,
            call="heads",
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "scheduled",
        )

    def test_match_can_be_started_after_toss_decision(self):
        self.service.start_match(
            self.match
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "live",
        )

    def test_live_match_can_be_completed(self):
        self.service.start_match(
            self.match
        )

        self.service.complete_match(
            self.match
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "completed",
        )

    def test_completed_match_cannot_be_started_again(self):
        self.match.status = "completed"
        self.match.save(
            update_fields=["status"]
        )

        with self.assertRaisesMessage(
            ValueError,
            "Completed match cannot be started again."
        ):
            self.service.start_match(
                self.match
            )