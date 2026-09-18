class PlayerRegistry:
    def __init__(self):
        self.players = {}
    def add_player(self, playerid, player):
        if playerid in self.players:
            raise ValueError(f"Player with ID {playerid} already exists.")
        self.players[playerid] = player
        
registry = PlayerRegistry()