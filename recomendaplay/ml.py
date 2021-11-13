import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os.path
import requests, json

def read_dataset():
    dados = pd.read_csv("recent_musics.csv")
    return dados

def kmeans_distances(dados):
    x = dados.iloc[:,1:5]
    print(x)
    kmeans = KMeans(n_clusters=3, init='random')
    kmeans.fit(x)
    print("Cluster Centers")
    print(kmeans.cluster_centers_)

def starndarlize_data(dataset):
    scaler = StandardScaler()
    std_data = scaler.fit_transform(dataset)
    print(std_data)