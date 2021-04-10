from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests, base64

def index(request):
    return render(request, 'sign_in.html', {})

def login(request):
    client_id = "3141a4fb805945dbbd4aa41d33696b8f"
    redirect_url = "http://localhost:8000/home"
    url = "https://accounts.spotify.com/authorize?client_id="+client_id+"&response_type=code&redirect_uri="+redirect_url+"&scope=user-read-private%20user-read-email%20user-read-recently-played&state=34fFs29kd09"
    return redirect(url)

def home(request):
    r = get_access_token(request.GET.get('code', ''))
    print(r.status_code)
    print(r.json()['access_token'])
    print('------------------------------------------------------------------------')
    print(get_recent_musics(r.json()['access_token']).text)
    return render(request, 'home.html')

def get_access_token(code):
    url = 'https://accounts.spotify.com/api/token'
    payload = {'grant_type': 'authorization_code', 
        'code': code, 
        'redirect_uri':'http://localhost:8000/home'
        }
    headers = {'Authorization': 'Basic '+get_base64_id()}
    return requests.post(url, data=payload, headers=headers)

def get_base64_id():
    client_id = "3141a4fb805945dbbd4aa41d33696b8f"
    client_secret = "567f3106d6cd4193b38e8fd4c81074da"
    client_key = client_id+":"+client_secret
    key_bytes = client_key.encode('ascii')
    base64_bytes = base64.b64encode(key_bytes)
    return base64_bytes.decode('ascii')

def get_recent_musics(token):
    url = 'https://api.spotify.com/v1/me/player/recently-played'
    headers = {'Authorization': 'Bearer '+token}
    return requests.get(url, headers=headers)