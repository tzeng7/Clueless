from typing import cast

from client_player import ClientPlayer
from messages.messages import BaseClientAction, Move, Suggest, Disprove, EndTurn, Accuse, IncorrectAccusation
from model.board import Board, Room
from model.board_enums import ActionType, Direction, Character, Weapon, Location


class Turn:

    def __init__(self, turn_id):
        self.turn_id: int = turn_id
        self.actions_taken: list[BaseClientAction] = []

    def is_last_action_move(self):
        return self.actions_taken and self.actions_taken[-1].action_type == ActionType.MOVE


class ClientGameManager:
    def __init__(self, player, board):
        self.player: ClientPlayer = player
        self.previous_turn = None
        self.current_turn = None
        self.board: Board = board

    def start_turn(self, turn_id: int):
        self.previous_turn = self.current_turn
        self.current_turn = Turn(turn_id=turn_id)

    def disprove(self, suggestion: Suggest):
        disproving_cards = []
        for card in self.player.cards:
            for c in card:
                if c.matches(suggestion.suggestion):
                    disproving_cards.append(c)
        print([card for card in disproving_cards])
        if not disproving_cards:
            input("No cards to disprove: Hit enter")
            selected_action = Disprove(self.player.player_id, None, suggestion)
        else:
            choice = int(input("Which card: "))
            selected_action = Disprove(self.player.player_id, disproving_cards[choice], suggestion)
        return selected_action

    def next_action(self) -> BaseClientAction:
        print("Choose an action: ")
        actions = self.__available_actions()
        for index, action in enumerate(actions):
            print(f"{index + 1}.  {action.value}")

        valid = False           # checking valid input
        while not valid:
            try:
                choice = int(input("Choice: "))
                if choice > len(actions) or choice < 1:
                    raise ValueError
                valid = True
            except ValueError:
                print("Invalid input!")

        match actions[choice - 1]:
            case ActionType.MOVE:
                # TODO: LOG BOARD // TEST EACH DIRECTION AND TRAVERSE WHOLE BOARD // TEST BEING BLOCKED IN HALLWAY
                # TODO: WHAT IF THERE ARE NO DIRECTIONS YOU CAN MOVE
                # print out which room has what per row of grid // string wrapper for board
                possible_directions = self.board.get_movement_options(self.player.player_id)
                if len(possible_directions) == 0:
                    print("You cannot move!")
                    selected_action = EndTurn(player_id=self.player.player_id)
                else:
                    for idx, possible_choice in enumerate(possible_directions):
                        print(f"{idx + 1}. {possible_choice[0].name}")
                    valid = False           # checking valid input
                    while not valid:
                        try:
                            choice = int(input("Choose direction: "))
                            if choice > len(possible_directions) or choice < 1:
                                raise ValueError
                            valid = True
                        except ValueError:
                            print("Invalid input!")
                    selected_action = Move(
                        player_id=self.player.player_id,
                        position=possible_directions[choice - 1][1]
                    )

            case ActionType.SUGGEST:
                print([character.value for character in list(Character)])
                print([weapon.value for weapon in Weapon])

                space = self.board.get_player_space(self.player.player_id)
                if self.board.is_in_room(self.player.player_id):
                    location = cast(Room, space).room_type
                else:
                    raise RuntimeError("Tried to make a suggestion but not a room")

                c, w = int(input("select character: ")), int(input("select weapon: "))

                selected_action = Suggest(player_id=self.player.player_id,
                                          suggestion=(
                                              list(Character)[c], list(Weapon)[w], location))
            case ActionType.ACCUSE:
                print("Making an accusation...")
                print([character.value for character in list(Character)])
                print([weapon.value for weapon in Weapon])
                print([location.value for location in Location])

                c = int(input("Select character for accusation: "))
                w = int(input("Select weapon for accusation: "))
                l = int(input("Select location for accusation: "))
                selected_action = Accuse(
                   player_id=self.player.player_id,
                   accusation=(list(Character)[c], list(Weapon)[w], list(Location)[l])
               )
            case ActionType.END_TURN:
                selected_action = EndTurn(player_id=self.player.player_id)

            case _:
                raise NotImplementedError("ActionType not yet implemented!")
        self.current_turn.actions_taken.append(selected_action)
        return selected_action

    def handle_suggestion(self, suggest: Suggest):
        suggested_player_id = self.board.get_player_id(suggest.suggestion[0])
        location = suggest.suggestion[2].get_position()
        if not location == self.board.get_player_position(suggested_player_id): #no change in location so we don't move
            self.board.move(suggested_player_id, location)
            if suggested_player_id == self.player.player_id:
                self.player.is_lastmove_suggested = True
                print(f"Moved current player by suggestion: {self.player.is_lastmove_suggested}")

    def handle_accusation(self, message : BaseClientAction):
        if message.name == "correct_accusation":
            print("You won the game!")
        elif message.name == "incorrect_accusation":
            print("You lost the game!")

    def __available_actions(self):

        available = []

        if self.board.get_movement_options(self.player.player_id) and not self.current_turn.actions_taken:
            available.append(ActionType.MOVE)
        if self.player.is_lastmove_suggested or (self.current_turn.is_last_action_move() and \
                self.board.is_in_room(self.player.player_id)):  # or moved by suggestion
            available.append(ActionType.SUGGEST)
        available.append(ActionType.ACCUSE)
        if len(available) == 1 and available[0] == ActionType.ACCUSE:
            available.append(ActionType.END_TURN)

        if not self.current_turn.actions_taken:
            self.player.is_lastmove_suggested = False #reset is_lastmove_suggested if it is the first action to be taken
            # TODO: remove the SUGGEST option if we suggested in this room last turn,
        return available
