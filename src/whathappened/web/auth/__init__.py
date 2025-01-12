"""Authentication module."""

import logging

from whathappened import login_manager
from whathappened.core.database import session
from ...core.auth.models import User  # noqa E402
from .forms import LoginForm, RegistrationForm  # noqa E402

logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id: str):
    logger.info("Loading user %s", user_id)
    return session.get(User, user_id)


from . import routes  # noqa: E402, F401 isort:skip
