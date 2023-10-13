from sys import stdin

from PodSixNet.Connection import ConnectionListener, connection
import pygame
import time
from threading import Thread

class PlayerClient(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
        print("Player client started")
        print("Ctrl-C to exit")
        # get a nickname from the user before starting
        print("Enter your nickname: ")
        connection.Send({"action": "nickname", "nickname": stdin.readline().rstrip("\n")})
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
        connection.Send({"action": "ready"})

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
        c.update()
