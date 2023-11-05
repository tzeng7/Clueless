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

    def get_position(self) -> (int, int):
        match self:
            case Location.STUDY:
                return (0, 0)
            case Location.HALL:
                return (0, 2)
            case Location.LOUNGE:
                return (0, 4)
            case Location.LIBRARY:
                return (2, 0)
            case Location.BILLIARD:
                return (2, 2)
            case Location.DINING:
                return (2, 4)
            case Location.CONSERVATORY:
                return (4, 0)
            case Location.BALLROOM:
                return (4, 2)
            case Location.KITCHEN:
                return (4, 4)


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

    @property
    def ordinal_value(self):
        return list(Character).index(self)


class Direction(Enum):
    # INITIALIZE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    SECRET_PASSAGEWAY = 5


class CardType(Enum):
    CHARACTER = 1
    WEAPON = 2
    LOCATION = 3


class ActionType(Enum):
    MOVE = "move"
    SUGGEST = "suggest"
    DISPROVE = "disprove"
    ACCUSE = "accuse"
    END_TURN = "end_turn"

    def is_user_initiated(self):
        match self:
            case ActionType.DISPROVE:
                return False
            case _:
                return True
