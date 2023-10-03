from board import Board
from board_enums import Character, RoomType, Weapon


class GameModel:

    def __init__(self):
        self.winning_combination = None
        self.players = []
        self.board = None

    def add_player(self):
        next_character = list(Character)[len(self.players)]
        self.players.append(Player(next_character))

    def start_game(self):
        self.winning_combination = (self.players[0].character, RoomType.STUDY, Weapon.ROPE) #TODO: RANDOMIZE
        self.board = Board()

    #TODO: CARDS & RANDOMIZATION OF CARDS 10/3
    def move(self, player, direction):
        self.board.move_in_direction(player, direction)

    def suggest(self, accuser, accused, weapon):
        #move accused to accuser's location
        self.board.move(accused, accuser.position) #TODO: move weapon into location

    def disprove(self, disprover): #TODO: disprove suggestion by showing card of suggested weapon/location
        # which card in disproving character can be shown to disprove
        # if no cards then call disprove using next player



    def accuse(self, accuser, accused, weapon):
        #deactivate player if wrong; return boolean whether right or wrong


class Player:
    def __init__(self, character): #TODO: name for customization/personalization
        self.position = None #not initialized
        self.character = character
        self.active = False

    def initialize_in_game(self):
        self.position = self.character.get_starting_position()

    # TODO: convert to python property
    def set_position(self, position):
        self.position = position


