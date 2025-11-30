# config.py
import os
from dotenv import load_dotenv

# Загружаем .env — важно указать путь явно, если запускаешь не из корня
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PHONE_NUMBERS = os.getenv("ADMIN_PHONE_NUMBERS", "").split(",")  # например: "79123456789,79876543210"

# Проверка критичных параметров
if not BOT_TOKEN:
    raise ValueError("Переменная BOT_TOKEN не задана в .env")