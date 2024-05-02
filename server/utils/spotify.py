import base64
import json
import time
from pathlib import Path

import requests

from blueprints.api.spotify import logger
from utils.config import SPOTIFY_CONFIG

project_root = Path(__file__).parent.parent
data_file_path = project_root / "data.json"

byte_clients = (
    SPOTIFY_CONFIG["clientId"] + ":" + SPOTIFY_CONFIG["clientSecret"]
).encode("utf-8")
encoded_clients = base64.b64encode(byte_clients).decode("utf-8")
authorization = f"Basic {encoded_clients}"


def get_token(code):
    token_url = "https://accounts.spotify.com/api/token"
    redirect_uri = SPOTIFY_CONFIG["redirectUri"]

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    post_response = requests.post(token_url, headers=headers, data=body)

    if post_response.status_code == 200:
        res = post_response.json()
        return res["access_token"], res["refresh_token"], res["expires_in"]
    else:
        logger.error(f"get_token: {post_response.status_code}, {post_response.json()}")
        return None


def check_token_status():
    with open(data_file_path, "r") as f:
        data = json.load(f)
        auth = data.get("spotify").get("auth")
    payload = None
    if time.time() > auth.get("token_expiration"):
        payload = refresh_token(auth.get("refresh_token"))
    if payload is not None:
        auth["token"] = payload[0]
        auth["token_expiration"] = time.time() + payload[1]
        data["spotify"]["auth"] = auth
        with open(data_file_path, "w") as f:
            f.write(json.dumps(data))
    else:
        logger.error("Error checking token status")
        return None
    return "Success"


def refresh_token(refresh_token):
    token_url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": authorization,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = {"refresh_token": refresh_token, "grant_type": "refresh_token"}
    post_response = requests.post(token_url, headers=headers, data=body)

    # 200 code indicates access token was properly granted
    if post_response.status_code == 200:
        return post_response.json()["access_token"], post_response.json()["expires_in"]
    else:
        logger.error(f"Attempted to refresh token: post_response.status_code")
        return None


def get(url, params={}):
    with open(data_file_path, "r") as f:
        data = json.load(f)
        auth = data.get("spotify").get("auth")
    headers = {"Authorization": "Bearer {}".format(auth.get("token"))}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401 and check_token_status() is not None:
        return get(url, params)
    else:
        logger.error(f"Error getting {url} {response.status_code}")
        return None
