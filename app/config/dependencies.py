from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from propan.config import settings


bot = Bot(token=settings.API_TOKEN)
storage = RedisStorage2(settings.REDIS_HOST, settings.REDIS_PORT)
dp = Dispatcher(bot, storage=storage)
