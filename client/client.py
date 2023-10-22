
from PodSixNet.Connection import ConnectionListener, connection
import time
from threading import Thread

from client_player import ClientPlayer
from messages.messages import JoinGame, Ready, UpdatePlayers, AssignPlayerID, DealCards,MakeMoveMessage


class GameClient(ConnectionListener):
    def __init__(self, host, port):
        self.player: ClientPlayer = None
        self.Connect((host, port))
        print("Player client started")
        print("Ctrl-C to exit")
        # get a nickname from the user before starting
        nickname = input("Enter your nickname: ")
        connection.Send(JoinGame(nickname=nickname).serialize())

        # listen for ready on a separate thread, in order to not block the thread,
        # which will prevent the client from receiving updates about other players joining.
        self.ready_thread = Thread(target=self.listen_for_ready)
        self.ready_thread.start()

    def update(self):
        connection.Pump()
        self.Pump()

        time.sleep(0.001)


    #######################################
    ### Keyboard I/O callbacks          ###
    #######################################
    def listen_for_ready(self):
        time.sleep(3)
        print(input("Hit any key when ready!\n"))
        print("READY!")
        connection.Send(Ready().serialize())

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

    def Network_deal_cards(self, data):
        deal_cards: DealCards = DealCards.deserialize(data)
        self.player.cards.append(deal_cards.cards)
        print(f"*** Received cards: {self.player.cards}")


    #------------start of modification-------------#
    def handle_make_move(self, move_data):
        # Implement handling player's move here

        pass

    def Network_your_turn(self, data):
        print("It's your turn")
        # Implement actions for the current player's turn

    def Network_not_your_turn(self, data):
        print("It's not your turn")
        # Implement actions for when it's not the player's turn



    def make_move(self, move_data):
        connection.Send(MakeMoveMessage(move_data=move_data).serialize())

    # ------------end of modification-------------#

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
