from typing import Protocol

import pygame_gui
import pygame
from pygame import Surface, SurfaceType, Color

import clueless.client.ui_enums
from clueless.client.client_game_manager import ClientGameManager
from clueless.client.ui_enums import Pico
from clueless.client.ui_elements import Element, TextInputElement, TextElement, ManagedButton, \
    ImageElement, HorizontalStack, VerticalStack, ActionButton, DirectionButton, ViewBox, \
    CharacterButton, WeaponButton, Stack, ManagedElement, LocationButton, CardButton
from clueless.messages.messages import BaseClientAction, Move, Suggest
from clueless.model.board_enums import Character, ActionType, Direction, Weapon, Location
from clueless.model.card import Card
from clueless.model.player import PlayerID


class View(Protocol):

    def __init__(self, screen: Surface | SurfaceType, ui_manager: pygame_gui.UIManager):
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

    def add_player_id(self, player_id: PlayerID):
        player_avatar = ImageElement(name="amongus_scarlet")
        player_id = TextElement(text=f"{player_id.nickname}({player_id.character})",
                                size=16,
                                primary_color=Pico.from_character(player_id.character))
        player = HorizontalStack([player_avatar, player_id], padding=0)

        # mustard_avatar = ImageElement(name="amongus_mustard")
        # mustard_id = TextElement(text=f"Colonel Mustard",
        #                          size=16,
        #                          primary_color=Pico.from_character(Character.MUSTARD))
        # player_2 = HorizontalStack([mustard_avatar, mustard_id], padding=0)

        stack = VerticalStack([player], alignment=clueless.client.ui_enums.Alignment.LEFT, padding=10)
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


