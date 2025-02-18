from field_operations import Field
from Shamirss import ShamirSecretSharing, SecretShare
from Networking import MainUser

# a=Field(3, 7)
# b=Field(9, 7)
# c=a+b
# print(c)
# print(b)

# j = 11  # Elegimos un primo, por ejemplo, 7, para trabajar en Z7

# # Creamos un polinomio aleatorio de grado 3 en Z7
# polinomio = Polynomio.random(t=3, p=j)
# print("Polinomio en Z7:")
# print(polinomio)

# # Evaluamos el polinomio en x=2
# x = 2
# resultado = polinomio.eval(x)
# print(f"El polinomio evaluado en x={x} es {resultado}")


def menu_encriptar():
    numero = int(input("Ingresa un número: "))
    primo = input("Ingresa un número primo (default 43112609): ")
    if primo == "": primo = 43112609
    else: primo = int(primo)

    cantidad_partes = int(input("Ingresa la cantidad de partes en las que se dividirá el número: "))
    minimo_partes = int(input("Ingresa la cantidad mínima de partes necesarias para recuperar el número: "))
    if minimo_partes > cantidad_partes:
        print("La cantidad mínima de partes no puede ser mayor a la cantidad de partes")
        return
    
    numero = Field(numero, primo)
    
    secretSharing = ShamirSecretSharing(secret=numero, num_shares=cantidad_partes)
    shares = secretSharing.generate_shares(t=minimo_partes)

    print("Shares generados (guardalo muy bien, y enviaselo a los otros pares):")
    for share in shares:
        print(share)

def menu_red():
    ip = input("Ingresa la IP del servidor (default 127.0.0.1 ): ")
    if ip == "": ip = "127.0.0.1"

    puerto = input("Ingresa el puerto del servidor (default random): ")
    if puerto == "":
        import random
        puerto = random.randint(1024, 49151)
    else: puerto = int(puerto)

    secreto = SecretShare(int(input("Ingresa el indice del secreto que tienes: ")), 
        Field(int(input("Ingresa el secreto que tienes: ")), int(input("Ingresa el primo del secreto: "))))

    print("Conectandose a la red en: ", f"{ip}:{puerto}")

    usuario = MainUser(secret=secreto, ip=ip, port=puerto)
    
    while True:
        command = input("Ingrese un comando (use help para más información): ")
        if command == "exit":
            break
        elif command.startswith("connect"):
            try:
                _, ip, port = command.split()
                usuario.connect(ip, int(port))
            except ValueError:
                print("[-] Formato incorrecto. Uso: connect <IP> <PUERTO>")
        elif command.startswith("message"):
            try:
                _, *message = command.split()
                usuario.broadcast(" ".join(message))
            except ValueError:
                print("[-] Formato incorrecto. Uso: message <MENSAJE>")
        elif command.startswith("list"):
            print("Conexiones:")
            for connection in usuario.party:
                print(f"{connection.uuid} | {connection.ip}:{connection.port}")
        elif command.startswith("compartir"):
            usuario.send_shares()
        elif command.startswith("recover"):
            reconstruido = usuario.reconstruct_secret()
            print(f"El secreto reconstruido es: {reconstruido}")
        elif command.startswith("shares"):
            print("Shares:")
            for share in usuario.shares:
                print(share)
        elif command.startswith("help"):
            print("Comandos disponibles:")
            print("connect <IP> <PUERTO> - Conectarse a un par")
            print("message <MENSAJE> - Enviar un mensaje a todos los pares conectados")
            print("list - Listar las conexiones actuales")
            print("compartir - Enviar los shares a los otros pares")
            print("recover - Recuperar el secreto")
            print("shares - Listar los shares actuales")
            print("exit - Salir del programa")
        else:
            print("Comando no reconocido")

if __name__ == "__main__":
    while True:
        print("¿Que deseas hacer?\n1. Encriptar un número\n2. Conectarse a la red\n3. Salir")
        opcion = input()

        if opcion == "1":
            menu_encriptar()
        elif opcion == "2":
            menu_red()
        elif opcion == "3":
            print("Adios")
            break
        else:
            print("Opción inválida")