from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from cricket.models import Player, Team, Match, Innings
from cricket.services.match_service import MatchService
from cricket.services.innings_service import InningsService
from cricket.services.match_result_service import MatchResultService
from cricket.serializers_auth import RegisterSerializer
from cricket.serializers import (
    PlayerSerializer,
    TeamSerializer,
    MatchSerializer,
    InningsSerializer,
    BallSerializer,
    ScorecardSerializer,
)


# -------------------------------------------------------------------
# Swagger request serializers
# -------------------------------------------------------------------

class TossRequestSerializer(serializers.Serializer):
    calling_team = serializers.CharField()
    call = serializers.ChoiceField(
        choices=["heads", "tails"]
    )


class TossDecisionRequestSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(
        choices=["bat", "bowl"]
    )


class InningsCreateRequestSerializer(serializers.Serializer):
    overs = serializers.IntegerField(min_value=1)


class OpeningBatsmenRequestSerializer(serializers.Serializer):
    striker_id = serializers.CharField()
    non_striker_id = serializers.CharField()


class BowlerRequestSerializer(serializers.Serializer):
    bowler_id = serializers.CharField()


class BallRequestSerializer(serializers.Serializer):
    runs = serializers.IntegerField(
        min_value=0,
        required=False,
        default=0
    )
    extra_type = serializers.CharField(
        required=False,
        allow_null=True
    )
    extra_runs = serializers.IntegerField(
        min_value=0,
        required=False,
        default=0
    )


class WicketRequestSerializer(serializers.Serializer):
    wicket_type = serializers.CharField()
    player_out_id = serializers.CharField()
    runs = serializers.IntegerField(
        min_value=0,
        required=False,
        default=0
    )


class ReplaceBatsmanRequestSerializer(serializers.Serializer):
    new_batsman_id = serializers.CharField()


# -------------------------------------------------------------------
# Players
# -------------------------------------------------------------------

class PlayerListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]

        return []

    @extend_schema(
        operation_id="players_list",
        responses=PlayerSerializer(many=True),
    )
    def get(self, request):
        players = Player.objects.all()

        serializer = PlayerSerializer(
            players,
            many=True
        )

        return Response(
            serializer.data
        )

    @extend_schema(
        operation_id="players_create",
        request=PlayerSerializer,
        responses={
            201: PlayerSerializer,
            400: OpenApiResponse(
                description="Validation error."
            ),
        },
    )
    def post(self, request):
        serializer = PlayerSerializer(
            data=request.data
        )

        if serializer.is_valid():
            player = serializer.save()

            return Response(
                PlayerSerializer(player).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PlayerDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]

        return []

    def get_player(self, player_id):
        try:
            return Player.objects.get(
                player_id=player_id
            )
        except Player.DoesNotExist:
            return None

    @extend_schema(
        operation_id="players_retrieve",
        responses={
            200: PlayerSerializer,
            404: OpenApiResponse(
                description="Player not found."
            ),
        },
    )
    def get(self, request, player_id):
        player = self.get_player(player_id)

        if player is None:
            return Response(
                {"error": "Player not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlayerSerializer(player)

        return Response(
            serializer.data
        )

    @extend_schema(
        operation_id="players_update",
        request=PlayerSerializer,
        responses={
            200: PlayerSerializer,
            400: OpenApiResponse(
                description="Validation error."
            ),
            404: OpenApiResponse(
                description="Player not found."
            ),
        },
    )
    def put(self, request, player_id):
        player = self.get_player(player_id)

        if player is None:
            return Response(
                {"error": "Player not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PlayerSerializer(
            player,
            data=request.data
        )

        if serializer.is_valid():
            player = serializer.save()

            return Response(
                PlayerSerializer(player).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        operation_id="players_delete",
        responses={
            204: OpenApiResponse(
                description="Player deleted successfully."
            ),
            404: OpenApiResponse(
                description="Player not found."
            ),
        },
    )
    def delete(self, request, player_id):
        player = self.get_player(player_id)

        if player is None:
            return Response(
                {"error": "Player not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        player.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# -------------------------------------------------------------------
# Teams
# -------------------------------------------------------------------

class TeamListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]

        return []

    @extend_schema(
        operation_id="teams_list",
        responses=TeamSerializer(many=True),
    )
    def get(self, request):
        teams = Team.objects.all()

        serializer = TeamSerializer(
            teams,
            many=True
        )

        return Response(
            serializer.data
        )

    @extend_schema(
        operation_id="teams_create",
        request=TeamSerializer,
        responses={
            201: TeamSerializer,
            400: OpenApiResponse(
                description="Validation error."
            ),
        },
    )
    def post(self, request):
        serializer = TeamSerializer(
            data=request.data
        )

        if serializer.is_valid():
            team = serializer.save()

            return Response(
                TeamSerializer(team).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TeamDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]

        return []

    def get_team(self, team_id):
        try:
            return Team.objects.get(
                team_id=team_id
            )
        except Team.DoesNotExist:
            return None

    @extend_schema(
        operation_id="teams_retrieve",
        responses={
            200: TeamSerializer,
            404: OpenApiResponse(
                description="Team not found."
            ),
        },
    )
    def get(self, request, team_id):
        team = self.get_team(team_id)

        if team is None:
            return Response(
                {"error": "Team not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeamSerializer(team)

        return Response(
            serializer.data
        )

    @extend_schema(
        operation_id="teams_update",
        request=TeamSerializer,
        responses={
            200: TeamSerializer,
            400: OpenApiResponse(
                description="Validation error."
            ),
            404: OpenApiResponse(
                description="Team not found."
            ),
        },
    )
    def put(self, request, team_id):
        team = self.get_team(team_id)

        if team is None:
            return Response(
                {"error": "Team not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeamSerializer(
            team,
            data=request.data
        )

        if serializer.is_valid():
            team = serializer.save()

            return Response(
                TeamSerializer(team).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        operation_id="teams_delete",
        responses={
            204: OpenApiResponse(
                description="Team deleted successfully."
            ),
            404: OpenApiResponse(
                description="Team not found."
            ),
        },
    )
    def delete(self, request, team_id):
        team = self.get_team(team_id)

        if team is None:
            return Response(
                {"error": "Team not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        team.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# -------------------------------------------------------------------
# Matches
# -------------------------------------------------------------------

class MatchListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]

        return []

    @extend_schema(
        operation_id="matches_list",
        responses=MatchSerializer(many=True),
    )
    def get(self, request):
        matches = Match.objects.all()

        serializer = MatchSerializer(
            matches,
            many=True
        )

        return Response(
            serializer.data
        )

    @extend_schema(
        operation_id="matches_create",
        request=MatchSerializer,
        responses={
            201: MatchSerializer,
            400: OpenApiResponse(
                description="Validation error."
            ),
        },
    )
    def post(self, request):
        serializer = MatchSerializer(
            data=request.data
        )

        if serializer.is_valid():
            match = serializer.save()

            return Response(
                MatchSerializer(match).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MatchDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]

        return []

    def get_match(self, match_id):
        try:
            return Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return None

    @extend_schema(
        operation_id="matches_retrieve",
        responses={
            200: MatchSerializer,
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def get(self, request, match_id):
        match = self.get_match(match_id)

        if match is None:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MatchSerializer(match)

        return Response(
            serializer.data
        )

    @extend_schema(
        operation_id="matches_update",
        request=MatchSerializer,
        responses={
            200: MatchSerializer,
            400: OpenApiResponse(
                description="Validation error."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def put(self, request, match_id):
        match = self.get_match(match_id)

        if match is None:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MatchSerializer(
            match,
            data=request.data
        )

        if serializer.is_valid():
            match = serializer.save()

            return Response(
                MatchSerializer(match).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        operation_id="matches_delete",
        responses={
            204: OpenApiResponse(
                description="Match deleted successfully."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def delete(self, request, match_id):
        match = self.get_match(match_id)

        if match is None:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        match.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


# -------------------------------------------------------------------
# Toss
# -------------------------------------------------------------------

class MatchTossView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="matches_toss",
        request=TossRequestSerializer,
        responses={
            200: MatchSerializer,
            400: OpenApiResponse(
                description="Invalid toss request."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def post(self, request, match_id):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        calling_team_id = request.data.get(
            "calling_team"
        )

        call = request.data.get(
            "call"
        )

        if not calling_team_id or not call:
            return Response(
                {
                    "error": (
                        "calling_team and call are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            calling_team = Team.objects.get(
                team_id=calling_team_id
            )
        except Team.DoesNotExist:
            return Response(
                {"error": "Calling team not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            match = MatchService().conduct_toss(
                match,
                calling_team,
                call
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_200_OK
        )


class MatchTossDecisionView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="matches_toss_decision",
        request=TossDecisionRequestSerializer,
        responses={
            200: MatchSerializer,
            400: OpenApiResponse(
                description="Invalid toss decision."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def post(self, request, match_id):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        decision = request.data.get(
            "decision"
        )

        if not decision:
            return Response(
                {"error": "Decision is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            match = MatchService().set_toss_decision(
                match,
                decision
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_200_OK
        )


# -------------------------------------------------------------------
# Innings
# -------------------------------------------------------------------

class MatchInningsCreateView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="matches_innings_create",
        request=InningsCreateRequestSerializer,
        responses={
            201: InningsSerializer,
            400: OpenApiResponse(
                description="Invalid innings request."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def post(self, request, match_id):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        overs = request.data.get("overs")

        if overs is None:
            return Response(
                {"error": "Overs is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            overs = int(overs)
        except (TypeError, ValueError):
            return Response(
                {"error": "Overs must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            innings = InningsService().create_next_innings(
                match=match,
                overs=overs
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            InningsSerializer(innings).data,
            status=status.HTTP_201_CREATED
        )


class OpeningBatsmenView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="innings_opening_batsmen",
        request=OpeningBatsmenRequestSerializer,
        responses={
            200: InningsSerializer,
            400: OpenApiResponse(
                description="Invalid opening batsmen."
            ),
            404: OpenApiResponse(
                description="Match or innings not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id,
        innings_number
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            innings = Innings.objects.get(
                match=match,
                innings_number=innings_number
            )
        except Innings.DoesNotExist:
            return Response(
                {"error": "Innings not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        striker_id = request.data.get("striker_id")
        non_striker_id = request.data.get("non_striker_id")

        if not striker_id or not non_striker_id:
            return Response(
                {
                    "error": (
                        "striker_id and non_striker_id "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            innings = InningsService().set_opening_batsmen(
                innings,
                striker_id,
                non_striker_id
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            InningsSerializer(innings).data,
            status=status.HTTP_200_OK
        )


class SetBowlerView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="innings_set_bowler",
        request=BowlerRequestSerializer,
        responses={
            200: InningsSerializer,
            400: OpenApiResponse(
                description="Invalid bowler."
            ),
            404: OpenApiResponse(
                description="Match or innings not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id,
        innings_number
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            innings = Innings.objects.get(
                match=match,
                innings_number=innings_number
            )
        except Innings.DoesNotExist:
            return Response(
                {"error": "Innings not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        bowler_id = request.data.get("bowler_id")

        if not bowler_id:
            return Response(
                {"error": "bowler_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            innings = InningsService().set_bowler(
                innings,
                bowler_id
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            InningsSerializer(innings).data,
            status=status.HTTP_200_OK
        )


# -------------------------------------------------------------------
# Ball-by-ball
# -------------------------------------------------------------------

class RecordBallView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="innings_record_ball",
        request=BallRequestSerializer,
        responses={
            201: BallSerializer,
            400: OpenApiResponse(
                description="Invalid ball data."
            ),
            404: OpenApiResponse(
                description="Match or innings not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id,
        innings_number
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            innings = Innings.objects.get(
                match=match,
                innings_number=innings_number
            )
        except Innings.DoesNotExist:
            return Response(
                {"error": "Innings not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        runs = request.data.get("runs", 0)
        extra_type = request.data.get("extra_type")
        extra_runs = request.data.get("extra_runs", 0)

        try:
            runs = int(runs)
            extra_runs = int(extra_runs)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": (
                        "runs and extra_runs must be integers."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if runs < 0:
            return Response(
                {"error": "Runs cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if extra_runs < 0:
            return Response(
                {"error": "Extra runs cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ball = InningsService().record_ball(
                innings=innings,
                runs=runs,
                extra_type=extra_type,
                extra_runs=extra_runs
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            BallSerializer(ball).data,
            status=status.HTTP_201_CREATED
        )


class RecordWicketView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="innings_record_wicket",
        request=WicketRequestSerializer,
        responses={
            201: BallSerializer,
            400: OpenApiResponse(
                description="Invalid wicket data."
            ),
            404: OpenApiResponse(
                description="Match or innings not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id,
        innings_number
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            innings = Innings.objects.get(
                match=match,
                innings_number=innings_number
            )
        except Innings.DoesNotExist:
            return Response(
                {"error": "Innings not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        wicket_type = request.data.get("wicket_type")
        player_out_id = request.data.get("player_out_id")
        runs = request.data.get("runs", 0)

        if not wicket_type or not player_out_id:
            return Response(
                {
                    "error": (
                        "wicket_type and player_out_id "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            runs = int(runs)
        except (TypeError, ValueError):
            return Response(
                {"error": "runs must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if runs < 0:
            return Response(
                {"error": "Runs cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ball = InningsService().record_wicket(
                innings=innings,
                wicket_type=wicket_type,
                player_out_id=player_out_id,
                runs=runs
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            BallSerializer(ball).data,
            status=status.HTTP_201_CREATED
        )


class ReplaceBatsmanView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="innings_replace_batsman",
        request=ReplaceBatsmanRequestSerializer,
        responses={
            200: InningsSerializer,
            400: OpenApiResponse(
                description="Invalid replacement batsman."
            ),
            404: OpenApiResponse(
                description="Match or innings not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id,
        innings_number
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            innings = Innings.objects.get(
                match=match,
                innings_number=innings_number
            )
        except Innings.DoesNotExist:
            return Response(
                {"error": "Innings not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_batsman_id = request.data.get(
            "new_batsman_id"
        )

        if not new_batsman_id:
            return Response(
                {"error": "new_batsman_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            innings = InningsService().replace_batsman(
                innings=innings,
                new_batsman_id=new_batsman_id
            )
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            InningsSerializer(innings).data,
            status=status.HTTP_200_OK
        )


# -------------------------------------------------------------------
# Match lifecycle
# -------------------------------------------------------------------

class MatchStartView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="matches_start",
        request=None,
        responses={
            200: MatchSerializer,
            400: OpenApiResponse(
                description="Match cannot be started."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )

            MatchService().start_match(match)

            return Response(
                MatchSerializer(match).data,
                status=status.HTTP_200_OK
            )

        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MatchCompleteView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="matches_complete",
        request=None,
        responses={
            200: MatchSerializer,
            400: OpenApiResponse(
                description="Match cannot be completed."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def post(
        self,
        request,
        match_id
    ):

        try:
            match = Match.objects.get(
                match_id=match_id
            )

            MatchService().complete_match(match)

            return Response(
                MatchSerializer(match).data,
                status=status.HTTP_200_OK
            )

        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MatchResultView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="matches_result",
        request=None,
        responses={
            200: MatchSerializer,
            400: OpenApiResponse(
                description="Unable to calculate match result."
            ),
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def post(self, request, match_id):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            match = MatchResultService().calculate_result(
                match
            )
        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            MatchSerializer(match).data,
            status=status.HTTP_200_OK
        )


# -------------------------------------------------------------------
# Scorecard
# -------------------------------------------------------------------

class MatchScorecardView(APIView):

    @extend_schema(
        operation_id="matches_scorecard",
        responses={
            200: ScorecardSerializer,
            404: OpenApiResponse(
                description="Match not found."
            ),
        },
    )
    def get(self, request, match_id):

        try:
            match = Match.objects.get(
                match_id=match_id
            )
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ScorecardSerializer(match)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# -------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------

class RegisterView(APIView):

    @extend_schema(
        operation_id="auth_register",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User registered successfully."
            ),
            400: OpenApiResponse(
                description="Registration validation error."
            ),
        },
    )
    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully.",
                    "username": user.username,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )