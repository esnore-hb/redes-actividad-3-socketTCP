from socket_tcp import PaqueteTCP, SocketTCP

address = ("localhost", 8000)


def main():
	print("Se crea socket - Cliente")

	# -- seccion crear el socket
	client_socket_tcp = SocketTCP()
	client_socket_tcp.bind(("localhost", 8001))
	client_socket_tcp.connect(address)
	# -- seccion crear el socket

	# --- seccion envio del archivo
	filename = input("Ingrese la ruta del archivo > ")
	with open(filename, "rb") as archivo:
		file = archivo.read()
	file_splitted = [file[i : (i + 16)] for i in range(0, len(file), 16)]
	for block in file_splitted:
		paquete = PaqueteTCP(body=block)
		client_socket_tcp._socket.sendto(
			SocketTCP.create_segment(paquete), client_socket_tcp._remote_address
		)
	# --- seccion envio del archivo

	# Señal provisional de fin del archivo, sin cierre TCP todavía.
	client_socket_tcp._socket.sendto(b"", client_socket_tcp._remote_address)
	print("File sent!")
	client_socket_tcp._socket.close()


if __name__ == "__main__":
	main()
