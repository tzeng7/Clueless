from enum import Enum
from typing import Protocol, Type

import pygame
import pygame_gui
from pygame import Surface, Color

import clueless.client.ui_enums
from clueless.client.client_game_manager import ClientGameManager
from clueless.client.ui_elements import Element, Rectangle, TextInputElement, TextElement, ManagedButton, \
    ImageElement, HorizontalStack, VerticalStack, \
    PayloadButton
from clueless.client.ui_enums import Pico
from clueless.messages.messages import Suggest
from clueless.model.board import Board
from clueless.model.board_enums import Character, ActionType, Direction, Weapon, Location, CardType
from clueless.model.card import Card
from clueless.model.player import PlayerID


class View(Protocol):
    """
    View manages drawing pygame and pygame_gui elements onto a screen. It also dispatches pygame events to its elements.
    """
    SCREEN_SIZE = (1000, 1000)

    def __init__(self, screen: Surface, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.ui_manager.clear_and_reset()
        # elements is a private property. adding and deleting elements require dedicated methods so that we can
        # kill pygame_gui elements when we want to remove them from the screen.
        self.__elements: list[Element] = []

    def draw(self):
        self.ui_manager.draw_ui(self.screen)
        for element in self.__elements:
            element.draw_onto(self.screen)

    def add_element(self, element: Element):
        self.__elements.append(element)

    def del_element(self, element: Element):
        element.kill()
        self.__elements.remove(element)

    def respond_to_event(self, event):
        """
        An element declares it can respond to event if it has the function named "respond_to_{event_name}"
        where event name is the pygame event name. An element can also declare it wants to handle all events if
        it has a respond_to_event method.

        :param event:
        :return:
        """
        fn_name = f"respond_to_{self.__event_name(event)}"
        for element in self.__elements:
            if hasattr(element, fn_name):
                print(f"Calling {fn_name} on element {element}")
                getattr(element, fn_name)(event)
            elif hasattr(element, "respond_to_event"):
                getattr(element, "respond_to_event")(fn_name, event)

    def __event_name(self, event):
        name = pygame.event.event_name(event.type)
        if name == pygame.event.event_name(pygame.USEREVENT):
            # all pygame_gui events are pygame user events, so we map pygame_gui event type to a string
            map = {
                pygame_gui.UI_TEXT_ENTRY_FINISHED: "UITextEntryFinished",
                pygame_gui.UI_BUTTON_PRESSED: "UIButtonPressed"
            }
            return map[event.type] if event.type in map else name
        else:
            return name


class TitleView(View):
    DEFAULT_BUTTON_SIZE = (200, 30)
    DEFAULT_LOBBY_IMAGE_SIZE = (65, 65)

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
        self.interactive_element = text_input

        title_text = TextElement(text="CLUELESS", primary_color=Color(0, 0, 255))
        title_text.set_center((screen.get_rect().width // 2, (screen.get_rect().height // 2) - 50))
        self.add_element(title_text)
        self.add_element(text_input)

        self.lobby_stack = VerticalStack([], alignment=clueless.client.ui_enums.Alignment.LEFT, padding=10)
        self.lobby_stack.set_bottom_right(View.SCREEN_SIZE)
        self.add_element(self.lobby_stack)

    def transition_to_ready_button(self):
        self.del_element(self.interactive_element)

        ready_button = ManagedButton(
            pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0), self.DEFAULT_BUTTON_SIZE),
                                         text='READY',
                                         manager=self.ui_manager,
                                         visible=True),
            on_click=self.delegate.did_ready
        )
        ready_button.set_center((self.screen.get_rect().width // 2, self.screen.get_rect().height // 2))
        self.add_element(ready_button)
        self.interactive_element = ready_button

    def add_player_id(self, players: [PlayerID]):
        player_list = []
        for player in players:
            player_avatar = ImageElement(name=player.character.file_name, size=self.DEFAULT_LOBBY_IMAGE_SIZE)
            player_id = TextElement(text=f"{player.nickname} ({player.character.value})",
                                    size=16,
                                    primary_color=Pico.from_character(player.character))
            player_row = HorizontalStack([player_avatar, player_id], padding=0)
            player_list.append(player_row)
        self.lobby_stack.elements = player_list  # replace with new list
        self.lobby_stack.set_bottom_right(self.SCREEN_SIZE)


class GameView(View):
    HORIZONTAL_PADDING = 15
    VERTICAL_PADDING = 5
    ACTION_BOX_SIZE = (400, 1000)
    BOX_PADDING = 10
    MENU_PADDING = 50
    MENU_BUTTON_HEIGHT = 24
    MAX_LEVELS = 4
    BOARD_SIZE = (600, 600)
    BOARD_TOP_LEFT = (200, 0)
    # This is the distance from the top left corner to the center of the cell on the board in either direction
    # So for example, (120, 120) is the center of the first cell, if screen size is 1000.
    BOARD_GRID_OFFSETS = [0.12, 0.31, 0.5, 0.69, 0.88] * View.SCREEN_SIZE[0]

    DIALOG_TEXT_WAITING = "Waiting for turn..."

    class Delegate(Protocol):
        def did_move(self, direction: (Direction, (int, int))):
            pass

        def did_suggest(self, character: Character, weapon: Weapon):
            pass

        def did_disprove(self, card: Card | None, suggest: Suggest):
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

    def __setup_elements(self):
        menu_width = self.screen.get_width() - (self.MENU_PADDING * 2)
        button_width = (menu_width - (self.HORIZONTAL_PADDING * (self.MAX_LEVELS - 1))) // self.MAX_LEVELS
        button_height = self.MENU_BUTTON_HEIGHT
        self.button_dimensions = pygame.Rect((0, 0), (button_width, button_height))

        # Setup ActionBox (bottom half of the screen)
        box_y = self.screen.get_height() - self.ACTION_BOX_SIZE[0]
        action_box_bounds = pygame.Rect(
            self.BOX_PADDING,
            box_y + self.BOX_PADDING,
            self.screen.get_width() - (self.BOX_PADDING * 2),
            self.ACTION_BOX_SIZE[0] - (self.BOX_PADDING * 2)
        )
        action_box = Rectangle(action_box_bounds, self.screen)
        self.menu_dialog = TextElement(self.DIALOG_TEXT_WAITING)
        self.menu_dialog.set_center(
            (self.screen.get_width() // 2, box_y + (self.menu_dialog.rectangle.height // 2) + self.MENU_PADDING)
        )
        self.menu = HorizontalStack([],
                                    alignment=clueless.client.ui_enums.Alignment.TOP,
                                    padding=self.HORIZONTAL_PADDING)
        self.menu.set_top_left((self.MENU_PADDING, self.menu_dialog.rectangle.bottom + self.VERTICAL_PADDING))

        # Setup Board (top half of the screen)
        board = ImageElement("GameBoardV1", self.BOARD_SIZE)
        board.set_top_left(self.BOARD_TOP_LEFT)
        self.board_elements: dict[PlayerID, ImageElement] = {}
        self.add_element(board)
        self.add_element(self.menu_dialog)
        self.add_element(self.menu)
        self.add_element(action_box)

    ########################
    ### ACTION SELECTION ###
    ########################

    def show_actions(self):
        dialog, button_stack = self.__generate_next_menu_level()
        next_button_stack = VerticalStack(elements=button_stack, padding=self.VERTICAL_PADDING)
        self.levels.append(button_stack)
        self.menu.add_element(next_button_stack)
        self.menu_dialog.text = dialog

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
            # no more buttons to show, means we need to call the matching delegate method
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
            self.current_selection.clear()
            self.menu.clear()

    def __make_direction_buttons(self, directions: list[(Direction, (int, int))]) -> list[PayloadButton]:
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

    def __make_card_entry_buttons(self, card_type: Type[Enum]):
        button_list = []
        for case in card_type:
            button_list.append(
                PayloadButton(payload=case,
                              button=pygame_gui.elements.UIButton(relative_rect=self.button_dimensions,
                                                                  text=case.value,
                                                                  manager=self.ui_manager,
                                                                  visible=True),
                              on_click=self.__menu_clicked)
            )
        return button_list

    #####################
    ### BOARD UPDATES ###
    #####################

    def update_board_elements(self, board_model: Board):
        # TODO: handle overlap
        for player_id, player_token in board_model.player_tokens.items():
            image_element: ImageElement
            if player_id in self.board_elements:
                image_element = self.board_elements[player_id]
            else:
                image_element = ImageElement(player_id.character.file_name, (50, 50))
                self.add_element(image_element)
                self.board_elements[player_id] = image_element
            new_board_position = player_token.position
            # X and Y, if (0, 0) were the top left of the board
            player_image_x = self.BOARD_GRID_OFFSETS[new_board_position[1]] * self.BOARD_SIZE[0]
            player_image_y = self.BOARD_GRID_OFFSETS[new_board_position[0]] * self.BOARD_SIZE[1]
            image_element.set_center((self.BOARD_TOP_LEFT[0] + player_image_x, self.BOARD_TOP_LEFT[1] + player_image_y))

    ################
    ### DISPROVE ###
    ################

    def show_disprove(self, disproving_cards: [Card], suggest: Suggest):
        self.menu_dialog.text = "Please select a card to disprove: "

        if not disproving_cards:
            none_button = PayloadButton.card_button(card=None, button=pygame_gui.elements.UIButton(
                relative_rect=self.button_dimensions,
                text="None",
                manager=self.ui_manager,
                visible=True),
                                                    on_click=lambda x: self.delegate.did_disprove(x, suggest))
            one_button_stack = VerticalStack([none_button], clueless.client.ui_enums.Alignment.TOP,
                                             padding=self.VERTICAL_PADDING)

            self.menu.add_element(one_button_stack)
            return
        else:
            character_cards = [card for card in disproving_cards if card.card_type == CardType.CHARACTER]
            weapon_cards = [card for card in disproving_cards if card.card_type == CardType.WEAPON]
            location_cards = [card for card in disproving_cards if card.card_type == CardType.LOCATION]

            def create_button(card: Card) -> PayloadButton:
                return PayloadButton.card_button(card=card,
                                                 button=pygame_gui.elements.UIButton(
                                                     relative_rect=self.button_dimensions,
                                                     text=card.card_value,
                                                     manager=self.ui_manager,
                                                     visible=True),
                                                 on_click=lambda x: self.__disprove_card_clicked(x, suggest))

            v_stack_character = VerticalStack(list(map(create_button, character_cards)),
                                              padding=self.VERTICAL_PADDING)
            v_stack_weapon = VerticalStack(list(map(create_button, weapon_cards)),
                                           padding=self.VERTICAL_PADDING)
            v_stack_location = VerticalStack(list(map(create_button, location_cards)),
                                             padding=self.VERTICAL_PADDING)
            self.menu.add_element(v_stack_character)
            self.menu.add_element(v_stack_weapon)
            self.menu.add_element(v_stack_location)

    def __disprove_card_clicked(self, payload: Card | None, suggest: Suggest):
        self.menu_dialog.text = self.DIALOG_TEXT_WAITING
        self.menu.clear()
        self.delegate.did_disprove(payload, suggest)
