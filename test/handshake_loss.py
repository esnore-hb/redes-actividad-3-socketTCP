"""Desde la raíz: python -c "import runpy; runpy.run_path('test/handshake_loss.py', run_name='__main__')"."""
import socket
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from socket_tcp import SocketTCP


class LossSocket:
    def __init__(self, udp, losses):
        self.udp = udp
        self.losses = losses
        self.closing = False

    def __getattr__(self, name):
        return getattr(self.udp, name)

    def sendto(self, data, address):
        packet = SocketTCP.parse_segment(data)
        if packet.fin == 1:
            self.closing = True
            kind = "fin_ack" if packet.ack else "fin"
        elif packet.syn == 1:
            kind = "syn_ack" if packet.ack else "syn"
        elif packet.ack == 1:
            kind = "close_ack" if self.closing else "ack"
        else:
            kind = "data"
        if self.losses.get(kind, 0) > 0:
            self.losses[kind] -= 1
            return len(data)  # Simula un paquete enviado que no llega.
        return self.udp.sendto(data, address)


def check_loss(kinds, close_from_recv=False):
    losses = dict(kinds) if isinstance(kinds, dict) else {kind: 1 for kind in kinds}
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
                if close_from_recv:
                    assert connection.recv(16) == b""
                else:
                    connection.recv_close()
                assert connection._socket.fileno() == -1

            with ThreadPoolExecutor(max_workers=1) as executor:
                receiver = executor.submit(receive)
                client.connect(server._local_address)
                client.send(message)
                client.close()
                receiver.result(timeout=5)
            assert not any(losses.values()), losses
            assert client._socket.fileno() == -1
            print("OK:", ", ".join(kinds) or "sin pérdidas")
    finally:
        for udp in sockets:
            udp.close()


if __name__ == "__main__":
    for kinds in ((), ("syn",), ("syn_ack",), ("ack",),
                  ("syn", "syn_ack", "ack", "data")):
        check_loss(kinds)
