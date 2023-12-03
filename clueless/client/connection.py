import queue
import time
from typing import Type

from PodSixNet.Connection import ConnectionListener, connection

from clueless.messages.messages import JoinGame, Ready, UpdatePlayers, AssignPlayerID, DealCards, YourTurn, \
    RequestDisprove, \
    Disprove, BaseMessage, StartGame, Move, Suggest, Accuse, BaseClientAction, EndGame, EndTurn


class GameConnection(ConnectionListener):
    # Responsible for sending and receiving messages to and from the server.
    # When receiving messages from the server, these messages will be added to the message queue
    # which the game client will react to.
    def __init__(self, host, port, message_queue: queue.SimpleQueue):
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

    def move(self, msg: Move):
        self.Send(Move(msg.player_id, msg.position))

    def next_action(self, msg: BaseClientAction):
        self.Send(msg)

    #######################################
    ### Network event/message callbacks ###
    #######################################


    def Network(self, data):
        # Deserializes the server payload as a Message and adds Message to the message queue
        # The message queue will be polled by the game client.
        msg_type: Type[BaseMessage]
        action_name = data['action']
        if action_name == AssignPlayerID.name:
            msg_type = AssignPlayerID
        elif action_name == UpdatePlayers.name:
            msg_type = UpdatePlayers
        elif action_name == StartGame.name:
            msg_type = StartGame
        elif action_name == DealCards.name:
            msg_type = DealCards
        elif action_name == YourTurn.name:
            msg_type = YourTurn
        elif action_name == EndGame.name:
            msg_type = EndGame
        # CLIENT ACTIONS
        elif action_name == Move.client_action_name():
            msg_type = Move
        elif action_name == Suggest.client_action_name():
            msg_type = Suggest
        elif action_name == Disprove.client_action_name():
            msg_type = Disprove
        elif action_name == RequestDisprove.name:
            msg_type = RequestDisprove
        elif action_name == Accuse.client_action_name():
            msg_type = Accuse
        elif action_name == EndTurn.client_action_name():
            msg_type = EndTurn
        else:
            print(f"ERROR: couldn't find corresponding message for {data['action']}")
            return
        self.message_queue.put(msg_type.deserialize(data))

    # built in stuff

    def Network_connected(self, data):
        print("*** You are now connected to the server")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()
