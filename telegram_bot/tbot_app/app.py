from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config
from aiogram import Bot, Dispatcher
from tbot_app.client import HTTPSession
from tbot_app.rabbit_mq_connection import RabbitMQConnection
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

session = HTTPSession()
connection = RabbitMQConnection()
bot = Bot(token=config('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())