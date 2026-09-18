from django.db import models


class Player(models.Model):
    player_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=20)
    batting_style = models.CharField(max_length=50)
    bowling_type = models.CharField(max_length=20, null=True, blank=True)
    bowling_style = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    team_id = models.CharField(max_length=20, primary_key=True)
    team_name = models.CharField(max_length=100)

    players = models.ManyToManyField(
        Player,
        related_name="teams"
    )

    captain = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="captained_teams"
    )

    def __str__(self):
        return self.team_name


class Match(models.Model):
    VALID_BALL_TYPES = {"tennis", "leather"}
    VALID_STATUSES = {"scheduled", "live", "completed"}

    match_id = models.CharField(max_length=20, primary_key=True)

    team1 = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="matches_as_team1"
    )

    team2 = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="matches_as_team2"
    )

    ground = models.CharField(max_length=200)
    ball_type = models.CharField(max_length=20)
    overs = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        default="scheduled"
    )

    toss_call = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    toss_result = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    toss_winner = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="toss_wins"
    )

    toss_decision = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    batting_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="matches_batting"
    )

    bowling_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="matches_bowling"
    )
    
    winner = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="matches_won"
    )

    result_type = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    result_margin = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.match_id


class Innings(models.Model):
    innings_number = models.PositiveIntegerField()

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="innings"
    )

    batting_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="innings_batting"
    )

    bowling_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="innings_bowling"
    )

    overs = models.PositiveIntegerField()
    current_over = models.PositiveIntegerField(default=0)
    balls_bowled = models.PositiveIntegerField(default=0)
    total_runs = models.PositiveIntegerField(default=0)
    wickets_fallen = models.PositiveIntegerField(default=0)

    striker = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="innings_as_striker"
    )

    non_striker = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="innings_as_non_striker"
    )

    current_bowler = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="innings_as_bowler"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["match", "innings_number"],
                name="unique_innings_per_match"
            )
        ]

    def __str__(self):
        return f"{self.match.match_id} - Innings {self.innings_number}"


class Over(models.Model):
    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="overs_data"
    )

    over_number = models.PositiveIntegerField()

    bowler = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="overs_bowled"
    )

    total_runs = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    legal_balls = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["innings", "over_number"],
                name="unique_over_per_innings"
            )
        ]

    def __str__(self):
        return f"{self.innings} - Over {self.over_number}"


class Ball(models.Model):
    over = models.ForeignKey(
        Over,
        on_delete=models.CASCADE,
        related_name="balls"
    )

    ball_number = models.PositiveIntegerField()

    striker = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="balls_faced"
    )

    non_striker = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="balls_as_non_striker"
    )

    bowler = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="balls_bowled"
    )

    runs = models.PositiveIntegerField(default=0)
    extras = models.PositiveIntegerField(default=0)

    extra_type = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    is_legal = models.BooleanField(default=True)
    wicket = models.BooleanField(default=False)

    wicket_type = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    player_out = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="dismissals"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["over", "ball_number"],
                name="unique_ball_per_over"
            )
        ]

    def __str__(self):
        return f"{self.over} - Ball {self.ball_number}"


class BatsmanStats(models.Model):
    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="batsman_stats"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="batsman_stats"
    )

    runs = models.PositiveIntegerField(default=0)
    balls_faced = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)

    is_out = models.BooleanField(default=False)

    dismissal_type = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["innings", "player"],
                name="unique_batsman_stats_per_innings"
            )
        ]

    def __str__(self):
        return f"{self.player.name} - {self.innings} - Batting"


class BowlerStats(models.Model):
    innings = models.ForeignKey(
        Innings,
        on_delete=models.CASCADE,
        related_name="bowler_stats"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="bowler_stats"
    )

    balls_bowled = models.PositiveIntegerField(default=0)
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    wides = models.PositiveIntegerField(default=0)
    no_balls = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["innings", "player"],
                name="unique_bowler_stats_per_innings"
            )
        ]

    def __str__(self):
        return f"{self.player.name} - {self.innings} - Bowling"