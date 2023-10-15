from client_player import ClientPlayer
from messages.messages import ClientAction
from model.board_enums import ActionType, Direction


class Turn:

    def __init__(self, turn_id):
        self.turn_id: int = turn_id
        self.actions_taken: list[ClientAction] = []

class ClientGameManager:
    def __init__(self, player):
        self.player: ClientPlayer = player
        self.previous_turn = None
        self.current_turn = None



    def start_turn(self, turn_id: int):
        self.previous_turn = self.current_turn
        self.current_turn = Turn(turn_id=turn_id)

    def next_action(self) -> ClientAction.BaseAction:
        print("Choose an action: ")
        actions = self.__available_actions()
        for index, action in enumerate(actions):
            print(f"{index + 1}.  {action.value}")
        choice = int(input("Choice: "))
        while not choice or choice <= 0 or choice > len(actions):
            print("Invalid input!")
            choice = int(input("Choice: "))

        match actions[choice - 1]:
            case ActionType.MOVE:
                # TODO: implement move logic
                selected_action = ClientAction.Move(
                    player_id=self.player.player_id,
                    position=self.player.character.get_starting_position()
                )
            case ActionType.END_TURN:
                selected_action = ClientAction.EndTurn(player_id=self.player.player_id)
            case _:
                raise NotImplementedError("ActionType not yet implemented!")
        self.current_turn.actions_taken.append(selected_action)
        return selected_action


    # def move_from_suggestion(self, turn_id, suggestion: ClientAction.Move):
    #     new_turn = Turn(turn_id=turn_id)
    #     new_turn.actions_taken = [ActionType.MOVE]
    #     self.previous_turn = self.current_turn
    #     self.current_turn = new_turn

    def __available_actions(self) -> list[ActionType]:
        if not self.player.active:
            return [ActionType.END_TURN]
        available = list(ActionType)

        if self.current_turn.actions_taken:
            # consider all actions that come after the action we just took.
            # e.g. if SUGGEST was the last move, only ACCUSE and END_TURN should be available
            last_action = self.current_turn.actions_taken[-1].action_type
            available = available[(available.index(last_action)+1):]

        # TODO: remove the SUGGEST option if we suggested in this room last turn,
        # and we did not move into a room by another player's suggestion
        return available

