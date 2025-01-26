from logging import getLogger

from pymongo.errors import BulkWriteError
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
from cpn_telegram_bot.bot.utils.authorized import authorized_chat_decorator
from cpn_telegram_bot.bot.utils.sudo import sudo_decorator
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.authorized_chat import AuthorizedChat

logger = getLogger(__name__)

(CONFIRM_STAGE,) = range(1)


@sudo_decorator
@authorized_chat_decorator
async def _auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
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
            "Để thêm Chat ID xác thực cho bot, nhập theo cú pháp `/auth -1230982 123192834`.\n"
            "Lưu ý không có quyền sửa đổi chat ID đã khai báo trong config.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    chat_ids: tuple[int, ...] = tuple(
        chat_id
        for chat_id in (int(chat_id) for chat_id in args)
        if chat_id not in config.AUTHORIZED_CHATS
    )

    if not chat_ids:
        await message.reply_text(
            "Không còn chat ID nào sau khi đã lọc.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END
    else:
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
        user_data["auth_chat_ids"] = chat_ids
        markup_chat_ids: str = ", ".join(f"`{chat_id}`" for chat_id in chat_ids)
        await message.reply_text(
            f"Xác thực các Chat ID: {markup_chat_ids}",
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
    try:
        await AuthorizedChat.insert_many(
            [AuthorizedChat(chat_id=chat_id) for chat_id in chat_ids]
        )
    except BulkWriteError as e:
        logger.warning(
            "There might be already authorized chat(s) or unknown error. %s", e
        )
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
    entry_points=[CommandHandler("auth", _auth)],
    states={
        CONFIRM_STAGE: [
            CallbackQueryHandler(_confirm, pattern=rf"^{ConfirmEnum.CONFIRM.name}$"),
            CallbackQueryHandler(_cancel, pattern=rf"^{ConfirmEnum.CANCEL.name}$"),
        ],
    },
    fallbacks=[CommandHandler("auth", _auth)],
    per_message=False,
)
