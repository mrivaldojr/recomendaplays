from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import pandas as pd
import requests, json
from .ml import dataset_pca, read_dataset, kmeans_distances, standarlize_dataset, kmeans_dataset
from .services import spotify_login_url, get_access_token, get_recent_musics, get_recent_musics_features, get_playlist

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):

    r = get_access_token(request.GET.get('code', ''))

    if r.status_code == 200:
        # # json com as músicas ouvidas recentemente
        json_response = get_recent_musics(r.json()['access_token'])

        big_dataset_df = read_dataset('big_dataset_labeled.csv')
        #print(big_dataset_df)

        #--Código para rodar o kmeans no dataset grande
        # dataset_grande_df = read_dataset("full_data_remove_duplicates.csv")
        # df_grande_features = dataset_grande_df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']]
        # ds_grande_columns_to_normalize = df_grande_features.iloc[:, 1:7]
        # ds_grande_ids = df_grande_features.iloc[:, 0:1]

        # column_names_ = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']

        # dataset_grande_stand = standarlize_dataset(ds_grande_columns_to_normalize)
        # dataset_grande_stand_df = pd.DataFrame(dataset_grande_stand, columns = column_names_)

        # final_stand_dataset = pd.concat([ds_grande_ids, dataset_grande_stand_df], axis='columns')

        # kmeans_dataset(final_stand_dataset.iloc[:,1:7], 80)
        #-- Fim Código para rodar o kmeans no dataset grande (formação de clusteres feitas anteriormente para salvar tempo de execução)

        # recupera ids para chamar a API de features
        ids = get_music_ids(json_response)
        features = get_recent_musics_features(r.json()['access_token'], ids).json()
        json_str = features
        info_str = json.dumps(features)
        info = json.loads(info_str)

        df = pd.json_normalize(info['audio_features'])

        #dataframe com todas as features    
        #df_completo = df[['id','instrumentalness','energy','loudness','tempo', 'acousticness', 'danceability', 'liveness', 'key', 'mode', 'speechiness', 'valence', 'time_signature']]
        
        #daframe com subset de features
        df_completo = df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']]
        #ds_columns_to_normalize = df_completo.iloc[:, 1:13]
        ds_columns_to_normalize = df_completo.iloc[:, 1:7]
        ds_ids = df_completo.iloc[:, 0:1]

        #todas as features
        #column_names = ['energy','danceability','acousticness','instrumentalness','key','liveness','loudness','mode','speechiness','tempo','time_signature','valence']

        column_names = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']

        dataset_csv_stand = standarlize_dataset(ds_columns_to_normalize)
        dataset_csv_stand_df = pd.DataFrame(dataset_csv_stand, columns = column_names)

        final_stand_dataset = pd.concat([ds_ids, dataset_csv_stand_df], axis='columns')

        #print(final_stand_dataset)

        trained_kmeans = kmeans_dataset(final_stand_dataset.iloc[:,1:7], 3)

        recomendation(trained_kmeans, big_dataset_df)
        
        #kmeans_dataset(final_stand_dataset.iloc[:,1:13])

        #df = df[['instrumentalness','energy','loudness','tempo']]
        #df.to_csv(r'recent_musics.csv', index = None)

        #kmeans_distances(read_dataset("recent_musics.csv"))

        # print("Std -----------------------------------------------------")
        # std_data = starndarlize_data(read_dataset("recent_musics.csv"))

        #dataset_pca(read_dataset("recent_musics.csv"))

        #print(get_music_list(json_response))

        return render(request, 'home.html', {'music_list':get_music_list(json_response)})
    else:
        return render(request, 'sign_in.html')

def get_music_list(json_response):
    recent_tracks = json_response.json()['items']
    recent_tracks = { each['track']['id'] : each for each in recent_tracks }.values()
    music_list = []
    for i in range(len(recent_tracks)):
        music_list.append(list(recent_tracks)[i])
    return music_list

def recomendation(kmeans_trained, p_dataframe):
    lowest = 0
    average_distance = 0
    print("--------------------Recommendation")
    for i in range (80):
        print('cluster')
        cluster_label_i = p_dataframe.query("Cluster == @i")
        print(cluster_label_i)
        print("labels")
        labels = kmeans_trained.predict(cluster_label_i.iloc[:,1:6])
        distances = kmeans_trained.transform(cluster_label_i.iloc[:,1:6])
        print(labels)
        quantity = len(cluster_label_i.index)
        print('quantity')
        print(quantity)
        average_distance = distances.sum() / quantity
        print('average distance')
        print(average_distance)
        if i == 0:
            lowest = distances.sum()
            cluster = i
        if(average_distance < lowest):
            lowest = average_distance
            cluster = i
        return cluster

    print('Menor Cluster')
    print(cluster)
    print('menor distancia')
    print(lowest)

def save_csv(json_string):
    a_json = json.loads(json_string)
    df = pd.DataFrame.from_dict(a_json, orient="index")
    return df

# get only the ids for the recent musics to call the fetures API 
def get_music_ids(json_response):
    musics = json_response.json()
    music_ids_arr = []
    #music_ids = ""

    for i in range(len(musics['items'])):
        #music_ids = music_ids+musics['items'][i]['track']['id']+","
        music_ids_arr.append(musics['items'][i]['track']['id'])
    music_ids_arr = list(dict.fromkeys(music_ids_arr))
    music_ids_string = ','.join(x for x in music_ids_arr)
    return music_ids_string

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