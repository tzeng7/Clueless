from typing import Protocol, runtime_checkable, Callable

import pygame
import pygame_gui
from pygame import Color, Surface


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


class Element(Protocol):
    def __init__(self, wrapped, rectangle: pygame.Rect, is_managed: bool):
        self.wrapped = wrapped
        self._rectangle: pygame.Rect = rectangle
        self.is_ui_manager_managed = is_managed

    @property
    def rectangle(self):
        return self._rectangle

    def set_top_left(self, top_left: (int, int)):
        self._rectangle.topleft = top_left

    def set_center(self, center: (int, int)):
        self._rectangle.center = center

    def hide(self):
        self.wrapped.hide()

    def show(self):
        self.wrapped.show()

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


class ManagedElement(Element):
    def __init__(self, any_element: pygame_gui.core.UIElement):
        super().__init__(any_element, any_element.rect, is_managed=True)

    def set_top_left(self, top_left: (int, int)):
        self.wrapped.set_position(top_left)

    def set_center(self, center: (int, int)):
        top_left = (center[0] - (self.rectangle.width // 2), center[1] - (self.rectangle.height // 2))
        self.set_top_left(top_left)


class TextInputElement(ManagedElement):
    def __init__(self, input: pygame_gui.elements.UITextEntryLine, on_text_finished: Callable[[str], None]):
        super().__init__(input)
        self.on_text_finished = on_text_finished

    def respond_to_UITextEntryFinished(self, event):
        self.on_text_finished(event.text)


class ManagedButton(ManagedElement):
    def __init__(self, button: pygame_gui.elements.UIButton, on_click: Callable[[str], None]):
        super().__init__(button)
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
        font = pygame.font.Font(filename="../resources/VT323-Regular.ttf", size=size)
        surface = font.render(text, True, primary_color, bgcolor=Color("white"))
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


class ImageElement(Element):
    def __init__(self):
        image = pygame.image.load('../resources/amongus.png').convert_alpha()
        DEFAULT_IMAGE_SIZE = (50, 50)
        # Scale the image to your needed size
        scaled_image = pygame.transform.smoothscale(image, DEFAULT_IMAGE_SIZE)
        super().__init__(scaled_image, scaled_image.get_rect(), is_managed=False)


class HorizontalStack(Element):
    def __init__(self, elements: list[Element], padding: int):
        self.elements = elements
        self.padding = padding
        total_width = 0
        for element in elements:
            total_width += element.rectangle.width
        total_width += padding * (len(elements) - 1)
        total_height = max([element.rectangle.height for element in elements])
        super().__init__(self.elements, pygame.Rect((0, 0), (total_width, total_height)), is_managed=False)

    def set_center(self, center: (int, int)):
        pass

    def set_top_left(self, top_left: (int, int)):
        pass

    def respond_to_event(self, fn_name, event):
        for element in self.elements:
            if hasattr(element, fn_name):
                getattr(element, fn_name)(event)
