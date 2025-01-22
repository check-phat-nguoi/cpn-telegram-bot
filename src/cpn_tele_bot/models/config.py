from typing import Any, cast

from pydantic import BaseModel, Field, field_validator


class ConfigModel(BaseModel):
    # TODO: Check if it can be int?
    OWNER: str = Field(
        title="Owner ID",
        description="ID của owner có toàn quyền với bot",
    )
    BOT_TOKEN: str = Field(
        title="Bot token",
        description="Bot token lấy từ @BotFather",
    )
    AUTHORIZED_CHATS: tuple[str, ...] | None = Field(
        title="Các Chat ID có quyền sử dụng bot",
        description="Các chat ID có quyền sử dụng bot",
    )

    @field_validator("AUTHORIZED_CHATS", mode="before")
    @classmethod
    def _authorized_chats_before_validator(cls, value: Any) -> Any:
        if value is None or isinstance(value, tuple):
            return value
        if isinstance(value, str):
            return value.split(" ")
        return value

    @field_validator("AUTHORIZED_CHATS", mode="after")
    @classmethod
    def _authorized_chats_after_validator(
        cls, value: tuple[str, ...] | None
    ) -> tuple[str, ...] | None:
        if value is None:
            return
        # PERF: maybe ... it's not really fast
        if any(
            filter(
                lambda chat_id: not cast(str, chat_id).lstrip("-").isnumeric(), value
            )
        ):
            raise ValueError("Authorized chat ID must be integer form")
        return value
