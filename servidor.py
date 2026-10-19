from socket_tcp import SocketTCP


def recieve_file(connection: SocketTCP):
	# recv() reconstruye los datos y procesa el FIN mediante recv_close().
	contenido = b""
	while True:
		data = connection.recv(16)
		if data == b"":
			break
		contenido += data
	print(contenido.decode("utf-8"))

	print("[STATUS] file recieve")


def main():
	new_socket_address = ("localhost", 8000)

	print("Se crea socket - Servidor")

	# --- seccion crear el socket
	server_socket_tcp = SocketTCP()
	server_socket_tcp.bind(new_socket_address)
	connection_socket_tcp, new_address = server_socket_tcp.accept()
	# --- seccion crear el socket

	recieve_file(connection_socket_tcp)
	server_socket_tcp._socket.close()

if __name__ == "__main__":
	main()
