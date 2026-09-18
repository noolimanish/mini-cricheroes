class TeamRegistry:

    def __init__(self):
        self.teams = {}

    def add_team(self, team_id, team):
        if team_id in self.teams:
            raise ValueError(
                f"Team with ID {team_id} already exists."
            )

        self.teams[team_id] = team


registry = TeamRegistry()