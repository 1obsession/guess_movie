from django.urls import path

from . import views

urlpatterns = [
    path('', views.MovieHomeView.as_view(), name='home'),
]