from typing import cast

from client_player import ClientPlayer
from messages.messages import BaseClientAction, Move, Suggest, Disprove, EndTurn, Accuse, IncorrectAccusation
from model.board import Board, Room
from model.board_enums import ActionType, Direction, Character, Weapon, Location


class Turn:

    def __init__(self, turn_id):
        self.turn_id: int = turn_id
        self.actions_taken: list[BaseClientAction] = []

    def is_last_action_move(self):
        return self.actions_taken and self.actions_taken[-1].action_type == ActionType.MOVE


class ClientGameManager:
    def __init__(self, player, board):
        self.player: ClientPlayer = player
        self.previous_turn = None
        self.current_turn = None
        self.board: Board = board

    def start_turn(self, turn_id: int):
        self.previous_turn = self.current_turn
        self.current_turn = Turn(turn_id=turn_id)

    def disprove(self, suggestion: Suggest):
        disproving_cards = []
        for card in self.player.cards:
            for c in card:
                if c.matches(suggestion.suggestion):
                    disproving_cards.append(c)
        print([card for card in disproving_cards])
        if not disproving_cards:
            input("No cards to disprove: Hit enter")
            selected_action = Disprove(self.player.player_id, None, suggestion)
        else:
            choice = int(input("Which card: "))
            selected_action = Disprove(self.player.player_id, disproving_cards[choice], suggestion)
        return selected_action

    def next_action(self) -> BaseClientAction:
        print("Choose an action: ")
        actions = self.__available_actions()
        for index, action in enumerate(actions):
            print(f"{index + 1}.  {action.value}")

        valid = False           # checking valid input
        while not valid:
            try:
                choice = int(input("Choice: "))
                if choice > len(actions) or choice < 1:
                    raise ValueError
                valid = True
            except ValueError:
                print("Invalid input!")

        match actions[choice - 1]:
            case ActionType.MOVE:
                # TODO: LOG BOARD // TEST EACH DIRECTION AND TRAVERSE WHOLE BOARD // TEST BEING BLOCKED IN HALLWAY
                # TODO: WHAT IF THERE ARE NO DIRECTIONS YOU CAN MOVE
                # print out which room has what per row of grid // string wrapper for board
                possible_directions = self.board.get_movement_options(self.player.player_id)
                if len(possible_directions) == 0:
                    print("You cannot move!")
                    selected_action = EndTurn(player_id=self.player.player_id)
                else:
                    for idx, possible_choice in enumerate(possible_directions):
                        print(f"{idx + 1}. {possible_choice[0].name}")
                    valid = False           # checking valid input
                    while not valid:
                        try:
                            choice = int(input("Choose direction: "))
                            if choice > len(possible_directions) or choice < 1:
                                raise ValueError
                            valid = True
                        except ValueError:
                            print("Invalid input!")
                    selected_action = Move(
                        player_id=self.player.player_id,
                        position=possible_directions[choice - 1][1]
                    )

            case ActionType.SUGGEST:
                print([character.value for character in list(Character)])
                print([weapon.value for weapon in Weapon])

                space = self.board.get_player_space(self.player.player_id)
                if self.board.is_in_room(self.player.player_id):
                    location = cast(Room, space).room_type
                else:
                    raise RuntimeError("Tried to make a suggestion but not a room")

                c, w = int(input("select character: ")), int(input("select weapon: "))

                selected_action = Suggest(player_id=self.player.player_id,
                                          suggestion=(
                                              list(Character)[c], list(Weapon)[w], location))
            case ActionType.ACCUSE:
                print("Making an accusation...")
                print([character.value for character in list(Character)])
                print([weapon.value for weapon in Weapon])
                print([location.value for location in Location])

                c = int(input("Select character for accusation: "))
                w = int(input("Select weapon for accusation: "))
                l = int(input("Select location for accusation: "))
                selected_action = Accuse(
                   player_id=self.player.player_id,
                   accusation=(list(Character)[c], list(Weapon)[w], list(Location)[l])
               )
            case ActionType.END_TURN:
                selected_action = EndTurn(player_id=self.player.player_id)

            case _:
                raise NotImplementedError("ActionType not yet implemented!")
        self.current_turn.actions_taken.append(selected_action)
        return selected_action

    def handle_suggestion(self, suggest: Suggest):
        suggested_player_id = self.board.get_player_id(suggest.suggestion[0])
        location = suggest.suggestion[2].get_position()
        if not location == self.board.get_player_position(suggested_player_id): #no change in location so we don't move
            self.board.move(suggested_player_id, location)
            if suggested_player_id == self.player.player_id:
                self.player.is_lastmove_suggested = True
                print(f"Moved current player by suggestion: {self.player.is_lastmove_suggested}")

    def handle_accusation(self, message : BaseClientAction):
        if message.name == "correct_accusation":
            print("You won the game!")
        elif message.name == "incorrect_accusation":
            print("You lost the game!")

    def __available_actions(self):

        available = []

        if self.board.get_movement_options(self.player.player_id) and not self.current_turn.actions_taken:
            available.append(ActionType.MOVE)
        if self.player.is_lastmove_suggested or (self.current_turn.is_last_action_move() and \
                self.board.is_in_room(self.player.player_id)):  # or moved by suggestion
            available.append(ActionType.SUGGEST)
        available.append(ActionType.ACCUSE)
        if len(available) == 1 and available[0] == ActionType.ACCUSE:
            available.append(ActionType.END_TURN)

        if not self.current_turn.actions_taken:
            self.player.is_lastmove_suggested = False #reset is_lastmove_suggested if it is the first action to be taken
            # TODO: remove the SUGGEST option if we suggested in this room last turn,
        return available

