from flask import Blueprint, abort, request

from . import logger, subsonic

search = Blueprint("search", __name__)


@search.route("/")
def search_query():
    query = request.args.get("query")
    type = request.args.get("type", "all")
    if query is None:
        return abort(400, "No query provided")
    logger.info(f"Attempting to search for {query}")
    match type:
        case "song":
            songs = subsonic.search_song(query, single=False)
            if songs is None:
                logger.warn(f"Failed to search for {query}")
                return abort(
                    404,
                    "The song you are looking for could not be found on the server.",
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
                    for song in songs
                ]
            }
        case "album":
            albums = subsonic.search_album(query)
            if albums is None:
                logger.warn(f"Failed to search for {query}")
                return abort(
                    404,
                    "The album you are looking for could not be found on the server.",
                )
            return {
                "albums": [
                    {
                        "title": album.title,
                        "artist": album.artist,
                        "cover": album.cover,
                        "id": album.id,
                    }
                    for album in albums
                ]
            }

        case "artists":
            artists = subsonic.search_artist(query)
            if artists is None:
                logger.warn(f"Failed to search for {query}")
                return abort(
                    404,
                    "The artist you are looking for could not be found on the server.",
                )
            return {
                "artists": [
                    {
                        "name": artist.name,
                        "id": artist.id,
                        "albums": artist.albums,
                    }
                    for artist in artists
                ]
            }
        case _:
            songs = subsonic.search_song(query, single=False)
            albums = subsonic.search_album(query, single=False)
            artists = subsonic.search_artist(query)
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
                    for song in songs
                ],
                "albums": [
                    {
                        "title": album.title,
                        "artist": album.artist,
                        "cover": album.cover,
                        "id": album.id,
                    }
                    for album in albums
                ],
                "artists": [
                    {
                        "name": artist.name,
                        "id": artist.id,
                        "albums": artist.albums,
                    }
                    for artist in artists
                ],
            }


@search.route("/artist/<string:id>")
def get_artist(id: str):
    logger.info(f"Attempting to get artist with id {id}")
    artist = subsonic.get_artist(id)
    if artist is None:
        logger.warn(f"Failed to get artist with id {id}")
        return abort(
            404, "The artist you are looking for could not be found on the server."
        )

    return {
        "name": artist.name,
        "id": artist.id,
        "albums": [
            {
                "title": album.title,
                "cover": album.cover,
                "id": album.id,
            }
            for album in artist.albums
        ],
    }
