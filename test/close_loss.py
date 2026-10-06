"""Pruebas del punto 8; ejecutar desde la raíz mediante runpy."""
import runpy
import socket
from unittest.mock import Mock

from socket_tcp import SocketTCP


if __name__ == "__main__":
    check_loss = runpy.run_path("test/handshake_loss.py")["check_loss"]
    for losses in ({}, {"fin": 1}, {"fin_ack": 1}, {"close_ack": 1},
                   {"close_ack": 4}, {"fin_ack": 3},
                   {"fin": 1, "fin_ack": 1, "close_ack": 4}):
        check_loss(losses, close_from_recv=True)

    # Sin respuesta, close() debe esperar tres timeouts y cerrar igualmente.
    client = SocketTCP()
    client._socket.close()
    udp = Mock()
    client._socket = udp
    client._remote_address = ("127.0.0.1", 9000)
    client._seq = 44
    udp.recvfrom.side_effect = socket.timeout()
    client.close()
    assert udp.recvfrom.call_count == 3
    assert udp.sendto.call_count == 3
    udp.close.assert_called_once()
    print("OK: tres timeouts sin respuesta cierran el socket")
