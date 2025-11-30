from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import random
from aiogram.filters import Command
from states.game_states import GuessNumberGame, RPSGame
from keyboards.reply import main_menu, rps_menu, remove_keyboard, rps_after_game_menu
from aiogram.utils.text_decorations import html_decoration as hd

router = Router()

# Ссылка на гифку для ошибок
ERROR_GIF_URL = "https://i.postimg.cc/5NMKNd0F/10-cats-mem-lvjj8lt6npax.gif"

@router.message(Command("cancel"))
async def cmd_cancel_anywhere(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer(
            "✅ Операция отменена. Возвращаемся в главное меню.",
            reply_markup=main_menu
        )
    else:
        await message.answer(
            "Вы уже в главном меню. Выберите игру:",
            reply_markup=main_menu
        )

# ===== УГАДАЙ ЧИСЛО ===== (Курсив)
@router.message(lambda message: message.text == "🎲 Угадай число")
async def start_guess_number(message: types.Message, state: FSMContext):
    await state.set_state(GuessNumberGame.guessing)
    secret_number = random.randint(1, 6)
    await state.update_data(secret_number=secret_number, attempts=1)

    text = hd.italic(
        f"🎯 Я загадал число от 1 до 6!\n"
        f"У тебя 1 попытка. Попробуй угадать!\n\n"
        f"Просто напиши число в чат:"
    )

    await message.answer(
        text,
        reply_markup=remove_keyboard,
        parse_mode='HTML'
    )

@router.message(StateFilter(GuessNumberGame.guessing))
async def process_guess(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        caption = hd.italic("❌ Пожалуйста, введите число от 1 до 6!")
        await message.answer_animation(
            animation=ERROR_GIF_URL,
            caption=caption,
            parse_mode='HTML'
        )
        return

    user_guess = int(message.text)
    data = await state.get_data()
    secret_number = data['secret_number']
    attempts = data['attempts'] - 1

    if user_guess < 1 or user_guess > 6:
        caption = hd.italic("❌ Пожалуйста, введите число от 1 до 6!")
        await message.answer_animation(
            animation=ERROR_GIF_URL,
            caption=caption,
            parse_mode='HTML'
        )
        return

    if user_guess == secret_number:
        text = hd.italic(f"🎉 Поздравляю! Ты угадал число {secret_number}!")
        await message.answer(
            text,
            reply_markup=main_menu,
            parse_mode='HTML'
        )
        await state.clear()
        return

    if attempts == 0:
        text = hd.italic(f"❌ Попытки закончились! Я загадал число {secret_number}.")
        await message.answer(
            text,
            reply_markup=main_menu,
            parse_mode='HTML'
        )
        await state.clear()
        return

    # Даем подсказку
    hint = "Загаданное число МЕНЬШЕ" if user_guess > secret_number else "Загаданное число БОЛЬШЕ"
    await state.update_data(attempts=attempts)

    text = hd.italic(
        f"{hint}\n"
        f"❌ Не угадал! Осталось попыток: {attempts}\n"
        f"Попробуй еще раз:"
    )

    await message.answer(
        text,
        parse_mode='HTML'
    )

# ===== КАМЕНЬ-НОЖНИЦЫ-БУМАГА ===== (Жирный)
@router.message(lambda message: message.text == "🪨✂️📄 Камень-ножницы-бумага")
async def start_rps(message: types.Message, state: FSMContext):
    await state.set_state(RPSGame.choosing)
    text = hd.bold("🎮 Выбери свой вариант:")

    await message.answer(
        text,
        reply_markup=rps_menu,
        parse_mode='HTML'
    )

@router.message(StateFilter(RPSGame.choosing))
async def process_rps_choice(message: types.Message, state: FSMContext):
    # Обработка кнопки "Назад"
    if message.text == "🔙 Назад":
        await state.clear()
        text = hd.bold("Возвращаемся в главное меню:")
        await message.answer(
            text,
            reply_markup=main_menu,
            parse_mode='HTML'
        )
        return

    # Обработка выбора после игры
    if message.text == "🔄 Сыграть еще":
        text = hd.bold("🎮 Отлично! Выбери свой вариант:")
        await message.answer(
            text,
            reply_markup=rps_menu,
            parse_mode='HTML'
        )
        return

    if message.text == "🔙 В главное меню":
        await state.clear()
        text = hd.bold("Возвращаемся в главное меню:")
        await message.answer(
            text,
            reply_markup=main_menu,
            parse_mode='HTML'
        )
        return

    # Обработка выбора игры
    user_choice_text = message.text

    # Определяем выбор пользователя по тексту кнопок
    if user_choice_text == "🪨 Камень":
        user_choice_clean = "камень"
    elif user_choice_text == "✂️ Ножницы":
        user_choice_clean = "ножницы"
    elif user_choice_text == "📄 Бумага":
        user_choice_clean = "бумага"
    else:
        caption = hd.bold("❌ Пожалуйста, выбери вариант с помощью кнопок ниже:")
        await message.answer_animation(
            animation=ERROR_GIF_URL,
            caption=caption,
            reply_markup=rps_menu,
            parse_mode='HTML'
        )
        return

    # Бот делает случайный выбор
    bot_choice = random.choice(["камень", "ножницы", "бумага"])

    # Определяем победителя
    if user_choice_clean == bot_choice:
        result = "🤝 Ничья!"
    elif (user_choice_clean == "камень" and bot_choice == "ножницы") or \
         (user_choice_clean == "ножницы" and bot_choice == "бумага") or \
         (user_choice_clean == "бумага" and bot_choice == "камень"):
        result = "🎉 Ты победил!"
    else:
        result = "❌ Бот победил!"

    # Эмодзи для выбора
    emoji_map = {"камень": "🪨", "ножницы": "✂️", "бумага": "📄"}

    # Показываем результат игры
    game_result = hd.bold(
        f"Твой выбор: {emoji_map[user_choice_clean]} {user_choice_clean}\n"
        f"Выбор бота: {emoji_map[bot_choice]} {bot_choice}\n\n"
        f"{result}"
    )

    await message.answer(
        game_result,
        parse_mode='HTML'
    )

    # Предлагаем сыграть еще
    play_again = hd.bold("Хочешь сыграть еще раз?")
    await message.answer(
        play_again,
        reply_markup=rps_after_game_menu,
        parse_mode='HTML'
    )
