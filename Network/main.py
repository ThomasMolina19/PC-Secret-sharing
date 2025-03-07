import NetworkUser

# Clase que maneja los comandos por consola.
class CommandHandler:
    def __init__(self, main_user: NetworkUser.MainUser):
        self.main_user: NetworkUser.MainUser = main_user

        # Lista de comandos disponibles.
        self.commands = {
            "connect": self.connect_user,
            "message": self.send_message,
            "number": self.send_number,
            "multiply": self.send_operation,
            "reconstruct": self.reconstruct_secret,
            "status": self.show_status,
            "exit": self.exit_program
        }

        # Variable para saber si el sistema está corriendo.
        self.running = True

    def run(self):
        print("Sistema iniciado. Escribe 'help' para ver los comandos.")

        # Mientras el sistema esté corriendo, se lee la entrada del usuario.
        while self.running:
            cmd_input = input(">> ").strip().split()

            # Si no se ingresó ningún comando, se ignora.
            if not cmd_input:
                continue
            
            # Se obtiene el comando y los argumentos.
            cmd = cmd_input[0]
            args = cmd_input[1:]

            # Si el comando es "help", se llama show_help.
            if cmd == "help":
                self.show_help()
            # Si está en la lista de comandos, se ejecuta
            elif cmd in self.commands:
                try:
                    # Se ejecuta el comando con los argumentos.
                    self.commands[cmd](*args)
                except Exception as e:
                    print(f"Error ejecutando '{cmd}':", e)
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Comando desconocido: {cmd}")

    def connect_user(self, ip, port):
        # Se conecta al servidor con la dirección y puerto especificados.
        self.main_user.connect(ip, int(port))

    def send_message(self, *message):
        # Se envía un mensaje a todos los usuarios conectados.
        # Por como se implementó, el mensaje debe ser una lista de strings.
        # Se envía el mensaje unido por espacios.
        self.main_user.broadcast(" ".join(message))

    def send_number(self, number):
        # Se envía el número propio a todos los usuarios conectados.
        self.main_user.send_number(numero=int(number))
        print("Número enviado.")

    def send_operation(self):
        # Se envía el resultado de la operación a todos los usuarios conectados.
        self.main_user.sendOperation()
        print("Operación enviada.")

    def reconstruct_secret(self):
        # Se reconstruye el secreto con las partes recibidas.
        secret = self.main_user.reconstruct_secret()
        print(f"Secreto reconstruido: {secret}")

    def show_status(self):
        # Se muestra el estado actual del usuario.
        self.main_user.status()

    def exit_program(self):
        # Detiene el sistema.
        self.running = False
        print("Saliendo del sistema.")

    def show_help(self):
        # Muestra los comandos disponibles.
        print("Comandos disponibles:")
        for cmd in self.commands.keys():
            print(f"  - {cmd}")


def handle_console(ip: str | None, port: int | None, uuid: str | None = None):
        """
        Inicia el sistema de comunicación por consola.
        Se crean un usuario principal y un manejador de comandos.
        Se ejecuta el manejador de comandos.

        En caso de que no se especifique la dirección IP o el puerto, se solicitan al usuario.
        Si no se ingresan, se obtiene la dirección IP local del dispositivo, y se asigna un puerto aleatorio.

        :param ip: Dirección IP del servidor.
        :param port: Puerto del servidor.
        :param uuid: UUID del usuario.
        """
        import random

        if not ip:
            ip = input("Ingresa la dirección IP del servidor: \n>> ")
            if not ip or ip == "":
                ip = get_local_ip()
        if not port:
            p = input("Ingresa el puerto del servidor: \n>> ")
            if p and p != "":
                port = int(p)
            else:
                port = 5500 + random.randint(1, 999)

        if not ip or not port:
            print("Debes ingresar una dirección IP y un puerto.")
            return
        
        main_user = NetworkUser.MainUser(ip, port, uuid)
        handler = CommandHandler(main_user)
        handler.run()

def handle_file(file_path: str, ip: str | None = None, port: int | None = None, uuid: str | None = None):
    """
    Lee el archivo de conexiones y ejecuta las acciones correspondientes.
    En caso de que se pasen los argumentos de IP, puerto y UUID, se crea un host con esos datos.
    De lo contrario, trata de obtenerlo del propio archivo.
    Si está especificado en el archivo, pero también se pasaron los argumentos, se usan los argumentos.

    Realiza las siguientes acciones:
    - Conectar con los usuarios.
    - Enviar los shares.
    - Enviar las operaciones.
    - Reconstruir el secreto.

    Opcionalmente, se puede mostrar el secreto esperado, aunque no es necesario.

    :param file_path: Ruta del archivo de conexiones.
    :param ip: Dirección IP del servidor.
    :param port: Puerto del servidor.
    :param uuid: UUID del usuario.
    """
    import FileManager
    import time

    cf = FileManager.ConnectionsFile(file_path)
    host = cf.create_host(ip, port, uuid)

    host.status()

    print("Conectando con usuarios...")
    cf.connect_with_users(host)
    print("Conexiones establecidas.")

    host.status()

    print("Enviando shares...")
    cf.send_shares(host)

    while len(host.input_shares) < len(host.party):
        print("Esperando shares...")
        time.sleep(1)

    print("Shares enviados.")

    host.status()

    print("Enviando operaciones...")
    cf.send_operations(host)

    while len(host.getMultiplicationShare(0)) < len(host.party):
        print("Esperando multiplicaciones...")
        time.sleep(1)

    print("Operaciones enviadas.")

    host.status()

    time.sleep(15)

    host.status()

    print("Reconstruyendo secreto...")
    secret = cf.reconstruct(host)
    print(f"Secreto reconstruido: {secret}")

    real_secret = cf.real_secret()
    print(f"Secreto esperado: {real_secret}")

    input("Presiona Enter para continuar...")


def get_local_ip():
        """
        Obtiene la dirección IP local del dispositivo.
        Se conecta a un servidor externo (Google DNS) para obtener la IP.
        """
        try:
            import socket
            # Crear un socket temporal y conectarse a un servidor externo (Google DNS)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # No envía datos, solo obtiene la IP local
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            print(f"Error obteniendo la IP local: {e}")
            return "127.0.0.1"  # Fallback a localhost


if __name__ == "__main__":
    """
    Cuando se ejecuta el script, se pueden pasar argumentos por consola.
    Los argumentos disponibles son:
    --ip: Dirección IP del servidor.
    --port: Puerto del servidor.
    --uuid: UUID del usuario.
    --file: Archivo de conexiones.

    En caso de que se pase un archivo, se ejecuta handle_file.
    En caso contrario, se ejecuta handle_console.

    handle_console: Inicia el sistema de comunicación por consola.
    handle_file: Lee un archivo de conexiones y ejecuta las acciones correspondientes.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Sistema de comunicación segura.")
    parser.add_argument("--ip", help="Dirección IP del servidor.", type=str, required=False)
    parser.add_argument("--port", help="Puerto del servidor.", type=int, required=False)
    parser.add_argument("--uuid", help="UUID del usuario.", type=str, required=False)
    parser.add_argument("--file", help="Archivo de conexiones.", type=str, required=False)
    args = parser.parse_args()

    if args.file is not None:
        handle_file(file_path=args.file, ip=args.ip, port=args.port, uuid=args.uuid)
    else:
        handle_console(args.ip, args.port, args.uuid)
