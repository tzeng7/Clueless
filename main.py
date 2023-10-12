from board import Board
from board_enums import Character, Location, Weapon, CardType
import random

# future features:
#   - lobby phase
#       - broadcasting users who have joined
#       - dropping from a lobby
#       - selecting your character

class Player:
    def __init__(self, character): #TODO: name for customization/personalization
        self.position = None #not initialized
        self.character = character
        self.active = False
        self.cards = [] #added

    def initialize_in_game(self):
        self.position = self.character.get_starting_position()

    # TODO: convert to python property
    def set_position(self, position):
        self.position = position

    def set_cards(self, card):
        self.cards.append(card)

    def get_character(self):
        return self.character
class Card:
    def __init__(self, card_type: CardType, card_value: int | str):
        self.card_type = card_type
        self.card_value = card_value

    @staticmethod
    def new_weapon_card(weapon_type: Weapon):
        return Card(card_type=CardType.WEAPON, card_value=weapon_type.value)

    @staticmethod
    def new_location_card(room_type: Location):
        return Card(card_type=CardType.LOCATION, card_value=room_type.value)

    @staticmethod
    def new_character_card(character: Character):
        return Card(card_type=CardType.CHARACTER, card_value=character.value)

    def matches(self, suggestion: (Character, Weapon, Location)):
        if self.card_type == CardType.CHARACTER:
            return self.card_value == suggestion[0].value
        if self.card_type == CardType.WEAPON:
            return self.card_value == suggestion[1].value
        if self.card_type == CardType.LOCATION:
            return self.card_value == suggestion[2].value
        

class GameModel:

    def __init__(self):
        self.winning_combination = None
        self.players = []
        self.board = None

        #for now


    def add_player(self):
        next_character = list(Character)[len(self.players)]
        self.players.append(Player(next_character))

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
    def distribute_cards(self):
        cards = self.__create_cards()
        for i in range(0, len(cards)):
            self.players[i % len(self.players)].cards.append(cards[i])

    def start_game(self):

        self.distribute_cards()

        self.board = Board()

    #TODO: CARDS & RANDOMIZATION OF CARDS
    def move(self, player, direction):
        self.board.move_in_direction(player, direction)

    def suggest(self, accuser, accused, weapon):
        #move accused to accuser's location
        self.board.move(accused, accuser.position) #TODO: move weapon into location

        #cue suggestion_responses

    def suggestion_responses(self, responder: Player, suggestion: (Character, Weapon, Location)):
        return [card for card in responder.cards if card.matches(suggestion)]

    def accuse(self, accuser, character, weapon, location):
        # deactivate player if wrong; return boolean whether right or wrong
        if (character, weapon, location) == self.winning_combination:
            return 'Game Over'
        accuser.active = False
        return accuser + 'inactive'
