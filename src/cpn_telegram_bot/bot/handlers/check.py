from logging import getLogger
from typing import Generator

from cpn_core.models.plate_info import PlateInfo
from cpn_core.models.violation_detail import ViolationDetail
from cpn_core.types.vehicle_type import VehicleTypeEnum, get_vehicle_enum
from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from cpn_telegram_bot.bot.utils.authorized import (
    authorized_chat_decorator,
)
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.modules.get_data import GetData

logger = getLogger(__name__)


@authorized_chat_decorator
async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message: Message | None = update.message
    args: list[str] | None = context.args
    if message is None or args is None:
        return ConversationHandler.END
    if not args:
        await message.reply_text(
            "**Chức năng:** Kiểm tra phạt nguội cho biển\n"
            "**Cú pháp:**\n"
            "- `/check 30F88251`\n"
            "- `/check 30F88251,1`\n"
            "- `/check 59XB-03135,1 20A1-53000,2`\n\n"
            "**Loại xe:**\n"
            "- `1`: Ô tô\n"
            "- `2`: Xe máy\n"
            "- `3`: Xe máy điện",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END
    for arg in args:
        parts = arg.strip().split(",")
        if len(parts) == 1:
            if not parts[0]:
                await message.reply_text("Sai cú pháp!")
                return ConversationHandler.END
            else:
                ...  # TODO: Handle if not pass type here?
        else:
            plate: str = parts[0]
            try:
                type: VehicleTypeEnum = get_vehicle_enum(parts[1])
            except ValueError:
                await message.reply_text("Sai cú pháp loại phương tiện!")
                return ConversationHandler.END
            plate_info: PlateInfo = PlateInfo(plate=plate, type=type)
            violation_details: (
                tuple[ViolationDetail, ...] | None
            ) = await GetData.get_data_single_plate(plate_info)
            if violation_details is None:
                await message.reply_text(
                    f"Có lỗi xảy ra khi lấy dữ liệu cho biển `{plate}`",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                return ConversationHandler.END
            messages: Generator[str] = (
                violation_detail.get_str(
                    show_less_detail=config.SHOW_LESS_DETAILS,
                    markdown=True,
                    time_format=config.TIME_FORMAT,
                )
                for violation_detail in violation_details
            )
            for message_ in messages:
                await message.reply_text(
                    message_,
                    parse_mode=ParseMode.MARKDOWN,  # HACK: Use legacy markdown version because in MARKDOWN_V2 it's suck and idk why
                )
    return ConversationHandler.END
