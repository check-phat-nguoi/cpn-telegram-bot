from typing import LiteralString

from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from cpn_telegram_bot.bot.utils.authorized import (
    authorized_chat_decorator,
)

TEXT: LiteralString = """[Source repo](https://github.com/check-phat-nguoi/cpn-telegram-bot)
Cho chúng tớ xin 1 ⭐"""


@authorized_chat_decorator
async def info_handler(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message | None = update.message
    if message is None:
        return
    await message.reply_text(TEXT, parse_mode=ParseMode.MARKDOWN_V2)
