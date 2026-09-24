import random
import socket


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
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


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

	"""Pipeline del socket:
	# --- server
	server_socketTCP = SocketTCP.SocketTCP()
	server_socketTCP.bind(address)
	connection_socketTCP, new_address = server_socketTCP.accept()

	# --- client
	client_socketTCP = SocketTCP.SocketTCP()
	client_socketTCP.connect(address)
	"""
	def bind(self, address: tuple[str, int]):
		self._socket.bind(address)
		self._address = address

	def connect(self, address: tuple[str, int]):
		if not self._address:
			raise Exception("socket_tcp: se te olvidó el bind") # noqa: TRY002

		# --- primera etapa
		x = random.randint(0,100)
		paquete = PaqueteTCP(syn = 1, seq = x)
		self._socket.sendto(self.create_segment(paquete), self._address)

		# --- segunda etapa
		binary = self._socket.recvfrom(23)[0]
		paquete = self.parse_segment(binary)

		if not (paquete.ack == 1 and paquete.syn == 1 and paquete.seq == x + 1):
			raise Exception( # noqa: TRY002
				"socket_tcp: no era el paquete que esperaba"
			)

		# --- tercera etapa
		paquete.syn = 0
		paquete.seq += 1
		self._socket.sendto(self.create_segment(paquete), self._address)


	def accept(self):

		paquete, address = self._socket.recvfrom(23)
		paquete_parseado = SocketTCP.parse_segment(paquete[0])

		if paquete_parseado.syn == 1: #se envio la solucitud del cliente
			seq_envio = paquete_parseado.seq + 1
			send_paquete = PaqueteTCP(ack=1, syn=1, seq=seq_envio)
			self._socket.sendto(SocketTCP.create_segment(send_paquete), address)


		timeout = 0.5

		paquete2, address = self._socket.recvfrom(23)
		paquete_parseado2 = SocketTCP.parse_segment(paquete2)

		if paquete_parseado2.ack == 1 and paquete_parseado2.seq == seq_envio+1:
			mi_socket_tcp = SocketTCP()
			return mi_socket_tcp, address

	def close():
		pass

	def recv_close():
		pass

	# --- Funciones del Stop & Wait

	def send(message: bytes):
		pass

	def recv(buff_size: bytes):
		pass
