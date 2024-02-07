
from src.utils.logger import get_console_logger
from src.utils.file_utils import get_config, write_in_config
from utils.artists_names_utils import get_Spotipy_Session, search_french_rap_playlists, get_playlists_tracks, get_artists_ids_from_tracks, get_artists_names

logger = get_console_logger()

def main():
    """
    Searches for French rap playlists on Spotify, extracts tracks, and updates artist names in configuration.

    This function automates the process of updating a YAML configuration file ('main.yml') with
    artist names extracted from French rap playlists found on Spotify. It performs several steps:

    1. Loads search parameters and settings from 'main.yml', including search type, limit, query,
       genre, and offsets for playlist search pagination.
    2. Initiates a Spotify session using credentials configured for the Spotipy client.
    3. Searches for playlists matching the specified query ('French rap') and parameters.
    4. Retrieves tracks from the found playlists and extracts artist IDs.
    5. Fetches artist names based on the extracted IDs, filtering by the specified genre.
    6. Updates the 'main.yml' configuration file with the sorted list of unique artist names.

    The function ensures that the configuration file always contains a current list of artists
    related to the French rap genre, facilitating further processing or analysis tasks.

    Side effects:
    - Modifies 'main.yml' by updating the 'artists_names' key with new artist names.

    Requires:
    - A valid Spotify API client configuration in 'main.yml'.
    - The Spotipy library and a Spotify developer account for API access.
    """

    CONFIG  =  get_config("main.yml")
    type    =  CONFIG["spotipy"]["type"]
    limit   =  CONFIG["spotipy"]["limit"]
    query   =  CONFIG["spotipy"]["query"]
    genre   =  CONFIG["spotipy"]["genre"]
    offsets =  CONFIG["spotipy"]["offsets"]
    
    sp = get_Spotipy_Session()
    
    playlist_ids = search_french_rap_playlists(sp, query, type, offsets, limit)
    tracks = get_playlists_tracks(sp, playlist_ids)
    artist_ids = get_artists_ids_from_tracks(tracks)
    artist_names = get_artists_names(sp, artist_ids, genre)

    config_data = get_config("main.yml")
    config_data["artists"]["names"] = sorted(list(artist_names))
    write_in_config("main.yml", config_data)

    logger.info('Artist names saved to main.yml under artists_names key')

if __name__ == "__main__":
    main()

