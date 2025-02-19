from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from aiogram import Bot, Dispatcher
from tbot_app.client import HTTPSession

session = HTTPSession()
bot = Bot(token=config('TOKEN'))
dp = Dispatcher(storage=MemoryStorage())