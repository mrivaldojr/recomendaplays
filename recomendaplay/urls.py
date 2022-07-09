from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login_spotify', views.login),
    path('home', views.home)
]