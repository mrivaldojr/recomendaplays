from locale import normalize
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import pandas as pd
import random
import requests, json
from .ml import dataset_pca, read_dataset, standarlize_dataset, kmeans_dataset, normalize_dataset
from .services import spotify_login_url, get_access_token, get_recent_musics, get_recent_musics_features, get_user, create_playlist, add_items_playlist, get_top

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):

    r = get_access_token(request.GET.get('code', ''))

    if r.status_code == 200:
        # json com as músicas ouvidas recentemente
        json_response = get_recent_musics(r.json()['access_token'])
        user = get_user(r.json()['access_token']).json()
        print('User----------------------------')
        print(user['id'])

        #pega top musicas e extai os gêneros 
        top_musics = get_top('artists',r.json()['access_token'])
        print(top_musics.json())
        print('-------')
        user_top_genres = get_artist_genre(top_musics.json()['items'])
        #user_genres_counts = {item:user_top_genres.count(item) for item in user_top_genres}
        user_genres_counts = pd.Series(user_top_genres).value_counts().nlargest(5)
        top5_genres = user_genres_counts.index.values.tolist()
        print(top5_genres)
        print('user top genres')
        print(user_top_genres)
        print(user_genres_counts)

        print('----------------------------------')
        # Create a playlist on spotify account
        # print('Create Playlist--------------------')
        # playlist_json = create_playlist(user['id'],r.json()['access_token'], 'Created via recsys').json()
        # print(playlist_json)
        # print(playlist_json['id'])

        # # read big dataset previously clustered
        # #big_dataset_df = read_dataset('big_dataset_labeled_5clusters.csv')
        # #big_dataset_df = read_dataset('dataset_9features_2cluster_labeled.csv')
        # #big_dataset_df = read_dataset('dataset_9features_4cluster_labeled.csv')
        big_dataset_df_80c = read_dataset('dataset_6features_80cluster_labeled.csv')
        big_dataset_df_6c = read_dataset('dataset_6features_3cluster_labeled.csv')

        # recupera ids para chamar a API de features
        ids = get_music_ids(json_response)
        features = get_recent_musics_features(r.json()['access_token'], ids).json()
        json_str = features
        info_str = json.dumps(features)
        info = json.loads(info_str)

        df = pd.json_normalize(info['audio_features'])
        
        ####features fran  artigo
        df_completo = df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']]
        ds_columns_to_normalize = df_completo.iloc[:, 1:7]
        column_names = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']

        # ####features fran
        # df_completo = df[['id','speechiness','liveness','energy','danceability','instrumentalness','loudness','tempo']]
        # ds_columns_to_normalize = df_completo.iloc[:, 1:8]
        # column_names = ['speechiness','liveness','energy','danceability','instrumentalness','loudness','tempo']
        
        # #####8features
        # # df_completo = df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness','tempo', 'valence']]
        # # ds_columns_to_normalize = df_completo.iloc[:, 1:9]
        # # column_names = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness', 'tempo', 'valence']

        # ######6features
        # #df_completo = df[['id','instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']]
        # #ds_columns_to_normalize = df_completo.iloc[:, 1:7]
        # #column_names = ['instrumentalness','energy','loudness', 'danceability', 'liveness', 'speechiness']
        
        #salva a coluna com os ids
        ds_ids = df_completo.iloc[:, 0:1]

        # ######12features   
        # #df_completo = df[['id','instrumentalness','energy','loudness','tempo', 'acousticness', 'danceability', 'liveness', 'key', 'mode', 'speechiness', 'valence', 'time_signature']]
        # #ds_columns_to_normalize = df_completo.iloc[:, 1:13]
        # #column_names = ['energy','danceability','acousticness','instrumentalness','key','liveness','loudness','mode','speechiness','tempo','time_signature','valence']
        
        #tratamento dos dados do usuário antes de fazer o modelo de clusters
        dataset_csv_stand = normalize_dataset(ds_columns_to_normalize)
        dataset_csv_stand_df = pd.DataFrame(dataset_csv_stand, columns = column_names)
        final_stand_dataset = pd.concat([ds_ids, dataset_csv_stand_df], axis='columns')

        # recomendation with genres
        trained_kmeans = kmeans_dataset(final_stand_dataset.iloc[:,0:1], final_stand_dataset.iloc[:,1:7], 3)
        chosen_cluster = random.choice(['D1','D2','D3'])

        ##################recommendation using all clusters sem genres
        print('#recommendation using all clusters (6clusters)')
        recomendation_no_genres_distances(trained_kmeans, big_dataset_df_6c, 'Total', 3)

        ##################recomendation using one cluster sem genres
        print('#recomendation using one cluster (6 clusters)')       
        recomendation_no_genres_distances(trained_kmeans, big_dataset_df_6c, chosen_cluster, 3)
        
        ##################recomendation using one cluster using genres
        # print('#recomendation using one cluster (6 clusters)')       
        # recomendation_with_genres_distances(trained_kmeans, big_dataset_df_6c, top5_genres, chosen_cluster, 3)

        ##################recommendation using all clusters using genres
        # print('#recommendation using all clusters (6clusters)')
        # recomendation_with_genres_distances(trained_kmeans, big_dataset_df_6c, top5_genres, 'Total', 3)

        #################recommendation using all clusters (80clusters)
        # print('#recommendation using all clusters (80clusters)')
        # recomendation_80c(trained_kmeans, big_dataset_df_80c, 'Total')

        #################recommendation using one of the clusters (80clusters)
        # print('#recommendation using all clusters (80clusters)')
        # recomendation_80c(trained_kmeans, big_dataset_df_80c, chosen_cluster)

        # chosen_cluster = recomendation(trained_kmeans, big_dataset_df)
        # #chosen_ids = recomendation(trained_kmeans, big_dataset_df)
        # # chosen_ids['id'] = '\"spotify:track:' + big_dataset_df['id'].astype(str) +'\"'
        # # print(chosen_ids)
        # # rec_id_list = chosen_ids['id'].tolist()
        # # rec = list_to_string(rec_id_list)
        # # print(add_items_playlist(r.json()['access_token'], playlist_json['id'], rec).json())

        # # #playlist_df =  big_dataset_df.query("Cluster == @chosen_cluster")
        # # #playlist_df['id'] = '\"spotify:track:' + big_dataset_df['id'].astype(str) +'\"'
        # # # print('Recomendação Aqui=======================================')
        # # # print(playlist_df)
        # # # rec_id_list = playlist_df['id'].tolist()
        # # # rec = list_to_string(rec_id_list)

        # # # print(add_items_playlist(r.json()['access_token'], playlist_json['id'], rec).json())

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

