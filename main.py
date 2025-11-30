# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем конфиг
from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Импортируем роутеры (важен порядок!)
from handlers.profile_handler import router as profile_router     # ← FSM-регистрация
from handlers.game_handlers import router as game_router
from handlers.reading_handler import router as reading_router
from handlers.common import router as common_router              # ← общий — в конце!

async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # 🔔 Порядок подключения критичен: сначала FSM (profile), потом остальные, common — в конце
    dp.include_router(profile_router)
    dp.include_router(game_router)
    dp.include_router(reading_router)
    dp.include_router(common_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())