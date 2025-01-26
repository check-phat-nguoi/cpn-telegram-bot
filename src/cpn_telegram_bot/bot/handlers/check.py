from typing import Generator

from telegram import Message, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from cpn_core.models.plate_info import PlateInfo
from cpn_core.models.violation_detail import ViolationDetail
from cpn_core.types.vehicle_type import get_vehicle_enum
from cpn_telegram_bot.bot.utils.authorized import (
    authorized_chat_decorator,
)
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.modules.get_data import GetData


@authorized_chat_decorator
async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message: Message | None = update.message
    args: list[str] | None = context.args
    if message is None or args is None:
        return ConversationHandler.END
    if not args:
        await message.reply_text(
            "Để kiểm tra phạt nguội cho biển, nhập theo cú pháp `/check 59XB-03135,1 20A1-53000,2`.\n\n"
            "Với:\n"
            "1: Ô tô\n"
            "2: Xe máy\n"
            "3: Xe máy điện",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END
    for arg in args:
        (plate, type) = arg.strip().split(",")
        if not type:
            ...
        plate_info: PlateInfo = PlateInfo(plate=plate, type=get_vehicle_enum(type))
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
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    return ConversationHandler.END
