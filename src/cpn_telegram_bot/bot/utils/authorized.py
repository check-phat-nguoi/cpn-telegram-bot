from functools import wraps

from telegram import Chat, Message, Update
from telegram.ext import ContextTypes

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.authorized_chat import AuthorizedChat


async def is_authorized_chat(chat_id: int) -> bool:
    print(await AuthorizedChat.find_all().to_list())
    return chat_id in config.AUTHORIZED_CHATS or (
        config.DB_URI is not None
        and AuthorizedChat.find_one(AuthorizedChat.chat_id == chat_id) is not None
    )


def authorized_chat_decorator(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        chat: Chat | None = update.effective_chat
        message: Message | None = update.effective_message
        if chat is None or message is None:
            return
        if not await is_authorized_chat(chat.id):
            await message.reply_text("Bạn không thể nhắn với bot.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
