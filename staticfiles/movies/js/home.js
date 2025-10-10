    <script>
        // Глобальные переменные
        let currentQuestion = null;
        let currentMode = 'image';
        let stats = {
            correct: 0,
            incorrect: 0,
            streak: 0
        };

        // Инициализация
        document.addEventListener('DOMContentLoaded', function() {
            loadQuestion('image');
            updateStats();
        });


        // Функция для получения CSRF токена
        function getCsrfToken() {
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Функция показа/скрытия элементов
        function toggleElement(id, show) {
            const element = document.getElementById(id);
            if (show) {
                element.classList.remove('hidden');
                element.classList.add('visible');
            } else {
                element.classList.add('hidden');
                element.classList.remove('visible');
            }
        }

        // Загрузка вопроса
        async function loadQuestion(mode = null) {
    if (mode) {
        currentMode = mode;
    }

    try {
        toggleElement('loading', true);
        toggleElement('question-container', false);
        toggleElement('result', false);
        toggleElement('next-btn', false);

        const response = await fetch(`/api/quiz/?mode=${currentMode}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const question = await response.json();

        // ✅ ПРОВЕРЯЕМ, ЧТО ЕСТЬ film_id
        if (!question.film_id) {
            console.error('No film_id in response:', question);
            throw new Error('Invalid question data: missing film_id');
        }

        currentQuestion = question;
        console.log('Current question:', currentQuestion); // ✅ ДЛЯ ОТЛАДКИ
        renderQuestion(question);

        toggleElement('loading', false);
        toggleElement('question-container', true);

    } catch (error) {
        console.error('Ошибка загрузки вопроса:', error);
        toggleElement('loading', false);
        alert('Не удалось загрузить вопрос: ' + error.message);
    }
}

        // Отображение вопроса
        function renderQuestion(question) {
            const contentDiv = document.getElementById('question-content');
            const optionsDiv = document.getElementById('options');

            // Очищаем предыдущий вопрос
            contentDiv.innerHTML = '';
            optionsDiv.innerHTML = '';

            // Отображаем контент в зависимости от типа вопроса
            if (question.mode === 'image') {
                contentDiv.innerHTML = `
                    <div style="text-align: center;">
                        <img src="${question.content}" alt="Кадр из фильма" class="question-image">
                        <p style="font-size: 18px; margin-top: 15px;">Какой это фильм?</p>
                    </div>
                `;
            } else if (question.mode === 'quote') {
                contentDiv.innerHTML = `
                    <div style="text-align: center;">
                        <div style="font-style: italic; font-size: 20px; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                            "${question.content}"
                        </div>
                        <p style="font-size: 18px;">Из какого это фильма/сериала?</p>
                    </div>
                `;
            } else if (question.mode === 'actor') {
                contentDiv.innerHTML = `
                    <div style="text-align: center;">
                        <p style="font-size: 18px; margin-bottom: 20px;">Какой фильм с участием этих актеров?</p>
                        <p style="font-size: 20px; font-weight: bold;">${question.content}</p>
                    </div>
                `;
            }

            // Создаем кнопки вариантов ответов
            if (question.options && question.options.length > 0) {
                question.options.forEach(option => {
                    const button = document.createElement('button');
                    button.className = 'option-btn';
                    button.textContent = option;
                    button.onclick = () => checkAnswer(option);
                    optionsDiv.appendChild(button);
                });
            } else {
                optionsDiv.innerHTML = '<p>Нет вариантов ответа</p>';
            }
        }

        // Проверка ответа
        async function checkAnswer(userAnswer) {
    try {
        console.log('Checking answer for question:', currentQuestion); // ✅ ОТЛАДКА

        if (!currentQuestion || !currentQuestion.film_id) {
            throw new Error('Нет данных о текущем вопросе. film_id: ' + (currentQuestion ? currentQuestion.film_id : 'undefined'));
        }

        const response = await fetch('/api/answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                film_id: currentQuestion.film_id,
                answer: userAnswer
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        showResult(result, userAnswer);

    } catch (error) {
        console.error('Ошибка проверки ответа:', error);
        alert('Ошибка при проверке ответа: ' + error.message);
    }
}

        // Показать результат
        function showResult(result, userAnswer) {
            const resultDiv = document.getElementById('result');
            const nextBtn = document.getElementById('next-btn');

            // Блокируем кнопки после ответа
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.disabled = true;
                if (btn.textContent === result.right_answer) {
                    btn.classList.add('correct');
                } else if (btn.textContent === userAnswer && !result.correct) {
                    btn.classList.add('incorrect');
                }
            });

            // Показываем результат
            resultDiv.innerHTML = `
                <h2 style="color: ${result.correct ? '#4CAF50' : '#f44336'};">
                    ${result.correct ? '✅ Правильно!' : '❌ Неправильно!'}
                </h2>
                ${result.correct ? '' : `<p style="font-size: 18px;">Правильный ответ: <strong>${result.right_answer}</strong></p>`}
                ${result.poster ? `<img src="${result.poster}" style="max-width: 200px; margin-top: 15px; border-radius: 5px;">` : ''}
            `;

            toggleElement('result', true);
            toggleElement('next-btn', true);
        }

        // Загружаем первый вопрос при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            loadQuestion('image');
        });

        // Обработка ошибок
        window.addEventListener('error', function(e) {
            console.error('Global error:', e.error);
        });
    </script>