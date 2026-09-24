
from socket import socket

class SocketTCP:
    def __init__(self):

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dest_address = None
        self.seq = 0
        #me imagino que van a ir mas cosas a medida que vaya avanzando


@staticmethod
#ej segmento = b'0,1,0,0|Hola mundo'
def parse_segment(segment:bytes) -> dict:

    header_bytes, payload_bytes = segment.split(b'|', 1)
    header = header_bytes.decode().split(',')

    return {
        'seq': int(header[0]),
        'syn': int(header[1]),
        'ack': int(header[2]),
        'fin': int(header[3]),
        'data': payload_bytes #recordar que esto esta en bytes
    }


def create_segment(segment_dict: dict) -> bytes:

        seq = segment_dict.get("seq", 0)
        syn = segment_dict.get("syn", 0)
        ack = segment_dict.get("ack", 0)
        fin = segment_dict.get("fin", 0)
        data = segment_dict.get("data", b"")

        # Construir cabecera
        header_str = f"{seq},{syn},{ack},{fin}|"
        return header_str.encode('utf-8') + data