from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing

class Party:
    def __init__(self, field: int, number_players: int):
        self.field = field
        self.number_players = number_players

    def generate_party(self):
        n = self.number_players

        party_shares = {}
        secrets = []

        for i in range(1, n + 1):
            while True:
                try:
                    secret = int(input(f"Ingresa el numero del P{i}: "))
                    secrets.append(Field(secret, self.field).value)
                    break
                except:
                    print("Ingrese un número válido.")

            shamir = ShamirSecretSharing(self.field, secret, n)
            shares = shamir.generate_shares(n-1)
            print(shares)
            
            party_shares[f"p_{i}"] = shares
        return party_shares

    @staticmethod
    def send(party_shares):
        mixed_shares = {key: [] for key in party_shares.keys()}
        n = len(party_shares)

        for i in range(n):
            for j, key in enumerate(party_shares.keys()):
                mixed_shares[f"p_{i + 1}"].append(party_shares[key][i])
        return mixed_shares
        

