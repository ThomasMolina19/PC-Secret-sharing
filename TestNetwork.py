from field_operations import Field
import NetworkUser
import random
import time

WAIT_TIME = 2.5

def create_users(num_users: int, mod: int, base_port: int = 5500) -> list[NetworkUser.MainUser]:
    users = []
    for i in range(num_users):
        user = NetworkUser.MainUser("127.0.0.1", base_port + i, f"user{i+1}")
        user.mod = mod
        users.append(user)
    return users

def connect_users(users: list[NetworkUser.MainUser]):
    for i in range(1, len(users)):
        users[i].connect("127.0.0.1", users[0].port)
        time.sleep(WAIT_TIME)

def test_connections(users: list[NetworkUser.MainUser]):
    for i in range(1, len(users)):
        assert users[i].uuid in users[0].party, f"{users[i].uuid} no conectado a {users[0].uuid}"
        assert users[0].uuid in users[i].party, f"{users[0].uuid} no conectado a {users[i].uuid}"
    print("Prueba de conexiones exitosa.")

def create_numbers(num_users: int, mod: int) -> list[list[int]]:
    return [[random.randint(1, mod) for _ in range(1)] for _ in range(num_users)]

def send_shares(users: list[NetworkUser.MainUser], numbers: list[list[int]]):
    for user, num_usuario in zip(users, numbers):
        for num in num_usuario:
            user.send_number(num)
            time.sleep(WAIT_TIME)

def send_operations(users: list[NetworkUser.MainUser]):
    for user in users:
        user.sendOperation()
        time.sleep(WAIT_TIME)

def test_reconstruct(users: list[NetworkUser.MainUser], real_secret: Field):
    for user in users:
        reconstructed = user.reconstruct_secret()
        assert reconstructed == real_secret, f"Secreto reconstruido incorrecto: {reconstructed} != {real_secret}"
    print("Prueba de shares exitosa.")

def main():
    num_users = int(input("Ingrese el número de usuarios a crear: "))
    primo = 43112609
    
    users = create_users(num_users, primo)
    connect_users(users)
    test_connections(users)
    
    numbers = create_numbers(num_users, primo)
    print("Compartiendo shares...")
    send_shares(users, numbers)

    for user in users:
        user.status()
        print("\n")
    
    print("Compartiendo operaciones...")
    send_operations(users)
    
    mod_numbers = [Field(num, primo) for num_list in numbers for num in num_list]
    real_secret = Field(1, primo)
    for num in mod_numbers:
        real_secret *= num
    
    for i, user in enumerate(users):
        user.status()
        print("\n" * 2)
    
    time.sleep(WAIT_TIME * 5)

    test_reconstruct(users, real_secret)

if __name__ == "__main__":
    main()
