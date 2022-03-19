from tg.commands import Command, classproperty

from db.themes import get_theme, get_theme_by_name
from db.messages import get_message
from utils.messages import removeprefix


class ADMIN_REQUEST_COMMAND(Command):
    text = 'admin'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - отправить заявку на администрирование компании'


class CREATE_THEME_COMMAND(Command):
    text = 'theme'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - создать тему'


class DELETE_THEME_COMMAND(Command):
    text = 'delete'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} [theme] - удалить тему'

    @classmethod
    async def parse(cls, text: str):
        theme_name = removeprefix(text, f'/{cls.text}')
        return await get_theme_by_name(theme_name.strip())


class THEME_LIST_COMMAND(Command):
    text = 'themes'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - получить список тем'


class SET_FILTERS_COMMAND(Command):
    text = 'filters'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - установить отслеживаемые темы'


class DELETE_THEME_INLINE(Command):
    text = 'delete_theme_'
    name = ''

    @classmethod
    async def parse(cls, text: str):
        theme_id = int(removeprefix(text, cls.text))
        return await get_theme(theme_id)

    @classmethod
    def __str__(cls):
        return cls.name


class REPLY(Command):
    text = 'reply_'
    name = 'Ответить'

    @classmethod
    async def parse(cls, text: str) -> (int, int):
        text = removeprefix(text, cls.text)
        if len(data := text.split('_')) == 1:
            user_message = await get_message(int(text))
            return user_message.message_id, user_message.user.id
        else:
            return int(data[0]), int(data[1])

    @classmethod
    async def parse_data(cls, data: (int, int)) -> (int, int):
        if data[1] is None:
            user_message = await get_message(int(data[0]))
            return user_message.message_id, user_message.user.id
        else:
            return int(data[0]), int(data[1])


class CHAT(REPLY):
    text = 'chat_with_'
    name = 'Создать чат'


class SEND_OUT_THEME_URL(Command):
    text = 'send_theme_'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - разослать ссылку на бота'


class SHOW_THEME(DELETE_THEME_INLINE):
    text = 'show_theme_'
    name = 'Сделать публичной'


class HIDE_THEME(DELETE_THEME_INLINE):
    text = 'hide_theme_'
    name = 'Сделать приватной'


class CREATE_THEME_URL(DELETE_THEME_INLINE):
    text = 'create_theme_url_description_'


class SHOW_THEME_DESCRIPTION(DELETE_THEME_INLINE):
    text = 'show_theme_description_'


class EDIT_THEME_DESCRIPTION(DELETE_THEME_INLINE):
    text = 'edit_theme_description_'


class SET_THEME(DELETE_THEME_INLINE):
    text = 'set_theme_filter_'


class EDIT_THEME_NAME(DELETE_THEME_INLINE):
    text = 'edit_theme_'


class DAY_MESSAGES(DELETE_THEME_INLINE):
    text = 'watch_by_day_'
    name = 'Вчера'


class THREE_DAYS_MESSAGES(DELETE_THEME_INLINE):
    text = 'watch_by_3days_'
    name = '3 дня'


class WEEK_MESSAGES(DELETE_THEME_INLINE):
    text = 'watch_by_week_'
    name = 'Неделя'
