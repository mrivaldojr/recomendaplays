from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
from .services import spotify_login_url, get_access_token, get_recent_musics

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    return redirect(spotify_login_url())

def home(request):
    r = get_access_token(request.GET.get('code', ''))
    print(get_recent_musics(r.json()['access_token']).text)
    return render(request, 'home.html')