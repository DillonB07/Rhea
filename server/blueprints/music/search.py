from flask import Blueprint, abort, request

from . import logger, subsonic

search = Blueprint("search", __name__)


@search.route("/", methods=["GET"])
def search_query():
    """
    Search for a song, album, or artist on the server
    ---
    tags:
      - subsonic
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: The query to search for
      - name: type
        in: query
        type: string
        required: false
        description: The type of search to perform (song, album, artist, all)
    responses:
      200:
        description: The search results
        content:
          application/json:
            schema:
              type: object
              properties:
                songs:
                  type: array
                  items:
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
                        type: string
                      genre:
                        type: string
                      year:
                        type: string
                      id:
                        type: string
                albums:
                  type: array
                  items:
                    type: object
                    properties:
                      title:
                        type: string
                      artist:
                        type: string
                      cover:
                        type: string
                      id:
                        type: string
                      year:
                        type: string
                      genre:
                        type: string
                artists:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      id:
                        type: string
                      albums:
                        type: array
                        items:
                          type: object
                          properties:
                            title:
                              type: string
                            cover:
                              type: string
                            id:
                              type: string
                            year:
                              type: string
                            genre:
                              type: string
      404:
        description: The song, album, or artist could not be found
    """
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
                    for song in (songs if songs is not None else [])
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
                    for album in (albums if albums is not None else [])
                ]
            }

        case "artist":
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
                        "albums": [
                            {
                                "title": album.title,
                                "cover": album.cover,
                                "id": album.id,
                                "year": album.year,
                                "genre": album.genre,
                            }
                            for album in artist.albums
                        ],
                    }
                    for artist in (artists if artists is not None else [])
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
                    for song in (songs if songs is not None else [])
                ],
                "albums": [
                    {
                        "title": album.title,
                        "artist": album.artist,
                        "cover": album.cover,
                        "id": album.id,
                        "year": album.year,
                        "genre": album.genre,
                    }
                    for album in (albums if albums is not None else [])
                ],
                "artists": [
                    {
                        "name": artist.name,
                        "id": artist.id,
                        "albums": artist.albums,
                    }
                    for artist in (artists if artists is not None else [])
                ],
            }


@search.route("/artist/<string:id>", methods=["GET"])
def get_artist(id: str):
    """
    Get an artist's information by their ID
    ---
    tags:
      - subsonic
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: The ID of the artist to get
    responses:
        200:
            description: The artist's information
            content:
            application/json:
                schema:
                type: object
                properties:
                    name:
                    type: string
                    id:
                    type: string
                    albums:
                    type: array
                    items:
                        type: object
                        properties:
                        title:
                            type: string
                        cover:
                            type: string
                        id:
                            type: string
        404:
            description: The artist could not be found
    """
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
            for album in (artist.albums if artist.albums is not None else [])
        ],
    }
