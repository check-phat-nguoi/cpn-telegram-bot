from functools import wraps

from telegram import Message, Update, User
from telegram.ext import ContextTypes

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.sudo_user import SudoUser


async def is_sudo(user_id: int) -> bool:
    return user_id in config.OWNERS or (
        config.DB_URI is not None
        and await SudoUser.find_one(SudoUser.user_id == user_id).exists()
    )


def sudo_decorator(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user: User | None = update.effective_user
        message: Message | None = update.effective_message
        if user is None or message is None:
            return
        user_id: int = user.id
        if not await is_sudo(user_id):
            await message.reply_text("Bạn không có quyền sử dụng lệnh này.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
