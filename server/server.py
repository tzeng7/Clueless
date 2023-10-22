from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time
import pdb

from messages.messages import JoinGame, StartGame, UpdatePlayers, AssignPlayerID, DealCards,YourTurnMessage,NotYourTurnMessage,MakeMoveMessage
from model.board_enums import Character
from model.player import PlayerID
from game_manager import GameManager
from server_player import ServerPlayer


class ClientChannel(Channel):

    def __init__(self, conn=None, addr=(), server=None, map=None):
        super().__init__(conn, addr, server, map)

    def Network(self, data):
        print(data)

    def Close(self):
        self._server.del_player(self)

    # From PodSixNet:
    # Whenever the client does connection.Send(mydata), the Network() method will be called.
    # The method Network_myaction() will only be called if your data has a key called ‘action’
    # with a value of “myaction”. In other words if it looks something like this:
    #
    # data = {"action": "myaction", "blah": 123, ...}

    def Network_join_game(self, data):
        nickname = JoinGame.deserialize(data).nickname
        print(f"Received join_game with nickname {nickname} from client channel {self}")
        self._server.add_player(self, nickname=nickname)

    def Network_ready(self, data):
        print(f"Received ready from client channel {self}")
        self._server.set_ready_for_player(self)


class ClueServer(Server):
    channelClass = ClientChannel

    def __init__(self):
        Server.__init__(self, localaddr=("127.0.0.1", 10000), listeners=6)
        self.player_queue: dict[ClientChannel, ServerPlayer] = {}
        self.current_player = None
        self.players =[] #this is queue of players which is used to maintain turns
        self.game_manager: GameManager = None
        print('Server launched')
        print(f'Socket: {self.socket}')

    # From PodSixNet:
    # Copied from ChatServer.py example
    def Connected(self, channel, addr):
        print("New Client Connected " + str(channel.addr))

    ################################
    #      PLAYER MANAGEMENT       #
    ################################

    def add_player(self, channel, nickname):
        print("New Player" + str(channel.addr))
        minted_id = PlayerID(character=list(Character)[len(self.player_queue)], nickname=nickname)
        self.player_queue[channel] = ServerPlayer(minted_id)

        channel.Send(AssignPlayerID(player_id=minted_id).serialize())
        #self.players.append(minted_id)
        self.send_players()
        print("players in queue", [p for p in self.player_queue])

    def del_player(self, channel):
        print("Deleting Player" + str(channel.addr))
        del self.player_queue[channel]
        self.send_players()

    def send_players(self):
        self.SendToAll(UpdatePlayers(players=[player.player_id for player in self.player_queue.values()]).serialize())

    def set_ready_for_player(self, channel):
        (self.player_queue[channel]).ready = True
        pdb.set_trace()
        print("READY")
        if all(player.ready for player in self.player_queue.values()):
            #adding players to the player list which is used to maintain turns
            pdb.set_trace()
            self.players = list(self.player_queue.values())
            self.SendToAll(StartGame().serialize())
            pdb.set_trace()
            self.start_game()

    ################################
    #      GAME MANAGEMENT       #
    ################################

    def start_game(self):
        # TODO Turn management
        self.game_manager = GameManager(players=self.player_queue.values())
        self.game_manager.start_game()
        pdb.set_trace()
        for player in self.game_manager.players:
            self.SendToPlayer(player.player_id, DealCards(cards=player.cards).serialize())
        pdb.set_trace()
        self.next_turn()

    #----------- start of modification -------------#
    def next_turn(self):
        if not self.current_player:
            self.current_player = self.players[0]  # Assign the first player's turn
            pdb.set_trace()
        else:
            current_player_index = self.players.index(self.current_player)
            next_player_index = (current_player_index + 1) % len(self.players)
            self.current_player = self.players[next_player_index]  # Switch to the next player's turn
            pdb.set_trace()

        self.SendToAll(YourTurnMessage().serialize())  # Notify everyone it's the current player's turn
        pdb.set_trace()
        # Implement a timer for the current player's turn
        time.sleep(10.0)
        self.end_turn()

    def end_turn(self):
        self.SendToAll(NotYourTurnMessage().serialize())  # Notify everyone the current player's turn is over
        self.next_turn()

    #------------end of modification-------------#


    ################################
    #       NETWORKING HELPERS     #
    ################################

    def SendToPlayer(self, player_id, data):
        for channel, p in self.player_queue.items():
            if player_id == p.player_id:
                channel.Send(data)
    def SendToChannel(self, channel: Channel, data):
        channel.Send(data)

    def SendToAll(self, data):
        [p.Send(data) for p in self.player_queue]

    def Launch(self):
        while True:
            self.Pump()
            time.sleep(0.0001)


if __name__ == '__main__':
    print('Hi PyCharm!')
    ClueServer().Launch()
