from django.urls import path

from . import views

app_name = 'difi'

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.search, name='search'),
    # path('search/',views.search, name='search'),
    # path('add/<int:stock_info_id>', views.stock_add, name='stock_add'),
]