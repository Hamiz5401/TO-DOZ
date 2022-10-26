from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'To_DoZ'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('create', views.ListCreateView.as_view(), name='create_list'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('detail/<int:pk_list>/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('detail/<int:pk_list>/create', views.TaskCreateView.as_view(), name='create_task'),
    path('detail/<int:pk_list>/<int:pk>/update', views.TaskUpdateView.as_view(), name='update_task'),
    path('detail/<int:pk_task>/done', views.done, name='done'),
]