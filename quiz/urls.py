from django.urls import path
from . import views

urlpatterns = [
    # Главная страница с викториной
    #path('', views.quiz_page, name='quiz-page'),

    # API для получения вопросов
    path('api/quiz/', views.quiz_api, name='quiz-api'),

    # API для проверки ответов
    path('api/answer/', views.answer_api, name='answer-api'),

    # Дополнительные пути (если нужно)
    #path('api/stats/', views.stats_api, name='stats-api'),
]