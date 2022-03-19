from datetime import datetime, timedelta

from base.messages import WELCOME, USER_FULL
from db import user as user_db, themes as theme_db, messages as msg_db, models, company as company_db
from tg.senders import send_message, copy_message, forward_message, answer_message
from utils.keyboards import construct_inline_keyboard, construct_regular_keyboard, slice_by_rows

from base.messages import THEME_BUTTON_MODIFIER
from . import messages, keyboards, commands


async def send_message_users(user_id: int, users):
    keyboard = slice_by_rows(
        users, 2, lambda user: f'{USER_FULL.from_user(user)}{THEME_BUTTON_MODIFIER}'
    )
    return await send_message(user_id, messages.USERS_LIST,
        reply_markup=construct_regular_keyboard(
            (keyboards.SEE_ALL_MESSAGES, keyboards.MENU_BACK),
            *keyboard
        )
    )


async def send_themes_menu(user_id: int, exclude={}):
    return await send_message(user_id, messages.THEME_LIST,
        reply_markup=construct_regular_keyboard(
            keyboards.ADMIN_THEMES_ROW,
            *(await get_themes_inline_buttons(user_id, exclude))
        )
    )


async def send_broadcast_messages_menu(user_id: int):
    return await send_message(user_id, messages.CHOOSE_DESTINATION,
        reply_markup=keyboards.MESSAGES_SEND_KEYBOARD
    )


async def send_messages_menu(user_id: int):
    return await send_message(user_id, messages.CHOOSE_ACTION,
        reply_markup=keyboards.MESSAGES_MENU_KEYBOARD
    )


async def send_settings_to_send(user_id: int, themes_ids, channel_ids, group_ids):
    text = ''

    themes = await theme_db.get_themes_by_ids(themes_ids)
    if themes:
        text += '\nВыбранные темы:\n' + '\n'.join(tuple(f'{i+1}) {theme}' for i, theme in enumerate(themes)))

    channels = await theme_db.get_channels_by_ids(channel_ids)
    if channels:
        text += '\nВыбранные каналы:\n' + '\n'.join(tuple(f'{i+1}) {channel.title}' for i, channel in enumerate(channels)))

    groups = await theme_db.get_groups_by_ids(group_ids)
    if groups:
        text += '\nВыбранные группы:\n' + '\n'.join(tuple(f'{i+1}) {group.title}' for i, group in enumerate(groups)))

    if not text:
        text = messages.NO_DESTINATION
    else:
        text = text.strip('\n')

    await send_message(user_id, text)


async def send_channel_keyboard(user_id: int, exclude=set()):
    channels = tuple(filter(lambda x: x.channel_id not in exclude, await theme_db.get_channels()))
    keyboard = slice_by_rows(
        channels, 2, lambda channel: f'{channel.title}{THEME_BUTTON_MODIFIER}'
    )
    return await send_message(user_id, messages.THEME_LIST,
        reply_markup=construct_regular_keyboard(
            (keyboards.MENU_CLEAR, keyboards.MENU_BACK),
            *keyboard
        )
    )


async def send_groups_keyboard(user_id: int, exclude=set()):
    groups = tuple(filter(lambda x: x.group_id not in exclude, await theme_db.get_groups()))
    keyboard = slice_by_rows(
        groups, 2, lambda group: f'{group.title}{THEME_BUTTON_MODIFIER}'
    )
    return await send_message(user_id, messages.THEME_LIST,
        reply_markup=construct_regular_keyboard(
            (keyboards.MENU_CLEAR, keyboards.MENU_BACK),
            *keyboard
        )
    )


async def send_watch_messages_menu(user_id: int):
    return await send_message(user_id, messages.THEME_LIST,
        reply_markup=construct_regular_keyboard(
            (keyboards.MENU_BACK,),
            *(await get_themes_inline_buttons(user_id))
        )
    )


async def send_handle_message(user_id: int):
    return await send_message(
        user_id, messages.INPUT_MESSAGE,
        reply_markup=keyboards.CANCEL_MESSAGING_KEYBOARD
    )


async def theme_created(admin, theme):
    await send_message_to_admins(
        messages.THEME_CREATED_BY_ADMIN % (theme.name, admin.tg_name),
        exclude={admin.id},
        parse_mode='html'
    )


async def theme_deleted(admin, theme):
    await send_message_to_admins(
        messages.THEME_DELETED_BY_ADMIN % (theme.name, admin.tg_name),
        exclude={admin.id},
        parse_mode='html'
    )


