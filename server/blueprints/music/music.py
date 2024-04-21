from flask import Blueprint, abort

from . import subsonic, logger
from .play import play as play_blueprint
from .search import search as search_blueprint

music = Blueprint("music", __name__)
music.register_blueprint(play_blueprint, url_prefix="/play")
music.register_blueprint(search_blueprint, url_prefix="/search")


@music.before_request
def before_request():
    try:
        logger.info("Attempting to connect to Subsonic server")
        if not subsonic.ping():
            logger.warn("Failed to connect to Subsonic server")
            return abort(500, "Failed to connect to Subsonic server")
        else:
            logger.info("Connected to Subsonic server")
    except Exception:  # noqa
        # We use a broad exception as there are a variety of Connection* errors that can be raised
        logger.warn("Failed to connect to Subsonic server")
        return abort(500, "Failed to connect to Subsonic server")


@music.route("/")
def index():
    return "Connected to Subsonic server"


@music.route("/now_playing")
def now_playing():
    logger.info("Attempting to get the current playing song")
    song = subsonic.get_now_playing()
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
