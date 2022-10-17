from django.urls import path

from . import views

app_name = 'To_DoZ'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('detail/<int:pk_list>/<int:pk_task>', views.detail, name='detail'),
    path('detail/<int:pk_list>/<int:pk_task>/done', views.done, name='done'),
]