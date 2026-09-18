class BatsmanStats:

    def __init__(self, player_id):
        self.player_id = player_id

        self.runs = 0
        self.balls_faced = 0
        self.fours = 0
        self.sixes = 0

        self.is_out = False
        self.dismissal_type = None

    # ========================================================
    # STRIKE RATE
    # ========================================================

    @property
    def strike_rate(self):
        if self.balls_faced == 0:
            return 0.0

        return (self.runs / self.balls_faced) * 100

    # ========================================================
    # RECORD BATTING RUNS
    # ========================================================

    def record_runs(self, runs):
        if runs < 0:
            raise ValueError(
                "Runs cannot be negative."
            )

        self.runs += runs
        self.balls_faced += 1

        if runs == 4:
            self.fours += 1

        elif runs == 6:
            self.sixes += 1

    # ========================================================
    # RECORD DISMISSAL
    # ========================================================

    def record_out(self, dismissal_type):
        self.is_out = True
        self.dismissal_type = dismissal_type