import pytest

from app import app
from backend.team import Team
from backend.team_registry import registry as team_registry


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_team_registry():
    team_registry.teams.clear()


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_match(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    response = client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Match created successfully."

    assert data["match"]["match_id"] == "M001"
    assert data["match"]["team1_id"] == "IND"
    assert data["match"]["team2_id"] == "AUS"
    assert data["match"]["ground"] == "Hyderabad"
    assert data["match"]["ball_type"] == "leather"
    assert data["match"]["overs"] == 20
    assert data["match"]["status"] == "scheduled"


def test_create_match_missing_field(client):
    response = client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing required fields."


def test_create_match_unknown_team(client):
    response = client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_get_match(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.get("/matches/M001")

    assert response.status_code == 200

    data = response.get_json()

    assert data["match_id"] == "M001"
    assert data["team1_id"] == "IND"
    assert data["team2_id"] == "AUS"
    assert data["ground"] == "Hyderabad"
    assert data["ball_type"] == "leather"
    assert data["overs"] == 20
    assert data["status"] == "scheduled"


def test_conduct_toss(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.player_ids = ["P1", "P2"]
    team2.player_ids = ["P3", "P4"]

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    create_response = client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    assert create_response.status_code == 201

    response = client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Toss conducted successfully."
    assert data["toss"]["call"] == "heads"
    assert data["toss"]["result"] in ["heads", "tails"]
    assert data["toss"]["winner_team_id"] in ["IND", "AUS"]


def test_conduct_toss_unknown_match(client):
    response = client.post(
        "/matches/UNKNOWN/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Match with ID UNKNOWN not found."


def test_conduct_toss_unknown_team(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "XYZ",
            "call": "heads"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_conduct_toss_invalid_call(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "invalid"
        }
    )

    assert response.status_code == 400
    assert "Toss call must be either" in response.get_json()["error"]


def test_conduct_toss_without_captain(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Calling team must have a captain to make the toss call."
    )


def test_choose_toss_decision(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    toss_response = client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    assert toss_response.status_code == 200

    match = __import__("app").matches["M001"]

    toss_winner_id = match.toss_winner.team_id

    response = client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Toss decision recorded successfully."
    assert data["decision"] == "bat"
    assert data["batting_team_id"] == toss_winner_id
    assert data["bowling_team_id"] in ["IND", "AUS"]
    assert data["bowling_team_id"] != data["batting_team_id"]


def test_choose_toss_decision_unknown_match(client):
    response = client.post(
        "/matches/UNKNOWN/toss/decision",
        json={
            "decision": "bat"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Match with ID UNKNOWN not found."


def test_choose_toss_decision_missing_field(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.post(
        "/matches/M001/toss/decision",
        json={
            "wrong_field": "bat"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Missing required fields."
    assert data["fields"] == ["decision"]


def test_choose_toss_decision_before_toss(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Toss has not been conducted yet."
    )


def test_choose_toss_decision_invalid(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    response = client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "invalid"
        }
    )

    assert response.status_code == 400

    assert "Invalid toss decision" in response.get_json()["error"]


def test_create_innings(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    response = client.post(
        "/matches/M001/innings"
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Innings created successfully."

    match = __import__("app").matches["M001"]

    assert data["innings"]["batting_team_id"] == (
        match.batting_team.team_id
    )

    assert data["innings"]["bowling_team_id"] == (
        match.bowling_team.team_id
    )

    assert data["innings"]["overs"] == 20
    assert data["innings"]["current_over"] == 0
    assert data["innings"]["total_runs"] == 0


def test_create_innings_unknown_match(client):
    response = client.post(
        "/matches/UNKNOWN/innings"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Match with ID UNKNOWN not found."


def test_create_innings_before_toss(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    response = client.post(
        "/matches/M001/innings"
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Toss has not been conducted yet."
    )


def test_create_innings_before_toss_decision(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    response = client.post(
        "/matches/M001/innings"
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Toss decision has not been made yet."
    )


def test_set_opening_batsmen(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    # India players
    team1.player_ids = ["P1", "P2"]

    # Australia players
    team2.player_ids = ["P3", "P4"]

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    client.post(
        "/matches/M001/innings"
    )

    match = __import__("app").matches["M001"]
    batting_player_ids = match.batting_team.player_ids

    response = client.post(
        "/matches/M001/innings/0/opening-batsmen",
        json={
            "striker_id": batting_player_ids[0],
            "non_striker_id": batting_player_ids[1]
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == (
        "Opening batsmen set successfully."
    )


def test_set_opening_batsmen_unknown_match(client):
    response = client.post(
        "/matches/UNKNOWN/innings/0/opening-batsmen",
        json={
            "striker_id": "P1",
            "non_striker_id": "P2"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Match with ID UNKNOWN not found."


def test_set_opening_batsmen_missing_field(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.player_ids = ["P1", "P2"]
    team2.player_ids = ["P3", "P4"]

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    client.post(
        "/matches/M001/innings"
    )

    response = client.post(
        "/matches/M001/innings/0/opening-batsmen",
        json={
            "striker_id": "P1"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "Missing required fields."
    )


def test_set_bowler(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    # India players
    team1.player_ids = ["P1", "P2"]

    # Australia players
    team2.player_ids = ["P3", "P4"]

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    client.post(
        "/matches/M001/innings"
    )
    
    response = client.post(
    "/matches/M001/innings/0/bowler",
        json={
            "bowler_id": "P3"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == (
        "Bowler set successfully."
    )


def test_set_bowler_unknown_match(client):
    response = client.post(
        "/matches/UNKNOWN/innings/0/bowler",
        json={
            "bowler_id": "P3"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Match with ID UNKNOWN not found."


def test_set_bowler_missing_field(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.player_ids = ["P1", "P2"]
    team2.player_ids = ["P3", "P4"]

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    client.post(
        "/matches/M001/innings"
    )

    response = client.post(
        "/matches/M001/innings/0/bowler",
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "Missing required fields."
    )


def test_set_bowler_invalid_bowler(client):
    team1 = Team(
        team_name="India",
        team_id="IND"
    )

    team2 = Team(
        team_name="Australia",
        team_id="AUS"
    )

    team1.player_ids = ["P1", "P2"]
    team2.player_ids = ["P3", "P4"]

    team1.captain_id = "P1"
    team2.captain_id = "P3"

    team_registry.add_team("IND", team1)
    team_registry.add_team("AUS", team2)

    client.post(
        "/matches",
        json={
            "match_id": "M001",
            "team1_id": "IND",
            "team2_id": "AUS",
            "ground": "Hyderabad",
            "ball_type": "leather",
            "overs": 20
        }
    )

    client.post(
        "/matches/M001/toss",
        json={
            "calling_team_id": "IND",
            "call": "heads"
        }
    )

    client.post(
        "/matches/M001/toss/decision",
        json={
            "decision": "bat"
        }
    )

    client.post(
        "/matches/M001/innings"
    )

    response = client.post(
        "/matches/M001/innings/0/bowler",
        json={
            "bowler_id": "P999"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "P999 is not part of the bowling team."