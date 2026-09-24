import random
import socket


class PaqueteTCP:
    """Estructura de 7 + 16 Bytes que almacena headers TCP.

    ACK (1 Byte): Acknowledge de la conexión.
    SYN (1 Byte): Sincronización de la conexión.
    FIN (1 Byte): Término de la conexión.
    SEQ (4 Bytes [Int]): Orden del paquete de la conexión.
    BODY (16 Bytes): Contenido transportado.
    """
    def __init__(
        self,
        ack: int = 0,
        syn: int = 0,
        fin: int = 0,
        seq: int = 0,
        body: bytes = b"",
    ):
        self.ack = ack
        self.syn = syn
        self.fin = fin
        self.seq = seq
        self.body = body


class SocketTCP:

    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._address = None  # Dirección local
        self.destino = None   # Dirección remota
        self.seq = 0          # Número de secuencia del socket

    @staticmethod
    def parse_segment(segment_bytes: bytes) -> PaqueteTCP:
        ack = int.from_bytes(segment_bytes[0:1], byteorder='big')
        syn = int.from_bytes(segment_bytes[1:2], byteorder='big')
        fin = int.from_bytes(segment_bytes[2:3], byteorder='big')
        seq = int.from_bytes(segment_bytes[3:7], byteorder='big')
        body = segment_bytes[7:]

        return PaqueteTCP(ack=ack, syn=syn, fin=fin, seq=seq, body=body)

    @staticmethod
    def create_segment(paquete: PaqueteTCP) -> bytes:
        header = (
            paquete.ack.to_bytes(1, byteorder="big")
            + paquete.syn.to_bytes(1, byteorder="big")
            + paquete.fin.to_bytes(1, byteorder="big")
            + paquete.seq.to_bytes(4, byteorder="big")
        )
        return header + paquete.body

    def bind(self, address: tuple[str, int]):
        self._socket.bind(address)
        self._address = address

    def connect(self, address: tuple[str, int]):
        self.destino = address

        # --- Paso 1: Cliente envía SYN (seq = x) ---
        x = random.randint(0, 100)
        self.seq = x
        p1 = PaqueteTCP(syn=1, seq=x)
        self._socket.sendto(self.create_segment(p1), self.destino)

        # --- Paso 2: Cliente recibe SYN-ACK ---
        binary, _ = self._socket.recvfrom(23)
        p2 = self.parse_segment(binary)

        # Verificamos que sea SYN-ACK y que confirme nuestro paquete (ack == x + 1)
        if not (p2.syn == 1 and p2.ack == 1 and p2.seq == x + 1):
            raise Exception("socket_tcp: Handshake fallido en etapa 2 (SYN-ACK inválido)")

        # --- Paso 3: Cliente envía ACK final ---
        self.seq = x + 1
        p3 = PaqueteTCP(ack=1, syn=0, seq=self.seq)
        self._socket.sendto(self.create_segment(p3), self.destino)

    def accept(self):
        # --- Paso 1: Servidor recibe SYN de un cliente ---
        binary, client_address = self._socket.recvfrom(23)
        p1 = self.parse_segment(binary)

        if p1.syn != 1:
            raise Exception("socket_tcp: Se esperaba un paquete SYN")

        seq_cliente = p1.seq

        # --- Crear nuevo socket dedicado para la conexión ---
        new_socket = SocketTCP()
        # Bind a puerto 0 hace que el SO le asigne un puerto libre distinto
        new_socket.bind((self._address[0], 0))
        new_socket.destino = client_address

        # --- Paso 2: Servidor envía SYN-ACK desde el nuevo socket ---
        # Responde confirmando seq = seq_cliente + 1
        seq_servidor = seq_cliente + 1
        new_socket.seq = seq_servidor
        p2 = PaqueteTCP(syn=1, ack=1, seq=seq_servidor)
        new_socket._socket.sendto(self.create_segment(p2), client_address)

        # --- Paso 3: Servidor recibe el ACK final del cliente ---
        binary2, _ = new_socket._socket.recvfrom(23)
        p3 = self.parse_segment(binary2)

        if not (p3.ack == 1 and p3.seq == seq_servidor + 1):
            raise Exception("socket_tcp: Handshake fallido en etapa 3 (ACK final inválido)")

        new_socket.seq = seq_servidor + 1
        return new_socket, new_socket._address