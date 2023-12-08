import unittest
from unittest.mock import patch, MagicMock
from clueless.client.client import GameClient
from clueless.model.board_enums import Character
from clueless.model.player import PlayerID
from clueless.server.game_manager import GameManager
from clueless.server.server import ClueServer
from clueless.messages.messages import AssignPlayerID, StartGame, DealCards
from clueless.model.board import Board
from clueless.server.server_player import ServerPlayer


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.server = ClueServer()
        self.server.Launch = MagicMock(name='Launch')
        self.characters = list(Character)

    def setUpClients(self, number_of_clients):
        self.patcher_send = patch('clueless.client.client.GameClient.send', create=True)
        self.patcher_update = patch('clueless.client.client.GameClient.update', create=True)

        self.mock_send = self.patcher_send.start()
        self.mock_update = self.patcher_update.start()
        self.clients = []

        for _ in range(number_of_clients):
            client = GameClient()
            client.Network_connected = MagicMock()
            client.Network_assign_player_id = MagicMock()
            # If GameClient does not have a player attribute, either add it or handle its absence
            client.player = MagicMock()  # Add a mock player if necessary
            self.clients.append(client)

    def test_clients_can_connect_and_communicate(self):
        for num_clients in range(2, 7):
            with self.subTest(num_clients=num_clients):
                self.setUpClients(num_clients)
                self.simulate_server_interaction(num_clients)
                self.assert_unique_player_ids(num_clients)
                self.simulate_start_game(num_clients)
                self.test_turn_order()
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

    def simulate_start_game(self, num_clients):
        # Create a mock channel
        mock_channel = MagicMock(name='MockChannel')

        # Create dummy players for GameManager with a mock channel
        dummy_players = [ServerPlayer(PlayerID(nickname="Player" + str(i + 1), character=self.characters[i % len(
            self.characters)]), channel=mock_channel) for i in range(num_clients)]

        # Instantiate GameManager with dummy players
        game_manager = GameManager(dummy_players)

        # Start the game which will distribute cards
        game_manager.start_game()

        all_cards = []

        for client, server_player in zip(self.clients, dummy_players):
            # Simulate server sending cards to client
            client.Network_deal_cards = MagicMock()
            serialized_cards = DealCards(server_player.cards).serialize()
            client.Network_deal_cards(serialized_cards)

            # Assert the client has received the cards
            client.Network_deal_cards.assert_called_with(serialized_cards)

            # Verify that the client's player cards match what GameManager dealt
            client.player.cards = server_player.cards
            self.assertEqual(client.player.cards, server_player.cards)

            # Add the player's cards to the all_cards list
            all_cards.extend(server_player.cards)

            # Check if all cards are unique
        self.assertEqual(len(all_cards), len(set(all_cards)), "Players do not have unique cards")

    def test_turn_order(self):
        for num_players in range(2, len(self.characters) + 1):
            with self.subTest(num_players=num_players):
                self.check_turn_order(num_players)

    def check_turn_order(self, num_players):
        # Ensure the number of players does not exceed the number of characters
        num_players = min(num_players, len(self.characters))
        mock_channel = MagicMock(name='MockChannel')
        players = [ServerPlayer(PlayerID(nickname="Player" + str(i + 1), character=self.characters[i]), channel=mock_channel) for i in range(num_players)]

        game_manager = GameManager(players)
        game_manager.start_game()

        for i in range(num_players * 2):  # Loop through a couple of full cycles
            expected_player = players[i % num_players]
            actual_player = game_manager.current_player

            # Check if the current player is as expected
            self.assertEqual(actual_player, expected_player, f"Turn order incorrect at turn {i}. Expected {expected_player.player_id.nickname}, got {actual_player.player_id.nickname}")

            # Simulate end of turn to move to the next player
            game_manager.next_turn()

    def tearDown(self):
        self.tearDownClients()

    def tearDownClients(self):
        # Check if the patchers have been initialized before stopping them
        if hasattr(self, 'patcher_send'):
            self.patcher_send.stop()
        if hasattr(self, 'patcher_update'):
            self.patcher_update.stop()
        if hasattr(self, 'clients'):
            self.clients.clear()


if __name__ == '__main__':
    unittest.main()