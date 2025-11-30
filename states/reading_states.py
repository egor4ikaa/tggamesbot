from aiogram.fsm.state import State, StatesGroup

class ReadingWebsite(StatesGroup):
    waiting_for_url = State()  # ← новое состояние
    reading = State()