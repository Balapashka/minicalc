from googleapiclient.discovery import build

API_KEY = "AIzaSyBev190lPq0xxMNoKf6cX8_TmheoPQZScM"
CHANNEL_HANDLE = "@Kboges"

try:
    youtube = build("youtube", "v3", developerKey=API_KEY)
    
    # Поиск канала по handle
    request = youtube.search().list(
        part="snippet",
        q=CHANNEL_HANDLE,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if response.get("items"):
        channel_id = response["items"][0]["id"]["channelId"]
        channel_title = response["items"][0]["snippet"]["title"]
        
        # Получаем детальную информацию о канале
        channel_request = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        channel_response = channel_request.execute()
        
        if channel_response.get("items"):
            channel_data = channel_response["items"][0]
            stats = channel_data["statistics"]
            
            print(f"✅ API работает успешно!")
            print(f"📺 Канал: {channel_title}")
            print(f"🆔 ID канала: {channel_id}")
            print(f"👥 Подписчиков: {stats.get('subscriberCount', 'N/A')}")
            print(f"🎬 Видео: {stats.get('videoCount', 'N/A')}")
            print(f"👁️ Просмотров: {stats.get('viewCount', 'N/A')}")
        else:
            print("❌ Не удалось получить информацию о канале")
    else:
        print("❌ Канал не найден")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
