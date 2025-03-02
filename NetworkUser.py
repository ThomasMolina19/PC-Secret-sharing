import socket as Socket
import ssl

import uuid as UUID
import threading

from socket import socket as Socket, AF_INET, SOCK_STREAM
from field_operations import Field

import Protocol
from NetworkProtocol import ShareProtocol, RequestConnectionProtocol, AcceptConectionProtocol, MessageProtocol, InputShareProtocol, FinalShareProtocol, ProductShareProtocol, NetworkProtocol, DELIMITADOR, SEPARADOR_IDENTIFICADOR
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

CERT_FILE = "ssl/cert.pem"
KEY_FILE = "ssl/key.pem"
HOSTNAME = "PC-Crypto"

class NetworkUser:
    def __init__(self, host: Socket, uuid_str: str = ""):
        self.uuid = uuid_str if uuid_str != "" else str(UUID.uuid4())
        self.host = host
        self.ip, self.port = self.host.getpeername()

    def __eq__(self, value: 'object') -> bool:
        if isinstance(value, NetworkUser):
            return self.uuid == value.uuid or self.host.getpeername() == value.host.getpeername()
        return False

class MainUser:
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
        self._multiplication_gates: dict[int, Protocol.MultiplicationGate] = {}
        self.final_shares: list[Protocol.SharedVariable] = []
    
        self.server_thread: threading.Thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

        self.addConnection(self.ip, self.port, self.uuid)

    def start_server(self):
        self.server = Socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen(5)
        self.log(f"Servidor iniciado en {self.ip}:{self.port}")
        while True:
            connection, _ = self.server.accept()
            threading.Thread(target=self.handle_client, args=(connection,), daemon=True).start()

    def handle_client(self, connection: Socket):
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
                # TODO: Hacer PING PONG con toda la party para saber si se desconectó alguien
                break
    
    @property
    def t(self) -> int:
        return (len(self.party) - 1) // 2 # Asegura que t < n/2
    
    @property
    def input_shares(self) -> list[Protocol.SharedVariable]:
        return list(sorted(self._input_shares.values(), key=lambda x: x.uuid))
    
    @property
    def multiplication_gates(self) -> list[Protocol.MultiplicationGate]:
        return list(sorted(self._multiplication_gates.values(), key=lambda x: x.index))
    
    def getGate(self, index: int) -> Protocol.MultiplicationGate:
        gate: Protocol.MultiplicationGate | None = self._multiplication_gates.get(index)
        if gate is None:
            gate = Protocol.MultiplicationGate(self, index)
            self._multiplication_gates[index] = gate
        return gate

    def log(self, message: str):
        print(f"\n[{self.uuid}] {message}")

    def broadcast(self, message: str):
        for user in self.party.values():
            protocol = MessageProtocol(self)
            protocol.send_message(user.host, message)

    def connect(self, ip: str, port: int, retries: int = 3, delay: int = 5) -> Socket | None:
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
        try:
            comando, contenido = message.split(SEPARADOR_IDENTIFICADOR, 1)
            for protocol in DEFAULT_PROTOCOLS:
                if protocol.identifier() == comando:
                    protocolInstance: NetworkProtocol = protocol(self)
                    protocolInstance.receive_message(contenido)
                    return
            Exception("Comando no reconocido")
        except Exception as e:
            self.log(f"Mensaje con formato invalido ({message}): {e}")
            import traceback
            traceback.print_exc()

    def send_number(self, numero: int, protocol: type[ShareProtocol] = InputShareProtocol, *args):
        shamirss = Shamirss.ShamirSecretSharing(Field(numero, self.mod), len(self.party))
        shares = shamirss.generate_shares(self.t)
        for indice, uuid in enumerate(self.party):
            user  = self.party[uuid]
            share = shares[indice]
            protocol_instance = protocol(self)
            protocol_instance.send_message(user.host, share, *args)
        
        self.log(f"Enviando número {numero} a los usuarios conectados bajo el protocolo {protocol.identifier()}")

    def onReceiveInputShare(self, user: NetworkUser, share: Protocol.SharedVariable):
        self._input_shares[share.uuid] = share
        self.log(f"Input recibido de {user.uuid}: {share}")

    def onReceiveProductShare(self, user: NetworkUser, share: Protocol.SharedVariable, operation_index: int):
        gate = self.getGate(operation_index)
        gate.addShare(share)
        self.log(f"Producto recibido de {user.uuid}: {share}")

        secret = gate.real_value
        if secret is not None:
            self.log(f"Secreto reconstruido de la multiplicación: {secret}")

            # Si es la ultima operación, se envia el secreto final
            if operation_index == len(self.multiplication_gates) - 1:
                self.send_number(secret.value, FinalShareProtocol)
            else:
                self.sendGate(operation_index + 1)
    
    def onReceiveFinalShare(self, user: NetworkUser, share: Protocol.SharedVariable):
        self.final_shares.append(share)
        self.log(f"Secreto final recibido de {user.uuid}: {share}")
        
    def sendGate(self, index: int = 0):
        self.log("gates" + ", ".join([str(gate) for gate in self.multiplication_gates]))
        gate = self.getGate(index)
        
        self.log(f"Enviando operación {gate.index}")
        self.send_number((gate.variables[0] * gate.variables[1]).value, ProductShareProtocol, gate.index)

    def reconstruct_secret(self) -> Field:
        if len(self.final_shares) < self.t:
            raise Exception("No hay suficientes partes para reconstruir el secreto.")
        return Shamirss.ShamirSecretSharing.recuperar_secreto(self.final_shares)