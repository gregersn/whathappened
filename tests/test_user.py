import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.auth.models import User

from .support import Conf as Config

class UserModelCase(unittest.TestCase):
    def setUp(self):        
        self.app = create_app(Config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))
    

if __name__ == '__main__':
    unittest.main(verbosity=2)
