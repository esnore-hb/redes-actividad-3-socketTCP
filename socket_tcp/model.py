class PaqueteTCP:
	"""Estructura de 7 + 16 Bytes que almacena headers TCP.

	Esta estructura tiene los headers ACK, SYN, FIN y SEQ.
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
		pass


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
