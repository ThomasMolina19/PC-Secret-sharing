#socket: Permite la comunicación entre procesos a través de la red. En este caso, se utiliza para la comunicación entre el servidor y los clientes.
import socket

#threading: Permite ejecutar múltiples tareas (hilos) al mismo tiempo. Así, cada cliente se maneja de forma independiente.
import threading

PORT=  5050
FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

#Se crea un socket para la conexión con el servidor. AF_INET indica que se utilizará IPv4 y SOCK_STREAM indica que se utilizará TCP.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Se conecta el cliente al servidor. Se utiliza la dirección IP del servidor y el puerto en el que el servidor está escuchando.
client.connect(ADDR)
