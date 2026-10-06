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
	) -> None:
		"""Constructor del PaqueteTCP.

		Los atributos ACK, SYN, FIN son `bool` representados en Python como
		`int`, pero al ser llevados a una cadena de `bytes`, son de 1 `byte` de
		tamaño. SEQ es un `int` tradicional de 4 `bytes`, y BODY son 16 `bytes`
		de cualquier contenido.

		Args:
			ack (int, optional): Acknowledge de la conexión. Defaults to 0.
			syn (int, optional): Sincronización de la conexión. Defaults to 0.
			fin (int, optional): Término de la conexión. Defaults to 0.
			seq (int, optional): Orden del paquete de la conexión. Defaults to 0.
			body (bytes, optional): Contenido transportado. Defaults to b"".
		"""
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
		self._seq = None  # Último número de secuencia del handshake o transferencia.

	@staticmethod
	def parse_segment(segment_bytes: bytes) -> PaqueteTCP:
		ack = int.from_bytes(segment_bytes[0:1])
		syn = int.from_bytes(segment_bytes[1:2])
		fin = int.from_bytes(segment_bytes[2:3])
		seq = int.from_bytes(segment_bytes[3:7])
		body = segment_bytes[7:]

		return PaqueteTCP(ack, syn, fin, seq, body)

	@staticmethod
	def create_segment(paquete: PaqueteTCP) -> bytes:
		header = (
			paquete.ack.to_bytes(1)
			+ paquete.syn.to_bytes(1)
			+ paquete.fin.to_bytes(1)
			+ paquete.seq.to_bytes(4)
		)
		return header + paquete.body

	def bind(self, address: tuple[str, int]):
		self._socket.bind(address)
		self._local_address = self._socket.getsockname()

	def connect(self, address: tuple[str, int]):
		if not self._local_address:
			self.bind(("", 0))
		self._remote_address = address

		# --- Paso 1: Cliente envía SYN (seq = x) ---
		x = random.randint(0, 100)
		paquete1 = PaqueteTCP(syn=1, seq=x)
		self._socket.sendto(self.create_segment(paquete1), self._remote_address)

		# --- Paso 2: Cliente recibe SYN-ACK ---
		binary, server_address = self._socket.recvfrom(23)
		paquete2 = self.parse_segment(binary)

		if not (
			paquete2.syn == 1 and paquete2.ack == 1
			and paquete2.fin == 0 and paquete2.seq == x + 1
		):
			raise Exception("socket_tcp: no hubo saludo de manos (etapa 2)")  # noqa: TRY002

		# --- Paso 3: Cliente envía ACK final ---
		self._remote_address = server_address
		paquete3 = PaqueteTCP(ack=1, syn=0, seq=x + 2)
		self._socket.sendto(self.create_segment(paquete3), self._remote_address)
		self._seq = paquete3.seq

	def accept(self):
		# --- Paso 1: Servidor recibe SYN de un cliente ---
		binary, client_address = self._socket.recvfrom(23)
		paquete1 = self.parse_segment(binary)

		if not (paquete1.syn == 1 and paquete1.ack == 0 and paquete1.fin == 0):
			raise Exception("socket_tcp: no recibí un SYN")  # noqa: TRY002

		x = paquete1.seq

		# --- Crear nuevo socket dedicado para la conexión ---
		new_socket = SocketTCP()
		if not self._local_address:
			raise Exception(  # noqa: TRY002
				"socket_tcp: ¿aceptando un paquete sin haber hecho bind()?"
			)
		# con puerto 0, el computador asigna un puerto
		new_socket.bind((self._local_address[0], 0))
		new_socket._remote_address = client_address

		# --- Paso 2: Servidor envía SYN-ACK desde el nuevo socket ---
		paquete2 = PaqueteTCP(syn=1, ack=1, seq=x + 1)
		new_socket._socket.sendto(self.create_segment(paquete2), client_address)

		# --- Paso 3: Servidor recibe el ACK final del cliente ---
		binary2, ack_address = new_socket._socket.recvfrom(23)
		paquete3 = self.parse_segment(binary2)

		if not (
			ack_address == client_address
			and paquete3.ack == 1 and paquete3.syn == 0
			and paquete3.fin == 0 and paquete3.seq == x + 2
		):
			raise Exception("socket_tcp: no hubo saludo de manos (etapa 3)")  # noqa: TRY002

		new_socket._seq = paquete3.seq
		print("[STATUS] Servidor conectado con cliente.")
		return new_socket, new_socket._local_address

	def close():
		pass

	def recv_close():
		pass

	# --- Funciones del Stop & Wait

	def send(self, message: bytes):
		length_message = len(message)
		x = 0
		paquete1 = PaqueteTCP(seq=x, body=length_message.to_bytes(4))

	def recv(self, buff_size: int):
		pass
