from django.urls import path

from . import views

app_name = 'difi'

urlpatterns = [
    path('', views.index, name='index'),
   
]