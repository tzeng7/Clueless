from enum import Enum

class Location(Enum):
    STUDY = "Study"
    HALL = "Hall"
    LOUNGE = "Lounge"
    LIBRARY = "Library"
    BILLIARD = "Billiard"
    DINING = "Dining"
    CONSERVATORY = "Conservatory"
    BALLROOM = "Ballroom"
    KITCHEN = "Kitchen"


class Weapon(Enum):
    ROPE = "Rope"
    DAGGER = "Dagger"
    WRENCH = "Wrench"
    REVOLVER = "Revolver"
    CANDLESTICK = "Candlestick"
    LEAD_PIPE = "Lead Pipe"


class Character(Enum):
    SCARLET = "Scarlet"
    PLUM = "Plum"
    MUSTARD = "Mustard"
    WHITE = "White"
    GREEN = "Green"
    PEACOCK = "Peacock"

    def get_starting_position(self):
        char_to_position = {
            self.SCARLET: (0, 3),
            self.PLUM: (1, 0),
            self.MUSTARD: (1, 4),
            self.WHITE: (4, 3),
            self.GREEN: (4, 1),
            self.PEACOCK: (3, 0)
        }
        return char_to_position[self]


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SECRET_PASSAGEWAY = 5


class CardType(Enum):
    CHARACTER = 1
    WEAPON = 2
    LOCATION = 3

