from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.reply import main_menu, auth_keyboard, remove_keyboard, main_menu_after_auth
from utils.user_manager import get_user, update_user_field, is_admin

router = Router()

ERROR_GIF_ID = "https://i.postimg.cc/5NMKNd0F/10-cats-mem-lvjj8lt6npax.gif"


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_data = get_user(user_id)

    if not user_data or not user_data.get("phone"):
        await message.answer(
            "Что может этот бот:\n"
            "📍 Организация мероприятий\n"
            "👥 Поиск участников и друзей\n"
            "💬 Общение по интересам\n\n"
            "Нажмите «Запустить», чтобы начать.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="▶️ Запустить")]],
                resize_keyboard=True
            )
        )
    else:
        # Уже авторизован
        if is_admin(user_id):
            await message.answer("👑 Добро пожаловать, администратор!", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("👤 Добро пожаловать пользователь! Выберите действие:", reply_markup=main_menu_after_auth)

@router.message(lambda message: message.contact and message.contact.phone_number)
async def handle_contact(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    update_user_field(user_id, phone=phone_number)

    # Проверяем статус
    if is_admin(user_id):
        await message.answer(
            "✅ Авторизация успешна!\n"
            "👑 Вы — администратор.\n\n",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        # Обычный пользователь — запускаем регистрацию профиля
        await message.answer(
            "✅ Авторизация успешна!\n"
            "Давайте заполним ваш профиль 👤",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer("Как вас зовут? (только имя)")
        await state.set_state("waiting_for_name")

@router.message(Command("setadmin"))
async def cmd_setadmin(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У тебя нет прав администратора.")
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Используй: /setadmin <user_id>")
        return

    try:
        target_id = int(args[1])
        set_admin(target_id, True)
        await message.answer(f"✅ Пользователь {target_id} назначен администратором.")
    except ValueError:
        await message.answer("❌ Неверный формат user_id.")

@router.message(Command("users"))
async def cmd_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У тебя нет прав администратора.")
        return

    users = load_users()
    text = "📋 Список пользователей:\n\n"
    for uid, data in users.items():
        role = "👑 Админ" if data["is_admin"] else "👤 Пользователь"
        text += f"{uid}: {data['phone']} — {role}\n"

    await message.answer(text, reply_markup=main_menu)

@router.message(Command("help"))
@router.message(lambda message: message.text == "❓ Помощь")
async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    help_text = (
        "🎲 <b>Угадай число</b>:\n"
        "Я загадываю число от 1 до 6. Попробуй угадать! У тебя 1 попытка.\n\n"
        "🪨✂️📄 <b>Камень, ножницы, бумага</b>:\n"
        "Выбери один из вариантов. Бот тоже сделает выбор. Победитель определяется по классическим правилам.\n\n"
        "📖 <b>Читать сайт</b>:\n"
        "Читайте по частям контент сайта. Бот запоминает, где вы остановились, и позволяет ставить закладки.\n\n"
        "Если вы нажали <b>Читать сайт</b> и передумали, выбери из меню команду <b>/cancel</b>\n\n"
        "Используй кнопки ниже, чтобы начать читать или играть!"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=main_menu)


@router.message(Command("games"))
@router.message(lambda message: message.text == "🎱 Начать играть")
async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    help_text = (
        "🎲 <b>Угадай число</b>:\n"
        "Я загадываю число от 1 до 6. Попробуй угадать! У тебя 1 попытка.\n\n"
        "🪨✂️📄 <b>Камень, ножницы, бумага</b>:\n"
        "Выбери один из вариантов. Бот тоже сделает выбор. Победитель определяется по классическим правилам.\n\n"
        "📖 <b>Читать сайт</b>:\n"
        "Читайте по частям контент сайта. Бот запоминает, где вы остановились, и позволяет ставить закладки.\n\n"
        "Если вы нажали <b>Читать сайт</b> и передумали, выбери из меню команду <b>/cancel</b> \n\n"
        "Используй кнопки ниже, чтобы начать читать или играть!"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=main_menu)


@router.message(lambda message: message.text == "💎 Главное меню")
async def cmd_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏠 Главное меню:",
        reply_markup=main_menu_after_auth
    )

@router.message(lambda message: message.text == "⬅️ Назад в меню")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✅ Вы вернулись в главное меню.",
        reply_markup=main_menu_after_auth
    )

@router.message()
async def handle_other_messages(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = get_user(user_id)

    # Если пользователь не авторизован — игнорируем
    if not user_data or not user_data.get("phone"):
        await message.answer(
            "Пожалуйста, сначала авторизуйтесь, отправив свой номер телефона.",
            reply_markup=auth_keyboard
        )
        return

    current_state = await state.get_state()
    if current_state is None:
        if message.text not in ["🎲 Угадай число", "🪨✂️📄 Камень-ножницы-бумага", "❓ Помощь", "📖 Читать сайт"]:
            await message.answer_animation(
                animation=ERROR_GIF_ID,
                caption="Пожалуйста, используйте кнопки меню для выбора игры.",
                reply_markup=main_menu
            )