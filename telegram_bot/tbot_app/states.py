from aiogram.fsm.state import StatesGroup, State


class PrivateSummary(StatesGroup):
    chat_id = State()
    date = State()

class PrivateAutoGenerationSettings(StatesGroup):
    frequency = State()
    timestamp = State()
    chat_id = State()