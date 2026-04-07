import logging

from whathappened.core.auth.models import Role, User, UserRoles
from whathappened.core.character.models import Character
from whathappened.core.database.models import UserProfile
from whathappened.web import create_app

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s %(message)s", level=logging.DEBUG
)
logging.debug("Logger initialized")

logging.getLogger("semver").setLevel(logging.INFO)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        "User": User,
        "UserProfile": UserProfile,
        "Character": Character,
        "Role": Role,
        "UserRoles": UserRoles,
    }
