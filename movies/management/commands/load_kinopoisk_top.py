import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Film, FilmFrame
import time


class Command(BaseCommand):
    help = 'Load top 50 movies from Kinopoisk with frames'

    def handle(self, *args, **options):
        KINOPOISK_API_KEY = getattr(settings, 'KINOPOISK_API_KEY', '')

        if not KINOPOISK_API_KEY:
            self.stderr.write('❌ KINOPOISK_API_KEY not found in settings.py')
            return

        # Загружаем топ фильмов
        movies_url = 'https://api.kinopoisk.dev/v1.4/movie'
        headers = {
            'X-API-KEY': KINOPOISK_API_KEY,
            'Accept': 'application/json'
        }

        params = {
            'page': 7,
            'limit': 50,
            'lists': 'top250',
            'sortField': 'rating.kp',
            'sortType': '-1',
            'selectFields': ['name', 'year', 'poster', 'description', 'persons', 'id', 'rating', 'countries']
        }

        try:
            response = requests.get(movies_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for movie_data in data.get('docs', []):
                try:
                    self.process_movie(movie_data, headers)
                    time.sleep(0.5)  # Пауза между запросами

                except Exception as e:
                    self.stderr.write(f'❌ Error processing movie: {e}')
                    continue

        except Exception as e:
            self.stderr.write(f'❌ API error: {e}')

    def process_movie(self, movie_data, headers):
        """Обрабатываем один фильм и его кадры"""
        kinopoisk_id = movie_data.get('id')
        title = movie_data.get('name', 'Неизвестно')
        year = movie_data.get('year', 0)

        self.stdout.write(f'🎬 Processing: {title} ({year})')

        # Получаем постер
        poster_url = ''
        if movie_data.get('poster'):
            poster_url = movie_data.get('poster', {}).get('url', '')

        # Получаем режиссера и актеров
        director = self.get_director(movie_data.get('persons', []))
        actors = self.get_actors(movie_data.get('persons', []))

        # Создаем или обновляем фильм
        film, created = Film.objects.update_or_create(
            kinopoisk_id=kinopoisk_id,
            defaults={
                'title': title,
                'year': year,
                'poster_url': poster_url,
                'plot': movie_data.get('description', ''),
                'director': director,
                'actors': actors,
                'rating': movie_data.get('rating', {}).get('kp', 0),
                'country': movie_data.get('countries', '').name,
            }
        )

        # Загружаем кадры из фильма
        self.load_frames(film, kinopoisk_id, headers)

        if created:
            self.stdout.write(f'✅ Added: {title}')
        else:
            self.stdout.write(f'⚡ Updated: {title}')

    def load_frames(self, film, kinopoisk_id, headers):
        """Загружаем кадры для фильма"""
        frames_url = f'https://api.kinopoisk.dev/v1.4/image'

        params = {
            'movieId': kinopoisk_id,
            'limit': 10,  # Берем первые 10 кадров
            'type': 'still',  # Кадры из фильма
        }

        try:
            response = requests.get(frames_url, headers=headers, params=params)
            response.raise_for_status()
            frames_data = response.json()

            for frame_data in frames_data.get('docs', [])[:5]:  # Сохраняем первые 5 кадров
                image_url = frame_data.get('url', '')
                if image_url:
                    FilmFrame.objects.get_or_create(
                        film=film,
                        image_url=image_url,
                        defaults={'description': f'Кадр из {film.title}'}
                    )

            self.stdout.write(f'   📸 Loaded {len(frames_data.get("docs", []))} frames')

        except Exception as e:
            self.stderr.write(f'   ❌ Error loading frames: {e}')

    def get_director(self, persons):
        """Получаем режиссера"""
        for person in persons:
            if person.get('profession') == 'режиссеры':
                return person.get('name', 'Неизвестен')
        return 'Неизвестен'

    def get_actors(self, persons):
        """Получаем основных актеров"""
        actors = []
        for person in persons:
            if person.get('profession') == 'актеры' and len(actors) < 3:
                actors.append(person.get('name', ''))
        return ', '.join(actors)