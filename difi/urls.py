from django.urls import path

from . import views

app_name = 'difi'

urlpatterns = [
    path('', views.index, name='index'),
    path('stock', views.select_stock_list, name='select_stock_list'),
    path('stock-value', views.select_stock_value_list, name='select_stock_value_list'),
    path('addstock', views.insert_stock, name='insert_stock'),
    path('deletestock',views.delete_stock, name='delete_stock'),
    path('updatestock',views.update_stock, name='update_stock'),
    path('calcstock',views.calc_stock, name='calc_stock'),
    path('login', views.login, name='login'),
    path('idcheck', views.id_check, name='id_check'),
    path('signup', views.signup, name='signup'),
    path('selectuser', views.select_user, name='select_user'),
    path('checkuser', views.check_user, name='check_user')

]