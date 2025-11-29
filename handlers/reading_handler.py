# handlers/reading_handler.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from states.reading_states import ReadingWebsite
from keyboards.reply import reading_menu, main_menu
from utils.web_reader import extract_readable_text
import json
import os
import hashlib

router = Router()

# Файл для закладок: { "user_id:url_hash": index }
BOOKMARKS_FILE = "reading_bookmarks.json"

def get_url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:10]

def load_bookmarks():
    if not os.path.exists(BOOKMARKS_FILE):
        return {}
    with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_bookmark(user_id: int, url: str, position: int):
    bookmarks = load_bookmarks()
    key = f"{user_id}:{get_url_hash(url)}"
    bookmarks[key] = {"url": url, "position": position}
    with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)

def get_bookmark(user_id: int, url: str) -> int:
    bookmarks = load_bookmarks()
    key = f"{user_id}:{get_url_hash(url)}"
    return bookmarks.get(key, {}).get("position", 0)

@router.message(lambda message: message.text == "📖 Читать сайт")
async def request_url(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, отправьте (html) ссылку на сайт, который хотите прочитать:")
    await state.set_state(ReadingWebsite.waiting_for_url)

@router.message(StateFilter(ReadingWebsite.waiting_for_url))
async def process_url(message: types.Message, state: FSMContext):
    if not message.text.startswith(("http://", "https://")):
        await message.answer("Пожалуйста, отправьте ссылку сайта (начинается с http:// или https://).")
        return

    url = message.text
    await message.answer("⏳ Загружаю и обрабатываю страницу...")

    paragraphs = extract_readable_text(url)

    if len(paragraphs) == 1 and paragraphs[0].startswith("❌ Ошибка"):
        await message.answer(paragraphs[0], reply_markup=main_menu)
        await state.clear()
        return

    if not paragraphs:
        await message.answer("Не удалось извлечь текст с сайта. Попробуйте другую ссылку.", reply_markup=main_menu)
        await state.clear()
        return

    # Сохраняем данные
    user_id = message.from_user.id
    saved_position = get_bookmark(user_id, url)

    if saved_position >= len(paragraphs):
        saved_position = 0  # сброс, если контент изменился

    await state.update_data(
        url=url,
        content=paragraphs,
        reading_position=saved_position
    )
    await state.set_state(ReadingWebsite.reading)

    # Отправляем первый абзац
    if saved_position > 0:
        await message.answer(f"📌 Вы остановились здесь. Продолжаем чтение:", reply_markup=reading_menu)
    else:
        await message.answer("Начинаем чтение:", reply_markup=reading_menu)

    await message.answer(paragraphs[saved_position])

@router.message(StateFilter(ReadingWebsite.reading))
async def handle_reading_actions(message: types.Message, state: FSMContext):
    data = await state.get_data()
    content = data.get("content", [])
    current_index = data.get("reading_position", 0)
    url = data.get("url", "")

    if not content:
        await message.answer("Ошибка: контент утерян. Попробуйте начать заново.", reply_markup=main_menu)
        await state.clear()
        return

    user_id = message.from_user.id

    if message.text == "➡️ Далее":
        next_index = current_index + 1
        if next_index >= len(content):
            await message.answer("📖 Вы дочитали до конца!", reply_markup=main_menu)
            await state.clear()
        else:
            await message.answer(content[next_index])
            await state.update_data(reading_position=next_index)
            save_bookmark(user_id, url, next_index)

    elif message.text == "🔖 Поставить закладку":
        save_bookmark(user_id, url, current_index)
        await message.answer(
            f"🔖 Закладка сохранена на позиции {current_index + 1} из {len(content)}.",
            reply_markup=reading_menu
        )

    elif message.text == "🔙 Назад":
        await state.clear()
        await message.answer("Возвращаемся в главное меню:", reply_markup=main_menu)

    else:
        await message.answer("Используйте кнопки для навигации:", reply_markup=reading_menu)