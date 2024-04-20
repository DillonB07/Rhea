# from queue  import Queue
import time

import vlc
from flask import Blueprint, abort

from utils.logging import print_info, print_warn
from utils.subsonic import Subsonic

music = Blueprint("music", __name__)

# queue: Queue = Queue()
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
    print_info("Attempting to connect to Subsonic server")
    if subsonic.ping():
        print_info("Connected to Subsonic server")
        return "Connected to Subsonic server"
    else:
        print_warn("Failed to connect to Subsonic server")
        return "Failed to connect to Subsonic server"


@music.route("/play/<string:query>")
def play(query: str):
    print_info(f"Attempting to play {query}")
    song = subsonic.search_song(query)
    if song is None:
        print_warn(f"Failed to play {query}")
        return abort(
            404, "The song you are looking for could not be found on the server."
        )
    music_queue.append(song)
    return f"Attempting to play {song.title} on {song.album} by {song.artist}"


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

    while True:
        if not media_player.is_playing() and len(music_queue) > 0:
            current_song = music_queue.pop(0)
            media = player.media_new(current_song.stream_url)
            media_player.set_media(media)
            media_player.play()
        else:
            # Sleep for a second to avoid busy waiting
            time.sleep(1)
