from typing import Protocol, runtime_checkable, Callable, cast

import pygame
import pygame_gui
from pygame import Color

from clueless.client.ui_enums import Alignment
from clueless.model.board_enums import ActionType, Direction, Character, Weapon, Location
from clueless.model.card import Card


class Element(Protocol):
    def __init__(self,
                 wrapped: pygame.Surface | pygame_gui.core.UIElement | list[pygame_gui.core.UIElement],
                 rectangle: pygame.Rect):
        self.wrapped = wrapped
        self._hidden = False
        self._rectangle: pygame.Rect = rectangle

    def hide(self):
        self._hidden = True

    def show(self):
        self._hidden = False

    @property
    def rectangle(self):
        return self._rectangle

    def set_top_left(self, top_left: (int, int)):
        self._rectangle.topleft = top_left

    def set_center(self, center: (int, int)):  # do not override, convenience method
        top_left = (center[0] - (self.rectangle.width // 2), center[1] - (self.rectangle.height // 2))
        self.set_top_left(top_left)

    def set_bottom_right(self, bottom_right: (int, int)):  # do not override, convenience method
        top_left = (bottom_right[0] - self.rectangle.width, bottom_right[1] - self.rectangle.height)
        self.set_top_left(top_left)

    def draw_onto(self, screen: pygame.Surface):
        if not self._hidden:
            screen.blit(self.wrapped, self.rectangle)

    # Permanently remove and clean up element from any managers.
    def kill(self):
        pass


class ManagedElement(Element):
    # "Managed" by pygame_gui and its UIManager
    def __init__(self, any_element: pygame_gui.core.UIElement):
        super().__init__(any_element, any_element.rect)

    def draw_onto(self, screen: pygame.Surface):
        pass

    def set_top_left(self, top_left: (int, int)):
        self.wrapped.set_position(top_left)

    def kill(self):
        self.wrapped.kill()


    def hide(self):
        cast(pygame_gui.core.UIElement, self.wrapped).hide()

    def show(self):
        cast(pygame_gui.core.UIElement, self.wrapped).show()

class TextInputElement(ManagedElement):
    def __init__(self, input: pygame_gui.elements.UITextEntryLine, on_text_finished: Callable[[str], None]):
        super().__init__(input)
        self.on_text_finished = on_text_finished

    def respond_to_UITextEntryFinished(self, event):
        if event.ui_element == self.wrapped:
            self.on_text_finished(event.text)



class ManagedButton(ManagedElement):
    def __init__(self, button: pygame_gui.elements.UIButton, on_click: Callable[[], None]):
        super().__init__(button)
        self.on_click = on_click
        self.is_selected = False

    def respond_to_UIButtonPressed(self, event):
        if event.ui_element == self.wrapped:
            if not self.is_selected:
                self.on_click()
            self.select()

    def select(self):
        self.is_selected = True
        self.wrapped.select()

    def unselect(self):
        self.is_selected = False
        self.wrapped.unselect()

    def disable(self):
        self.wrapped.disable()

    def set_text(self, text):
        self.wrapped.set_text(text)


class PayloadButton(ManagedButton):
    def __init__(self, payload: any, button: pygame_gui.elements.UIButton,
                 on_click: Callable[[any], None]):
        super().__init__(button, lambda: on_click(payload))
        self.payload = payload

    @classmethod
    def action_button(cls, action_type: ActionType, button: pygame_gui.elements.UIButton,
                      on_click: Callable[[ActionType], None]):
        return PayloadButton(action_type, button, on_click)

    @classmethod
    def direction_button(cls, movement_option: (Direction, (int, int)), button: pygame_gui.elements.UIButton,
                         on_click: Callable[[(Direction, (int, int))], None]):
        return PayloadButton(movement_option, button, on_click)

    @classmethod
    def character_button(self, character: Character, button: pygame_gui.elements.UIButton,
                         on_click: Callable[[Character], None]):
        return PayloadButton(character, button, on_click)

    @classmethod
    def weapon_button(self, weapon: Weapon, button: pygame_gui.elements.UIButton,
                      on_click: Callable[[Weapon], None]):
        return PayloadButton(weapon, button, on_click)

    @classmethod
    def location_button(self, location: Location, button: pygame_gui.elements.UIButton,
                        on_click: Callable[[Location], None]):
        return PayloadButton(location, button, on_click)

    @classmethod
    def card_button(self, card: Card | None, button: pygame_gui.elements.UIButton,
                    on_click: Callable[[Card | None], None]):
        return PayloadButton(card, button, on_click)


class TextElement(Element):

    def __init__(self,
                 text: str,
                 align: int = pygame.FONT_LEFT,
                 size: int = 32,
                 primary_color: Color = Color("black")):
        self.font = pygame.font.Font(filename="../resources/VT323-Regular.ttf", size=size)
        self.font.align = align
        surface = self.font.render(text, True, primary_color, bgcolor=Color("white"))
        super().__init__(surface, surface.get_rect())
        self._text = text
        self.size = size
        self.primary_color = primary_color

    @property
    def strikethrough(self):
        return self.font.strikethrough

    @strikethrough.setter
    def strikethrough(self, is_strikethrough):
        self.font.strikethrough = is_strikethrough
        self.__rerender()

    @property
    def color(self):
        return self.primary_color

    @color.setter
    def color(self, new_color):
        self.primary_color = new_color
        self.__rerender()

    def __rerender(self):
        old_rect = self.rectangle
        self.wrapped = self.font.render(self.text, True, self.primary_color)
        self._rectangle = self.wrapped.get_rect()
        self.rectangle.center = old_rect.center

    def to_grayscale(self):
        self.color = self.primary_color.grayscale()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text: str):
        self._text = new_text
        self.__rerender()


class ImageElement(Element):
    def __init__(self, name, size):
        image = pygame.image.load(f'../resources/{name}.png').convert_alpha()
        # Scale the image to your needed size
        scaled_image = pygame.transform.smoothscale(image, size)
        super().__init__(scaled_image, scaled_image.get_rect())

    def to_grayscale(self):
        self.wrapped = pygame.transform.grayscale(self.wrapped)


class Rectangle(Element):
    def __init__(self, rect: pygame.Rect, screen: pygame.Surface):
        super().__init__(screen, rect)

    def draw_onto(self, screen: pygame.Surface):
        pygame.draw.rect(screen, pygame.Color(0, 0, 0, 0), self.rectangle, 4, 10)


class Stack(Element):

    def __init__(self, elements: list[Element], axis: int, alignment: Alignment, padding: int):
        self.__elements = elements
        self.axis = axis
        self.alignment = alignment
        self.padding = padding
        super().__init__(elements, self.__calculate_total_rect())
        self.set_top_left((0, 0))

    @property
    def elements(self):
        return self.__elements

    @elements.setter
    def elements(self, elements):
        self.__elements = elements
        old_position = self.rectangle.topleft
        self._rectangle = self.__calculate_total_rect()
        self.set_top_left(top_left=old_position)

    def hide(self):
        for element in self.elements:
            element.hide()
    def show(self):
        for element in self.elements:
            element.show()

    def clear(self):
        for element in self.elements:
            element.kill()
        self.elements = []

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
            elif hasattr(element, "respond_to_event"):
                getattr(element, "respond_to_event")(fn_name, event)

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

    def add_element(self, element: Element):
        self.elements.append(element)
        old_position = self.rectangle.topleft
        self._rectangle = self.__calculate_total_rect()
        self.set_top_left(top_left=old_position)

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
            total_height = max(heights, default=0)
            total_width = sum(widths)
            total_width += self.padding * (len(self.elements) - 1)
        else:
            # axis == 1
            total_height = sum(heights)
            total_height += self.padding * (len(self.elements) - 1)
            total_width = max(widths, default=0)
        return pygame.Rect((0, 0), (total_width, total_height))


class HorizontalStack(Stack):
    def __init__(self, elements: list[Element], alignment: Alignment = Alignment.CENTER, padding: int = 0):
        super().__init__(elements, axis=0, alignment=alignment, padding=padding)


class VerticalStack(Stack):
    def __init__(self, elements: list[Element], alignment: Alignment = Alignment.LEFT, padding: int = 0):
        self.alignment = alignment
        super().__init__(elements, axis=1, alignment=alignment, padding=padding)


class ServerSelector(HorizontalStack):
    SELECTOR_WIDTH = 150

    def __init__(self, ip_address: str, ui_manager: pygame_gui.UIManager, on_switch: Callable[[str], None]):
        ip_label = TextElement(text=ip_address, size=22)

        button = ManagedButton(
            button=pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((0, 0), (self.SELECTOR_WIDTH-ip_label.rectangle.width, ip_label.rectangle.height + 4)),
                text="EDIT",
                manager=ui_manager,
                visible=True
            ),
            on_click=self.on_click
        )

        self.permanent_elements = [ip_label, button]
        entry_element = TextInputElement(
            input=pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((0, 0), (self.SELECTOR_WIDTH, ip_label.rectangle.height + 4)),
                manager=ui_manager,
                placeholder_text=self.permanent_elements[0].text,
                visible=False
            ),
            on_text_finished=self.on_text_finished
        )


        self.entry_elements = [entry_element]
        self.on_switch = on_switch
        super().__init__(elements=self.permanent_elements)

    def on_click(self):
        self.hide()
        self.elements = self.entry_elements
        self.show()

    def on_text_finished(self, new_ip_address):
        self.on_switch(new_ip_address)
        cast(TextElement, self.permanent_elements[0]).text = new_ip_address
        self.__switch_to_permanent()

    @property
    def ip_address(self) -> str:
        return cast(TextElement, self.permanent_elements[0]).text

    def respond_to_event(self, fn_name, event):
        super().respond_to_event(fn_name, event)
        entry_line = cast(pygame_gui.elements.UITextEntryLine, self.entry_elements[0].wrapped)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not entry_line.is_focused:
                self.__switch_to_permanent()

    def disable(self):
        cast(ManagedButton, self.permanent_elements[1]).kill()

    def __switch_to_permanent(self):
        cast(pygame_gui.elements.UITextEntryLine, self.entry_elements[0].wrapped).clear()
        self.hide()
        self.elements = self.permanent_elements
        cast(ManagedButton, self.elements[1]).unselect()  # unselect button next time
        self.show()