import unittest
from network.peer import Peer

class DummyChatWindow:
    def __init__(self):
        self.messages = []

    def display_message(self, msg):
        self.messages.append(msg)

    def ask_connection_approval(self, requester):
        return True

class PeerTestCase(unittest.TestCase):
    def test_bind_chat_window(self):
        peer = Peer("127.0.0.1", 5000)
        window = DummyChatWindow()
        peer.bind_chat_window(window)
        self.assertEqual(peer.chat_window, window)

    def test_broadcast_adds_message_id(self):
        peer = Peer("127.0.0.1", 5001)
        window = DummyChatWindow()
        window.username = "test"
        peer.bind_chat_window(window)

        peer.broadcast("Test message")
        self.assertTrue(len(peer.received_messages) > 0)

if __name__ == '__main__':
    unittest.main()
