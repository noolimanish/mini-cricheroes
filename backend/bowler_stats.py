class BowlerStats:

    def __init__(self, player_id):
        self.player_id = player_id

        self.balls_bowled = 0
        self.runs_conceded = 0
        self.wickets = 0

        self.wides = 0
        self.no_balls = 0

    # -------------------------
    # Record ball
    # -------------------------

    def record_ball(self, runs_conceded, legal=True):

        if runs_conceded < 0:
            raise ValueError(
                "Runs conceded cannot be negative."
            )

        self.runs_conceded += runs_conceded

        if legal:
            self.balls_bowled += 1

    # -------------------------
    # Wicket
    # -------------------------

    def record_wicket(self):

        self.wickets += 1

    # -------------------------
    # Wide
    # -------------------------

    def record_wide(self):

        self.wides += 1

    # -------------------------
    # No-ball
    # -------------------------

    def record_no_ball(self):

        self.no_balls += 1

    # -------------------------
    # Overs
    # -------------------------

    @property
    def overs(self):

        completed = self.balls_bowled // 6
        balls = self.balls_bowled % 6

        return f"{completed}.{balls}"

    # -------------------------
    # Economy
    # -------------------------

    @property
    def economy(self):

        if self.balls_bowled == 0:
            return 0.0

        overs = self.balls_bowled / 6

        return self.runs_conceded / overs