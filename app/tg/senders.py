from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.deep_linking import get_start_link
from aiogram.dispatcher.webhook import SendMessage, ForwardMessage, EditMessageText, EditMessageReplyMarkup

from propan.logger import loguru as logger

from config.dependencies import bot


async def get_theme_url(name: str):
    return await get_start_link(name)


async def send_message(chat_id: int, text: str, **kwargs) -> Message:
    try:
        return await bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        logger.warning(e)


async def copy_message(chat_id: int, from_chat_id: int, message_id: int, **kwargs) -> Message:
    try:
        return await bot.copy_message(chat_id, from_chat_id, message_id, **kwargs)
    except Exception as e:
        logger.warning(e)


async def reply_message(chat_id: int, message_id: int, text: str, **kwargs) -> Message:
    try:
        return await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=message_id,
            **kwargs
        )
    except Exception as e:
        logger.warning(e)


async def forward_message(chat_id: int, from_chat_id: int, message_id: int, **kwargs) -> Message:
    try:
        return await bot.forward_message(chat_id, from_chat_id, message_id, **kwargs)
    except Exception as e:
        logger.warning(e)


async def copy_message(chat_id: int, from_chat_id: int, message_id: int, **kwargs) -> Message:
    try:
        return await bot.copy_message(chat_id, from_chat_id, message_id, **kwargs)
    except Exception as e:
        logger.warning(e)


async def answer_message(chat_id: int, message_id: int, text: str, **kwargs) -> Message:
    return await send_message(
        chat_id,
        text,
        reply_to_message_id=message_id,
        **kwargs
    )


async def edit_message(chat_id: int, message_id: int, text: str, **kwargs) -> Message:
    try:
        return await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode='html',
            **kwargs
        )
    except Exception as e:
        logger.warning(e)


async def edit_keyboard(chat_id: int, message_id: int, reply_markup) -> Message:
    try:
        return await bot.edit_message_reply_markup(
            chat_id, message_id, reply_markup=reply_markup
        )
    except Exception as e:
        logger.warning(e)


async def remove_keyboard(chat_id: int, message_id: int) -> Message:
    try:
        return await bot.edit_message_reply_markup(
            chat_id, message_id, reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.warning(e)
