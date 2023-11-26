import json
import yaml

def get_genius_cred(path):
    with open(path) as f:
        genius_cred = json.load(f)
       
    return genius_cred

def get_spotify_cred(path):
    with open(path) as f:
        spotify_creds = json.load(f)

    return spotify_creds

def get_config(path):       
    with open(path) as cfg:
        CONFIG = yaml.load(cfg, Loader=yaml.FullLoader)
    
    return CONFIG

def write_in_config(path, config_data):
    with open(path, 'w', encoding='utf-8') as file:
        yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True)