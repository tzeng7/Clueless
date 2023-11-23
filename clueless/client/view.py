from enum import Enum
from typing import Protocol, Type

import pygame_gui
import pygame
from pygame import Surface, SurfaceType, Color

import clueless.client.ui_enums
from clueless.client.client_game_manager import ClientGameManager
from clueless.client.ui_enums import Pico
from clueless.client.ui_elements import Element, TextInputElement, TextElement, ManagedButton, \
    ImageElement, HorizontalStack, VerticalStack, ViewBox, \
    Stack, ManagedElement, PayloadButton
from clueless.messages.messages import BaseClientAction, Move, Suggest
from clueless.model.board_enums import Character, ActionType, Direction, Weapon, Location, CardType
from clueless.model.card import Card
from clueless.model.player import PlayerID


class View(Protocol):

    def __init__(self, screen: Surface, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.ui_manager.clear_and_reset()
        self.elements: list[Element] = []

    def draw(self):
        self.ui_manager.draw_ui(self.screen)
        for element in self.elements:
            element.draw_onto(self.screen)

    def add_element(self, element: Element):
        self.elements.append(element)

    def del_element(self, element: Element):
        element.kill()
        self.elements.remove(element)

    def respond_to_event(self, event):
        fn_name = f"respond_to_{self.__event_name(event)}"
        # print(f"Received {self.__event_name(event)}")
        for element in self.elements:
            if hasattr(element, fn_name):
                # print(f"Calling {fn_name} on element {element}")
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
    DEFAULT_BUTTON_SIZE = (200, 30)
    DEFAULT_IMAGE_SIZE = (50, 50)

    class Delegate(Protocol):
        def did_set_nickname(self, nickname: str):
            pass

        def did_ready(self):
            pass

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate):
        super().__init__(screen, ui_manager)
        self.delegate = delegate

        text_input = TextInputElement(
            pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 0), self.DEFAULT_BUTTON_SIZE),
                                                manager=ui_manager,
                                                placeholder_text="Enter nickname"),
            on_text_finished=delegate.did_set_nickname
        )
        text_input.set_center((screen.get_rect().width // 2, screen.get_rect().height // 2))

        title_text = TextElement(text="CLUELESS v 0.1.0", primary_color=Color(0, 0, 255))
        title_text.set_center((screen.get_rect().width // 2, (screen.get_rect().height // 2) - 50))
        self.add_element(title_text)
        self.add_element(text_input)
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
        for element in self.elements:
            if isinstance(element, TextInputElement):
                self.del_element(element)

        ready_button = ManagedButton(
            pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0), self.DEFAULT_BUTTON_SIZE),
                                         text='READY',
                                         manager=self.ui_manager,
                                         visible=True),
            on_click=self.delegate.did_ready
        )
        ready_button.set_center((self.screen.get_rect().width // 2, self.screen.get_rect().height // 2))
        self.add_element(ready_button)

    def add_player_id(self, players: [PlayerID]):

        player_list = []
        for player in players:
            player_avatar = ImageElement(name=f"amongus_{player.character}", size=self.DEFAULT_IMAGE_SIZE)
            player_id = TextElement(text=f"{player.nickname}({player.character})",
                                    size=16,
                                    primary_color=Pico.from_character(player.character))
            player_stack = HorizontalStack([player_avatar, player_id], padding=0)
            player_list.append(player_stack)

        stack = VerticalStack(player_list, alignment=clueless.client.ui_enums.Alignment.LEFT, padding=10)
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


class ActionView(View):
    HORIZONTAL_PADDING = 15
    VERTICAL_PADDING = 5
    ACTION_BOX_SIZE = (400, 1000)
    BOX_PADDING = 10
    MENU_PADDING = 50
    MAX_LEVELS = 4

    BOARD_SIZE = (150, 150 )

    class Delegate(Protocol):
        def did_move(self, direction: (Direction, (int, int))):
            pass

        def did_suggest(self, character: Character, weapon: Weapon):
            pass

        def did_disprove(self, card: Card):
            pass

        def did_accuse(self, character: Character, weapon: Weapon, location: Location):
            pass

        def did_end_turn(self):
            pass

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate,
                 game_manager: ClientGameManager):
        super().__init__(screen, ui_manager)
        self.delegate = delegate
        self.game_manager = game_manager
        self.current_selection = []
        self.levels: list[list[PayloadButton]] = []
        self.__setup_elements()
        self.__show_board()

    def __setup_elements(self):
        button_width = (self.screen.get_width()
                        - (self.HORIZONTAL_PADDING * (self.MAX_LEVELS - 1))
                        - (self.MENU_PADDING * 2)) // self.MAX_LEVELS
        button_height = 24  # TODO: fixed
        self.button_dimensions = pygame.Rect((0, 0), (button_width, button_height))
        dialog, button_stack = self.__generate_next_menu_level()
        first_level_button_stack = VerticalStack(elements=button_stack, padding=self.VERTICAL_PADDING)
        self.levels.append(button_stack)

        box_y = self.screen.get_height() - self.ACTION_BOX_SIZE[0]

        rectangle = pygame.Rect(
            self.BOX_PADDING,
            box_y + self.BOX_PADDING,
            self.screen.get_width() - (self.BOX_PADDING * 2),
            self.ACTION_BOX_SIZE[0] - (self.BOX_PADDING * 2)
        )
        action_box = ViewBox(rectangle, self.screen)
        self.menu_dialog = TextElement(dialog)
        self.menu_dialog.set_center(
            (self.screen.get_width() // 2, box_y + (self.menu_dialog.rectangle.height // 2) + self.MENU_PADDING))
        self.menu = HorizontalStack([first_level_button_stack], alignment=clueless.client.ui_enums.Alignment.TOP,
                                    padding=self.HORIZONTAL_PADDING)
        self.menu.set_top_left((self.MENU_PADDING, self.menu_dialog.rectangle.bottom + self.VERTICAL_PADDING))
        self.add_element(self.menu_dialog)
        self.add_element(self.menu)
        self.add_element(action_box)

    def __generate_next_menu_level(self) -> (str, list[PayloadButton]):
        button_list = []
        if len(self.current_selection) == 0:
            for action in self.game_manager.available_actions():
                button_list.append(PayloadButton.action_button(
                    action_type=action,
                    button=pygame_gui.elements.UIButton(relative_rect=self.button_dimensions,
                                                        text=action.name,
                                                        manager=self.ui_manager,
                                                        visible=True),
                    on_click=self.__menu_clicked
                ))
            return "Please select an action: ", button_list
        else:
            match (self.current_selection[0], len(self.current_selection)):
                case ActionType.MOVE, 1:
                    return "Please select a possible direction: ", self.__make_direction_buttons(
                        self.game_manager.available_movement_options())
                case ActionType.SUGGEST, 1:
                    return "Please select a character to suggest: ", self.__make_card_entry_buttons(Character)
                case ActionType.SUGGEST, 2:
                    return "Please select a weapon to suggest: ", self.__make_card_entry_buttons(Weapon)
                case ActionType.ACCUSE, 1:
                    return "Please select a character to accuse: ", self.__make_card_entry_buttons(Character)
                case ActionType.ACCUSE, 2:
                    return (f"Please select the weapon that {self.current_selection[1].value} used: ",
                            self.__make_card_entry_buttons(Weapon))
                case ActionType.ACCUSE, 3:
                    return (f"Please select the room where {self.current_selection[1].value} "
                            f"used the {self.current_selection[2].value}: "), self.__make_card_entry_buttons(
                        Location)
                case _:
                    return "", []

    def __menu_clicked(self, payload):
        self.current_selection.append(payload)
        # highlight selection and disable rest
        for button in self.levels[-1]:
            if button.payload == payload:
                button.select()
            else:
                button.disable()

        dialog, button_stack = self.__generate_next_menu_level()
        self.levels.append(button_stack)

        if len(button_stack) > 0:
            # push next level
            self.menu.add_element(VerticalStack(elements=button_stack, padding=self.VERTICAL_PADDING))
            self.menu_dialog.text = dialog
        else:
            match self.current_selection[0]:
                case ActionType.MOVE:
                    self.delegate.did_move(self.current_selection[1])
                case ActionType.SUGGEST:
                    self.delegate.did_suggest(self.current_selection[1], self.current_selection[2])
                case ActionType.ACCUSE:
                    self.delegate.did_accuse(self.current_selection[1], self.current_selection[2],
                                             self.current_selection[3])
                case ActionType.END_TURN:
                    self.delegate.did_end_turn()

    def __make_direction_buttons(self, directions: list[(Direction, (int, int))]) -> list[PayloadButton]:
        # for element in self.elements:
        #     if isinstance(element, Stack):
        #         self.del_element(element)

        button_list = []
        for direction in directions:
            button_list.append(PayloadButton.direction_button(
                movement_option=direction,
                button=pygame_gui.elements.UIButton(relative_rect=self.button_dimensions,
                                                    text=direction[0].name,
                                                    manager=self.ui_manager,
                                                    visible=True),
                on_click=self.__menu_clicked
            ))
        return button_list

    def __make_card_entry_buttons(self, type: Type[Enum]):
        button_list = []
        for case in type:
            button_list.append(
                PayloadButton(payload=case,
                              button=pygame_gui.elements.UIButton(relative_rect=self.button_dimensions,
                                                                  text=case.value,
                                                                  manager=self.ui_manager,
                                                                  visible=True),
                              on_click=self.__menu_clicked)
            )
        return button_list

    def __show_board(self):
        count = 0
        rooms = []
        board = []
        for location in Location:
            room = ImageElement(name=f"{location.value}", size= self.BOARD_SIZE)
            rooms.append(room)
            count = count + 1
            if count == 3:
                count = 0
                board.append(
                    HorizontalStack(elements=rooms.copy(), alignment=clueless.client.ui_enums.Alignment.CENTER, padding=100))
                rooms.clear()
        v_stack = VerticalStack(elements=board, alignment=clueless.client.ui_enums.Alignment.CENTER, padding=50)
        v_stack.set_top_left((0,0))
        v_stack.set_center((500, 300))
        self.add_element(v_stack)


class DisproveView(View):
    HORIZONTAL_PADDING = 15
    VERTICAL_PADDING = 5
    ACTION_BOX_SIZE = (400, 1000)
    BOX_PADDING = 10
    MENU_PADDING = 50
    MAX_LEVELS = 4

    class Delegate(Protocol):
        def did_disprove(self, card: Card, suggest: Suggest):
            pass

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate,
                 disproving_cards: [Card], suggest: Suggest):

        super().__init__(screen, ui_manager)
        self.delegate = delegate
        self.suggest = suggest

        button_width = (self.screen.get_width()
                        - (self.HORIZONTAL_PADDING * (self.MAX_LEVELS - 1))
                        - (self.MENU_PADDING * 2)) // self.MAX_LEVELS
        button_height = 24  # TODO: fixed
        self.button_dimensions = pygame.Rect((0, 0), (button_width, button_height))

        box_y = self.screen.get_height() - self.ACTION_BOX_SIZE[0]

        rectangle = pygame.Rect(
            self.BOX_PADDING,
            box_y + self.BOX_PADDING,
            self.screen.get_width() - (self.BOX_PADDING * 2),
            self.ACTION_BOX_SIZE[0] - (self.BOX_PADDING * 2)
        )
        action_box = ViewBox(rectangle, self.screen)

        menu_dialog = TextElement("Please select a card to disprove: ")

        button_list_character = []
        button_list_weapon = []
        button_list_location = []
        for card in disproving_cards:
            if card.card_type == CardType.CHARACTER:
                button_list_character.append(PayloadButton.card_button(card=card,
                                                                       button=pygame_gui.elements.UIButton(
                                                                           relative_rect=self.button_dimensions,
                                                                           text=card.card_value,
                                                                           manager=self.ui_manager,
                                                                           visible=True),
                                                                       on_click=lambda x: self.delegate.did_disprove(x,
                                                                                                                     suggest)))
            elif card.card_type == CardType.WEAPON:
                button_list_weapon.append(PayloadButton.card_button(card=card,
                                                                    button=pygame_gui.elements.UIButton(
                                                                        relative_rect=self.button_dimensions,
                                                                        text=card.card_value,
                                                                        manager=self.ui_manager,
                                                                        visible=True),
                                                                    on_click=lambda x: self.delegate.did_disprove(x,
                                                                                                                  suggest)))
            elif card.card_type == CardType.LOCATION:
                button_list_location.append(PayloadButton.card_button(card=card,
                                                                      button=pygame_gui.elements.UIButton(
                                                                          relative_rect=self.button_dimensions,
                                                                          text=card.card_value,
                                                                          manager=self.ui_manager,
                                                                          visible=True),
                                                                      on_click=lambda x: self.delegate.did_disprove(x,
                                                                                                                    suggest)))
        v_stack_character = VerticalStack(button_list_character, clueless.client.ui_enums.Alignment.TOP,
                                          padding=self.VERTICAL_PADDING)
        v_stack_weapon = VerticalStack(button_list_weapon, clueless.client.ui_enums.Alignment.TOP,
                                       padding=self.VERTICAL_PADDING)
        v_stack_location = VerticalStack(button_list_location, clueless.client.ui_enums.Alignment.TOP,
                                         padding=self.VERTICAL_PADDING)

        h_stack = HorizontalStack([v_stack_character, v_stack_weapon, v_stack_location],
                                  alignment=clueless.client.ui_enums.Alignment.TOP,
                                  padding=self.VERTICAL_PADDING)
        h_stack.set_top_left((self.MENU_PADDING, menu_dialog.rectangle.bottom + self.VERTICAL_PADDING))
        h_stack.set_center((self.screen.get_width() // 2, box_y + (h_stack.rectangle.height // 2) + 100))
        menu_dialog.set_center((self.screen.get_width() // 2, box_y + (menu_dialog.rectangle.height // 2)))
        self.add_element(h_stack)
        self.add_element(action_box)
        self.add_element(menu_dialog)
