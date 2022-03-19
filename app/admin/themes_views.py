from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from config.dependencies import dp
from base.messages import THEME_BUTTON_MODIFIER
from base import senders as base_senders
from db import themes as theme_db, user as user_db, filters as filters_db
from tg.senders import send_message, edit_message, get_theme_url, edit_keyboard
from utils.messages import removesuffix

from .states import AdminState
from . import keyboards, commands, messages, senders


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.themes_filters)
async def choose_theme_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку выбора темы из меню '''
    theme_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    theme = await theme_db.get_theme_by_name(theme_name)

    user = await user_db.get_user(message.from_user.id)
    await filters_db.add_theme(user, theme.id)

    async with state.proxy() as data:
        selected_themes = set(data.get('selected_themes', []) + [theme.id])
        data['selected_themes'] = list(selected_themes)

    await base_senders.send_user_filters(user.id)
    await senders.send_themes_menu(user.id, exclude=selected_themes)


@dp.message_handler(text=keyboards.MENU_THEME_BUTTON, chat_type=ChatType.PRIVATE, state=AdminState.base)
@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.THEME_LIST_COMMAND.text], state=AdminState)
async def theme_list_menu_button(message: types.Message):
    ''' Вывод списка тем по нажатию клавиши в меню или через команду '''
    await AdminState.themes.set()


@dp.message_handler(text=keyboards.NEW_THEME_BUTTON, chat_type=ChatType.PRIVATE, state=AdminState.themes)
@dp.message_handler(text=keyboards.NEW_THEME_BUTTON, chat_type=ChatType.PRIVATE, state=AdminState.themes_filters)
@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.CREATE_THEME_COMMAND.text], state=AdminState)
async def create_theme_command(message: types.Message):
    ''' Создание новой темы по нажатию клавиши в меню или через команду '''
    await AdminState.input_theme.set()
    await senders.create_theme_message(message.chat.id)


@dp.callback_query_handler(
    text_startswith=[commands.CREATE_THEME_URL.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def create_theme_url(query: types.CallbackQuery, state: FSMContext):
    ''' Формирование ссылки на бота с темой '''
    theme = await commands.CREATE_THEME_URL.parse(query.data)
    async with state.proxy() as data:
        data['theme_to_send'] = theme.id
    await senders.send_theme_url(query.from_user.id, await get_theme_url(theme.uuid))


@dp.callback_query_handler(
    text=commands.SEND_OUT_THEME_URL.text, chat_type=ChatType.PRIVATE, state=AdminState)
async def send_theme_url(query: types.CallbackQuery, state: FSMContext):
    ''' Перенаправление ссылки '''
    async with state.proxy() as data:
        data['themes_to_send'] = []
        data['channels_to_send'] = []
        data['groups_to_send'] = []
    await AdminState.send_messages.set()


@dp.callback_query_handler(
    text_startswith=[commands.SHOW_THEME_DESCRIPTION.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def show_theme_description(query: types.CallbackQuery, state: FSMContext):
    ''' Вывод описания темы по нажатию на кнопку под сообщением'''
    theme = await commands.SHOW_THEME_DESCRIPTION.parse(query.data)
    _, is_not_empty = await senders.send_theme_description(query.message.chat.id, theme, keyboard=None)
    if is_not_empty is False:
        async with state.proxy() as data:
            data['theme_to_edit'] = theme.id
        await AdminState.edit_description.set()


@dp.callback_query_handler(
    text_startswith=[commands.EDIT_THEME_DESCRIPTION.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def edit_theme_description_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Изменение описания темы по нажатию на кнопку под сообщением '''
    theme = await commands.EDIT_THEME_DESCRIPTION.parse(query.data)
    async with state.proxy() as data:
        data['theme_to_edit'] = theme.id
    await AdminState.edit_description.set()


