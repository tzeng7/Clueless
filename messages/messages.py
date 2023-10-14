import pickle
import uuid
from typing import Self

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
