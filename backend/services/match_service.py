from backend.match import Match


class MatchService:

    def create_match(
        self,
        match_id,
        team1,
        team2,
        ground,
        ball_type,
        overs,
        status="scheduled"
    ):
        return Match(
            match_id,
            team1,
            team2,
            ground,
            ball_type,
            overs,
            status
        )

    def conduct_toss(self, match, calling_team, call):

        return match.conduct_toss(
            calling_team,
            call
        )

    def choose_toss_decision(self, match, decision):

        return match.choose_toss_decision(
            decision
        )