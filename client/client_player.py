from model.player import PlayerIDWrapper, PlayerID
from model.suggestion import Suggestion


class ClientPlayer(PlayerIDWrapper):
    def __init__(self, player_id: PlayerID):
        PlayerIDWrapper.__init__(self, player_id)
        # client side
        self.cards = []
        # self.can_suggest = False
        self.active = True
        self.has_moved = False

    def suggestion_responses(self, suggestion: Suggestion):
        return [card for card in self.cards if card.matches(suggestion)]

    @property
    def has_moved(self):
        return self._has_moved

    @has_moved.setter
    def has_moved(self, has_moved):
        self._has_moved = has_moved
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active
