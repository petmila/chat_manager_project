from mmpy_bot import Bot, Settings
from mmpy_bot.driver import Driver

from mmbot.connections.http_client import HTTPSession
from mmbot.plugins.save_plugin import SavePlugin
from mmbot.plugins.summary_plugin import SummaryPlugin
from mmbot.connections.rabbitmq_producer import RabbitMQConnection
from decouple import config


driver = Driver({
    "url": config('MATTERMOST_URL'),
    "scheme": "https",
    "token": config('TOKEN'),
    "port": config('DRIVER_PORT'),
    "verify": False,
})
driver.login()
bot_user_id = driver.users.get_user("me")["id"]

session = HTTPSession()
connection = RabbitMQConnection()
settings = Settings(
        MATTERMOST_URL=config('MATTERMOST_URL'),
        MATTERMOST_API_PATH=config('MATTERMOST_API_PATH'),
        MATTERMOST_PORT=config('MATTERMOST_PORT'),
        BOT_TOKEN=config('TOKEN'),
        BOT_TEAM=config('BOT_TEAM'),
        SSL_VERIFY=False,
        # WEBHOOK_HOST_URL="http://127.0.0.1",
        # WEBHOOK_HOST_PORT=8065,
        WEBHOOK_HOST_ENABLED=True
)
bot = Bot(
    settings=settings,
    plugins=[SummaryPlugin(bot_user_id, settings), SavePlugin(bot_user_id, settings)],
)
bot.run()
