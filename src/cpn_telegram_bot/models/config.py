from re import compile as re_compile
from typing import Any, Literal

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
    AUTHORIZED_CHATS: tuple[int, ...] | None = Field(
        title="Các Chat ID có quyền sử dụng bot",
        description="Các chat ID có quyền sử dụng bot",
    )
    DB_URI: str | None = Field(
        title="Database URI",
        description="Database URI",
        default=None,
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
        description="Thời gian (s) để gửi request đến server API và gửi notify message",
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

    @field_validator("BOT_TOKEN", mode="after")
    @classmethod
    def validate_bot_token(cls, value: str) -> str:
        if not BOT_TOKEN_PATTERN.match(value):
            raise ValueError(f"Bot token {value} is not valid")
        return value

    @field_validator("AUTHORIZED_CHATS", mode="before")
    @classmethod
    def _authorized_chats_before_validator(cls, value: Any) -> tuple[int, ...] | None:
        if value is None:
            return
        return _pipe_chat_id_strings(value)

    @field_validator("AUTHORIZED_CHATS", mode="after")
    @classmethod
    def _authorized_chats_after_validator(
        cls, value: tuple[str, ...] | None
    ) -> tuple[str, ...] | None:
        if value is None:
            return
        if any(filter(_check_not_valid_id, value)):
            raise ValueError("Authorized chat ID must be integer form")
        return value
