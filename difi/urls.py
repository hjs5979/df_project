from django.urls import path

from . import views

app_name = 'difi'

urlpatterns = [
    path('<str:stock_info_ticker>/', views.search, name='search'),
]