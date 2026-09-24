class PaqueteTCP:
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
		self.body: bytes = bytes(16)

class SocketTCP:

	def __init__(self):
		pass


	@staticmethod
	def parse_segment(segment_bytes: bytes) -> PaqueteTCP:
		# Desempaquetamos cada campo según la posición fija
		ack = int.from_bytes(segment_bytes[0:1], byteorder='big')
		syn = int.from_bytes(segment_bytes[1:2], byteorder='big')
		fin = int.from_bytes(segment_bytes[2:3], byteorder='big')
		seq = int.from_bytes(segment_bytes[3:7], byteorder='big')
		body = segment_bytes[7:]

		return PaqueteTCP(
			ack=ack,
			syn=syn,
			fin=fin,
			seq=seq,
			body=body
		)

	@staticmethod
	def create_segment(segment_dict: PaqueteTCP) -> bytes:
		seq = segment_dict.seq
		syn = segment_dict.syn
		ack = segment_dict.ack
		fin = segment_dict.fin
		body = segment_dict.body

		ack_bytes = ack.to_bytes(1, byteorder='big')
		syn_bytes = syn.to_bytes(1, byteorder='big')
		fin_bytes = fin.to_bytes(1, byteorder='big')
		seq_bytes = seq.to_bytes(4, byteorder='big')

		header = ack_bytes + syn_bytes + fin_bytes + seq_bytes

		return header + body

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
