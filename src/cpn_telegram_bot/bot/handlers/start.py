from telegram import Chat, Message, Update
from telegram.ext import ContextTypes

from cpn_telegram_bot.bot.utils.authorized import is_authorized_chat


async def start_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message | None = update.message
    chat: Chat | None = update.effective_chat
    if message is None or chat is None:
        return
    text: str = (
        "Xin chào"
        if await is_authorized_chat(chat.id)
        else "Bạn không có quyền nhắn với bot"
    )
    await message.reply_text(text)
