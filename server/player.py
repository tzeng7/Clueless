from enum import Enum


class Character(Enum):
    SCARLET = "Scarlet"
    PLUM = "Plum"
    MUSTARD = "Mustard"
    WHITE = "White"
    GREEN = "Green"
    PEACOCK = "Peacock"

class Player:
    def __init__(self, character):
        self.character = character
        self.nickname = f"Anonymous ({character.value})"
        self._ready = False
        # self.position = None # not initialized
        # self.character = character
        # self.active = False # deactivate for false accusation
        # self.cards = []

    @property
    def ready(self):
        return self._ready

    @ready.setter
    def ready(self, ready):
        self._ready = ready

    # def enter_board(self):
    #     self.position = self.character.get_starting_position()

    # TODO: convert to python property
    # def set_position(self, position):
    #     self.position = position
    #
    # def set_cards(self, card):
    #     self.cards.append(card)
    #
    # def get_character(self):
    #     return self.character
