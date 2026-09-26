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
		self._local_address = None
		self._remote_address = None

	@staticmethod
	def parse_segment(segment_bytes: bytes) -> PaqueteTCP:
		ack = int.from_bytes(segment_bytes[0:1], byteorder="big")
		syn = int.from_bytes(segment_bytes[1:2], byteorder="big")
		fin = int.from_bytes(segment_bytes[2:3], byteorder="big")
		seq = int.from_bytes(segment_bytes[3:7], byteorder="big")
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
		self._local_address = address

	def connect(self, address: tuple[str, int]):
		if not self._local_address:
			raise Exception("socket_tcp: se te olvidó el bind()")  # noqa: TRY002
		self._remote_address = address

		# --- Paso 1: Cliente envía SYN (seq = x) ---
		x = random.randint(0, 100)
		paquete1 = PaqueteTCP(syn=1, seq=x)
		self._socket.sendto(self.create_segment(paquete1), self._remote_address)

		# --- Paso 2: Cliente recibe SYN-ACK ---
		binary, _ = self._socket.recvfrom(23)
		paquete2 = self.parse_segment(binary)

		if not (
			paquete2.syn == 1 and paquete2.ack == 1 and paquete2.seq == x + 1
		):
			raise Exception("socket_tcp: no hubo saludo de manos (etapa 2)")

		# --- Paso 3: Cliente envía ACK final ---
		paquete3 = PaqueteTCP(ack=1, syn=0, seq=x + 2)
		self._socket.sendto(self.create_segment(paquete3), self._remote_address)

	def accept(self):
		# --- Paso 1: Servidor recibe SYN de un cliente ---
		binary, client_address = self._socket.recvfrom(23)
		paquete1 = self.parse_segment(binary)

		if paquete1.syn != 1:
			raise Exception("socket_tcp: no recibí un SYN")

		x = paquete1.seq

		# --- Crear nuevo socket dedicado para la conexión ---
		new_socket = SocketTCP()
		if not self._local_address:
			raise Exception(
				"socket_tcp: ¿aceptando un paquete sin haber hecho bind()?"
			)
		# con puerto 0, el computador asigna un puerto
		new_socket.bind((self._local_address[0], 0))
		new_socket._remote_address = client_address

		# --- Paso 2: Servidor envía SYN-ACK desde el nuevo socket ---
		paquete2 = PaqueteTCP(syn=1, ack=1, seq=x + 1)
		new_socket._socket.sendto(self.create_segment(paquete2), client_address)

		# --- Paso 3: Servidor recibe el ACK final del cliente ---
		binary2, _ = new_socket._socket.recvfrom(23)
		paquete3 = self.parse_segment(binary2)

		if not (
			paquete3.ack == 1 and paquete3.syn == 0 and paquete3.seq == x + 2
		):
			raise Exception("socket_tcp: no hubo saludo de manos (etapa 3)")

		return new_socket, new_socket._remote_address

	def close():
		pass

	def recv_close():
		pass

	# --- Funciones del Stop & Wait

	def send(message: bytes):
		pass

	def recv(buff_size: bytes):
		pass
