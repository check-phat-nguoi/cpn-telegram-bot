from logging import getLogger

from beanie.operators import In
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

(SELECT_STAGE, CONFIRM_STAGE) = range(2)


@sudo_decorator
@authorized_chat_decorator
async def _deauth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    args: list[str] | None = context.args
    message: Message | None = update.message
    user_data: dict | None = context.user_data
    if args is None or message is None or user_data is None:
        return
    if config.DB_URI is None:
        await message.reply_text(
            "Chức năng hủy xác thực Chat ID mà bot có thể chat không hỗ trợ khi không có kết nối cơ sở dữ liệu",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    if len(args) == 0:
        await message.reply_text(
            "Để hủy xác thực Chat ID cho bot, nhập theo cú pháp `/deauth -1230982 123192834`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    chat_ids: tuple[int, ...] = tuple(
        int(chat_id) for chat_id in args if chat_id not in config.AUTHORIZED_CHATS
    )
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
    user_data["deauth_chat_ids"] = chat_ids
    markup_chat_ids: str = ", ".join(f"`{chat_id}`" for chat_id in chat_ids)
    await message.reply_text(
        f"Xác nhận hủy xác thực các Chat ID: {markup_chat_ids}",
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
    chat_ids: tuple[int, ...] = user_data["deauth_chat_ids"]
    user_data.clear()
    try:
        AuthorizedChat.find(In(AuthorizedChat.chat_id, chat_ids)).delete_many()
    except Exception as e:
        logger.error("Error occurred while deauthorize chat IDs. %s", e)
    await query.edit_message_text(
        text="Đã hủy xác thực các Chat ID!", reply_markup=None
    )
    return ConversationHandler.END


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    query: CallbackQuery | None = update.callback_query
    user_data: dict | None = context.user_data
    if query is None or user_data is None:
        return
    await query.answer()
    user_data.clear()
    await query.edit_message_text(
        text="Đã hủy hủy xác thực các Chat ID", reply_markup=None
    )
    return ConversationHandler.END


deauth_chat_cov = ConversationHandler(
    entry_points=[CommandHandler("deauth", _deauth)],
    states={
        CONFIRM_STAGE: [
            CallbackQueryHandler(_confirm, pattern=rf"^{ConfirmEnum.CONFIRM.name}$"),
            CallbackQueryHandler(_cancel, pattern=rf"^{ConfirmEnum.CANCEL.name}$"),
        ],
    },
    fallbacks=[CommandHandler("deauth", _deauth)],
)
