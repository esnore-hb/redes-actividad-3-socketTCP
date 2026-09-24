import socket

from socket_tcp import SocketTCP


def recieve_file(socket: socket.socket):
	# Se puede hacer lo mismo con un mensaje, con la diferencia de no estar
	# escribiendo lo recibido a un archivo

	pkg_size = 23 # bytes
	data = socket.recvfrom(pkg_size)[0]
	file = open("./recieved.txt", "wb")

	while True:
		# Un paquete vacio es el fin de la comunicación
		if data == b"" : break
		else:
			paquete = SocketTCP.parse_segment(data)
			file.write(paquete.body)
			data = socket.recvfrom(pkg_size)[0]
			print(f"[TRANSFER] Recieving pkg... ({len(data)})")
	file.close()

	print("[STATUS] file recieve")
	socket.close()


def main():
	new_socket_address = ("localhost", 8000)

	print("Se crea socket - Servidor")
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_socket.bind(new_socket_address)

	print("\tEsperando clientes ...")

	recieve_file(server_socket)

if __name__ == "__main__":
	main()