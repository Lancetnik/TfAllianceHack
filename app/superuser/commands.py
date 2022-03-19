from tg.commands import Command, classproperty
from utils.messages import removeprefix

from db.models import User
from db.user import get_user_raw


class START_SUPERUSER_COMMAND(Command):
    text = 'superuser'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - начать сессию в качестве владельца компании'


class CHECK_SUPERUSERS_COMMAND(Command):
    text = 'owners'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - список совладельцев компании'


class CHECK_ADMINS_COMMAND(Command):
    text = 'admins'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - список администраторов компании'


class KICK_ADMIN_COMMAND(Command):
    text = 'kick'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} [admin] - исключить администратора'

    @classmethod
    async def parse(cls, message: str, is_admin=True) -> (User, str):
        admin_text = removeprefix(message, f'/{cls.text}')
        admin_text_words = admin_text.split()

        admin = None
        if len(admin_text_words) == 1:
            admin = await get_user_raw(
                username=removeprefix(admin_text_words[0], '@'),
                is_admin=is_admin
            )
        elif len(admin_text_words) == 2:
            admin = await get_user_raw(
                first_name=admin_text_words[0],
                last_name=admin_text_words[1],
                is_admin=is_admin
            )
        return admin, admin_text
