from model.board_enums import Character


class PlayerID:
    # TOOD: equality
    def __init__(self, character: Character, nickname: str):
        self.character = character
        self.nickname = nickname

    def __repr__(self):
        return f"PlayerID(character={self.character.value}, nickname={self.nickname})"


class PlayerIDWrapper:
    def __init__(self, player_id: PlayerID):
        self.player_id = player_id

    @property
    def nickname(self):
        return self.player_id.nickname

    @property
    def character(self):
        return self.player_id.character


class PlayerToken:
    def __init__(self):
        self._position = None

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position