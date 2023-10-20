from model.board_enums import Character


class PlayerID:
    # TOOD: equality
    def __init__(self, character: Character, nickname: str):
        self.character = character
        self.nickname = nickname

    def __eq__(self, other):
        # Equality Comparison between two objects
        return self.character == other.character and self.nickname == other.nickname

    def __hash__(self):
        # hash(custom_object)
        return hash((self.character, self.nickname))

    def __repr__(self):
        return f"PlayerID(character={self.character.value}, nickname={self.nickname})"

    def __eq__(self, other):
        return self.character == other.character and self.nickname == other.nickname


class PlayerIDWrapper:
    def __init__(self, player_id: PlayerID):
        self.player_id = player_id

    @property
    def nickname(self):
        return self.player_id.nickname

    @property
    def character(self):
        return self.player_id.character


class PlayerToken(PlayerIDWrapper):
    def __init__(self, player_id: PlayerID):
        super().__init__(player_id=player_id)
        self.position = None

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position