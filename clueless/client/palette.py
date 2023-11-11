from pygame import Color

from clueless.model.board_enums import Character


def rgb_from_hex(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Pico:
    BLACK = Color(rgb_from_hex("#000000"))
    NAVY = Color(rgb_from_hex("#1D2B53"))
    PLUM = Color(rgb_from_hex("#7E2553"))
    DARK_GREEN = Color(rgb_from_hex("#008751"))
    RED = Color(rgb_from_hex("#FF004D"))
    ORANGE = Color(rgb_from_hex("#FFA300"))
    YELLOW = Color(rgb_from_hex("#FFEC27"))
    GREEN = Color(rgb_from_hex("#00E436"))
    BLUE = Color(rgb_from_hex("#29ADFF"))
    LILAC = Color(rgb_from_hex("#83769C"))
    PINK = Color(rgb_from_hex("#FF77A8"))
    PEACH = Color(rgb_from_hex("#FFCCAA"))

    # extra
    PEACOCK = Color(rgb_from_hex("#359cbb"))

    @classmethod
    def from_character(cls, character: Character):
        char_to_color = {
            Character.SCARLET: cls.RED,
            Character.PLUM: cls.PLUM,
            Character.MUSTARD: cls.YELLOW,
            Character.WHITE: cls.BLACK,
            Character.GREEN: cls.DARK_GREEN,
            Character.PEACOCK: cls.PEACOCK
        }
        return char_to_color[character]

