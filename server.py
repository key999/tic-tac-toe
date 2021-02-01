import socket
import threading
from itertools import cycle
from time import sleep


class Server(threading.Thread):
    IDs = cycle(range(1, 11))
    _run = True
    _connections = {}

    def __init__(self, port: int = 25555):
        threading.Thread.__init__(self)
        self._port = port

    def run(self) -> None:
        with socket.socket() as server_socket:
            print("SerThr: Initialized, binding socket... ", end='')  # DEBUG
            server_socket.bind(("0.0.0.0", self._port))
            print("Socket bound! Listening...")  # DEBUG
            server_socket.listen()

            while self._run:
                connection_id = next(self.IDs)
                if connection_id in self._connections.keys():
                    continue

                connection, address = server_socket.accept()
                self._connections[connection_id] = connection, address
                print(f"SerThr: Connection established, address: {address}\nLaunching connection thread...")  # DEBUG

                connection_id.append(Connection(connection, address, connection_id).start())
                print("SerThr: Thread launched, continuing to listen")  # DEBUG

            for i in connection_id:
                i.join()

    @property
    def connections_ids(self):
        return self._connections.keys()

    def connection(self, connection_id: int) -> str or socket.socket:
        return self._connections[connection_id]


class Connection(threading.Thread):
    _connection_2_address = _connection_2_id = _connection_2_sock = None

    def __init__(self, connection_1_socket, connection_1_address, connection_1_id):
        threading.Thread.__init__(self)
        self._connection_1_sock = connection_1_socket
        self._connection_1_address = connection_1_address
        self._connection_1_id = connection_1_id

    def run(self):
        sleep(3)
        print("\tConThr: Connection thread here, sending ID to client")  # DEBUG
        self._connection_1_sock.send(f"{self._connection_1_id}".encode())

        print("\tConThr: Sending available IDs list to client.")  # DEBUG
        self._connection_1_sock.send(server.connections_ids)

        while self._connection_2_id is None:
            self._connection_2_id = self._connection_1_sock.recv().decode()
            print(f"\tConThr: Client wants to connect to ID {self._connection_2_id}")  # DEBUG
            if self._connection_2_id not in server.connections_ids:
                print(f"\tConThr: {self._connection_2_id} is not yet connected, asking again...")  # DEBUG
                self._connection_1_sock.send(f"11: destination not found".encode())

        print(f"\tConThr: {self._connection_2_id} is already connected. Starting a game...")  # DEBUG
        self._connection_2_sock = server.connection(self._connection_2_id)[0]
        self._connection_2_address = server.connection(self._connection_2_id)[1]
        Game(self._connection_1_sock, self._connection_2_sock).run()
        # print(f"\tConThr: Game between {self._connection_1_address} \
        # and {self._connection_2_address} launched.")  # DEBUG


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


server = Server()
server.run()
