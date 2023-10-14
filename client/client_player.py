from model.player import PlayerIDWrapper, PlayerID
from model.suggestion import Suggestion


class ClientPlayer(PlayerIDWrapper):
    def __init__(self, player_id: PlayerID):
        PlayerIDWrapper.__init__(self, player_id)
        # client side
        self.cards = []
        # self.can_suggest = False
        self.active = True

    def suggestion_responses(self, suggestion: Suggestion):
        return [card for card in self.cards if card.matches(suggestion)]

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active