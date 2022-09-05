from locale import normalize
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import pandas as pd
import requests, json
from .ml import dataset_pca, read_dataset, standarlize_dataset, kmeans_dataset, normalize_dataset
from .services import spotify_login_url, get_access_token, get_recent_musics, get_recent_musics_features, get_user, create_playlist, add_items_playlist

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):

    r = get_access_token(request.GET.get('code', ''))

    if r.status_code == 200:
        # json com as músicas ouvidas recentemente
        json_response = get_recent_musics(r.json()['access_token'])
        user = features = get_user(r.json()['access_token']).json()
        print('User----------------------------')
        print(user['id'])

        print('Create Playlist--------------------')
        playlist_json = create_playlist(user['id'],r.json()['access_token'], 'Created via recsys').json()
        print(playlist_json)
        print(playlist_json['id'])

        #print(add_items_playlist(r.json()['access_token'], '30TtxTGS2d4CSovY2DhIoA', '\"spotify:track:2FPhwJ4XMald6q18tGjEY5\", \"spotify:track:4m1mqQuy34Nzh0480VR364\"').json())

        # read big dataset previously clustered
        #big_dataset_df = read_dataset('big_dataset_labeled_5clusters.csv')
        #big_dataset_df = read_dataset('dataset_9features_2cluster_labeled.csv')
        big_dataset_df = read_dataset('dataset_9features_4cluster_labeled.csv')
       
        # recupera ids para chamar a API de features
        ids = get_music_ids(json_response)
        features = get_recent_musics_features(r.json()['access_token'], ids).json()
        json_str = features
        info_str = json.dumps(features)
        info = json.loads(info_str)

        #dataframe com todas as features    
        #df_completo = df[['id','instrumentalness','energy','loudness','tempo', 'acousticness', 'danceability', 'liveness', 'key', 'mode', 'speechiness', 'valence', 'time_signature']]
        
        #dataframe com features das musicas dos usuários
        df = pd.json_normalize(info['audio_features'])
        #df_completo = df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']]
        df_completo = df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness','tempo', 'valence']]
        #ds_columns_to_normalize = df_completo.iloc[:, 1:13]
        #ds_columns_to_normalize = df_completo.iloc[:, 1:7]
        ds_columns_to_normalize = df_completo.iloc[:, 1:9]
        ds_ids = df_completo.iloc[:, 0:1]

        #todas as features
        #column_names = ['energy','danceability','acousticness','instrumentalness','key','liveness','loudness','mode','speechiness','tempo','time_signature','valence']

        #column_names = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']
        column_names = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness', 'tempo', 'valence']

        #dataset_csv_stand = standarlize_dataset(ds_columns_to_normalize)

        #tratamento dos dados do usuário antes de fazer o modelo de clusters
        dataset_csv_stand = normalize_dataset(ds_columns_to_normalize)
        dataset_csv_stand_df = pd.DataFrame(dataset_csv_stand, columns = column_names)
        final_stand_dataset = pd.concat([ds_ids, dataset_csv_stand_df], axis='columns')
        print('final_stand_dataset')
        print(final_stand_dataset)

        trained_kmeans = kmeans_dataset(final_stand_dataset, 3)

        #chosen_cluster = recomendation(trained_kmeans, big_dataset_df)
        chosen_ids = recomendation(trained_kmeans, big_dataset_df)
        chosen_ids['id'] = '\"spotify:track:' + big_dataset_df['id'].astype(str) +'\"'
        print(chosen_ids)
        rec_id_list = chosen_ids['id'].tolist()
        rec = list_to_string(rec_id_list)
        print(add_items_playlist(r.json()['access_token'], playlist_json['id'], rec).json())

        #playlist_df =  big_dataset_df.query("Cluster == @chosen_cluster")
        #playlist_df['id'] = '\"spotify:track:' + big_dataset_df['id'].astype(str) +'\"'
        # print('Recomendação Aqui=======================================')
        # print(playlist_df)
        # rec_id_list = playlist_df['id'].tolist()
        # rec = list_to_string(rec_id_list)

        # print(add_items_playlist(r.json()['access_token'], playlist_json['id'], rec).json())


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

