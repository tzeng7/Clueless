from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from weakref import WeakKeyDictionary
import time

from player import Player, Character


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

    def Network_myaction(self, data):
        print(f"myaction: {data}")

    def Network_nickname(self, data):
        nickname = data['nickname']
        print(f"Received nickname {nickname} from client channel {self}")
        self._server.SetNicknameForPlayer(self, nickname)
        self._server.SendPlayers()

    def Network_ready(self, data):
        print(f"Received ready from client channel {self}")
        self._server.SetReadyForPlayer(self)


class ClueServer(Server):

    channelClass = ClientChannel

    def __init__(self):
        Server.__init__(self, localaddr=("127.0.0.1", 10000), listeners=6)
        self.players: dict[ClientChannel, Player] = WeakKeyDictionary()
        print('Server launched')
        print(f'Socket: {self.socket}')

    # From PodSixNet:
    # Copied from ChatServer.py example
    def Connected(self, channel, addr):
        self.AddPlayer(channel)

    def AddPlayer(self, channel):
        print("New Player" + str(channel.addr))
        self.players[channel] = Player(character=list(Character)[len(self.players)])
        self.SendPlayers()
        print("players", [p for p in self.players])

    def DelPlayer(self, channel):
        print("Deleting Player" + str(channel.addr))
        del self.players[channel]
        self.SendPlayers()

    def SendPlayers(self):
        self.SendToAll({"action": "players", "players": [p.nickname for p in self.players.values()]})

    def SendToAll(self, data):
        [p.Send(data) for p in self.players]

    def SetNicknameForPlayer(self, channel, nickname):
        self.players[channel].nickname = nickname

    def SetReadyForPlayer(self, channel):
        (self.players[channel]).ready = True
        print("READY")
        if all(player.ready for player in self.players.values()):
            self.SendToAll({"action": "game_start"})

    def Launch(self):
        while True:
            self.Pump()
            time.sleep(0.0001)

if __name__ == '__main__':
    print('Hi PyCharm!')
    ClueServer().Launch()
