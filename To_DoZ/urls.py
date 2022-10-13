from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('missing/', views.MissingView.as_view(), name='missing'),
    path('detail/<int:pk_list>/<int:pk_task>', views.detail, name='detail'),
]