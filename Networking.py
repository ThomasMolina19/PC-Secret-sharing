from socket import AF_INET, SOCK_STREAM, socket as Socket
import threading
import uuid as UUID

from field_operations import Field
from Shamirss import SecretShare, ShamirSecretSharing

DELIMITADOR = "||"

class NetworkUser:
    """
        Clase que representa un usuario de la red.

        Atributos:
        -----------
        host : socket.socket
            Socket del usuario.
        uuid : str
            Identificador único del usuario. Por defecto, un UUID aleatorio.
        ip : str
            Dirección IP del usuario.
        port : int
            Puerto del usuario.
        
        Métodos:
        --------
        __eq__(value: NetworkUser) -> bool:
            Determina si dos usuarios son iguales.

        send(message: str):
            Envía un mensaje a este usuario.
    """

    def __init__(self, host: Socket, uuid_str: str = None):
        self.uuid = uuid_str if uuid_str else str(UUID.uuid4())
        self.host = host
        self.ip, self.port = self.host.getpeername()

    def __eq__(self, value):
        """
        Son iguales si y solo si tienen el mismo UUID o si tienen la misma dirección IP y puerto
        """

        if isinstance(value, NetworkUser):
            return self.uuid == value.uuid or self.host.getpeername() == value.host.getpeername()
        return False

    def send(self, message: str):
        """
        Enviar un mensaje a este usuario
        """
            
        try:
            self.host.send((message + DELIMITADOR).encode("utf-8")) # Notese el delimitador al final, para poder separar mensajes en el buffer
        except Exception as e:
            print(f"[-] No se pudo enviar el mensaje a {self.uuid}: {e}")

