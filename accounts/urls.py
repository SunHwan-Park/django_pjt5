from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('add_genre/', views.add_genre, name='add_genre'),
    path('delete_genre/', views.delete_genre, name='delete_genre'),
]