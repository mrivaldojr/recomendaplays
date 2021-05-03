from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
import requests
from .services import spotify_login_url, get_access_token, get_recent_musics

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):
    r = get_access_token(request.GET.get('code', ''))
    #print(get_recent_musics(r.json()['access_token']).text)
    json_response = get_recent_musics(r.json()['access_token'])
    print(get_music_list(json_response))
    return render(request, 'home.html', {'music_list':get_music_list(json_response)})

def get_music_list(json_response):
    musics = json_response.json()
    music_list = []
    for i in range(len(musics['items'])):
        music_list.append(musics['items'][i])
    return music_list