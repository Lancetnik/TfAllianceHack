from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from config.dependencies import dp
from db import filters as filters_db, user as user_db, messages as message_db
from tg.senders import reply_message, copy_message, send_message

from . import keyboards, senders, messages
from .states import UserState


@dp.message_handler(text=keyboards.MENU_BACK, chat_type=ChatType.PRIVATE, state=UserState)
async def back_to_menu_button(message: types.Message):
    ''' Нажатие на кнопку назад в меню '''
    await UserState.previous()


@dp.message_handler(chat_type=ChatType.PRIVATE, state=UserState.base, content_types=types.ContentType.ANY)
async def send_message_to_admin(message: types.Message):
    ''' Отправка сообщения администратору '''
    user = await user_db.get_or_create_user(message.from_user)
    filters = await filters_db.get_or_create_filter(user)
    for theme in await filters.themes.all():
        await message_db.create_message(message, theme)
    await senders.send_to_admins(filters, message)
    await reply_message(message.chat.id, message.message_id, messages.MESSAGE_SENDED)


@dp.message_handler(chat_type=ChatType.PRIVATE, state=UserState.chat, content_types=types.ContentType.ANY)
async def send_message_to_chat(message: types.Message, state: FSMContext):
    ''' Сообщение в чат пользователю '''
    async with state.proxy() as data:
        admin_id = int(data['chat_with'])
    await copy_message(admin_id, message.chat.id, message.message_id)
    await send_message(message.chat.id, messages.MESSAGE_SENDED)
