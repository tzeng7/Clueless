import pygame
from pygame import Surface, SurfaceType, Color


class View:

    def __init__(self, screen: Surface | SurfaceType):
        self.screen = screen

    def response_to_mouse_hover(self, pos: (int, int)):
        pass

    def respond_to_mouse_down(self, pos: (int, int)):
        pass


class TitleView(View):
    HIGHLIGHT_COLOR = Color(200, 0, 0)
    DEFAULT_COLOR = Color(255, 0, 0)
    def __init__(self, screen: Surface | SurfaceType):
        super().__init__(screen=screen)
        title_text = pygame.font.Font(size=32).render("CLUELESS v 0.1.0", True, "blue")
        self.title_rect = title_text.get_rect()
        self.title_rect.center = (screen.get_rect().width // 2, screen.get_rect().height // 2)
        screen.blit(title_text, self.title_rect)
        subtitle_text = pygame.font.Font(size=24).render("READY", True, "red")
        self.subtitle_rect = subtitle_text.get_rect()
        self.subtitle_rect.center = (screen.get_rect().width // 2, self.title_rect.bottom + (self.subtitle_rect.height // 2))
        screen.blit(subtitle_text, self.subtitle_rect)
        self.ready_selected = False

    def response_to_mouse_hover(self, pos: (int, int)):
        if self.subtitle_rect.collidepoint(pos[0], pos[1]):
            print("Collided")
            if not self.ready_selected:
                self.ready_selected = True
                self.__draw_ready()
        else:
            if self.ready_selected:
                self.ready_selected = False
                self.__draw_ready()

    def respond_to_mouse_down(self, pos: (int, int)):
        if self.subtitle_rect.collidepoint(pos[0], pos[1]):
            print("READY")

    def __draw_ready(self):
        color = TitleView.DEFAULT_COLOR if not self.ready_selected else TitleView.HIGHLIGHT_COLOR
        self.screen.fill("white", self.subtitle_rect)
        subtitle_text = pygame.font.Font(size=24).render("READY", True, color)
        self.screen.blit(subtitle_text, self.subtitle_rect)

class ClientViewManager:
    def __init__(self):
        pygame.init()
        width, height = 500, 500
        screen = pygame.display.set_mode((width, height))
        screen.fill('white')
        pygame.display.set_caption("Clueless")
        self.view = TitleView(screen)


    def process_input(self):
        mouse_pos = pygame.mouse.get_pos()
        self.view.response_to_mouse_hover(mouse_pos)
        for event in pygame.event.get():
            # quit if the quit button was pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.view.respond_to_mouse_down(pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                exit()