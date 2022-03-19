from aiogram import types
from aiogram.types.chat import ChatType

from config.dependencies import dp
from db import user as user_db
from superuser.senders import send_admin_request
from tg.senders import send_message

from . import messages, commands, keyboards
from .states import AdminState


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.ADMIN_REQUEST_COMMAND.text], state='*')
async def admin_request_command(message: types.Message):
    ''' Запрос на получение роли администратора '''
    user = await user_db.get_or_create_user(message.from_user)
    if user.is_admin is False:
        await send_admin_request(user)
        response = messages.ADMIN_REQUEST_SENDED
    else:
        response = messages.ALREADY_ADMIN
    await send_message(message.chat.id, response)


@dp.message_handler(text=keyboards.MENU_BACK, chat_type=ChatType.PRIVATE, state=AdminState)
async def back_to_menu_button(message: types.Message):
    ''' Нажатие на кнопку назад в меню '''
    await AdminState.previous()
