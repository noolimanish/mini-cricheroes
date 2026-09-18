class Ball:

    VALID_EXTRA_TYPES = {
        "wide",
        "no-ball",
        "bye",
        "leg-bye"
    }

    VALID_WICKET_TYPES = {
        "bowled",
        "caught",
        "lbw",
        "run-out",
        "stumped",
        "hit-wicket"
    }

    def __init__(
        self,
        ball_number,
        striker_id,
        non_striker_id,
        bowler_id
    ):
        self.ball_number = ball_number

        self.striker_id = striker_id
        self.non_striker_id = non_striker_id
        self.bowler_id = bowler_id

        # Batting runs
        self.runs = 0

        # Extra runs
        self.extras = 0
        self.extra_type = None

        # Legal delivery
        self.is_legal = True

        # Wicket information
        self.wicket = False
        self.wicket_type = None
        self.player_out_id = None

    def set_extra(self, extra_type, extra_runs=1):

        extra_type = extra_type.lower()

        if extra_type not in self.VALID_EXTRA_TYPES:
            raise ValueError(
                f"Invalid extra type. Choose from {self.VALID_EXTRA_TYPES}."
            )

        if extra_runs < 0:
            raise ValueError("Extra runs cannot be negative.")

        self.extra_type = extra_type
        self.extras = extra_runs

        # Wide and no-ball are NOT legal deliveries
        if extra_type in {"wide", "no-ball"}:
            self.is_legal = False

        return self

    def set_wicket(self, player_out_id, wicket_type):

        wicket_type = wicket_type.lower()

        if wicket_type not in self.VALID_WICKET_TYPES:
            raise ValueError(
                f"Invalid wicket type. Choose from {self.VALID_WICKET_TYPES}."
            )

        self.wicket = True
        self.wicket_type = wicket_type
        self.player_out_id = player_out_id

        return self