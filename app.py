from flask import Flask, jsonify, request

from backend.services.match_service import MatchService
from backend.team_registry import registry as team_registry
from backend.services.innings_service import InningsService


app = Flask(__name__)

match_service = MatchService()

matches = {}
innings_service = InningsService()


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/matches", methods=["POST"])
def create_match():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON."
        }), 400

    required_fields = [
        "match_id",
        "team1_id",
        "team2_id",
        "ground",
        "ball_type",
        "overs"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields.",
            "fields": missing_fields
        }), 400

    try:
        team1 = team_registry.teams[data["team1_id"]]
        team2 = team_registry.teams[data["team2_id"]]

        match = match_service.create_match(
            match_id=data["match_id"],
            team1=team1,
            team2=team2,
            ground=data["ground"],
            ball_type=data["ball_type"],
            overs=data["overs"],
            status=data.get("status", "scheduled")
        )

        matches[match.match_id] = match

        return jsonify({
            "message": "Match created successfully.",
            "match": {
                "match_id": match.match_id,
                "team1_id": match.team1.team_id,
                "team2_id": match.team2.team_id,
                "ground": match.ground,
                "ball_type": match.ball_type,
                "overs": match.overs,
                "status": match.status
            }
        }), 201

    except KeyError as error:
        return jsonify({
            "error": f"Team with ID {error.args[0]} not found."
        }), 404

    except (ValueError, TypeError) as error:
        return jsonify({
            "error": str(error)
        }), 400


@app.route("/matches/<match_id>", methods=["GET"])
def get_match(match_id):
    match = matches.get(match_id)

    if not match:
        return jsonify({
            "error": f"Match with ID {match_id} not found."
        }), 404

    return jsonify({
        "match_id": match.match_id,
        "team1_id": match.team1.team_id,
        "team2_id": match.team2.team_id,
        "ground": match.ground,
        "ball_type": match.ball_type,
        "overs": match.overs,
        "status": match.status
    }), 200


@app.route("/matches/<match_id>/toss", methods=["POST"])
def conduct_toss(match_id):
    match = matches.get(match_id)

    if match is None:
        return jsonify({
            "error": f"Match with ID {match_id} not found."
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON."
        }), 400

    required_fields = ["calling_team_id", "call"]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields.",
            "fields": missing_fields
        }), 400

    try:
        calling_team = team_registry.teams[data["calling_team_id"]]

        toss_call, toss_winner, toss_result = (
            match_service.conduct_toss(
                match,
                calling_team,
                data["call"]
            )
        )

        return jsonify({
            "message": "Toss conducted successfully.",
            "toss": {
                "call": toss_call,
                "result": toss_result,
                "winner_team_id": toss_winner.team_id
            }
        }), 200

    except KeyError as error:
        return jsonify({
            "error": f"Team with ID {error.args[0]} not found."
        }), 404

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


@app.route("/matches/<match_id>/toss/decision", methods=["POST"])
def choose_toss_decision(match_id):
    match = matches.get(match_id)

    if match is None:
        return jsonify({
            "error": f"Match with ID {match_id} not found."
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON."
        }), 400

    if "decision" not in data:
        return jsonify({
            "error": "Missing required fields.",
            "fields": ["decision"]
        }), 400

    try:
        batting_team, bowling_team = match_service.choose_toss_decision(
            match,
            data["decision"]
        )

        return jsonify({
            "message": "Toss decision recorded successfully.",
            "decision": data["decision"].lower(),
            "batting_team_id": batting_team.team_id,
            "bowling_team_id": bowling_team.team_id
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


@app.route("/matches/<match_id>/innings", methods=["POST"])
def create_innings(match_id):
    match = matches.get(match_id)

    if match is None:
        return jsonify({
            "error": f"Match with ID {match_id} not found."
        }), 404

    if match.toss_winner is None:
        return jsonify({
            "error": "Toss has not been conducted yet."
        }), 400

    if match.toss_decision is None:
        return jsonify({
            "error": "Toss decision has not been made yet."
        }), 400

    try:
        innings = innings_service.create_innings(
            batting_team=match.batting_team,
            bowling_team=match.bowling_team,
            overs=match.overs
        )

        if not hasattr(match, "innings"):
            match.innings = []

        match.innings.append(innings)

        return jsonify({
            "message": "Innings created successfully.",
            "innings": {
                "batting_team_id": innings.batting_team.team_id,
                "bowling_team_id": innings.bowling_team.team_id,
                "overs": innings.overs,
                "current_over": innings.current_over,
                "total_runs": innings.total_runs
            }
        }), 201

    except (ValueError, TypeError) as error:
        return jsonify({
            "error": str(error)
        }), 400


@app.route(
    "/matches/<match_id>/innings/<int:innings_index>/opening-batsmen",
    methods=["POST"]
)
def set_opening_batsmen(match_id, innings_index):
    match = matches.get(match_id)

    if match is None:
        return jsonify({
            "error": f"Match with ID {match_id} not found."
        }), 404

    if not hasattr(match, "innings") or innings_index >= len(match.innings):
        return jsonify({
            "error": f"Innings with index {innings_index} not found."
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON."
        }), 400

    required_fields = [
        "striker_id",
        "non_striker_id"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields.",
            "fields": missing_fields
        }), 400

    try:
        innings = match.innings[innings_index]

        innings_service.set_opening_batsmen(
            innings,
            data["striker_id"],
            data["non_striker_id"]
        )

        return jsonify({
            "message": "Opening batsmen set successfully.",
            "opening_batsmen": {
                "striker_id": innings.striker_id,
                "non_striker_id": innings.non_striker_id
            }
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


@app.route(
    "/matches/<match_id>/innings/<int:innings_index>/bowler",
    methods=["POST"]
)
def set_bowler(match_id, innings_index):
    match = matches.get(match_id)

    if match is None:
        return jsonify({
            "error": f"Match with ID {match_id} not found."
        }), 404

    if not hasattr(match, "innings") or innings_index >= len(match.innings):
        return jsonify({
            "error": f"Innings with index {innings_index} not found."
        }), 404

    data = request.get_json()

    # None means there was no JSON body at all.
    # An empty JSON object {} is valid JSON and should reach
    # the required-field validation below.
    if data is None:
        return jsonify({
            "error": "Request body must contain JSON."
        }), 400

    if "bowler_id" not in data:
        return jsonify({
            "error": "Missing required fields.",
            "fields": ["bowler_id"]
        }), 400

    try:
        innings = match.innings[innings_index]

        innings_service.set_bowler(
            innings,
            data["bowler_id"]
        )

        return jsonify({
            "message": "Bowler set successfully.",
            "bowler_id": innings.current_bowler_id
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


if __name__ == "__main__":
    app.run(debug=True)