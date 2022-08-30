import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os.path
import requests, json

def read_dataset(file_name):
    dados = pd.read_csv(file_name)
    return dados

def kmeans_distances(dados):
    x = dados.iloc[:,1:5]
    #print(x)
    kmeans = KMeans(n_clusters=3, init='random')
    kmeans.fit(x)
    #print("Cluster Centers")
    #print(kmeans.cluster_centers_)

def kmeans_dataset(data, nclusters):
    #x = data.iloc[:,1:13]
    x = data.iloc[:,1:7]
    kmeans = KMeans(n_clusters=nclusters, init='random')
    kmeans.fit(x)
    print('KMeans Inertia')
    print(kmeans.inertia_)
    print("Final locations of the centroid")
    print(kmeans.cluster_centers_)
    print("The number of iterations required to converge")
    print(kmeans.n_iter_)
    print("Labels")
    label = kmeans.fit_predict(x)
    print(kmeans.labels_[:39])
    print('label')
    print(label)
    x['Cluster'] = label
    print("Cluster Columns -------------------------------")
    if nclusters == 3:
        x.to_csv(r'musicas_usuarios_labeled.csv', index = None)
    else:
        x.to_csv(r'dataset_labeled.csv', index = None)
    print(x)
    filtered_label0 = x[label == 0]
    return kmeans
    #print(filtered_label0)

def starndarlize_data(dataset):
    scaler = StandardScaler()
    std_data = scaler.fit_transform(dataset)
 
def dataset_pca(dataset):
    #data = starndarlize_data(dataset)
    scaler = StandardScaler()
    std_data = scaler.fit_transform(dataset)
    pca = PCA()
    pca.fit(std_data)
    evr = pca.explained_variance_ratio_
    #print("PCA ----------------------------")
    #print(evr)
    #print(evr.cumsum())

def standarlize_dataset(p_dataframe):
    scaler = StandardScaler()
    return scaler.fit_transform(p_dataframe)