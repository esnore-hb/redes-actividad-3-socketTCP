"""Desde la raíz: python -c "import runpy; runpy.run_path('test/handshake_loss.py', run_name='__main__')"."""
import socket
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from socket_tcp import SocketTCP


class LossSocket:
    def __init__(self, udp, losses):
        self.udp = udp
        self.losses = losses

    def __getattr__(self, name):
        return getattr(self.udp, name)

    def sendto(self, data, address):
        packet = SocketTCP.parse_segment(data)
        if packet.syn == 1:
            kind = "syn_ack" if packet.ack else "syn"
        elif packet.ack == 1:
            kind = "ack"
        else:
            kind = "data"
        if kind in self.losses:
            self.losses.remove(kind)
            return len(data)  # Simula un paquete enviado que no llega.
        return self.udp.sendto(data, address)


def check_loss(kinds):
    losses = set(kinds)
    real_socket = socket.socket
    sockets = []

    def make_socket(*args, **kwargs):
        udp = LossSocket(real_socket(*args, **kwargs), losses)
        sockets.append(udp)
        return udp

    message = ("Mensaje largo con canción y café. " * 20).encode()
    try:
        with patch("socket_tcp.model.socket.socket", side_effect=make_socket):
            server = SocketTCP()
            client = SocketTCP()
            server.bind(("127.0.0.1", 0))

            def receive():
                connection, _ = server.accept()
                connection._socket.settimeout(3)
                data = connection.recv(14)
                while len(data) < len(message):
                    data += connection.recv(14)
                assert data == message
                connection.recv_close()
                assert connection._socket.fileno() == -1

            with ThreadPoolExecutor(max_workers=1) as executor:
                receiver = executor.submit(receive)
                client.connect(server._local_address)
                client.send(message)
                client.close()
                receiver.result(timeout=5)
            assert not losses, losses
            assert client._socket.fileno() == -1
            print("OK:", ", ".join(kinds) or "sin pérdidas")
    finally:
        for udp in sockets:
            udp.close()


if __name__ == "__main__":
    for kinds in ((), ("syn",), ("syn_ack",), ("ack",),
                  ("syn", "syn_ack", "ack", "data")):
        check_loss(kinds)
