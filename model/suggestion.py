from model.board_enums import Character, Weapon, Location


class Suggestion:
    def __init__(self, character: Character, weapon: Weapon, location: Location):
        self.character = character
        self.weapon = weapon
        self.location = location