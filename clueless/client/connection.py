import queue
from typing import Type

from PodSixNet.Connection import ConnectionListener, connection
import time

from clueless.messages.messages import JoinGame, Ready, UpdatePlayers, AssignPlayerID, DealCards, YourTurn, RequestDisprove, \
    Disprove, BaseMessage, StartGame, Move, Suggest, Accuse, EndTurn


class GameConnection(ConnectionListener):
    def __init__(self, host, port, message_queue: queue.SimpleQueue):
        # self.player: ClientPlayer = None
        # self.game_manager: ClientGameManager = None
        self.Connect((host, port))
        self.message_queue = message_queue
        print("Connected to server")
        print("Ctrl-C to exit")

    def update(self):
        connection.Pump()
        self.Pump()

        time.sleep(0.001)

    def Send(self, data: BaseMessage):
        connection.Send(data.serialize())

    #######################################
    ### SEND HELPERS                    ###
    #######################################
    def join_game(self, nickname: str):
        self.Send(JoinGame(nickname=nickname))

    def ready(self):
        self.Send(Ready())

    #######################################
    ### Network event/message callbacks ###
    #######################################
    def Network(self, data):
        msg_type: Type[BaseMessage]
        match data['action']:
            case AssignPlayerID.name:
                msg_type = AssignPlayerID
            case UpdatePlayers.name:
                msg_type = UpdatePlayers
            case StartGame.name:
                msg_type = StartGame
            case DealCards.name:
                msg_type = DealCards
            case YourTurn.name:
                msg_type = YourTurn
            # CLIENT ACTIONS
            case Move.name:
                msg_type = Move
            case Suggest.name:
                msg_type = Suggest
            case Disprove.name:
                msg_type = Disprove
            case RequestDisprove.name:
                msg_type = RequestDisprove
            case Accuse.name:
                msg_type = Accuse
            case _:
                print(f"ERROR: couldn't find corresponding message for {data['action']}")
                return
        self.message_queue.put(msg_type.deserialize(data))

    # def Network_assign_player_id(self, data):
    #     player_id = AssignPlayerID.deserialize(data).player_id
    #     print(f"*** you are: {player_id}")
    #     self.player = ClientPlayer(player_id=player_id)
    #
    # def Network_update_players(self, data):
    #     update_players: UpdatePlayers = UpdatePlayers.deserialize(data)
    #     print(f"*** players: {[p for p in update_players.players]}")
    #
    # def Network_start_game(self, data):
    #     print("*** Game Started!")
    #     board = StartGame.deserialize(data).board
    #     self.game_manager = ClientGameManager(player=self.player, board=board)
    #
    # def Network_deal_cards(self, data):
    #     deal_cards: DealCards = DealCards.deserialize(data)
    #     self.player.cards.append(deal_cards.cards)
    #     print(f"*** Received cards: {self.player.cards}")
    #
    # def Network_start_turn(self, data):
    #     print("*** Turn start!")
    #     turn_id = YourTurn.deserialize(data).turn_id
    #     self.game_manager.start_turn(turn_id=turn_id)  # managing turn history
    #     self.Send(self.game_manager.next_action())
    #
    # def Network_ClientAction_move(self, data):
    #     print("*** Received move!")
    #     move: Move = Move.deserialize(data)
    #
    #     self.game_manager.board.move(move.player_id, move.position)
    #     print(self.game_manager.board)
    #     # self.game_manager.board.move(move., move.position)
    #     if move.player_id == self.player.player_id:
    #         self.Send(self.game_manager.next_action())

    # def Network_ClientAction_suggest(self, data):
    #     print("*** Received suggestion")
    #     suggest: Suggest = Suggest.deserialize(data)
    #
    #     self.game_manager.handle_suggestion(suggest)
    #     print(self.game_manager.board)
    #     # for player in self.game_manager.board.player_tokens:
    #     #     if suggest.suggestion[0] == player.character:
    #     #
    #     #         self.game_manager.board.move(player, suggest.suggestion[2].get_position())
    #     #         print("Moved suggested player.")
    #
    #
    #     # if suggest.player_id == self.player.player_id:
    #     #     self.Send(self.game_manager.next_action())
    #     # self.Send(self.game_manager.next_action())
    #
    # def Network_ClientAction_disprove(self, data):
    #     disprove: Disprove = Disprove.deserialize(data)
    #     if not disprove.card:
    #         print(f"*** No one can disprove suggestion")
    #     else:
    #         print(f"*** Received disprove {disprove.card}")
    #     self.Send(self.game_manager.next_action())
    #
    # def Network_request_disprove(self, data):
    #     request_disprove = RequestDisprove.deserialize(data)
    #     self.Send(self.game_manager.disprove(request_disprove.suggest))
    #
    # def Network_ClientAction_accuse(self, data):
    #     accuse: Accuse = Accuse.deserialize(data)
    #     '''if accuse.is_correct:
    #         print("Congratulations! Your accusation was correct. You win!")
    #
    #     print("Sorry, your accusation was incorrect. You are eliminated from the game.")
    #     self.player.active = False'''
    #     self.Send(self.game_manager.handle_accusation_response(accuse))
    #     # EndTurn(self.player.player_id)


    # built in stuff

    def Network_connected(self, data):
        print("*** You are now connected to the server")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()
