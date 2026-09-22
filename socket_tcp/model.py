class _PaqueteTCP:
	"""Estructura de 7 + 16 Bytes que almacena headers TCP.

	Esta estructura tiene los headers ACK, SYN, FIN y SEQ.
	ACK (1 Byte): Acknowledge de la conexión.
	SYN (1 Byte): Sincronización de la conexión.
	FIN (1 Byte): Término de la conexión.
	SEQ (4 Bytes [Int]): Orden del paquete de la conexión.
	BODY (16 Bytes): Contenido transportado.
	"""
	def __init__(self):
		self.ack: bytes = bytes(1)
		self.syn: bytes = bytes(1)
		self.fin: bytes = bytes(1)
		self.seq: bytes = bytes(4)
		self.body: bytes = bytes(9)

class SocketTCP:

	def __init__(self):
		pass

	@staticmethod
	def parse_segment():
		pass

	@staticmethod
	def create_segment():
		pass

	def bind(address: tuple[str, str]):
		pass

	def connect(address: tuple[str, str]):
		pass

	def accept():
		pass

	def close():
		pass

	def recv_close():
		pass

	# --- Funciones del Stop & Wait

	def send(message: bytes):
		pass

	def recv(buff_size: bytes):
		pass
