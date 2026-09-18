from django.test import TestCase
from rest_framework.test import APIClient
from cricket.test_helpers import authenticate_client
from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
    Over,
    Ball,
    BatsmanStats,
    BowlerStats,
)

from cricket.services.innings_service import InningsService


class InningsServiceTestCase(TestCase):

    def setUp(self):
        # Players
        self.p1 = Player.objects.create(
            player_id="TP1",
            name="Test Batsman 1",
            email="tp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.p2 = Player.objects.create(
            player_id="TP2",
            name="Test Batsman 2",
            email="tp2@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.p3 = Player.objects.create(
            player_id="TP3",
            name="Test Bowler",
            email="tp3@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        # Teams
        self.batting_team = Team.objects.create(
            team_id="TIND",
            team_name="Test India",
            captain=self.p1,
        )

        self.bowling_team = Team.objects.create(
            team_id="TAUS",
            team_name="Test Australia",
            captain=self.p3,
        )

        self.batting_team.players.add(
            self.p1,
            self.p2,
        )

        self.bowling_team.players.add(
            self.p3,
        )

        # Match
        self.match = Match.objects.create(
            match_id="TM001",
            team1=self.batting_team,
            team2=self.bowling_team,
            ground="Test Ground",
            ball_type="tennis",
            overs=20,
            status="live",
        )

        # Service
        self.service = InningsService()

        # Innings
        self.innings = self.service.create_innings(
            match=self.match,
            batting_team=self.batting_team,
            bowling_team=self.bowling_team,
            overs=20,
        )

        # Opening batsmen + bowler
        self.service.set_opening_batsmen(
            self.innings,
            "TP1",
            "TP2",
        )

        self.service.set_bowler(
            self.innings,
            "TP3",
        )

    def test_create_innings(self):
        self.assertEqual(
            self.innings.innings_number,
            1,
        )

        self.assertEqual(
            self.innings.batting_team,
            self.batting_team,
        )

        self.assertEqual(
            self.innings.bowling_team,
            self.bowling_team,
        )

        self.assertEqual(
            self.innings.overs,
            20,
        )

    def test_set_opening_batsmen(self):
        self.assertEqual(
            self.innings.striker_id,
            "TP1",
        )

        self.assertEqual(
            self.innings.non_striker_id,
            "TP2",
        )

    def test_set_bowler(self):
        self.assertEqual(
            self.innings.current_bowler_id,
            "TP3",
        )

    def test_record_normal_four(self):
        ball = self.service.record_ball(
            self.innings,
            runs=4,
        )

        self.assertEqual(
            ball.runs,
            4,
        )

        self.assertTrue(
            ball.is_legal,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            4,
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertEqual(
            batsman_stats.runs,
            4,
        )

        self.assertEqual(
            batsman_stats.balls_faced,
            1,
        )

        self.assertEqual(
            batsman_stats.fours,
            1,
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.balls_bowled,
            1,
        )

        self.assertEqual(
            bowler_stats.runs_conceded,
            4,
        )

    def test_record_wide(self):
        self.service.record_ball(
            self.innings,
            runs=0,
            extra_type="wide",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            1,
        )

        self.assertEqual(
            self.innings.balls_bowled,
            0,
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.balls_bowled,
            0,
        )

        self.assertEqual(
            bowler_stats.runs_conceded,
            1,
        )

        self.assertEqual(
            bowler_stats.wides,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertEqual(
            batsman_stats.balls_faced,
            0,
        )

    def test_record_no_ball(self):
        self.service.record_ball(
            self.innings,
            runs=0,
            extra_type="no-ball",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            1,
        )

        self.assertEqual(
            self.innings.balls_bowled,
            0,
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.balls_bowled,
            0,
        )

        self.assertEqual(
            bowler_stats.runs_conceded,
            1,
        )

        self.assertEqual(
            bowler_stats.no_balls,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertEqual(
            batsman_stats.balls_faced,
            1,
        )

    def test_record_bye(self):
        self.service.record_ball(
            self.innings,
            runs=0,
            extra_type="bye",
            extra_runs=1,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            1,
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertEqual(
            batsman_stats.runs,
            0,
        )

        self.assertEqual(
            batsman_stats.balls_faced,
            1,
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.balls_bowled,
            1,
        )

        self.assertEqual(
            bowler_stats.runs_conceded,
            0,
        )

    def test_record_leg_bye(self):
        self.service.record_ball(
            self.innings,
            runs=0,
            extra_type="leg-bye",
            extra_runs=2,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.total_runs,
            2,
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertEqual(
            batsman_stats.runs,
            0,
        )

        self.assertEqual(
            batsman_stats.balls_faced,
            1,
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.runs_conceded,
            0,
        )

    def test_record_bowled_wicket(self):
        ball = self.service.record_wicket(
            self.innings,
            wicket_type="bowled",
            player_out_id="TP1",
        )

        self.assertTrue(
            ball.wicket,
        )

        self.assertEqual(
            ball.player_out_id,
            "TP1",
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.wickets_fallen,
            1,
        )

        self.assertEqual(
            self.innings.balls_bowled,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertTrue(
            batsman_stats.is_out,
        )

        self.assertEqual(
            batsman_stats.dismissal_type,
            "bowled",
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.wickets,
            1,
        )

    def test_record_run_out(self):
        ball = self.service.record_wicket(
            self.innings,
            wicket_type="run-out",
            player_out_id="TP1",
        )

        self.assertTrue(
            ball.wicket,
        )

        self.innings.refresh_from_db()

        self.assertEqual(
            self.innings.wickets_fallen,
            1,
        )

        batsman_stats = BatsmanStats.objects.get(
            innings=self.innings,
            player=self.p1,
        )

        self.assertTrue(
            batsman_stats.is_out,
        )

        bowler_stats = BowlerStats.objects.get(
            innings=self.innings,
            player=self.p3,
        )

        self.assertEqual(
            bowler_stats.wickets,
            0,
        )


class PlayerAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player = Player.objects.create(
            player_id="P100",
            name="API Test Player",
            email="p100@test.com",
            role="batsman",
            batting_style="right-hand",
        )

    def test_get_player_list(self):
        response = self.client.get(
            "/players/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["player_id"],
            "P100",
        )

    def test_create_player(self):
        data = {
            "player_id": "P101",
            "name": "New API Player",
            "email": "p101@test.com",
            "role": "batsman",
            "batting_style": "right-hand",
            "bowling_type": None,
            "bowling_style": None,
        }

        response = self.client.post(
            "/players/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["player_id"],
            "P101",
        )

        self.assertTrue(
            Player.objects.filter(
                player_id="P101"
            ).exists()
        )

    def test_duplicate_player_id(self):
        
        data = {
            "player_id": "P100",
            "name": "Duplicate Player",
            "email": "duplicate@test.com",
            "role": "batsman",
            "batting_style": "right-hand",
            "bowling_type": None,
            "bowling_style": None,
        }

        response = self.client.post(
            "/players/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "player_id",
            response.data,
        )

    def test_get_player_detail(self):
        response = self.client.get(
            "/players/P100/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["player_id"],
            "P100",
        )

        self.assertEqual(
            response.data["name"],
            "API Test Player",
        )

    def test_get_unknown_player(self):
        response = self.client.get(
            "/players/UNKNOWN/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.data["error"],
            "Player not found.",
        )

    def test_update_player(self):
        data = {
            "player_id": "P100",
            "name": "Updated API Player",
            "email": "updated@test.com",
            "role": "all-rounder",
            "batting_style": "right-hand",
            "bowling_type": "seam",
            "bowling_style": "right-arm-medium",
        }

        response = self.client.put(
            "/players/P100/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["name"],
            "Updated API Player",
        )

        self.assertEqual(
            response.data["role"],
            "all-rounder",
        )

        self.player.refresh_from_db()

        self.assertEqual(
            self.player.name,
            "Updated API Player",
        )

    def test_delete_player(self):
        response = self.client.delete(
            "/players/P100/"
        )

        self.assertEqual(
            response.status_code,
            204,
        )

        self.assertFalse(
            Player.objects.filter(
                player_id="P100"
            ).exists()
        )

    def test_get_deleted_player(self):
        self.client.delete(
            "/players/P100/"
        )

        response = self.client.get(
            "/players/P100/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )


from rest_framework.test import APIClient
from django.test import TestCase

from cricket.models import Player, Team


class TeamAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="TP1",
            name="Team Player One",
            email="tp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="TP2",
            name="Team Player Two",
            email="tp2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team = Team.objects.create(
            team_id="TST",
            team_name="Test Team",
            captain=self.player1,
        )

        self.team.players.add(
            self.player1,
            self.player2
        )

    def test_get_teams(self):
        response = self.client.get("/teams/")

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]["team_id"],
            "TST"
        )

    def test_create_team(self):
        
        response = self.client.post(
            "/teams/",
            {
                "team_id": "NEW",
                "team_name": "New Team",
                "players": [
                    "TP1",
                    "TP2"
                ],
                "captain": "TP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["team_id"],
            "NEW"
        )

        self.assertEqual(
            response.data["players"],
            ["TP1", "TP2"]
        )

        self.assertEqual(
            response.data["captain"],
            "TP1"
        )

    def test_duplicate_team_id(self):
        response = self.client.post(
            "/teams/",
            {
                "team_id": "TST",
                "team_name": "Duplicate Team",
                "players": [],
                "captain": None,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_get_team_detail(self):
        response = self.client.get(
            "/teams/TST/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["team_id"],
            "TST"
        )

        self.assertEqual(
            response.data["team_name"],
            "Test Team"
        )

        self.assertEqual(
            set(response.data["players"]),
            {"TP1", "TP2"}
        )

        self.assertEqual(
            response.data["captain"],
            "TP1"
        )

    def test_unknown_team(self):
        response = self.client.get(
            "/teams/UNKNOWN/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_update_team(self):
        response = self.client.put(
            "/teams/TST/",
            {
                "team_id": "TST",
                "team_name": "Updated Team",
                "players": [
                    "TP1"
                ],
                "captain": "TP1",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["team_name"],
            "Updated Team"
        )

        self.assertEqual(
            response.data["players"],
            ["TP1"]
        )

        self.assertEqual(
            response.data["captain"],
            "TP1"
        )

    def test_delete_team(self):
        response = self.client.delete(
            "/teams/TST/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

        response = self.client.get(
            "/teams/TST/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

class MatchAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="MP1",
            name="Match Player One",
            email="mp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="MP2",
            name="Match Player Two",
            email="mp2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="MT1",
            team_name="Match Team One",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1
        )

        self.team2 = Team.objects.create(
            team_id="MT2",
            team_name="Match Team Two",
            captain=self.player2,
        )

        self.team2.players.add(
            self.player2
        )

        self.match = Match.objects.create(
            match_id="MAT1",
            team1=self.team1,
            team2=self.team2,
            ground="Test Ground",
            ball_type="tennis",
            overs=10,
            status="live",
        )

    def test_get_matches(self):
        response = self.client.get(
            "/matches/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]["match_id"],
            "MAT1"
        )

    def test_create_match(self):
        response = self.client.post(
            "/matches/",
            {
                "match_id": "MAT2",
                "team1": "MT1",
                "team2": "MT2",
                "ground": "New Ground",
                "ball_type": "leather",
                "overs": 20,
                "status": "scheduled",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["match_id"],
            "MAT2"
        )

        self.assertEqual(
            response.data["team1"],
            "MT1"
        )

        self.assertEqual(
            response.data["team2"],
            "MT2"
        )

    def test_duplicate_match_id(self):
        response = self.client.post(
            "/matches/",
            {
                "match_id": "MAT1",
                "team1": "MT1",
                "team2": "MT2",
                "ground": "Duplicate Ground",
                "ball_type": "tennis",
                "overs": 10,
                "status": "scheduled",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_get_match_detail(self):
        response = self.client.get(
            "/matches/MAT1/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["match_id"],
            "MAT1"
        )

        self.assertEqual(
            response.data["team1"],
            "MT1"
        )

        self.assertEqual(
            response.data["team2"],
            "MT2"
        )

        self.assertEqual(
            response.data["ground"],
            "Test Ground"
        )

    def test_unknown_match(self):
        response = self.client.get(
            "/matches/UNKNOWN/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_update_match(self):
        response = self.client.put(
            "/matches/MAT1/",
            {
                "match_id": "MAT1",
                "team1": "MT1",
                "team2": "MT2",
                "ground": "Updated Ground",
                "ball_type": "leather",
                "overs": 20,
                "status": "scheduled",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["ground"],
            "Updated Ground"
        )

        self.assertEqual(
            response.data["ball_type"],
            "leather"
        )

        self.assertEqual(
            response.data["overs"],
            20
        )

    def test_delete_match(self):
        response = self.client.delete(
            "/matches/MAT1/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

        response = self.client.get(
            "/matches/MAT1/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

class MatchTossAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="TP1",
            name="Toss Player One",
            email="toss1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="TP2",
            name="Toss Player Two",
            email="toss2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="TS1",
            team_name="Toss Team One",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1
        )

        self.team2 = Team.objects.create(
            team_id="TS2",
            team_name="Toss Team Two",
            captain=self.player2,
        )

        self.team2.players.add(
            self.player2
        )

        self.match = Match.objects.create(
            match_id="TOSS1",
            team1=self.team1,
            team2=self.team2,
            ground="Toss Ground",
            ball_type="tennis",
            overs=10,
            status="scheduled",
        )

    def test_conduct_toss(self):
        response = self.client.post(
            "/matches/TOSS1/toss/",
            {
                "calling_team": "TS1",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            response.data["toss_result"],
            ["heads", "tails"]
        )

        self.assertIn(
            response.data["toss_winner"],
            ["TS1", "TS2"]
        )

        match = Match.objects.get(
            match_id="TOSS1"
        )

        self.assertEqual(
            match.toss_call,
            "heads"
        )

        self.assertIn(
            match.toss_result,
            ["heads", "tails"]
        )

        self.assertIn(
            match.toss_winner_id,
            ["TS1", "TS2"]
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/toss/",
            {
                "calling_team": "TS1",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    def test_missing_fields(self):
        response = self.client.post(
            "/matches/TOSS1/toss/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertIn(
            "error",
            response.data
        )

    def test_calling_team_not_found(self):
        response = self.client.post(
            "/matches/TOSS1/toss/",
            {
                "calling_team": "UNKNOWN",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Calling team not found."
        )

    def test_calling_team_not_part_of_match(self):
        other_player = Player.objects.create(
            player_id="TP3",
            name="Other Player",
            email="other@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        other_team = Team.objects.create(
            team_id="TS3",
            team_name="Other Team",
            captain=other_player,
        )

        other_team.players.add(
            other_player
        )

        response = self.client.post(
            "/matches/TOSS1/toss/",
            {
                "calling_team": "TS3",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Calling team must be one of the teams in the match."
        )

    def test_invalid_toss_call(self):
        response = self.client.post(
            "/matches/TOSS1/toss/",
            {
                "calling_team": "TS1",
                "call": "middle",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertIn(
            "Invalid toss call",
            response.data["error"]
        )

    def test_toss_requires_captain(self):
        self.team1.captain = None
        self.team1.save()

        response = self.client.post(
            "/matches/TOSS1/toss/",
            {
                "calling_team": "TS1",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Calling team must have a captain."
        )

    def test_toss_only_for_scheduled_match(self):
        self.match.status = "live"
        self.match.save()

        response = self.client.post(
            "/matches/TOSS1/toss/",
            {
                "calling_team": "TS1",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Toss can only be conducted for a scheduled match."
        )

class MatchTossDecisionAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        authenticate_client(self.client)

        self.player1 = Player.objects.create(
            player_id="DP1",
            name="Decision Player One",
            email="dp1@test.com",
            role="batsman",
            batting_style="right-hand",
        )

        self.player2 = Player.objects.create(
            player_id="DP2",
            name="Decision Player Two",
            email="dp2@test.com",
            role="bowler",
            batting_style="right-hand",
            bowling_type="seam",
            bowling_style="right-arm-fast",
        )

        self.team1 = Team.objects.create(
            team_id="DT1",
            team_name="Decision Team One",
            captain=self.player1,
        )

        self.team1.players.add(
            self.player1
        )

        self.team2 = Team.objects.create(
            team_id="DT2",
            team_name="Decision Team Two",
            captain=self.player2,
        )

        self.team2.players.add(
            self.player2
        )

        self.match = Match.objects.create(
            match_id="DEC1",
            team1=self.team1,
            team2=self.team2,
            ground="Decision Ground",
            ball_type="tennis",
            overs=10,
            status="scheduled",
        )

    def conduct_toss(self):
        response = self.client.post(
            "/matches/DEC1/toss/",
            {
                "calling_team": "DT1",
                "call": "heads",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.match.refresh_from_db()

    def test_choose_bat(self):
        self.conduct_toss()

        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {
                "decision": "bat",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.toss_decision,
            "bat"
        )

        self.assertEqual(
            self.match.batting_team_id,
            self.match.toss_winner_id
        )

        if self.match.toss_winner_id == "DT1":
            self.assertEqual(
                self.match.bowling_team_id,
                "DT2"
            )
        else:
            self.assertEqual(
                self.match.bowling_team_id,
                "DT1"
            )

    def test_choose_bowl(self):
        self.conduct_toss()

        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {
                "decision": "bowl",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.toss_decision,
            "bowl"
        )

        self.assertEqual(
            self.match.bowling_team_id,
            self.match.toss_winner_id
        )

        if self.match.toss_winner_id == "DT1":
            self.assertEqual(
                self.match.batting_team_id,
                "DT2"
            )
        else:
            self.assertEqual(
                self.match.batting_team_id,
                "DT1"
            )

    def test_decision_before_toss(self):
        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {
                "decision": "bat",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Toss must be conducted before choosing a decision."
        )

    def test_invalid_decision(self):
        self.conduct_toss()

        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {
                "decision": "draw",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Invalid toss decision. Choose bat or bowl."
        )

    def test_missing_decision(self):
        self.conduct_toss()

        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Decision is required."
        )

    def test_decision_already_made(self):
        self.conduct_toss()

        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {
                "decision": "bat",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        response = self.client.post(
            "/matches/DEC1/toss/decision/",
            {
                "decision": "bowl",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.data["error"],
            "Toss decision has already been made."
        )

    def test_match_not_found(self):
        response = self.client.post(
            "/matches/UNKNOWN/toss/decision/",
            {
                "decision": "bat",
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
        
    def test_create_team_with_captain_not_in_team(self):

        player1 = Player.objects.create(
            player_id="P1",
            name="Player One",
            email="p1@test.com",
            role="batsman",
            batting_style="right"
        )

        player2 = Player.objects.create(
            player_id="P2",
            name="Player Two",
            email="p2@test.com",
            role="batsman",
            batting_style="right"
        )

        response = self.client.post(
            "/teams/",
            {
                "team_id": "IND",
                "team_name": "India",
                "players": ["P1"],
                "captain": "P2"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertIn(
            "Captain must be a member of the team.",
            str(response.data)
        )


    def test_create_team_with_captain_in_team(self):

        player = Player.objects.create(
            player_id="P1",
            name="Player One",
            email="p1@test.com",
            role="batsman",
            batting_style="right"
        )

        response = self.client.post(
            "/teams/",
            {
                "team_id": "IND",
                "team_name": "India",
                "players": ["P1"],
                "captain": "P1"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201
        )