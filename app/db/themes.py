from typing import Optional, List
from uuid import uuid4

from .models import Theme, ThemeDescription, Group, Channel, User
from .user import get_user


async def create_theme(name: str) -> Theme:
    return await Theme.objects.create(name=name, uuid=uuid4())


async def get_theme(theme_id: int) -> Optional[Theme]:
    return await Theme.objects.get_or_none(id=theme_id)


async def get_theme_by_uuid(uuid: str) -> Optional[Theme]:
    return await Theme.objects.get_or_none(uuid=uuid)


async def get_theme_by_name(name: str) -> Optional[Theme]:
    return await Theme.objects.get_or_none(name=name)


async def get_group_by_name(name: str) -> Optional[Group]:
    return await Group.objects.get_or_none(title=name)


async def get_channel_by_name(name: str) -> Optional[Group]:
    return await Channel.objects.get_or_none(title=name)


async def get_themes(is_admin) -> List[Theme]:
    if is_admin is True:
        return await Theme.objects.all()
    else:
        return await Theme.objects.filter(is_public=True).all()


async def get_channels() -> List[Channel]:
    return await Channel.objects.all()


async def get_groups() -> List[Group]:
    return await Group.objects.all()


async def delete_theme(theme: Theme):
    for description in await theme.description.all():
        await description.delete()

    for message in await theme.messages.all():
        await message.delete()

    for watched in await theme.watched.all():
        await watched.delete()

    await theme.delete()


async def update_or_create_theme_description(theme, message):
    descriptions = await theme.description.all()  # not .first() -> error as empty
    if descriptions:
        description = descriptions[0]
        await description.update(
            user=await get_user(message.from_user.id), message_id=message.message_id
        )
    else:
        description = await ThemeDescription.objects.create(
            theme=theme,
            user=await get_user(message.from_user.id),
            message_id=message.message_id
        )
    return description


async def create_channel(chat, status):
    if status == 'kicked':
        await Channel.objects.delete(channel_id=chat.id)
    else:
        await Channel.objects.get_or_create(channel_id=chat.id, title=chat.title)


async def create_group(group, status):
    if status == 'member':
        await Group.objects.create(group_id=group.id, title=group.title)
    elif status == 'left':
        await Group.objects.delete(group_id=group.id)


async def get_themes_by_ids(ids):
    return await Theme.objects.filter(id__in=ids).all()


async def get_channels_by_ids(ids):
    return await Channel.objects.filter(channel_id__in=ids).all()


async def get_groups_by_ids(ids):
    return await Group.objects.filter(group_id__in=ids).all()


async def get_users_by_themes(ids: List[int]) -> List[int]:
    themes = await get_themes_by_ids(ids)
    return [
        filter.user.id
        for theme in themes
        for filter in await theme.in_admin_filters.prefetch_related('user').all()
        if filter.user.is_admin is False
    ]
