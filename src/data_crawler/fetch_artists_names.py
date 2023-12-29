import time
import random as rd
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from src.utils.file_utils import get_spotify_cred, get_config, write_in_config

def search_french_rap_playlists(sp, offsets):
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
        print(f'Fetching playlists starting from offset: {offset}')
        response = sp.search(q="genre: french hip hop", limit=50, type="playlist", offset=offset)
        all_playlist_ids.extend([item["id"] for item in response["playlists"]["items"]])

        while response["playlists"]["next"]:
            response = sp.next(response["playlists"])
            all_playlist_ids.extend([item["id"] for item in response["playlists"]["items"]])

    return all_playlist_ids


def get_playlist_tracks(sp, playlist_id):
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


def get_playlists_tracks(sp, playlist_ids):
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
        print(f'Fetching tracks from playlist {count}')
        tracks = get_playlist_tracks(sp, playlist_id)
        all_tracks.extend(tracks)

    print(f"Fetched {len(all_tracks)} tracks")

    return all_tracks


def get_artists_ids_from_tracks(tracks):
    """
    Extracts unique artist IDs from a list of tracks.

    Parameters:
    tracks (list): A list of track dictionaries.

    Returns:
    set: A set of unique artist IDs.
    """
    artists_ids = {track["track"]["artists"][0]["id"] for track in tracks if track["track"]}

    print(f'Fetched {len(artists_ids)} unique artists')

    return artists_ids


def get_tracks_artists_spotify(sp, artist_ids):
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
        print(f"Fetching artist {artist_id}")
        result = sp.artist(artist_id)

        if "genres" in result and "french hip hop" in result["genres"]:
            print(result["name"])
            artist_names.add(result["name"])

    return artist_names


def main():

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
    
    sp = spotipy.Spotify(client_credentials_manager=client_cred_manager,auth= sp_auth.get_cached_token())
    playlist_ids = search_french_rap_playlists(sp, [0, 50, 100, 150, 200])
    tracks = get_playlists_tracks(sp, playlist_ids)
    artist_ids = get_artists_ids_from_tracks(tracks)
    artist_names = get_tracks_artists_spotify(sp, artist_ids)

    
    config_data = get_config("main.yml")
    config_data['artists_names'] = sorted(list(artist_names))
    write_in_config("main.yml", config_data)

    print('Artist names saved to main.yml under artists_names key')

if __name__ == "__main__":
    main()

