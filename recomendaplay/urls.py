from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('actionUrl', views.login),
    path('home', views.home)
]