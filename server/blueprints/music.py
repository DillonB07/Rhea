import vlc
from flask import Blueprint, abort

from utils.logging import print_info, print_warn
from utils.subsonic import Subsonic

music = Blueprint("music", __name__)

subsonic: Subsonic = Subsonic()
music_queue = []
current_song = None
player = vlc.Instance()
media_player = player.media_player_new()


@music.before_request
def before_request():
    try:
        print_info("Attempting to connect to Subsonic server")
        if not subsonic.ping():
            print_warn("Failed to connect to Subsonic server")
            return abort(500, "Failed to connect to Subsonic server")
        else:
            print_info("Connected to Subsonic server")
    except Exception:  # noqa
        # We use a broad exception as there are a variety of Connection* errors that can be raised
        print_warn("Failed to connect to Subsonic server")
        return abort(500, "Failed to connect to Subsonic server")


@music.route("/")
def index():
    return "Connected to Subsonic server"


@music.route("/play_song/<string:query>")
def play_song(query: str):
    print_info(f"Attempting to play {query}")
    song = subsonic.search_song(query)
    if song is None:
        print_warn(f"Failed to play {query}")
        return abort(
            404, "The song you are looking for could not be found on the server."
        )
    music_queue.append(song)
    return f"Added {song.title} by {song.artist} to the queue"


@music.route("/play_album/<string:query>")
def play_album(query: str):
    print_info(f"Attempting to play {query}")
    album = subsonic.search_album(query)
    if album is None:
        print_warn(f"Failed to play {query}")
        return abort(
            404, "The album you are looking for could not be found on the server."
        )
    music_queue.extend(album.songs)
    return f"Added songs from {album.title} by {album.artist} to the queue"


@music.route("/play_song_by_id/<string:id>")
def play_song_by_id(id: str):
    print_info(f"Attempting to play song with id {id}")
    song = subsonic.get_song(id)
    if song is None:
        print_warn(f"Failed to play song with id {id}")
        return abort(
            404, "The song you are looking for could not be found on the server."
        )
    music_queue.append(song)
    return f"Added {song.title} by {song.artist} to the queue"


@music.route("/next")
def next_song():
    if media_player.is_playing():
        print_info("Skipping the current song")
        media_player.stop()
        return "Skipped the current song"
    else:
        print_warn("No song is currently playing")
        return abort(404, "No song is currently playing")


@music.route("/queue")
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


@music.route("/search_song/<string:query>")
def search_song(query: str):
    print_info(f"Attempting to search for {query}")
    songs = subsonic.search_song(query, single=False)
    if songs is None:
        print_warn(f"Failed to search for {query}")
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


@music.route("/now_playing")
def now_playing():
    print_info("Attempting to get the current playing song")
    song = subsonic.get_now_playing()
    if song is None:
        print_warn("Failed to get the current playing song")
        return abort(404, "No song is currently playing")
    print_info(f"Now playing {song.title} | {song.artist} | {song.album}")
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
            print_info(
                f"Now playing {current_song.title} | {current_song.artist} | {current_song.album}"
            )
        elif (
            media_player.is_playing()
            and (current_time / length) > 0.5
            and not scrobbled
        ):
            subsonic.scrobble(current_song.id, True)
            scrobbled = True
