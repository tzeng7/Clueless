from enum import Enum


class RoomType(Enum):
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
    SCARLET = 1
    PLUM = 2
    MUSTARD = 3
    WHITE = 4
    GREEN = 5
    PEACOCK = 6

    def get_starting_position(self):
        dict = {
            self.SCARLET: (0, 3),
            self.PLUM: (1, 0),
            self.MUSTARD: (1, 4),
            self.WHITE: (4, 3),
            self.GREEN: (4, 1),
            self.PEACOCK: (3, 0)
        }
        return dict[self]


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SECRET_PASSAGEWAY = 5
