from model.player import PlayerIDWrapper, PlayerID
from model.suggestion import Suggestion


class ClientPlayer(PlayerIDWrapper):
    def __init__(self, wrapped: PlayerID):
        PlayerIDWrapper.__init__(self, wrapped)
        # client side
        self.cards = []
        self.can_suggest = False

    def suggestion_responses(self, suggestion: Suggestion):
        return [card for card in self.cards if card.matches(suggestion)]