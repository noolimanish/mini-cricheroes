import logging
import random

from cricket.models import Match


logger = logging.getLogger(__name__)


class MatchService:

    def conduct_toss(
        self,
        match,
        calling_team,
        call
    ):
        if match.status != "scheduled":
            raise ValueError(
                "Toss can only be conducted for a scheduled match."
            )

        if calling_team not in {
            match.team1,
            match.team2
        }:
            raise ValueError(
                "Calling team must be one of the teams in the match."
            )

        if not calling_team.captain_id:
            raise ValueError(
                "Calling team must have a captain."
            )

        valid_calls = {
            "heads",
            "tails"
        }

        call = call.lower()

        if call not in valid_calls:
            raise ValueError(
                "Invalid toss call. Choose heads or tails."
            )

        toss_result = random.choice(
            ["heads", "tails"]
        )

        match.toss_call = call
        match.toss_result = toss_result

        if call == toss_result:
            match.toss_winner = calling_team
        else:
            if calling_team == match.team1:
                match.toss_winner = match.team2
            else:
                match.toss_winner = match.team1

        match.save(
            update_fields=[
                "toss_call",
                "toss_result",
                "toss_winner"
            ]
        )

        logger.info(
            "Toss conducted for match %s: call=%s result=%s winner=%s",
            match.match_id,
            call,
            toss_result,
            match.toss_winner_id
        )

        return match

    def set_toss_decision(
        self,
        match,
        decision
    ):
        if not match.toss_winner_id:
            raise ValueError(
                "Toss must be conducted before choosing a decision."
            )

        if match.toss_decision:
            raise ValueError(
                "Toss decision has already been made."
            )

        if not decision:
            raise ValueError(
                "Decision is required."
            )

        decision = decision.lower()

        valid_decisions = {
            "bat",
            "bowl"
        }

        if decision not in valid_decisions:
            raise ValueError(
                "Invalid toss decision. Choose bat or bowl."
            )

        toss_winner = match.toss_winner

        if toss_winner == match.team1:
            other_team = match.team2
        else:
            other_team = match.team1

        match.toss_decision = decision

        if decision == "bat":
            match.batting_team = toss_winner
            match.bowling_team = other_team
        else:
            match.batting_team = other_team
            match.bowling_team = toss_winner

        match.save(
            update_fields=[
                "toss_decision",
                "batting_team",
                "bowling_team"
            ]
        )

        logger.info(
            "Toss decision set for match %s: decision=%s batting_team=%s bowling_team=%s",
            match.match_id,
            decision,
            match.batting_team_id,
            match.bowling_team_id
        )

        return match

    def start_match(
        self,
        match
    ):
        if match.status == "completed":
            raise ValueError(
                "Completed match cannot be started again."
            )

        if match.status != "scheduled":
            raise ValueError(
                "Match can only be started from scheduled status."
            )

        if not match.toss_winner_id:
            raise ValueError(
                "Toss must be conducted before starting the match."
            )

        if not match.toss_decision:
            raise ValueError(
                "Toss decision must be made before starting the match."
            )

        if not match.batting_team_id or not match.bowling_team_id:
            raise ValueError(
                "Batting and bowling teams must be set before starting the match."
            )

        match.status = "live"

        match.save(
            update_fields=[
                "status"
            ]
        )

        logger.info(
            "Match %s started",
            match.match_id
        )

        return match

    def complete_match(
        self,
        match
    ):
        if match.status != "live":
            raise ValueError(
                "Only a live match can be completed."
            )

        match.status = "completed"

        match.save(
            update_fields=[
                "status"
            ]
        )

        logger.info(
            "Match %s completed",
            match.match_id
        )

        return match