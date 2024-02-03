import time
import random as rd
from typing import List, Dict, Set

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

from src.utils.file_utils import get_spotify_cred
from src.utils.logger import get_console_logger

logger = get_console_logger()

def search_french_rap_playlists(sp, query: str, type: str, offsets: List[int], limit: int) -> List[str]:
    """
    Fetches French hip hop playlists from Spotify.

    Parameters:
    sp (Spotify object): Spotify client object.
    offsets (list of int): List of offsets for pagination.

    Returns:
    list: List of playlist IDs.
    """
    all_playlist_ids = []

    for offset in offsets:
        logger.info(f'Fetching playlists starting from offset: {offset}')
        response = sp.search(q=query, limit=limit, type=type, offset=offset)
        all_playlist_ids.extend([item["id"] for item in response["playlists"]["items"]])

        while response["playlists"]["next"]:
            response = sp.next(response["playlists"])
            all_playlist_ids.extend([item["id"] for item in response["playlists"]["items"]])

    return all_playlist_ids


def get_tracks(sp, playlist_id: str) -> List[Dict]:
    """
    Retrieves tracks from a specific Spotify playlist.

    Parameters:
    sp (Spotify object): Spotify client object.
    playlist_id (str): The Spotify ID of the playlist.

    Returns:
    list: List of tracks in the playlist.
    """
    tracks = []

    result = sp.playlist_items(playlist_id)
    tracks.extend(result["items"])

    while result["next"]:
        result = sp.next(result)
        tracks.extend(result["items"])

    return tracks


def get_playlists_tracks(sp, playlist_ids: List[str]) -> List[Dict]:
    """
    Retrieves tracks from multiple Spotify playlists.

    Parameters:
    sp (Spotify object): Spotify client object.
    playlist_ids (list of str): List of Spotify playlist IDs.

    Returns:
    list: List of tracks from all specified playlists.
    """
    all_tracks = []

    for count, playlist_id in enumerate(playlist_ids, start=1):
        logger.info(f'Fetching tracks from playlist {count}')
        tracks = get_tracks(sp, playlist_id)
        all_tracks.extend(tracks)

    logger.info(f"Fetched {len(all_tracks)} tracks")

    return all_tracks


def get_artists_ids_from_tracks(tracks: List[Dict]) -> Set[str]:
    """
    Extracts unique artist IDs from a list of tracks.

    Parameters:
    tracks (list): A list of track dictionaries.

    Returns:
    set: A set of unique artist IDs.
    """
    artists_ids = {track["track"]["artists"][0]["id"] for track in tracks if track["track"]}

    logger.info(f'Fetched {len(artists_ids)} unique artists')

    return artists_ids


def get_artists_names(sp, artist_ids: Set[str], genre: str) -> Set[str]:
    """
    Retrieves artist names from Spotify based on their IDs if they belong to the 'french hip hop' genre.

    Parameters:
    sp (Spotify object): Spotify client object.
    artist_ids (set of str): Set of artist IDs.

    Returns:
    set: A set of artist names.
    """
    artist_names = set()
    
    for idx, artist_id in enumerate(artist_ids):
        # Adding extra sleep time to avoid getting timed out
        if idx % 1000 == 0:
            time.sleep(10)
        
        time.sleep(rd.uniform(0.2, 0.7))
        logger.info(f"Fetching artist {artist_id}")
        result = sp.artist(artist_id)

        if "genres" in result and genre in result["genres"]:
            logger.info(result["name"])
            artist_names.add(result["name"])

    return artist_names

def get_Spotipy_Session():
    spotify_creds = get_spotify_cred("spotify_cred.json")

    client_cred_manager = SpotifyClientCredentials(
        client_id=spotify_creds["cid"], 
        client_secret=spotify_creds["cis"]
    )

    sp_auth = SpotifyOAuth(client_id=spotify_creds["cid"],
            client_secret=spotify_creds["cis"],
            redirect_uri="http://127.0.0.1:8000/",
            scope="user-library-read"
            )
    
    return spotipy.Spotify(
            client_credentials_manager=client_cred_manager,
            auth= sp_auth.get_cached_token()
        )
