from field_operations import Field
from Shamirss import ShamirSecretSharing

class Party:
    def __init__(self, field: int, number_players: int):
        self.field = field
        self.number_players = number_players

    def generate_party(self, valores: list[int]):
        n = self.number_players
        secrets = valores
        t = (n) // 2

        party_shares = {}
        

        for i in range(1, n + 1):
            while True:
                try:
                    secret = secrets[i - 1]
                    secrets.append(Field(secret, self.field).value)
                    break
                except:
                    print("Ingrese un número válido.")

            shamir = ShamirSecretSharing(self.field, secret, n)
            shares = shamir.generate_shares(t)

            
            print(f"Shares generados por el jugador {i}:")
            print(f"{shares}\n")
            
            party_shares[f"p_{i}"] = shares
        
        mixed_shares = self.send(party_shares)
        print("Fragmentos originlaes de los jugadores:")
        print(party_shares)
        
        return mixed_shares

    @staticmethod
    def send(party_shares):
        mixed_shares = {key: [] for key in party_shares.keys()}
        n = len(party_shares)

        for i in range(n):
            for j, key in enumerate(party_shares.keys()):
                mixed_shares[f"p_{i + 1}"].append(party_shares[key][i])
        return mixed_shares
    





