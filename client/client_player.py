from model.player import PlayerIDWrapper, PlayerID


class ClientPlayer(PlayerIDWrapper):
    def __init__(self, player_id: PlayerID):
        PlayerIDWrapper.__init__(self, player_id)
        # client side
        self.cards = []
        # self.can_suggest = False
        self.active = True
        self.is_lastmove_suggested = False
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active
