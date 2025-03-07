import json
import NetworkUser
import time
from field_operations import Field

WAIT_TIME = 3.5

class ConnectionsFile:
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.data = self.read_json()
        if self.data is None:
            raise Exception("Error al leer el archivo de conexiones.")

        self.host = self.data.get("host", {})
        self.users = self.data.get("users", {})
        pass

    def read_json(self) -> dict | None:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"Error al leer el archivo JSON: {e}")
            return None
        
    def create_host(self) -> NetworkUser.MainUser:
        host_ip, host_port, uuid = self.host.get("ip"), self.host.get("port"), self.host.get("uuid")
        if host_ip is None or host_port is None:
            raise Exception("No se ha definido el host.")
        
        host = NetworkUser.MainUser(host_ip, host_port, uuid)
        return host
    
    def connect_with_users(self, host: NetworkUser.MainUser):
        l = list(map(lambda x: x.port, host.party.values()))
        i = list(map(lambda x: x.ip, host.party.values()))

        for user in self.users:
            user_ip, user_port = user.get("ip"), user.get("port")
            if user_ip is None or user_port is None:
                print(f"Usuario sin información completa: {user}")
                continue
            if host.party.get(user.get("uuid")) is not None:
                continue
            if user_port in l and user_ip in i:
                continue
            print(f"Conectando con {user_ip}:{user_port}")
            connection = host.connect(user_ip, user_port)
            if connection is None:
                raise Exception(f"No se pudo conectar con {user_ip}:{user_port}")
            time.sleep(3)

    def send_shares(self, host: NetworkUser.MainUser):
        for user_data in self.users:
            ip, port = user_data.get("ip"), user_data.get("port")
            if ip is None or port is None:
                continue
            if host.ip != ip or host.port != port:
                continue
            numbers = user_data.get("numbers", [])
            for num in numbers:
                # Envía cada número a todas las partes conectadas
                host.send_number(num)
                time.sleep(WAIT_TIME)

    def send_operations(self, host: NetworkUser.MainUser):
        # Envía la operación (multiplicación) a todas las partes
        host.sendOperation()
        time.sleep(WAIT_TIME * 3)

    def reconstruct(self, host: NetworkUser.MainUser):
        reconstructed_secret = host.reconstruct_secret()
        print("Reconstrucción del secreto exitosa.")
        return reconstructed_secret
    
    def real_secret(self):
        acum = 1
        for user in self.users:
            numbers = user.get("numbers", [])
            for num in numbers:
                acum *= num
        return Field(acum, 43112609)