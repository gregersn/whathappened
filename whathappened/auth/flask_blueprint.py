import logging





from whathappened import login_manager
from whathappened.email import send_mail

bp = Blueprint('auth', __name__, url_prefix='/auth')

from .models import User  # noqa E402
from .forms import LoginForm, RegistrationForm  # noqa E402

logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(id: str):
    logger.info(f"Loading user {id}")
    return User.query.get(int(id))


def send_password_reset_email(user: User):
    token = user.get_reset_password_token()
    send_mail('[What Happened?] Reset your password',
              sender=current_app.config['ADMINS'][0],
              recipients=[user.email],
              text_body=render_template('/auth/reset_password.txt',
                                        user=user,
                                        token=token))


from . import routes  # noqa: E402, F401 isort:skip
