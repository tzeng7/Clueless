import unittest

from messages.messages import BaseMessage, JoinGame


class MyTestCase(unittest.TestCase):
    def test_base_message(self):
        original = BaseMessage()
        serialized = original.serialize()
        deserialized: BaseMessage = BaseMessage.deserialize(serialized)
        self.assertEqual(deserialized.uuid, original.uuid)

    def test_join_game(self):
        original = JoinGame(nickname="Bob")
        serialized = original.serialize()
        deserialized: JoinGame = JoinGame.deserialize(serialized)
        self.assertEqual(deserialized.uuid, original.uuid)
        self.assertEqual(deserialized.nickname, original.nickname)
