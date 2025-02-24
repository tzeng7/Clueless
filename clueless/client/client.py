import queue

import pygame
import pygame_gui
from typing import cast

from clueless.client.client_game_manager import ClientGameManager
from clueless.client.client_player import ClientPlayer
from clueless.client.connection import GameConnection
from clueless.client.view import TitleView, View, GameView
from clueless.messages.messages import AssignPlayerID, UpdatePlayers, StartGame, Move, DealCards, YourTurn, Suggest, \
    RequestDisprove, Disprove, EndTurn, Accuse, EndGame
from clueless.model.board import Room
from clueless.model.board_enums import Direction, Character, Weapon, Location
from clueless.model.card import Card
from clueless.model.player import PlayerID


class GameClient(TitleView.Delegate):
    # GameClient serves as the controller for the game.
    # GameClient will handle all server messages that are added to the message queue.
    # Has access to the View to update the pygame screen or transition to a new pygame screen.
    # Will call the client game manager to handle game logic and what data to send to the server.
    def __init__(self):
        pygame.init()
        width, height = View.SCREEN_SIZE
        self.screen: pygame.Surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Clueless")
        self.ui_manager = pygame_gui.UIManager((self.screen.get_rect().width, self.screen.get_rect().height))
        self.game_clock = pygame.time.Clock()
        self.server_ip_address = "127.0.0.1"
        self.view: View = TitleView(self.screen, self.server_ip_address, self.ui_manager, delegate=self)
        self.message_queue = queue.SimpleQueue()
        self.connection: GameConnection | None = None
        self.game_manager: ClientGameManager = None
        self.player: ClientPlayer = None
        self.player_list: [PlayerID] = []

    def update(self):
        if self.connection:
            self.connection.update()
        self.process_input()
        self.ui_manager.update(self.game_clock.tick(60))
        self.screen.fill('white')
        self.view.draw()
        pygame.display.update()

    def redraw(self):
        self.screen.fill('white')
        self.view.draw()
        pygame.display.update()

    def transition(self, new_view: View):
        self.screen.fill('white')
        self.view = new_view

    def process_input(self):
        while not self.message_queue.empty():
            next_message = self.message_queue.get()
            fn_name = f"handle_msg_{next_message.name}"
            if hasattr(self, fn_name):
                getattr(self, fn_name)(next_message)
            else:
                print(f"Couldn't find handler for {next_message.name}")

        for event in pygame.event.get():
            # quit if the quit button was pressed
            self.ui_manager.process_events(event)
            if event.type == pygame.QUIT:
                exit()
            else:
                self.view.respond_to_event(event)

    ###############################################
    ##########     TitleView.Delegate       #######
    ###############################################

    def did_update_server_ip(self, new_ip_address: str):
        self.server_ip_address = new_ip_address

    def did_set_nickname(self, nickname: str):
        # on_text_finished: text input element
        self.connection = GameConnection(self.server_ip_address, int(10000), self.message_queue)
        if type(self.view) is not TitleView:
            print("Error: received ready but no longer showing title view")
        self.connection.join_game(nickname=nickname)
        self.view.transition_to_ready_button()

    def did_ready(self):
        # on_click: ready button
        if type(self.view) is not TitleView:
            print("Error: received ready but no longer showing title view")
        print("READY FROM DELEGATE!")
        self.connection.ready()

    ###############################################
    ##########     GameView.Delegate       #######
    ###############################################
    def did_move(self, movement_option: (Direction, (int, int))):
        # on_click: action_button, direction_button
        if type(self.view) is not GameView:
            print("Error: received movement selection but no longer showing game view")
        self.connection.Send(self.game_manager.move(movement_option[1]))

    def did_suggest(self, character: Character, weapon: Weapon):
        # on_click: action_button, character_button, weapon_button
        if type(self.view) is not GameView:
            print("Error: received suggestion selection but no longer showing game view")
        print(f"Suggested: {character}, {weapon}")
        game_view = cast(GameView, self.view)
        game_view.set_dialog("Waiting for disproval...")
        space = self.game_manager.board.get_player_space(self.player.player_id)
        location = cast(Room, space).room_type
        self.connection.Send(self.game_manager.suggest((character, weapon, location)))

    def did_accuse(self, character: Character, weapon: Weapon, location: Location):
        # on_click: action_button, character_button, weapon_button, location_button
        if type(self.view) is not GameView:
            print("Error: received suggestion selection but no longer showing game view")
        self.connection.Send(self.game_manager.accuse((character, weapon, location)))

    def did_end_turn(self):
        # on_click: action_button
        if type(self.view) is not GameView:
            print("Error: received suggestion selection but no longer showing game view")
        self.connection.Send(self.game_manager.end_turn())
        game_view = cast(GameView, self.view)
        game_view.restore_default_menu_text()

    def did_disprove(self, card: Card, suggest: Suggest):
        game_view = cast(GameView, self.view)
        if game_view.menu_dialog.text != "Your accusation was incorrect.":
            game_view.restore_default_menu_text()
        self.connection.Send(self.game_manager.disprove(card, suggest))


    #######################################
    ###         SERVER MESSAGE          ###
    #######################################
    def handle_msg_assign_player_id(self, msg: AssignPlayerID):
        if type(self.view) is not TitleView:
            print("Error: received AssignPlayerID but no longer showing title view")
        self.player = ClientPlayer(msg.player_id)

    def handle_msg_update_players(self, msg: UpdatePlayers):
        if type(self.view) is not TitleView:
            print("Error: received UpdatePlayers but no longer showing title view")
        self.player_list = [player[0] for player in msg.players]
        cast(TitleView, self.view).add_player_id(msg.players, self.player.player_id)
        print("Received UpdatePlayers!")
        self.redraw()

    def handle_msg_start_game(self, msg: StartGame):
        if type(self.view) is not TitleView:
            print("Error: received StartGame but no longer showing title view")
        print("Received StartGame!")
        self.game_manager = ClientGameManager(self.player, msg.board)
        game_view = GameView(self.screen, self.ui_manager, self, self.game_manager)
        self.transition(game_view)
        game_view.initialize_player_list(self.player_list, self.player.player_id)
        game_view.update_board_elements(msg.board)

    def handle_msg_deal_cards(self, msg: DealCards):
        print("Received DealCards!")
        self.player.cards = msg.cards

    def handle_msg_start_turn(self, msg: YourTurn):
        print("Received Start Turn!")
        if type(self.view) is not GameView:
            print("Error: received StartTurn but not showing game view")
        game_view = cast(GameView, self.view)
        game_view.set_turn_pointer(msg.turn_id % len(self.player_list))
        if type(self.view) is GameView:
            cast(GameView, self.view).display_player_cards(self.player.cards)
        if self.player.player_id == msg.player_id:
            self.game_manager.start_turn(msg.turn_id)
            game_view.show_actions()



    def handle_msg_ClientAction_move(self, msg: Move):
        print("Received Move!")
        game_view = cast(GameView, self.view)
        self.game_manager.board.move(msg.player_id, msg.position)
        print(self.game_manager.board)
        game_view.update_board_elements(self.game_manager.board)
        if msg.player_id == self.player.player_id:
            game_view.show_actions()
        else:
            game_view.set_dialog(f"{msg.player_id.character.value} moved to the "
                                 f"{self.game_manager.board.get_character_position_description(msg.player_id)}.")
            self.redraw()
            pygame.time.delay(2000)
            game_view.restore_default_menu_text()

    def handle_msg_ClientAction_suggest(self, suggest: Suggest):
        self.game_manager.handle_suggestion(suggest)
        game_view = cast(GameView, self.view)

        game_view.update_board_elements(self.game_manager.board)
        if self.player.player_id == suggest.player_id:
            self.game_manager.suggest(suggest.suggestion)
        else:
            game_view.set_dialog(f"{suggest.player_id.nickname} suggested that {suggest.suggestion[0].value} committed murder\n"
                                 f"using the {suggest.suggestion[1].value} in the {suggest.suggestion[2].value}.")
            self.redraw()
            pygame.time.delay(2000)
            game_view.restore_default_menu_text()

    def handle_msg_request_disprove(self, request_disprove: RequestDisprove):
        print("Received Request Disprove")
        print(request_disprove.suggest.suggestion)
        disproving_cards = self.game_manager.disproving_cards(request_disprove.suggest)
        game_view = cast(GameView, self.view)
        game_view.show_disprove(disproving_cards, request_disprove.suggest)

    def handle_msg_ClientAction_disprove(self, disprove: Disprove):
        game_view = cast(GameView, self.view)

        if disprove.suggest.player_id == self.player.player_id:
            if not disprove.card:
                text = "No one was able to disprove your suggestion."
            else:
                text = (f"{disprove.player_id.nickname} disproved your suggestion!\n"
                        + f"The disproving card is {disprove.card.card_value}.")
            game_view.set_dialog(text)
            self.redraw()
            pygame.time.delay(2000)
            game_view.show_actions()
        elif disprove.player_id != self.player.player_id:
            if not disprove.card:
                text = f"No one was able to disprove {disprove.suggest.player_id.nickname}'s suggestion."
            else:
                text = f"{disprove.suggest.player_id.nickname}'s suggestion was disproved by {disprove.player_id.nickname}."
            game_view.set_dialog(text)
            self.redraw()
            pygame.time.delay(2000)
            game_view.restore_default_menu_text()

    def handle_msg_ClientAction_accuse(self, accuse: Accuse):
        game_view = cast(GameView, self.view)
        game_view.show_accusation_incorrect(accuse, is_own_accusation=self.player.player_id == accuse.player_id)
        if self.player.player_id == accuse.player_id:
            self.connection.Send(self.game_manager.end_turn())
        self.redraw()
        pygame.time.delay(2000)
        game_view.restore_default_menu_text()

    def handle_msg_ClientAction_end_turn(self, end_turn: EndTurn):
        print("Received End Turn!")
        # if self.player.player_id == end_turn.player_id:


    def handle_msg_end_game(self, end_game: EndGame):
        print(f"{end_game.accuse.player_id.nickname} guessed correctly. Game Over!")
        game_view = cast(GameView, self.view)
        game_view.game_over(end_game.accuse)

if __name__ == '__main__':
    c = GameClient()
    while 1:
        c.update()
