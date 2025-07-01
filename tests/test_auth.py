import unittest
from utils import auth
from storage import chat_db

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        chat_db.init_db()
        self.username = "test_user"
        self.password = "secure123"

    def test_register_user_duplicate(self):
        auth.register_user(self.username, self.password)
        result = auth.register_user(self.username, self.password)
        self.assertFalse(result)

    def test_authenticate_user_success(self):
        auth.register_user(self.username, self.password)
        result = auth.authenticate_user(self.username, self.password)
        self.assertTrue(result)

    def test_authenticate_user_failure(self):
        result = auth.authenticate_user("nonexistent", "whatever")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
