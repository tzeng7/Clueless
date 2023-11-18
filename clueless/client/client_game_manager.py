from typing import cast

from client_player import ClientPlayer
from clueless.messages.messages import BaseClientAction, Move, Suggest, Disprove, EndTurn, Accuse, EndGame
from clueless.model.board import Board, Room
from clueless.model.board_enums import ActionType, Direction, Character, Weapon, Location
from clueless.model.card import Card


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

    def disproving_cards(self, suggestion: Suggest):
        disproving_cards = []
        for card in self.player.cards:
            if card.matches(suggestion.suggestion):
                disproving_cards.append(card)
        return disproving_cards

    def disprove(self, card: Card, suggest: Suggest):
        disprove_command = Disprove(player_id=self.player.player_id,
                                    card=card,
                                    suggest=suggest)
        return disprove_command

    def move(self, position: (int, int)):
        move_command = Move(
            player_id=self.player.player_id,
            position=position
        )
        self.current_turn.actions_taken.append(move_command)
        return move_command

    def suggest(self, suggestion: (Character, Weapon, Location)):
        suggest_command = Suggest(player_id=self.player.player_id, suggestion=suggestion)
        self.current_turn.actions_taken.append(suggest_command)
        return suggest_command

    def accuse(self, accusation: (Character, Weapon, Location)):
        accuse_command = Accuse(
            player_id=self.player.player_id,
            accusation=accusation
        )
        self.current_turn.actions_taken.append(accuse_command)
        return accuse_command

    def end_turn(self):
        selected_action = EndTurn(player_id=self.player.player_id)
        self.current_turn.actions_taken.append(selected_action)
        return selected_action

    def handle_suggestion(self, suggest: Suggest):
        suggested_player_id = self.board.get_player_id(suggest.suggestion[0])
        location = suggest.suggestion[2].get_position()
        if not location == self.board.get_player_position(
                suggested_player_id):  # no change in location so we don't move
            self.board.move(suggested_player_id, location)
            if suggested_player_id == self.player.player_id:
                self.player.is_lastmove_suggested = True
                print(f"Moved current player by suggestion: {self.player.is_lastmove_suggested}")

    def handle_accusation_response(self, accuse: Accuse):

        if accuse.is_correct:
            print("Congratulations! Your accusation was correct. You win!")
            selected_action = EndGame()
        else:
            print("Sorry, your accusation was incorrect. You are eliminated from the game.")
            self.player.active = False
            selected_action = EndTurn(player_id=self.player.player_id)

        return selected_action

    def available_movement_options(self):
        return self.board.get_movement_options(self.player.player_id)

    def available_actions(self):

        available = []

        if self.board.get_movement_options(self.player.player_id) and not self.current_turn.actions_taken:
            available.append(ActionType.MOVE)
        if self.player.is_lastmove_suggested or (self.current_turn.is_last_action_move() and
                                                 self.board.is_in_room(
                                                     self.player.player_id)):  # or moved by suggestion
            available.append(ActionType.SUGGEST)
        available.append(ActionType.ACCUSE)
        if len(available) == 1 and available[0] == ActionType.ACCUSE:
            available.append(ActionType.END_TURN)

        if not self.current_turn.actions_taken:
            self.player.is_lastmove_suggested = False  # reset is_lastmove_suggested if it is the first action to be taken
            # TODO: remove the SUGGEST option if we suggested in this room last turn,
        return available
