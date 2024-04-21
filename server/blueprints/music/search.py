from flask import Blueprint, abort

from . import logger, subsonic

search = Blueprint("search", __name__)


@search.route("/song/<string:query>")
def search_song(query: str):
    logger.info(f"Attempting to search for {query}")
    songs = subsonic.search_song(query, single=False)
    if songs is None:
        logger.warn(f"Failed to search for {query}")
        return abort(
            404, "The song you are looking for could not be found on the server."
        )
    return {
        "songs": [
            {
                "title": song.title,
                "artist": song.artist,
                "album": song.album,
                "track": song.track,
                "cover": song.cover,
                "duration": song.duration,
                "genre": song.genre,
                "year": song.year,
                "id": song.id,
            }
            for song in songs[:50]
        ]
    }
