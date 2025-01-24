from re import compile as re_compile
from typing import Any, Literal

from cpn_core.types.api import ApiEnum
from pydantic import BaseModel, Field, field_validator

BOT_TOKEN_PATTERN = re_compile(r"^[0-9]+:.+$")


def _check_not_valid_id(id: str | int) -> bool:
    if isinstance(id, int):
        return False
    return not id.lstrip("-").isnumeric()


def _pipe_chat_id_strings(ids: Any) -> tuple[int, ...]:
    if isinstance(ids, tuple):
        return ids
    if isinstance(ids, str):
        ids_str: list[str] = ids.split(" ")
        return tuple(int(id) for id in ids_str)
    raise ValueError("IDs must be list of strings or id strings separated with space")


class ConfigModel(BaseModel):
    # TODO: Check if it can be int?
    OWNERS: tuple[int, ...] = Field(
        title="Owner IDs",
        description="ID của các owner có toàn quyền với bot",
        min_length=1,
    )
    BOT_TOKEN: str = Field(
        title="Bot token",
        description="Bot token lấy từ @BotFather",
    )
    AUTHORIZED_CHATS: tuple[int, ...] = Field(
        title="Các Chat ID có quyền sử dụng bot",
        description="Các chat ID có quyền sử dụng bot",
    )
    PLATES: tuple[int, ...] | None = Field(
        title="Danh sách biển mặc định",
        description="Các biển mặc định",
        default=None,
    )
    APIS: tuple[ApiEnum, ...] = Field(
        title="Danh sách API",
        description="Các API sẽ được get fallback theo thứ tự. Mặc định sẽ là tất cả đều được fallback",
        default=(
            ApiEnum.phatnguoi_vn,
            ApiEnum.checkphatnguoi_vn,
            ApiEnum.zm_io_vn,
            ApiEnum.csgt_vn,
        ),
    )
    DB_URI: str | None = Field(
        title="Database URI",
        description="Database URI (Mongodb) để lưu trữ dữ liệu của bot sau khi custom. Trường hợp bot khởi động lại, server restart sẽ giữ được dữ liệu đã custom.",
        default=None,
    )
    LOCAL_BOT_API_URL: str | None = Field(
        title="Tự host bot",
        description="URL dẫn tới selfhost bot telegram (không phải con bot này mà là bot server...)",  # FIXME: the desc so bruh
    )
    PENDING_FINES_ONLY: bool = Field(
        title="Lọc chưa nộp phạt",
        description="Chỉ lọc các thông tin vi phạm chưa nộp phạt",
        default=True,
    )
    SHOW_LESS_DETAILS: bool = Field(
        title="Hiển thị ít thông tin",
        description="Chỉ hiển thị những thông tin biển vi phạm cần thiết",
        default=False,
    )
    REQUEST_TIMEOUT: int = Field(
        title="Thời gian request",
        description="Thời gian (s) để gửi request đến server API",
        default=20,
    )
    TIME_FORMAT: Literal["12", "24"] = Field(
        description="Định dạng thời gian 12h hoặc 24h",
        default="24",
    )

    @field_validator("OWNERS", mode="before")
    @classmethod
    def _authorized_owners_before_validator(cls, value: Any) -> tuple[int, ...]:
        if value is None:
            raise ValueError("Onwer IDs must be given")
        return _pipe_chat_id_strings(value)

    @field_validator("OWNERS", mode="after")
    @classmethod
    def _authorized_owners_after_validator(
        cls, value: tuple[str, ...]
    ) -> tuple[str, ...]:
        if any(filter(_check_not_valid_id, value)):
            raise ValueError("Onwer ID must be integer form")
        return value

    @field_validator("APIS", mode="before")
    @classmethod
    def _apis_before_validator(cls, value: Any) -> tuple[ApiEnum, ...]:
        if isinstance(value, tuple):
            return tuple(ApiEnum(api) for api in value)
        elif isinstance(value, str):
            apis: list[str] = value.split(" ")
            return tuple(ApiEnum(api) for api in apis)
        raise ValueError(
            "APIS must be list of ApiEnum string or string of ApiEnums separated with space"
        )

    @field_validator("BOT_TOKEN", mode="after")
    @classmethod
    def validate_bot_token(cls, value: str) -> str:
        if not BOT_TOKEN_PATTERN.match(value):
            raise ValueError(f"Bot token {value} is not valid")
        return value

    @field_validator("AUTHORIZED_CHATS", mode="before")
    @classmethod
    def _authorized_chats_before_validator(cls, value: Any) -> tuple[int, ...]:
        return _pipe_chat_id_strings(value)

    @field_validator("AUTHORIZED_CHATS", mode="after")
    @classmethod
    def _authorized_chats_after_validator(
        cls, value: tuple[str, ...]
    ) -> tuple[str, ...]:
        if any(filter(_check_not_valid_id, value)):
            raise ValueError("Authorized chat ID must be integer form")
        return value
