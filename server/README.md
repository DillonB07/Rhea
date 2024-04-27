# Server

This is the backend for Rhea that each of the frontends will connect to to perform actions.

## Features

- Subsonic
    - Search songs, albums and artists
    - Get currently playing song
    - Media controls
        - Toggle play/pause
        - Play song/album by name or ID
        - Shuffle queue
        - Get queue
        - Clear queue
        - Skip to next song
        - Change volume
        - Get volume

## Endpoints

For more detailed information about the endpoints, please see the API documentation at `/apidocs`
when running the server. You may also look at the code - each route has a docstring explaining
all the necessary information about the route.

- `/api/subsonic` - Subsonic API
    - `/search` - Search for songs, albums and artists
        - `/artist/{id}` - Search for an artist
    - `/play`
        - `/song` - Play a song
        - `/album` - Play an album
        - `/toggle_playback` - Toggle play/pause
        - `/queue` - Get the current queue
        - `/clear` - Clear the current queue
        - `/skip` - Skip to the next song
        - `/shuffle` - Shuffle the current queue
        - `/volume` - Get or set the volume
    - `/now_playing` - Get the currently playing song

## Planned Features

These are features that I plan to add at some point. They are roughly sorted by priority, but
there are no ETAs.

- Playlists
- Favourites
- Repeat modes - track, context, none
- Queue management
    - Add song to queue
    - Remove song from queue
    - Move song in queue
    - Play next
- Skip to previous song

## Running the server

To run the server, you will need to have Python 3.8 or higher installed.
You should also create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

You will need to create a `utils/config.py` file. See `utils/config.py.example` for the
necessary fields.

Then, you can run the server with:

```bash
python3 app.py
```