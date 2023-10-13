from sys import stdin

from PodSixNet.Connection import ConnectionListener, connection
import pygame
import time

class PlayerClient(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
        print("Player client started")
        print("Ctrl-C to exit")
        # get a nickname from the user before starting
        print("Enter your nickname: ")
        connection.Send({"action": "nickname", "nickname": stdin.readline().rstrip("\n")})
        for _ in range(1, 10):
            self.Loop()
        print("Hit enter when ready!")
        stdin.readline()
        connection.Send({"action": "ready"})


    def Loop(self):
        connection.Pump()
        self.Pump()

    #######################################
    ### Network event/message callbacks ###
    #######################################

    def Network_players(self, data):
        print("*** players: " + ", ".join([p for p in data['players']]))

    def Network_game_start(self, data):
        print("*** Game Started!")

    def Network_message(self, data):
        print(data['who'] + ": " + data['message'])

    # built in stuff

    def Network_connected(self, data):
        print("You are now connected to the server")

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()

    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()


if __name__ == '__main__':
    c = PlayerClient("127.0.0.1", int(10000))
    while 1:
        c.Loop()
        time.sleep(0.001)