class MainUser():
    """
    Clase que representa un usuario principal en la red.
    Esta diseñada para ser unica por cada usuario, y se encarga de manejar las conexiones con otros usuarios.
    Requiere un secreto compartido para funcionar, y se encarga de compartirlo con los demás usuarios.

    MENSAJES POR DEFECTO:
    - NUEVO_USUARIO=[UUID];[IP];[PUERTO]: Se usa al conectarse a un nuevo usuario.
    - CONEXION_ESTABLECIDA=[UUID];[IP];[PUERTO]: Se usa para confirmar la conexión.
    - MENSAJE=[MENSAJE]: Se usa para enviar un mensaje de texto al usuario.
    - SHARE=[INDICE];[VALOR];[MODULO]: Se usa para compartir un secreto.

    Atributos:
    -----------
    secret : SecretShare
        El secreto compartido por este usuario.
    shares : list[SecretShare]
        Lista de shares recibidos por este usuario.
    ip : str
        Dirección IP del servidor.
    port : int
        Puerto del servidor.
    uuid : str
        Identificador único del usuario. Por defecto, un UUID aleatorio.
    party : list[NetworkUser]
        Lista de usuarios conectados a este usuario.
    server : socket.socket
        Socket del servidor.
    server_thread : threading.Thread
        Hilo del servidor.

    Métodos:
    --------
    start_server():
        Inicia el servidor del usuario.
    handle_client(connection: socket.socket):
        Maneja un cliente conectado al servidor.
    log(message: str):
        Imprime un mensaje con el identificador del usuario.
    connect(ip: str, port: int):
        Conecta a un usuario con la dirección IP y puerto especificados.
    send_shares():
        Envía el secreto compartido a todos los usuarios conectados.
    reconstruct_secret() -> Field:
        Reconstruye el secreto a partir de los shares recibidos.
    add_connection(ip: str, port: int, uuid: str) -> NetworkUser:
        Crea una nueva conexión con un usuario y lo añade a la lista de conexiones.
    handle_new_user(message: str):
        Maneja un mensaje de nuevo usuario.
    handle_connection_established(message: str):
        Maneja un mensaje de conexión establecida.
    handle_message(message: str):
        Maneja un mensaje de texto.
    handle_share(message: str):
        Maneja un mensaje de compartición de secreto.
    receive(message: str):
        Recibe un mensaje y lo manda al método adecuado dependiendo del comando.
    """
    def __init__(self, secret: SecretShare, ip: str, port: int, uuid: str = None):
        self.secret: SecretShare = secret
        self.shares: list[SecretShare] = [secret]
        
        self.ip: str = ip
        self.port: int = port
        self.uuid: str = uuid if uuid is not None else str(UUID.uuid4())

        self.party: list[NetworkUser] = []
    
        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

    def start_server(self):
        """
        Inicia el servidor del usuario.
        """
        self.server = Socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(5)
        self.log(f"Servidor iniciado en {self.ip}:{self.port}")

        while True:
            connection, address = self.server.accept()
            threading.Thread(target=self.handle_client, args=(connection,), daemon=True).start()

    def handle_client(self, connection: Socket):
        """
        Maneja un cliente conectado al servidor. Se encarga de recibir los mensajes y almacenarlos en un buffer.
        El buffer es necesario, porque si muchos mensajes llegan al mismo tiempo, se pueden juntar en un solo mensaje y no se procesarían correctamente.
        """
        buffer = ""
        while True:
            try:
                data = connection.recv(1024).decode("utf-8")
                if not data:
                    break

                buffer += data

                while DELIMITADOR in buffer:  # Procesa todos los mensajes en el buffer
                    message, buffer = buffer.split(DELIMITADOR, 1)
                    self.receive(message)
            except Exception as e:
                print(f"[-] Error al recibir mensaje: {e}")
                break
    
    def log(self, message: str):
        print(f"\n[{self.uuid}] {message}")

    def connect(self, ip: str, port: int):
        """
        Envía un mensaje de conexión a la dirección IP y puerto especificados.
        Solo envía un mensaje solicitando conexión, no lo añade a la lista de conexiones.
        
        Parámetros:
        -----------
        ip : str
            Dirección IP del usuario a conectar.
        port : int
            Puerto del usuario a conectar
        """

        try:
            connection = Socket(AF_INET, SOCK_STREAM)
            connection.connect((ip, port))

            connection.send(f"NUEVO_USUARIO={str(self.uuid)};{self.ip};{str(self.port)}{DELIMITADOR}".encode("utf-8"))
            self.log(f"Enviando solicitud de conexión a {ip}:{port}")

        except Exception as e:
            self.log(f"No se pudo conectar a {ip}:{port}:{str(e)}")

        finally:
            connection.close()

    def send_shares(self):
        """
        Envía el secreto compartido a todos los usuarios conectados.
        """

        for user in self.party:
            user.send(f"SHARE={str(self.secret.indice)};{str(self.secret.valor.value)};{str(self.secret.valor.mod)}")
            self.log(f"Compartiendo secreto con {user.uuid}")

    def reconstruct_secret(self) -> Field:
        """
        Reconstruye el secreto a partir de los shares recibidos.

        Returns:
        --------
        Field
            El secreto reconstruido.
        """

        secret = ShamirSecretSharing.recuperar_secreto(self.shares)
        return secret

    def broadcast(self, message: str):
        """
        Envía un mensaje a todos los usuarios conectados.
        """

        for user in self.party:
            user.send(f"MENSAJE={message}")

    def add_connection(self, ip: str, port: int, uuid: str) -> NetworkUser:
        """
        Crea una nueva conexión con un usuario y lo añade a la lista de conexiones.
        Devuelve el usuario creado.

        Parámetros:
        -----------
        ip : str
            Dirección IP del usuario a conectar.
        port : int
            Puerto del usuario a conectar.
        uuid : str
            UUID del usuario a conectar.

        Returns:
        --------
        NetworkUser
            El usuario creado, None si es el mismo, o si esta ya registrado.
        """

        if uuid is self.uuid: # Previene la conexión consigo mismo
            return None
        
        for user in self.party:
            if user.uuid == uuid:
                return None # Evita duplicados

        connection = Socket(AF_INET, SOCK_STREAM)
        connection.connect((ip, port))

        user = NetworkUser(connection, uuid)
        self.party.append(user)

        self.log(f"Conexión establecida con {uuid} | {ip}:{port}")

        return user


    def handle_new_user(self, message: str):
        """
        Cuando un peer desea conectarse a este usuario, recibe el mensaje NUEVO_USUARIO que contiene el uuid, ip y puerto del servidor del nuevo usuario.
        Este método se encarga de crear la conexion con el nuevo usuario y enviarle la información de las conexiones actuales, para que el nuevo usuario pueda conectarse a ellos.
        Al final, envía un mensaje de confirmación de conexión al nuevo usuario.

        Parámetros:
        -----------
        message : str
            El mensaje en formato [uuid];[ip];[puerto]
        """

        uuid, ip, port = message.split(";")
        user = self.add_connection(ip, int(port), uuid)

        if user is None: # Si el usuario ya está registrado o es el mismo, no se envía la información
            return

        for connection in self.party:
            if connection != user:
                user.send(f"NUEVO_USUARIO={connection.uuid};{connection.ip};{connection.port}")

        user.send(f"CONEXION_ESTABLECIDA={self.uuid};{self.ip};{str(self.port)}")

    def handle_connection_established(self, message: str):
        """
        Cuando el nuevo usuario acepta la conexión, envía un mensaje de confirmación de conexión al usuario que lo solicitó.
        Este método, se encarga de tomar la información de la confirmación y guardarla en la lista de conexiones.

        Parámetros:
        -----------
        message : str
            El mensaje en formato [uuid];[ip];[puerto]
        """

        uuid, ip, port = message.split(";")

        self.add_connection(ip, int(port), uuid)

    def handle_message(self, message: str):
        """
        Maneja un mensaje de texto recibido.
        """

        self.log(f"Mensaje recibido: {message}")

    def handle_share(self, message: str):
        """
        Maneja un mensaje de compartición de secreto recibido.
        """

        indice, valor, modulo = message.split(";")
        share = SecretShare(int(indice), Field(int(valor), int(modulo)))
        self.shares.append(share)
        self.log(f"Recibido share: {share}")

    # Diccionario de mensajes por defecto
    mensajes_por_defecto = {
        "NUEVO_USUARIO": handle_new_user,
        "CONEXION_ESTABLECIDA": handle_connection_established,
        "MENSAJE": handle_message,
        "SHARE": handle_share
    }

    def receive(self, message: str):
        """
        Recibe un mensaje y lo manda al método adecuado dependiendo del comando.
        """

        try:
            comando, contenido = message.split("=", 1)
            if comando in self.mensajes_por_defecto:
                self.mensajes_por_defecto[comando](self, contenido)
            else:
                self.log(f"Mensaje con formato invalido: {comando}")
        except Exception as e:
            self.log(f"Mensaje con formato invalido: {e}")

