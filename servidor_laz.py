import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('127.0.0.1', 8000))

print("Servidor UDP esperando trozos...")

while True:
    data, addr = server_socket.recvfrom(1024)

    if not data:
        print("Fin de transmisión recibido.")
        break

    print(f"Recibido ({len(data)} bytes): {data}")