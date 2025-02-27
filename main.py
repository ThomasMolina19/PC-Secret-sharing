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


if __name__ == "__main__":
    ip = input("Ingresa la dirección IP del servidor: \n>> ")

    if ip == "":
        ip = "127.0.0.1"

    port = input("Ingresa el puerto del servidor: \n>> ")

    if port == "":
        import random
        port = 5000 + random.randint(1, 1000)

    main_user = NetworkUser.MainUser(ip, int(port))
    handler = CommandHandler(main_user)
    handler.run()