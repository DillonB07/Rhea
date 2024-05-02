import json
from pathlib import Path
from urllib.parse import urlencode

from flask import Blueprint, make_response, redirect, request

from utils.config import SPOTIFY_CONFIG
from utils.security import create_state_key
from utils.spotify import get_token

project_root = Path(__file__).parent.parent.parent.parent
data_file_path = project_root / "data.json"

spotify = Blueprint("spotify", __name__)
scopes = (
    "user-read-playback-state user-modify-playback-state user-read-currently-playing "
    "app-remote-control streaming playlist-read-private playlist-read-collaborative "
    "playlist-modify-private playlist-modify-public user-read-playback-position user-top-read "
    "user-read-recently-played user-library-modify user-library-read "
    "user-read-email user-read-private"
)


@spotify.route("/login", methods=["GET"])
def login():
    """
    Redirects the user to the Spotify login page. This must be called manually by the user.
    ---
    tags:
      - spotify
    responses:
        302:
            description: Redirects the user to the Spotify login page.
    """
    state = create_state_key(15)
    auth_url = "https://accounts.spotify.com/authorize?"
    params = {
        "client_id": SPOTIFY_CONFIG["clientId"],
        "response_type": "code",
        "redirect_uri": SPOTIFY_CONFIG["redirectUri"],
        "state": state,
        "scope": scopes,
    }
    query_params = urlencode(params)
    res = make_response(redirect(auth_url + query_params))
    with open(data_file_path, "r") as f:
        data = json.load(f)
        data["spotify"]["auth"]["state"] = state
    with open(data_file_path, "w") as f:
        f.write(json.dumps(data))
    return res


@spotify.route("/callback", methods=["GET"])
def callback():
    with open(data_file_path, "r") as f:
        data = json.load(f)
    if request.args.get("state") != data.get("spotify").get("auth").get("state"):
        return "Invalid state", 400
    elif request.args.get("error"):
        return request.args.get("error"), 400
    else:
        code = request.args.get("code")
        payload = get_token(code)
        if payload is not None:
            data["spotify"]["auth"]["token"] = payload[0]
            data["spotify"]["auth"]["refresh_token"] = payload[1]
            data["spotify"]["auth"]["token_expiration"] = payload[2]
            with open(data_file_path, "w") as f:
                f.write(json.dumps(data))
            return "Success"
        else:
            return "Failed to access token", 400
