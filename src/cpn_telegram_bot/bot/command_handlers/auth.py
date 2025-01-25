from logging import getLogger

from pymongo.errors import DuplicateKeyError
from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from cpn_telegram_bot.bot.types.confirm import ConfirmEnum
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.authorized_chat import AuthorizedChat

logger = getLogger(__name__)

(CONFIRM_STAGE,) = range(1)


async def _auth_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    args: list[str] | None = context.args
    message: Message | None = update.message
    user_data: dict | None = context.user_data
    if args is None or message is None or user_data is None:
        return
    if config.DB_URI is None:
        await message.reply_text(
            "Chức năng thêm Chat ID xác thực để bot có thể chat không hỗ trợ khi không có kết nối cơ sở dữ liệu",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    if len(args) == 0:
        await message.reply_text(
            "Để thêm Chat ID xác thực cho bot, nhập theo cú pháp `/auth -1230982 123192834`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    chat_ids = ", ".join(f"`{chat_id}`" for chat_id in args)
    keyboard = [
        [
            InlineKeyboardButton(
                ConfirmEnum.CONFIRM.value, callback_data=ConfirmEnum.CONFIRM.name
            ),
            InlineKeyboardButton(
                ConfirmEnum.CANCEL.value, callback_data=ConfirmEnum.CANCEL.name
            ),
        ]
    ]
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(keyboard)
    user_data["auth_chat_ids"] = tuple(int(chat_id) for chat_id in args)
    await message.reply_text(
        f"Xác thực các Chat ID: {chat_ids}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return CONFIRM_STAGE


async def _confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query: CallbackQuery | None = update.callback_query
    user_data: dict | None = context.user_data
    if query is None or user_data is None:
        return
    await query.answer()
    chat_ids: tuple[int, ...] = user_data["auth_chat_ids"]
    user_data.clear()
    for chat_id in chat_ids:
        try:
            await AuthorizedChat(chat_id=chat_id).insert()
            logger.info("Chat ID %s has been authorized.", chat_id)
        except DuplicateKeyError as e:
            logger.warning("Chat ID %s is already authorized. %s", chat_id, e)
    await query.edit_message_text(text="Đã thêm các Chat ID!")
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query: CallbackQuery | None = update.callback_query
    user_data: dict | None = context.user_data
    if query is None or user_data is None:
        return
    await query.answer()
    chat_ids: tuple[int, ...] = user_data["auth_chat_ids"]
    logger.debug(
        "Cancel authenticate Chat ID %s.",
        str(chat_ids),
    )
    user_data.clear()
    await query.edit_message_text(text="Đã hủy thêm xác thực các Chat ID")
    return ConversationHandler.END


auth_chat_cov = ConversationHandler(
    entry_points=[CommandHandler("auth", _auth_stage)],
    states={
        CONFIRM_STAGE: [
            CallbackQueryHandler(_confirm, pattern=rf"^{ConfirmEnum.CONFIRM.name}$"),
            CallbackQueryHandler(_cancel, pattern=rf"^{ConfirmEnum.CANCEL.name}$"),
        ],
    },
    fallbacks=[CommandHandler("auth", _auth_stage)],
)
