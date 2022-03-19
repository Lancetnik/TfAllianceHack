from aiogram import types

from .models import User


async def get_user(user_id: int) -> User:
    return await User.objects.get_or_none(id=user_id)


async def delete_user(user: User):
    for i in await user.admin_filters.all():
        await i.delete()

    for i in await user.user_messages.all():
        await i.delete()

    for i in await user.watched.all():
        await i.delete()

    for i in await user.descriptions.all():
        await i.delete()

    await user.delete()


async def get_user_raw(**kwargs) -> User:
    return await User.objects.get_or_none(**kwargs)


async def get_or_create_user(user: types.User) -> User:
    return await User.objects.get_or_create(
        id=user.id, first_name=user.first_name,
        last_name=user.last_name, username=user.username,
        language_code=user.language_code or None
    )
