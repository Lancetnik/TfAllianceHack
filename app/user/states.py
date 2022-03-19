from tg.states import StatesGroup, State

from . import senders


class BaseState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        await senders.send_user_menu(context.user)
        await context.update_data({
            'prev_state': []
        })


class ThemesFiltersState(State):
    async def set(self, context=None, history=True):
        context = await super().set(context=context, history=history)
        selected_themes = set((await context.get_data()).get('selected_themes', []))
        await senders.send_user_themes_menu(context.user, exclude=selected_themes, is_admin=False)


class UserState(StatesGroup):
    base = BaseState()
    themes_filters = ThemesFiltersState()
    chat = State()
