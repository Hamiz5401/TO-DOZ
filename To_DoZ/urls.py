from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'To_DoZ'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('detail/<str:subject>/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('detail/create', views.TaskCreateView.as_view(), name='create'),
    path('detail/<int:pk_task>/done', views.done, name='done'),
]