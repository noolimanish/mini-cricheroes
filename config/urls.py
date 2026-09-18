from django.contrib import admin
from django.urls import path

from cricket.views import (
    PlayerListCreateView,
    PlayerDetailView,
    TeamListCreateView,
    TeamDetailView,
    MatchListCreateView,
    MatchDetailView,
    MatchTossView,
    MatchTossDecisionView,
    MatchInningsCreateView,
    OpeningBatsmenView,
    SetBowlerView,
    RecordBallView,
    RecordWicketView,
    ReplaceBatsmanView,
    MatchStartView,
    MatchCompleteView,
    MatchResultView,
    MatchScorecardView,
    RegisterView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    # Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Players
    path(
        "players/",
        PlayerListCreateView.as_view()
    ),

    path(
        "players/<str:player_id>/",
        PlayerDetailView.as_view()
    ),

    # Teams
    path(
        "teams/",
        TeamListCreateView.as_view()
    ),

    path(
        "teams/<str:team_id>/",
        TeamDetailView.as_view()
    ),

    # Matches
    path(
        "matches/",
        MatchListCreateView.as_view()
    ),

    path(
        "matches/<str:match_id>/",
        MatchDetailView.as_view()
    ),

    # Match lifecycle
    path(
        "matches/<str:match_id>/toss/",
        MatchTossView.as_view()
    ),

    path(
        "matches/<str:match_id>/toss/decision/",
        MatchTossDecisionView.as_view()
    ),

    path(
        "matches/<str:match_id>/start/",
        MatchStartView.as_view()
    ),

    path(
        "matches/<str:match_id>/complete/",
        MatchCompleteView.as_view()
    ),

    # Innings
    path(
        "matches/<str:match_id>/innings/",
        MatchInningsCreateView.as_view()
    ),

    path(
        "matches/<str:match_id>/innings/<int:innings_number>/opening-batsmen/",
        OpeningBatsmenView.as_view()
    ),

    path(
        "matches/<str:match_id>/innings/<int:innings_number>/bowler/",
        SetBowlerView.as_view()
    ),

    # Ball-by-ball
    path(
        "matches/<str:match_id>/innings/<int:innings_number>/balls/",
        RecordBallView.as_view()
    ),

    path(
        "matches/<str:match_id>/innings/<int:innings_number>/wicket/",
        RecordWicketView.as_view()
    ),

    path(
        "matches/<str:match_id>/innings/<int:innings_number>/replace-batsman/",
        ReplaceBatsmanView.as_view()
    ),

    # Result & scorecard
    path(
        "matches/<str:match_id>/result/",
        MatchResultView.as_view()
    ),

    path(
        "matches/<str:match_id>/scorecard/",
        MatchScorecardView.as_view()
    ),

    # Authentication
    path(
        "auth/register/",
        RegisterView.as_view()
    ),

    path(
        "auth/login/",
        TokenObtainPairView.as_view()
    ),

    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view()
    ),

    # API Documentation
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui"
    ),
]