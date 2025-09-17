from django.shortcuts import render
from django.views.generic import ListView

from .tasks import fetch_popular_movies


class MovieHomeView(ListView):
    template_name = 'movies/home.html'
    context_object_name = 'movies'
    title_page = 'Home'

    def get_queryset(self):
        return