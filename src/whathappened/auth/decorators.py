from functools import wraps
import logging

logger = logging.getLogger(__name__)


def login_required(f, *args, **kwargs):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.error("This is where we check if a user is logged in")
        return f(*args, **kwargs)

    return decorated_function
