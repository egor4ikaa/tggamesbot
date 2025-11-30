# handlers/profile_handler.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from states.profile_states import ProfileStates
from keyboards.reply import (
    gender_menu, age_skip_menu, photo_skip_menu, location_menu,
    edit_profile_menu, main_menu_after_auth
)
from utils.user_manager import get_user, update_user_field
import re

router = Router()

@router.message(
    lambda msg: msg.text == "⬅️ Назад в меню",
    StateFilter(ProfileStates)  # срабатывает в ЛЮБОМ состоянии FSM профиля
)
async def cancel_editing(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Редактирование отменено. Изменения не сохранены.",
        reply_markup=main_menu_after_auth
    )

# Заглушки (заменятся на загрузку из БД после реализации админки)
REGIONS = ["Москва", "Санкт-Петербург", "Екатеринбург", "Новосибирск", "Казань", "Удмуртская республика"]
INTERESTS = ["Спорт", "Кино", "Музыка", "Путешествия", "Кулинария", "IT", "Книги", "Агро"]

# Генерация клавиатур для регионов/интересов с "Пропустить"
def make_choice_keyboard(options: list[str], with_skip: bool = True) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=opt)] for opt in options]
    if with_skip:
        buttons.append([KeyboardButton(text="⏭ Пропустить")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

# Запуск регистрации
@router.message(Command("profile"))
@router.message(lambda msg: msg.text == "👤 Мой профиль")
async def cmd_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)

    # Если профиль не заполнен — запускаем регистрацию
    if not user or not user.get("name"):
        await message.answer("Давайте заполним ваш профиль 👤", reply_markup=ReplyKeyboardRemove())
        await message.answer("Как вас зовут? (только имя)")
        await state.set_state(ProfileStates.waiting_for_name)
    else:
        # Показ профиля
        lines = ["👤 *Ваш профиль:*"]
        if user.get("name") or user.get("surname"):
            lines.append(f"👁‍🗨 Имя: {user['name']} {user['surname']}")
        if user.get("age"):
            lines.append(f"🎂 Возраст: {user['age']}")
        if user.get("gender"):
            lines.append(f"⚧ Пол: {user['gender']}")
        if user.get("region"):
            lines.append(f"📍 Регион: {user['region']}")
        if user.get("interests"):
            lines.append(f"🎯 Интересы: {', '.join(user['interests'])}")
        if user.get("photo_id"):
            lines.append("🖼 Фото: прикреплено")
        # Вывод профиля
        text = "\n".join(lines)
        if user.get("photo_id"):
            await message.answer_photo(
                photo=user["photo_id"],
                caption=text,
                parse_mode="Markdown",
                reply_markup=edit_profile_menu
            )
        else:
            await message.answer(
                text or "Профиль пуст.",
                parse_mode="Markdown",
                reply_markup=edit_profile_menu
            )

#  Редактирование 
@router.message(lambda msg: msg.text == "✏️ Редактировать профиль")
async def edit_profile(message: types.Message, state: FSMContext):
    await message.answer("✏️ Начинаем редактирование профиля.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Как вас зовут?")
    await state.set_state(ProfileStates.waiting_for_name)

# Имя
@router.message(StateFilter(ProfileStates.waiting_for_name))
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not re.fullmatch(r"[а-яА-ЯёЁa-zA-Z]+", name):
        await message.answer("📛 Не похоже на имя. Попробуйте ещё раз (только буквы).")
        return
    await state.update_data(name=name)
    await message.answer("Теперь введите вашу фамилию:")
    await state.set_state(ProfileStates.waiting_for_surname)

# Фамилия 
@router.message(StateFilter(ProfileStates.waiting_for_surname))
async def process_surname(message: types.Message, state: FSMContext):
    surname = message.text.strip()
    if not re.fullmatch(r"[а-яА-ЯёЁa-zA-Z]+", surname):
        await message.answer("📛 Не похоже на фамилию. Попробуйте ещё раз (только буквы).")
        return
    await state.update_data(surname=surname)
    await message.answer("Укажите ваш пол:", reply_markup=gender_menu)
    await state.set_state(ProfileStates.waiting_for_gender)

# Пол 
@router.message(StateFilter(ProfileStates.waiting_for_gender))
async def process_gender(message: types.Message, state: FSMContext):
    text = message.text
    if text == "♂️ Муж":
        gender = "муж"
    elif text == "♀️ Жен":
        gender = "жен"
    elif text == "⏭ Пропустить":
        gender = None
    else:
        await message.answer("Выберите пол кнопкой:", reply_markup=gender_menu)
        return
    await state.update_data(gender=gender)
    await message.answer("Сколько вам лет? (укажите цифрами, например: 25)", reply_markup=age_skip_menu)
    await state.set_state(ProfileStates.waiting_for_age)

# Возраст 
@router.message(StateFilter(ProfileStates.waiting_for_age))
async def process_age(message: types.Message, state: FSMContext):
    text = message.text
    if text == "⏭ Пропустить":
        await state.update_data(age=None)
        await _ask_region(message, state)
        return

    if not text.isdigit():
        await message.answer("🔢 Не похоже на возраст. Попробуйте ещё раз (только цифры).")
        return

    age = int(text)
    if not (1 <= age <= 120):
        await message.answer("🔢 Возраст должен быть от 1 до 120. Попробуйте ещё раз.")
        return

    await state.update_data(age=age)
    await _ask_region(message, state)

async def _ask_region(message: types.Message, state: FSMContext):
    await message.answer("Выберите ваш регион:", reply_markup=make_choice_keyboard(REGIONS))
    await state.set_state(ProfileStates.waiting_for_region)

# Регион
@router.message(StateFilter(ProfileStates.waiting_for_region))
async def process_region(message: types.Message, state: FSMContext):
    text = message.text
    if text == "⏭ Пропустить":
        region = ""
    elif text in REGIONS:
        region = text
    else:
        await message.answer("Выберите регион из списка:", reply_markup=make_choice_keyboard(REGIONS))
        return
    await state.update_data(region=region)
    await message.answer("Выберите ваши интересы (можно выбрать несколько, по одному):",
                         reply_markup=make_choice_keyboard(INTERESTS))
    await state.update_data(interests=[])  # будем накапливать
    await state.set_state(ProfileStates.waiting_for_interests)

# Интересы (мульти-выбор) 
@router.message(StateFilter(ProfileStates.waiting_for_interests))
async def process_interests(message: types.Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    interests = data.get("interests", [])

    if text == "⏭ Пропустить":
        # Завершаем выбор интересов
        await state.update_data(interests=interests)
        await _ask_photo(message, state)
        return

    if text in INTERESTS and text not in interests:
        interests.append(text)
        await state.update_data(interests=interests)
        await message.answer(f"✅ Добавлен интерес: *{text}*\nМожно добавить ещё или нажмите *«Пропустить»*.",
                             parse_mode="Markdown", reply_markup=make_choice_keyboard(INTERESTS))
    elif text in interests:
        await message.answer(f"🔹 Вы уже добавили *{text}*.", parse_mode="Markdown")
    else:
        await message.answer("Выберите интерес из списка:", reply_markup=make_choice_keyboard(INTERESTS))

#Фото 
async def _ask_photo(message: types.Message, state: FSMContext):
    await message.answer("Загрузите фото профиля (jpg/jpeg/png) или нажмите «Пропустить»:",
                         reply_markup=photo_skip_menu)
    await state.set_state(ProfileStates.waiting_for_photo)

@router.message(StateFilter(ProfileStates.waiting_for_photo))
async def process_photo(message: types.Message, state: FSMContext):
    if message.text == "⏭ Пропустить":
        await state.update_data(photo_id="")
        await _ask_location(message, state)
        return

    if message.photo:
        photo_id = message.photo[-1].file_id  # берем самое большое
        await state.update_data(photo_id=photo_id)
        await _ask_location(message, state)
    else:
        # Проверка формата (если пользователь прислал не фото)
        if message.document:
            mime = message.document.mime_type
            if mime in ["image/jpeg", "image/png"]:
                await state.update_data(photo_id=message.document.file_id)
                await _ask_location(message, state)
                return
        await message.answer("🖼 Не похоже на фото. Загрузите изображение в формате jpg, jpeg или png.")

#Геопозиция
async def _ask_location(message: types.Message, state: FSMContext):
    await message.answer("Укажите ваше местоположение (можно пропустить):", reply_markup=location_menu)
    await state.set_state(ProfileStates.waiting_for_location)

@router.message(StateFilter(ProfileStates.waiting_for_location))
async def process_location(message: types.Message, state: FSMContext):
    location = None
    if message.location:
        location = {"latitude": message.location.latitude, "longitude": message.location.longitude}
    elif message.text == "⏭ Пропустить":
        location = None
    else:
        await message.answer("📍 Нажмите кнопку «Отправить геопозицию» или «Пропустить».", reply_markup=location_menu)
        return

    await state.update_data(location=location)

    # Сохраняем всё в БД 
    data = await state.get_data()
    user_id = message.from_user.id

    update_user_field(
        user_id,
        name=data.get("name", ""),
        surname=data.get("surname", ""),
        gender=data.get("gender"),
        age=data.get("age"),
        region=data.get("region", ""),
        interests=data.get("interests", []),
        photo_id=data.get("photo_id", ""),
        location=location
    )

    await message.answer("✅ Профиль успешно сохранён!", reply_markup=main_menu_after_auth)
    await state.clear()

    # Показываем профиль
    await cmd_profile(message, state)
