from functools import wraps

from telegram import Chat, Update
from telegram.ext import ContextTypes

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.authorized_chat import AuthorizedChat


async def is_authorized_chat(chat_id: int) -> bool:
    return chat_id in config.AUTHORIZED_CHATS or (
        config.DB_URI is not None
        and chat_id in await AuthorizedChat.find_all().to_list()
    )


def authorized_chat_decorator(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        chat: Chat | None = update.effective_chat
        if chat is None:
            return
        chat_id: int = chat.id
        if not await is_authorized_chat(chat_id):
            print("Bạn không thể nhắn với bot.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
