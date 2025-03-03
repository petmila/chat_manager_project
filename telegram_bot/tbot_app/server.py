import json
from aiohttp import web

from tbot_app.message import send_message_to_telegram


async def handle_http_request(request):
    """

    :param request:
    :return:
    """
    try:
        data = await request.json()
        chat_id = data.get("chat_id")
        text = data.get("text")

        if not chat_id or not text:
            return web.Response(text=json.dumps({"error": "Invalid data"}), status=400)

        response = await send_message_to_telegram(chat_id, text)
        return web.Response(text=json.dumps(response), status=200)

    except Exception as e:
        return web.Response(text=json.dumps({"error": str(e)}), status=500)


async def start_http_server():
    """
    Запускает встроенный HTTP-сервер на aiogram.
    """
    app = web.Application()
    app.router.add_post('/send_message', handle_http_request)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("HTTP-сервер бота запущен на 0.0.0.0:8080")