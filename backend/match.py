import random


class Match:
    VALID_BALL_TYPES = {"tennis", "leather"}
    VALID_TOSS_DECISIONS = {"bat", "bowl"}
    VALID_STATUSES = {"scheduled", "live", "completed"}

    def __init__(
        self,
        match_id,
        team1,
        team2,
        ground,
        ball_type,
        overs,
        status
    ):
        ball_type = ball_type.lower()
        status = status.lower()

        # Validation
        if ball_type not in self.VALID_BALL_TYPES:
            raise ValueError(
                f"Invalid ball type. Choose from {self.VALID_BALL_TYPES}."
            )

        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid match status. Choose from {self.VALID_STATUSES}."
            )

        if overs <= 0:
            raise ValueError("Overs must be greater than 0.")

        # Store match data
        self.match_id = match_id
        self.team1 = team1
        self.team2 = team2
        self.ground = ground
        self.ball_type = ball_type
        self.overs = overs
        self.status = status

        # Toss data - not known yet
        self.toss_call = None
        self.toss_result = None
        self.toss_winner = None
        self.toss_decision = None
        self.batting_team = None
        self.bowling_team = None
        

    def conduct_toss(self, calling_team, call):
        call = call.lower()

        if calling_team not in [self.team1, self.team2]:
            raise ValueError(
                "Calling team must be one of the participating teams."
            )

        if calling_team.captain_id is None:
            raise ValueError(
                "Calling team must have a captain to make the toss call."
            )

        if call not in ["heads", "tails"]:
            raise ValueError(
                "Toss call must be either 'heads' or 'tails'."
            )

        self.toss_call = call
        self.toss_result = random.choice(["heads", "tails"])

        if self.toss_call == self.toss_result:
            self.toss_winner = calling_team
        else:
            self.toss_winner = (
                self.team1
                if calling_team == self.team2
                else self.team2
            )

        return self.toss_call, self.toss_winner, self.toss_result
    
    def choose_toss_decision(self, decision):
        decision = decision.lower()

        if self.toss_winner is None:
            raise ValueError("Toss has not been conducted yet.")

        if decision not in self.VALID_TOSS_DECISIONS:
            raise ValueError(
                f"Invalid toss decision. Choose from {self.VALID_TOSS_DECISIONS}."
            )

        self.toss_decision = decision
        
        if decision == "bat":
            self.batting_team = self.toss_winner
            self.bowling_team = (self.team1 if self.toss_winner == self.team2 else self.team2)
        else:
            self.bowling_team=self.toss_winner
            self.batting_team=(self.team2 if self.toss_winner == self.team1 else self.team1)
            
        return self.batting_team, self.bowling_team
    
    