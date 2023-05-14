from django.urls import path

from . import views

app_name = 'difi'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:search_param>', views.search, name='search'),
    path('stock/', views.get_one, name='get_one'),
    path('addstock', views.add_one, name='add_one'),
]