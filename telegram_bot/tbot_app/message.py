from tbot_app import bot


async def send_message_to_telegram(user_id: str, text: str):
    """
    Функция отправляет сообщение пользователю в Telegram.
    """
    try:
        await bot.send_message(chat_id=user_id, text=text)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