async def send_messages_by_theme(user_id: int, theme, user=None, day=None, check=True):
    watched = await msg_db.get_or_create_watched(user_id, theme)

    if day is None:
        msgs = await msg_db.get_messages(theme, user, time=watched.datetime)
    elif day == 'day':
        await send_message(user_id, messages.LAST_DAY_MESSAGES % theme.name)
        day = datetime.now() - timedelta(days=1)
        msgs = await msg_db.get_messages(theme, user, time=datetime(
            day.year, day.month, day.day
        ))
    elif day == '3day':
        await send_message(user_id, messages.LAST_3DAYS_MESSAGES % theme.name)
        day = datetime.now() - timedelta(days=3)
        msgs = await msg_db.get_messages(theme, user, time=datetime(
            day.year, day.month, day.day
        ))
    elif day == 'week':
        await send_message(user_id, messages.LAST_WEEK_MESSAGES % theme.name)
        day = datetime.now() - timedelta(days=7)
        msgs = await msg_db.get_messages(theme, user, time=datetime(
            day.year, day.month, day.day
        ))

    if check is True:
        await watched.update(datetime=datetime.now())

    if not msgs:
        await send_message(user_id, messages.THERE_NO_MESSAGES,
            reply_markup=construct_inline_keyboard({
                commands.DAY_MESSAGES.name: f'{commands.DAY_MESSAGES.text}{theme.id}'
            }, {
                commands.THREE_DAYS_MESSAGES.name: f'{commands.THREE_DAYS_MESSAGES.text}{theme.id}'
            }, {
                commands.WEEK_MESSAGES.name: f'{commands.WEEK_MESSAGES.text}{theme.id}'
            })
        )
    else:
        for message in msgs:
            msg = await forward_message(user_id, message.user.id, message.message_id)
            await answer_message(user_id, msg.message_id,
                f'Отправлено: {message.datetime.strftime("%d.%m.%Y %H:%M")}',
                parse_mode='html',
                reply_markup=construct_inline_keyboard({
                    commands.REPLY.name: f'{commands.REPLY.text}{message.id}',
                    commands.CHAT.name: f'{commands.CHAT.text}{message.id}'
                }))


async def send_theme_message(user_id: int, theme: models.Theme):
    if theme is None:
        return await send_message(user_id, messages.THEME_NOT_FOUND)
    else:
        sr = {messages.THEME_URL: f'{commands.CREATE_THEME_URL.text}{theme.id}'}
        if theme.is_public is True:
            sr[commands.HIDE_THEME.name] = f'{commands.HIDE_THEME.text}{theme.id}'
        else:
            sr[commands.SHOW_THEME.name] = f'{commands.SHOW_THEME.text}{theme.id}'
        return await send_message(user_id, theme.name, reply_markup=await get_theme_keyboard(theme))


async def get_theme_keyboard(theme):
    sr = {messages.THEME_URL: f'{commands.CREATE_THEME_URL.text}{theme.id}'}
    if theme.is_public is True:
        sr[commands.HIDE_THEME.name] = f'{commands.HIDE_THEME.text}{theme.id}'
    else:
        sr[commands.SHOW_THEME.name] = f'{commands.SHOW_THEME.text}{theme.id}'
    return construct_inline_keyboard({
        messages.THEME_DESCRIPTION: f'{commands.SHOW_THEME_DESCRIPTION.text}{theme.id}',
        messages.EDIT_THEME_NAME: f'{commands.EDIT_THEME_NAME.text}{theme.id}'
    }, sr, {
        messages.DELETE_BUTTON: f'{commands.DELETE_THEME_INLINE.text}{theme.id}'
    })


async def create_theme_message(user_id: int):
    return await send_message(user_id,
        messages.PLEASE_INPUT_THEME,
        reply_markup=keyboards.CANCEL_THEME_CREATION_KEYBOARD
    )


async def send_admin_menu(user_id: int):
    return await send_message(user_id,
        WELCOME.from_user(await user_db.get_user(user_id)),
        reply_markup=keyboards.ADMIN_BASE_KEYBOARD
    )


async def send_theme_description(user_id: int, theme: models.Theme, keyboard=True):
    descriptions = await theme.description.all()  # not .first() -> error as empty
    if descriptions:
        description = descriptions[0]
        return await copy_message(
            user_id, description.user.id, description.message_id,
            reply_markup=construct_inline_keyboard({
                messages.EDIT_THEME_DESCRIPTION : f'{commands.EDIT_THEME_DESCRIPTION.text}{theme.id}'
            }) if keyboard is True else keyboard), True
    else:
        return await send_message(user_id, messages.THEME_DESCRIPTION_NOT_FOUND), False



async def edit_description_message(user_id: int):
    return await send_message(user_id,
        messages.PLEASE_EDIT_DESCRIPTION,
        reply_markup=keyboards.CANCEL_THEME_CREATION_KEYBOARD
    )


async def succesful_edit_description(user_id: int):
    return await send_message(user_id, messages.SUCCESFUL_EDIT_DESCRIPTION)


async def get_themes_inline_buttons(user_id: int, exclude={}, is_admin=True):
    themes = tuple(filter(lambda x: x.id not in exclude, await theme_db.get_themes(is_admin)))
    return slice_by_rows(
        themes, 2, lambda theme: f'{theme.name}{THEME_BUTTON_MODIFIER}'
    )


async def send_theme_url(user_id, url):
    return await send_message(user_id, url, reply_markup=construct_inline_keyboard({
        messages.SEND_OUT_THEME_URL: commands.SEND_OUT_THEME_URL.text
    }))


async def no_group(user_id):
    return await send_message(user_id, messages.NO_GROUPS)


async def _sending_message_to_admin(text: str, exclude=set(), **kwargs):
    for owner in await company_db.get_company_admins():
        if owner.id in exclude:
            continue
        else:
            yield owner, await send_message(owner.id, text, **kwargs)


async def send_message_to_admins(text: str, exclude=set(), **kwargs):
    async for _ in _sending_message_to_admin(text, exclude, **kwargs):
        pass
