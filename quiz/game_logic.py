import random
from movies.models import Film, FilmFrame


def get_random_film():
    return Film.objects.order_by("?").first()


def generate_question(mode="image"):
    film = get_random_film()
    if not film:
        return None

    # Получаем кадры фильма
    frames = FilmFrame.objects.filter(film=film)
    frame_url = None
    if frames.exists():
        frame_url = random.choice(frames).image_url

    # Варианты ответов
    other_films = Film.objects.exclude(id=film.id).order_by("?")[:3]
    options = [film.title] + [f.title for f in other_films]
    random.shuffle(options)

    if mode == "image" and frame_url:
        return {
            "mode": "image",
            "content": frame_url,  # Используем кадр вместо постера
            "options": options,
            "film_id": film.id,
            "correct_answer": film.title
        }
    else:
        # Fallback на постер если нет кадров
        return {
            "mode": "image",
            "content": film.poster_url or "",
            "options": options,
            "film_id": film.id,
            "correct_answer": film.title
        }