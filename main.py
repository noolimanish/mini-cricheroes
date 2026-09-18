from backend.player import Player
from backend.player_registry import registry
from backend.team import Team
from backend.match import Match
from backend.innings import Innings

# ============================================================

# PLAYERS

# ============================================================

player1 = Player(
"Manish",
"[manish@example.com](mailto:manish@example.com)",
"All Rounder",
"Right-handed",
"seam",
"right-arm-fast"
)

player2 = Player(
"Rohit",
"[rohit@example.com](mailto:rohit@example.com)",
"Batsman",
"Left-handed",
"spin",
"left-arm-orthodox"
)

player3 = Player(
"Virat",
"[virat@example.com](mailto:virat@example.com)",
"Bowler",
"Right-handed",
"seam",
"right-arm-medium"
)

player4 = Player(
"Rahul",
"[rahul@example.com](mailto:rahul@example.com)",
"Batsman",
"Right-handed"
)

# ============================================================

# PLAYER REGISTRY

# ============================================================

registry.add_player("P101", player1)
registry.add_player("P102", player2)
registry.add_player("P103", player3)
registry.add_player("P104", player4)

print("Players:")
print(registry.players)

# ============================================================

# TEAM 1

# ============================================================

team1 = Team("Team 1", "T001")

team1.add_player("P101")
team1.add_player("P102")
team1.add_player("P104")

team1.set_captain("P101")

print("\nTeam 1:")
print("Players:", team1.player_ids)
print("Captain:", team1.captain_id)

# ============================================================

# TEAM 2

# ============================================================

team2 = Team("Team 2", "T002")

team2.add_player("P103")

print("\nTeam 2:")
print("Players:", team2.player_ids)

# ============================================================

# MATCH

# ============================================================

match1 = Match(
"M001",
team1,
team2,
"Uppal Ground",
"Tennis",
10,
"Scheduled"
)

# ============================================================

# TOSS

# ============================================================

result = match1.conduct_toss(
team1,
"heads"
)

print("\nToss:")
print("Call:", result[0])
print("Winner:", result[1].team_name)
print("Coin:", result[2])

# ============================================================

# TOSS DECISION

# ============================================================

batting_team, bowling_team = (
match1.choose_toss_decision("bat")
)

print("\nToss Decision:")
print(
"Toss Winner:",
match1.toss_winner.team_name
)

print(
"Decision:",
match1.toss_decision
)

print(
"Batting First:",
batting_team.team_name
)

print(
"Bowling First:",
bowling_team.team_name
)

# ============================================================

# FIRST INNINGS

# ============================================================

innings1 = Innings(
match1.batting_team,
match1.bowling_team,
match1.overs
)

# ============================================================

# OPENING BATSMEN

# ============================================================

innings1.set_opening_batsmen(
"P101",
"P102"
)

innings1.current_bowler_id = "P103"

print("\nInnings:")
print(
"Batting Team:",
innings1.batting_team.team_name
)

print(
"Bowling Team:",
innings1.bowling_team.team_name
)

print(
"Striker:",
innings1.striker_id
)

print(
"Non-striker:",
innings1.non_striker_id
)

print(
"Bowler:",
innings1.current_bowler_id
)

# ============================================================

# TEST NORMAL BALLS

# ============================================================

print("\n========== BALL TEST ==========")

innings1.record_ball(1)

print(
"After 1 run:",
innings1.total_runs,
innings1.overs_display
)

innings1.record_ball(4)

print(
"After 4 runs:",
innings1.total_runs,
innings1.overs_display
)

innings1.record_ball(2)

print(
"After 2 runs:",
innings1.total_runs,
innings1.overs_display
)

# ============================================================

# TEST EXTRAS

# ============================================================

print("\n========== EXTRA TESTS ==========")

# Wide

ball = innings1.record_ball(
runs=0,
extra_type="wide",
extra_runs=1
)

