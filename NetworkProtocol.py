from abc import ABC, abstractmethod
from field_operations import Field
from socket import socket as Socket
from Multiplication import SharedVariable, MultiplicationVariable

DELIMITADOR = "||"
SEPARADOR_IDENTIFICADOR = "="
SEPARADOR_ARGUMENTOS = ";"

class NetworkProtocol(ABC):
    def __init__(self, user):
        self.user = user

    @abstractmethod
    def identifier(self: "NetworkProtocol | None" = None) -> str:
        pass

    @abstractmethod
    def send_message(self, other: Socket, *args) -> None:
        pass

    @abstractmethod
    def receive_message(self, message: str, *args) -> None:
        pass

    def format_message(self, *args) -> bytes:
        return (self.identifier() + SEPARADOR_IDENTIFICADOR + SEPARADOR_ARGUMENTOS.join(map(str, args)) + DELIMITADOR).encode("utf-8")
    
    def parse_message(self, message: str) -> tuple:
        return tuple(message.split(SEPARADOR_ARGUMENTOS))

class RequestConnectionProtocol(NetworkProtocol):
    def identifier(self = None):
        return "REQUEST_CONNECTION"
    
    def send_message(self, other: Socket, from_user = None, *args) -> None:
        if from_user is None: from_user = self.user
        m = self.format_message(from_user.uuid, from_user.ip, from_user.port)
        other.send(m)

    def receive_message(self, message: str, *args):
        uuid, ip, port = self.parse_message(message)
        connection = self.user.addConnection(uuid=uuid, ip=ip, port=int(port))

        if connection is None:
            return
        
        for member in self.user.party.values():
            if member.uuid != self.user.uuid:
                self.send_message(member.host, from_user=connection)

class AcceptConectionProtocol(NetworkProtocol):
    def identifier(self = None):
        return "ACCEPT_CONNECTION"
    
    def send_message(self, other: Socket, from_user = None, *args) -> None:
        if from_user is None: from_user = self.user
        m = self.format_message(self.user.uuid, self.user.ip, self.user.port)
        other.send(m)

    def receive_message(self, message: str, *args):
        uuid, ip, port = self.parse_message(message)
        self.user.addConnection(uuid=uuid, ip=ip, port=int(port))

class MessageProtocol(NetworkProtocol):
    def identifier(self = None):
        return "MESSAGE"
    
    def send_message(self, other: Socket, message: str = "", *args) -> None:
        other.send(self.format_message(self.user.uuid, message))

    def receive_message(self, message: str, *args):
        m = self.parse_message(message)
        print(f"[{m[0]}] -> {m[1]}")

class InputShareProtocol(NetworkProtocol):
    """
    INPUT_SHARE=user_uuid;value;mod;varUUID
    """
    def identifier(self = None):
        return "INPUT_SHARE"
    
    def send_message(self, other: Socket, share: Field | None = None, *args) -> None:
        if share is None:
            Exception("Ingresa un share válido")
            return

        shareVariable = SharedVariable(share, self.user.uuid)
        message = self.format_message(self.user.uuid, share.value, share.mod, shareVariable.uuid)
        other.send(message)

    def receive_message(self, message: str, *args):
        uuid, value, mod, varUUID= self.parse_message(message)
        share = Field(int(value), int(mod))

        user = self.user.party[uuid]

        if user is None:
            self.user.log(f"Usuario desconocido: {uuid}")
            return
        
        shareVariable = SharedVariable(share, uuid, varUUID)

        self.user.addInputShare(user, shareVariable)

class ProductShareProtocol(NetworkProtocol):
    """
    PRODUCT_SHARE=user_uuid;value;mod;varUUID;indice
    """
    def identifier(self = None):
        return "PRODUCT_SHARE"
    
    def send_message(self, other: Socket, variable: MultiplicationVariable | None = None, *args) -> None:
        if variable is None:
            Exception("Ingresa un share válido")
            return
        other.send(self.format_message(self.user.uuid, variable.value.value, variable.value.mod, variable.uuid, variable.indice))

    def receive_message(self, message: str, *args):
        uuid, value, mod, varUUID, indice = self.parse_message(message)
        share = Field(int(value), int(mod))

        user = self.user.party[uuid]

        if user is None:
            self.user.log(f"Usuario desconocido: {uuid}")
            return
        
        shareVariable = MultiplicationVariable(share, uuid, int(indice))
        self.user.processProductShare(user, shareVariable)