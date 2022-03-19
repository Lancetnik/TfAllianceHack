from aiogram import types
from aiogram.types.chat import ChatType

from admin.states import AdminState
from config.dependencies import dp
from db import company as company_db, user as user_db
from tg.senders import send_message

from . import commands, messages, senders


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.START_SUPERUSER_COMMAND.text], state='*')
async def start_superuser_session(message: types.Message):
    user = await user_db.get_or_create_user(message.from_user)
    if user.is_owner is False:
        if await company_db.get_company_owners_count() == 0:
            await company_db.add_company_owner(user)
            await AdminState.base.set()
            return
        else:
            await senders.send_superuser_request(user)
            response = messages.ALREADY_HAVE_SUPERUSER
    else:
        response = messages.ALREADY_SUPERUSER
    await send_message(message.chat.id, response)


@dp.callback_query_handler(chat_type=ChatType.PRIVATE, text=['confirm_admin'], state='*')
async def confirm_admin_inline_button(query: types.CallbackQuery):
    user = await user_db.get_user(query.message.chat.id)
    new_admin_id = query.message.entities[0].user.id
    new_admin = await user_db.get_user(new_admin_id)
    await company_db.add_company_admin(new_admin)
    await senders.confirm_admin(user, new_admin)


@dp.callback_query_handler(chat_type=ChatType.PRIVATE, text=['make_owner'], state='*')
async def confirm_owner_inline_button(query: types.CallbackQuery):
    user = await user_db.get_user(query.message.chat.id)
    new_owner_id = query.message.entities[0].user.id
    new_owner = await user_db.get_user(new_owner_id)
    await company_db.add_company_owner(new_owner)
    await senders.confirm_owner(user, new_owner)


@dp.callback_query_handler(chat_type=ChatType.PRIVATE, text=['deny_admin'], state='*')
async def deny_admin_inline_button(query: types.CallbackQuery):
    user = await user_db.get_user(query.message.chat.id)
    new_admin_id = query.message.entities[0].user.id
    new_admin = await user_db.get_user(new_admin_id)
    await senders.deny_admin(user, new_admin)


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.CHECK_SUPERUSERS_COMMAND.text], state='*')
async def company_owner_list_command(message: types.Message):
    owners = await company_db.get_company_owners()
    await send_message(message.chat.id,
        messages.OWNER_LIST + '\n'.join(map(
            lambda owner: f'{owner[0] + 1}) {owner[1].tg_name}',
            enumerate(owners)
        )),
        parse_mode='html'
    )


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.CHECK_ADMINS_COMMAND.text], state='*')
async def company_admin_list_command(message: types.Message):
    admins = await company_db.get_company_admins()
    await send_message(message.chat.id,
        messages.ADMIN_LIST + '\n'.join(map(
            lambda admin: f'{admin[0] + 1}) {admin[1].tg_name}',
            enumerate(admins)
        )),
        parse_mode='html'
    )


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.KICK_ADMIN_COMMAND.text], state='*')
async def kick_admin_command(message: types.Message):
    user = await user_db.get_or_create_user(message.from_user)
    admin, admin_name = await commands.KICK_ADMIN_COMMAND.parse(message.text)
    if admin is not None:
        if user == admin:
            await send_message(message.chat.id, messages.TRY_KICK_YOURSELF)
        else:
            response = messages.ADMIN_KICKED % (admin.tg_name, user.tg_name)
            await company_db.kick_company_admin(admin)
            await senders.send_message_to_owners(
                response, exclude={admin.id}, parse_mode='html'
            )
            await send_message(admin.id, messages.YOU_KICKED)
    else:
        await send_message(message.chat.id, messages.ADMIN_NOT_FOUND % admin_name)
