# Importa el socket y los protocolos de red
# AF_INET: Indica que vamos a usar ipv4 (ejm: 127.0.0.1)
# SOCK_STREAM: Indica que vamos a usar TCP
# Renombramos socket a Socket para mayor claridad y comodidad
from socket import AF_INET, SOCK_STREAM, socket as Socket

# Importa threading para manejar múltiples conexiones simultáneas
import threading

# Importa uuid para generar identificadores únicos para los usuarios
import uuid as UUID

# Importa Field para manejar operaciones en un campo finito
from field_operations import Field
from Shamirss import SecretShare, ShamirSecretSharing

# DELIMITADOR: Caracter que se usa para separar mensajes en el buffer, debe ser lo más improbable posible
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
        # Si no se especifica un UUID, se genera uno aleatorio
        self.uuid = uuid_str if uuid_str else str(UUID.uuid4())

        # Se guarda el socket del usuario
        self.host = host

        # Se guarda la dirección IP y el puerto del usuario
        # getpeername() devuelve la dirección IP y el puerto del usuario al que está conectado el socket
        self.ip, self.port = self.host.getpeername()

    def __eq__(self, value):
        """
        Son iguales si y solo si tienen el mismo UUID o si tienen la misma dirección IP y puerto
        """

        # Solo son iguales si es un usuario de la red
        if isinstance(value, NetworkUser):
            # Compara el UUID o la dirección IP y puerto
            return self.uuid == value.uuid or self.host.getpeername() == value.host.getpeername()
        return False

    def send(self, message: str):
        """
        Enviar un mensaje a este usuario
        """
            
        try:
            # Intenta enviar el mensaje al usuario, lo codifica en utf-8 y añade un delimitador al final para separar mensajes
            self.host.send((message + DELIMITADOR).encode("utf-8"))
        except Exception as e:
            print(f"[-] No se pudo enviar el mensaje a {self.uuid}: {e}")

