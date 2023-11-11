import queue

import pygame
import pygame_gui
from pygame import Surface

from clueless.client.connection import GameConnection
from clueless.client.view import TitleView, View, GameView
from clueless.messages.messages import AssignPlayerID, UpdatePlayers, StartGame


class GameClient(TitleView.Delegate):
    def __init__(self):
        pygame.init()
        width, height = 1000, 1000
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill('white')
        pygame.display.set_caption("Clueless")
        self.ui_manager = pygame_gui.UIManager((self.screen.get_rect().width, self.screen.get_rect().height))
        self.game_clock = pygame.time.Clock()
        self.view = TitleView(self.screen, self.ui_manager, delegate=self)
        self.message_queue = queue.SimpleQueue()
        self.connection = GameConnection("127.0.0.1", int(10000), self.message_queue)

    def update(self):
        self.connection.update()
        self.process_input()
        self.ui_manager.update(self.game_clock.tick(60))
        self.view.draw()
        pygame.display.update()

    def transition(self, new_view: View):
        self.ui_manager.clear_and_reset()
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

    def handle_msg_assign_player_id(self, msg: AssignPlayerID):
        if type(self.view) is not TitleView:
            print("Error: received AssignPlayerID but no longer showing title view")
        self.view.add_player_id(msg.player_id)

    def handle_msg_update_players(self, msg: UpdatePlayers):
        if type(self.view) is not TitleView:
            print("Error: received UpdatePlayers but no longer showing title view")
        print("Received UpdatePlayers!")

    def handle_msg_start_game(self, msg: StartGame):
        if type(self.view) is not TitleView:
            print("Error: received StartGame but no longer showing title view")
        print("Received StartGame!")
        self.transition(GameView(self.screen, self.ui_manager, self))


if __name__ == '__main__':
    c = GameClient()
    while 1:
        c.update()
