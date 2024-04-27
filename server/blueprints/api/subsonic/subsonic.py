from flask import Blueprint, abort

from . import subsonic as subsonic_client, logger
from .play import play as play_blueprint
from .search import search as search_blueprint

subsonic = Blueprint("subsonic", __name__)
subsonic.register_blueprint(play_blueprint, url_prefix="/play")
subsonic.register_blueprint(search_blueprint, url_prefix="/search")


@subsonic.before_request
def before_request():
    """
    Checks if the Subsonic server is reachable before each request
    ---
    tags:
     - subsonic
    responses:
      503:
        description: Failed to connect to Subsonic server
    """
    try:
        logger.info("Attempting to connect to Subsonic server")
        if not subsonic_client.ping():
            logger.warn("Failed to connect to Subsonic server")
            return abort(500, "Failed to connect to Subsonic server")
        else:
            logger.info("Connected to Subsonic server")
    except Exception:  # noqa
        # We use a broad exception as there are a variety of Connection* errors that can be raised
        logger.warn("Failed to connect to Subsonic server")
        return abort(503, "Failed to connect to Subsonic server")


@subsonic.route("/", methods=["GET"])
def index():
    """
    Checks if the Subsonic server is reachable
    ---
    tags:
     - subsonic
    responses:
      200:
        description: Connected to Subsonic server
      503:
        description: Failed to connect to Subsonic server
    """
    return "Connected to Subsonic server"


@subsonic.route("/now_playing", methods=["GET"])
def now_playing():
    """
    Gets the current playing song
    ---
    tags:
     - subsonic
    responses:
        200:
            description: The current playing song
            content:
            application/json:
                schema:
                type: object
                properties:
                    title:
                    type: string
                    artist:
                    type: string
                    album:
                    type: string
                    track:
                    type: string
                    cover:
                    type: string
                    duration:
                    type: integer
                    genre:
                    type: string
                    year:
                    type: string
        404:
            description: No song is currently playing
    """
    logger.info("Attempting to get the current playing song")
    song = subsonic_client.get_now_playing()
    if song is None:
        logger.warn("Failed to get the current playing song")
        return abort(404, "No song is currently playing")
    logger.info(f"Now playing {song.title} | {song.artist} | {song.album}")
    return {
        "title": song.title,
        "artist": song.artist,
        "album": song.album,
        "track": song.track,
        "cover": song.cover,
        "duration": song.duration,
        "genre": song.genre,
        "year": song.year,
    }