print("\nWide:")
print("Runs:", ball.runs)
print("Extras:", ball.extras)
print("Extra Type:", ball.extra_type)
print("Legal:", ball.is_legal)
print("Total Runs:", innings1.total_runs)
print("Overs:", innings1.overs_display)

# No-ball

ball = innings1.record_ball(
runs=0,
extra_type="no-ball",
extra_runs=1
)

print("\nNo-ball:")
print("Runs:", ball.runs)
print("Extras:", ball.extras)
print("Extra Type:", ball.extra_type)
print("Legal:", ball.is_legal)
print("Total Runs:", innings1.total_runs)
print("Overs:", innings1.overs_display)

# Bye

ball = innings1.record_ball(
runs=0,
extra_type="bye",
extra_runs=1
)

print("\nBye:")
print("Runs:", ball.runs)
print("Extras:", ball.extras)
print("Extra Type:", ball.extra_type)
print("Legal:", ball.is_legal)
print("Total Runs:", innings1.total_runs)
print("Overs:", innings1.overs_display)

# Leg-bye

ball = innings1.record_ball(
runs=0,
extra_type="leg-bye",
extra_runs=1
)

print("\nLeg-bye:")
print("Runs:", ball.runs)
print("Extras:", ball.extras)
print("Extra Type:", ball.extra_type)
print("Legal:", ball.is_legal)
print("Total Runs:", innings1.total_runs)
print("Overs:", innings1.overs_display)

# ============================================================

# WICKET TEST

# ============================================================

print("\n========== WICKET TEST ==========")

# Make P101 striker

innings1.striker_id = "P101"
innings1.non_striker_id = "P102"

print("\nBefore wicket:")
print("Striker:", innings1.striker_id)
print("Non-striker:", innings1.non_striker_id)
print("Wickets:", innings1.wickets_fallen)

# P101 gets bowled

ball = innings1.record_wicket(
"bowled"
)

print("\nWicket:")
print("Wicket:", ball.wicket)
print("Player Out:", ball.player_out_id)
print("Wicket Type:", ball.wicket_type)
print("Wickets:", innings1.wickets_fallen)
print("Batsmen Out:", innings1.batsmen_out)

# ============================================================

# NEW BATSMAN

# ============================================================

innings1.replace_batsman("P104")

print("\nAfter new batsman:")
print("Striker:", innings1.striker_id)
print("Non-striker:", innings1.non_striker_id)
print("Batsmen Used:", innings1.batsmen_used)
print("Batsmen Out:", innings1.batsmen_out)

# ============================================================

# CURRENT INNINGS STATUS

# ============================================================

print("\n========== CURRENT INNINGS STATUS ==========")

print(
"Batting Team:",
innings1.batting_team.team_name
)

print(
"Bowling Team:",
innings1.bowling_team.team_name
)

print(
"Total Runs:",
innings1.total_runs
)

print(
"Wickets:",
innings1.wickets_fallen
)

print(
"Overs:",
innings1.overs_display
)

print(
"Striker:",
innings1.striker_id
)

print(
"Non-striker:",
innings1.non_striker_id
)

# ============================================================

# BATSMAN STATS

# ============================================================

print("\n========== BATSMAN STATS ==========")

for player_id, stats in innings1.batsman_stats.items():

    
    print("\nPlayer:", player_id)
    print("Runs:", stats.runs)
    print("Balls:", stats.balls_faced)
    print("4s:", stats.fours)
    print("6s:", stats.sixes)
    print(
        "Strike Rate:",
        round(stats.strike_rate, 2)
    )
    print("Out:", stats.is_out)


# ============================================================

# BOWLER STATS

# ============================================================

print("\n========== BOWLER STATS ==========")

for player_id, stats in innings1.bowler_stats.items():


    print("\nBowler:", player_id)
    print("Runs Conceded:", stats.runs_conceded)
    print("Balls:", stats.balls_bowled)
    print("Overs:", stats.overs)
    print("Wickets:", stats.wickets)
    print("Wides:", stats.wides)
    print("No-balls:", stats.no_balls)
    print("Economy:", round(stats.economy, 2))

