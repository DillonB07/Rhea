import vlc
from flask import Blueprint, abort

from . import subsonic, logger

play = Blueprint("play", __name__)

music_queue = []
current_song = None
player = vlc.Instance()
media_player = player.media_player_new()


@play.route("/song/query/<string:query>")
def play_song(query: str):
    logger.info(f"Attempting to play {query}")
    song = subsonic.search_song(query)
    if song is None:
        logger.warn(f"Failed to play {query}")
        return abort(
            404, "The song you are looking for could not be found on the server."
        )
    music_queue.append(song)
    return f"Added {song.title} by {song.artist} to the queue"


@play.route("/song/id/<string:id>")
def play_song_by_id(id: str):
    logger.info(f"Attempting to play song with id {id}")
    song = subsonic.get_song(id)
    if song is None:
        logger.warn(f"Failed to play song with id {id}")
        return abort(
            404, "The song you are looking for could not be found on the server."
        )
    music_queue.append(song)
    return f"Added {song.title} by {song.artist} to the queue"


@play.route("/album/query/<string:query>")
def play_album(query: str):
    logger.info(f"Attempting to play {query}")
    album = subsonic.search_album(query)
    if album is None:
        logger.warn(f"Failed to play {query}")
        return abort(
            404, "The album you are looking for could not be found on the server."
        )
    music_queue.extend(album.songs)
    return f"Added songs from {album.title} by {album.artist} to the queue"


@play.route("/album/id/<string:id>")
def play_album_by_id(id: str):
    logger.info(f"Attempting to play album with id {id}")
    album = subsonic.get_album(id)
    if album is None:
        logger.warn(f"Failed to play album with id {id}")
        return abort(
            404, "The album you are looking for could not be found on the server."
        )
    music_queue.extend(album.songs)
    return f"Added songs from {album.title} by {album.artist} to the queue"


@play.route("/next")
def next_song():
    if media_player.is_playing():
        logger.info("Skipping the current song")
        media_player.stop()
        return "Skipped the current song"
    else:
        logger.warn("No song is currently playing")
        return abort(404, "No song is currently playing")


@play.route("/queue")
def queue():
    return {
        "queue": [
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
            for song in music_queue[:50]
        ]
    }


def check_queue_and_play():
    global media_player
    global music_queue
    global current_song
    scrobbled = False

    while True:
        length = media_player.get_length() / 1000
        current_time = media_player.get_time() / 1000
        if not media_player.is_playing() and len(music_queue) > 0:
            current_song = music_queue.pop(0)
            media = player.media_new(current_song.stream_url)
            media_player.set_media(media)
            media_player.play()
            subsonic.scrobble(current_song.id, False)
            scrobbled = False
            logger.info(
                f"Now playing {current_song.title} | {current_song.artist} | {current_song.album}"
            )
        elif (
            media_player.is_playing()
            and (current_time / length) > 0.5
            and not scrobbled
        ):
            subsonic.scrobble(current_song.id, True)
            scrobbled = True
        else:
            time.sleep(1)
