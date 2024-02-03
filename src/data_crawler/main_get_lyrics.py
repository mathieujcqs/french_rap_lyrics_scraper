import os
import json

from src.utils.logger import get_console_logger
from src.utils.file_utils import get_config, write_json_file
from utils.lyrics_utils import get_genius_headers, get_artists_ids, get_artist_songs_url, get_song_lyrics

logger = get_console_logger()

def main():
    CONFIG = get_config("main.yml")
    artists_names       = CONFIG["artists"]["names"]
    artists_lyrics_dir  = CONFIG["artists"]["lyrics_dir"]
    genius_base_url     = CONFIG["genius"]['base_url']
    genius_api_base_url = CONFIG["genius"]['api_base_url']
    min_sleep_time      = CONFIG["genius"]['min_sleep_time']
    max_sleep_time      = CONFIG["genius"]['max_sleep_time']

    os.makedirs(artists_lyrics_dir, exist_ok=True)

    headers = get_genius_headers()
    artists_ids = get_artists_ids(genius_api_base_url, headers, artists_names)

    for artist_id, artist_name in artists_ids.items():
        song_urls = get_artist_songs_url(genius_api_base_url, headers, artist_id)
        logger.info(f'Fetching {len(song_urls)} songs for artist: {artist_name}')
        artist_lyrics = get_song_lyrics(genius_base_url, song_urls, min_sleep_time, max_sleep_time)
        
        safe_artist_name = "".join(
            c if c.isalnum() or c in " ._-()" else "_"
            for c in artist_name
        )

        # Constructing the file path
        file_path = os.path.join(artists_lyrics_dir, f"{safe_artist_name}.json")

        # Writing the lyrics data to the file
        write_json_file(artist_lyrics, file_path)

        logger.info(f"Lyrics for {artist_name} saved to {file_path}")

if __name__ == '__main__':
    main()
     