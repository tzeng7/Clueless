import pickle
import uuid
from typing import Self

from clueless.model.board import Board
from clueless.model.board_enums import ActionType, Character, Weapon, Location
from clueless.model.card import Card
from clueless.model.player import PlayerID


class BaseMessage:
    name = "base_message"

    def __init__(self):
        self.uuid = str(uuid.uuid4())

    def serialize(self):
        return {"action": self.name, "uuid": self.uuid, "payload": pickle.dumps(self).hex()}

    @classmethod
    def deserialize(cls, data) -> Self:
        return pickle.loads(bytes.fromhex(data["payload"]))


# SERVER BOUND

class JoinGame(BaseMessage):
    name = "join_game"

    def __init__(self, nickname):
        super().__init__()
        self.nickname = nickname


class Ready(BaseMessage):
    name = "ready"

class EndGame(BaseMessage):
    name = "end_game"

class BaseClientAction(BaseMessage):
    action_type = None
    name = "ClientAction"

    @classmethod
    def client_action_name(cls):
        if hasattr(cls, "action_type") and cls.action_type:
            return f"ClientAction_{cls.action_type.value}"
        else:
            return "ClientAction"

    def __init__(self, player_id: PlayerID):
        super().__init__()
        self.player_id = player_id
        self.name = self.client_action_name()


class Move(BaseClientAction):
    action_type = ActionType.MOVE

    def __init__(self, player_id: PlayerID, position: (int, int)):
        super().__init__(player_id)
        self.position = position


class Suggest(BaseClientAction):
    action_type = ActionType.SUGGEST

    def __init__(self, player_id: PlayerID, suggestion: (Character, Weapon, Location)):
        super().__init__(player_id)
        self.suggestion = suggestion


class Disprove(BaseClientAction):
    action_type = ActionType.DISPROVE

    def __init__(self, player_id: PlayerID, card: Card | None, suggest: Suggest):
        super().__init__(player_id)
        self.card = card
        self.suggest = suggest


class EndTurn(BaseClientAction):
    action_type = ActionType.END_TURN

    def __init__(self, player_id: PlayerID):
        super().__init__(player_id)


# CLIENT BOUND

class AssignPlayerID(BaseMessage):
    name = "assign_player_id"

    def __init__(self, player_id: PlayerID):
        super().__init__()
        self.player_id = player_id


class UpdatePlayers(BaseMessage):
    name = "update_players"

    def __init__(self, players: [(PlayerID, bool)]):
        super().__init__()
        self.players: [(PlayerID, bool)] = players


class StartGame(BaseMessage):
    name = "start_game"

    def __init__(self, board: Board):
        super().__init__()
        self.board = board


class DealCards(BaseMessage):
    name = "deal_cards"

    def __init__(self, cards: [Card]):
        super().__init__()
        self.cards = cards


class YourTurn(BaseMessage):
    name = "start_turn"

    def __init__(self, turn_id: int, player_id: PlayerID):
        super().__init__()
        self.turn_id: int = turn_id
        self.player_id: PlayerID = player_id


class RequestDisprove(BaseMessage):
    name = "request_disprove"

    def __init__(self, suggest: Suggest):
        super().__init__()
        self.suggest = suggest


# added accuse class

class Accuse(BaseClientAction):
    action_type = ActionType.ACCUSE
    is_correct = False

    def __init__(self, player_id: PlayerID, accusation: (Character, Weapon, Location)):
        super().__init__(player_id)
        self.accusation = accusation


class EndGame(BaseMessage):
    name = "end_game"

    def __init__(self, accuse: Accuse):
        super().__init__()
        self.accuse = accuse
