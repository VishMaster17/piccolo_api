import typing as t
import uuid

from asgiref.sync import async_to_sync

from piccolo.columns.column_types import Varchar, ForeignKey
from piccolo.extensions.user.tables import BaseUser
from piccolo.table import Table


def generate_token() -> str:
    return str(uuid.uuid4())


class TokenAuth(Table):
    """
    Holds randomly generated tokens.

    Useful for mobile authentication, IOT etc. Session auth is recommended for
    web usage.
    """

    token = Varchar(default=generate_token)
    user = ForeignKey(references=BaseUser)

    @classmethod
    async def create_token(
        cls, user_id: int, one_per_user: bool = True
    ) -> str:
        """
        Create a new token.

        :param one_per_user: If True, a ValueError is raised if a token
                             already exists for that user.

        """
        if await cls.exists().where(cls.user.id == user_id).run():
            raise ValueError(f"User {user_id} already has a token.")

        token_auth = cls(user=user_id)
        await token_auth.save().run()

        return token_auth.token

    @classmethod
    def create_token_sync(cls, user_id: int) -> str:
        return async_to_sync(cls.create_token)(user_id)

    @classmethod
    async def authenticate(cls, token: str) -> t.Optional[int]:
        return cls.select(cls.user.id).where(cls.token == token).first()

    @classmethod
    async def authenticate_sync(cls, token: str) -> t.Optional[int]:
        return async_to_sync(cls.authenticate)(token)
