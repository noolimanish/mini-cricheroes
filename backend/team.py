from backend.player_registry import registry
class Team:
    def __init__(
        self,
        team_name,
        team_id,
        player_ids=None,
        captain_id=None
    ):
        self.team_name = team_name
        self.team_id = team_id
        self.player_ids = player_ids or []
        self.captain_id = captain_id
        self.playing_xi = []

    def add_player(self, player_id):
        if player_id in registry.players:
            if player_id not in self.player_ids:
                self.player_ids.append(player_id)
            else:
                raise ValueError(
                    f"Player with ID {player_id} is already in the team."
                )
        else:
            raise ValueError(
                f"Player with ID {player_id} is not in the player registry."
            )

    def set_captain(self, player_id):
        if player_id not in self.player_ids:
            raise ValueError(
                "Captain must be a member of the team."
            )

        self.captain_id = player_id

    def set_playing_xi(self, player_ids):
        if len(player_ids) != 11:
            raise ValueError(
                "Playing XI must contain exactly 11 players."
            )

        if len(set(player_ids)) != 11:
            raise ValueError(
                "Playing XI cannot contain duplicate players."
            )

        for player_id in player_ids:
            if player_id not in self.player_ids:
                raise ValueError(
                    f"Player {player_id} is not a member of the team."
                )

        self.playing_xi = player_ids.copy()