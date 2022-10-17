from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'To_DoZ'
urlpatterns = [
    path('', login_required(views.HomeView.as_view()), name='home'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('detail/<int:pk_list>/<int:pk_task>', views.detail, name='detail'),
    path('detail/<int:pk_list>/<int:pk_task>/done', views.done, name='done'),
]