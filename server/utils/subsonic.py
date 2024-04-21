import urllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable

import requests
from colorama import Fore, Style

from .authentication import Auth
from .config import SUBSONIC_CONFIG as CONFIG
from .messages import info, warn, error


@dataclass()
class Song:
    """Song model"""

    title: str
    stream_url: str
    artist: str
    album: str
    cover: str
    duration: str
    track: str
    year: str
    genre: str
    id: str


@dataclass()
class Album:
    """Album model"""

    id: str
    title: str
    artist: str
    cover: str
    year: str
    genre: str
    songs: list[Song] = field(default_factory=list)


@dataclass()
class Artist:
    """Artist model"""

    id: str
    name: str
    albums: list[Album]


class Subsonic:
    def __init__(self) -> None:
        self.auth: Auth = Auth()
        self.url: str = CONFIG["subsonicUrl"]

        self.params: dict[str, str] = {
            "u": CONFIG["user"]["username"],
            "t": self.auth.token,
            "s": self.auth.salt,
            "v": "1.16.1",
            # Client name
            "c": "Rhea",
        }

        self.info: Callable[[str], None] = lambda message: info(
            f"{Fore.MAGENTA}Subsonic{Style.RESET_ALL}", message
        )
        self.warn: Callable[[str], None] = lambda message: warn(
            f"{Fore.MAGENTA}Subsonic{Style.RESET_ALL}", message
        )
        self.error: Callable[[str], None] = lambda message: error(
            f"{Fore.MAGENTA}Subsonic{Style.RESET_ALL}", message
        )

    def xml_request(self, subroute: str, params: dict[str, str]) -> ET.Element:
        """
        Generic request to the Subsonic API in XML.

        Subroute should come in the format of /subroute, with the slash ahead of it.
        """

        r: requests.Response = requests.get(
            url=f"{self.url}/rest{subroute}", params=params
        )

        return ET.fromstring(r.text)

    def build_url(self, subroute: str, params: dict) -> str:
        """
        Generates a generic Subsonic API URL.

        Subroute should come in the format of /subroute, with the slash ahead of it.
        """

        return f"{self.url}/rest{subroute}?{urllib.parse.urlencode(params)}"

    def build_song(self, attrib: dict[str, str]) -> Song:
        stream_url: str = self.build_url(
            "/stream", {**self.params, "id": attrib.get("id")}
        )

        # Make a model of only the necessary data of the song
        return Song(
            title=attrib.get("title"),
            stream_url=stream_url,
            artist=attrib.get("artist"),
            album=attrib.get("album"),
            track=attrib.get("track"),
            year=attrib.get("year"),
            cover=self.build_url(
                "/getCoverArt", {**self.params, "id": attrib.get("coverArt")}
            ),
            duration=attrib.get("duration"),
            genre=attrib.get("genre"),
            id=attrib.get("id"),
        )

    def build_artist(self, attrib: dict[str, str], albums: list[dict]) -> Artist:
        return Artist(
            id=attrib.get("id"),
            name=attrib.get("name"),
            albums=[self.build_album(album) for album in albums],
        )

    def build_album(self, attrib: dict[str, str]) -> Album:
        return Album(
            id=attrib.get("id"),
            title=attrib.get("title"),
            artist=attrib.get("artist"),
            cover=self.build_url(
                "/getCoverArt", {**self.params, "id": attrib.get("coverArt")}
            ),
            year=attrib.get("year"),
            genre=attrib.get("genre"),
            songs=(
                [self.build_song(song) for song in attrib.get("songs")]
                if attrib.get("songs")
                else []
            ),
        )

    def ping(self) -> bool:
        """Test if the server is only and return true only if the status is ok."""

        response: ET.Element = self.xml_request("/ping", self.params)
        self.info("Requested ping to server")

        if response.attrib["status"] == "ok":
            self.info("Requested ping returned ok status")
            return True
        elif response.attrib["status"] == "failed":
            self.warn("Requested ping returned failed status")
            return False
        else:
            self.error("Requested ping returned an unexpected status value")
            return False

    def get_album(self, id: str) -> Album:
        """Generates an Album model"""

        album_data: ET.Element = self.xml_request(
            "/getAlbum", {**self.params, "id": id}
        )[0]

        album_songs: list[Song] = [self.build_song(song.attrib) for song in album_data]

        album = Album(
            id=album_data.attrib["id"],
            title=album_data.attrib["name"],
            artist=album_data.attrib["artist"],
            cover=self.build_url(
                "/getCoverArt", {**self.params, "id": album_data.attrib["coverArt"]}
            ),
            songs=album_songs,
            year=album_data.attrib["year"],
            genre=album_data.attrib["genre"],
        )

        return album

    def get_song(self, id: str) -> Song:
        """Generates a Song model by its ID"""

        song_data: ET.Element = self.xml_request("/getSong", {**self.params, "id": id})[
            0
        ]

        song = self.build_song(song_data.attrib)

        return song

    def get_artist(self, id: str) -> Artist:
        """Generates an Artist model by its ID"""

        artist_data: ET.Element = self.xml_request(
            "/getArtist", {**self.params, "id": id}
        )[0]

        ns = {"ns0": "http://subsonic.org/restapi"}
        album_elems = artist_data.findall("ns0:album", ns)
        albums = [album.attrib for album in album_elems]

        artist = self.build_artist(artist_data, albums)

        return artist

    def search_song(self, query: str, single: bool = True) -> Song | None:
        """Search a song with a query and generates a Song model with the first result or None if
        no one is found"""

        self.info(f'Searching a song with the query "{query}"')

        search_results: ET.Element = self.xml_request(
            "/search3", {**self.params, "query": query}
        )[0]

        only_songs_results: list[ET.Element] = [
            result
            for result in search_results
            if result.tag == "{http://subsonic.org/restapi}song"
        ]

        # Return None if no song is found
        if not only_songs_results:
            self.warn("No song has been matched")
            return None

        if single:
            first_song_result_metadata = only_songs_results[0].attrib

            # Make a model of only the necessary data of the song
            song: Song = self.build_song(first_song_result_metadata)
            self.info(f'Matched the song "{song.title}"')

            return song
        else:
            songs: list[Song] = [
                self.build_song(song.attrib) for song in only_songs_results
            ]
            self.info(f"Matched {len(songs)} songs")
            return songs

    def search_album(self, query: str) -> Album | None:
        """Search an album with a query and returns an Album model or None is no album is found"""

        self.info(f'Searching an album with the query "{query}"')

        search_results: ET.Element = self.xml_request(
            "/search3", {**self.params, "query": query}
        )[0]

        only_albums_results: list[ET.Element] = [
            result
            for result in search_results
            if result.tag == "{http://subsonic.org/restapi}album"
        ]

        # Return None if no album is found
        if not only_albums_results:
            self.warn("No album has been matched")
            return None

        first_album_result_id: str = only_albums_results[0].attrib["id"]
        self.info(f'Matched the album "{only_albums_results[0].attrib["name"]}"')

        return self.get_album(first_album_result_id)

    def search_artist(self, query: str) -> list[Artist] | None:
        """Search an artist with a query and returns a list of Artist models or None is no artist
        is found"""

        self.info(f'Searching an artist with the query "{query}"')

        search_results: ET.Element = self.xml_request(
            "/search3", {**self.params, "query": query}
        )[0]

        only_artists_results: list[ET.Element] = [
            result
            for result in search_results
            if result.tag == "{http://subsonic.org/restapi}artist"
        ]

        # Return None if no artist is found
        if not only_artists_results:
            self.warn("No artist has been matched")
            return None

        # search for albums by artists
        artists: list[Artist] = [
            self.get_artist(artist.attrib["id"]) for artist in (only_artists_results)
        ]
        return artists

    def search_playlist(self, query: str) -> list[Song] | None:
        """Search a playlist with a query and returns a list of Song models with all the songs
        in the album or None is no playlist is found"""

        self.info(f'Searching a playlist with the query "{query}"')
        playlists_list: ET.Element = self.xml_request("/getPlaylists", self.params)[0]

        matched_playlist: str
        for playlist_element in playlists_list:
            if query in playlist_element.attrib["name"]:
                matched_playlist = playlist_element.attrib
                break

        if matched_playlist["id"] is None:
            self.warn("No playlist has been matched")
            return None

        playlist: ET.Element = self.xml_request(
            "/getPlaylist", {**self.params, "id": matched_playlist["id"]}
        )[0]

        only_entries: list[ET.Element] = [
            data
            for data in playlist
            if data.tag == "{http://subsonic.org/restapi}entry"
        ]

        song_list: list[Song] = [
            self.build_song(entry.attrib) for entry in only_entries
        ]

        self.info(f'Matched the playlist "{matched_playlist["name"]}"')

        return song_list

    def get_now_playing(self) -> Song | None:
        """Get the song that is currently playing on the server"""

        now_playing: ET.Element = self.xml_request("/getNowPlaying", self.params)[0]

        if len(now_playing) == 0:
            self.warn("No song currently playing")
            return None

        song: Song = self.build_song(now_playing[0].attrib)

        self.info(f'Now playing "{song.title}"')

        return song

    def scrobble(self, id: str, submission: bool) -> None:
        """Scrobble a song by its ID"""

        self.info(f'Scrobbling song with ID "{id}"')

        self.xml_request(
            "/scrobble", {**self.params, "id": id, "submission": submission}
        )
