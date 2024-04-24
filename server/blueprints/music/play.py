import random
import time

import vlc
from flask import Blueprint, abort, request

from . import subsonic, logger

play = Blueprint("play", __name__)

music_queue = []
current_song = None
player = vlc.Instance()
media_player = player.media_player_new()
media_player.audio_set_volume(50)


@play.route("/song", methods=["POST"])
def play_song():
    """
    Play a song by searching for the song name or providing the song id.
    ID takes precedence over query.
    ---
    tags:
      - subsonic
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              query:
                type: string
              id:
                type: string
    responses:
        200:
            description: The song was successfully added to the queue
        400:
            description: No song name or id was provided
        404:
            description: The song you are looking for could not be found on the server
    """
    data = request.get_json()
    query: str = data.get("query")
    track_id: str = data.get("id")
    if not query and not id:
        return abort(400, "No song name or id was provided.")
    if track_id:
        logger.info(f"Attempting to play song with id {track_id}")
        song = subsonic.get_song(track_id)
        if not song:
            logger.warn(f"Failed to play song with id {track_id}")
            return abort(
                404, "The song you are looking for could not be found on the server."
            )
        s = song[0]
        music_queue.append(s)
        return f"Added {s.title} by {s.artist} to the queue"
    elif query:
        logger.info(f"Attempting to play {query}")
        song = subsonic.search_song(query)
        if not song:
            logger.warn(f"Failed to play {query}")
            return abort(
                404, "The song you are looking for could not be found on the server."
            )
        s = song[0]
        music_queue.append(s)
        return f"Added {s.title} by {s.artist} to the queue"


@play.route("/album", methods=["POST"])
def play_album():
    """
    Play an album by searching for the album name or providing the album id.
    ID takes precedence over query.
    ---
    tags:
      - subsonic
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              query:
                type: string
              id:
                type: string
    responses:
        200:
            description: The album was successfully added to the queue
        400:
            description: No album name or id was provided
        404:
            description: The album you are looking for could not be found on the server
    """
    data = request.get_json()
    query: str = data.get("query")
    album_id: str = data.get("id")
    if not query and not album_id:
        return abort(400, "No album name or id was provided.")
    if album_id:
        logger.info(f"Attempting to play album with id {album_id}")
        album = subsonic.get_album(album_id)
        if not album:
            logger.warn(f"Failed to play album with id {album_id}")
            return abort(
                404, "The album you are looking for could not be found on the server."
            )
        music_queue.extend(album.songs)
        return f"Added songs from {album.title} by {album.artist} to the queue"
    elif query:
        logger.info(f"Attempting to play {query}")
        album = subsonic.search_album(query)
        if not album:
            logger.warn(f"Failed to play {query}")
            return abort(
                404, "The album you are looking for could not be found on the server."
            )
        music_queue.extend(album.songs)
        return f"Added songs from {album.title} by {album.artist} to the queue"


@play.route("/next", methods=["POST"])
def next_song():
    """
    Skip the current song and play the next song in the queue
    ---
    tags:
      - subsonic
    responses:
        200:
            description: Skipped the current song
        404:
            description: No song is currently playing
    """
    if media_player.is_playing():
        logger.info("Skipping the current song")
        media_player.stop()
        return "Skipped the current song"
    else:
        logger.warn("No song is currently playing")
        return abort(404, "No song is currently playing")


@play.route("/queue", methods=["GET"])
def queue():
    """
    Get the current queue
    ---
    tags:
      - subsonic
    responses:
        200:
            description: The current queue
            schema:
                type: object
                properties:
                    queue:
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
        404:
            description: The queue is empty
    """
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


@play.route("/shuffle", methods=["POST"])
def shuffle():
    """
    Shuffle the current queue
    ---
    tags:
      - subsonic
    responses:
        200:
            description: Shuffled the queue
    """
    logger.info("Shuffling the queue")
    random.shuffle(music_queue)
    return "Shuffled the queue"


@play.route("/clear", methods=["POST"])
def clear():
    """
    Clear the current queue
    ---
    tags:
      - subsonic
    responses:
        200:
            description: Cleared the queue
    """
    logger.info("Cleared the queue")
    music_queue.clear()
    return "Cleared the queue"


@play.route("/toggle_playback", methods=["POST"])
def toggle_playback():
    """
    Toggle the playback of the current song
    ---
    tags:
      - subsonic
    responses:
        200:
            description: Toggled the playback of the current song
        204:
            description: No song is currently playing
    """
    out = media_player.pause()
    if out == 0:
        return f"Toggled the playback of the current song {out}"
    else:
        return abort(204, "No song is currently playing")


@play.route("/volume", methods=["GET", "POST"])
def volume():
    """
    Get, set or increase the volume of the media player.
    GET to get the current volume.
    POST to set or increase the volume.
    ---
    tags:
      - subsonic
    parameters:
        - in: body
          name: body
          required: false
          schema:
            type: object
            properties:
              amount:
                type: integer
                description: The amount to increase the volume by or set to if set is True
              set:
                type: boolean
                description: Set the volume to the amount provided
    responses:
        200:
            description: The volume is now set to the amount provided
        400:
            description: The amount provided is not an integer
        404:
            description: The volume is already at the maximum or minimum
    """
    # Volume should ideally be changed via the hosts volume control. Whilst this does work,
    # it is not recommended to be used as it can significantly decrease the quality of the audio.
    data = request.get_json()
    change = data.get("amount", 0)
    set = data.get("set", False)
    if request.method == "GET":
        return {media_player.audio_get_volume()}

    if change != 0:
        new_volume = media_player.audio_get_volume() + change if not set else change
        if new_volume > 200:
            new_volume = 200
        elif new_volume < 0:
            new_volume = 0
        media_player.audio_set_volume(new_volume)
        return f"Volume is now {new_volume}"

    return f"Volume is {media_player.audio_get_volume()}"


def check_queue_and_play():
    global media_player
    global music_queue
    global current_song
    scrobbled = False

    while True:
        length = media_player.get_length() / 1000
        current_time = media_player.get_time() / 1000
        if (
            not media_player.is_playing()
            and len(music_queue) > 0
            and media_player.get_state() != vlc.State.Paused
        ):
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
