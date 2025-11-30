# states/game_states.py
from aiogram.fsm.state import State, StatesGroup

class GuessNumberGame(StatesGroup):
    guessing = State()

class RPSGame(StatesGroup):
    choosing = State()