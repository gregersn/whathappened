from whathappened.core.auth.models import User


class CurrentUser:
    user: User | None = None

    @property
    def is_anonymous(self):
        return self.user is None

    @property
    def is_authenticated(self):
        return self.user is not None

    def set_user(self, user: User):
        self.user = user

    def clear(self):
        self.user = None

    @property
    def username(self):
        if self.user:
            return self.user.username
        return "Unnamed"

    @property
    def id(self):
        if self.user:
            return self.user.id
        return None


current_user = CurrentUser()
