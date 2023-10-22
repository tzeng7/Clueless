from PodSixNet.Connection import ConnectionListener, connection
import time
from threading import Thread

from client_game_manager import ClientGameManager
from client_player import ClientPlayer
from messages.messages import JoinGame, Ready, UpdatePlayers, AssignPlayerID, DealCards, YourTurn, RequestDisprove, \
    Disprove, BaseMessage, StartGame, Move, Suggest


class GameClient(ConnectionListener):
    def __init__(self, host, port):
        self.player: ClientPlayer = None
        self.game_manager: ClientGameManager = None
        self.Connect((host, port))
        print("Player client started")
        print("Ctrl-C to exit")
        # get a nickname from the user before starting
        nickname = input("Enter your nickname: ")
        self.Send(JoinGame(nickname=nickname))

        # listen for ready on a separate thread, in order to not block the thread,
        # which will prevent the client from receiving updates about other players joining.
        self.ready_thread = Thread(target=self.listen_for_ready)
        self.ready_thread.start()

    def update(self):
        connection.Pump()
        self.Pump()

        time.sleep(0.001)

    def Send(self, data: BaseMessage):
        connection.Send(data.serialize())

    #######################################
    ### Keyboard I/O callbacks          ###
    #######################################
    def listen_for_ready(self):
        time.sleep(2)
        print(input("Hit any key when ready!\n"))
        print("READY!")
        self.Send(Ready())

    #######################################
    ### Network event/message callbacks ###
    #######################################

    def Network_assign_player_id(self, data):
        player_id = AssignPlayerID.deserialize(data).player_id
        print(f"*** you are: {player_id}")
        self.player = ClientPlayer(player_id=player_id)

    def Network_update_players(self, data):
        update_players: UpdatePlayers = UpdatePlayers.deserialize(data)
        print(f"*** players: {[p for p in update_players.players]}")

    def Network_start_game(self, data):
        print("*** Game Started!")
        board = StartGame.deserialize(data).board
        self.game_manager = ClientGameManager(player=self.player, board=board)

    def Network_start_turn(self, data):
        print("*** Turn start!")
        turn_id = YourTurn.deserialize(data).turn_id
        self.game_manager.start_turn(turn_id=turn_id)  # managing turn history
        self.Send(self.game_manager.next_action())

    def Network_ClientAction_move(self, data):
        print("*** Received move!")
        move: Move = Move.deserialize(data)

        self.game_manager.board.move(move.player_id, move.position)
        # self.game_manager.board.move(move., move.position)
        if move.player_id == self.player.player_id:
            self.Send(self.game_manager.next_action())

    def Network_ClientAction_suggest(self, data):
        print("*** Received suggestion")
        suggest: Suggest = Suggest.deserialize(data)

        for player in self.game_manager.board.player_tokens:
            if suggest.suggestion[0] == player.character:
                self.game_manager.board.move(player, suggest.suggestion[2].get_position())
                print("Moved suggested player.")


        # if suggest.player_id == self.player.player_id:
        #     self.Send(self.game_manager.next_action())
        # self.Send(self.game_manager.next_action())

    def Network_ClientAction_disprove(self, data):
        disprove: Disprove = Disprove.deserialize(data)
        if not disprove.card:
            print(f"*** No one can disprove suggestion")
        else:
            print(f"*** Received disprove {disprove.card}")
        self.Send(self.game_manager.next_action())

    def Network_request_disprove(self, data):
        request_disprove = RequestDisprove.deserialize(data)
        self.Send(self.game_manager.disprove(request_disprove.suggest))

    def Network_deal_cards(self, data):
        deal_cards: DealCards = DealCards.deserialize(data)
        self.player.cards.append(deal_cards.cards)
        print(f"*** Received cards: {self.player.cards}")

    # built in stuff

    def Network_connected(self, data):
        print("*** You are now connected to the server")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()


if __name__ == '__main__':
    c = GameClient("127.0.0.1", int(10000))
    while 1:
        c.update()
