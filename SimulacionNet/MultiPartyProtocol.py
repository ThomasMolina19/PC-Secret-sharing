from field_operations import Field
from Shamirss import ShamirSecretSharing
from Party import Party

class Protocol:
    def __init__(self, field: int, number_players: int):
        self.field = field
        self.number_players = number_players

    def run_protocol(self, valores: list[int]):
        n = self.number_players
        secrets = valores.copy()  # Usamos una copia para no modificar la lista original
        t = n // 2

        players = []
        for i in range(1, n + 1):
            # Se extrae el secreto correspondiente al jugador i
            while True:
                try:
                    secret = secrets[i - 1]
                    # Se recalcula o transforma el secreto utilizando Field
                    secrets.append(Field(secret, self.field).value)
                    break
                except Exception:
                    print("Ingrese un número válido.")
            
            # Se generan los fragmentos usando Shamir
            shamir = ShamirSecretSharing(self.field, secret, n)
            shares = shamir.generate_shares(t)
            print(f"Shares generados por el jugador {i}:")
            print(f"{shares}\n")
            
            # Se crea un objeto Party y se añade a la lista de jugadores
            players.append(Party(i, shares))

        mixed_shares = Party.send(players)  # Llamamos al método send desde la clase Party
        print("Fragmentos originales de los jugadores:")
        for p in players:
            print(p)
        
        return mixed_shares