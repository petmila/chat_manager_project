from functools import wraps
from mmpy_bot import listen_to


def listen_without_mention(pattern):
    def decorator(func):
        @listen_to(pattern)
        @wraps(func)
        async def wrapper(plugin, message, *args, **kwargs):
            """
            Фильтрация только сообщений в групповых чатах и
             сообщений где нет обращений к боту
            """
            bot_user_id = plugin.bot_user_id
            if bot_user_id in message.mentions:
                return
            return await func(plugin, message, *args, **kwargs)
        return wrapper
    return decorator