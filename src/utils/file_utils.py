import os
import json
import yaml

from typing import List, Dict, Set

from src.paths import CONFIG_DIR, DATA_DIR

def get_genius_cred(path):
    with open(CONFIG_DIR / path,) as f:
        genius_cred = json.load(f)
       
    return genius_cred

def get_spotify_cred(path: str) -> Dict:
    with open(CONFIG_DIR / path,) as f:
        spotify_creds = json.load(f)

    return spotify_creds

def get_config(path: str) -> Dict:  
    with open(CONFIG_DIR / path) as cfg:
        CONFIG = yaml.load(cfg, Loader=yaml.FullLoader)
    
    return CONFIG

def write_in_config(path, config_data) -> None:
    with open(CONFIG_DIR / path, 'w', encoding='utf-8') as file:
        yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True)

def read_songs_json_files(folder_path: str):
    all_songs = []
    for file_name in os.listdir(DATA_DIR / folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(DATA_DIR / folder_path, file_name)
            with open(file_path, 'r') as file:
                data = json.load(file)
                for song_name, song_details in data.items():
                    song_details['song_name'] = song_name
                    song_details['artist_name'] = file_name.replace(".json", '')
                    all_songs.append(song_details)
    return all_songs

def write_json_file(data, file_path) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)