from model.player import PlayerID, PlayerIDWrapper


class ServerPlayer(PlayerIDWrapper):
    def __init__(self, wrapped: PlayerID):
        PlayerIDWrapper.__init__(self, wrapped)
        self._active = False  # deactivate for false accusation
        self._ready = False


    @property
    def ready(self):
        return self._ready

    @ready.setter
    def ready(self, ready):
        self._ready = ready

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active

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
