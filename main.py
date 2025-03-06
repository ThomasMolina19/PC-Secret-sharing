import NetworkUser

# Clase que maneja los comandos por consola.
class CommandHandler:
    def __init__(self, main_user: NetworkUser.MainUser):
        self.main_user: NetworkUser.MainUser = main_user

        # Lista de comandos disponibles.
        self.commands = {
            "connect": self.connect_user,
            "send_message": self.send_message,
            "send_number": self.send_number,
            "send_operations": self.send_operation,
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
        self.main_user.sendGate()
        print("Operación enviada.")

    def reconstruct_secret(self):
        # Se reconstruye el secreto con las partes recibidas.
        secret = self.main_user.reconstruct_secret()
        print(f"Secreto reconstruido: {secret}")

    def show_status(self):
        # Se muestra el estado actual del usuario.
        print(f"Usuarios conectados: ")
        for user in self.main_user.party.values():
            print(f"  - {user.uuid} ({user.ip}:{user.port})")
        print(f"Partes: ")
        for share in self.main_user.input_shares:
            print(f"  - {share}")

    def exit_program(self):
        # Detiene el sistema.
        self.running = False
        print("Saliendo del sistema.")

    def show_help(self):
        # Muestra los comandos disponibles.
        print("Comandos disponibles:")
        for cmd in self.commands.keys():
            print(f"  - {cmd}")


def handle_console(ip: str | None, port: int | None):
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
        
        main_user = NetworkUser.MainUser(ip, port)
        handler = CommandHandler(main_user)
        handler.run()

def handle_file(file_path: str):
    import FileManager

    cf = FileManager.ConnectionsFile(file_path)
    host = cf.create_host()
    cf.connect_with_users(host)
    print("Conexiones establecidas.")


def get_local_ip():
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
    import argparse

    parser = argparse.ArgumentParser(description="Sistema de comunicación segura.")
    parser.add_argument("--ip", help="Dirección IP del servidor.", type=str, required=False)
    parser.add_argument("--port", help="Puerto del servidor.", type=int, required=False)
    parser.add_argument("--file", help="Archivo de conexiones.", type=str, required=False)
    args = parser.parse_args()

    if args.file is not None:
        handle_file(file_path=args.file)
    else:
        handle_console(args.ip, args.port)
