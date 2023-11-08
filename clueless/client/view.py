from typing import Callable, Self, Protocol

import pygame
from pygame import Surface, SurfaceType, Color, Rect


class View(Protocol):
    class Element(Protocol):
        def __init__(self, surface: Surface):
            self.surface = surface
            self.rectangle = surface.get_rect()
            self._highlighted = False

        @property
        def highlighted(self):
            return self._highlighted

        @highlighted.setter
        def highlighted(self, highlighted: bool):
            if highlighted != self._highlighted:
                self._highlighted = highlighted
                self.did_change_highlight()

        def did_change_highlight(self):
            pass

        def respond_to_mouse_down(self):
            pass

    def __init__(self, screen: Surface | SurfaceType):
        self.screen = screen
        self.elements: list[View.Element] = []

    def draw(self):
        self.screen.fill(Color("white"))
        for element in self.elements:
            self.screen.blit(element.surface, element.rectangle)

    def draw_element(self, element):
        self.screen.fill(Color("white"), element.rectangle)
        self.screen.blit(element.surface, element.rectangle)

    def respond_to_mouse_hover(self, pos: (int, int)):
        for element in self.elements:
            if element.rectangle.collidepoint(pos[0], pos[1]):
                if not element.highlighted:
                    element.highlighted = True
                    self.draw_element(element)
            else:
                if element.highlighted:
                    element.highlighted = False
                    self.draw_element(element)

    def respond_to_mouse_down(self, pos: (int, int)):
        for element in self.elements:
            if element.rectangle.collidepoint(pos[0], pos[1]):
                element.respond_to_mouse_down()


class TextElement(View.Element):

    def __init__(self,
                 text: str,
                 size: int = 32,
                 primary_color: Color = Color("black"),
                 highlight_color: Color | None = None,
                 on_mouse_down: Callable[[], None] | None = None):
        super().__init__(pygame.font.Font(size=size).render(text, True, primary_color))
        self.text = text
        self.size = size
        self.primary_color = primary_color
        self.highlight_color = highlight_color
        self.on_mouse_down = on_mouse_down
    #
    # def set_center(self, center: (int, int)):
    #     self.rectangle.center = center

    def did_change_highlight(self):
        if self.highlighted and self.highlight_color:
            chosen_color = self.highlight_color
        else:
            chosen_color = self.primary_color
        old_rect = self.rectangle
        self.surface = pygame.font.Font(size=self.size).render(self.text, True, chosen_color)
        self.surface.get_rect().center = old_rect.center

    def respond_to_mouse_down(self):
        if not self.on_mouse_down:
            return
        self.on_mouse_down()


class TitleView(View):
    HIGHLIGHT_COLOR = Color(200, 0, 0)
    DEFAULT_COLOR = Color(255, 0, 0)

    class Delegate(Protocol):
        def did_set_nickname(self):
            pass

        def did_ready(self):
            pass

    def __init__(self, screen: Surface | SurfaceType, delegate: Delegate):
        super().__init__(screen=screen)
        self.title_text = TextElement(text="CLUELESS v 0.1.0", primary_color=Color(0, 0, 255))
        self.title_text.rectangle.center = (screen.get_rect().width // 2, screen.get_rect().height // 3)
        self.elements.append(self.title_text)

        self.subtitle_text = TextElement(text="READY",
                                         size=24,
                                         primary_color=Color(255, 0, 0),
                                         highlight_color=Color(255, 153, 153),
                                         on_mouse_down=delegate.did_ready)
        self.subtitle_text.rectangle.center = (
            screen.get_rect().width // 2, self.title_text.rectangle.bottom + (self.subtitle_text.rectangle.height // 2)
        )
        self.elements.append(self.subtitle_text)
        player_list = TextElement(text="Currently in the lobby: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z", size=20, primary_color=Color(0, 0, 255))
        player_list.rectangle.bottom = screen.get_rect().bottom
        self.elements.append(player_list)


    def update_current_players(self, players: list[str]):
        pass
