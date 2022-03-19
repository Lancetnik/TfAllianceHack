from datetime import datetime

from .models import WatchedThemes, SendedMessage, Theme
from .user import get_user


async def create_message(message, theme: Theme) -> SendedMessage:
    return await SendedMessage.objects.create(
        user=await get_user(message.from_user.id),
        theme=theme,
        message_id=message.message_id,
        datetime=datetime.now()
    )


async def get_message(message_id: int) -> SendedMessage:
    return await SendedMessage.objects.get_or_none(id=message_id)


async def get_messages(theme: Theme, user=None, time=None):
    if time is None:
        messages = SendedMessage.objects\
            .filter(theme=theme)\
            .prefetch_related('user')
    else:
        messages = SendedMessage.objects\
            .filter(theme=theme, datetime__gt=time)\
            .prefetch_related('user')
    if user:
        messages = messages.filter(user=user)
    return await messages.all()


async def get_or_create_watched(user_id: int, theme: Theme) -> WatchedThemes:
    user = await get_user(user_id)
    return await WatchedThemes.objects.get_or_create(user=user, theme=theme)
