from asyncio import get_event_loop
from datetime import datetime
from typing import Optional, List
from uuid import UUID

import ormar

from . import metadata, database, connect_db
from base.messages import USER, USER_FULL


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"
        table_args = {'extend_existing': True}

    id: int = ormar.BigInteger(primary_key=True)
    first_name: str = ormar.Text(length=128)
    last_name: Optional[str] = ormar.Text(length=128, nullable=True)
    username: Optional[str] = ormar.Text(length=128, nullable=True)
    language_code: Optional[str] = ormar.Text(length=2, nullable=True)

    is_admin: bool = ormar.Boolean(default=False)
    is_owner: bool = ormar.Boolean(default=False)

    def __hash__(self):
        return self.id

    @property
    def tg_name(self):
        if self.username is not None:
            return f'@{self.username}'
        else:
            return self.raw_name

    @property
    def name(self):
        if self.username is not None:
            return f'@{self.username}'
        else:
            return USER_FULL.from_user(self)

    def __eq__(self, other):
        return self.id == other.id

    @property
    def raw_name(self):
        return USER.from_user(self)


class Theme(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'company_theme'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.Text(length=128, unique=True)
    is_public: bool = ormar.Boolean(default=False)
    uuid: UUID = ormar.UUID(nullable=False, unique=True)

    def __str__(self):
        return self.name


class ThemeDescription(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'theme_description'

    id: int = ormar.Integer(primary_key=True)
    message_id: int = ormar.BigInteger()
    user: User = ormar.ForeignKey(
        User, nullable=False, related_name='descriptions'
    )
    theme: Theme = ormar.ForeignKey(
        Theme, unique=True, related_name='description'
    )


class AdminFilter(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'admin_filters'

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(
        User, nullable=False, unique=True, related_name='admin_filters'
    )
    themes: List[Optional[Theme]] = ormar.ManyToMany(
        Theme, related_name='in_admin_filters'
    )


class SendedMessage(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'sended_message'

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(
        User, nullable=False, related_name='user_messages'
    )
    theme: Theme = ormar.ForeignKey(
        Theme, nullable=False, related_name='messages'
    )
    message_id: int = ormar.BigInteger()
    datetime: datetime = ormar.DateTime()


class WatchedThemes(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'watche_themes'

    id: int = ormar.Integer(primary_key=True)
    user: User = ormar.ForeignKey(
        User, nullable=False, related_name='watched'
    )
    theme: Theme = ormar.ForeignKey(
        Theme, nullable=False, related_name='watched'
    )
    datetime: datetime = ormar.DateTime(nullable=True)


class Group(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'groups'

    id: int = ormar.Integer(primary_key=True)
    group_id: int = ormar.BigInteger()
    title: str = ormar.Text(length=128)


class Channel(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'channels'

    id: int = ormar.Integer(primary_key=True)
    channel_id: int = ormar.BigInteger()
    title: str = ormar.Text(length=128)


get_event_loop().run_until_complete(connect_db())
