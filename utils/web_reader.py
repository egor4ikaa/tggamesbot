import requests
from bs4 import BeautifulSoup
import re

def extract_readable_text(url: str) -> list[str]:
    """
    Загружает страницу по URL и возвращает список абзацев (непустых строк текста).
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TelegramBot/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")

        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()

        # Получаем весь текст
        text = soup.get_text(separator="\n", strip=True)

        # Разбиваем на строки и фильтруем пустые/слишком короткие
        paragraphs = [
            p.strip() for p in text.split("\n")
            if p.strip() and len(p.strip()) > 20  # минимум 20 символов
        ]

        # Опционально: объединить короткие строки или разбить длинные
        return paragraphs

    except Exception as e:
        return [f"❌ Ошибка при загрузке сайта:\n{str(e)}"]