def list_to_string(items):
    string_result = ''
    string_result = ','.join(x for x in items)
    return string_result

#versão anterior considerando qua playlist já vem pronta a partir do kmeans
# def recomendation(kmeans_trained, p_dataframe):
#     lowest = 0
#     average_distance = 0
#     print("--------------------Recommendation")
#     for i in range (80):
#         print('cluster')
#         cluster_label_i = p_dataframe.query("Cluster == @i")
#         print(cluster_label_i)
#         print("labels")
#         labels = kmeans_trained.predict(cluster_label_i.iloc[:,1:7])
#         distances = kmeans_trained.transform(cluster_label_i.iloc[:,1:7])
#         print(labels)
#         quantity = len(cluster_label_i.index)
#         print('quantity')
#         print(quantity)
#         average_distance = distances.sum() / quantity
#         print('average distance')
#         print(average_distance)
#         if i == 0:
#             lowest = distances.sum()
#             cluster = i
#         if(average_distance < lowest):
#             lowest = average_distance
#             cluster = i
#     print('Menor Cluster')
#     print(cluster)
#     print('menor distancia')
#     print(lowest)
#     return cluster

#versão usando clusteres calculados usando heuristicas para ter um numero bom 
def recomendation(kmeans_trained, p_dataframe):
    lowest = 0
    average_distance = 0
    distances_array = []
    print("--------------------Recommendation")
    for i in range (4):
        print('======================')
        cluster_label_i = p_dataframe.query("Cluster == @i")
        print('Cluster')
        print(i)
        print('--')
        labels = kmeans_trained.predict(cluster_label_i.iloc[:,1:9])
        distances = kmeans_trained.transform(cluster_label_i.iloc[:,1:9])
        #print(labels)
        quantity = len(cluster_label_i.index)
        print('Number of tracks')
        print(quantity)
        average_distance = distances.sum() / quantity
        print('average distance')
        print(average_distance)
        if i == 0:
            lowest = distances.sum()
            cluster = i
            distances_array = distances
        if(average_distance < lowest):
            lowest = average_distance
            cluster = i
            distances_array = distances
        print('xxxxxxxxxxxxxxxxxxxxxxxx')

    print('Cluster com menor distância média')
    print(cluster)
    print('menor distancia')
    print(lowest)
    print('distances array')
    print(distances_array)
    df_distances = pd.DataFrame(distances_array, columns = ['D1','D2','D3'])
    df_distances['Total'] = df_distances['D1'] + df_distances['D2'] + df_distances['D3']
    print('distances Dataframe')
    print(df_distances)
    print(cluster)
    df_cluster = p_dataframe.query("Cluster == @cluster").reset_index(drop=True)
    df_cluster.to_csv(r'chosen_cluster_junior.csv', index = None)
    dataset_with_distances = pd.concat([df_cluster, df_distances], axis='columns')
    print(dataset_with_distances)
    chosen_musics_df = dataset_with_distances.sort_values(by=['D2'])
    print(chosen_musics_df)
    print(chosen_musics_df.iloc[:25, :1])
    #print(p_dataframe.query("Cluster == @cluster").reset_index(drop=True))
    return chosen_musics_df.iloc[:25, :1]

# versão sem clusterizar o dataset grande
# def recomendation(kmeans_trained, p_dataframe):
#     labels = kmeans_trained.predict(p_dataframe.iloc[:,1:9])
#     distances = kmeans_trained.transform(p_dataframe.iloc[:,1:9])
#     df_distances = pd.DataFrame(distances, columns = ['D1','D2','D3'])
#     df_distances['Total'] = df_distances['D1'] + df_distances['D2'] + df_distances['D3']
#     print('distances Dataframe')
#     dataset_with_distances = pd.concat([p_dataframe, df_distances], axis='columns')
#     print(dataset_with_distances)
#     chosen_musics_df = dataset_with_distances.sort_values(by=['Total'])
#     print(chosen_musics_df)
#     print(chosen_musics_df.iloc[:25, :1])
#     #print(p_dataframe.query("Cluster == @cluster").reset_index(drop=True))
#     return chosen_musics_df.iloc[:25, :1]
    
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