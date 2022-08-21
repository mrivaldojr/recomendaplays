import requests, base64, environ
import pandas as pd

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env()

client_id = env("CLIENT_ID")
client_secret = env("CLIENT_SECRET")
redirect_url = "http://localhost:8000/home"

def spotify_login_url():
    return "https://accounts.spotify.com/authorize?client_id="+client_id+\
    "&response_type=code&redirect_uri="+redirect_url+\
    "&scope=user-read-private%20user-read-email%20user-read-recently-played&state=34fFs29kd09"

def get_access_token(code):
    url = 'https://accounts.spotify.com/api/token'
    payload = {'grant_type': 'authorization_code', 
        'code': code, 
        'redirect_uri':'http://localhost:8000/home'
        }
    headers = {'Authorization': 'Basic '+get_base64_id()}
    return requests.post(url, data=payload, headers=headers)

def get_base64_id():
    client_key = client_id+":"+client_secret
    key_bytes = client_key.encode('ascii')
    base64_bytes = base64.b64encode(key_bytes)
    return base64_bytes.decode('ascii')

def get_recent_musics(token):
    url = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
    headers = {'Authorization': 'Bearer '+token}
    return requests.get(url, headers=headers)

def get_playlist(token):
    url = 'https://api.spotify.com/v1/playlists/37i9dQZF1DXd9rSDyQguIk'
    headers = {'Authorization': 'Bearer '+token}
    return requests.get(url, headers=headers)

def get_recent_musics_features(token, ids):
    url = 'https://api.spotify.com/v1/audio-features?ids='+ids
    headers = {'Authorization': 'Bearer '+token}
    return requests.get(url, headers=headers)