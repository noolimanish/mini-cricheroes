from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from cricket.models import (
    Player,
    Team,
    Match,
    Innings,
    Ball,
    BatsmanStats,
    BowlerStats,
)


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = [
            "player_id",
            "name",
            "email",
            "role",
            "batting_style",
            "bowling_type",
            "bowling_style",
        ]


class TeamSerializer(serializers.ModelSerializer):

    players = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Player.objects.all()
    )

    captain = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Team
        fields = [
            "team_id",
            "team_name",
            "players",
            "captain",
        ]

    def validate(self, data):

        if "players" in data:
            players = set(data["players"])
        elif self.instance:
            players = set(
                self.instance.players.all()
            )
        else:
            players = set()

        captain = data.get(
            "captain",
            getattr(self.instance, "captain", None)
        )

        if captain is not None and captain not in players:
            raise serializers.ValidationError(
                "Captain must be a member of the team."
            )

        return data


class MatchSerializer(serializers.ModelSerializer):

    team1 = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all()
    )

    team2 = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all()
    )

    class Meta:
        model = Match
        fields = [
            "match_id",
            "team1",
            "team2",
            "ground",
            "ball_type",
            "overs",
            "status",
            "toss_call",
            "toss_result",
            "toss_winner",
            "toss_decision",
            "batting_team",
            "bowling_team",
            "winner",
            "result_type",
            "result_margin",
        ]

        read_only_fields = [
            "status",
            "toss_call",
            "toss_result",
            "toss_winner",
            "toss_decision",
            "batting_team",
            "bowling_team",
            "winner",
            "result_type",
            "result_margin",
        ]

    def validate(self, data):

        team1 = data.get(
            "team1",
            getattr(self.instance, "team1", None)
        )

        team2 = data.get(
            "team2",
            getattr(self.instance, "team2", None)
        )

        if team1 == team2:
            raise serializers.ValidationError(
                "A match must have two different teams."
            )

        return data

    def validate_ball_type(self, value):

        if value not in {"tennis", "leather"}:
            raise serializers.ValidationError(
                "ball_type must be either tennis or leather."
            )

        return value

    def validate_overs(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "overs must be a positive integer."
            )

        return value


class InningsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Innings
        fields = [
            "id",
            "innings_number",
            "match",
            "batting_team",
            "bowling_team",
            "overs",
            "current_over",
            "balls_bowled",
            "total_runs",
            "wickets_fallen",
            "striker",
            "non_striker",
            "current_bowler",
        ]

        read_only_fields = [
            "id",
            "innings_number",
            "match",
            "batting_team",
            "bowling_team",
            "current_over",
            "balls_bowled",
            "total_runs",
            "wickets_fallen",
            "striker",
            "non_striker",
            "current_bowler",
        ]


class BallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ball
        fields = [
            "id",
            "over",
            "ball_number",
            "striker",
            "non_striker",
            "bowler",
            "runs",
            "extras",
            "extra_type",
            "is_legal",
            "wicket",
            "wicket_type",
            "player_out",
        ]

        read_only_fields = fields


class ScorecardBallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ball
        fields = [
            "id",
            "ball_number",
            "striker",
            "non_striker",
            "bowler",
            "runs",
            "extras",
            "extra_type",
            "is_legal",
            "wicket",
            "wicket_type",
            "player_out",
        ]


class BatsmanScorecardSerializer(serializers.ModelSerializer):

    strike_rate = serializers.SerializerMethodField()

    class Meta:
        model = BatsmanStats
        fields = [
            "player",
            "runs",
            "balls_faced",
            "fours",
            "sixes",
            "strike_rate",
            "is_out",
            "dismissal_type",
        ]

    @extend_schema_field(serializers.FloatField())
    def get_strike_rate(self, batsman):

        if batsman.balls_faced == 0:
            return 0.0

        return round(
            (
                batsman.runs
                / batsman.balls_faced
            ) * 100,
            2
        )


