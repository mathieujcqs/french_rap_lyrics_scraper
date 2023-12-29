import os
import re
import json
import time
import requests
import random as rd
from bs4 import BeautifulSoup
from src.utils.file_utils import get_genius_cred, get_config

def get_artists_ids(api_base_url, headers, artists_names):
    """Fetch artist IDs based on artist names.

    Args:
    api_base_url (str): The base URL of the API.
    headers (dict): The headers to include in the API request.
    artists_names (list of str): A list of artist names.

    Returns:
    list of int: A list of artist IDs.
    """
    artists_ids = {}

    for artist_name in artists_names:
        params = {"q": artist_name}
        print(f"Looking for {artist_name} id")
        response = requests.get(f"{api_base_url}/search/", params=params, headers=headers)
        response_json = response.json()

        artist_id = None
        for hit in response_json['response']['hits']:
            if (hit["result"]["primary_artist"]["name"].lower() == artist_name.lower()) and (hit["type"] == "song"):
                artist_id = hit["result"]["primary_artist"]["id"]
                break

        if artist_id is not None:
            print("Collecting songs for", artist_name, ": Artist ID", artist_id)
            artists_ids[artist_id] = artist_name
        else:
            print("Artist", artist_name, "not found.")

    print("IDs found")
    return artists_ids

def get_artist_songs_url(api_base_url, headers, artist_id):
    """Fetch URLs of all songs by a specific artist from the Genius API.

    Args:
    api_base_url (str): The base URL of the API.
    headers (dict): The headers to include in the API request.
    artist_id (int): The unique identifier for the artist.

    Returns:
    list of tuples: A list containing tuples with the song title and song URL.
    """
    artist_songs_url = {}

    page_count = 1
    while True:
        params = {"per_page": 50, "page": page_count}
        response = requests.get(
            f"{api_base_url}/artists/{artist_id}/songs",
            params=params,
            headers=headers
        )
        response_json = response.json()
        
        for song in response_json['response']['songs']:
            if song["primary_artist"]["id"] == artist_id:
                artist_songs_url[song['title']] =  song["path"]
                
        if response_json['response'].get('next_page') is None:
            break
        else:
            page_count += 1

        print(len(artist_songs_url), "songs found")

    return artist_songs_url

def extract_verse_refrain(lyrics):
    """Extract verses and refrains from lyrics.

    Args:
    lyrics (str): A string containing the song lyrics.

    Returns:
    tuple: A tuple containing two lists, one with the verses and one with the refrains.
    """
    verse_pattern = r'\[Couplet \d+\]\n(.*?)(?=\[Refrain\]|\Z)'
    refrain_pattern = r'\[Refrain\]\n(.*?)(?=\[Couplet \d+\]|\Z)'

    # Extract Couplet and Refrain sections
    verses = re.findall(verse_pattern, lyrics, re.DOTALL)
    refrains = re.findall(refrain_pattern, lyrics, re.DOTALL)

    return verses, refrains

def get_song_lyrics(base_url, song_urls, min_sleep_time, max_sleep_time):
    """
    Fetch and store song lyrics categorized by verses and refrains.

    Args:
    base_url (str): The base URL.
    song_urls (list of tuples): A list of tuples containing song names and URLs.
    min_sleep_time (float): Minimum sleep time between two scrapes of the Genius website.
    max_sleep_time (float): Maximum sleep time between two scrapes of the Genius website.

    Returns:
    dict: A dictionary containing song lyrics categorized by verses and refrains.
    """
    artist_lyrics = {}

    for song_name, url in song_urls:
        try:
            time.sleep(rd.uniform(min_sleep_time, max_sleep_time))
            response = requests.get(f"{base_url}{url}")

            if response.status_code == 200:
                artist_lyrics[song_name] = {}

                html = BeautifulSoup(response.text, "html.parser")
                div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))

                if div:
                    lyrics = div.get_text(separator="\n")
                    song_verses, song_refrains = extract_verse_refrain(lyrics)
                    artist_lyrics[song_name]['lyrics'] = lyrics
                    artist_lyrics[song_name]['verses'] = song_verses
                    artist_lyrics[song_name]['refrains'] = song_refrains
                else:
                    print(f"Lyrics not found for {song_name}")

            elif response.status_code == 429:  # Rate limited
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0)) - int(time.time())
                reset_time = max(0, reset_time)
                print(f"Rate limit exceeded. Sleeping for {reset_time} seconds.")
                time.sleep(reset_time)
                continue  # retry the current song

            else:
                print(f"Error fetching {song_name}. HTTP Status Code: {response.status_code}")

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            continue

    return artist_lyrics

def main(CONFIG, headers):
    artists_names = CONFIG['artists_names']
    base_url = CONFIG['genius_base_url']
    api_base_url = CONFIG['genius_api_base_url']
    artists_lyrics_dir = CONFIG["artists_lyrics_dir"]
    min_sleep_time = CONFIG['min_sleep_time']
    max_sleep_time = CONFIG['max_sleep_time']

    os.makedirs(artists_lyrics_dir, exist_ok=True)

    artists_ids = get_artists_ids(api_base_url, headers, artists_names)

    for artist_id, artist_name in artists_ids.items():
        song_urls = get_artist_songs_url(api_base_url, headers, artist_id)
        print(f'Fetching {len(song_urls)} songs for artist: {artist_name}')
        artist_lyrics = get_song_lyrics(base_url, song_urls, min_sleep_time, max_sleep_time)
        
        safe_artist_name = "".join(
            c if c.isalnum() or c in " ._-()" else "_"
            for c in artist_name
        )

        # Constructing the file path
        file_path = os.path.join(artists_lyrics_dir, f"{safe_artist_name}.json")

        # Writing the lyrics data to the file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(artist_lyrics, file, ensure_ascii=False, indent=4)

        print(f"Lyrics for {artist_name} saved to {file_path}")

if __name__ == '__main__':
    genius_cred = get_genius_cred("genius_cred.json")
    CONFIG = get_config("main.yml")
    headers= { 'Authorization' : f"Bearer {genius_cred['cat']}"}
    main(CONFIG, headers)
     