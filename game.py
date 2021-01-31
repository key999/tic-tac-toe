import threading
import socket


class Game(threading.Thread):
    def __init__(self, connection_1_sock: socket.socket, connection_2_sock: socket.socket):
        threading.Thread.__init__(self)
        self._connections = connection_1_sock, connection_2_sock

    def run(self):
        self.set_game()
        while True:
            # send game data
            for i in self._connections:
                i.send("13".encode())
                i.send("Game started".encode())  # DEBUG

            # compute game data
            self.compute()

            # receive player 1 data
            cmd = self._connections[0].recv(2048).decode()
            if cmd == "q":
                self.end()
                break

            # compute game data
            self.compute()

            # receive player 2 data
            cmd = self._connections[1].recv(2048).decode()
            if cmd == "q":
                self.end()
                break

    def set_game(self):
        pass

    def compute(self):
        pass

    def end(self):
        for i in self._connections:
            print(f"Shutting down {i}")  # DEBUG
            i.send("12".encode())
            i.send("Game closed by player".encode())  # DEBUG
            i.shutdown(socket.SHUT_RDWR)
            i.close()
