from typing import Dict, AsyncGenerator
from functools import partial

from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from admin.states import AdminState
from config.dependencies import storage
from db.models import User
from db.company import get_company_owners
from tg.senders import send_message, edit_message
from utils.keyboards import construct_inline_keyboard

from . import messages


async def _sending_message_to_owners(text: str, exclude=set(), **kwargs) -> (User, AsyncGenerator[Message, Message]):
    for owner in await get_company_owners():
        if owner.id in exclude:
            continue
        else:
            yield owner, await send_message(owner.id, text, **kwargs)


async def send_message_to_owners(text: str, **kwargs):
    async for _ in _sending_message_to_owners(text, **kwargs):
        pass


async def _send_request_to_owners(user: User, text: str, **kwargs):
    async for owner, message in _sending_message_to_owners(
        text=text % user.raw_name, **kwargs
    ):
        admin_context = FSMContext(storage, owner.id, owner.id)
        async with admin_context.proxy() as data:
            old_messages = data.get(str(user.id), [])
            data[user.id] = old_messages + [message.message_id]


send_admin_request = partial(_send_request_to_owners, 
    text = messages.ADMIN_REQUEST_NOTIFICATION,
    parse_mode ='html',
    reply_markup = construct_inline_keyboard({
        messages.CONFIRM_BUTTON: 'confirm_admin',
        messages.DENY_BUTTON: 'deny_admin'
    }, {
        messages.MAKE_OWNER_BUTTON: 'make_owner'
    })
)

send_superuser_request = partial(_send_request_to_owners,
    text = messages.OWNER_REQUEST_NOTIFICATION,
    parse_mode = 'html',
    reply_markup = construct_inline_keyboard({
        messages.CONFIRM_BUTTON: 'make_owner',
        messages.DENY_BUTTON: 'deny_admin'
    }, {
        messages.MAKE_ADMIN_BUTTON: 'confirm_admin',
    })
)


async def _edit_admins_notifications(user, admin, text, confirm_text, keyboard=None, state=None):
    for owner in await get_company_owners():
        owner_storage = FSMContext(storage, owner.id, owner.id)
        async with owner_storage.proxy() as data:
            messages = data.get(str(admin.id), [])
            for message_id in messages:
                await edit_message(
                    chat_id=owner.id, message_id=message_id,
                    text=text % (admin.tg_name, user.tg_name)
                )
            data[admin.id] = []

    await send_message(admin.id, confirm_text, reply_markup=keyboard)
    if state is not None:
        user_context = FSMContext(storage, admin.id, admin.id)
        await state.set(context=user_context)


confirm_admin = partial(_edit_admins_notifications,
    text=messages.ADMIN_CONFIRMED_NOTIFICATION,
    confirm_text=messages.ADMIN_CONFIRMED_ANSWER,
    state=AdminState.base
)

deny_admin = partial(_edit_admins_notifications,
    text=messages.ADMIN_DENY_NOTIFICATION,
    confirm_text=messages.ADMIN_DENY_ANSWER
)

confirm_owner = partial(_edit_admins_notifications,
    text=messages.OWNER_CONFIRMED_NOTIFICATION,
    confirm_text=messages.OWNER_CONFIRMED_ANSWER,
    state=AdminState.base
)
