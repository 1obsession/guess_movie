import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Film
import time


class Command(BaseCommand):
    help = 'Load movies from OMDb API'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of movies to load')

    def handle(self, *args, **options):
        count = options['count']
        api_key = settings.OMDB_API_KEY

        # Популярные фильмы для поиска
        popular_movies = [
            "The Shawshank Redemption", "The Godfather", "The Dark Knight",
            "Pulp Fiction", "Fight Club", "Forrest Gump", "Inception",
            "The Matrix", "Goodfellas", "The Silence of the Lambs",
            "Star Wars", "The Lord of the Rings", "Harry Potter",
            "Avatar", "Titanic", "Jurassic Park", "The Avengers",
            "Interstellar", "Gladiator", "The Departed", "Whiplash",
            "Parasite", "Joker", "The Social Network", "La La Land",
            "Mad Max: Fury Road", "Get Out", "Black Panther", "Django Unchained",
            "The Wolf of Wall Street", "Gravity", "The Revenant", "Birdman",
            "12 Years a Slave", "Argo", "The Artist", "The King's Speech",
            "Slumdog Millionaire", "No Country for Old Men", "The Departed",
            "Crash", "Million Dollar Baby", "The Lord of the Rings: The Return of the King",
            "Chicago", "A Beautiful Mind", "Gladiator", "American Beauty",
            "Shakespeare in Love", "Titanic", "The English Patient",
            "Braveheart", "Forrest Gump", "Schindler's List", "Unforgiven",
            "The Silence of the Lambs", "Dances with Wolves", "Driving Miss Daisy",
            "Rain Man", "The Last Emperor", "Platoon", "Out of Africa",
            "Amadeus", "Terms of Endearment", "Gandhi", "Chariots of Fire",
            "Ordinary People", "Kramer vs. Kramer", "The Deer Hunter",
            "Annie Hall", "Rocky", "The Sting", "The Godfather Part II",
            "One Flew Over the Cuckoo's Nest", "The Godfather", "Patton",
            "Midnight Cowboy", "Oliver!", "In the Heat of the Night",
            "A Man for All Seasons", "The Sound of Music", "My Fair Lady",
            "Tom Jones", "Lawrence of Arabia", "West Side Story", "The Apartment",
            "Ben-Hur", "Gigi", "The Bridge on the River Kwai", "Around the World in 80 Days",
            "Marty", "On the Waterfront", "From Here to Eternity", "The Greatest Show on Earth",
            "An American in Paris", "All About Eve", "All the King's Men", "Hamlet",
            "Gentleman's Agreement", "The Best Years of Our Lives", "The Lost Weekend",
            "Going My Way", "Casablanca", "Mrs. Miniver", "How Green Was My Valley",
            "Rebecca", "Gone with the Wind", "You Can't Take It with You", "The Life of Emile Zola",
            "The Great Ziegfeld", "Mutiny on the Bounty", "It Happened One Night",
            "Cavalcade", "Grand Hotel", "Cimarron", "All Quiet on the Western Front",
            "The Broadway Melody", "Wings"
        ]

        loaded_count = 0

        for movie_title in popular_movies[:count]:
            try:
                # Делаем запрос к OMDb API
                url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
                response = requests.get(url)
                data = response.json()

                if data.get('Response') == 'True':
                    # Создаем или обновляем фильм
                    film, created = Film.objects.update_or_create(
                        title=data['Title'],
                        defaults={
                            'year': int(data['Year'][:4]) if data['Year'] != 'N/A' else None,
                            'poster_url': data['Poster'] if data['Poster'] != 'N/A' else '',
                            'plot': data['Plot'] if data['Plot'] != 'N/A' else '',
                            'director': data['Director'] if data['Director'] != 'N/A' else '',
                            'actors': data['Actors'] if data['Actors'] != 'N/A' else '',
                            'imdb_id': data['imdbID'] if data['imdbID'] != 'N/A' else ''
                        }
                    )

                    if created:
                        self.stdout.write(f'Added: {film.title} ({film.year})')
                        loaded_count += 1
                    else:
                        self.stdout.write(f'Updated: {film.title}')

                    # Пауза чтобы не превысить лимит API
                    time.sleep(0.1)

            except Exception as e:
                self.stderr.write(f'Error loading {movie_title}: {e}')
                continue

        self.stdout.write(f'Successfully loaded {loaded_count} movies')