def get_artist_genre(top_artists_json):
    genres = []
    for i in range(len(top_artists_json)):
        genre = top_artists_json[i]['genres']
        if len(genre)>0:
            for g in genre:
                if 'rock' in g:
                    genres.append('rock')
                if 'metal' in g:
                    genres.append('metal')
                if 'axe' in g:
                    genres.append('axe')
                if 'pagode' in g:
                    genres.append('pagode')
                if 'edm' in g:
                    genres.append('edm')
                if 'funk' in g:
                    genres.append('funk')
                if 'rap' in g:
                    genres.append('rap')
                if 'hip hop' in g:
                    genres.append('hip hop')
                if 'jazz' in g:
                    genres.append('jazz')
                if 'pagode baiano' in g:
                    genres.append('pagode baiano')
                if 'sertanejo' in g:
                    genres.append('sertanejo')
                if 'pop' in g:
                    genres.append('pop')
    return genres

def recomendation_with_genres_distances(kmeans_trained, p_dataframe, genres, distance_to_sort, n_cluster):
    print('DISTANCE TO SORT')
    print(distance_to_sort)
    lowest = 0
    average_distance = 0
    distances_array = []
    print("--------------------Recommendation")
    for i in range (n_cluster):
        print('======================')
        cluster_label_i = p_dataframe.query("Cluster == @i")
        print('Cluster')
        print(i)
        print('--')
        # decide para quais clusters 
        labels = kmeans_trained.predict(cluster_label_i.iloc[:,4:10])
        # retorna a matriz de distâncias para de cada item para cada um dos centroides
        distances = kmeans_trained.transform(cluster_label_i.iloc[:,4:10])
        quantity = len(cluster_label_i.index)
        # transforma a matriz de distancias em dataframe para facilitar o cálculo
        df_distances_ = pd.DataFrame(distances, columns = ['D1','D2','D3'])
        df_distances_['Total'] = df_distances_['D1'] + df_distances_['D2'] + df_distances_['D3']
        # soma todos os valores do cluster (D1, D2, D3 ou a soma dos 3) escolhido 
        distance_sum = df_distances_[distance_to_sort].sum()
        print('Number of tracks')
        print(quantity)
        print('Distance SUM')
        print(distance_sum)
        average_distance = distance_sum / quantity
        print('average distance')
        print(average_distance)
        if i == 0:
            df_distances = df_distances_
            lowest = average_distance
            cluster = i
            distances_array = distances
        if(average_distance < lowest):
            df_distances = df_distances_
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
    df_cluster = p_dataframe.query("Cluster == @cluster").reset_index(drop=True)
    dataset_with_distances = pd.concat([df_cluster, df_distances], axis='columns')
    print(dataset_with_distances)
    chosen_musics_df = dataset_with_distances.sort_values(by=[distance_to_sort])
    chosen_musics_genre = chosen_musics_df.loc[chosen_musics_df['genres'].isin(genres)]
    print(chosen_musics_genre.iloc[:25, 0:4])
    return chosen_musics_genre.iloc[:25, :1]

#versão usando clusteres calculados usando heuristicas para ter um numero bom 
def recomendation_no_genres_distances(kmeans_trained, p_dataframe, distance_to_sort, n_cluster):
    print('DISTANCE TO SORT')
    print(distance_to_sort)
    lowest = 0
    average_distance = 0
    distances_array = []
    print("--------------------Recommendation")
    for i in range (n_cluster):
        print('======================')
        cluster_label_i = p_dataframe.query("Cluster == @i")
        print('Cluster')
        print(i)
        print('--')
        # decide para quais clusters 
        labels = kmeans_trained.predict(cluster_label_i.iloc[:,4:10])
        # retorna a matriz de distâncias para de cada item para cada um dos centroides
        distances = kmeans_trained.transform(cluster_label_i.iloc[:,4:10])
        quantity = len(cluster_label_i.index)
        # transforma a matriz de distancias em dataframe para facilitar o cálculo
        df_distances_ = pd.DataFrame(distances, columns = ['D1','D2','D3'])
        df_distances_['Total'] = df_distances_['D1'] + df_distances_['D2'] + df_distances_['D3']
        # soma todos os valores do cluster (D1, D2, D3 ou a soma dos 3) escolhido 
        distance_sum = df_distances_[distance_to_sort].sum()
        print('Number of tracks')
        print(quantity)
        print('Distance SUM')
        print(distance_sum)
        average_distance = distance_sum / quantity
        print('average distance')
        print(average_distance)
        if i == 0:
            df_distances = df_distances_
            lowest = average_distance
            cluster = i
            distances_array = distances
        if(average_distance < lowest):
            df_distances = df_distances_
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
    df_cluster = p_dataframe.query("Cluster == @cluster").reset_index(drop=True)
    dataset_with_distances = pd.concat([df_cluster, df_distances], axis='columns')
    print(dataset_with_distances)
    chosen_musics_df = dataset_with_distances.sort_values(by=[distance_to_sort])
    print(chosen_musics_df.iloc[:25, 0:4])
    return chosen_musics_df.iloc[:25, :1]

#versão do primeiro trabalho, considerando 80 clusters
def recomendation_80c(kmeans_trained, p_dataframe, distance_to_sort):
    lowest = 0
    average_distance = 0
    print("Recommendation")
    for i in range (80):
        print('cluster')
        print(i)
        cluster_label_i = p_dataframe.query("Cluster == @i")
        print(cluster_label_i.iloc[:,:10])
        print("labels")
        labels = kmeans_trained.predict(cluster_label_i.iloc[:,4:10])
        distances = kmeans_trained.transform(cluster_label_i.iloc[:,4:10])
        # transforma a matriz de distancias em dataframe para facilitar o cálculo
        df_distances_ = pd.DataFrame(distances, columns = ['D1','D2','D3'])
        df_distances_['Total'] = df_distances_['D1'] + df_distances_['D2'] + df_distances_['D3']
        # soma todos os valores do cluster (D1, D2, D3 ou a soma dos 3) escolhido 
        distance_sum = df_distances_[distance_to_sort].sum()
        print(labels)
        quantity = len(cluster_label_i.index)
        print('quantity')
        print(quantity)
        print('Sum Distances')
        print(distance_sum)
        average_distance = distance_sum / quantity
        print('average distance')
        print(average_distance)
        if i == 0:
            df_distances = df_distances_
            lowest = average_distance
            cluster = i
            distances_array = distances
        if(average_distance < lowest):
            df_distances = df_distances_
            lowest = average_distance
            cluster = i
            distances_array = distances
    print('Menor Cluster')
    print(cluster)
    print('menor distancia')
    print(lowest)
    return cluster
    
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