from abc import ABC, abstractmethod
from field_operations import Field
from socket import socket as Socket

import NetworkUser
import Protocol

DELIMITADOR = "||"
SEPARADOR_IDENTIFICADOR = "="
SEPARADOR_ARGUMENTOS = ";"

class NetworkProtocol(ABC):
    def __init__(self, user: "NetworkUser.MainUser"):
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

class ShareProtocol(NetworkProtocol, ABC):
    def send_message(self, other: Socket, share: Protocol.SharedVariable | None = None, *args) -> None:
        if share is None:
            raise Exception("Ingresa un share válido")

        message = self.format_message(self.user.uuid, share.value.value, share.value.mod, share.index, share.uuid, *args)
        other.send(message)

    def receive_message(self, message: str, *args):
        uuid, value, mod, index, varUUID, *other = self.parse_message(message)
        share = Field(int(value), int(mod))

        user = self.user.party.get(uuid)
        if user is None:
            self.user.log(f"Usuario desconocido: {uuid}")
            return
        
        shareVariable = Protocol.SharedVariable(share, int(index), varUUID)
        self.messageFunction(user, shareVariable, *other)

    @abstractmethod
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *args) -> None:
        pass
        

class InputShareProtocol(ShareProtocol):
    """
    INPUT_SHARE=user_uuid;value;mod;index;varUUID
    """
    def identifier(self = None):
        return "INPUT_SHARE"
    
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *_) -> None:
        self.user.onReceiveInputShare(user, share)

class ProductShareProtocol(ShareProtocol):
    """
    PRODUCT_SHARE=user_uuid;value;mod;index;varUUID;operation_index
    """
    def identifier(self = None):
        return "PRODUCT_SHARE"
    
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *args) -> None:
        self.user.log(f"args: {args}")
        self.user.onReceiveProductShare(user, share, int(args[0]))

class FinalShareProtocol(ShareProtocol):
    """
    FINAL_SHARE=user_uuid;value;mod;index;varUUID
    """
    def identifier(self = None):
        return "FINAL_SHARE"
    
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *_) -> None:
        self.user.onReceiveFinalShare(user, share)