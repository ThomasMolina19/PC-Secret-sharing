#socket: Permite la comunicación entre procesos a través de la red. En este caso, se utiliza para la comunicación entre el servidor y los clientes.
import socket

#threading: Permite ejecutar múltiples tareas (hilos) al mismo tiempo. Así, cada cliente se maneja de forma independiente.
import threading

FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT"

#Función que maneja las conexiones entrantes de los clientes y los mensajes que envían. Para este ejemplo, solo se imprime el mensaje recibido.
def handle_client(conn, addr):

    #Se imprime la dirección del cliente que se ha conectado y esto nos da informacion de la dirección del cliente que se ha conectado.
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")

    #Se crea una variable que indica si el cliente está conectado o no. y recibiremos información del cliente mientras esté conectado. para este ejemplo, se asume que el cliente está conectado. 
    connected = True
    while connected:

        #Se recibe el mensaje del cliente. 1024 es el tamaño del buffer, que es la cantidad de datos que se pueden recibir a la vez. o mejor dicho, la cantidad de datos que se pueden recibir en un solo mensaje. donde HEADER = 64 es el tamaño del mensaje. HEADER son 64 bytes. y decode('utf-8'= FORMAT) es el formato en el que se reciben los datos. 
        msg_length = conn.recv(HEADER).decode(FORMAT)

        if msg_length:

            #msg_length es la longitud del mensaje que se va a recibir. si la longitud del mensaje es 0, significa que el cliente se ha desconectado.
            msg_length = int(msg_length)

            #Se recibe el mensaje del cliente.
            msg = conn.recv(msg_length).decode(FORMAT)
            
            #Si el mensaje recibido es igual al mensaje de desconexión, se cambia el valor de la variable connected a False, lo que indica que el cliente se ha desconectado.
            if msg == DISCONNECT_MESSAGE:
                connected = False
        
            #imprime el mensaje recibido y la dirección del cliente que lo envió.
            print(f"[{addr}] {msg}")
    conn.close() 




#Función que inicia el servidor y se encarga de manejar las conexiones entrantes
def start():
    
    #Se pone el servidor a escuchar las conexiones entrantes. 
    server.listen()

    print(f"[ESCUCHANDO] El servidor está escuchando en {SERVER}")

    #Vamos a escuchar las conexiones entrantes de los clientes de forma indefinida
    while True:
        
        #Se acepta la conexión entrante y se obtiene la dirección del cliente. Asi cuando una nueva conexion es aceptada, se crea un nuevo socket y se obtiene la dirección del cliente.
        conn, addr = server.accept()

        #Se crea un hilo para manejar la conexión entrante. Asi cuando una conexion ocurra, la información de la conexión y la dirección del cliente se pasan a la función handle_client. 
        thread = threading.Thread(target=handle_client, args=(conn, addr))

        #Se inicia el hilo
        thread.start()

        #Se imprime el número de conexiones activas en el servidor. esto nos dice cuantos servidores están conectados al servidor.
        print(f"[CONEXIÓN ACTIVA] {threading.active_count() - 1}")


PORT = 5050

#En este ejemplo se utiliza la dirección IP de la máquina local
#SERVER = "192.168.68.106"

#en esta linea, para no digitar manualmente la ip, se obtiene la ip de la máquina local automaticamente
SERVER = socket.gethostbyname(socket.gethostname())

#si imprimimos server, nos mostrará la ip de la máquina local
#print(SERVER)

#Se crea una tupla con la dirección del servidor y el puerto al que se conectará el cliente 
ADDR = (SERVER, PORT)

#Se crea el socket del servidor, INET es el protocolo de internet, aqui le decimos que busque ipsv4, si fuera ipsv6 se pondría AF_INET6. SOCK_STREAM es el tipo de socket, que es un socket de flujo de datos.  
server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Se enlaza el servidor a la dirección y puerto especificados, asi se le dice al servidor a que dirección y puerto debe escuchar atraves de la tupla ADDR. asi el socket se asocia a la dirección y puerto especificados. que en este caso es la dirección de la máquina local y el puerto 5050.
server.bind(ADDR)

print("[INICIANDO] El servidor está iniciando...")
start()#Se inicia el servidor

