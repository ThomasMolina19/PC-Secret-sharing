from field_operations import Field
import NetworkUser
import random
import time

WAIT_TIME = 2.5

def create_users(num_users: int, mod: int, base_port: int = 5500) -> list[NetworkUser.MainUser]:
    """
    Crea una lista de usuarios con el número de usuarios especificado.
    :param num_users: Número de usuarios a crear.
    :param mod: Módulo para las operaciones de campo.
    :param base_port: Puerto base para los usuarios.
    :return: Lista de usuarios creados.

    Los usuarios se crean con la dirección IP local y un puerto base + i.
    """
    users = []
    for i in range(num_users):
        user = NetworkUser.MainUser("127.0.0.1", base_port + i, f"user{i+1}")
        user.mod = mod
        users.append(user)
    return users

def connect_users(users: list[NetworkUser.MainUser]) -> None:
    """
    Conecta a los usuarios entre sí.
    :param users: Lista de usuarios a conectar.
    """
    for i in range(1, len(users)):
        users[i].connect("127.0.0.1", users[0].port)
        time.sleep(WAIT_TIME)

def test_connections(users: list[NetworkUser.MainUser]) -> None:
    """
    Prueba que todos los usuarios estén conectados entre sí.
    Esto se hace verificando que el usuario i esté conectado con el usuario 0 y viceversa.
    :param users: Lista de usuarios a probar.
    """
    for i in range(1, len(users)):
        assert users[i].uuid in users[0].party, f"{users[i].uuid} no conectado a {users[0].uuid}"
        assert users[0].uuid in users[i].party, f"{users[0].uuid} no conectado a {users[i].uuid}"
    print("Prueba de conexiones exitosa.")

def create_numbers(num_users: int, mod: int) -> list[list[int]]:
    """
    Crea números aleatorios para compartir entre los usuarios.
    :param num_users: Número de usuarios.
    :param mod: Módulo para las operaciones de campo.
    :return: Lista de números aleatorios para compartir.
    """
    return [[random.randint(1, mod) for _ in range(1)] for _ in range(num_users)]

def send_shares(users: list[NetworkUser.MainUser], numbers: list[list[int]]) -> None:
    """
    Comparte los números entre los usuarios.
    :param users: Lista de usuarios a compartir.
    :param numbers: Lista de números a compartir.
    """
    for user, num_usuario in zip(users, numbers):
        for num in num_usuario:
            user.send_number(num)
            time.sleep(WAIT_TIME)

def send_operations(users: list[NetworkUser.MainUser]) -> None:
    """
    Comparte la operación de multiplicación entre los usuarios.
    :param users: Lista de usuarios a compartir la operación.
    """
    for user in users:
        user.sendOperation()
        time.sleep(WAIT_TIME)

def test_reconstruct(users: list[NetworkUser.MainUser], real_secret: Field) -> None:
    """
    Prueba que el secreto reconstruido sea correcto.
    :param users: Lista de usuarios a probar.
    :param real_secret: Secreto real a comparar.
    """
    for user in users:
        reconstructed = user.reconstruct_secret()
        assert reconstructed == real_secret, f"Secreto reconstruido incorrecto: {reconstructed} != {real_secret}"
    print("Prueba de shares exitosa.")

def main():
    """
    Función principal para probar la red de usuarios.
    Genera n usuarios, los conecta, comparte números, realiza operaciones y reconstruye el secreto.
    """

    num_users = int(input("Ingrese el número de usuarios a crear: "))
    primo = 43112609
    
    # Crear usuarios
    users = create_users(num_users, primo)

    # Los conecta entre sí
    connect_users(users)

    # Prueba que todos estén conectados entre sí
    test_connections(users)
    
    # Crea números aleatorios para compartir
    numbers = create_numbers(num_users, primo)

    print("Compartiendo shares...")
    # Comparte los números entre los usuarios
    send_shares(users, numbers)

    # Muestra el estado de cada usuario
    for user in users:
        user.status()
        print("\n")
    
    print("Compartiendo operaciones...")
    # Comparte la operación de multiplicación
    send_operations(users)
    
    # Calcula cuál es el secreto real para comparar con el secreto reconstruido
    mod_numbers = [Field(num, primo) for num_list in numbers for num in num_list]
    real_secret = Field(1, primo)
    for num in mod_numbers:
        real_secret *= num
    
    # Muestra el estado de cada usuario
    for i, user in enumerate(users):
        user.status()
        print("\n" * 2)
    
    print("Reconstruyendo secreto...")
    # Da tiempo para que se realice la reconstrucción
    time.sleep(WAIT_TIME * 5)

    # Prueba que el secreto reconstruido sea correcto
    test_reconstruct(users, real_secret)

if __name__ == "__main__":
    main()
