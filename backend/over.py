class Over:

    def __init__(self, over_number, bowler_id):

        self.over_number = over_number
        self.bowler_id = bowler_id

        self.balls = []

        self.total_runs = 0
        self.wickets = 0
        self.legal_balls = 0

    def add_ball(self, ball):

        # An over can contain more than 6 deliveries
        # because wides/no-balls are not legal balls.
        if self.legal_balls >= 6:
            raise ValueError(
                "This over already has 6 legal balls."
            )

        self.balls.append(ball)

        self.total_runs += (
            ball.runs + ball.extras
        )

        if ball.is_legal:
            self.legal_balls += 1

        if ball.wicket:
            self.wickets += 1