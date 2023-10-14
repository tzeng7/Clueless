from model.board import Board
from model.board_enums import Character, Location, Weapon, CardType
import random

from model.card import Card
from server_player import ServerPlayer


# future features:
#   - lobby phase
#       - broadcasting users who have joined
#       - dropping from a lobby
#       - selecting your character
class GameManager:

    def __init__(self, players: [ServerPlayer]):
        # TODO: Sort this into play order
        self.players = sorted(players, key=lambda x: x.player_id.character.value)
        self.board = Board()
        self.turn = 0
        self.winning_combination = None


    def start_game(self):
        # Distribute Cards
        cards = self.__create_cards()
        for i in range(0, len(cards)):
            self.players[i % len(self.players)].cards.append(cards[i])

        # Ask for turn

    def __create_cards(self):
        cards = []

        #how to choose specific combination and distribute the rest
        self.winning_combination = (Card(CardType.CHARACTER, random.choice(list(Character))),
                                    Card(CardType.LOCATION, random.choice(list(Location))),
                                    Card(CardType.WEAPON, random.choice(list(Weapon))))


        cards.extend([Card(CardType.CHARACTER, x.value) for x in Character if not x.value == self.winning_combination[0]])
        cards.extend([Card(CardType.LOCATION, x.value) for x in Location if not x.value == self.winning_combination[1]])
        cards.extend([Card(CardType.WEAPON, x.value) for x in Weapon if not x.value == self.winning_combination[2]])
        random.shuffle(cards)
        return cards
    #added



    #TODO: CARDS & RANDOMIZATION OF CARDS
    def move(self, player, direction):
        self.board.move_in_direction(player, direction)

    def suggest(self, accuser, accused, weapon):
        #move accused to accuser's location
        self.board.move(accused, accuser.position) #TODO: move weapon into location

        #cue suggestion_responses

    def accuse(self, accuser, character, weapon, location):
        # deactivate player if wrong; return boolean whether right or wrong
        if (character, weapon, location) == self.winning_combination:
            return 'Game Over'
        accuser.active = False
        return accuser + 'inactive'
