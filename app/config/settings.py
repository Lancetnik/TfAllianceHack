from propan.config import settings


DATABASE_URL = f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}\
@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'
