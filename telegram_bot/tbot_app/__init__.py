import logging

from .app import bot, dp, connection, session
from .handlers import summary, saving, history
from .keyboards import inline_keyboard

logging.basicConfig(level=logging.DEBUG)

