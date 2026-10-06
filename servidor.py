import socket

from socket_tcp import SocketTCP


def recieve_file(socket: socket.socket):
	# Extrae los datos de cada segmento y reconstruye el contenido.

	pkg_size = 23 # bytes
	data = socket.recvfrom(pkg_size)[0]
	contenido = b""

	while True:
		# Un paquete vacio es el fin de la comunicación
		if data == b"" : break
		else:
			paquete = SocketTCP.parse_segment(data)
			contenido += paquete.body
			data = socket.recvfrom(pkg_size)[0]
	print(contenido.decode("utf-8"))

	print("[STATUS] file recieve")
	socket.close()


def main():
	new_socket_address = ("localhost", 8000)

	print("Se crea socket - Servidor")

	# --- seccion crear el socket
	server_socket_tcp = SocketTCP()
	server_socket_tcp.bind(new_socket_address)
	connection_socket_tcp, new_address = server_socket_tcp.accept()
	# --- seccion crear el socket

	recieve_file(connection_socket_tcp._socket)
	server_socket_tcp._socket.close()

if __name__ == "__main__":
	main()