class BowlerScorecardSerializer(serializers.ModelSerializer):

    overs = serializers.SerializerMethodField()
    economy = serializers.SerializerMethodField()

    class Meta:
        model = BowlerStats
        fields = [
            "player",
            "overs",
            "balls_bowled",
            "runs_conceded",
            "wickets",
            "wides",
            "no_balls",
            "economy",
        ]

    @extend_schema_field(serializers.CharField())
    def get_overs(self, bowler):

        completed_overs = bowler.balls_bowled // 6
        remaining_balls = bowler.balls_bowled % 6

        return f"{completed_overs}.{remaining_balls}"

    @extend_schema_field(serializers.FloatField())
    def get_economy(self, bowler):

        if bowler.balls_bowled == 0:
            return 0.0

        economy = (
            bowler.runs_conceded * 6
        ) / bowler.balls_bowled

        return round(economy, 2)


class ScorecardInningsSerializer(serializers.ModelSerializer):

    score = serializers.SerializerMethodField()
    overs_completed = serializers.SerializerMethodField()
    run_rate = serializers.SerializerMethodField()

    balls = serializers.SerializerMethodField()
    batting_stats = serializers.SerializerMethodField()
    bowling_stats = serializers.SerializerMethodField()

    class Meta:
        model = Innings
        fields = [
            "id",
            "innings_number",
            "batting_team",
            "bowling_team",
            "overs",
            "current_over",
            "balls_bowled",
            "total_runs",
            "wickets_fallen",
            "score",
            "overs_completed",
            "run_rate",
            "striker",
            "non_striker",
            "current_bowler",
            "batting_stats",
            "bowling_stats",
            "balls",
        ]

    @extend_schema_field(serializers.CharField())
    def get_score(self, innings):

        return (
            f"{innings.total_runs}/"
            f"{innings.wickets_fallen}"
        )

    @extend_schema_field(serializers.CharField())
    def get_overs_completed(self, innings):

        completed_overs = innings.balls_bowled // 6
        remaining_balls = innings.balls_bowled % 6

        return f"{completed_overs}.{remaining_balls}"

    @extend_schema_field(serializers.FloatField())
    def get_run_rate(self, innings):

        if innings.balls_bowled == 0:
            return 0.0

        run_rate = (
            innings.total_runs * 6
        ) / innings.balls_bowled

        return round(run_rate, 2)

    @extend_schema_field(
        ScorecardBallSerializer(many=True)
    )
    def get_balls(self, innings):

        balls = Ball.objects.filter(
            over__innings=innings
        ).order_by(
            "over__over_number",
            "ball_number"
        )

        return ScorecardBallSerializer(
            balls,
            many=True
        ).data

    @extend_schema_field(
        BatsmanScorecardSerializer(many=True)
    )
    def get_batting_stats(self, innings):

        stats = BatsmanStats.objects.filter(
            innings=innings
        ).select_related(
            "player"
        ).order_by(
            "id"
        )

        return BatsmanScorecardSerializer(
            stats,
            many=True
        ).data

    @extend_schema_field(
        BowlerScorecardSerializer(many=True)
    )
    def get_bowling_stats(self, innings):

        stats = BowlerStats.objects.filter(
            innings=innings
        ).select_related(
            "player"
        ).order_by(
            "id"
        )

        return BowlerScorecardSerializer(
            stats,
            many=True
        ).data


class ScorecardSerializer(serializers.ModelSerializer):

    innings = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "match_id",
            "team1",
            "team2",
            "ground",
            "ball_type",
            "overs",
            "status",
            "winner",
            "result_type",
            "result_margin",
            "result",
            "innings",
        ]

    @extend_schema_field(
        serializers.CharField(allow_null=True)
    )
    def get_result(self, match):

        if match.status != "completed":
            return None

        if match.result_type == "tie":
            return "Match tied"

        if not match.winner:
            return None

        if match.result_type == "runs":

            return (
                f"{match.winner.team_name} "
                f"won by {match.result_margin} runs"
            )

        if match.result_type == "wickets":

            return (
                f"{match.winner.team_name} "
                f"won by {match.result_margin} wickets"
            )

        return None

    @extend_schema_field(
        ScorecardInningsSerializer(many=True)
    )
    def get_innings(self, match):

        innings = match.innings.order_by(
            "innings_number"
        )

        return ScorecardInningsSerializer(
            innings,
            many=True
        ).data