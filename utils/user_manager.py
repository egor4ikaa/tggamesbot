# utils/user_manager.py
import json
import os
from config import ADMIN_PHONE_NUMBERS

USER_DB_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    with open(USER_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(user_id: int):
    users = load_users()
    return users.get(str(user_id))

def update_user_field(user_id: int, **kwargs):
    users = load_users()
    user_key = str(user_id)
    if user_key not in users:
        users[user_key] = {
            "phone": "",
            "is_admin": False,
            "name": "",
            "surname": "",
            "gender": None,
            "age": None,
            "region": "",
            "interests": [],
            "photo_id": "",
            "location": None
        }
    # Определяем is_admin на основе phone (если phone обновлён)
    if "phone" in kwargs:
        phone = kwargs["phone"]
        # Убираем возможный '+' и ведущие нули, приводим к строке
        clean_phone = str(phone).lstrip('+').lstrip('0')
        kwargs["is_admin"] = clean_phone in ADMIN_PHONE_NUMBERS

    users[user_key].update(kwargs)
    save_users(users)

def is_admin(user_id: int) -> bool:
    user = get_user(user_id)
    return user.get("is_admin", False) if user else False