from field_operations import Field
from NetworkUser import MainUser
import random
import time

def create_users(num_users: int, base_port: int = 5500) -> list[MainUser]:
    users = [MainUser("127.0.0.1", base_port + i, f"user{i+1}") for i in range(num_users)]
    return users

def connect_users(users: list[MainUser]):
    for i in range(1, len(users)):
        users[i].connect("127.0.0.1", users[0].port)
        time.sleep(2)

def test_connections(users: list[MainUser]):
    for i in range(1, len(users)):
        assert users[i].uuid in users[0].party, f"{users[i].uuid} no conectado a {users[0].uuid}"
        assert users[0].uuid in users[i].party, f"{users[0].uuid} no conectado a {users[i].uuid}"
    print("Prueba de conexiones exitosa.")

def create_numbers(num_users: int, mod: int) -> list[list[int]]:
    return [[random.randint(1, mod) for _ in range(random.randint(1, 3))] for _ in range(num_users)]

def send_shares(users: list[MainUser], numbers: list[list[int]]):
    for user, num_usuario in zip(users, numbers):
        for num in num_usuario:
            user.send_number(num)
            time.sleep(1.2)

def send_operations(users: list[MainUser]):
    for user in users:
        user.send_operation()
        time.sleep(2)

def test_reconstruct(users: list[MainUser], real_secret: Field):
    for user in users:
        reconstructed = user.reconstruct_secret()
        assert reconstructed == real_secret, f"Secreto reconstruido incorrecto: {reconstructed} != {real_secret}"
    print("Prueba de shares exitosa.")

def main():
    num_users = int(input("Ingrese el número de usuarios a crear: "))
    primo = 43112609
    
    users = create_users(num_users)
    connect_users(users)
    test_connections(users)
    
    numbers = create_numbers(num_users, primo)
    send_shares(users, numbers)
    
    print("Compartiendo operaciones...")
    send_operations(users)
    
    mod_numbers = [Field(num, primo) for num_list in numbers for num in num_list]
    real_secret = Field(1, primo)
    for num in mod_numbers:
        real_secret *= num
    
    for i, user in enumerate(users):
        print(f"\n{user.uuid}\nNúmeros: {', '.join(map(str, numbers[i]))}\nPartes: {', '.join(map(str, user.input_shares))}\nOperaciones: {', '.join(map(str, user.product_shares))}")
    
    test_reconstruct(users, real_secret)

if __name__ == "__main__":
    main()
