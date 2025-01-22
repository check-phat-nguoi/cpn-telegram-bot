from telegram import Message, Update
from telegram.ext import ContextTypes


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message | None = update.message
    if message is None:
        return
    await message.reply_text("Xin chào")