if __name__ == "__main__":
    """
    Prueba de la implementación de Shamir Secret Sharing con conexiones de red.
    Prueba la conexión entre n usuarios, compartiendo un secreto y reconstruyéndolo.
    """
    import time

    def create_users(num_users: int, shares: list[SecretShare]):
        users = []
        base_port = 5000
        for i in range(num_users):
            users.append(MainUser(shares[i], "127.0.0.1", base_port + i, f"user{i+1}"))
        return users

    def connect_users(users: list[MainUser]):
        for i in range(1, len(users)):
            users[i].connect("127.0.0.1", users[0].port)
            time.sleep(1)  # Pequeña pausa para evitar colisiones

    def test_connections(users: list[MainUser]):
        # Verifica que todos los usuarios (excepto el primero) están conectados al primero
        for i in range(1, len(users)):
            assert any(conn.uuid == users[i].uuid for conn in users[0].party), f"{users[i].uuid} no conectado a {users[0].uuid}"
            assert any(conn.uuid == users[0].uuid for conn in users[i].party), f"{users[0].uuid} no conectado a {users[i].uuid}"
        print("Prueba de conexiones exitosa.")

    def send_shares(users: list[MainUser]):
        for user in users:
            user.send_shares()
            time.sleep(1) # Pequeña pausa para evitar colisiones

    def test_shares(users: list[MainUser], secret: Field):
        for user in users:
            assert len(user.shares) == len(users), f"El usuario {user.uuid} no recibió todos los shares."
            assert user.reconstruct_secret() == secret, f"El usuario {user.uuid} no reconstruyó el secreto correctamente."
            
        print("Prueba de shares exitosa.")

    num_users = int(input("Ingrese el número de usuarios a crear: "))
    primo = 43112609 # #47 primo de Mersenne
    t = int(num_users - 1) # El número mínimo de partes necesarias para reconstruir el secreto
    secret = Field.random(primo) # Genera un secreto aleatorio
    shares = ShamirSecretSharing(secret, num_users).generate_shares(t)
    print("Shares generados: ", shares)

    users = create_users(num_users, shares)

    connect_users(users)
    test_connections(users)
    send_shares(users)
    test_shares(users, secret)
