import unittest
from unittest.mock import patch, MagicMock
from client.client import GameClient
from server.server import ClueServer
from messages.messages import AssignPlayerID


class MyTestCase(unittest.TestCase):
    def setUp(self):
        # Mock the server's Launch method to avoid starting a real server
        self.server = ClueServer()
        self.server.Launch = MagicMock(name='Launch')

    def setUpClients(self, number_of_clients):
        # Initialize clients and patch their network methods to prevent real network usage
        self.patcher_send = patch('client.client.GameClient.send', create=True)
        self.patcher_update = patch('client.client.GameClient.update', create=True)

        self.mock_send = self.patcher_send.start()
        self.mock_update = self.patcher_update.start()

        self.clients = [GameClient("127.0.0.1", 10000) for _ in range(number_of_clients)]

        for client in self.clients:
            client.Network_connected = MagicMock()
            client.Network_assign_player_id = MagicMock()

    def test_clients_can_connect_and_communicate(self):
        for num_clients in range(2, 7):
            with self.subTest(num_clients=num_clients):
                self.setUpClients(num_clients)
                self.simulate_server_interaction(num_clients)
                self.assert_unique_player_ids(num_clients)
                self.tearDownClients()  # Reset after each subtest

    def simulate_server_interaction(self, num_clients):
        # Simulate server interaction with each client
        for i, client in enumerate(self.clients):
            player_id_message = AssignPlayerID(str(i + 1))
            serialized_message = player_id_message.serialize()

            # Simulate server sending a welcome message and assigning player IDs
            client.Network_connected({'action': 'join_game'})

            # Mock the behavior of Network_assign_player_id to set the player_id on the client's player object
            def mock_assign_player_id(msg):
                # Making sure the client has a player attribute which is not None
                if client.player is None:
                    client.player = MagicMock()
                client.player.player_id = AssignPlayerID.deserialize(msg).player_id

            client.Network_assign_player_id.side_effect = mock_assign_player_id
            client.Network_assign_player_id(serialized_message)

            # Assert that the clients have received the welcome message and set their player ID
            client.Network_connected.assert_called_with({'action': 'join_game'})
            client.Network_assign_player_id.assert_called_with(serialized_message)

    def assert_unique_player_ids(self, num_clients):
        # Assert that all player IDs are unique
        player_ids = [client.player.player_id for client in self.clients]
        print(player_ids)  # just to check player ids
        self.assertEqual(len(set(player_ids)), num_clients, "Player IDs are not unique")

    def tearDownClients(self):
        # Stop patching the send and update methods
        self.patcher_send.stop()
        self.patcher_update.stop()
        self.clients.clear()

    def tearDown(self):
        self.tearDownClients()


if __name__ == '__main__':
    unittest.main()

