from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from config.dependencies import dp, storage
from db import themes as theme_db
from superuser.commands import KICK_ADMIN_COMMAND
from tg.senders import send_message, copy_message, reply_message, get_theme_url
from user.states import UserState
from user import senders as usr_senders
from utils.keyboards import construct_inline_keyboard
from utils.messages import removesuffix

from . import keyboards, messages, senders, commands
from .states import AdminState


@dp.message_handler(text=keyboards.MESSAGES_MENU, chat_type=ChatType.PRIVATE, state=AdminState.base)
async def messages_menu_button(message: types.Message):
    ''' Переход в меню сообщений '''
    await AdminState.message_menu.set()


@dp.message_handler(text=keyboards.WATCH_MESSAGES, chat_type=ChatType.PRIVATE, state=AdminState.message_menu)
async def watch_messages_menu_button(message: types.Message):
    ''' Переход в меню просмотра сообщений '''
    await AdminState.watch_messages.set()


@dp.callback_query_handler(
    text_startswith=[commands.DAY_MESSAGES.text], chat_type=ChatType.PRIVATE, state=AdminState.watch_messages)
async def watch_messages_by_day(query: types.CallbackQuery):
    ''' Просмотр сообщений по теме за последний день '''
    theme = await commands.DAY_MESSAGES.parse(query.data)
    await senders.send_messages_by_theme(query.from_user.id, theme, day='day')


@dp.callback_query_handler(
    text_startswith=[commands.THREE_DAYS_MESSAGES.text], chat_type=ChatType.PRIVATE, state=AdminState.watch_messages)
async def watch_messages_by_3days(query: types.CallbackQuery):
    ''' Просмотр сообщений по теме за три последних дня '''
    theme = await commands.THREE_DAYS_MESSAGES.parse(query.data)
    await senders.send_messages_by_theme(query.from_user.id, theme, day='3day')


@dp.callback_query_handler(
    text_startswith=[commands.WEEK_MESSAGES.text], chat_type=ChatType.PRIVATE, state=AdminState.watch_messages)
async def watch_messages_by_week(query: types.CallbackQuery):
    ''' Просмотр сообщений по теме за неделю '''
    theme = await commands.WEEK_MESSAGES.parse(query.data)
    await senders.send_messages_by_theme(query.from_user.id, theme, day='week')


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.watch_messages)
async def choose_theme_messages_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку выбора темы из меню сообщений '''
    theme_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    async with state.proxy() as data:
        data['theme_messages'] = theme_name
    await AdminState.choouse_user.set()


@dp.message_handler(text=keyboards.SEE_ALL_MESSAGES, chat_type=ChatType.PRIVATE, state=AdminState.choouse_user)
async def see_all_messages_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку просмотра всех сообщений из меню сообщений '''
    async with state.proxy() as data:
        theme_name = data['theme_messages']
        data['theme_messages'] = None
    theme = await theme_db.get_theme_by_name(theme_name)
    await senders.send_messages_by_theme(message.from_user.id, theme)
    await AdminState.previous()


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.choouse_user)
async def see_user_messages(message: types.Message, state: FSMContext):
    user_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    user, _ = await KICK_ADMIN_COMMAND.parse(user_name, is_admin=False)
    async with state.proxy() as data:
        theme_name = data['theme_messages']
    theme = await theme_db.get_theme_by_name(theme_name)
    await senders.send_messages_by_theme(message.from_user.id, theme, user, check=False)


