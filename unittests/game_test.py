import unittest


class MyTestCase(unittest.TestCase):
    pass
    # def test_players(self):
    #     game = GameManager()
    #     game.add_player()
    #     game.add_player()
    #     game.add_player()
    #
    #     players = ['Scarlet, Plum, Mustard']
    #     print(game.players[0].character)
    #
    #     gameplayers = [game.players[0].character, game.players[1].character, game.players[2].character]
    #     self.assertEqual(gameplayers, players)

    # def test_winning_combination(self):
    #     game = GameManager(None, players=[ServerPlayer(PlayerID(nickname="Bob", character=Character.SCARLET))])
    #     players = []
    #     for i in range(4):
    #         players.append(ServerPlayer(PlayerID(nickname=f"Bob_{i}", character=list(Character)[i])))
    #     game.distribute_cards()
    #     print(game.winning_combination)
    #
    # def test_player_cards(self):
    #     game = GameManager()
    #     for i in range(4):
    #         game.add_player()
    #     game.distribute_cards()
    #     for player in game.players:
    #         print(player.character)
    #         print(player.cards)
    #
    # def test_suggest(self):
    #     game = GameModel()
    #     for i in range(4):
    #         game.add_player()
    #     game.start_game()
    #
    #     game.board.initialize_player(game.players[0], (0, 0))
    #     game.board.initialize_player(game.players[1], (4, 4))
    #
    #     game.suggest(game.players[0], game.players[1], Weapon.ROPE)
    #
    #     self.assertEqual(game.players[0].position, game.players[1].position)
    #
    # def test_suggestion_response(self):
    #     game = GameModel()
    #     for i in range(1):
    #         game.add_player()
    #     game.players[0].cards.append(Card(CardType.CHARACTER, Character.PLUM.value))
    #     game.players[0].cards.append(Card(CardType.WEAPON, Weapon.ROPE.value))
    #     game.players[0].cards.append(Card(CardType.LOCATION, Location.BALLROOM.value))
    #
    #     suggestion = (Character.PLUM, Weapon.ROPE, Location.STUDY)
    #
    #     self.assertEqual(game.suggestion_responses(game.players[0], suggestion)[0].card_value, "Plum")
    #     self.assertEqual(game.suggestion_responses(game.players[0], suggestion)[1].card_value, "Rope")
    #
    # def test_board_movement(self):
    #     board = Board()
    #     game = GameModel()
    #     game.add_player()
    #     board.initialize_player(game.players[0], (0,0))
    #     board.move_in_direction(game.players[0], Direction.SECRET_PASSAGEWAY)
    #
    #     self.assertEqual(game.players[0].position, (4,4))
    #
    #     board.move_in_direction(game.players[0], Direction.LEFT)
    #
    #     self.assertEqual(game.players[0].position, (4, 3))
    #
    #     board.move_in_direction(game.players[0], Direction.LEFT)
    #     board.move_in_direction(game.players[0], Direction.LEFT)
    #     board.move_in_direction(game.players[0], Direction.LEFT)
    #
    #     board.move_in_direction(game.players[0], Direction.SECRET_PASSAGEWAY)
    #
    #     self.assertEqual(game.players[0].position, (0,4))

if __name__ == '__main__':
    unittest.main()
