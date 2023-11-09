from typing import Callable, Self, Protocol, runtime_checkable

import pygame_gui
import pygame
from pygame import Surface, SurfaceType, Color

from clueless.client.ui_elements import Element, TextInputElement, TextElement, ManagedButton


class View(Protocol):

    def __init__(self, screen: Surface | SurfaceType, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.elements: list[Element] = []

    def draw(self):
        self.ui_manager.draw_ui(self.screen)
        for element in [e for e in self.elements if not e.is_ui_manager_managed]:
            self.screen.blit(element.wrapped, element.rectangle)

    def add_element(self, element: Element):
        self.elements.append(element)

    def respond_to_event(self, event):
        # def respond_to_MOUSEBUTTONDOWN(self, event: pygame.event)
        fn_name = f"respond_to_{self.__event_name(event)}"
        print(f"{fn_name}")
        for element in self.elements:
            if hasattr(element, fn_name):
                print(f"Calling {fn_name} on element {element}")
                getattr(element, fn_name)(event)


    def __event_name(self, event):
        name = pygame.event.event_name(event.type)
        if name == pygame.event.event_name(pygame.USEREVENT):
            map = {
                pygame_gui.UI_TEXT_ENTRY_FINISHED: "UITextEntryFinished",
                pygame_gui.UI_BUTTON_PRESSED: "UIButtonPressed"
            }
            return map[event.type] if event.type in map else name
        else:
            return name



class TitleView(View):
    HIGHLIGHT_COLOR = Color(200, 0, 0)
    DEFAULT_COLOR = Color(255, 0, 0)

    class Delegate(Protocol):
        def did_set_nickname(self, nickname: str):
            pass

        def did_ready(self):
            pass

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate):
        super().__init__(screen, ui_manager)
        self.delegate = delegate

        pos = pygame.Rect((0, 0), (200, 30))
        pos.center = (screen.get_rect().width // 2, screen.get_rect().height // 2)
        self.ready_button = pygame_gui.elements.UIButton(relative_rect=pos,
                                                         text='READY',
                                                         manager=ui_manager,
                                                         visible=False)
        self.text_input = pygame_gui.elements.UITextEntryLine(relative_rect=pos, manager=ui_manager,
                                                              placeholder_text="Enter nickname")

        self.title_text = TextElement(text="CLUELESS v 0.1.0", primary_color=Color(0, 0, 255))
        self.title_text.rectangle.center = (screen.get_rect().width // 2, (screen.get_rect().height // 2) - 50)
        self.add_element(self.title_text)
        self.add_element(ManagedButton(self.ready_button, on_click=delegate.did_ready))
        self.add_element(TextInputElement(self.text_input, on_text_finished=delegate.did_set_nickname))
        # self.subtitle_text = TextElement(text="READY",
        #                                  size=24,
        #                                  primary_color=Color(255, 0, 0),
        #                                  highlight_color=Color(255, 153, 153),
        #                                  on_mouse_down=delegate.did_ready)
        # self.subtitle_text.rectangle.center = (
        #     screen.get_rect().width // 2, self.title_text.rectangle.bottom + (self.subtitle_text.rectangle.height // 2)
        # )
        # self.add_element(self.subtitle_text)
        # player_list = TextElement(text="Currently in the lobby: a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z", size=20, primary_color=Color(0, 0, 255))
        # player_list.rectangle.bottom = screen.get_rect().bottom
        # self.elements.append(player_list)

    def transition_to_ready_button(self):
        self.text_input.hide()
        self.ready_button.show()

