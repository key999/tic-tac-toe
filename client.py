import socket
import threading


class Client:
    _available_clients = []
    _my_id = -1

    def __init__(self, server_address: str = "127.0.0.1", server_port: int = 25555):
        self._server_address = server_address
        self._server_port = server_port

    def run(self):
        with socket.socket() as sock:
            sock.connect((self._server_address, self._server_port))
            Listen(sock).start()
            while True:
                command = input(f"{self._my_id}$: ")
                if command in ['q', 'quit', 'exit', 'x']:
                    break
                sock.send(command.encode())

    @property
    def clients(self):
        return self._available_clients

    @property
    def my_id(self):
        return self._my_id


class Listen(threading.Thread):
    def __init__(self, sock: socket.socket):
        threading.Thread.__init__(self)
        self._server = sock

    def run(self):
        while True:
            response = self._server.recv(2048).decode()
            print(response)  # DEBUG

            if response.startswith('you:'):
                # client.set_my_id(response[4:])
                client._my_id = response[4:]
            elif response.startswith('clients:'):
                # client.set_clients(response[8:].split(', '))
                client._available_clients = response[8:].split(', ')


if __name__ == "__main__":
    print("Game started, please specify:")
    client = Client()
    client.run()