class MainUser():
    """
    Clase que representa un usuario principal en la red.
    Se encarga de manejar las conexiones con otros usuarios.
    Requiere un número para funcionar, y se encarga de compartirlo con los demás usuarios y calcular la operación.

    MENSAJES POR DEFECTO:
    - NUEVO_USUARIO=[UUID];[IP];[PUERTO]: Se usa al conectarse a un nuevo usuario.
    - CONEXION_ESTABLECIDA=[UUID];[IP];[PUERTO]: Se usa para confirmar la conexión.
    - MENSAJE=[MENSAJE]: Se usa para enviar un mensaje de texto al usuario.
    - PARTE=[UUID];[VALOR];[MODULO]: Se usa para enviar una parte del secreto.
    - OPERACION=[UUID];[VALOR];[MODULO]: Se usa para enviar el resultado de una operación.

    Atributos:
    -----------
    numero : Field
        Número a compartir.
    ip : str
        Dirección IP del usuario.
    port : int
        Puerto del usuario.
    uuid : str
        UUID del usuario.
    party : dict[str, NetworkUser]
        Lista de conexiones con otros usuarios.
    partes : list[SecretShare]
        Lista de partes del número compartido.
    operaciones : list[SecretShare]
        Lista de operaciones recibidas.
    server_thread : threading.Thread
        Hilo del servidor del usuario.
    server : socket.socket
        Socket del servidor del usuario.

    Métodos:
    --------
    __init__(numero: Field, ip: str, port: int, uuid: str = None)
        Inicializa el usuario principal con su número, IP, puerto y UUID.

    start_server()
        Inicia el servidor del usuario para aceptar conexiones entrantes.

    handle_client(connection: Socket)
        Maneja los mensajes entrantes de un cliente conectado.

    log(message: str)
        Imprime mensajes de log con el UUID del usuario.

    connect(ip: str, port: int)
        Envía una solicitud de conexión a otro usuario.

    send_number()
        Genera y envía las partes del número secreto a los usuarios conectados.

    send_operation()
        Realiza una operación con las partes recibidas y la envía a los usuarios.

    reconstruct_secret() -> Field
        Reconstruye el secreto a partir de las operaciones recibidas.

    broadcast(message: str)
        Envía un mensaje a todos los usuarios conectados.

    add_connection(ip: str, port: int, uuid: str) -> NetworkUser
        Añade un nuevo usuario a la red.

    handle_new_user(message: str)
        Maneja la solicitud de conexión de un nuevo usuario.

    handle_connection_established(message: str)
        Maneja la confirmación de una conexión establecida.

    handle_message(message: str)
        Procesa un mensaje de texto recibido.

    handle_part(message: str)
        Procesa una parte del secreto recibida.

    handle_operation(message: str)
        Procesa una operación recibida.

    receive(message: str)
        Dirige los mensajes recibidos al método correspondiente.
    """
    def __init__(self, numero: Field, ip: str, port: int, uuid: str = None):
        # Almacena el número del usuario
        self.numero: Field = numero
        
        # Almacena la dirección IP y el puerto del usuario
        self.ip: str = ip
        self.port: int = port

        # Almacena el UUID del usuario, si no se especifica, se genera uno aleatorio
        self.uuid: str = uuid if uuid is not None else str(UUID.uuid4())

        # Crea el diccionario de conexiones con otros usuarios, donde la clave es el UUID del usuario y el valor es el usuario
        self.party: dict[str, NetworkUser] = {}

        # Inicializa las listas de partes y operaciones
        # Las partes son las partes del número compartido, y las operaciones son las operaciones recibidas
        self.partes: list[SecretShare] = []
        self.operaciones: list[SecretShare] = []
    
        # Inicia el servidor del usuario
        # Se inicia en un hilo separado para no bloquear el hilo principal
        self.server_thread: threading.Thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

    def start_server(self):
        """
        Inicia el servidor del usuario.
        """

        # Crea un socket para el servidor y lo enlaza a la dirección IP y puerto del usuario
        # AF_INET indica que vamos a usar ipv4 y SOCK_STREAM indica que vamos a usar TCP
        self.server = Socket(AF_INET, SOCK_STREAM)

        # Enlaza el servidor a la dirección IP y puerto del usuario
        self.server.bind((self.ip, self.port))

        # Escucha por conexiones entrantes con un máximo de 5 conexiones en espera
        self.server.listen(5)

        self.log(f"Servidor iniciado en {self.ip}:{self.port}")

        # El usuario se conecta a si mismo, ya que él también es parte de la red
        self.add_connection(self.ip, self.port, self.uuid)

        # Bucle infinito para aceptar conexiones entrantes
        while True:
            # Acepta una conexión entrante
            connection, _ = self.server.accept()

            # Procesa la conexión en un hilo separado para no bloquear el hilo principal
            threading.Thread(target=self.handle_client, args=(connection,), daemon=True).start()

    def handle_client(self, connection: Socket):
        """
        Maneja un cliente conectado al servidor. Se encarga de recibir los mensajes y almacenarlos en un buffer.
        El buffer es necesario, porque si muchos mensajes llegan al mismo tiempo, se pueden juntar en un solo mensaje y no se procesarían correctamente.
        """

        # Inicializa el buffer, este se va a ir llenando con los mensajes recibidos para procesarlos uno por uno
        buffer = ""
        while True:
            try:
                # Recibe un mensaje del cliente y lo decodifica en utf-8
                data = connection.recv(1024).decode("utf-8")
                if not data:
                    # Cuando no hay más datos, se cierra la conexión
                    break
                
                # Añade los datos al buffer para procesarlos luego
                buffer += data

                while DELIMITADOR in buffer:  # Procesa todos los mensajes en el buffer
                    # Divide el buffer en dos partes, el mensaje y el resto del buffer
                    message, buffer = buffer.split(DELIMITADOR, 1)
                    
                    # Procesa el mensaje
                    self.receive(message)
            except Exception as e:
                print("[-] Error al recibir mensaje:", e)
                break
    
    def log(self, message: str):
        # Imprime un mensaje con el identificador del usuario para mayor claridad
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
            # Crea un socket y se conecta a la dirección IP y puerto especificados
            connection = Socket(AF_INET, SOCK_STREAM)
            connection.connect((ip, port))

            # Envía un mensaje de solicitud de conexión al usuario, y le envía su UUID, dirección IP y puerto
            connection.send(f"NUEVO_USUARIO={str(self.uuid)};{self.ip};{str(self.port)}{DELIMITADOR}".encode("utf-8"))
            self.log(f"Enviando solicitud de conexión a {ip}:{port}")

        except Exception as e:
            self.log(f"No se pudo conectar a {ip}:{port}:{str(e)}")

        finally:
            # Cuando el mensaje se manda, el socket ya no importa, así que se cierra
            connection.close()

    def send_number(self):
        """
        Genera partes del numero y las envía a los usuarios conectados.
        """

        # Genera las partes del número usando Shamir Secret Sharing. Genera dependiendo del número de usuarios conectados
        shamirss = ShamirSecretSharing(self.numero, len(self.party))

        # El número de partes necesarias para reconstruir el secreto
        t = len(self.party) - 1 # Temporal, no sé cómo vamos a manejar esto

        # Genera las partes del número a compartir
        shares = shamirss.generate_shares(t)

        # Python, así cómo ordena números, también puede ordenar strings, por lo que se ordenan los UUIDs
        # para que las partes se envíen en el mismo orden a todos los usuarios
        # Así, dependiendo el orden, cada usuario tiene un índice único
        ordered = sorted(self.party)

        # Itera a través de los usuarios ordenados usando enumerate para obtener el índice y el UUID
        for indice, uuid in enumerate(ordered):
            # Obtiene el usuario del diccionario de conexiones
            user  = self.party[uuid]

            # Obtiene el share correspondiente al índice
            share = shares[indice].valor

            # Envía el share al usuario en el formato "PARTE=[UUID];[VALOR];[MODULO]"
            user.send(f"PARTE={self.uuid};{share.value};{share.mod}")
        
        self.log("Shares enviados.")

    def send_operation(self):
        """
        Envía una operación a los usuarios conectados.
        """

        # De igual forma que send_number, se ordenan los UUIDs para que las operaciones se envíen en el mismo orden a todos los usuarios
        ordered = sorted(self.party)

        # Obtiene los valores de los shares a través de la función map y una función lambda que obtiene el valor de cada share
        values = list(map(lambda share: share.valor, self.partes))

        # Realiza la operación con los valores de los shares
        operation = sum(values) # TODO: Por ahora computa la suma, hasta implementar la multiplicación

        # Itera a través de los usuarios ordenados para enviar la operación a cada uno
        for uuid in ordered:
            # Obtiene el usuario del diccionario de conexiones
            user  = self.party[uuid]

            # Envía la operación al usuario en el formato "OPERACION=[UUID];[VALOR];[MODULO]"
            user.send(f"OPERACION={self.uuid};{operation.value};{operation.mod}")
        
        self.log("Operación enviada.")

    def reconstruct_secret(self) -> Field:
        """
        Reconstruye el secreto a partir de las operaciones recibidas.

        Returns:
        --------
        Field
            El secreto reconstruido.
        """

        t = len(self.party) - 1 # TODO: Cuando se implemente el valor t, se usará aquí
        
        # Revisa si hay suficientes operaciones para reconstruir el secreto
        if len(self.operaciones) < t:
            self.log(f"Se necesitan al menos {t} operaciones para reconstruir el secreto, solo se tienen {len(self.operaciones)}")
            return None

        # Reconstruye el secreto usando Shamir Secret Sharing (lagrange) y las operaciones recibidas
        secret = ShamirSecretSharing.recuperar_secreto(self.operaciones)

        return secret

    def broadcast(self, message: str):
        """
        Envía un mensaje a todos los usuarios conectados.
        """

        # Itera a través de los usuarios en el diccionario de conexiones y envía el mensaje a cada uno
        for user in self.party.values():
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
            El usuario creado, None si esta ya registrado.
        """

        # Este método, realmente es auxiliar, ya que es repetitivo en handle_new_user y handle_connection_established
        # Se encarga de crear la conexión con el nuevo usuario y añadirlo a la lista de conexiones

        # Si el usuario ya está registrado, no se añade
        if uuid in self.party:
                return None

        # Crea un socket y se conecta a la dirección IP y puerto especificados
        connection = Socket(AF_INET, SOCK_STREAM)
        connection.connect((ip, port))

        # Crea un nuevo usuario con la conexión y el UUID
        user = NetworkUser(connection, uuid)

        # Añade el usuario al diccionario de conexiones
        self.party[uuid] = user

        self.log(f"Conexión establecida con {uuid} | {ip}:{port}")

        return user

    # Una pequeña nota para las funciones que siguen: Cada uno se encarga de manejar un tipo de mensaje.
    # Filtrado a través de un diccionario de mensajes por defecto.
    # Se podría implementar en POO, pero preferí un enfonque más funcional para no tener que crear una clase por cada tipo de mensaje

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

        # Cómo el mensaje es en formato [uuid];[ip];[puerto], se divide en tres partes
        uuid, ip, port = message.split(";")

        # Crea la conexión con el nuevo usuario y lo añade a la lista de conexiones
        user = self.add_connection(ip, int(port), uuid)

        if user is None: # Si el usuario ya está registrado, no se envía la información
            return

        # Envía la información de las conexiones actuales al nuevo usuario, para que pueda conectarse a ellos
        for connection in self.party.values():
            # No tiene sentido enviar la información del nuevo usuario a sí mismo
            if connection != user:
                # Envía la información de la conexión en el formato "NUEVO_USUARIO=[UUID];[IP];[PUERTO]"
                user.send(f"NUEVO_USUARIO={connection.uuid};{connection.ip};{connection.port}")

        # Envía un mensaje de confirmación de conexión al nuevo usuario en el formato "CONEXION_ESTABLECIDA=[UUID];[IP];[PUERTO]"
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

        # Cómo el mensaje es en formato [uuid];[ip];[puerto], se divide en tres partes
        uuid, ip, port = message.split(";")

        # Crea la conexión con el nuevo usuario y lo añade a la lista de conexiones
        self.add_connection(ip, int(port), uuid)

    def handle_message(self, message: str):
        """
        Maneja un mensaje de texto recibido.
        """

        # Simplemente imprime el mensaje recibido
        self.log(f"Mensaje recibido: {message}")

    def handle_part(self, message: str):
        """
        Maneja un mensaje de compartición de secreto recibido.
        """

        # Cómo el mensaje es en formato [uuid];[valor];[modulo], se divide en tres partes
        uuid, valor, modulo = message.split(";")

        # Obtiene el usuario del diccionario de conexiones
        user = self.party[uuid]

        # Si el usuario no está registrado, imprime un mensaje de error
        if user is None:
            self.log(f"Usuario desconocido: {uuid}")
            return
        
        # Ordena los UUIDs para que las partes se guarden en el mismo orden en todos los usuarios
        ordered = sorted(self.party)

        # Obtiene el índice del usuario en la lista ordenada
        indice = ordered.index(uuid)

        # Crea un share con el índice + 1 (para que empiece desde 1), y el valor recibido
        share = SecretShare(int(indice + 1), Field(int(valor), int(modulo)))

        # Añade el share a la lista de partes
        self.partes.append(share)

        self.log(f"Recibido share: {share}")

    def handle_operation(self, message: str):
        """
        Maneja un mensaje de operación recibido.
        """

        # Notese la similitud con handle_part, ya que el formato es el mismo

        # Cómo el mensaje es en formato [uuid];[valor];[modulo], se divide en tres partes
        uuid, valor, modulo = message.split(";")

        # Obtiene el usuario del diccionario de conexiones
        user = self.party[uuid]

        # Si el usuario no está registrado, imprime un mensaje de error
        if user is None:
            self.log(f"Usuario desconocido: {uuid}")
            return
        
        # Ordena los UUIDs para que las operaciones se guarden en el mismo orden en todos los usuarios
        ordered = sorted(self.party)

        # Obtiene el índice del usuario en la lista ordenada
        indice = ordered.index(uuid)

        # Crea un share con el índice + 1 (para que empiece desde 1 y así facilitar laggrange), y el valor recibido
        share = SecretShare(int(indice + 1), Field(int(valor), int(modulo)))

        # Añade el share a la lista de operaciones
        self.operaciones.append(share)

        self.log(f"Recibida operación: {share}")

    # Diccionario de mensajes por defecto
    # Cada mensaje tiene un método asociado que se encarga de manejarlo cómo se mencionó anteriormente
    mensajes_por_defecto = {
        "NUEVO_USUARIO": handle_new_user,
        "CONEXION_ESTABLECIDA": handle_connection_established,
        "MENSAJE": handle_message,
        "PARTE": handle_part,
        "OPERACION": handle_operation
    }

    def receive(self, message: str):
        """
        Recibe un mensaje y lo manda al método adecuado dependiendo del comando.
        """

        try:
            # Divide el mensaje en dos partes, el comando y el contenido del mensaje (separa por el primer "=")
            comando, contenido = message.split("=", 1)

            # Si el comando está en el diccionario de mensajes por defecto, se manda al método asociado
            if comando in self.mensajes_por_defecto:
                # Se llama al método asociado con el contenido del mensaje
                self.mensajes_por_defecto[comando](self, contenido)
            else:
                # Si el comando no está en el diccionario, imprime un mensaje de error
                self.log(f"Mensaje con formato invalido ({message}): No existe el comando '{comando}'")
        except Exception as e:
            # Si hay un error al procesar el mensaje, imprime un mensaje de error
            self.log(f"Mensaje con formato invalido ({message}): {e}")

if __name__ == "__main__":
    """
    Prueba de la implementación de Shamir Secret Sharing con conexiones de red.
    Prueba la conexión entre n usuarios, compartiendo un secreto y reconstruyéndolo.
    """
    # Importa time para pausas
    import time
    
    # Función que crea n usuarios con un número aleatorio y los devuelve en una lista
    def create_users(num_users: int, mod: int) -> list[MainUser]:
        # Crea una lista para almacenar los usuarios
        users = []

        # Puerto base para los usuarios (van a estar en puertos consecutivos)
        base_port = 5500

        # Itera para crear los n usuarios
        for i in range(num_users):
            # Crea un usuario con un número aleatorio, en la ip 127.0.0.1 (local), en el puerto base_port + 1, con uuid "user(i+1)" y lo añade a la lista
            users.append(MainUser(Field.random(mod), "127.0.0.1", base_port + i, f"user{i+1}"))

        # Devuelve la lista de usuarios
        return users

    # Función que conecta a los usuarios entre sí
    def connect_users(users: list[MainUser]):
        # Conecta a todos los usuarios al primero y por cómo funciona la red, todos los usuarios se conectan entre sí
        for i in range(1, len(users)):
            # Conecta al usuario i al usuario 0 (todos con el primero)
            users[i].connect("127.0.0.1", users[0].port)

            # Pequeña pausa para evitar colisiones
            time.sleep(2)

    # Verifica que todos los usuarios están conectados entre sí
    def test_connections(users: list[MainUser]):
        # Iteramos a través de los usuarios
        for i in range(1, len(users)):
            # Verificamos que el usuario i esté conectado al usuario 0
            assert users[i].uuid in users[0].party, f"{users[i].uuid} no conectado a {users[0].uuid}"

            # Verificamos que el usuario 0 esté conectado al usuario i
            assert users[0].uuid in users[i].party, f"{users[0].uuid} no conectado a {users[i].uuid}"

        # Todos los usuarios están conectados entre sí
        print("Prueba de conexiones exitosa.")

    # Función que envía los shares a los usuarios
    def send_shares(users: list[MainUser]):
        # Itera a través de los usuarios para enviar los shares
        for user in users:
            user.send_number() # Envía el número a compartir
            time.sleep(2) # Pequeña pausa para evitar colisiones

    # Función que envía las operaciones a los usuarios
    def send_operations(users: list[MainUser]):
        # Itera a través de los usuarios para enviar las operaciones
        for user in users:
            user.send_operation() # Envía la operación
            time.sleep(2) # Pequeña pausa para evitar colisiones

    # Función que prueba la reconstrucción del secreto
    def test_reconstruct(users: list[MainUser]):
        # Obtiene el secreto real sumando los números de los usuarios
        # Cuando se tenga la multiplicación lista, se cambiará a multiplicar
        # Este es el valor que se espera reconstruir
        real_secret = sum(user.numero for user in users)

        # Itera a través de los usuarios para reconstruir el secreto
        for user in users:
            # Reconstruye el secreto del usuario
            reconstructed = user.reconstruct_secret()

            # Verifica que el secreto reconstruido sea igual al secreto real
            assert reconstructed == real_secret, f"Secreto reconstruido incorrecto: {reconstructed} != {real_secret}"
        
        # Todos los secretos se reconstruyeron correctamente
        print("Prueba de shares exitosa.")

    # Pide al usuario el número de usuarios a crear
    num_users = int(input("Ingrese el número de usuarios a crear: "))

    # Primo de Mersenne 47
    primo = 43112609

    # Crea n usuarios con un número aleatorio y los almacena en una lista
    users: list[MainUser] = create_users(num_users, primo)

    # Conecta a los usuarios entre sí
    connect_users(users)

    # Verifica que todos los usuarios están conectados entre sí
    test_connections(users)

    # Comparte el secreto entre los usuarios
    print("Compartiendo secreto...")
    send_shares(users)

    # Comparte las operaciones entre los usuarios
    print("Compartiendo operaciones...")
    send_operations(users)

    # Imprime los usuarios y sus partes y operaciones para verificar
    for user in users:
        print()
        print(f"{user.uuid}\nNúmero: {user.numero}\nPartes:", *user.partes, "\nOperaciones:", *user.operaciones)

    # Prueba la reconstrucción del secreto
    test_reconstruct(users)