from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from config.dependencies import dp
from db import user as user_db, filters as filters_db

from . import commands, keyboards
from .states import AdminState


@dp.message_handler(text=keyboards.MENU_FILTERS_BUTTON, chat_type=ChatType.PRIVATE, state=AdminState.base)
@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.SET_FILTERS_COMMAND.text], state=AdminState)
async def filters_menu_button(message: types.Message):
    ''' Вызов меню фильтров через кнопку меню или команду '''
    user = await user_db.get_or_create_user(message.from_user)
    await filters_db.get_or_create_filter(user)
    await AdminState.set_filters.set()


@dp.message_handler(text=keyboards.FILTERS_THEME_BUTTON, chat_type=ChatType.PRIVATE, state=AdminState.set_filters)
async def theme_to_select_list_menu_button(message: types.Message, state: FSMContext):
    ''' Вывод списка тем по нажатию клавиши в меню '''
    await AdminState.themes_filters.set()
