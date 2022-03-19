import asyncio
from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging

from propan.config import settings
from propan.logger import loguru as logger

from config.dependencies import bot, dp

from superuser.views import *

from admin.views import *
from admin.themes_views import *
from admin.filters_views import *
from admin.messages_views import *

from base.views import *
from base.filters_views import *

from user.filters_views import *
from user.views import *


logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp):
    logger.debug('Starting...')
    await bot.set_webhook(settings.WEBHOOK_URL)


async def on_shutdown(dp):
    logger.debug('Shutting down..')
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logger.debug('Bye!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor = executor.set_webhook(dispatcher=dp,
                                    webhook_path=settings.WEBHOOK_PATH,
                                    loop=loop,
                                    skip_updates=False,
                                    on_startup=on_startup,
                                    on_shutdown=on_shutdown)
    executor.run_app(loop=loop, host=settings.WEBAPP_HOST, port=settings.WEBAPP_PORT)
