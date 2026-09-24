import socket
import sys

import socket_tcp

address = ("localhost", 8000)

def main():
	file = sys.stdin.read()

	print("Se crea socket - Cliente")

	# --- seccion envio del archivo
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	file_splitted = [file[i : (i + 16)] for i in range(0, len(file), 16)]
	print(file_splitted)
	for block in file_splitted:
		print(block)
		client_socket.sendto(f"{block}".encode(), address)
	# --- seccion envio del archivo

	# Cerrar conexion
	client_socket.sendto(b"", address)
	print("File sent!")
	client_socket.close()



if __name__ == "__main__":
	main()