@dp.callback_query_handler(
    text_startswith=[commands.REPLY.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def reply_to_message_handler(query: types.CallbackQuery, state: FSMContext):
    ''' Ответить на конкретное сообщение '''
    await AdminState.reply_user.set()
    await send_message(query.from_user.id, messages.REPLY_TO_USER, reply_markup=construct_inline_keyboard({
        messages.CANCEL_BUTTON: 'cancel_reply'
    }))
    async with state.proxy() as data:
        data['reply_to'] = await commands.REPLY.parse(query.data)


@dp.callback_query_handler(
    text='cancel_reply', chat_type=ChatType.PRIVATE, state=AdminState.reply_user)
async def cancel_reply_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Отмена ответа пользователю '''
    await send_message(query.message.chat.id, messages.REPLY_CANCELED)
    await AdminState.previous()
    async with state.proxy() as data:
        data['reply_to'] = None


@dp.message_handler(chat_type=ChatType.PRIVATE, state=AdminState.reply_user, content_types=types.ContentType.ANY)
async def send_reply_to_user(message: types.Message, state: FSMContext):
    ''' Ответ пользователю '''
    async with state.proxy() as data:
        msg_id, usr_id = await commands.REPLY.parse_data(data['reply_to'])
        data['reply_to'] = None

    await copy_message(
        usr_id, message.chat.id,
        message.message_id, reply_to_message_id=msg_id
    )

    await send_message(message.chat.id, messages.USER_REPLIED)
    await AdminState.previous()


@dp.callback_query_handler(
    text_startswith=[commands.CHAT.text], chat_type=ChatType.PRIVATE, state=AdminState)
async def start_chat_with_user(query: types.CallbackQuery, state: FSMContext):
    ''' Создать чат с пользователем '''
    msg_id, usr_id = await commands.CHAT.parse(query.data)

    await AdminState.chat.set()
    await send_message(query.from_user.id, messages.REPLY_TO_USER, reply_markup=construct_inline_keyboard({
        messages.CLOSE_CHAT_BUTTON: 'close_chat'
    }))

    await reply_message(usr_id, msg_id, messages.ADMIN_STARTED_CHAT)
    user_context = FSMContext(storage, usr_id, usr_id)
    await UserState.chat.set(context=user_context)
    async with user_context.proxy() as data:
        data['chat_with'] = query.from_user.id

    async with state.proxy() as data:
        data['chat_with'] = (msg_id, usr_id)


@dp.callback_query_handler(
    text='close_chat', chat_type=ChatType.PRIVATE, state=AdminState.chat)
async def close_chat_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Закрыть чат с пользователем '''
    async with state.proxy() as data:
        msg_id, usr_id = await commands.CHAT.parse_data(data['chat_with'])
        data['chat_with'] = None

    user_context = FSMContext(storage, usr_id, usr_id)
    await UserState.base.set(context=user_context)
    async with user_context.proxy() as data:
        data['chat_with'] = None

    await send_message(usr_id, messages.ADMIN_CLOSE_CHAT)
    await send_message(query.message.chat.id, messages.CHAT_CLOSED)
    await AdminState.previous()


@dp.message_handler(chat_type=ChatType.PRIVATE, state=AdminState.chat, content_types=types.ContentType.ANY)
async def send_message_to_chat(message: types.Message, state: FSMContext):
    ''' Сообщение в чат пользователю '''
    async with state.proxy() as data:
        msg_id, usr_id = await commands.CHAT.parse_data(data['chat_with'])
    await copy_message(usr_id, message.chat.id, message.message_id)
    await send_message(message.chat.id, messages.USER_REPLIED)


@dp.message_handler(text=keyboards.SEND_MESSAGES, chat_type=ChatType.PRIVATE, state=AdminState.message_menu)
async def send_messages_menu_button(message: types.Message, state: FSMContext):
    ''' Переход в меню отправки сообщений '''
    async with state.proxy() as data:
        data['themes_to_send'] = []
        data['channels_to_send'] = []
        data['groups_to_send'] = []
    await AdminState.send_messages.set()


@dp.message_handler(text=keyboards.SEND_TO_CHANNEL, chat_type=ChatType.PRIVATE, state=AdminState.send_messages)
async def send_messages_to_channel_menu_button(message: types.Message, state: FSMContext):
    ''' Выбор канала для отправки '''
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []))
        selected_groups = set(data.get('groups_to_send', []))
        selected_channels = set(data.get('channels_to_send', []))
        await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, selected_groups)
    await AdminState.choose_channel.set()


@dp.message_handler(text=keyboards.SEND_TO_GROUP, chat_type=ChatType.PRIVATE, state=AdminState.send_messages)
async def send_messages_to_group_menu_button(message: types.Message, state: FSMContext):
    ''' Выбор группы для отправки '''
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []))
        selected_groups = set(data.get('groups_to_send', []))
        selected_channels = set(data.get('channels_to_send', []))
        await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, selected_groups)
    await AdminState.choose_group.set()


