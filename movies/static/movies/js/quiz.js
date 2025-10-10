console.log('🎬 quiz.js начал загружаться...');

// Простая проверка что файл выполняется
try {
    console.log('✅ quiz.js выполняется!');
    console.log('📁 URL файла:', document.currentScript?.src || 'неизвестно');
} catch (error) {
    console.error('❌ Ошибка в начале файла:', error);
}

// Глобальные переменные
let currentQuestion = null;
let currentMode = 'image';
let stats = {
    correct: 0,
    incorrect: 0,
    streak: 0
};

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ quiz.js загружен!');
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
    if (element) {
        if (show) {
            element.classList.remove('hidden');
        } else {
            element.classList.add('hidden');
        }
    }
}

// Обновление статистики
function updateStats() {
    const correctEl = document.getElementById('correct-count');
    const streakEl = document.getElementById('streak-count');
    const totalEl = document.getElementById('total-count');

    if (correctEl) correctEl.textContent = stats.correct;
    if (streakEl) streakEl.textContent = stats.streak;
    if (totalEl) totalEl.textContent = stats.correct + stats.incorrect;
}

// Загрузка вопроса
async function loadQuestion(mode = null, clickedElement = null) {
    if (mode) {
        currentMode = mode;
        // Обновляем активную кнопку режима
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Если кнопка была нажата - активируем её
        if (clickedElement) {
            clickedElement.classList.add('active');
        } else {
            // Иначе активируем кнопку по умолчанию
            const defaultBtn = document.querySelector('.mode-btn[onclick*="image"]');
            if (defaultBtn) defaultBtn.classList.add('active');
        }
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

        if (!question.film_id) {
            throw new Error('Invalid question data: missing film_id');
        }

        currentQuestion = question;
        console.log('Current question:', currentQuestion);
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

    if (!contentDiv || !optionsDiv) {
        console.error('Не найдены элементы вопроса');
        return;
    }

    contentDiv.innerHTML = '';
    optionsDiv.innerHTML = '';

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

    if (question.options && question.options.length > 0) {
        question.options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.textContent = option;
            button.onclick = () => checkAnswer(option);
            optionsDiv.appendChild(button);
        });
    }
}

// Проверка ответа
async function checkAnswer(userAnswer) {
    try {
        console.log('Checking answer for question:', currentQuestion);

        if (!currentQuestion || !currentQuestion.film_id) {
            throw new Error('Нет данных о текущем вопросе');
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
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const resultPoster = document.getElementById('result-poster');
    const nextBtn = document.getElementById('next-btn');

    if (!resultDiv || !resultTitle || !resultMessage) {
        console.error('Не найдены элементы результата');
        return;
    }

    // Блокируем кнопки после ответа
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.disabled = true;
        if (btn.textContent === result.right_answer) {
            btn.classList.add('correct');
        } else if (btn.textContent === userAnswer && !result.correct) {
            btn.classList.add('incorrect');
        }
    });

    // Обновляем статистику
    if (result.correct) {
        stats.correct++;
        stats.streak++;
    } else {
        stats.incorrect++;
        stats.streak = 0;
    }
    updateStats();

    // Показываем результат
    resultTitle.textContent = result.correct ? '✅ Правильно!' : '❌ Неправильно!';
    resultTitle.style.color = result.correct ? '#4CAF50' : '#f44336';

    if (!result.correct) {
        resultMessage.innerHTML = `Правильный ответ: <strong>${result.right_answer}</strong>`;
    } else {
        resultMessage.innerHTML = 'Отличная работа! 🎉';
    }

    if (result.poster) {
        resultPoster.src = result.poster;
        resultPoster.style.display = 'block';
        resultPoster.alt = `Постер фильма ${result.right_answer}`;
    } else {
        resultPoster.style.display = 'none';
    }

    toggleElement('result', true);
    toggleElement('next-btn', true);
}

// Сброс игры
function resetGame() {
    stats = {
        correct: 0,
        incorrect: 0,
        streak: 0
    };
    updateStats();
    loadQuestion('image');
}

// Глобальная обработка ошибок
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});