from clueless.model.board_enums import CardType, Weapon, Location, Character


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

    def __repr__(self):
        return f"Card({self.card_type}, value={self.card_value})"