@dp.message_handler(text=keyboards.SEND_TO_THEME, chat_type=ChatType.PRIVATE, state=AdminState.send_messages)
async def send_messages_to_theme_menu_button(message: types.Message, state: FSMContext):
    ''' Выбор темы для отправки '''
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []))
        selected_groups = set(data.get('groups_to_send', []))
        selected_channels = set(data.get('channels_to_send', []))
        await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, selected_groups)
    await AdminState.choose_theme.set()


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.choose_theme)
async def choose_theme_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку выбора темы из меню '''
    theme_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    theme = await theme_db.get_theme_by_name(theme_name)
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []) + [theme.id])
        selected_groups = set(data.get('groups_to_send', []))
        selected_channels = set(data.get('channels_to_send', []))
        data['themes_to_send'] = list(selected_themes)
    await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, selected_groups)
    await usr_senders.send_user_themes_menu(message.from_user.id, exclude=selected_themes)


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.choose_group)
async def choose_group_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку выбора группы из меню '''
    group_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    group = await theme_db.get_group_by_name(group_name)
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []))
        selected_groups = set(data.get('groups_to_send', []) + [group.group_id])
        selected_channels = set(data.get('channels_to_send', []))
        data['groups_to_send'] = list(selected_groups)
    await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, selected_groups)
    await senders.send_groups_keyboard(message.from_user.id, exclude=selected_groups)


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=AdminState.choose_channel)
async def choose_channel_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку выбора каналов из меню '''
    channel_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    channel = await theme_db.get_channel_by_name(channel_name)
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []))
        selected_groups = set(data.get('groups_to_send', []))
        selected_channels = set(data.get('channels_to_send', []) + [channel.channel_id])
        data['channels_to_send'] = list(selected_channels)
    await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, selected_groups)
    await senders.send_channel_keyboard(message.from_user.id, exclude=selected_channels)


@dp.message_handler(text=keyboards.MENU_CLEAR, chat_type=ChatType.PRIVATE, state=AdminState.choose_theme)
async def clear_themes_menu_button(message: types.Message, state: FSMContext):
    ''' Сброс тем при нажатии на кнопку в меню '''
    async with state.proxy() as data:
        data['themes_to_send'] = []
        selected_channels = set(data.get('channels_to_send', []))
        selected_groups = set(data.get('groups_to_send', []))

    await send_message(message.chat.id, messages.DESTINATION_THEMES_CLEARED)
    await senders.send_settings_to_send(message.from_user.id, [], selected_channels, selected_groups)
    await usr_senders.send_user_themes_menu(message.from_user.id)


@dp.message_handler(text=keyboards.MENU_CLEAR, chat_type=ChatType.PRIVATE, state=AdminState.choose_channel)
async def clear_channels_menu_button(message: types.Message, state: FSMContext):
    ''' Сброс каналов при нажатии на кнопку в меню '''
    async with state.proxy() as data:
        data['channels_to_send'] = []
        selected_themes = set(data.get('themes_to_send', []))
        selected_groups = set(data.get('groups_to_send', []))

    await send_message(message.chat.id, messages.DESTINATION_CHANNELS_CLEARED)
    await senders.send_settings_to_send(message.from_user.id, selected_themes, [], selected_groups)
    await senders.send_channel_keyboard(message.from_user.id)


@dp.message_handler(text=keyboards.MENU_CLEAR, chat_type=ChatType.PRIVATE, state=AdminState.choose_group)
async def clear_groups_menu_button(message: types.Message, state: FSMContext):
    ''' Сброс групп при нажатии на кнопку в меню '''
    async with state.proxy() as data:
        data['groups_to_send'] = []
        selected_channels = set(data.get('channels_to_send', []))
        selected_themes = set(data.get('themes_to_send', []))

    await send_message(message.chat.id, messages.DESTINATION_GROUPS_CLEARED)
    await senders.send_settings_to_send(message.from_user.id, selected_themes, selected_channels, [])
    await senders.send_groups_keyboard(message.from_user.id)


@dp.message_handler(text=keyboards.SEND_MESSAGE, chat_type=ChatType.PRIVATE, state=AdminState.send_messages)
async def handle_send_message_menu_button(message: types.Message, state: FSMContext):
    ''' Переход в режим отправки сообщения '''
    async with state.proxy() as data:
        if (theme_id := data.get('theme_to_send')):
            theme_id = int(theme_id)
            theme = await theme_db.get_theme(theme_id)
            url = await get_theme_url(theme.uuid)

            for user_id in await get_destination(state):
                msg, _ = await senders.send_theme_description(user_id, theme, keyboard=None)
                await reply_message(user_id, msg.message_id, messages.CAN_REPLY % (theme.name, url))

            await send_message(message.chat.id, messages.MESSAGE_SENDED)
            await AdminState.previous()

            data['theme_to_send'] = None
        else:
            selected_themes = set(data.get('themes_to_send', []))
            selected_groups = set(data.get('groups_to_send', []))
            selected_channels = set(data.get('channels_to_send', []))
            await senders.send_settings_to_send(
                message.from_user.id, selected_themes,
                selected_channels, selected_groups
            )
            await AdminState.handle_message.set()


@dp.callback_query_handler(text='cancel_messaging', chat_type=ChatType.PRIVATE, state=AdminState.handle_message)
async def cancel_messaging_inline_button(query: types.CallbackQuery):
    ''' Отмена отправки сообщения '''
    await send_message(query.from_user.id, messages.MESSAGING_CANCELED)
    await AdminState.previous()


@dp.message_handler(chat_type=ChatType.PRIVATE, state=AdminState.handle_message)
async def message_to_send(message: types.Message, state: FSMContext):
    ''' Захват сообщения для отправки '''
    for user_id in await get_destination(state):
        await copy_message(user_id, message.chat.id, message.message_id)

    await send_message(message.chat.id, messages.MESSAGE_SENDED)
    await AdminState.previous()


@dp.message_handler(text=keyboards.MENU_CLEAR, chat_type=ChatType.PRIVATE, state=AdminState.send_messages)
async def clear_filters(message: types.Message, state: FSMContext):
    ''' Очистка адресатов '''
    await get_destination(state)
    await send_message(message.chat.id, messages.DESTINATION_CLEARED)


async def get_destination(state):
    async with state.proxy() as data:
        selected_themes = set(data.get('themes_to_send', []))
        data['themes_to_send'] = []
        selected_groups = set(data.get('groups_to_send', []))
        data['groups_to_send'] = []
        selected_channels = set(data.get('channels_to_send', []))
        data['channels_to_send'] = []

    destinations = set(await theme_db.get_users_by_themes(selected_themes))
    destinations |= selected_groups
    destinations |= selected_channels

    return destinations
