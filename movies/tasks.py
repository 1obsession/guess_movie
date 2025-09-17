import requests
from django.conf import settings
from .models import Film

OMDB_API_KEY = settings.OMDB_API_KEY # Добавьте ключ в settings.py


def fetch_movie_by_title(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        Film.objects.update_or_create(
            imdb_id=response["imdbID"],
            defaults={
                "title": response["Title"],
                "year": int(response["Year"][:4]) if response["Year"] else None,
                "poster_url": response["Poster"] if response["Poster"] != "N/A" else None,
                "plot": response["Plot"],
                "director": response["Director"],
                "actors": response["Actors"],
            }
        )
    return response


# Пример: Загрузка топ-10 фильмов
def fetch_popular_movies():
    popular_titles = ["The Godfather", "Inception", "Pulp Fiction", "The Dark Knight", "Fight Club"]
    for title in popular_titles:
        fetch_movie_by_title(title)