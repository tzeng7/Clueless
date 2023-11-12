from typing import Protocol

import pygame_gui
import pygame
from pygame import Surface, SurfaceType, Color

import clueless.client.ui_enums
from clueless.client.ui_enums import Pico
from clueless.client.ui_elements import Element, TextInputElement, TextElement, ManagedButton, \
    ImageElement, HorizontalStack, VerticalStack
from clueless.model.board_enums import Character
from clueless.model.player import PlayerID


class View(Protocol):

    def __init__(self, screen: Surface | SurfaceType, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.elements: list[Element] = []

    def draw(self):
        self.ui_manager.draw_ui(self.screen)
        for element in self.elements:
            element.draw_onto(self.screen)

    def add_element(self, element: Element):
        self.elements.append(element)

    def respond_to_event(self, event):
        fn_name = f"respond_to_{self.__event_name(event)}"
        print(f"Received {self.__event_name(event)}")
        for element in self.elements:
            if hasattr(element, fn_name):
                print(f"Calling {fn_name} on element {element}")
                getattr(element, fn_name)(event)
            elif hasattr(element, "respond_to_event"):
                # print(f"Calling {fn_name} on element {element}")
                getattr(element, "respond_to_event")(fn_name, event)

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
        self.ready_button = ManagedButton(
            pygame_gui.elements.UIButton(relative_rect=pos,
                                         text='READY',
                                         manager=ui_manager,
                                         visible=False),
            on_click=delegate.did_ready
        )
        self.ready_button.set_center((screen.get_rect().width // 2, screen.get_rect().height // 2))

        self.text_input = TextInputElement(
            pygame_gui.elements.UITextEntryLine(relative_rect=pos,
                                                manager=ui_manager,
                                                placeholder_text="Enter nickname"),
            on_text_finished=delegate.did_set_nickname
        )
        self.text_input.set_center((screen.get_rect().width // 2, screen.get_rect().height // 2))

        self.title_text = TextElement(text="CLUELESS v 0.1.0", primary_color=Color(0, 0, 255))
        self.title_text.set_center((screen.get_rect().width // 2, (screen.get_rect().height // 2) - 50))
        self.add_element(self.title_text)
        self.add_element(self.ready_button)
        self.add_element(self.text_input)
        # self.subtitle_text = TextElement(text="READY",
        #                                  size=24,
        #                                  primary_color=Color(255, 0, 0),
        #                                  highlight_color=Color(255, 153, 153),
        #                                  on_mouse_down=delegate.did_ready)
        # self.subtitle_text.set_center(
        #     (screen.get_rect().width // 2, self.title_text.rectangle.bottom + (self.subtitle_text.rectangle.height // 2))
        # )
        # self.add_element(self.subtitle_text)

    def transition_to_ready_button(self):
        self.text_input.hide()
        self.ready_button.show()

    def add_player_id(self, player_id: PlayerID):

        # self.add_element(ManagedElement(
        #     pygame_gui.elements.UITextBox(f"LOBBY LIST:\nScarlet\nViolet\n{player_id.nickname}({player_id.character}", relative_rect=pygame.Rect(30, 20, 500, 100), manager=self.ui_manager)
        #   ))
        # player_id = TextElement(text=f"{player_id.nickname}({player_id.character})",
        #                         size=24,
        #                         primary_color=Pico.from_character(player_id.character))
        # player_id.rectangle.topleft = (1000 - player_id.rectangle.width, 1000 - player_id.rectangle.height)
        # self.add_element(player_id)
        player_avatar = ImageElement(name="scarlet")
        player_id = TextElement(text=f"{player_id.nickname}({player_id.character})",
                                size=16,
                                primary_color=Pico.from_character(player_id.character))
        player = HorizontalStack([player_avatar, player_id], padding=0)

        mustard_avatar = ImageElement(name="mustard")
        mustard_id = TextElement(text=f"Colonel Mustard",
                                 size=16,
                                 primary_color=Pico.from_character(Character.MUSTARD))
        player_2 = HorizontalStack([mustard_avatar, mustard_id], padding=0)

        stack = VerticalStack([player, player_2], alignment=clueless.client.ui_enums.Alignment.LEFT, padding=10)
        stack.set_top_left((1000 - stack.rectangle.width, 1000 - stack.rectangle.height))
        self.add_element(stack)

class GameView(View):
    class Delegate(Protocol):
        hi = "hi"

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate):
        super().__init__(screen, ui_manager)
        self.delegate = delegate

        self.game_started = TextElement(text="GAME STARTED!", primary_color=Color(0, 0, 255))
        self.game_started.set_center((screen.get_rect().width // 2, (screen.get_rect().height // 2) - 50))
        self.add_element(self.game_started)