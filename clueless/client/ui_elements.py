from typing import Protocol, runtime_checkable, Callable

import pygame
import pygame_gui
from pygame import Color, Surface

from clueless.client.ui_enums import Alignment
from clueless.model.board_enums import ActionType, Direction, Character, Weapon, Location
from clueless.model.card import Card


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
    def __init__(self, wrapped: pygame.Surface | pygame_gui.core.UIElement | list, rectangle: pygame.Rect,
                 is_managed: bool):
        self.wrapped = wrapped
        self._rectangle: pygame.Rect = rectangle
        self.is_ui_manager_managed = is_managed
        self.is_hidden = False

    @property
    def rectangle(self):
        return self._rectangle

    def set_top_left(self, top_left: (int, int)):
        self._rectangle.topleft = top_left

    def set_center(self, center: (int, int)):
        top_left = (center[0] - (self.rectangle.width // 2), center[1] - (self.rectangle.height // 2))
        self.set_top_left(top_left)

    def draw_onto(self, screen: pygame.Surface):
        if self.is_hidden:
            return
        screen.blit(self.wrapped, self.rectangle)

    def hide(self):
        self.is_hidden = True

    def show(self):
        self.is_hidden = False

    # Permanently remove and clean up element from any managers.
    def kill(self):
        pass

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


# "Managed" by pygame_gui and its UIManager
class ManagedElement(Element):
    def __init__(self, any_element: pygame_gui.core.UIElement):
        super().__init__(any_element, any_element.rect, is_managed=True)

    def draw_onto(self, screen: pygame.Surface):
        pass

    def set_top_left(self, top_left: (int, int)):
        self.wrapped.set_position(top_left)

    def hide(self):
        self.wrapped.hide()

    def show(self):
        self.wrapped.show()

    def kill(self):
        self.wrapped.kill()


class TextInputElement(ManagedElement):
    def __init__(self, input: pygame_gui.elements.UITextEntryLine, on_text_finished: Callable[[str], None]):
        super().__init__(input)
        self.on_text_finished = on_text_finished

    def respond_to_UITextEntryFinished(self, event):
        self.on_text_finished(event.text)


class ManagedButton(ManagedElement):
    def __init__(self, button: pygame_gui.elements.UIButton, on_click: Callable[[], None]):
        super().__init__(button)
        self.on_click = on_click

    def respond_to_UIButtonPressed(self, event):
        if event.ui_element == self.wrapped:
            self.on_click()


class ActionButton(ManagedButton):
    def __init__(self, action_type: ActionType, button: pygame_gui.elements.UIButton,
                 on_click: Callable[[ActionType], None]):
        super().__init__(button, lambda: on_click(action_type))
        self.action_type = action_type


class DirectionButton(ManagedButton):
    def __init__(self, movement_option: (Direction, (int, int)), button: pygame_gui.elements.UIButton,
                 on_click: Callable[[(Direction, (int, int))], None]):
        super().__init__(button, lambda: on_click(movement_option))
        self.movement_option = movement_option

class CharacterButton(ManagedButton):
    def __init__(self, character: Character, button: pygame_gui.elements.UIButton,
                 on_click: Callable[[Character], None]):
        super().__init__(button, lambda: on_click(character))
        self.character = character

class WeaponButton(ManagedButton):
    def __init__(self, weapon: Weapon, button: pygame_gui.elements.UIButton,
                 on_click: Callable[[Weapon], None]):
        super().__init__(button, lambda: on_click(weapon))
        self.weapon = weapon

class LocationButton(ManagedButton):
    def __init__(self, location: Location, button: pygame_gui.elements.UIButton,
                 on_click: Callable[[Location], None]):
        super().__init__(button, lambda: on_click(location))
        self.location = location

class CardButton(ManagedButton):
    def __init__(self, card: Card | None, button: pygame_gui.elements.UIButton,
                 on_click: Callable[[Card], None]):
        super().__init__(button, lambda: on_click(card))
        self.card = card

class TextElement(Element, Clickable, Hoverable):

    def __init__(self,
                 text: str,
                 size: int = 32,
                 primary_color: Color = Color("black"),
                 highlight_color: Color | None = None,
                 on_mouse_down: Callable[[], None] | None = None):
        self.font = pygame.font.Font(filename="../resources/VT323-Regular.ttf", size=size)
        surface = self.font.render(text, True, primary_color, bgcolor=Color("white"))
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
        self.wrapped = self.font.render(self.text, True, color)
        self.wrapped.get_rect().center = old_rect.center

    def clicked(self):
        if not self.on_mouse_down:
            return
        self.on_mouse_down()


class ImageElement(Element):
    def __init__(self, name):
        image = pygame.image.load(f'../resources/{name}.png').convert_alpha()
        DEFAULT_IMAGE_SIZE = (50, 50)
        # Scale the image to your needed size
        scaled_image = pygame.transform.smoothscale(image, DEFAULT_IMAGE_SIZE)
        super().__init__(scaled_image, scaled_image.get_rect(), is_managed=False)


class ViewBox(Element):
    def __init__(self, rect: pygame.Rect, screen: pygame.Surface):
        super().__init__(screen, rect, False)

    def draw_onto(self, screen: pygame.Surface):
        pygame.draw.rect(screen, pygame.Color(0, 0, 0, 0), self.rectangle, 3, 10)



class Stack(Element):

    def __init__(self, elements: list[Element], axis: int, alignment: Alignment, padding: int):
        self.elements = elements
        self.axis = axis
        self.alignment = alignment
        self.padding = padding
        super().__init__(elements, self.__calculate_total_rect(), is_managed=False)

    def hide(self):
        for element in self.elements:
            element.hide()

    def show(self):
        for element in self.elements:
            element.show()

    def kill(self):
        for element in self.elements:
            element.kill()

    def draw_onto(self, screen: pygame.Surface):
        for element in self.elements:
            element.draw_onto(screen)

    def respond_to_event(self, fn_name, event):
        for element in self.elements:
            if hasattr(element, fn_name):
                getattr(element, fn_name)(event)

    def set_top_left(self, top_left: (int, int)):
        relative_x = 0
        relative_y = 0
        for element in self.elements:
            if self.axis == 0:
                relative_y = self.__calculate_alignment_position(element)[1]
                temp = relative_x + element.rectangle.width + self.padding
            else:
                relative_x = self.__calculate_alignment_position(element)[0]
                temp = relative_y + element.rectangle.height + self.padding

            element.set_top_left((relative_x + top_left[0], relative_y + top_left[1]))

            if self.axis == 0:
                relative_x = temp
            else:
                relative_y = temp
        self.rectangle.topleft = top_left

    def __calculate_alignment_position(self, element):
        relative_x = 0
        relative_y = 0
        match self.alignment:
            case Alignment.CENTER:
                if self.axis == 0:
                    relative_y = (self.rectangle.height - element.rectangle.height) // 2
                else:
                    relative_x = (self.rectangle.width - element.rectangle.width) // 2
            case Alignment.LEFT:
                relative_x = 0
            case Alignment.RIGHT:
                relative_x = self.rectangle.width - element.rectangle.width
            case Alignment.TOP:
                relative_y = 0
            case Alignment.BOTTOM:
                relative_y = self.rectangle.height - element.rectangle.height
        return relative_x, relative_y

    def __calculate_total_rect(self):
        heights = [element.rectangle.height for element in self.elements]
        widths = [element.rectangle.width for element in self.elements]
        if self.axis == 0:
            total_height = max(heights)
            total_width = sum(widths)
            total_width += self.padding * (len(self.elements) - 1)
        else:
            # axis == 1
            total_height = sum(heights)
            total_height += self.padding * (len(self.elements) - 1)
            total_width = max(widths)
        return pygame.Rect((0, 0), (total_width, total_height))


class HorizontalStack(Stack):
    def __init__(self, elements: list[Element], alignment: Alignment = Alignment.CENTER, padding: int = 0):
        super().__init__(elements, axis=0, alignment=alignment, padding=padding)


class VerticalStack(Stack):
    def __init__(self, elements: list[Element], alignment: Alignment = Alignment.LEFT, padding: int = 0):
        self.alignment = alignment
        super().__init__(elements, axis=1, alignment=alignment, padding=padding)
