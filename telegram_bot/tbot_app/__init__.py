import logging

from .app import bot, dp, session
from .handlers import summary, saving, history
from .keyboards import inline_keyboard

logging.basicConfig(level=logging.DEBUG)

