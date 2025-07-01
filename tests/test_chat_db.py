import unittest
from storage import chat_db

class ChatDbTestCase(unittest.TestCase):
    def setUp(self):
        chat_db.init_db()

    def test_save_and_get_history(self):
        chat_db.save_message("user1", "hello world")
        history = chat_db.get_history()
        self.assertTrue(any("hello world" in m for _, m, _ in history))

    def test_add_and_validate_user(self):
        username = "u1"
        pwd_hash = "hash123"
        added = chat_db.add_user(username, pwd_hash)
        self.assertTrue(added)

        retrieved = chat_db.validate_user(username)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved[0], pwd_hash)

    def test_active_user_management(self):
        chat_db.set_user_active("test_user", 9000)
        users = chat_db.get_active_users()
        self.assertIn(("test_user", 9000), users)

        chat_db.set_user_inactive("test_user")
        users = chat_db.get_active_users()
        self.assertNotIn(("test_user", 9000), users)

if __name__ == '__main__':
    unittest.main()
