import socket as Socket
import uuid as UUID
import threading

from socket import socket as Socket, AF_INET, SOCK_STREAM

from field_operations import Field
from Shamirss import ShamirSecretSharing, SecretShare

from Multiplication import SharedVariable, MultiplicationVariable

from NetworkProtocol import *
DEFAULT_PROTOCOLS: list[type[NetworkProtocol]] = [
    RequestConnectionProtocol,
    AcceptConectionProtocol,
    MessageProtocol,
    InputShareProtocol,
    ProductShareProtocol
]

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

    def __init__(self, host: Socket, uuid_str: str = ""):
        # Si no se especifica un UUID, se genera uno aleatorio
        self.uuid = uuid_str if uuid_str != "" else str(UUID.uuid4())

        # Se guarda el socket del usuario
        self.host = host

        self.multiplication_shares: dict[int, MultiplicationVariable] = {}

        # Se guarda la dirección IP y el puerto del usuario
        # getpeername() devuelve la dirección IP y el puerto del usuario al que está conectado el socket
        self.ip, self.port = self.host.getpeername()

    def addMultiplicationShare(self, share: MultiplicationVariable):
        self.multiplication_shares[share.indice] = share

    def __eq__(self, value: 'object') -> bool:
        """
        Son iguales si y solo si tienen el mismo UUID o si tienen la misma dirección IP y puerto
        """

        # Solo son iguales si es un usuario de la red
        if isinstance(value, NetworkUser):
            # Compara el UUID o la dirección IP y puerto
            return self.uuid == value.uuid or self.host.getpeername() == value.host.getpeername()
        return False

