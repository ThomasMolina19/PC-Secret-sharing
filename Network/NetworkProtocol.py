from abc import ABC, abstractmethod
from field_operations import Field
from socket import socket as Socket

import NetworkUser
import Protocol

import uuid as UUID

DELIMITADOR = "||"
SEPARADOR_IDENTIFICADOR = "="
SEPARADOR_ARGUMENTOS = ";"

class NetworkProtocol(ABC):
    """
    Clase abstracta que define un protocolo de comunicación entre usuarios.
    Toda clase que herede de esta clase debe implementar los métodos identifier, send_message y receive_message.

    identifier: Método que devuelve un identificador único para el protocolo.
    Este identificador se utiliza para identificar el tipo de mensaje que se está enviando.

    send_message: Método que envía un mensaje a otro usuario.
    Este método recibe como argumento un socket y una cantidad variable de argumentos.

    receive_message: Método que recibe un mensaje de otro usuario.
    Este método recibe como argumento un mensaje y una cantidad variable de argumentos.

    Además, esta clase define los métodos format_message y parse_message, que se encargan de formatear y parsear los mensajes, respectivamente.

    Con métodos abstractos, se espera que las clases hijas implementen estos métodos de acuerdo a sus necesidades.
    """
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
        """
        Formatea un mensaje a partir de una cantidad variable de argumentos.
        El mensaje se forma de la siguiente manera:
        IDENTIFICADOR=ARGUMENTO1;ARGUMENTO2;...;ARGUMENTO_N||
        """
        return (self.identifier() + SEPARADOR_IDENTIFICADOR + SEPARADOR_ARGUMENTOS.join(map(str, args)) + DELIMITADOR).encode("utf-8")
    
    def parse_message(self, message: str) -> tuple:
        """
        Parsea un mensaje en una tupla de argumentos.
        Recibe los generados por format_message.
        """
        return tuple(message.split(SEPARADOR_ARGUMENTOS))

class RequestConnectionProtocol(NetworkProtocol):
    """
    Protocolo:
    REQUEST_CONNECTION=user_uuid;ip;port

    Este protocolo se utiliza para solicitar una conexión con otro usuario.
    Este protocolo se envía a un usuario y se espera una respuesta con el protocolo ACCEPT_CONNECTION.
    """
    def identifier(self = None):
        return "REQUEST_CONNECTION"
    
    def send_message(self, other: Socket, from_user = None, *args) -> None:
        """
        Envia a través de un socket un mensaje con el protocolo REQUEST_CONNECTION.
        Si no se especifica un usuario, se envía el mensaje desde el usuario actual.
        """
        if from_user is None: from_user = self.user
        m = self.format_message(from_user.uuid, from_user.ip, from_user.port)
        other.send(m)

    def receive_message(self, message: str, *args):
        """
        Recibe un mensaje con el protocolo REQUEST_CONNECTION.
        Se espera que el mensaje contenga el UUID, IP y puerto del usuario que envía la solicitud.
        Se crea una conexión con el usuario que envía la solicitud y se envía un mensaje de aceptación.

        Si el usuario ya está conectado, no se crea una nueva conexión.

        Además, a cada miembro del grupo se le envía un mensaje con el protocolo REQUEST_CONNECTION.
        Para que cada miembro del grupo se conecte con el usuario que envía la solicitud.
        """
        uuid, ip, port = self.parse_message(message)
        connection = self.user.addConnection(uuid=uuid, ip=ip, port=int(port))

        if connection is None:
            return
        
        for member in self.user.party.values():
            if member.uuid != self.user.uuid:
                self.send_message(member.host, from_user=connection)

class AcceptConectionProtocol(NetworkProtocol):
    """
    Protocolo:
    ACCEPT_CONNECTION=user_uuid;ip;port

    Este protocolo se utiliza para aceptar una conexión con otro usuario.
    Este protocolo se envía como respuesta a un protocolo REQUEST_CONNECTION.

    Se espera que el usuario que envía el mensaje haya recibido un protocolo REQUEST_CONNECTION.
    """
    def identifier(self = None):
        return "ACCEPT_CONNECTION"
    
    def send_message(self, other: Socket, from_user = None, *args) -> None:
        """
        Envia a través de un socket un mensaje con el protocolo ACCEPT_CONNECTION.
        Si no se especifica un usuario, se envía el mensaje desde el usuario actual.

        Se envia cómo respuesta a un mensaje con el protocolo REQUEST_CONNECTION, indicando que la conexión ha sido aceptada.
        """
        if from_user is None: from_user = self.user
        m = self.format_message(self.user.uuid, self.user.ip, self.user.port)
        other.send(m)

    def receive_message(self, message: str, *args):
        """
        Recibe un mensaje con el protocolo ACCEPT_CONNECTION.
        Se espera que el mensaje contenga el UUID, IP y puerto del usuario que acepta la conexión.
        Se crea una conexión con el usuario que acepta la conexión.
        """
        uuid, ip, port = self.parse_message(message)
        self.user.addConnection(uuid=uuid, ip=ip, port=int(port))

