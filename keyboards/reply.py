from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲 Угадай число"), KeyboardButton(text="🪨✂️📄 Камень-ножницы-бумага")],
        [KeyboardButton(text="📖 Читать сайт"), KeyboardButton(text="❓ Помощь")], [KeyboardButton(text="💎 Главное меню")]
    ],
    resize_keyboard=True
)

# Главное меню после регистрации
main_menu_after_auth = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🎱 Начать играть")]
    ],
    resize_keyboard=True
)

# Меню для игры в камень-ножницы-бумагу
rps_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🪨 Камень"), KeyboardButton(text="✂️ Ножницы")],
        [KeyboardButton(text="📄 Бумага"), KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)
# В reply.py добавьте:

# Клавиатура для чтения сайта
reading_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➡️ Далее")],
        [KeyboardButton(text="🔖 Поставить закладку"), KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# Меню после игры (сыграть еще или выйти)
rps_after_game_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔄 Сыграть еще"), KeyboardButton(text="🔙 В главное меню")]
    ],
    resize_keyboard=True
)

# Для скрытия клавиатуры
remove_keyboard = ReplyKeyboardRemove()

auth_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True  # скрывается после использования
)


skip_button = KeyboardButton(text="⏭ Пропустить")

# Пол
gender_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="♂️ Муж"), KeyboardButton(text="♀️ Жен")],
        [KeyboardButton(text="⏭ Пропустить")],
        [KeyboardButton(text="⬅️ Назад в меню")]  # ← добавлено
    ],
    resize_keyboard=True,
    one_time_keyboard=False  # ← важно: не скрывать, чтобы кнопка всегда была
)

# Возраст (можно сделать как ввод, но по ТЗ — выбор диапазона)
# Для простоты реализуем как ввод числа (валидация 1–120), но если нужно — заменим на кнопки
age_skip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад в меню")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Клавиатура "Пропустить" для фото/гео
photo_skip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад в меню")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

location_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Отправить геопозицию", request_location=True)],
        [KeyboardButton(text="⬅️ Назад в меню")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Меню "Редактировать профиль" (внутри профиля)
edit_profile_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Редактировать профиль")],
        [KeyboardButton(text="⬅️ Назад в меню")]
    ],
    resize_keyboard=True
)