# class BoardView(View):
#     class Delegate(Protocol):
class ActionView(View):
    class Delegate(Protocol):
        def did_select(self, action_type: ActionType):
            pass

        def did_select_direction(self, direction: Direction):
            pass

        def did_suggest(self, character: Character, weapon: Weapon):
            pass

        def did_disprove(self, card: Card):
            pass

        def did_accuse(self, character: Character, weapon: Weapon, location: Location):
            pass

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate,
                 available_actions: [ActionType]):
        super().__init__(screen, ui_manager)

        self.choose_action_text = TextElement("Please select an action: ")
        self.choose_action_text.set_center((500, 775))
        self.add_element(self.choose_action_text)

        rectangle = pygame.Rect(.5, 750, 1000, 249)
        action_box = ViewBox(rectangle, screen)
        self.add_element(action_box)
        self.delegate = delegate

        pos = pygame.Rect((0, 0), (200, 30))
        button_list = []
        for action in available_actions:
            button_list.append(ActionButton(action_type=action,
                                            button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                text=action.name,
                                                                                manager=ui_manager,
                                                                                visible=True),
                                            on_click=delegate.did_select))

        stack = VerticalStack(button_list, padding=25)
        stack.set_top_left((stack.rectangle.width - 100, 900 - stack.rectangle.height))
        self.add_element(stack)

    def transition_to_direction(self, directions: list[(Direction, (int, int))]):
        for element in self.elements:
            if isinstance(element, Stack):
                self.del_element(element)

        button_list = []
        choose_direction = TextElement("Please select a possible direction: ")
        choose_direction.set_center((500, 775))
        self.add_element(choose_direction)

        pos = pygame.Rect((0, 0), (200, 30))
        for direction in directions:
            button_list.append(DirectionButton(movement_option=direction,
                                               button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                   text=direction[0].name,
                                                                                   manager=self.ui_manager,
                                                                                   visible=True),
                                               on_click=self.delegate.did_select_direction))
        stack = HorizontalStack(button_list, padding=25)
        stack.set_center((500, 850))
        self.add_element(stack)

    ##############################
    ###         SUGGEST        ###
    ##############################

    #starts suggestion view - shows character first
    def transition_to_suggestion(self):
        for element in self.elements:
            if isinstance(element, Stack) or isinstance(element, TextElement):
                self.del_element(element)

        button_list = []
        choose_character = TextElement("Please select a character to suggest: ")
        choose_character.set_center((500, 775))
        self.add_element(choose_character)

        pos = pygame.Rect((0, 0), (100, 30))
        for character in Character:
            button_list.append(
                CharacterButton(character=character, button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                         text=character.value,
                                                                                         manager=self.ui_manager,
                                                                                         visible=True),
                                on_click=self.did_select_character))
        stack = HorizontalStack(button_list, padding=15)
        stack.set_center((500, 850))
        self.add_element(stack)

    # transitions to weapon view during suggest phase
    def __transition_weapon(self):
        for element in self.elements:
            if isinstance(element, Stack) or isinstance(element, TextElement):
                self.del_element(element)
        button_list = []

        choose_weapon = TextElement("Please select a weapon to suggest: ")
        choose_weapon.set_center((500, 775))
        self.add_element(choose_weapon)

        pos = pygame.Rect((0, 0), (100, 30))
        for weapon in Weapon:
            button_list.append(
                WeaponButton(weapon=weapon, button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                text=weapon.value,
                                                                                manager=self.ui_manager,
                                                                                visible=True),
                             on_click=lambda w: self.delegate.did_suggest(self.last_selection, w)))
        stack = HorizontalStack(button_list, padding=15)
        stack.set_center((500, 850))
        self.add_element(stack)

    # after select character view, show select weapon view
    def did_select_character(self, character: Character):
        self.last_selection = character
        self.__transition_weapon()

    def transition_disprove(self, disproving_cards: [Card]):
        for element in self.elements:
            if isinstance(element, Stack) or isinstance(element, TextElement):
                self.del_element(element)
        button_list = []

        choose_disproving_suggestion = TextElement("Please select a card to disprove with: ")
        choose_disproving_suggestion.set_center((500, 775))
        self.add_element(choose_disproving_suggestion)

        pos = pygame.Rect((0, 0), (100, 30))
        for card in disproving_cards:
            button_list.append(CardButton(card=card, button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                         text=f"{card.type}.{card.value}",
                                                                                         manager=self.ui_manager,
                                                                                         visible=True),
                                          on_click=self.delegate.did_disprove))

        stack = HorizontalStack(button_list, padding=15)
        stack.set_center((500, 850))
        self.add_element(stack)

    # Transition to accuse part of action view - start with characters
    def transition_accuse(self):
        for element in self.elements:
            if isinstance(element, Stack) or isinstance(element, TextElement):
                self.del_element(element)

        button_list = []
        choose_character = TextElement("Please select a character to accuse: ")
        choose_character.set_center((500, 775))
        self.add_element(choose_character)

        pos = pygame.Rect((0, 0), (100, 30))
        for character in Character:
            button_list.append(
                CharacterButton(character=character, button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                         text=character.value,
                                                                                         manager=self.ui_manager,
                                                                                         visible=True),
                                on_click=self.did_accuse_character))
        stack = HorizontalStack(button_list, padding=15)
        stack.set_center((500, 850))
        self.add_element(stack)





    ##################################
    #              END TURN          #
    ##################################
    def transition_end_turn(self):
        for element in self.elements:
            if isinstance(element, Stack) or isinstance(element, TextElement):
                self.del_element(element)
        turn_over_text = TextElement("TURN OVER")
        turn_over_text.set_center((500, 850))
        self.add_element(turn_over_text)

class DisproveView(View):
    class Delegate(Protocol):
        def did_disprove(self, card: Card, suggest: Suggest):
            pass

    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, delegate: Delegate,
                 disproving_cards: [Card], suggest: Suggest):

        super().__init__(screen, ui_manager)
        self.delegate = delegate
        self.suggest = suggest
        rectangle = pygame.Rect(.5, 750, 1000, 249)
        action_box = ViewBox(rectangle, screen)
        self.add_element(action_box)

        for element in self.elements:
            if isinstance(element, Stack) or isinstance(element, TextElement):
                self.del_element(element)
        button_list = []

        choose_disproving_suggestion = TextElement("Please select a card to disprove with: ")
        choose_disproving_suggestion.set_center((500, 775))
        self.add_element(choose_disproving_suggestion)

        pos = pygame.Rect((0, 0), (100, 30))
        if not disproving_cards:
            button_list.append(CardButton(card=None, button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                         text=f"None",
                                                                                         manager=self.ui_manager,
                                                                                         visible=True),
                                          on_click=lambda x: self.delegate.did_disprove(Card, suggest)))
        else:
            for card in disproving_cards:
                button_list.append(CardButton(card=card, button=pygame_gui.elements.UIButton(relative_rect=pos,
                                                                                             text=f"{card.card_value}",
                                                                                             manager=self.ui_manager,
                                                                                             visible=True),
                                              on_click=lambda x: self.delegate.did_disprove(card, suggest)))

        stack = HorizontalStack(button_list, padding=15)
        stack.set_center((500, 850))
        self.add_element(stack)


