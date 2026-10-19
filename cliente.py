import sys

from socket_tcp import SocketTCP


def main():
	address = (sys.argv[1], int(sys.argv[2]))
	file = sys.stdin.buffer.read()

	print("Se crea socket - Cliente")

	# -- seccion crear el socket
	client_socket_tcp = SocketTCP()
	client_socket_tcp.debug = "--debug" in sys.argv[3:]
	client_socket_tcp.bind(("localhost", 8001))
	client_socket_tcp.connect(address)
	# -- seccion crear el socket

	# --- seccion envio del archivo
	client_socket_tcp.send(file)
	# --- seccion envio del archivo

	client_socket_tcp.close()
	print("File sent!")


if __name__ == "__main__":
	main()
