import random
import socket
import time


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

		self._recv_buffer = b""
		self._recv_remaining = 0
		self._recv_seq = -1
		self._handshake_seq = None
		self._pending_segment = None

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
		x = random.randint(0, 100)
		syn = self.create_segment(PaqueteTCP(syn=1, seq=x))
		previous_timeout = self._socket.gettimeout()
		self._socket.settimeout(0.01)
		try:
			while True:
				self._socket.sendto(syn, address)
				try:
					binary, server_address = self._socket.recvfrom(23)
					response = self.parse_segment(binary)
					if (response.syn == 1 and response.ack == 1
						and response.fin == 0 and response.seq == x + 1):
						break
				except socket.timeout:
					continue
			self._remote_address = server_address
			self._handshake_seq = x + 2
			ack = PaqueteTCP(ack=1, seq=self._handshake_seq)
			self._socket.sendto(self.create_segment(ack), server_address)
			self._seq = self._handshake_seq
		finally:
			self._socket.settimeout(previous_timeout)

	def accept(self):
		# Espera el SYN inicial; el cliente lo retransmite si se pierde.
		while True:
			binary, client_address = self._socket.recvfrom(23)
			request = self.parse_segment(binary)
			if request.syn == 1 and request.ack == 0 and request.fin == 0:
				break
		x = request.seq
		new_socket = SocketTCP()
		new_socket.bind((self._local_address[0], 0))
		new_socket._remote_address = client_address
		response = self.create_segment(PaqueteTCP(syn=1, ack=1, seq=x + 1))
		previous_timeout = new_socket._socket.gettimeout()
		new_socket._socket.settimeout(0.01)
		try:
			while True:
				new_socket._socket.sendto(response, client_address)
				try:
					binary, address = new_socket._socket.recvfrom(23)
					packet = self.parse_segment(binary)
					if address != client_address or packet.seq != x + 2:
						continue
					if packet.syn != 0 or packet.fin != 0:
						continue
					if packet.ack == 1:
						break
					# La longitud tambi?n confirma la conexi?n si se perdi? el ACK.
					if packet.ack == 0 and len(packet.body) == 4:
						new_socket._pending_segment = (binary, address)
						break
				except socket.timeout:
					continue
		finally:
			new_socket._socket.settimeout(previous_timeout)
		new_socket._seq = x + 2
		print("[STATUS] Servidor conectado con cliente.")
		return new_socket, new_socket._local_address

	def close(self):
		x = self._seq
		fin = self.create_segment(PaqueteTCP(fin=1, seq=x))
		self._socket.settimeout(0.01)
		try:
			for attempt in range(3):
				self._socket.sendto(fin, self._remote_address)
				try:
					while True:
						binary, address = self._socket.recvfrom(23)
						response = self.parse_segment(binary)
						if (address == self._remote_address
							and response.fin == 1 and response.ack == 1
							and response.syn == 0 and response.seq == x + 1):
							break
				except socket.timeout:
					continue
				ack = self.create_segment(PaqueteTCP(ack=1, seq=x + 2))
				self._socket.sendto(ack, self._remote_address)
				# Tres reenv?os del ACK final, separados por un timeout.
				for repeat in range(3):
					time.sleep(0.01)
					self._socket.sendto(ack, self._remote_address)
				break
		finally:
			# Tambi?n libera el socket si se cumplen los tres timeouts.
			self._socket.close()

	def recv_close(self, fin=None):
		# Puede recibir el FIN directamente o desde recv().
		if fin is None:
			while True:
				binary, address = self._socket.recvfrom(23)
				packet = self.parse_segment(binary)
				if address != self._remote_address:
					continue
				if packet.fin == 1 and packet.ack == 0 and packet.syn == 0:
					fin = packet
					break
				if (packet.fin == 0 and packet.ack == 0
					and packet.syn == 0 and packet.seq == self._recv_seq):
					ack = PaqueteTCP(ack=1, seq=packet.seq)
					self._socket.sendto(self.create_segment(ack), address)

		x = fin.seq
		response = self.create_segment(PaqueteTCP(fin=1, ack=1, seq=x + 1))
		self._socket.settimeout(0.01)
		try:
			self._socket.sendto(response, self._remote_address)
			timeouts = 0
			while timeouts < 3:
				try:
					binary, address = self._socket.recvfrom(23)
					ack = self.parse_segment(binary)
					if address != self._remote_address:
						continue
					if (ack.ack == 1 and ack.fin == 0 and ack.syn == 0
						and ack.seq == x + 2):
						break
					# Si se perdi? FIN-ACK, el emisor vuelve a enviar FIN.
					if ack.fin == 1 and ack.ack == 0 and ack.syn == 0 and ack.seq == x:
						self._socket.sendto(response, address)
				except socket.timeout:
					timeouts += 1
		finally:
			self._socket.close()

	# --- Funciones del Stop & Wait

	def send(self, message: bytes):
		length_message = len(message)
		x = self._seq
		blocks = [length_message.to_bytes(4)]
		blocks += [message[i:i + 16] for i in range(0, length_message, 16)]
		previous_timeout = self._socket.gettimeout()
		self._socket.settimeout(0.01)
		try:
			for block in blocks:
				segment = self.create_segment(PaqueteTCP(seq=x, body=block))
				while True:
					self._socket.sendto(segment, self._remote_address)
					try:
						binary, address = self._socket.recvfrom(23)
						ack = self.parse_segment(binary)
						# SYN-ACK repetido: el servidor no recibi? el ACK final.
						if (address == self._remote_address and ack.syn == 1
							and ack.ack == 1 and ack.fin == 0
							and ack.seq == self._handshake_seq - 1):
							final_ack = PaqueteTCP(ack=1, seq=self._handshake_seq)
							self._socket.sendto(self.create_segment(final_ack), address)
							continue
						if address == self._remote_address and ack.ack == 1 and ack.seq == x:
							break
					except socket.timeout:
						continue
				x += 1
				self._seq = x
		finally:
			self._socket.settimeout(previous_timeout)

	def recv(self, buff_size: int) -> bytes:
		# primer mensaje es el largo del mensaje
		if self._recv_remaining == 0 and not self._recv_buffer:
			while True:
				if self._pending_segment is not None:
					binary, address = self._pending_segment
					self._pending_segment = None
				else:
					binary, address = self._socket.recvfrom(23)
				paquete = SocketTCP.parse_segment(binary)
				if address == self._remote_address and paquete.fin == 1 and paquete.ack == 0:
					self.recv_close(paquete)
					return b""
				if paquete.ack == 1 or paquete.syn == 1:
					continue
				ack = PaqueteTCP(ack=1, seq=paquete.seq)
				self._socket.sendto(SocketTCP.create_segment(ack), address)

				if paquete.seq != self._recv_seq:
					break
			self._recv_remaining = int.from_bytes(paquete.body)
			self._recv_seq = paquete.seq

		while len(self._recv_buffer) < buff_size and self._recv_remaining > 0:
			binary, address = self._socket.recvfrom(23)
			paquete = SocketTCP.parse_segment(binary)
			if address == self._remote_address and paquete.fin == 1 and paquete.ack == 0:
				self.recv_close(paquete)
				break
			if paquete.ack == 1 or paquete.syn == 1:
				continue

			# paquete duplicado. nuestro ACK se perdió
			if paquete.seq == self._recv_seq:
				ack = PaqueteTCP(ack=1, seq=paquete.seq)
				self._socket.sendto(SocketTCP.create_segment(ack), address)
				continue

			# paquete fuera de orden
			if paquete.seq != self._recv_seq + 1:
				continue

			self._recv_buffer += paquete.body
			self._recv_remaining -= len(paquete.body)
			self._recv_seq = paquete.seq

			ack = PaqueteTCP(ack=1, seq=self._recv_seq)
			self._socket.sendto(SocketTCP.create_segment(ack), address)

		# se devuelve a lo mas buff_size, y se guarda el resto,
		# para la siguiente llamada a recv()
		data = self._recv_buffer[:buff_size]
		self._recv_buffer = self._recv_buffer[buff_size:]
		return data

