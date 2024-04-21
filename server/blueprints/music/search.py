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
            for song in songs
        ]
    }


@search.route("/album/<string:query>")
def search_album(query: str):
    logger.info(f"Attempting to search for {query}")
    albums = subsonic.search_album(query)
    if albums is None:
        logger.warn(f"Failed to search for {query}")
        return abort(
            404, "The album you are looking for could not be found on the server."
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


@search.route("/artists/<string:query>")
def search_artists(query: str):
    logger.info(f"Attempting to search for {query}")
    artists = subsonic.search_artist(query)
    if artists is None:
        logger.warn(f"Failed to search for {query}")
        return abort(
            404, "The artist you are looking for could not be found on the server."
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
