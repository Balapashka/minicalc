# YouTube Channel Video Links Parser

Парсер для сбора всех ссылок на видео с YouTube канала в .txt файл.

## Требования

- Python 3.6+
- Библиотека `google-api-python-client`
- API ключ YouTube Data API v3

## Установка зависимостей

```bash
pip install google-api-python-client
```

## Получение API ключа

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Создайте новый проект или выберите существующий
3. Включите YouTube Data API v3
4. Создайте учетные данные (API ключ)
5. Скопируйте полученный ключ

## Использование

### Установка переменной окружения

```bash
export YOUTUBE_API_KEY=ваш_ключ_api
```

### Запуск парсера

```bash
# Ссылка на канал в формате @handle
python youtube_parser.py https://www.youtube.com/@ChannelName

# Ссылка на канал в формате /channel/ID
python youtube_parser.py https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxx

# Просто ID канала
python youtube_parser.py UCxxxxxxxxxxxxxxxxxxxxxxx

# С указанием имени выходного файла
python youtube_parser.py https://www.youtube.com/@ChannelName my_videos.txt
```

## Поддерживаемые форматы ссылок

- `https://www.youtube.com/@ChannelName` (handle)
- `https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxx`
- `https://www.youtube.com/c/ChannelName`
- `https://www.youtube.com/user/Username`
- `UCxxxxxxxxxxxxxxxxxxxxxxx` (raw channel ID)
- `@ChannelName` (handle без домена)

## Результат

Скрипт создает файл `.txt` (по умолчанию `youtube_videos.txt`) со списком всех видео канала в формате:
```
https://www.youtube.com/watch?v=VIDEO_ID
https://www.youtube.com/watch?v=VIDEO_ID2
...
```

## Как это работает

1. Скрипт принимает ссылку на канал или его ID
2. При необходимости resolves handle/custom URL в настоящий channel ID через API
3. Использует YouTube Data API v3 с пагинацией для получения ВСЕХ видео канала
4. Сохраняет все ссылки в текстовый файл

## Примечания

- YouTube Data API имеет квоты (бесплатно ~10,000 единиц в день)
- Поиск видео использует до 1 единицы квоты на запрос
- Для каналов с большим количеством видео может потребоваться несколько запросов
