class Wicket:
    VALID_TYPES = {
        "bowled",
        "caught",
        "lbw",
        "run-out",
        "stumped",
        "hit-wicket"
    }

    def __init__(self, player_out_id, wicket_type, fielder_id=None):
        wicket_type = wicket_type.lower()

        if wicket_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid wicket type. Choose from {self.VALID_TYPES}."
            )

        self.player_out_id = player_out_id
        self.wicket_type = wicket_type
        self.fielder_id = fielder_id