from typing import Annotated

from beanie import Document, Indexed


class AuthorizedChat(Document):
    chat_id: Annotated[int, Indexed(unique=True)]
