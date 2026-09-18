from cricket.services.innings_service import InningsService


class MatchResultService:

    def calculate_result(self, match):

        # Match is already completed
        if match.status == "completed":
            raise ValueError(
                "Match is already completed."
            )

        innings = match.innings.order_by(
            "innings_number"
        )

        # Both innings are required
        if innings.count() != 2:
            raise ValueError(
                "Both innings must be completed before calculating result."
            )

        first_innings = innings[0]
        second_innings = innings[1]

        # Both innings must be completed
        innings_service = InningsService()

        if not innings_service.is_innings_complete(
            first_innings
        ):
            raise ValueError(
                "Both innings must be completed before calculating result."
            )

        if not innings_service.is_innings_complete(
            second_innings
        ):
            raise ValueError(
                "Both innings must be completed before calculating result."
            )

        # Team 2 wins by wickets
        if (
            second_innings.total_runs
            > first_innings.total_runs
        ):
            winner = second_innings.batting_team
            result_type = "wickets"

            wickets_lost = second_innings.wickets_fallen
            result_margin = 10 - wickets_lost

        # Team 1 wins by runs
        elif (
            first_innings.total_runs
            > second_innings.total_runs
        ):
            winner = first_innings.batting_team
            result_type = "runs"

            result_margin = (
                first_innings.total_runs
                - second_innings.total_runs
            )

        # Match tied
        else:
            winner = None
            result_type = "tie"
            result_margin = 0

        match.winner = winner
        match.result_type = result_type
        match.result_margin = result_margin
        match.status = "completed"

        match.save(
            update_fields=[
                "winner",
                "result_type",
                "result_margin",
                "status",
            ]
        )

        return match