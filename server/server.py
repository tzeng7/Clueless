from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
import time

from messages.messages import JoinGame, StartGame, UpdatePlayers, AssignPlayerID, BaseClientAction, BaseMessage, Move, \
    Suggest, Disprove, EndTurn, Accuse
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

    def Network_ClientAction_move(self, data):
        move_action = Move.deserialize(data)
        print(f"Received ClientAction_move from client channel {self}")
        self._server.move(self, move_action)

    def Network_ClientAction_suggest(self, data):
        suggest_action = Suggest.deserialize(data)
        print(f"Received ClientAction_suggest from client channel {self}")
        self._server.suggest(self, suggest_action)

    def Network_ClientAction_accuse(self, data):
        accuse_action = Accuse.deserialize(data)
        print(f"Received ClientAction_accuse from client channel {self}")
        self._server.accuse(self, accuse_action)

    def Network_ClientAction_disprove(self, data):
        disprove_action = Disprove.deserialize(data)
        print(f"Received ClientAction_disprove from client channel {self}")
        self._server.disprove(self, disprove_action)

    def Network_ClientAction_end_turn(self, data):
        end_turn_action = EndTurn.deserialize(data)
        print(f"Received ClientAction_end_turn from client channel {self}")
        self._server.end_turn(end_turn_action)


class ClueServer(Server):
    channelClass = ClientChannel

    def __init__(self):
        Server.__init__(self, localaddr=("127.0.0.1", 10000), listeners=6)
        self.player_queue: dict[ClientChannel, ServerPlayer] = {}
        self.game_manager: GameManager = None
        self.min_players = 2
        self.max_players = 6
        print('Server launched')
        print(f'Socket: {self.socket}')

    # From PodSixNet:
    # Copied from ChatServer.py example
    def Connected(self, channel, addr):
        print("New Client Connected " + str(channel.addr))

    ################################
    #       LOBBY MANAGEMENT       #
    ################################

    def add_player(self, channel, nickname):
        #  limit to 6 players
        if len(self.player_queue) < self.max_players:
            print("New Player" + str(channel.addr))
            minted_id = PlayerID(character=list(Character)[len(self.player_queue)], nickname=nickname)
            self.player_queue[channel] = ServerPlayer(minted_id, channel=channel)
            self.SendToChannel(channel, AssignPlayerID(player_id=minted_id))
            self.send_players()
            print("players in queue", [p for p in self.player_queue])
        else:
            print("Game is full")

    def del_player(self, channel):
        print("Deleting Player" + str(channel.addr))
        del self.player_queue[channel]
        self.send_players()

    def send_players(self):
        self.SendToAll(UpdatePlayers(players=[player.player_id for player in self.player_queue.values()]))

    def set_ready_for_player(self, channel):
        (self.player_queue[channel]).ready = True
        print("READY")
        if all(player.ready for player in self.player_queue.values()) and len(self.player_queue) >= self.min_players:
            self.start_game()
        else:
            print("Waiting for more players")

    ################################
    #      GAME MANAGEMENT       #
    ################################

    def start_game(self):
        self.game_manager = GameManager(players=self.player_queue.values())
        self.SendToAll(StartGame(board=self.game_manager.board))
        self.game_manager.start_game()

    def move(self, channel, move_action: Move):
        player_to_move = self.player_queue[channel]
        self.game_manager.move(player_to_move, move_action)

    def suggest(self, channel, suggest_action: Suggest):
        self.game_manager.suggest(suggest_action)
        # TODO: list out rules of when suggest can be called

    def accuse(self, channel, accuse_action: Accuse):
        player_accusing = self.player_queue[channel]
        self.game_manager.accuse(player_accusing, accuse_action)

    def disprove(self, channel, disprove_action: Disprove):
        self.game_manager.disprove(disprove_action)

    def end_turn(self, end_turn_action: EndTurn):
        self.game_manager.end_turn(end_turn_action)

    ################################
    #       NETWORKING HELPERS     #
    ################################

    def SendToPlayer(self, player_id, data: BaseMessage):
        for channel, p in self.player_queue.items():
            if player_id == p.player_id:
                channel.Send(data.serialize())

    def SendToChannel(self, channel: Channel, data: BaseMessage):
        channel.Send(data.serialize())

    def SendToAll(self, data: BaseMessage):
        serialized = data.serialize()
        [p.Send(serialized) for p in self.player_queue]

    def Launch(self):
        while True:
            self.Pump()
            time.sleep(0.0001)


if __name__ == '__main__':
    print('Hi PyCharm!')
    ClueServer().Launch()