class MainUser:
    """
    Clase que representa un usuario principal en la red.
    Se encarga de manejar las conexiones con otros usuarios.
    Requiere un número para funcionar, y se encarga de compartirlo con los demás usuarios y calcular la operación.
    """
    def __init__(self, ip: str, port: int, uuid: str = ""):        
        # Almacena la dirección IP y el puerto del usuario
        self.ip: str = ip
        self.port: int = port

        # Módulo para las operaciones de campo
        self.mod = 43112609

        # Almacena el UUID del usuario, si no se especifica, se genera uno aleatorio
        self.uuid: str = uuid if uuid != "" else str(UUID.uuid4())

        # Crea el diccionario de conexiones con otros usuarios, donde la clave es el UUID del usuario y el valor es el usuario
        self.party: dict[str, NetworkUser] = {}

        self.input_shares: dict[str, SharedVariable] = {}
        self.multiplication_shares: dict[int, list[SecretShare]] = {}
    
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
        self.addConnection(self.ip, self.port, self.uuid)

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
                print("[-] Error al recibir mensaje:", e) # TODO: Handle disconnection
                break
    
    @property
    def t(self) -> int:
        return (len(self.party) - 1) // 2 # Asegura que t < n/2

    def log(self, message: str):
        # Imprime un mensaje con el identificador del usuario para mayor claridad
        print(f"\n[{self.uuid}] {message}")

    def broadcast(self, message: str):
        """
        Envía un mensaje a todos los usuarios conectados.
        """
        # Itera a través de los usuarios en el diccionario de conexiones y envía el mensaje a cada uno
        for user in self.party.values():
            protocol = MessageProtocol(self)
            protocol.send_message(user.host, message)

    def connect(self, ip: str, port: int):
        """
        Envía un mensaje de conexión a la dirección IP y puerto especificados.
        Solo envía un mensaje solicitando conexión, no lo añade a la lista de conexiones.
        """

        connection = None
        try:
            # Crea un socket y se conecta a la dirección IP y puerto especificados
            connection = Socket(AF_INET, SOCK_STREAM)
            connection.connect((ip, port))

            protocol = RequestConnectionProtocol(self)
            protocol.send_message(connection)

            self.log(f"Enviando solicitud de conexión a {ip}:{port}")

        except Exception as e:
            self.log(f"No se pudo conectar a {ip}:{port}:{str(e)}")

        finally:
            if connection:
                connection.close()

    def addConnection(self, ip: str, port: int, uuid: str) -> NetworkUser | None:
        """
        Crea una nueva conexión con un usuario y lo añade a la lista de conexiones.
        Devuelve el usuario creado.
        """

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

        # Ordena el diccionario de conexiones por UUID
        self.party = dict(sorted(self.party.items()))

        self.log(f"Conexión establecida con {uuid} | {ip}:{port}")

        acceptProtocol = AcceptConectionProtocol(self)
        acceptProtocol.send_message(user.host)

        return user

    def receive(self, message: str):
        """
        Recibe un mensaje y lo manda al método adecuado dependiendo del comando.
        """
        try:
            # Divide el mensaje en dos partes, el comando y el contenido del mensaje
            comando, contenido = message.split(SEPARADOR_IDENTIFICADOR, 1)

            for protocol in DEFAULT_PROTOCOLS:
                if protocol.identifier() == comando:
                    protocolInstance: NetworkProtocol = protocol(self)
                    protocolInstance.receive_message(contenido)
                    return
            Exception("Comando no reconocido")
        except Exception as e:
            # Si hay un error al procesar el mensaje, imprime un mensaje de error
            self.log(f"Mensaje con formato invalido ({message}): {e}")
            import traceback
            traceback.print_exc()

    def send_number(self, numero: int, protocol: type[NetworkProtocol] = InputShareProtocol):
        """
        Genera partes del numero y las envía a los usuarios conectados.
        """

        # Genera las partes del número usando Shamir Secret Sharing. Genera dependiendo del número de usuarios conectados
        shamirss = ShamirSecretSharing(Field(numero, self.mod), len(self.party))

        # Genera las partes del número a compartir
        shares = shamirss.generate_shares(self.t)

        # Itera a través de los usuarios ordenados usando enumerate para obtener el índice y el UUID
        for indice, uuid in enumerate(self.party):
            # Obtiene el usuario del diccionario de conexiones
            user  = self.party[uuid]

            # Obtiene el share correspondiente al índice
            share = shares[indice].valor

            # Envía el share al usuario en el formato "PARTE=[UUID];[VALOR];[MODULO]"
            protocol_instance = protocol(self)
            protocol_instance.send_message(user.host, share)
        
        self.log("Shares enviados.")

    def addInputShare(self, user: NetworkUser, share: SharedVariable):
        self.input_shares[share.uuid] = share
        self.input_shares = dict(sorted(self.input_shares.items()))
        self.log(f"Share recibido de {user.uuid}: {share}")

    def handle_multiplication(self, a: SharedVariable, b: SharedVariable, gate_index: int):
        """Multiply two shared values [a] and [b], reshare, and recombine."""
        # Step 1: Local multiplication (degree becomes 2t)
        h_p = a.value * b.value  # Field multiplication

        # Step 2: Reshare h_p with degree t
        shamir = ShamirSecretSharing(h_p, len(self.party))
        reshared_secrets = shamir.generate_shares(self.t)

        # Step 3: Send reshared shares to all parties
        for idx, user_uuid in enumerate(self.party):
            user = self.party[user_uuid]
            share = reshared_secrets[idx]
            variable = MultiplicationVariable(share.valor, self.uuid, gate_index)
            protocol = ProductShareProtocol(self)
            protocol.send_message(user.host, variable)

    def recombination_vector(self, indices: list[int]) -> dict[int, Field]:
        """Compute Lagrange coefficients for indices to reconstruct f(0)."""
        prime = self.mod
        vector = {}
        for idx in indices:
            numerator = Field(1, prime)
            denominator = Field(1, prime)
            for j in indices:
                if idx == j:
                    continue
                numerator *= Field(-j, prime)
                denominator *= Field(idx - j, prime)
            li = numerator * denominator.inverse()
            vector[idx] = li
        return vector
    
    def processProductShare(self, user: NetworkUser, share: MultiplicationVariable):
        user.addMultiplicationShare(share)
        self.log(f"Received product share {share.indice} from {user.uuid}")

        # Check if all shares for this gate are received
        gate_shares = [u.multiplication_shares.get(share.indice, None) for u in self.party.values()]
        if all(gate_shares) and len(gate_shares) > self.t:
            # Reconstruct the recombined share
            indices = list(range(len(self.party)))
            r_vector = self.recombination_vector(indices)
            
            combined = Field(0, self.mod)
            for idx, uuid in enumerate(self.party):
                share_i = self.party[uuid].multiplication_shares[share.indice].value
                combined += share_i * r_vector[idx]
            
            # Store the recombined share for future operations
            new_share = SharedVariable(combined, self.uuid)
            self.input_shares[f"gate_{share.indice}"] = new_share

    def start_computation(self):
        """After all inputs are shared, process multiplication gates."""
        input_vars = list(self.input_shares.values())
        for i in range(len(input_vars) - 1):
            a = input_vars[i]
            b = input_vars[i+1]
            self.handle_multiplication(a, b, gate_index=i)

    def reconstruct_secret(self) -> Field:
        """
        Reconstructs the secret from shares received from all parties.
        Assumes shares for the final result are stored in `input_shares`.
        """
        # Collect shares from all parties
        shares = []
        party_uuids = sorted(self.party.keys())  # Sorted UUIDs of all players
        
        for share_var in self.input_shares.values():
            # Extract sender's UUID and their share value
            sender_uuid = share_var.sender
            value = share_var.value
            
            # Map sender's UUID to their Shamir index (1-based)
            index = party_uuids.index(sender_uuid) + 1
            
            # Create a SecretShare object
            shares.append(SecretShare(index, value))
        
        # Ensure at least t+1 shares are available
        if len(shares) <= self.t:
            raise ValueError(f"Not enough shares (got {len(shares)}, need at least {self.t + 1})")
        
        # Reconstruct the secret using Shamir's method
        return ShamirSecretSharing.recuperar_secreto(shares)