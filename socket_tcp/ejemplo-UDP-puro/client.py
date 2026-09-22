	# Tab indentation
import socket

address = ("localhost", 5000)

def send_file(socket: socket.socket, filename: str):
	file = open(filename, "rb")

	data = file.read(4)
	while data:
		socket.sendto(data, address)
		data = file.read(4)
		print("Sending ...")

	# cerrando archivo, y paquete vacio para cerrar comunicación
	file.close()
	socket.sendto(b"", address)

	print("File sent!")


print("Se crea socket - Cliente")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# -- Para enviar mensajes comunes
# message = input("Ingrese mensaje > ") + "\n"
# client_socket.sendto(message.encode(), address)

send_file(client_socket, "./src/ejemplo-UDP-puro/lorem-ipsum.txt")

# -- Para recibir el echo del server
# message = client_socket.recvfrom(4)

# print("Mensaje recibido: ", message[0].decode())

client_socket.close()
