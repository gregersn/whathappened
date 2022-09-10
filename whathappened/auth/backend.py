"""Backend for authentication."""
import base64
import binascii
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, SimpleUser


class Backend(AuthenticationBackend):
    """Authentication backend."""

    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid basic auth credentials') from exc

        username, _, password = decoded.partition(":")
        # TODO: You'd want to verify the username and password here.
        print("Here is probably the place to authenticate")
        return AuthCredentials(["authenticated"]), SimpleUser(username)
