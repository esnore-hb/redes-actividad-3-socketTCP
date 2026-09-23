import socket
import sys

import socket_tcp

address = ("localhost", 8000)


def send_file(socket: socket.socket, file: str):

	file_splitted = [file[i : (i + 16)] for i in range(0, len(file), 16)]
	print(file_splitted)
	for block in file_splitted:
		print(block)
		socket.sendto(f"{block}".encode(), address)

	# Cerrar conexion
	socket.sendto(b"", address)
	print("File sent!")


def main():
	file = sys.stdin.read()

	print("Se crea socket - Cliente")

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	send_file(client_socket, file)
	client_socket.close()



if __name__ == "__main__":
	main()
