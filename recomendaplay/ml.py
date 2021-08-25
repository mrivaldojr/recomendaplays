import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os.path


def read_dataset():
    # wcss = []
    # dados = pd.read_csv("dataSpotify.csv")
    dados = pd.read_csv("recent_musics.csv")
    print(dados.head())