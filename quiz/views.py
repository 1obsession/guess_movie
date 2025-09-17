from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.views.decorators.http import require_http_methods
from movies.models import Film
from quiz.game_logic import generate_question


@csrf_exempt
@require_http_methods(["GET"])
def quiz_api(request):
    """API для получения вопросов"""
    mode = request.GET.get('mode', 'image')
    try:
        question_data = generate_question(mode)

        if not question_data:
            return JsonResponse({'error': 'No films in database'}, status=404)

        return JsonResponse(question_data)  # ✅ Просто возвращаем весь объект

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def answer_api(request):
    """API для проверки ответов"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            film_id = data.get('film_id')
            user_answer = data.get('answer')

            # Ваша логика проверки
            film = Film.objects.get(id=film_id)
            is_correct = (user_answer.lower() == film.title.lower())

            return JsonResponse({
                'correct': is_correct,
                'right_answer': film.title,
                'poster': film.poster_url or ''
            })

        except Film.DoesNotExist:
            return JsonResponse({'error': 'Film not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return None