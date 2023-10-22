import pickle
import uuid
from typing import Self
import pdb

from model.card import Card
from model.player import PlayerID


class BaseMessage:
    name = "BaseMessage"

    def __init__(self):
        self.uuid = str(uuid.uuid4())

    def serialize(self):
        return {"action": self.name, "uuid": self.uuid, "payload": pickle.dumps(self).hex()}

    @staticmethod
    def deserialize(data) -> Self:
        return pickle.loads(bytes.fromhex(data["payload"]))


# SERVER BOUND

class JoinGame(BaseMessage):
    name = "join_game"

    def __init__(self, nickname):
        super().__init__()
        self.nickname = nickname


class Ready(BaseMessage):
    name = "ready"


# CLIENT BOUND
class StartGame(BaseMessage):
    name = "start_game"

#------------start of modification-------------#
class YourTurnMessage(BaseMessage):
    name = "your_turn"
    pdb.set_trace()

class NotYourTurnMessage(BaseMessage):
    name = "not_your_turn"
    pdb.set_trace()

class MakeMoveMessage(BaseMessage):
    name = "make_move"
    def __init__(self, move_data):
        super().__init__()
        self.move_data = move_data


#------------end of modification-------------#

class AssignPlayerID(BaseMessage):
    name = "assign_player_id"

    def __init__(self, player_id: PlayerID):
        super().__init__()
        self.player_id = player_id


class UpdatePlayers(BaseMessage):
    name = "update_players"

    def __init__(self, players: [PlayerID]):
        super().__init__()
        self.players: [PlayerID] = players


class DealCards(BaseMessage):
    name = "deal_cards"

    def __init__(self, cards: [Card]):
        super().__init__()
        self.cards = cards

