from field_operations import Field
from Networking import MainUser

# Clase que maneja los comandos por consola.
class CommandHandler:
    def __init__(self, main_user: MainUser):
        self.main_user: MainUser = main_user

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
                    print(f"Error ejecutando '{cmd}': {e}")
            else:
                print(f"Comando desconocido: {cmd}")

    def connect_user(self, ip, port):
        # Se conecta al servidor con la dirección y puerto especificados.
        self.main_user.connect(ip, int(port))
        print(f"Conectado a {ip}:{port}")

    def send_message(self, message):
        # Se envía un mensaje a todos los usuarios conectados.
        self.main_user.broadcast(message)
        print(f"Mensaje enviado: {message}")

    def send_number(self):
        # Se envía el número propio a todos los usuarios conectados.
        self.main_user.send_number()
        print("Número enviado.")

    def send_operation(self):
        # Se envía el resultado de la operación a todos los usuarios conectados.
        self.main_user.send_operation()
        print("Operación enviada.")

    def reconstruct_secret(self):
        # Se reconstruye el secreto con las partes recibidas.
        secret = self.main_user.reconstruct_secret()
        print(f"Secreto reconstruido: {secret}")

    def show_status(self):
        # Se muestra el estado actual del usuario.
        print(f"Usuarios conectados: ", *list(self.main_user.party.keys()))
        print(f"Número propio: {self.main_user.numero}")
        print(f"Partes: ", *self.main_user.partes)
        print(f"Operaciones: ", *self.main_user.operaciones)

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
    port = input("Ingresa el puerto del servidor: \n>> ")
    numero = input("Ingresa el número a enviar: \n>> ")

    primo = 43112609 # Número primo para el campo. (47 de Mersenne)
    main_user = MainUser(Field(int(numero), primo), ip, int(port))
    
    handler = CommandHandler(main_user)
    handler.run()