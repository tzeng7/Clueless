from typing import Protocol, runtime_checkable, Callable

import pygame
import pygame_gui
from pygame import Color


@runtime_checkable
class Clickable(Protocol):
    def clicked(self):
        pass


@runtime_checkable
class Hoverable(Protocol):
    def mouse_over(self):
        pass

    def mouse_away(self):
        pass


@runtime_checkable
class Element(Protocol):
    def __init__(self, wrapped, rectangle: pygame.Rect, is_managed: bool):
        self.wrapped = wrapped
        self.rectangle = rectangle
        self.is_ui_manager_managed = is_managed

    # @classmethod
    # def from_gui_managed(cls, element: pygame_gui.core.UIElement):
    #     cls(element, rectangle=element.rect, is_managed=True)
    #
    # @classmethod
    # def from_surface(cls, surface: pygame.Surface):
    #     cls(surface, rectangle=surface.get_rect(), is_managed=False)

    def respond_to_MouseDown(self, event):
        if not isinstance(self, Clickable):
            return
        if self.rectangle.collidepoint(event.pos[0], event.pos[1]):
            self.clicked()

    def respond_to_MouseMotion(self, event):
        if not isinstance(self, Hoverable):
            return
        if self.rectangle.collidepoint(event.pos[0], event.pos[1]):
            self.mouse_over()
        else:
            self.mouse_away()


class TextInputElement(Element):
    def __init__(self, input: pygame_gui.elements.UITextEntryLine, on_text_finished: Callable[[str], None]):
        super().__init__(input, input.rect, is_managed=True)
        self.on_text_finished = on_text_finished

    def respond_to_UITextEntryFinished(self, event):
        self.on_text_finished(event.text)

class ManagedButton(Element):
    def __init__(self, button: pygame_gui.elements.UIButton, on_click: Callable[[str], None]):
        super().__init__(button, button.rect, is_managed=True)
        self.on_click = on_click

    def respond_to_UIButtonPressed(self, event):
        self.on_click()

class TextElement(Element, Clickable, Hoverable):

    def __init__(self,
                 text: str,
                 size: int = 32,
                 primary_color: Color = Color("black"),
                 highlight_color: Color | None = None,
                 on_mouse_down: Callable[[], None] | None = None):
        surface = pygame.font.Font(size=size).render(text, True, primary_color)
        super().__init__(surface, surface.get_rect(), is_managed=False)
        self.text = text
        self.size = size
        self.primary_color = primary_color
        self.highlight_color = highlight_color
        self.on_mouse_down = on_mouse_down
        self.highlighted = False

    def mouse_over(self):
        if self.highlight_color and not self.highlighted:
            self.highlighted = True
            self.__change_color(self.highlight_color)

    def mouse_away(self):
        if self.highlighted:
            self.highlighted = False
            self.__change_color(self.primary_color)


    def __change_color(self, color):
        old_rect = self.rectangle
        self.wrapped = pygame.font.Font(size=self.size).render(self.text, True, color)
        self.wrapped.get_rect().center = old_rect.center

    def clicked(self):
        if not self.on_mouse_down:
            return
        self.on_mouse_down()
