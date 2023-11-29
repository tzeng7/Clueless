import queue

import pygame
import pygame_gui
from typing import cast

from clueless.client.client_game_manager import ClientGameManager
from clueless.client.client_player import ClientPlayer
from clueless.client.connection import GameConnection
from clueless.client.view import TitleView, View, GameView, ActionView, DisproveView
from clueless.messages.messages import AssignPlayerID, UpdatePlayers, StartGame, Move, DealCards, YourTurn, Suggest, \
    RequestDisprove, Disprove, EndTurn, Accuse
from clueless.model.board import Room
from clueless.model.board_enums import ActionType, Direction, Character, Weapon, Location
from clueless.model.card import Card


class GameClient(TitleView.Delegate):
    def __init__(self):
        pygame.init()
        width, height = 1000, 1000
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Clueless")
        self.ui_manager = pygame_gui.UIManager((self.screen.get_rect().width, self.screen.get_rect().height))
        self.game_clock = pygame.time.Clock()
        self.view: View = TitleView(self.screen, self.ui_manager, delegate=self)
        self.message_queue = queue.SimpleQueue()
        self.connection = GameConnection("127.0.0.1", int(10000), self.message_queue)
        self.game_manager: ClientGameManager = None
        self.player: ClientPlayer = None

    def update(self):
        self.connection.update()
        self.process_input()
        self.ui_manager.update(self.game_clock.tick(60))
        self.screen.fill('white')
        self.view.draw()
        pygame.display.update()

    def transition(self, new_view: View):
        self.screen.fill('white')
        self.view = new_view

    def process_input(self):
        while not self.message_queue.empty():
            next_message = self.message_queue.get()
            fn_name = f"handle_msg_{next_message.name}"
            if hasattr(self, fn_name):
                getattr(self, fn_name)(next_message)
            else:
                print(f"Couldn't find handler for {next_message.name}")

        for event in pygame.event.get():
            # quit if the quit button was pressed
            self.ui_manager.process_events(event)
            if event.type == pygame.QUIT:
                exit()
            else:
                self.view.respond_to_event(event)

    # TitleView.Delegate
    def did_set_nickname(self, nickname: str):
        if type(self.view) is not TitleView:
            print("Error: received ready but no longer showing title view")
        self.connection.join_game(nickname=nickname)
        self.view.transition_to_ready_button()

    def did_ready(self):
        if type(self.view) is not TitleView:
            print("Error: received ready but no longer showing title view")
        print("READY FROM DELEGATE!")
        self.connection.ready()

    # ActionView.Delegate
    def did_move(self, movement_option: (Direction, (int, int))):
        if type(self.view) is not ActionView:
            print("Error: received movement selection but no longer showing action view")
        self.connection.Send(self.game_manager.move(movement_option[1]))

    def did_suggest(self, character: Character, weapon: Weapon):
        if type(self.view) is not ActionView:
            print("Error: received suggestion selection but no longer showing action view")
        print(f"Suggested: {character}, {weapon}")
        space = self.game_manager.board.get_player_space(self.player.player_id)
        location = cast(Room, space).room_type
        self.connection.Send(self.game_manager.suggest((character, weapon, location)))

    def did_accuse(self, character: Character, weapon: Weapon, location: Location):
        self.connection.Send(self.game_manager.accuse((character, weapon, location)))

    def did_end_turn(self):
        self.connection.Send(self.game_manager.end_turn())

    def did_disprove(self, card: Card, suggest: Suggest):
        self.connection.Send(self.game_manager.disprove(card, suggest))

    def handle_msg_assign_player_id(self, msg: AssignPlayerID):
        if type(self.view) is not TitleView:
            print("Error: received AssignPlayerID but no longer showing title view")
        self.player = ClientPlayer(msg.player_id)
        # self.view.add_player_id(msg.player_id)

    def handle_msg_update_players(self, msg: UpdatePlayers):
        if type(self.view) is not TitleView:
            print("Error: received UpdatePlayers but no longer showing title view")
        self.view.add_player_id(msg.players)
        print("Received UpdatePlayers!")

    def handle_msg_start_game(self, msg: StartGame):
        if type(self.view) is not TitleView:
            print("Error: received StartGame but no longer showing title view")
        print("Received StartGame!")
        self.transition(GameView(self.screen, self.ui_manager, self))
        self.game_manager = ClientGameManager(self.player, msg.board)

    def handle_msg_start_turn(self, msg: YourTurn):
        print("Received Start Turn!")
        self.game_manager.start_turn(msg.turn_id)
        self.transition(ActionView(self.screen, self.ui_manager, self, self.game_manager))

    def handle_msg_deal_cards(self, msg: DealCards):
        print("TODO: Received DealCards!")
        self.player.cards = msg.cards
        print(self.player.cards)

    def handle_msg_ClientAction_move(self, msg: Move):
        print("Received Move!")
        self.game_manager.board.move(msg.player_id, msg.position)
        print(self.game_manager.board)
        if msg.player_id == self.player.player_id:
            self.transition(ActionView(self.screen, self.ui_manager, self, self.game_manager))

    def handle_msg_ClientAction_suggest(self, suggest: Suggest):
        if self.player.player_id == suggest.player_id:
            self.game_manager.suggest(suggest.suggestion)

    def handle_msg_request_disprove(self, request_disprove: RequestDisprove):
        print("Received Request Disprove")
        print(request_disprove.suggest.suggestion)
        disproving_cards = self.game_manager.disproving_cards(request_disprove.suggest)
        self.transition(DisproveView(self.screen, self.ui_manager, self, disproving_cards, request_disprove.suggest))

        action_view: ActionView = self.view

    def handle_msg_ClientAction_disprove(self, disprove: Disprove):
        if not disprove.card:
            print("No card to disprove.")
        else:
            print(f"The disproving card is {disprove.card.card_value}")
        if disprove.suggest.player_id == self.player.player_id:
            self.transition(ActionView(self.screen, self.ui_manager, self, self.game_manager))

    def handle_msg_ClientAction_accuse(self, accuse: Accuse):
        print(f"The accusation is {accuse.accusation[0], accuse.accusation[1], accuse.accusation[2]}")


    def handle_msg_ClientAction_end_turn(self, end_turn: EndTurn):
        pass


if __name__ == '__main__':
    c = GameClient()
    while 1:
        c.update()
