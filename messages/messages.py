import pickle
import uuid
from typing import Self

from model.board import Board
from model.board_enums import Direction, ActionType, Character, Weapon, Location
from model.card import Card
from model.player import PlayerID


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


class ClientAction:
    class BaseAction(BaseMessage):
        name = "ClientAction"

        def __init__(self, player_id: PlayerID):
            super().__init__()
            self.player_id = player_id
            if hasattr(self, "action_type") and self.action_type:
                self.name = f"ClientAction_{self.action_type.value}"

        @staticmethod
        def name_for_action(action_type: ActionType):
            return f"ClientAction_{action_type.value}"

    class Move(BaseAction):
        action_type = ActionType.MOVE

        def __init__(self, player_id: PlayerID, position: (int, int)):
            super().__init__(player_id)
            self.position = position

    class Suggest(BaseAction):
        action_type = ActionType.SUGGEST

        def __init__(self, player_id: PlayerID, suggestion: (Character, Weapon, Location)):
            super().__init__(player_id)
            self.suggestion = suggestion

    class Disprove(BaseAction):
        action_type = ActionType.DISPROVE

        def __init__(self, player_id: PlayerID, card: Card):
            super().__init__(player_id)
            self.card = card

    class EndTurn(BaseAction):
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

    def __init__(self, players: [PlayerID]):
        super().__init__()
        self.players: [PlayerID] = players


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

    def __init__(self, turn_id: int):
        super().__init__()
        self.turn_id: int = turn_id
