document.getElementById('generate-audio').addEventListener('click', async () => {
    const button = document.getElementById('generate-audio');
    const textInput = document.getElementById('text-input').value.trim();
    const generatedText = document.getElementById('generated-text');
    const audioPlayer = document.getElementById('audio-player');
    const jsonTimestamps = document.getElementById('json-timestamps');
    const resultBlock = document.getElementById('result-block');

    // Скрываем элементы до получения ответа
    audioPlayer.classList.add('hidden');
    resultBlock.classList.add('hidden');

    if (!textInput) {
        alert('Пожалуйста, введите текст для синтеза');
        return;
    }

    // Disable the button и изменим текст
    button.disabled = true;
    button.textContent = "Загрузка...";

    try {
        // Отправляем запрос на сервер для синтеза речи
        const response = await fetch('/synthesize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: textInput }),
        });

        if (!response.ok) {
            throw new Error('Ошибка при генерации аудио.');
        }

        const result = await response.json();

        // Отображаем сгенерированный текст
        // Предполагается, что result.original_text содержит оригинальный текст
        // и result.words содержит массив с таймингами
        generatedText.innerHTML = result.original_text; // Временно отображаем исходный текст

        // Отображаем JSON тайминговую разметку
        jsonTimestamps.textContent = JSON.stringify(result.words, null, 2);

        // Устанавливаем источник аудио
        audioPlayer.src = result.audio_url;

        // Показываем аудиоплеер и блок результатов
        audioPlayer.classList.remove('hidden');
        resultBlock.classList.remove('hidden');

        // Начинаем воспроизведение аудио
        audioPlayer.play();

        // Предполагается, что result.words - массив объектов с полями word, start_time, end_time
        // Сортируем слова по времени начала для корректной последовательности
        const words = result.words.sort((a, b) => a.start_time - b.start_time);

        // Разбиваем оригинальный текст на слова и оборачиваем в span
        const originalText = result.original_text;
        const wordsOriginal = originalText.split(/(\s+|[.,!?]+)/); // Сохраняем пробелы и знаки препинания

        // Функция для сопоставления слов с таймингами
        let wordIndex = 0;
        let timingIndex = 0;

        const wrappedText = wordsOriginal.map(token => {
            // Проверяем, является ли токен словом (исключаем пробелы и знаки препинания)
            const cleanToken = token.replace(/[.,!?]/g, '').trim();
            if (cleanToken.length === 0) {
                return token; // Возвращаем пробел или знак препинания без оборачивания
            }

            if (timingIndex < words.length && cleanToken.toLowerCase() === words[timingIndex].word.toLowerCase()) {
                const wordObj = words[timingIndex];
                const start = wordObj.start_time;
                const end = wordObj.end_time;
                timingIndex++;
                return `<span class="word" data-start="${start}" data-end="${end}">${token}</span>`;
            } else {
                // Если нет совпадения, возвращаем без оборачивания
                return token;
            }
        }).join('');

        // Обновляем сгенерированный текст с обёрнутыми словами
        generatedText.innerHTML = wrappedText;

        // Переменная для хранения текущего выделенного слова
        let currentHighlighted = null;

        // Обработчик события timeupdate для подсветки слов
        audioPlayer.addEventListener('timeupdate', function highlightWords() {
            const currentTime = audioPlayer.currentTime * 1000; // Преобразуем в миллисекунды

            // Находим слово, которое должно быть выделено в текущий момент
            for (let span of generatedText.querySelectorAll('.word')) {
                const start = parseInt(span.getAttribute('data-start'), 10);
                const end = parseInt(span.getAttribute('data-end'), 10);

                if (currentTime >= start && currentTime <= end) {
                    if (currentHighlighted !== span) {
                        if (currentHighlighted) {
                            currentHighlighted.classList.remove('highlight');
                        }
                        span.classList.add('highlight');
                        currentHighlighted = span;
                        // Прокрутка к выделенному слову, если необходимо
                        span.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    return;
                }
            }

            // Если нет текущего слова, убрать подсветку
            if (currentHighlighted) {
                currentHighlighted.classList.remove('highlight');
                currentHighlighted = null;
            }
        });

        // Когда воспроизведение закончится, вернём текст в исходное состояние
        audioPlayer.addEventListener('ended', () => {
            if (currentHighlighted) {
                currentHighlighted.classList.remove('highlight');
                currentHighlighted = null;
            }
        });

    } catch (error) {
        alert(error.message);
    } finally {
        // Восстанавливаем состояние кнопки
        button.disabled = false;
        button.textContent = "Сгенерировать аудио";
    }
});
