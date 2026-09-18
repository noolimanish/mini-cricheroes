import logging

from django.db import transaction

from cricket.models import (
    Innings,
    Over,
    Ball,
    BatsmanStats,
    BowlerStats,
)


logger = logging.getLogger(__name__)


class InningsService:

    def create_innings(
        self,
        match,
        batting_team,
        bowling_team,
        overs
    ):
        if match.status != "live":
            raise ValueError(
                "Match must be live to create an innings."
            )

        innings = Innings.objects.create(
            innings_number=match.innings.count() + 1,
            match=match,
            batting_team=batting_team,
            bowling_team=bowling_team,
            overs=overs
        )

        logger.info(
            "Innings %s created for match %s",
            innings.innings_number,
            match.match_id
        )

        return innings

    def create_next_innings(
        self,
        match,
        overs
    ):
        """
        Create the next innings of a match.

        First innings:
            Uses the batting and bowling teams decided
            by the toss.

        Second innings:
            Reverses the teams from the first innings.

        This method contains the business rules for
        creating innings. The API view should only
        receive the request and call this method.
        """

        if match.status != "live":
            raise ValueError(
                "Match must be live to create an innings."
            )

        if not match.batting_team_id or not match.bowling_team_id:
            raise ValueError(
                "Toss decision must be made before creating an innings."
            )

        if overs <= 0:
            raise ValueError(
                "Overs must be a positive integer."
            )

        existing_innings = match.innings.order_by(
            "innings_number"
        )

        innings_count = existing_innings.count()

        # Only two innings are allowed.
        if innings_count >= 2:
            raise ValueError(
                "Both innings have already been created."
            )

        # First innings.
        if innings_count == 0:
            return self.create_innings(
                match=match,
                batting_team=match.batting_team,
                bowling_team=match.bowling_team,
                overs=overs
            )

        # Second innings.
        first_innings = existing_innings.first()

        if not self.is_innings_complete(first_innings):
            raise ValueError(
                "First innings is not complete."
            )

        # Reverse the teams for the second innings.
        batting_team = first_innings.bowling_team
        bowling_team = first_innings.batting_team

        return self.create_innings(
            match=match,
            batting_team=batting_team,
            bowling_team=bowling_team,
            overs=overs
        )

    def set_opening_batsmen(
        self,
        innings,
        striker_id,
        non_striker_id
    ):
        if innings.striker_id or innings.non_striker_id:
            raise ValueError(
                "Opening batsmen have already been set."
            )

        if striker_id == non_striker_id:
            raise ValueError(
                "Striker and non-striker must be different."
            )

        if not innings.batting_team.players.filter(
            player_id=striker_id
        ).exists():
            raise ValueError(
                f"{striker_id} is not part of the batting team."
            )

        if not innings.batting_team.players.filter(
            player_id=non_striker_id
        ).exists():
            raise ValueError(
                f"{non_striker_id} is not part of the batting team."
            )

        innings.striker_id = striker_id
        innings.non_striker_id = non_striker_id

        innings.save(
            update_fields=[
                "striker",
                "non_striker"
            ]
        )

        logger.info(
            "Opening batsmen set for match %s innings %s: striker=%s non_striker=%s",
            innings.match.match_id,
            innings.innings_number,
            striker_id,
            non_striker_id
        )

        return innings

    def set_bowler(
        self,
        innings,
        bowler_id
    ):
        if not innings.bowling_team.players.filter(
            player_id=bowler_id
        ).exists():
            raise ValueError(
                f"{bowler_id} is not part of the bowling team."
            )

        innings.current_bowler_id = bowler_id

        innings.save(
            update_fields=["current_bowler"]
        )

        logger.info(
            "Bowler %s selected for match %s innings %s",
            bowler_id,
            innings.match.match_id,
            innings.innings_number
        )

        return innings

    def create_over(
        self,
        innings
    ):
        if not innings.current_bowler_id:
            raise ValueError(
                "A bowler must be selected before creating an over."
            )

        if innings.overs_data.count() >= innings.overs:
            raise ValueError(
                "Innings overs limit has been reached."
            )

        over_number = innings.overs_data.count() + 1

        over = Over.objects.create(
            innings=innings,
            over_number=over_number,
            bowler_id=innings.current_bowler_id
        )

        logger.info(
            "Over %s created for match %s innings %s",
            over_number,
            innings.match.match_id,
            innings.innings_number
        )

        return over

    def _get_batsman_stats(
        self,
        innings,
        player_id
    ):
        stats, created = BatsmanStats.objects.get_or_create(
            innings=innings,
            player_id=player_id
        )

        return stats

    def _get_bowler_stats(
        self,
        innings,
        player_id
    ):
        stats, created = BowlerStats.objects.get_or_create(
            innings=innings,
            player_id=player_id
        )

        return stats

    def record_ball(
        self,
        innings,
        runs=0,
        extra_type=None,
        extra_runs=0
    ):
        with transaction.atomic():
            if innings.wickets_fallen >= 10:
                raise ValueError(
                    "All 10 wickets have fallen. Innings is complete."
                )

            if innings.striker_id is None:
                raise ValueError(
                    "Opening batsmen must be set before recording a ball."
                )

            if innings.current_bowler_id is None:
                raise ValueError(
                    "Bowler must be set before recording a ball."
                )

            if runs < 0:
                raise ValueError(
                    "Runs cannot be negative."
                )

            if extra_runs < 0:
                raise ValueError(
                    "Extra runs cannot be negative."
                )

            valid_extra_types = {
                "wide",
                "no-ball",
                "bye",
                "leg-bye"
            }

            if extra_type is not None:
                extra_type = extra_type.lower()

                if extra_type not in valid_extra_types:
                    raise ValueError(
                        f"Invalid extra type. Choose from {valid_extra_types}."
                    )

            latest_wicket = (
                innings.overs_data
                .filter(balls__wicket=True)
                .order_by(
                    "-over_number",
                    "-balls__ball_number"
                )
                .first()
            )

            if latest_wicket is not None:
                dismissed_player_id = (
                    latest_wicket.balls
                    .filter(wicket=True)
                    .order_by("-ball_number")
                    .values_list(
                        "player_out_id",
                        flat=True
                    )
                    .first()
                )

                if dismissed_player_id in {
                    innings.striker_id,
                    innings.non_striker_id
                }:
                    raise ValueError(
                        "New batsman must be selected before recording the next ball."
                    )

            over = (
                innings.overs_data
                .filter(legal_balls__lt=6)
                .order_by("-over_number")
                .first()
            )

            if over is None:
                over = self.create_over(innings)

            if (
                over.over_number == innings.overs
                and over.legal_balls >= 6
            ):
                raise ValueError(
                    "Innings overs limit has been reached."
                )

            ball_number = over.balls.count() + 1

            is_legal = True

            if extra_type in {"wide", "no-ball"}:
                is_legal = False

            striker_id = innings.striker_id
            bowler_id = innings.current_bowler_id

            ball = Ball.objects.create(
                over=over,
                ball_number=ball_number,
                striker_id=striker_id,
                non_striker_id=innings.non_striker_id,
                bowler_id=bowler_id,
                runs=runs,
                extras=extra_runs,
                extra_type=extra_type,
                is_legal=is_legal
            )

            over.total_runs += runs + extra_runs

            if is_legal:
                over.legal_balls += 1

            over.save(
                update_fields=[
                    "total_runs",
                    "legal_balls"
                ]
            )

            innings.total_runs += runs + extra_runs

            if is_legal:
                innings.balls_bowled += 1

            innings.current_over = over.over_number

            innings.save(
                update_fields=[
                    "total_runs",
                    "balls_bowled",
                    "current_over"
                ]
            )

            batsman_stats = self._get_batsman_stats(
                innings,
                striker_id
            )

            if extra_type != "wide":
                batsman_stats.balls_faced += 1

                if extra_type not in {"bye", "leg-bye"}:
                    batsman_stats.runs += runs

                    if runs == 4:
                        batsman_stats.fours += 1

                    elif runs == 6:
                        batsman_stats.sixes += 1

            batsman_stats.save()

            bowler_stats = self._get_bowler_stats(
                innings,
                bowler_id
            )

            if is_legal:
                bowler_stats.balls_bowled += 1

            if extra_type not in {"bye", "leg-bye"}:
                bowler_stats.runs_conceded += runs + extra_runs

            if extra_type == "wide":
                bowler_stats.wides += extra_runs

            elif extra_type == "no-ball":
                bowler_stats.no_balls += extra_runs

            bowler_stats.save()

            if extra_type == "wide":
                total_rotation_runs = max(
                    extra_runs - 1,
                    0
                )

            elif extra_type in {
                "bye",
                "leg-bye"
            }:
                total_rotation_runs = extra_runs

            else:
                total_rotation_runs = runs

            if total_rotation_runs % 2 == 1:
                (
                    innings.striker_id,
                    innings.non_striker_id
                ) = (
                    innings.non_striker_id,
                    innings.striker_id
                )

                innings.save(
                    update_fields=[
                        "striker",
                        "non_striker"
                    ]
                )

            if is_legal and over.legal_balls == 6:
                innings.striker_id, innings.non_striker_id = (
                    innings.non_striker_id,
                    innings.striker_id
                )

                innings.save(
                    update_fields=[
                        "striker",
                        "non_striker"
                    ]
                )

            self._check_match_completion(innings)

            logger.info(
                "Ball recorded: match=%s innings=%s over=%s ball=%s runs=%s extras=%s",
                innings.match.match_id,
                innings.innings_number,
                over.over_number,
                ball_number,
                runs,
                extra_runs
            )

            return ball

    def record_wicket(
        self,
        innings,
        wicket_type,
        player_out_id,
        runs=0
    ):
        with transaction.atomic():
            valid_wicket_types = {
                "bowled",
                "caught",
                "lbw",
                "run-out",
                "stumped",
                "hit-wicket"
            }

            wicket_type = wicket_type.lower()

            if wicket_type not in valid_wicket_types:
                raise ValueError(
                    f"Invalid wicket type. Choose from {valid_wicket_types}."
                )

            if innings.wickets_fallen >= 10:
                raise ValueError(
                    "All 10 wickets have fallen. Innings is complete."
                )

            if innings.striker_id is None:
                raise ValueError(
                    "Opening batsmen must be set before recording a wicket."
                )

            if innings.current_bowler_id is None:
                raise ValueError(
                    "Bowler must be set before recording a wicket."
                )

            over = (
                innings.overs_data
                .filter(legal_balls__lt=6)
                .order_by("-over_number")
                .first()
            )

            if over is None:
                over = self.create_over(innings)

            if (
                over.over_number == innings.overs
                and over.legal_balls >= 6
            ):
                raise ValueError(
                    "Innings overs limit has been reached."
                )

            if player_out_id not in {
                innings.striker_id,
                innings.non_striker_id
            }:
                raise ValueError(
                    "Player being dismissed must be one of the current batsmen."
                )

            ball_number = over.balls.count() + 1

            striker_id = innings.striker_id
            bowler_id = innings.current_bowler_id

            ball = Ball.objects.create(
                over=over,
                ball_number=ball_number,
                striker_id=striker_id,
                non_striker_id=innings.non_striker_id,
                bowler_id=bowler_id,
                runs=runs,
                is_legal=True,
                wicket=True,
                wicket_type=wicket_type,
                player_out_id=player_out_id
            )

            over.total_runs += runs
            over.legal_balls += 1
            over.wickets += 1

            over.save(
                update_fields=[
                    "total_runs",
                    "legal_balls",
                    "wickets"
                ]
            )

            innings.total_runs += runs
            innings.balls_bowled += 1
            innings.wickets_fallen += 1
            innings.current_over = over.over_number

            innings.save(
                update_fields=[
                    "total_runs",
                    "balls_bowled",
                    "wickets_fallen",
                    "current_over"
                ]
            )

            batsman_stats = self._get_batsman_stats(
                innings,
                player_out_id
            )

            batsman_stats.balls_faced += 1
            batsman_stats.is_out = True
            batsman_stats.dismissal_type = wicket_type

            batsman_stats.save()

            bowler_stats = self._get_bowler_stats(
                innings,
                bowler_id
            )

            bowler_stats.balls_bowled += 1

            if wicket_type != "run-out":
                bowler_stats.wickets += 1

            bowler_stats.runs_conceded += runs

            bowler_stats.save()

            self._check_match_completion(innings)

            logger.info(
                "Wicket recorded: match=%s innings=%s player_out=%s wicket_type=%s",
                innings.match.match_id,
                innings.innings_number,
                player_out_id,
                wicket_type
            )

            return ball

    def replace_batsman(
        self,
        innings,
        new_batsman_id
    ):
        if not innings.batting_team.players.filter(
            player_id=new_batsman_id
        ).exists():
            raise ValueError(
                f"{new_batsman_id} is not part of the batting team."
            )

        if new_batsman_id in {
            innings.striker_id,
            innings.non_striker_id
        }:
            raise ValueError(
                "New batsman is already at the crease."
            )

        if innings.wickets_fallen == 0:
            raise ValueError(
                "A batsman can only be replaced after a wicket."
            )

        if innings.striker_id is None and innings.non_striker_id is None:
            raise ValueError(
                "No batsman is available to replace."
            )

        latest_wicket = (
            innings.overs_data
            .filter(balls__wicket=True)
            .order_by(
                "-over_number",
                "-balls__ball_number"
            )
            .first()
        )

        if latest_wicket is None:
            raise ValueError(
                "No wicket record found."
            )

        dismissed_player_id = (
            latest_wicket.balls
            .filter(wicket=True)
            .order_by("-ball_number")
            .values_list(
                "player_out_id",
                flat=True
            )
            .first()
        )

        if dismissed_player_id == innings.striker_id:
            innings.striker_id = new_batsman_id

        elif dismissed_player_id == innings.non_striker_id:
            innings.non_striker_id = new_batsman_id

        else:
            raise ValueError(
                "Dismissed player is not currently at the crease."
            )

        innings.save(
            update_fields=[
                "striker",
                "non_striker"
            ]
        )

        logger.info(
            "Batsman replaced in match %s innings %s: dismissed=%s new=%s",
            innings.match.match_id,
            innings.innings_number,
            dismissed_player_id,
            new_batsman_id
        )

        return innings

    def _check_match_completion(self, innings):
        """
        If the second innings is complete and the first
        innings is also complete, calculate the final result.
        """

        if innings.innings_number != 2:
            return

        if not self.is_innings_complete(innings):
            return

        first_innings = Innings.objects.get(
            match=innings.match,
            innings_number=1,
        )

        if not self.is_innings_complete(first_innings):
            return

        from cricket.services.match_result_service import (
            MatchResultService
        )

        logger.info(
            "Both innings complete for match %s. Calculating result.",
            innings.match.match_id
        )

        MatchResultService().calculate_result(
            innings.match
        )

    def is_innings_complete(self, innings):

        if innings.wickets_fallen >= 10:
            return True

        if innings.balls_bowled >= innings.overs * 6:
            return True

        if innings.innings_number == 2:

            first_innings = Innings.objects.get(
                match=innings.match,
                innings_number=1,
            )

            if innings.total_runs > first_innings.total_runs:
                return True

        return False