class MessageProtocol(NetworkProtocol):
    """
    Protocolo:
    MESSAGE=user_uuid;message

    Este protocolo se utiliza para enviar mensajes entre usuarios.
    Se espera que el mensaje contenga el UUID del usuario que envía el mensaje y el mensaje en sí.
    """
    def identifier(self = None):
        return "MESSAGE"
    
    def send_message(self, other: Socket, message: str = "", *args) -> None:
        other.send(self.format_message(self.user.uuid, message))

    def receive_message(self, message: str, *args):
        m = self.parse_message(message)
        print(f"[{m[0]}] -> {m[1]}")

class ShareProtocol(NetworkProtocol, ABC):
    """
    Protocolo base para compartir valores entre usuarios.
    Se espera que las clases hijas implementen el método messageFunction.

    El mensaje se forma de la siguiente manera:
        IDENTIFIER=user_uuid;value;mod;uuid;*args

    user_uuid: UUID del usuario que envía el mensaje.
    value: Valor del share.
    mod: Modulo del share.
    uuid: UUID de la variable compartida.
    *args: Argumentos adicionales.

    Esta clase existe para compartir valores entre usuarios.
    Así, se pueden compartir valores de forma segura y eficiente.
    """

    def send_message(self, other: Socket, share: Field | None = None, *args) -> None:
        if share is None:
            raise Exception("Ingresa un share válido")

        message = self.format_message(self.user.uuid, share.value, share.mod, str(UUID.uuid4()), *args)
        try:
            other.send(message)
        except Exception as e:
            pass

    def receive_message(self, message: str, *args):
        """
        Recibe un mensaje con el protocolo SHARE.
        Se espera que el mensaje contenga el UUID, valor, módulo y UUID de la variable compartida.
        Se crea un objeto Field a partir del valor y el módulo.
        Se crea un objeto SharedVariable a partir del Field, el UUID y el UUID de la variable compartida.
        Se llama al método messageFunction con el usuario que envía el mensaje y la variable compartida.
        """
        uuid, value, mod, varUUID, *other = self.parse_message(message)
        share = Field(int(value), int(mod))

        user = self.user.party.get(uuid)
        if user is None:
            self.user.log(f"Usuario desconocido: {uuid}")
            return
        
        shareVariable = Protocol.SharedVariable(share, uuid, varUUID)
        self.messageFunction(user, shareVariable, *other)

    @abstractmethod
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *args) -> None:
        pass
        

class InputShareProtocol(ShareProtocol):
    """
    INPUT_SHARE=user_uuid;value;mod;varUUID
    """
    def identifier(self = None):
        return "INPUT_SHARE"
    
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *_) -> None:
        self.user.onReceiveInputShare(user, share)

class ProductShareProtocol(NetworkProtocol):
    """
    PRODUCT_SHARE=user_uuid;value;mod;varUUID;operation_index
    """
    def identifier(self = None):
        return "PRODUCT_SHARE"
    
    def send_message(self, other: Socket, share: Protocol.Field | None = None, operation_index: int | None = None, *args) -> None:
        if share is None:
            raise Exception("Ingresa un share válido")
        if operation_index is None:
            raise Exception("Ingresa un índice de operación válido")

        message = self.format_message(self.user.uuid, share.value, share.mod, str(UUID.uuid4()), operation_index, *args)
        other.send(message)
    
    def receive_message(self, message: str, *args):
        uuid, value, mod, varUUID, opIndex = self.parse_message(message)
        n = Field(int(value), int(mod))
        variable = Protocol.MultiplicationVariable(Protocol.SharedVariable(n, uuid, varUUID), int(opIndex))

        u = self.user.party.get(uuid)
        if u is None:
            self.user.log(f"Usuario desconocido: {uuid}")
            return

        self.user.onReceiveProductShare(u, variable, int(opIndex))

class FinalShareProtocol(ShareProtocol):
    """
    FINAL_SHARE=user_uuid;value;mod;varUUID
    """
    def identifier(self = None):
        return "FINAL_SHARE"
    
    def messageFunction(self, user: "NetworkUser.NetworkUser", share: Protocol.SharedVariable, *_) -> None:
        self.user.onReceiveFinalShare(user, share)