from tg.states import StatesGroup, State

from base import senders as base_senders
from db import themes as theme_db, messages as msg_db
from user import senders as usr_senders
from . import senders


class BaseState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_admin_menu(context.user)
        await context.update_data({
            'prev_state': []
        })


class ThemesState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_themes_menu(context.user)


class FiltersState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await base_senders.send_user_filters(context.user)
        await base_senders.send_filters_menu(context.user)


class ThemesFiltersState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        selected_themes = set((await context.get_data()).get('selected_themes', []))
        await senders.send_themes_menu(context.user, exclude=selected_themes)


class MessagesState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_watch_messages_menu(context.user)


class EditDescriptionState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.edit_description_message(context.user)


class MessagesMenuState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_messages_menu(context.user)


class SendMessagesState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_broadcast_messages_menu(context.user)


class HandleMessagesState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_handle_message(context.user)


class ChooseChannelState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_channel_keyboard(
            context.user, set((await context.get_data()).get('channels_to_send', []))
        )


class ChooseThemeState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await usr_senders.send_user_themes_menu(
            context.user, set((await context.get_data()).get('themes_to_send', []))
        )


class ChooseGroupState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_groups_keyboard(
            context.user, set((await context.get_data()).get('groups_to_send', []))
        )


class ChooseUserState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        async with context.proxy() as data:
            theme_name = data['theme_messages']
            theme = await theme_db.get_theme_by_name(theme_name)
            watched = await msg_db.get_or_create_watched(context.user, theme)
            messages = await msg_db.get_messages(theme, time=watched.datetime)
            users = set(i.user for i in messages)
            await senders.send_message_users(context.user, users)


class AdminState(StatesGroup):
    base = BaseState()

    themes = ThemesState()
    input_theme = State()
    edit_theme = State()
    edit_description = EditDescriptionState()

    set_filters = FiltersState()
    themes_filters = ThemesFiltersState()

    message_menu = MessagesMenuState()

    watch_messages = MessagesState()
    choouse_user = ChooseUserState()
    reply_user = State()
    chat = State()

    send_messages = SendMessagesState()
    handle_message = HandleMessagesState()
    choose_channel = ChooseChannelState()
    choose_theme = ChooseThemeState()
    choose_group = ChooseGroupState()