@dp.callback_query_handler(
    text_startswith=[commands.SHOW_THEME.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def make_theme_public(query: types.CallbackQuery):
    ''' Сделать тему публичной '''
    theme = await commands.SHOW_THEME.parse(query.data)
    await theme.update(is_public=True)
    await edit_keyboard(
        query.from_user.id, query.message.message_id, await senders.get_theme_keyboard(theme)
    )


@dp.callback_query_handler(
    text_startswith=[commands.HIDE_THEME.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def make_theme_provat(query: types.CallbackQuery, state):
    ''' Сделать тему приватной '''
    theme = await commands.HIDE_THEME.parse(query.data)
    await theme.update(is_public=False)
    await edit_keyboard(
        query.from_user.id, query.message.message_id, await senders.get_theme_keyboard(theme)
    )


@dp.callback_query_handler(text='cancel_theme_creation', chat_type=ChatType.PRIVATE, state=AdminState.edit_description)
async def cancel_description_theme_creation_inline_button(query: types.CallbackQuery):
    ''' Отмена создания описания темы после нажатия на кнопку под сообщением '''
    await send_message(query.message.chat.id, messages.DESCRIPTION_THEME_CREATION_CANCELED)
    await AdminState.previous()


@dp.message_handler(chat_type=ChatType.PRIVATE, state=AdminState.edit_description, content_types=types.ContentType.ANY)
async def edit_theme_description(message: types.Message, state: FSMContext):
    ''' Изменение описания темы '''
    async with state.proxy() as data:
        theme = await theme_db.get_theme(data['theme_to_edit'])
        data['theme_to_edit'] = None

    await theme_db.update_or_create_theme_description(theme, message)
    await senders.succesful_edit_description(message.chat.id)
    await AdminState.previous()


@dp.callback_query_handler(text='cancel_theme_creation', chat_type=ChatType.PRIVATE, state=AdminState.input_theme)
@dp.callback_query_handler(text='cancel_theme_creation', chat_type=ChatType.PRIVATE, state=AdminState.edit_theme)
async def cancel_theme_creation_inline_button(query: types.CallbackQuery):
    ''' Отмена создания темы после нажатия на кнопку под сообщением '''
    await send_message(query.message.chat.id, messages.THEME_CREATION_CANCELED)
    await AdminState.previous()


@dp.message_handler(text_endswith=[THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.themes)
async def select_theme_button(message: types.Message):
    ''' Захват нажатия на кнопку выбора темы из меню '''
    theme_name = removesuffix(message.text, THEME_BUTTON_MODIFIER)
    theme = await theme_db.get_theme_by_name(theme_name)
    await senders.send_theme_message(message.chat.id, theme)


@dp.callback_query_handler(text_startswith=[commands.DELETE_THEME_INLINE.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def delete_theme_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Удаление темы по нажатию на кнопку под сообщением '''
    theme = await commands.DELETE_THEME_INLINE.parse(query.data)
    response = await _delete_theme(theme, state)
    user = await user_db.get_or_create_user(query.from_user)
    await senders.theme_deleted(user, theme)
    await edit_message(
        query.message.chat.id, query.message.message_id, response
    )


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.DELETE_THEME_COMMAND.text], state=AdminState)
async def delete_theme_command(message: types.Message, state: FSMContext):
    ''' Удаление темы с помощью команды '''
    theme = await commands.DELETE_THEME_COMMAND.parse(message.text)
    response = await _delete_theme(theme, state)
    user = await user_db.get_or_create_user(message.from_user)
    await senders.theme_deleted(user, theme)
    await send_message(message.chat.id, response)


@dp.callback_query_handler(
    text_startswith=[commands.EDIT_THEME_NAME.text], chat_type=ChatType.PRIVATE, state=AdminState.themes)
async def edit_theme_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Редактирование темы по нажатию на кнопку под сообщением '''
    theme = await commands.EDIT_THEME_NAME.parse(query.data)
    if theme is not None:
        await AdminState.edit_theme.set()
        await senders.create_theme_message(query.message.chat.id)
        async with state.proxy() as data:
            data['theme'] = theme.id
    else:
        await send_message(query.message.chat.id, messages.THEME_NOT_FOUND)


@dp.message_handler(chat_type=ChatType.PRIVATE, state=AdminState.edit_theme)
async def input_new_theme_name(message: types.Message, state: FSMContext):
    ''' Ввод нового названия редактируемой темы '''
    async with state.proxy() as data:
        theme = await theme_db.get_theme(data['theme'])
        data['theme'] = None

    if theme:
        await theme.update(name=message.text)
        await senders.send_theme_message(message.chat.id, theme)
    else:
        await send_message(message.chat.id, messages.THEME_NOT_FOUND)

    await AdminState.previous()


@dp.message_handler(chat_type=ChatType.PRIVATE, state=AdminState.input_theme)
async def input_theme_to_create(message: types.Message, state: FSMContext):
    ''' Ввод названия новой темы '''
    theme = await theme_db.create_theme(message.text)
    await send_message(message.chat.id, messages.THEME_CREATED % theme)
    user = await user_db.get_or_create_user(message.from_user)
    await senders.theme_created(user, theme)
    await senders.send_theme_message(message.chat.id, theme)
    await AdminState.previous()


async def _delete_theme(theme, state) -> str:
    if theme is not None:
        response = messages.THEME_DELETED % theme
        await theme_db.delete_theme(theme)

        state_name = await state.get_state()
        if state_name == AdminState.themes.state or \
                state_name == AdminState.themes_filters.state:
            await senders.send_themes_menu(state.chat)

    else:
        response = messages.THEME_NOT_FOUND
    return response


@dp.my_chat_member_handler()
async def add_bot_to_channel(update: types.ChatMemberUpdated):
    chat = update.chat
    status = update.new_chat_member.status
    if chat.type == "channel":
        await theme_db.create_channel(chat, status)
    elif chat.type == "group":
        await theme_db.create_group(chat, status)
