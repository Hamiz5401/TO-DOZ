from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'To_DoZ'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('table/', views.TableView.as_view(), name='table'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('detail/<int:pk_list>/<int:pk>', views.DetailView.as_view(), name='detail'),
    
    path('create', views.ListCreateView.as_view(), name='create_list'),
    path('<int:pk>/update', views.ListUpdateView.as_view(), name='update_list'),
    path('<int:pk>/delete', views.ListDeleteView.as_view(), name='delete_list'),
    
    path('detail/<int:pk_list>/create', views.TaskCreateView.as_view(), name='create_task'),
    path('detail/<int:pk_list>/<int:pk>/update', views.TaskUpdateView.as_view(), name='update_task'),
    path('detail/<int:pk_list>/<int:pk>/delete', views.TaskDeleteView.as_view(), name='delete_task'),
    
    path('detail/<int:pk_task>/done', views.done, name='done'),
    path('get_classroom_data', views.create_classroom_data, name='get_data'),

    path('discord_create_form/', views.DiscordCreateView.as_view(), name='discord_create_form'),
    path('discord_update_form/', views.DiscordUpdateView.as_view(), name='discord_update_form')
]