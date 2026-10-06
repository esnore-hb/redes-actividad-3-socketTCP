	# Tab indentation
import socket


def recieve_file(socket: socket.socket):
	# Recibe el contenido enviado por el cliente y lo imprime.

	pkg_size = 4 # bytes

	data = socket.recvfrom(pkg_size)[0]

	contenido = b""
	while True:
		# Un paquete vacio es el fin de la comunicación
		if data == b"" : break
		else:
			contenido += data
			data = socket.recvfrom(pkg_size)[0]
	print(contenido.decode("utf-8"))

	print("[STATUS] file recieve")
	socket.close()


if __name__ == "__main__":
	end_of_message = "\n"
	new_socket_address = ("localhost", 5000)

	print("Se crea socket - Servidor")

	# -- Setup --
	# SOCK_DGRAM por no orientado a conexión
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_socket.bind(new_socket_address)

	print("\tEsperando clientes ...")

	recieve_file(server_socket)
