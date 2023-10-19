from client_player import ClientPlayer
from messages.messages import ClientAction
from model.board import Board
from model.board_enums import ActionType, Direction, Character, Weapon, Location


class Turn:

    def __init__(self, turn_id):
        self.turn_id: int = turn_id
        self.actions_taken: list[ClientAction] = []


class ClientGameManager:
    def __init__(self, player, board):
        self.player: ClientPlayer = player
        self.previous_turn = None
        self.current_turn = None
        self.board: Board = board

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
                # TODO: LOG BOARD // TEST EACH DIRECTION AND TRAVERSE WHOLE BOARD // TEST BEING BLOCKED IN HALLWAY
                # print out which room has what per row of grid // string wrapper for board
                if not self.player.initialized:
                    selected_action = ClientAction.Move(
                        player_id=self.player.player_id,
                        position=self.player.character.get_starting_position()
                    )
                    self.player.initialized = True
                else:
                    possible_directions = self.board.get_movement_options(self.player.player_id)
                    for idx, possible_choice in enumerate(possible_directions):
                        print(f"{idx + 1}. {possible_choice[0].name}")
                    choice = int(input("Choose direction: "))
                    selected_action = ClientAction.Move(
                        player_id=self.player.player_id,
                        position=possible_directions[choice - 1][1]
                    )
                # TODO: Suggest/Accuse
            case ActionType.SUGGEST:
                print([character.value for character in list(Character)])
                print([weapon.value for weapon in Weapon])
                print([location.value for location in Location])

                c, w, l = int(input("select character: ")), int(input("select weapon: ")), int(input("select location: "))

                selected_action = ClientAction.Suggest(player_id=self.player.player_id,
                                                       suggestion=(
                                                           list(Character)[c], list(Weapon)[w], list(Location)[l]))
            case ActionType.ACCUSE:
                selected_action = ClientAction.EndTurn(player_id=self.player.player_id)
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
            available = available[(available.index(last_action) + 1):]

        # TODO: remove the SUGGEST option if we suggested in this room last turn,
        # and we did not move into a room by another player's suggestion
        return available
