from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

from whathappened.core.auth.models import User


class LoginManager(AbstractAuthenticationMiddleware):
    async def authenticate_request(
        self, connection: ASGIConnection
    ) -> AuthenticationResult:
        user = None
        if connection.session.get("username", None):
            user = User.query.filter_by(
                username=connection.session.get("username", None)
            ).first()
            if not user:
                raise NotAuthorizedException()
        return AuthenticationResult(user, None)
