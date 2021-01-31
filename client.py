import socket
import threading


class Client:
    def __init__(self, server_address: str, server_port: int):
        self._server_address = server_address
        self._server_port = server_port

    def run(self):
        with socket.socket() as sock:
            sock.connect((self._server_address, self._server_port))
            Listen(sock).start()
            while True:
                pass


class Listen(threading.Thread):
    def __init__(self, sock: socket.socket):
        threading.Thread.__init__(self)
        self._server = sock

    def run(self):
        while True:
            print(self._server.recv(2048).decode())


if __name__ == "__main__":
    print("Game started, please specify:")
    Client(input("Server address: "), int(input("Server port: ")))
