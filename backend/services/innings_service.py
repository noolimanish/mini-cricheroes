from backend.innings import Innings


class InningsService:

    def create_innings(
        self,
        batting_team,
        bowling_team,
        overs
    ):
        return Innings(
            batting_team,
            bowling_team,
            overs
        )

    def set_opening_batsmen(
        self,
        innings,
        striker_id,
        non_striker_id
    ):
        innings.set_opening_batsmen(
            striker_id,
            non_striker_id
        )

    def set_bowler(
        self,
        innings,
        bowler_id
    ):
        if bowler_id not in innings.bowling_team.player_ids:
            raise ValueError(
                f"{bowler_id} is not part of the bowling team."
            )

        innings.current_bowler_id = bowler_id

    def record_ball(
        self,
        innings,
        runs=0,
        extra_type=None,
        extra_runs=0
    ):
        return innings.record_ball(
            runs=runs,
            extra_type=extra_type,
            extra_runs=extra_runs
        )

    def record_wicket(
        self,
        innings,
        wicket_type,
        runs=0
    ):
        return innings.record_wicket(
            wicket_type,
            runs
        )

    def replace_batsman(
        self,
        innings,
        new_batsman_id
    ):
        return innings.replace_batsman(
            new_batsman_id
        )