import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket UDP
SERVER_ADDR = ('127.0.0.1', 8000)

filepath = input("Ingrese ruta del archivo: ") #ruta

with open(filepath, 'rb') as file: # abrir en binario
    while True:
        chunk = file.read(16) #trozo de máximo 16

        if not chunk:#si no hay trozo terminar el bucle
            break

        client_socket.sendto(chunk, SERVER_ADDR)#enviar al servidor

client_socket.sendto(b"", SERVER_ADDR) #cerrar servidor
client_socket.close() #cerrar socket