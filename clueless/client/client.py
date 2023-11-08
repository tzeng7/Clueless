import pygame

from clueless.client.connection import GameConnection
from clueless.client.view import TitleView, View


class GameClient(TitleView.Delegate):
    def __init__(self):
        pygame.init()
        width, height = 500, 500
        screen = pygame.display.set_mode((width, height))
        screen.fill('white')
        pygame.display.set_caption("Clueless")
        self.game_clock = pygame.time.Clock()
        self.view = TitleView(screen, delegate=self)
        # self.connection = GameConnection("127.0.0.1", int(10000))

    def update(self):
        self.game_clock.tick(60)
        # self.connection.update()
        self.process_input()
        self.view.draw()
        pygame.display.update()

    def transition(self, new_view: View):
        self.view = new_view

    def process_input(self):
        mouse_pos = pygame.mouse.get_pos()
        self.view.respond_to_mouse_hover(mouse_pos)
        for event in pygame.event.get():
            # quit if the quit button was pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.view.respond_to_mouse_down(pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                exit()

    # TitleView.Delegate
    def did_set_nickname(self):
        if type(self.view) is not TitleView:
            print("Error: received ready but no longer showing title view")
        print("READY FROM DELEGATE!")

    def did_ready(self):
        if type(self.view) is not TitleView:
            print("Error: received ready but no longer showing title view")
        print("READY FROM DELEGATE!")
        # self.connection.join_game("Leslie")
        # self.connection.ready()



if __name__ == '__main__':
    c = GameClient()
    while 1:
        c.update()
