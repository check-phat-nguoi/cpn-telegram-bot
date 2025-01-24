from logging import getLogger
from typing import TypedDict, cast

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

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.authorized_chat import AuthorizedChat

logger = getLogger(__name__)

(CONFIRM_STAGE,) = range(1)
CONFIRM_DATA, CANCEL_DATA = range(2)


class _UserDataContext(TypedDict):
    auth_chat_ids: tuple[int, ...] | None


async def _auth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    args: list[str] | None = context.args
    message: Message | None = update.message
    user_data_context: dict | None = context.user_data
    if args is None or message is None or user_data_context is None:
        return ConversationHandler.END
    if config.DB_URI is None:
        await message.reply_text(
            "Chức năng thêm Chat ID xác thực để bot có thể chat không hỗ trợ khi không có kết nối cơ sở dữ liệu",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    casted_user_data_context: _UserDataContext = cast(
        _UserDataContext, user_data_context
    )
    if len(args) == 0:
        await message.reply_text(
            "Để thêm Chat ID xác thực cho bot, nhập theo cú pháp `/auth -1230982 123192834`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    chat_ids = ", ".join(f"`{chat_id}`" for chat_id in args)
    keyboard = [
        [
            InlineKeyboardButton("Xác nhận", callback_data=CONFIRM_DATA),
            InlineKeyboardButton("Hủy", callback_data=CANCEL_DATA),
        ]
    ]
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(keyboard)
    casted_user_data_context["auth_chat_ids"] = tuple(int(chat_id) for chat_id in args)
    await message.reply_text(
        f"Xác thực các Chat ID: {chat_ids}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return CONFIRM_STAGE


async def _confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query: CallbackQuery | None = update.callback_query
    user_data_context: dict | None = context.user_data
    if query is None or user_data_context is None:
        return ConversationHandler.END
    casted_user_data_context: _UserDataContext = cast(
        _UserDataContext, user_data_context
    )
    await query.answer()
    chat_ids: tuple[int, ...] | None = casted_user_data_context["auth_chat_ids"]
    if chat_ids is None:
        return ConversationHandler.END
    for chat_id in chat_ids:
        try:
            await AuthorizedChat(chat_id=chat_id).insert()
        except DuplicateKeyError as e:
            logger.warning("Chat ID %s is already authorized. %s", chat_id, e)
    await query.edit_message_text(text="Đã thêm các Chat ID!")
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query: CallbackQuery | None = update.callback_query
    user_data_context: dict | None = context.user_data
    if query is None or user_data_context is None:
        return ConversationHandler.END
    casted_user_data_context: _UserDataContext = cast(
        _UserDataContext, user_data_context
    )
    await query.answer()
    chat_ids: tuple[int, ...] | None = casted_user_data_context["auth_chat_ids"]
    casted_user_data_context["auth_chat_ids"] = None
    logger.debug(
        "Cancel authenticate Chat ID %s.",
        str(chat_ids),
    )
    await query.edit_message_text(text="Đã hủy thêm xác thực các Chat ID")
    return ConversationHandler.END


auth_chat_cov = ConversationHandler(
    entry_points=[CommandHandler("auth", _auth_handler)],
    states={
        CONFIRM_STAGE: [
            CallbackQueryHandler(_confirm, pattern=rf"^{CONFIRM_DATA}$"),
            CallbackQueryHandler(_cancel, pattern=rf"^{CANCEL_DATA}$"),
        ],
    },
    fallbacks=[CommandHandler("auth", _auth_handler)],
)
