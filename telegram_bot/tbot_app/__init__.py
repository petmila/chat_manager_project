import logging

from .app import bot, dp, session
from .handlers import summary, saving, history

logging.basicConfig(level=logging.DEBUG)

