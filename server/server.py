from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time

from messages.messages import JoinGame, StartGame, UpdatePlayers, AssignPlayerID
from model.board_enums import Character
from model.player import PlayerID
from server_player import ServerPlayer


class ClientChannel(Channel):

    def __init__(self, conn=None, addr=(), server=None, map=None):
        super().__init__(conn, addr, server, map)

    def Network(self, data):
        print(data)

    def Close(self):
        self._server.DelPlayer(self)

    # From PodSixNet:
    # Whenever the client does connection.Send(mydata), the Network() method will be called.
    # The method Network_myaction() will only be called if your data has a key called ‘action’
    # with a value of “myaction”. In other words if it looks something like this:
    #
    # data = {"action": "myaction", "blah": 123, ...}

    def Network_join_game(self, data):
        nickname = JoinGame.deserialize(data).nickname
        print(f"Received join_game with nickname {nickname} from client channel {self}")
        self._server.AddPlayer(self, nickname=nickname)

    def Network_ready(self, data):
        print(f"Received ready from client channel {self}")
        self._server.SetReadyForPlayer(self)


class ClueServer(Server):
    channelClass = ClientChannel

    def __init__(self):
        Server.__init__(self, localaddr=("127.0.0.1", 10000), listeners=6)
        self.player_queue: dict[ClientChannel, ServerPlayer] = {}
        self.game_model = None
        print('Server launched')
        print(f'Socket: {self.socket}')

    # From PodSixNet:
    # Copied from ChatServer.py example
    def Connected(self, channel, addr):
        print("New Client Connected " + str(channel.addr))

    ################################
    #      PLAYER MANAGEMENT       #
    ################################

    def AddPlayer(self, channel, nickname):
        print("New Player" + str(channel.addr))
        minted_id = PlayerID(character=list(Character)[len(self.player_queue)], nickname=nickname)
        self.player_queue[channel] = ServerPlayer(minted_id)
        channel.Send(AssignPlayerID(player_id=minted_id).serialize())
        self.SendPlayers()
        print("players in queue", [p for p in self.player_queue])

    def DelPlayer(self, channel):
        print("Deleting Player" + str(channel.addr))
        del self.player_queue[channel]
        self.SendPlayers()

    def SendPlayers(self):
        self.SendToAll(UpdatePlayers(players=[player.wrapped for player in self.player_queue.values()]).serialize())

    def SetReadyForPlayer(self, channel):
        (self.player_queue[channel]).ready = True
        print("READY")
        if all(player.ready for player in self.player_queue.values()):
            self.SendToAll(StartGame().serialize())

    def SendToPlayer(self, to_player, data):
        for channel, player in self.player_queue:
            if player == to_player:
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
