from backend.ball import Ball
from backend.over import Over
from backend.batsman_stats import BatsmanStats
from backend.bowler_stats import BowlerStats

class Innings:

    def __init__(self, batting_team, bowling_team, overs):

        self.batting_team = batting_team
        self.bowling_team = bowling_team
        self.overs = overs

        # -------------------------
        # Match progress
        # -------------------------

        self.current_over = 0
        self.balls_bowled = 0

        # -------------------------
        # Score
        # -------------------------

        self.total_runs = 0
        self.wickets_fallen = 0

        # -------------------------
        # Current players
        # -------------------------

        self.striker_id = None
        self.non_striker_id = None
        self.current_bowler_id = None

        # -------------------------
        # Ball / over data
        # -------------------------

        self.balls = []
        self.overs_data = []

        # -------------------------
        # Batsman tracking
        # -------------------------

        self.batsmen_used = []
        self.batsmen_out = []

        self.batsman_stats = {}
        self.bowler_stats = {}

    # ========================================================
    # OPENING BATSMEN
    # ========================================================

    def set_opening_batsmen(self, striker_id, non_striker_id):

        if striker_id == non_striker_id:
            raise ValueError(
                "Striker and non-striker cannot be the same player."
            )

        if striker_id not in self.batting_team.player_ids:
            raise ValueError(
                f"{striker_id} is not part of the batting team."
            )

        if non_striker_id not in self.batting_team.player_ids:
            raise ValueError(
                f"{non_striker_id} is not part of the batting team."
            )

        self.striker_id = striker_id
        self.non_striker_id = non_striker_id

        if striker_id not in self.batsmen_used:
            self.batsmen_used.append(striker_id)

        if non_striker_id not in self.batsmen_used:
            self.batsmen_used.append(non_striker_id)

        self._create_batsman_stats(striker_id)
        self._create_batsman_stats(non_striker_id)

    # ========================================================
    # BATSMAN STATS
    # ========================================================

    def _create_batsman_stats(self, player_id):

        if player_id not in self.batsman_stats:
            self.batsman_stats[player_id] = BatsmanStats(
                player_id
            )

    # ========================================================
    # BOWLER STATS
    # ========================================================

    def get_bowler_stats(self, bowler_id):

        if bowler_id not in self.bowler_stats:
            self.bowler_stats[bowler_id] = BowlerStats(
                bowler_id
            )

        return self.bowler_stats[bowler_id]

    # ========================================================
    # CREATE OVER
    # ========================================================

    def create_over(self):

        if self.current_over >= self.overs:
            raise ValueError(
                "All overs have been completed."
            )

        if self.current_bowler_id is None:
            raise ValueError(
                "Bowler has not been set."
            )

        over = Over(
            self.current_over + 1,
            self.current_bowler_id
        )

        self.overs_data.append(over)
        self.current_over += 1

        return over

    # ========================================================
    # GET CURRENT OVER
    # ========================================================

    def get_current_over(self):

        if not self.overs_data:
            return self.create_over()

        current_over = self.overs_data[-1]

        # If the previous over is complete, create a new over.
        # Strike was already changed when the sixth legal ball
        # was recorded, so do not change it again here.
        if current_over.legal_balls >= 6:
            return self.create_over()

        return current_over

    # ========================================================
    # ADD BALL
    # ========================================================

    def add_ball(self, ball):

        # Maximum legal deliveries
        if self.balls_bowled >= self.overs * 6:
            raise ValueError(
                "All overs have been bowled."
            )

        # Store ball
        self.balls.append(ball)

        # Add team runs
        self.total_runs += (
            ball.runs + ball.extras
        )

        # Only legal deliveries count
        if ball.is_legal:
            self.balls_bowled += 1

        # Wicket
        if ball.wicket:
            self.wickets_fallen += 1

    # ========================================================
    # RECORD NORMAL BALL / EXTRA
    # ========================================================

    def record_ball(
        self,
        runs=0,
        extra_type=None,
        extra_runs=0
    ):

        # -------------------------
        # Validation
        # -------------------------

        if self.striker_id is None:
            raise ValueError(
                "Striker has not been set."
            )

        if self.non_striker_id is None:
            raise ValueError(
                "Non-striker has not been set."
            )

        if self.current_bowler_id is None:
            raise ValueError(
                "Bowler has not been set."
            )

        if runs < 0:
            raise ValueError(
                "Runs cannot be negative."
            )

        if extra_runs < 0:
            raise ValueError(
                "Extra runs cannot be negative."
            )

        # -------------------------
        # Get current over
        # -------------------------

        current_over = self.get_current_over()

        # -------------------------
        # Ball number
        # -------------------------

        ball_number = len(current_over.balls) + 1

        # -------------------------
        # Create Ball
        # -------------------------

        ball = Ball(
            ball_number,
            self.striker_id,
            self.non_striker_id,
            self.current_bowler_id
        )

        ball.runs = runs

        # -------------------------
        # Extras
        # -------------------------

        if extra_type is not None:
            ball.set_extra(
                extra_type,
                extra_runs
            )

        # -------------------------
        # Batsman stats
        # -------------------------

        self._create_batsman_stats(
            self.striker_id
        )

        batsman = self.batsman_stats[
            self.striker_id
        ]

        if extra_type is None:

            # Normal legal delivery
            batsman.record_runs(runs)

        elif extra_type == "no-ball":

            # No-ball is not counted as a ball faced.
            # Runs scored from the bat count to the batsman.
            if runs > 0:

                batsman.runs += runs

                if runs == 4:
                    batsman.fours += 1

                elif runs == 6:
                    batsman.sixes += 1

        # Wide, bye and leg-bye do not add runs
        # to the batsman's personal score.

        # -------------------------
        # Bowler stats
        # -------------------------

        bowler = self.get_bowler_stats(
            self.current_bowler_id
        )

        runs_conceded = ball.runs

        if ball.extra_type in {
            "wide",
            "no-ball"
        }:
            runs_conceded += ball.extras

        elif ball.extra_type in {
            "bye",
            "leg-bye"
        }:
            runs_conceded += 0

        bowler.record_ball(
            runs_conceded,
            legal=ball.is_legal
        )

        if ball.extra_type == "wide":
            bowler.record_wide()

        elif ball.extra_type == "no-ball":
            bowler.record_no_ball()

        # -------------------------
        # Add ball to over
        # -------------------------

        current_over.add_ball(ball)

        # -------------------------
        # Add ball to innings
        # -------------------------

        self.add_ball(ball)

        # -------------------------
        # Strike rotation
        # -------------------------

        if extra_type is None:

            if runs % 2 == 1:
                self.striker_id, self.non_striker_id = (
                    self.non_striker_id,
                    self.striker_id
                )

        elif extra_type in {
            "bye",
            "leg-bye"
        }:

            if extra_runs % 2 == 1:
                self.striker_id, self.non_striker_id = (
                    self.non_striker_id,
                    self.striker_id
                )

        # -------------------------
        # End of over
        # -------------------------

        # Change ends immediately after the sixth legal ball.
        # get_current_over() will create the next over later
        # without performing another strike swap.
        if current_over.legal_balls >= 6:

            self.striker_id, self.non_striker_id = (
                self.non_striker_id,
                self.striker_id
            )

        return ball

    # ========================================================
    # RECORD WICKET
    # ========================================================

    def record_wicket(
        self,
        wicket_type,
        runs=0
    ):

        if self.striker_id is None:
            raise ValueError(
                "Striker has not been set."
            )

        if self.non_striker_id is None:
            raise ValueError(
                "Non-striker has not been set."
            )

        if self.current_bowler_id is None:
            raise ValueError(
                "Bowler has not been set."
            )

        if runs < 0:
            raise ValueError(
                "Runs cannot be negative."
            )

        # -------------------------
        # Get current over
        # -------------------------

        current_over = self.get_current_over()

        # -------------------------
        # Player getting out
        # -------------------------

        player_out_id = self.striker_id

        # -------------------------
        # Ball
        # -------------------------

        ball_number = len(
            current_over.balls
        ) + 1

        ball = Ball(
            ball_number,
            self.striker_id,
            self.non_striker_id,
            self.current_bowler_id
        )

        ball.runs = runs

        ball.set_wicket(
            player_out_id,
            wicket_type
        )

        # Wicket ball is legal
        ball.is_legal = True

        # -------------------------
        # Batsman stats
        # -------------------------

        self._create_batsman_stats(
            player_out_id
        )

        batsman = self.batsman_stats[
            player_out_id
        ]

        batsman.record_runs(runs)
        batsman.record_out(wicket_type)

        # -------------------------
        # Bowler stats
        # -------------------------

        bowler = self.get_bowler_stats(
            self.current_bowler_id
        )

        bowler.record_ball(
            runs,
            legal=True
        )

        # Run-outs are not credited to the bowler.
        if wicket_type.lower() != "run-out":
            bowler.record_wicket()

        # -------------------------
        # Add ball
        # -------------------------

        current_over.add_ball(ball)

        self.add_ball(ball)

        # -------------------------
        # Track dismissed player
        # -------------------------

        if player_out_id not in self.batsmen_out:

            self.batsmen_out.append(
                player_out_id
            )

        # -------------------------
        # End of over
        # -------------------------

        if current_over.legal_balls >= 6:

            self.striker_id, self.non_striker_id = (
                self.non_striker_id,
                self.striker_id
            )

        return ball

    # ========================================================
    # REPLACE BATSMAN
    # ========================================================

    def replace_batsman(self, new_batsman_id):

        if new_batsman_id not in self.batting_team.player_ids:

            raise ValueError(
                f"{new_batsman_id} is not part of the batting team."
            )

        if new_batsman_id in self.batsmen_used:

            raise ValueError(
                f"{new_batsman_id} has already batted."
            )

        if not self.batsmen_out:

            raise ValueError(
                "No batsman is waiting to be replaced."
            )

        dismissed_player = self.batsmen_out[-1]

        # Replace striker
        if self.striker_id == dismissed_player:

            self.striker_id = new_batsman_id

        # Replace non-striker
        elif self.non_striker_id == dismissed_player:

            self.non_striker_id = new_batsman_id

        else:

            raise ValueError(
                "Dismissed player is not currently at the crease."
            )

        self.batsmen_used.append(
            new_batsman_id
        )

        self._create_batsman_stats(
            new_batsman_id
        )

        return new_batsman_id

    # ========================================================
    # OVERS DISPLAY
    # ========================================================

    @property
    def overs_display(self):

        completed_overs = (
            self.balls_bowled // 6
        )

        balls_in_current_over = (
            self.balls_bowled % 6
        )

        return (
            f"{completed_overs}."
            f"{balls_in_current_over}"
        )

    # ========================================================
    # OVERS COMPLETED
    # ========================================================

    @property
    def overs_completed(self):

        return self.balls_bowled // 6

    # ========================================================
    # CURRENT OVER
    # ========================================================

    @property
    def current_over_data(self):

        if not self.overs_data:
            return None

        return self.overs_data[-1]

