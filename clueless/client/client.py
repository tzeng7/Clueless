import pygame
import pygame_gui

from clueless.client.connection import GameConnection
from clueless.client.view import TitleView, View


class GameClient(TitleView.Delegate):
    def __init__(self):
        pygame.init()
        width, height = 1000, 1000
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill('white')
        pygame.display.set_caption("Clueless")
        self.manager = pygame_gui.UIManager((self.screen.get_rect().width, self.screen.get_rect().height))
        self.game_clock = pygame.time.Clock()
        self.view = TitleView(self.screen, self.manager, delegate=self)
        self.connection = GameConnection("127.0.0.1", int(10000))

    def update(self):

        self.manager.update(self.game_clock.tick(30))
        self.connection.update()
        self.process_input()
        self.view.draw()
        pygame.display.update()

    def transition(self, new_view: View):
        self.view = new_view

    def process_input(self):
        for event in pygame.event.get():
            # quit if the quit button was pressed
            self.manager.process_events(event)
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



if __name__ == '__main__':
    c = GameClient()
    while 1:
        c.update()
