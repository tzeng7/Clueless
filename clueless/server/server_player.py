from PodSixNet.Channel import Channel

from clueless.messages.messages import BaseMessage
from clueless.model.player import PlayerID, PlayerIDWrapper


class ServerPlayer(PlayerIDWrapper):
    def __init__(self, player_id: PlayerID, channel: Channel):
        PlayerIDWrapper.__init__(self, player_id)
        self._active = True  # deactivate for false accusation
        self._ready = False
        self._channel = channel
        self._cards = []

    def Send(self, message: BaseMessage):
        self._channel.Send(message.serialize())

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

    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        self._cards = cards
