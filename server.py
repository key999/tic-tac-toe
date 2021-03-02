import socket
import threading
from itertools import cycle
from time import sleep
from sys import exit as sysexit


class Supervisor:
    def __init__(self):
        self.server = Server()

    def run(self):
        self.server.start()
        server_started = True
        while server_started:
            cmd = input(f"{self.server.native_id}$: ")
            if cmd == "help":
                print("help - view this section;\n"
                      "connections - show active server connections;\n"
                      "close <connection id> - close specified connection;\n"
                      "close all - close all server connections softly;\n"
                      "stop - forcefully shutdown server")
            elif cmd == "connections":
                print(self.server.get_all_connections)
            elif cmd.startswith("close"):
                if cmd == "close all":
                    self.server.close_all_connections()
                else:
                    self.server.close_connection(int(cmd[6:]))
            elif cmd == "stop":
                server_started = False
                self.server.stop()
                sysexit()
            elif cmd == '':
                continue
            else:
                print("No such command, try 'help'")


class Server(threading.Thread):
    IDs = cycle(range(1, 11))
    _run = True
    _connections = {}

    def __init__(self, port: int = 25555):
        threading.Thread.__init__(self)
        self._port = port

    def run(self) -> None:
        with socket.socket() as server_socket:
            print(f"SerThr: Initialized, binding socket... ", end='')  # DEBUG
            sleep(1)  # DEBUG
            server_socket.bind(("0.0.0.0", self._port))
            print(f"Socket bound! Listening...")  # DEBUG
            server_socket.listen()

            while self._run:
                connection_id = next(self.IDs)
                if connection_id in self._connections.keys():
                    continue

                connection, address = server_socket.accept()

                self._connections[connection_id] = {}
                self._connections[connection_id]["socket"] = connection
                self._connections[connection_id]["address"] = address
                print(f"SerThr: Connection established, address: {address}\n"
                      f"Launching {self.get_connection_by_id(connection_id)} thread...")  # DEBUG

                self._connections[connection_id]["thread"] = \
                    Connection(connection, address, connection_id, self)
                self._connections[connection_id]["thread"].start()
                print(f"SerThr: Thread launched, continuing to listen")  # DEBUG

    @property
    def get_connections_ids(self) -> list:
        return list(self._connections.keys())

    @property
    def get_all_connections(self) -> dict:
        return self._connections

    def get_connection_by_id(self, connection_id: int) -> dict:
        return self._connections[connection_id]

    def close_connection(self, connection_id: int) -> None:
        """
        Closes socket, ends thread, deletes from dictionary

        :param connection_id: int
        :return: None
        """
        try:
            self._connections[connection_id]["socket"].close()
            try:
                self._connections[connection_id]["thread"].join()
            except RuntimeError:
                pass
            self._connections.pop(connection_id)
        except KeyError:
            print(f"SerThr: Cannot close {connection_id}, already closed")  # DEBUG

    def close_all_connections(self) -> None:
        # TODO
        for connection in self._connections:
            self._connections[connection]["socket"].close()
            self._connections[connection]["thread"].join()
        self._connections = {}

    def stop(self) -> None:
        self._run = False


class Connection(threading.Thread):
    _connection_2_address = _connection_2_id = _connection_2_sock = None

    def __init__(self, connection_1_socket: socket.socket, connection_1_address: str,
                 connection_1_id: int, server_instance: Server):
        threading.Thread.__init__(self)
        self._connection_1_sock = connection_1_socket
        self._connection_1_address = connection_1_address
        self._connection_1_id = connection_1_id
        self.server = server_instance

    def __del__(self) -> None:
        print(f"\tConThr{self.native_id}: Life ended, destructing")  # DEBUG
        print(f"\tConThr{self.native_id}: Closing socket, deleting connection...")  # DEBUG
        self.server.close_connection(self._connection_1_id)

    def run(self) -> None:
        sleep(1)  # DEBUG
        print(f"\tConThr{self.native_id}: Connection thread here, sending ID to client")  # DEBUG
        self._connection_1_sock.send(f"you:{self._connection_1_id}".encode())

        print(f"\tConThr{self.native_id}: Sending available IDs list to client")  # DEBUG
        self._connection_1_sock.send(f"clients:{str(list(self.server.get_connections_ids))[1:-1]}".encode())

        print(f"\tConThr{self.native_id}: Waiting for client input")  # DEBUG
        try:
            while True:
                client_command = self._connection_1_sock.recv(2048).decode()

                if client_command.startswith('connect: '):
                    self._connection_2_id = int(client_command[client_command.find(' ') + 1:])
                    print(f"\tConThr{self.native_id}: Client wants to connect to ID {self._connection_2_id}")  # DEBUG

                    if self._connection_2_id not in self.server.get_connections_ids:
                        print(
                            f"\tConThr{self.native_id}: {self._connection_2_id} is not yet connected, asking again...")  # DEBUG
                        self._connection_1_sock.send(f"11: destination not found".encode())
                        continue
                    elif self._connection_2_id == self._connection_1_id:
                        print(f"\tConThr{self.native_id}: {self._connection_1_id} trying to connect to itself")  # DEBUG
                        self._connection_1_sock.send(f"14: self connection impossible".encode())
                        continue
                    else:
                        print(
                            f"\tConThr{self.native_id}: {self._connection_2_id} is already connected. Starting a game...")  # DEBUG
                        self._connection_2_sock = self.server.get_connection_by_id(self._connection_2_id)["socket"]
                        self._connection_2_address = self.server.get_connection_by_id(self._connection_2_id)["address"]
                        Game(self._connection_1_sock, self._connection_2_sock).run()
                        print(f"\tConThr{self.native_id}: Game between {self._connection_1_address}\
                         and {self._connection_2_address} launched.")  # DEBUG

                elif client_command == 'disconnect':
                    print(f"\tConThr{self.native_id}: {self._connection_1_address} wants to disconnect")  # DEBUG
                    break
        except ConnectionError as e:
            print(f"\tConThr{self.native_id}: Connection {self._connection_1_sock} ended\n"
                  f"\tConThr{self.native_id}: {e}")  # DEBUG
        finally:
            self.__del__()


class Game:
    def __init__(self, connection_1_sock: socket.socket, connection_2_sock: socket.socket):
        # threading.Thread.__init__(self)
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


x = Supervisor()
x.run()
