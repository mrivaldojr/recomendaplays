from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import pandas as pd
import requests, json
from .ml import read_dataset
from .services import spotify_login_url, get_access_token, get_recent_musics, get_recent_musics_features

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):
    r = get_access_token(request.GET.get('code', ''))
    json_response = get_recent_musics(r.json()['access_token'])
    
    ids = get_music_ids(json_response)
    features = get_recent_musics_features(r.json()['access_token'], ids).json()
    
    json_str = features
    
    info_str = json.dumps(features)
    info = json.loads(info_str)
    df = pd.json_normalize(info['audio_features'])

    df = df[['id','instrumentalness','energy','loudness','tempo']]
    
    df.to_csv(r'recomendaplay/recent_musics.csv', index = None)

    read_dataset()

    return render(request, 'home.html', {'music_list':get_music_list(json_response)})

def get_music_list(json_response):
    musics = json_response.json()
    music_list = []
    for i in range(len(musics['items'])):
        music_list.append(musics['items'][i])
    return music_list

def save_csv(json_string):
    a_json = json.loads(json_string)
    df = pd.DataFrame.from_dict(a_json, orient="index")
    return df

# get only the ids for the recent musics to call the fetures API 
def get_music_ids(json_response):
    musics = json_response.json()
    music_ids = ""
    for i in range(len(musics['items'])):
        music_ids= music_ids+musics['items'][i]['track']['id']+","
    return music_ids

def save_file(json_str):
    out_file = open("json_str.json", "w")
    json.dump(json_str, out_file, indent = 6)
    out_file.close()