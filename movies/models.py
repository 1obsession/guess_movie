from django.db import models
from rest_framework.authtoken.admin import User

from django.db import models


class Film(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    poster_url = models.URLField(blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=100, blank=True, null=True)
    actors = models.CharField(max_length=200, blank=True, null=True)
    imdb_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    kinopoisk_id = models.IntegerField(unique=True, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.year})"


class FilmFrame(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='frames')
    image_url = models.URLField()
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Frame from {self.film.title}"

class Question(models.Model):
    MODE_CHOICES = [
        ('image', 'По кадру'),
        ('sound', 'По саундтреку'),
        ('quote', 'По цитате'),
        ('actor', 'По актеру'),
    ]

    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    content = models.TextField()  # URL изображения/аудио или текст цитаты
    options = models.JSONField()  # Варианты ответов (если нужны)


class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    current_question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL)