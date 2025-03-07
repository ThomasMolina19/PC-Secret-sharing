import socket as Socket
import ssl

import uuid as UUID
import threading

from socket import socket as Socket, AF_INET, SOCK_STREAM
from field_operations import Field

import Protocol
from NetworkProtocol import RequestConnectionProtocol, AcceptConectionProtocol, MessageProtocol, InputShareProtocol, FinalShareProtocol, ProductShareProtocol, NetworkProtocol, DELIMITADOR, SEPARADOR_IDENTIFICADOR
import Shamirss

import time


DEFAULT_PROTOCOLS: list[type[NetworkProtocol]] = [
    RequestConnectionProtocol,
    AcceptConectionProtocol,
    MessageProtocol,
    InputShareProtocol,
    ProductShareProtocol,
    FinalShareProtocol
]
"""
Protocolos por defecto que se utilizan en la comunicación entre los usuarios.
Tienen que estar en una lista para poder ser utilizados en la función receive.
"""

CERT_FILE = "ssl/cert.pem"
KEY_FILE = "ssl/key.pem"
HOSTNAME = "PC-Crypto"
"""
Constantes para la configuración de la conexión segura.
Estos archivos deben fueron generados con OpenSSL.
"""

class NetworkUser:
    """
    Clase que representa la conexión con otro usuario en la red.
    Almacena la información de la conexión y el UUID del usuario.
    """
    def __init__(self, host: Socket, uuid_str: str = ""):
        self.uuid = uuid_str if uuid_str != "" else str(UUID.uuid4())
        self.host = host
        self.ip, self.port = self.host.getpeername()

    def __eq__(self, value: 'object') -> bool:
        if isinstance(value, NetworkUser):
            return self.uuid == value.uuid or self.host.getpeername() == value.host.getpeername()
        return False

class MainUser:
    """
    Clase principal que representa al usuario principal de la red.
    Se encarga de manejar las conexiones con otros usuarios y de enviar y recibir mensajes.

    Para su inicialización, se requiere la dirección IP y el puerto en el que se va a conectar.
    También se puede especificar un UUID para el usuario, de lo contrario se generará uno aleatorio.

    En su inicialización, se crean los contextos de conexión segura y se inicia el servidor en un hilo aparte.

    Por defecto, el módulo de operaciones es 43112609, que es un número primo de Mersenne.
    """
    def __init__(self, ip: str, port: int, uuid: str | None = None):        
        self.ip: str = ip
        self.port: int = port

        self.mod = 43112609

        self.uuid: str = uuid if uuid else str(UUID.uuid4())

        self.party: dict[str, NetworkUser] = {}

        self.server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.server_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

        self.client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.client_context.load_verify_locations(CERT_FILE)

        self._input_shares: dict[str, Protocol.SharedVariable] = {}
        self.__multiplication_shares: dict[int, list[Protocol.MultiplicationVariable]] = {}
        self.multiplication_results: list[Field] = []
        self.final_shares: list[Protocol.SharedVariable] = []
    
        self.server_thread: threading.Thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

        self.addConnection(self.ip, self.port, self.uuid)

    def start_server(self):
        """
        Inicia el servidor en un hilo aparte.
        Se encarga de aceptar las conexiones entrantes y de manejarlas en hilos aparte.
        """
        self.server = Socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(5)
        self.log(f"Servidor iniciado en {self.ip}:{self.port}")
        while True:
            connection, _ = self.server.accept()
            threading.Thread(target=self.handle_client, args=(connection,), daemon=True).start()

    def handle_client(self, connection: Socket):
        """"
        Maneja las conexiones entrantes.
        Envuelve la conexión en un socket seguro y recibe los mensajes.
        Estos mensajes son almacenados en un buffer hasta que se reciba un delimitador.
        Así, se pueden recibir varios mensajes en un solo paquete y evitar problemas de fragmentación.
        Cada mensaje se envía a la función receive para su procesamiento.
        """
        buffer = ""
        connection = self.server_context.wrap_socket(connection, server_side=True)
        while True:
            try:
                data = connection.recv(1024).decode("utf-8")
                if not data:
                    break
                buffer += data
                while DELIMITADOR in buffer:
                    message, buffer = buffer.split(DELIMITADOR, 1)
                    self.receive(message)
            except Exception as e:
                break
    
    @property
    def t(self) -> int:
        """
        Retorna el número de partes necesarias para reconstruir el secreto.
        Se calcula como (n - 1) // 2, donde n es el número de partes.
        Así, se asegura que t < n/2, para un correcto funcionamiento del protocolo.
        """
        return (len(self.party) - 1) // 2
    
    @property
    def input_shares(self) -> list[Protocol.SharedVariable]:
        """
        Retorna la lista de partes de las variables de entrada.
        Estas partes son las que se envían a los demás usuarios para realizar las operaciones.
        Cada vez que se solicita se ordena para garantizar que todos los usuarios tengan el mismo orden.
        """
        return list(sorted(self._input_shares.values(), key=lambda x: x.sender))
    
    def getMultiplicationShare(self, index: int) -> list[Protocol.MultiplicationVariable]:
        """
        De forma similar a input_shares, retorna las partes de la multiplicación en un índice específico.
        Se ordenan para garantizar que todos los usuarios tengan el mismo orden.
        No se encuentra publico en la API, pero se utiliza internamente y accedible a través de getMultiplicationShare y addMultiplicationShare.
        """
        if not index in self.__multiplication_shares:
            return []
        return list(sorted(self.__multiplication_shares[index], key=lambda x: x.sender))
    
    def addMultiplicationShare(self, share: Protocol.MultiplicationVariable):
        """
        Añade una parte de la multiplicación a la lista de partes.
        Se almacenan en un diccionario con el índice de la operación como clave.
        """
        self.__multiplication_shares.setdefault(share.operation_index, []).append(share)

    def log(self, message: str):
        """
        Imprime un mensaje en la consola con el UUID del usuario.
        """
        print(f"\n[{self.uuid}] {message}")

    def broadcast(self, message: str):
        """"
        Envía un mensaje a todos los usuarios conectados.
        """
        for user in self.party.values():
            protocol = MessageProtocol(self)
            protocol.send_message(user.host, message)

    def connect(self, ip: str, port: int, retries: int = 3, delay: int = 5) -> Socket | None:
        """
        Envia una solicitud de conexión a un usuario en la red.
        Se intenta conectar varias veces antes de fallar.

        Crea un socket y lo envuelve en una conexión segura.
        Se envía un mensaje de solicitud de conexión y se espera una respuesta.
        Si la conexión es exitosa, se retorna el socket seguro.
        Este socket se descarta, ya que es temporal para la conexión.
        """
        secure_connection = None
        attempt = 0
        
        while attempt < retries:
            try:
                connection = Socket(AF_INET, SOCK_STREAM)
                secure_connection = self.client_context.wrap_socket(connection, server_hostname=HOSTNAME)
                secure_connection.connect((ip, port))
                
                protocol = RequestConnectionProtocol(self)
                protocol.send_message(secure_connection)
                
                self.log(f"Enviando solicitud de conexión a {ip}:{port}")
                return secure_connection  # Return on successful connection
            
            except Exception as e:
                if e.args[0] == 10061:
                    self.log(f"No se pudo conectar a {ip}:{port} (Intento {attempt + 1}/{retries}): {str(e)}")
                    attempt += 1
                    if attempt < retries:
                        time.sleep(delay)  # Wait before retrying
                    else:
                        self.log("Se agotaron los intentos de reconexión.")
                        break
                else:
                    self.log(f"Error inesperado al conectar a {ip}:{port}: {str(e)}")
                    break

    def addConnection(self, ip: str, port: int, uuid: str) -> NetworkUser | None:
        """
        Añade un usuario a la lista de conexiones.
        Se crea un socket seguro y se envía un mensaje de aceptación de conexión.
        Se retorna el usuario creado.
        El usuario se almacena en un diccionario con el UUID como clave.
        """
        if uuid in self.party:
            return None
        connection = Socket(AF_INET, SOCK_STREAM)
        secure_connection = self.client_context.wrap_socket(connection, server_hostname=HOSTNAME)
        secure_connection.connect((ip, port))
        user = NetworkUser(secure_connection, uuid)
        self.party[uuid] = user
        self.party = dict(sorted(self.party.items()))
        self.log(f"Conexión establecida con {uuid} | {ip}:{port}")
        acceptProtocol = AcceptConectionProtocol(self)
        acceptProtocol.send_message(user.host)

        return user

    def receive(self, message: str):
        """
        Despues de haberse separado correctamente el mensaje del buffer, se envía a esta función para su procesamiento.
        Se intenta identificar el comando y se envía a la función correspondiente.
        Si no se reconoce el comando, se lanza una excepción, que se captura y se imprime en la consola.
        """
        try:
            comando, contenido = message.split(SEPARADOR_IDENTIFICADOR, 1)
            for protocol in DEFAULT_PROTOCOLS:
                if protocol.identifier() == comando:
                    protocolInstance: NetworkProtocol = protocol(self)
                    protocolInstance.receive_message(contenido)
                    return
            raise Exception("Comando no reconocido")
        except Exception as e:
            self.log(f"Error al recibir mensaje: {e}")

    def send_number(self, numero: int, protocol: type[NetworkProtocol] = InputShareProtocol, *args) -> list[Field]:
        """
        Envia un número a todos los usuarios conectados.

        Se usa Shamir Secret Sharing para dividir el número en partes, y estas son las que se envían.

        Se utiliza el protocolo especificado para enviar la parte correspondiente.
        Por defecto, se utiliza InputShareProtocol.

        Se retorna una lista con las partes generadas por el protocolo.
        """
        shamirss = Shamirss.ShamirSecretSharing(Field(numero, self.mod), len(self.party))
        shares = shamirss.generate_shares(self.t)
        for indice, uuid in enumerate(self.party):
            user  = self.party[uuid]
            share = shares[indice]
            protocol_instance = protocol(self)
            protocol_instance.send_message(user.host, share, *args)
        return shares

    def onReceiveInputShare(self, user: NetworkUser, share: Protocol.SharedVariable):
        """
        Cuando se recibe una parte de una variable de entrada, se almacena en la lista de partes.
        """
        self._input_shares[share.uuid] = share

    def onReceiveProductShare(self, user: NetworkUser, share: Protocol.MultiplicationVariable, operation_index: int):
        """
        Cuando se recibe una parte de una multiplicación, se almacena en la lista de partes.
        Se verifica si se han recibido todas las partes de la multiplicación.

        Si se han recibido todas las partes, se calcula el resultado de la multiplicación y se envía a los demás usuarios.
        Este proceso se repite hasta que se hayan calculado todos los resultados de las multiplicaciones.

        Cuando se han calculado todos los resultados, se envía la parte final a los demás usuarios.
        """
        self.addMultiplicationShare(share)

        shares = self.getMultiplicationShare(operation_index)

        if len(shares) == len(self.party):
            result = Shamirss.ShamirSecretSharing.recuperar_secreto(shares) # type: ignore
            self.multiplication_results.append(result)
            if len(self.multiplication_results) < len(self.input_shares) - 1:
                time.sleep(2.2)
                self.sendOperation(operation_index + 1)
            else:
                time.sleep(2.2)
                self.sendFinalShare(user)
    
    def sendFinalShare(self, user: NetworkUser):
        """
        Envia la parte final de la multiplicación a un usuario específico.
        """
        protocol = FinalShareProtocol(self)
        protocol.send_message(user.host, self.multiplication_results[-1])


    def onReceiveFinalShare(self, user: NetworkUser, share: Protocol.SharedVariable):
        """
        Al recibir la parte final de una multiplicación, se almacena en la lista de partes finales.
        Se verifica si se han recibido todas las partes finales.

        Si esta parte es nueva, se añade a la lista de partes finales y se envía las partes del usuario a los demás.
        """
        if (share in self.final_shares):
            return
        self.final_shares.append(share)
        self.final_shares = list(sorted(self.final_shares, key=lambda x: x.sender))

        self.log(f"Recibida parte final de {user.uuid}")

        for user in self.party.values():
            self.sendFinalShare(user)
        
    def sendOperation(self, index: int = 0):
        """
        Envía la operación de multiplicación a todos los usuarios conectados.
        Se genera la multiplicación correspondiente y se envía a los demás usuarios.
        Se utiliza el índice para identificar la operación.
        Se deben hacer n - 1 operaciones, donde n es el número de partes.
        """
        index = len(self.multiplication_results)
        m = Protocol.Multiplication.generate_next_multiplication(self, self.multiplication_results, self.input_shares, index)
        self.send_number(m.value, ProductShareProtocol, index)


    def reconstruct_secret(self) -> Field:
        """
        Recupera el secreto a partir de las partes finales.
        Se verifica que haya suficientes partes para reconstruir el secreto.
        Utiliza Shamir Secret Sharing (interpolación de Lagrange) para recuperar el secreto.
        """
        if len(self.final_shares) < self.t:
            raise Exception("No hay suficientes partes para reconstruir el secreto.")
        return Shamirss.ShamirSecretSharing.recuperar_secreto(self.final_shares)
    
    def status(self):
        """
        Imprime en la consola el estado actual del usuario.
        Se muestran los usuarios conectados, las partes de las variables de entrada, las operaciones y los resultados.
        """
        print(f"Usuarios conectados: ")
        for user in self.party.values():
            print(f"  - {user.uuid} ({user.ip}:{user.port})")
        print(f"Partes: ")
        for share in self.input_shares:
            print(f"  - {share}")
        print("Operaciones: ")
        for index in range(len(self.__multiplication_shares)):
            print(f"  - Operación #{index}: ", *self.getMultiplicationShare(index))
        print("Resultados: ", *self.multiplication_results)
        print("Final Shares: ", *self.final_shares)