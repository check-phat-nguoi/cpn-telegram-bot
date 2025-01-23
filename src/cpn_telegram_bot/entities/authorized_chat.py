from beanie import Document


class AuthorizedChat(Document):
    chat_ids: tuple[int, ...]
