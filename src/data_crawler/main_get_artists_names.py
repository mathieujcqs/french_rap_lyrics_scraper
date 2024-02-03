
from src.utils.logger import get_console_logger
from src.utils.file_utils import get_config, write_in_config
from utils.artists_names_utils import get_Spotipy_Session, search_french_rap_playlists, get_playlists_tracks, get_artists_ids_from_tracks, get_artists_names

logger = get_console_logger()

def main():
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

