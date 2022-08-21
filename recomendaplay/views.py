from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import pandas as pd
import requests, json
from .ml import dataset_pca, read_dataset, kmeans_distances, starndarlize_data
from .services import spotify_login_url, get_access_token, get_recent_musics, get_recent_musics_features, get_playlist

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):

    r = get_access_token(request.GET.get('code', ''))

    if r.status_code == 200:
        json_response = get_recent_musics(r.json()['access_token'])

###### Peagar dados de Plylists para gerar dataset com músicas diversas ##########################
        json_response_playlist = get_playlist(r.json()['access_token'])

        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        #print(json_response_playlist.json())
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        # salvar também as informações da músicas
        test = json_response_playlist.json()
        json_reponse_playlist_info = json.dumps(test)
        json_reponse_playlist_info_2 = json.loads(json_reponse_playlist_info)
        df_playlist_info = pd.json_normalize(json_reponse_playlist_info_2['tracks']['items'])

        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print(df_playlist_info)
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        #df = df[['id','instrumentalness','energy','loudness','tempo']]
        df_playlist_info = df_playlist_info[['track.id', 'track.name', 'track.album.name']]
        df_playlist_info.to_csv(r'playlist_info.csv', index = None)

        ids_playlist = get_music_ids_playlists(json_response_playlist)
        #print("-----------------------------------------------------")
        #print(ids_playlist)
        #print("-----------------------------------------------------")
        featuresPlaylist = get_recent_musics_features(r.json()['access_token'], ids_playlist).json()

        info_str_playlist = json.dumps(featuresPlaylist)
        info_playlist = json.loads(info_str_playlist)
        df_playlist = pd.json_normalize(info_playlist['audio_features'])

        # df = df[['id','instrumentalness','energy','loudness','tempo']]
        df_playlist = df_playlist[['id','instrumentalness','energy','loudness','tempo', 'acousticness', 'danceability', 'liveness', 'key', 'mode', 'speechiness', 'valence', 'time_signature']]
        df_playlist.to_csv(r'playlist.csv', index = None)

###### ##############################  #################################################################

        ids = get_music_ids(json_response)
        features = get_recent_musics_features(r.json()['access_token'], ids).json()
        
        json_str = features
        
        info_str = json.dumps(features)
        info = json.loads(info_str)
        df = pd.json_normalize(info['audio_features'])

        # df = df[['id','instrumentalness','energy','loudness','tempo', 'acousticness', 'danceability', 'liveness', 'key', 'mode', 'speechiness']]
        df = df[['instrumentalness','energy','loudness','tempo']]
        df.to_csv(r'recent_musics.csv', index = None)

        kmeans_distances(read_dataset())

        # print("Std -----------------------------------------------------")
        # std_data = starndarlize_data(read_dataset())

        dataset_pca(read_dataset())

        return render(request, 'home.html', {'music_list':get_music_list(json_response)})
    else:
        return render(request, 'sign_in.html')

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

def get_music_ids_playlists(json_response):
    musics = json_response.json()
    music_ids = ""
    for i in range(len(musics['tracks']['items'])):
        music_ids= music_ids+musics['tracks']['items'][i]['track']['id']+","
    return music_ids

def save_file(json_str):
    out_file = open("json_str.json", "w")
    json.dump(json_str, out_file, indent = 6)
    out_file.close()